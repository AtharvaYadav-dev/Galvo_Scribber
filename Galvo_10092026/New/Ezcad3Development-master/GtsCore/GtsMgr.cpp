#include <QMessageBox>
#include <QCoreApplication>
#include <QDebug>

#include "GtsMgr.h"

GtsMgr::GtsMgr(QObject* parent)
    : QObject(parent)
    , m_axisInfo(m_axisCount)
{
    m_cfg.axes.resize(m_axisCount);

    // 初始化各个模块
    m_boardMgr = std::make_unique<BoardMgr>(this);
    m_axisMgr = std::make_unique<AxisMgr>(this);
    m_motionMgr = std::make_unique<MotionMgr>(this, this);
    m_interpolationMgr = std::make_unique<InterpolationMgr>(this);
    m_ioMgr = std::make_unique<IOMgr>(this);
    m_feedbackMgr = std::make_unique<FeedbackMgr>(this);
    m_configMgr = std::make_unique<ConfigMgr>(this);

    // 注入依赖
    m_configMgr->injectDependencies(&m_cfg, this, m_axisMgr.get());

    // 创建定时器用来刷新实时数据
    m_refreshTimer = new QTimer(this);
    connect(m_refreshTimer, &QTimer::timeout, this, &GtsMgr::onRefreshTimeout);

    // gts子管理类的日志和错误信号汇总到总管理类
    connect(axisMgr(), &AxisMgr::errorOccurred, this, &GtsMgr::onErrorOccurred);
    connect(boardMgr(), &BoardMgr::errorOccurred, this, &GtsMgr::onErrorOccurred);
    connect(motionMgr(), &MotionMgr::errorOccurred, this, &GtsMgr::onErrorOccurred);
    connect(feedbackMgr(), &FeedbackMgr::errorOccurred, this, &GtsMgr::onErrorOccurred);
    connect(configMgr(), &ConfigMgr::errorOccurred, this, &GtsMgr::onErrorOccurred);
    connect(ioMgr(), &IOMgr::errorOccurred, this, [this](short errorCode, const QString& errorMsg) {  onErrorOccurred(-1, errorCode, errorMsg);   });
    connect(axisMgr(), &AxisMgr::logMessage, this, &GtsMgr::onLogMessage);
    connect(boardMgr(), &BoardMgr::logMessage, this, &GtsMgr::onLogMessage);
    connect(motionMgr(), &MotionMgr::logMessage, this, &GtsMgr::onLogMessage);
    connect(feedbackMgr(), &FeedbackMgr::logMessage, this, &GtsMgr::onLogMessage);
    connect(configMgr(), &ConfigMgr::logMessage, this, &GtsMgr::onLogMessage);
    connect(ioMgr(), &IOMgr::logMessage, this, &GtsMgr::onLogMessage);
    // 设置发送变化转发
    connect(configMgr(),&ConfigMgr::configChanged, this, &GtsMgr::onConfigChanged);

}

GtsMgr::~GtsMgr() 
{
    stopRefresh();
    m_refreshTimer = nullptr;
}

void GtsMgr::startRefresh(int intervalMs)
{
    if (m_refreshTimer->isActive()) {
        m_refreshTimer->stop();
    }
    // 立即刷新一次 
    onRefreshTimeout();
    // 启动定时器
    m_refreshTimer->start(intervalMs);
}

void GtsMgr::stopRefresh()
{
    m_refreshTimer->stop();
}

void GtsMgr::initAfterBoardOpened()
{
    // 启动定时器开始实时获取数据
    startRefresh();
    // 从 JSON 加载配置(通过 ConfigMgr)
    if (!m_configMgr->loadAxisConfig()) {
        m_configMgr->readAllAxisConfigFromBoard();
        m_configMgr->saveAxisConfig();
    }
    else {
        m_configMgr->applyAllAxisConfigToBoard();
    }
    // 读取DAC配置
    m_configMgr->readDacConfig();
    // 读取control误差极限
    m_configMgr->readFollowErrorLimit();
    // 读取profile停止减速度参数
    m_configMgr->readStopDecel();

    emit m_configMgr->configChanged();

    // 读取运动参数
    m_motionMgr->getCommonMotionInfo(m_axisInfo.items);
    emit axisSettingUpdated(m_axisInfo.items);


    // 同时看一下每个轴的 homeInit 返回值
    for (short i = 1; i <= m_axisCount; ++i) {
        short err = GtsHal::homeInit();  // 直接看返回值
        qDebug() << "axis" << i << "homeInit ret:" << err;
    }
}

void GtsMgr::cleanupAfterBoardClosed()
{
    stopRefresh();
    m_axisInfo.items.clear();     // 清空轴数据
    m_clocks = Clock(); // 清空时钟
}

double GtsMgr::pulsePerMm(short profile) const
{
    long alpha = configMgr()->softPulseAlpha(profile);
    long beta = configMgr()->softPulseBeta(profile);
    if (alpha == 0) return 0.0;
    return static_cast<double>(beta) / alpha;       // beta pulse = 1 mm
}

double GtsMgr::mmPerPulse(short profile) const
{
    long alpha = configMgr()->softPulseAlpha(profile);
    long beta = configMgr()->softPulseBeta(profile);
    if (beta == 0) return 0.0;
    return static_cast<double>(alpha) / beta;       // 1 pulse = alpha/beta mm
}

long GtsMgr::mmToPulse(short profile, double mm) const
{
    return static_cast<long>(mm * pulsePerMm(profile));
}

double GtsMgr::mmpsToPulsePerMs(short profile, double mmps) const
{
    return mmps * pulsePerMm(profile) / 1000.0;       // mm/s → pulse/ms
}

double GtsMgr::mmps2ToPulsePerMs2(short profile, double mmps2) const
{
    return mmps2 * pulsePerMm(profile) / 1000000.0;   // mm/s² → pulse/ms²
}

double GtsMgr::pulseToMm(short profile, long pulse) const
{
    double ppm = pulsePerMm(profile);
    if (ppm == 0.0) return 0.0;
    return static_cast<double>(pulse) / ppm;
}

void GtsMgr::onRefreshTimeout()
{
    if (!m_boardMgr->isOpen()) return;

    // 读取板卡时钟
    m_clocks = m_boardMgr->getClocks();
    emit boardClockUpdated(m_clocks);

    // 读取轴状态信息
    m_axisMgr->getAxisStatusAndMotionInfo(m_axisInfo.items);
    emit axisUpdated(m_axisInfo.items);

    // 读取IO状态信息
    m_ioMgr->getPLimitDI(m_di.posLimit);
    m_ioMgr->getNLimitDI(m_di.negLimit);
    m_ioMgr->getDriverAlarmDI(m_di.alarm);
    m_ioMgr->getHomeDI(m_di.home);
    m_ioMgr->getGPI(m_di.GPI);
    m_ioMgr->getArriveDI(m_di.arrive);
    m_ioMgr->getHandwheelDI(m_di.handwheel);
    emit diUpdated(m_di);

    // 读取DO状态信息
    m_ioMgr->getMotorEnableDO(m_do.servoOn);
    m_ioMgr->getGPO(m_do.GPO);
    m_ioMgr->getClearAlarmDO(m_do.almClear);
    emit doUpdated(m_do);
}

void GtsMgr::onErrorOccurred(short axis, short errorCode, const QString& errorMsg)
{
    emit errorOccurred(axis, errorCode, errorMsg);
}

void GtsMgr::onLogMessage(const QString& message, QColor color, const QString& source)
{
    emit logMessage(message, color, source);
}

void GtsMgr::onConfigChanged()
{
    emit configChanged();
}
