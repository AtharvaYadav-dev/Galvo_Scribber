#include <QCoreApplication>
#include <QEventLoop>
#include <QThread>
#include <QMessageBox>

#include "GtsMgr.h"
#include "GtsMotionMgr.h"

MotionMgr::MotionMgr(GtsMgr* totalMgr, QObject* parent)
    : QObject(parent)
    , m_gtsMgr(totalMgr)
{
}

MotionMgr::~MotionMgr() 
{
    m_gtsMgr = nullptr;
}

bool MotionMgr::setAxisMotionMode(short axis, short mode)
{
    if (!checkProfile(axis)) return false;
    if (mode == 0) {
        // 点位运动模式 (Trap)
        return setTrapMode(axis);
    }
    else if (mode == 1) {
        // Jog 持续运动模式
        return setJogMode(axis);
    }
    else {
        // 无效模式
        m_lastError = -1;
        return false;
    }
}

void MotionMgr::getAxisMotionInfo(std::vector<SingleAxisInfo>& vecAxis)
{
    for (auto& axis : vecAxis) {
        short axisIndex = axis.axisIndex;                  // 轴号 1~4
        axis.prfPosOriginal = axisProfilePos(axisIndex);   // 规划位置
        axis.prfVelOriginal = axisProfileVel(axisIndex);   // 规划速度
        axis.prfAccOriginal = axisProfileAcc(axisIndex);   // 规划加速度
    }
}

void MotionMgr::getCommonMotionInfo(std::vector<SingleAxisInfo>& vecAxis)
{
    for (auto& axis : vecAxis) {
        short profile = axis.axisIndex;                     // 轴号 1-4
        axis.prfMode = profileMode(profile);               // 运动模式
        m_gtsMgr->axisCfg()->axes[profile - 1].trapParam.motionVel = targetVel(profile);
    }
}


void MotionMgr::getTrapMotionInfo(std::vector<SingleAxisInfo>& vecTrap)
{
    for (auto& axis : vecTrap) {
        short profile = axis.axisIndex;  // 轴号 1-4
        double ppm = m_gtsMgr->pulsePerMm(profile);
        TTrapPrm prm = {};
        if (getTrapParams(profile, prm)) {
            m_gtsMgr->axisCfg()->axes[profile - 1].trapParam.acc = prm.acc / (ppm > 0 ? ppm : 1.0);
            m_gtsMgr->axisCfg()->axes[profile - 1].trapParam.dec = prm.dec / (ppm > 0 ? ppm : 1.0);
            m_gtsMgr->axisCfg()->axes[profile - 1].trapParam.somoothTime = prm.smoothTime;
        }
    }
}

bool MotionMgr::setTrapParam(short axisId, const TrapParam& param)
{
    if (!checkProfile(axisId)) return false;
    TTrapPrm prm;
    double ppm = m_gtsMgr->pulsePerMm(axisId);
    prm.acc = param.acc * ppm;
    prm.dec = param.dec * ppm;
    prm.smoothTime = param.somoothTime;  // 平滑时间
    if (!setTrapParams(axisId, prm)) {
        return false;
    }
    return true;
}


bool MotionMgr::startTrapMotion(short profile, double stepSize, const TrapParam& trap)
{
    if (!checkProfile(profile)) return false;

    if (trap.motionVel <= 0.0) {
        emit errorOccurred(profile, -1,
            QStringLiteral("轴%1 运动速度无效 (dMotionVel = %2 mm/s)，必须 > 0")
            .arg(profile).arg(trap.motionVel, 0, 'f', 3));
        return false;
    }
    if (stepSize == 0.0) {
        emit errorOccurred(profile, -1,
            QStringLiteral("轴%1 步长为 0 mm，无法运动").arg(profile));
        return false;
    }
    if (trap.acc <= 0.0) {
        emit errorOccurred(profile, -1,
            QStringLiteral("轴%1 加速度无效 (acc = %2 mm/s^2)，必须 > 0")
            .arg(profile).arg(trap.acc, 0, 'f', 6));
        return false;
    }
    if (trap.dec <= 0.0) {
        emit errorOccurred(profile, -1,
            QStringLiteral("轴%1 减速度无效 (dec = %2 mm/s^2)，必须 > 0")
            .arg(profile).arg(trap.dec, 0, 'f', 6));
        return false;
    }
    if (trap.somoothTime < 0) {
        emit errorOccurred(profile, -1,
            QStringLiteral("轴%1 平滑时间无效 (smoothTime = %2)，不能为负数")
            .arg(profile).arg(trap.somoothTime));
        return false;
    }

    // 单次模式
    if (trap.cycleTimes <= 0) {
        return singleTrapMotion(profile, stepSize,
            trap.acc, trap.dec, trap.somoothTime, trap.motionVel);
    }

    // 循环模式：异步状态机驱动,onTrapCycleStep 递归自调度
    if (m_trapCycle.active) {
        emit errorOccurred(profile, -1,
            QStringLiteral("轴%1 循环运动已在执行，请先取消").arg(profile));
        return false;
    }

    m_trapCycle.active      = true;
    m_trapCycle.profile     = profile;
    m_trapCycle.stepSize    = stepSize;
    m_trapCycle.acc         = trap.acc;
    m_trapCycle.dec         = trap.dec;
    m_trapCycle.smoothTime  = trap.somoothTime;
    m_trapCycle.vel         = trap.motionVel;
    m_trapCycle.totalTimes  = trap.cycleTimes;
    m_trapCycle.currentStep = -1;   // 首次递增后为 0
    m_trapCycle.delayMs     = trap.delay;

    // 直接触发第一步(首次无需 waitMotionDone)
    onTrapCycleStep(profile);
    return true;
}

void MotionMgr::cancelTrapCycle()
{
    if (!m_trapCycle.active) return;
    m_trapCycle.active = false;
    emit motionDone(m_trapCycle.profile);  // 通知同步等待者退出
    stop(m_trapCycle.profile, 0);  // 紧急停止
}

bool MotionMgr::trapMotionSync(short profile, double lengthMm)
{
    // 走原有的异步入口
    if (!trapMotion(profile, lengthMm))
        return false;

    // 单次模式: singleTrapMotion 发送完即结束
    if (!m_trapCycle.active)
        return true;

    // 循环模式: 嵌套事件循环等待 motionDone 或 errorOccurred
    bool completed = false;
    QEventLoop loop;

    QMetaObject::Connection c1 = connect(this, &MotionMgr::motionDone,
        [&](short p) {
            if (p == profile) { completed = true; loop.quit(); }
        });
    QMetaObject::Connection c2 = connect(this, &MotionMgr::errorOccurred,
        [&](short p, short, const QString&) {
            if (p == profile) { loop.quit(); }
        });

    loop.exec();  // 内部 processEvents, UI 不冻结

    disconnect(c1);
    disconnect(c2);
    return completed;
}

void MotionMgr::onTrapCycleStep(short profile)
{
    if (!m_trapCycle.active || m_trapCycle.profile != profile)
        return;

    m_trapCycle.currentStep++;

    // 全部完成?
    if (m_trapCycle.currentStep >= m_trapCycle.totalTimes * 2) {
        m_trapCycle.active = false;
        emit motionDone(profile);
        return;
    }

    // 偶数步正向, 奇数步反向
    double sign = (m_trapCycle.currentStep % 2 == 0) ? 1.0 : -1.0;
    double step = sign * m_trapCycle.stepSize;

    // 下发本次运动
    if (!singleTrapMotion(m_trapCycle.profile, step,
        m_trapCycle.acc, m_trapCycle.dec,
        m_trapCycle.smoothTime, m_trapCycle.vel)) {
        m_trapCycle.active = false;
        emit errorOccurred(profile, -1,
            QStringLiteral("循环Trap第%1步下发失败").arg(m_trapCycle.currentStep + 1));
        return;
    }

    // 等待运动完成(processEvents 保持 UI 响应)
    waitMotionDone(profile);

    // 等待期间可能被 cancelTrapCycle 取消
    if (!m_trapCycle.active) return;

    // 步间延时
    if (m_trapCycle.delayMs > 0) {
        GtsHal::delay(static_cast<unsigned short>(m_trapCycle.delayMs));
    }

    if (!m_trapCycle.active) return;

    // 递归调度下一步(QueuedConnection 回到事件循环,不爆栈)
    QMetaObject::invokeMethod(this, "onTrapCycleStep", Qt::QueuedConnection,
                              Q_ARG(short, profile));
}



bool MotionMgr::trapMotion(short profile, double lengthMm)
{
    if (!checkProfile(profile)) return false;

    if (lengthMm == 0.0) {
        emit errorOccurred(profile, -1,
            QStringLiteral("轴%1 下发长度为 0，无法运动").arg(profile));
        return false;
    }

    int idx = profile - 1;
    SingleAxisInfo* pAxis = m_gtsMgr->getAxisRef(idx);
    if (!pAxis) return false;

    TrapParam trapPrm = m_gtsMgr->axisCfg()->axes[idx].trapParam;
    emit logMessage(QStringLiteral("轴%1 Trap运动").arg(profile), Qt::darkGreen);
    // 设置完规划器当量后脉冲会放大,最后脉冲数为lengthMM * beta / alpha
    return startTrapMotion(profile, lengthMm, trapPrm);
}


void MotionMgr::getJogMotionInfo(std::vector<SingleAxisInfo>& vecAxis)
{
    for (auto& axis : vecAxis) {
        short profile = axis.axisIndex;  // 轴号 1-4
        double ppm = m_gtsMgr->pulsePerMm(profile);
        TJogPrm prm = {};
        if (getJogParams(profile, prm)) {
            // 读到了才更新内存 —— pulse → mm
            m_gtsMgr->axisCfg()->axes[profile - 1].jogParam.acc = prm.acc / (ppm > 0 ? ppm : 1.0);
            m_gtsMgr->axisCfg()->axes[profile - 1].jogParam.dec = prm.dec / (ppm > 0 ? ppm : 1.0);
        }
    }
}

bool MotionMgr::setJogParam(short axisId, const JogParam& param)
{
    if (!checkProfile(axisId)) return false;

    // 只更新内存
    m_gtsMgr->axisCfg()->axes[axisId - 1].jogParam = param;

    return true;
}


bool MotionMgr::startJogMotion(short profile, short direction)
{
    if (!checkProfile(profile)) return false;

    int idx = profile - 1;
    const JogParam& jog = m_gtsMgr->axisCfg()->axes[idx].jogParam;

    // ── 参数检查 ——
    if (jog.motionVel <= 0.0) {
        emit errorOccurred(profile, -1,
            QStringLiteral("轴%1 Jog速度无效 (dMotionVel = %2)，必须 > 0")
            .arg(profile).arg(jog.motionVel, 0, 'f', 3));
        return false;
    }
    if (jog.acc <= 0.0) {
        emit errorOccurred(profile, -1,
            QStringLiteral("轴%1 Jog加速度无效 (acc = %2)，必须 > 0")
            .arg(profile).arg(jog.acc, 0, 'f', 6));
        return false;
    }
    if (jog.dec <= 0.0) {
        emit errorOccurred(profile, -1,
            QStringLiteral("轴%1 Jog减速度无效 (dec = %2)，必须 > 0")
            .arg(profile).arg(jog.dec, 0, 'f', 6));
        return false;
    }

    // 设置为 Jog 模式
    m_lastError = GtsHal::prfJog(profile);
    if (m_lastError != 0) {
        emit errorOccurred(profile, m_lastError, QStringLiteral("prfJog: ") + lastErrorString());
        return false;
    }

    // 设置 Jog 参数 —— 软件层 mm/ms² → pulse/ms²
    double ppm = m_gtsMgr->pulsePerMm(profile);
    TJogPrm prm;
    prm.acc = jog.acc * ppm;
    prm.dec = jog.dec * ppm;
    prm.smooth = 0.0;
    m_lastError = GtsHal::setJogPrm(profile, prm);
    if (m_lastError != 0) {
        emit errorOccurred(profile, m_lastError, QStringLiteral("setJogPrm: ") + lastErrorString());
        return false;
    }

    // 设置速度 —— 软件层 mm/ms → pulse/ms
    double targetVel = (direction > 0) ? jog.motionVel * ppm : -jog.motionVel * ppm;

    m_lastError = GtsHal::setVel(profile, targetVel);
    if (m_lastError != 0) {
        emit errorOccurred(profile, m_lastError, QStringLiteral("setVel: ") + lastErrorString());
        return false;
    }

    // 启动运动
    long mask = 1L << (profile - 1);
    m_lastError = GtsHal::update(mask);
    if (m_lastError != 0) {
        emit errorOccurred(profile, m_lastError, QStringLiteral("update: ") + lastErrorString());
        return false;
    }

    emit logMessage(QStringLiteral("轴%1 Jog运动").arg(profile), Qt::darkGreen);
    return true;
}

bool MotionMgr::homeStart(short axis)
{
    if (!checkProfile(axis))
    {
        emit errorOccurred(axis, -1, QStringLiteral("轴%1 不存在").arg(axis));
        return false;
    }

    ConfigMgr* cfg = m_gtsMgr->configMgr();
    HomeMode mode = cfg->homeModeValue(axis);
    double homeVel = cfg->homeVel(axis);        // 速度 (mm/ms)
    double homeAcc = cfg->homeAcc(axis);        // 加速度 (mm/ms²)
    double homeRange = cfg->homeRange(axis);    // 搜索范围 (mm)
    double homeOffset = cfg->homeOffset(axis);  // 偏移量 (mm)

    // ── 参数检查 ──
    if (homeVel <= 0.0) {
        emit errorOccurred(axis, -1,
            QStringLiteral("轴%1 回零速度无效 (homeVel = %2)，必须 > 0")
            .arg(axis).arg(homeVel, 0, 'f', 3));
        return false;
    }
    if (homeAcc <= 0.0) {
        emit errorOccurred(axis, -1,
            QStringLiteral("轴%1 回零加速度无效 (homeAcc = %2)，必须 > 0")
            .arg(axis).arg(homeAcc, 0, 'f', 6));
        return false;
    }
    if (homeRange == 0.0) {
        emit errorOccurred(axis, -1,
            QStringLiteral("轴%1 回零搜索范围无效 (homeRange = %2)，不能为 0")
            .arg(axis).arg(homeRange, 0, 'f', 0));
        return false;
    }

    // ── 搜索方向 ──
    bool searchPos = false;
    QString modeName;
    switch (mode) {
    case HomeMode::HomeMode_nLlimit:   searchPos = false; modeName = QStringLiteral("负限位");  break;
    case HomeMode::HomeMode_pLlimit:   searchPos = true;  modeName = QStringLiteral("正限位");  break;
    case HomeMode::HomeMode_Home:      searchPos = false; modeName = QStringLiteral("原点DI");  break;
    case HomeMode::HomeMode_HomeIndex: searchPos = false; modeName = QStringLiteral("原点+Index"); break;
    case HomeMode::HomeMode_Index:     searchPos = false; modeName = QStringLiteral("Index");   break;
    default:
        emit errorOccurred(axis, -1,
            QStringLiteral("轴%1 回零模式未知 (mode = %2)")
            .arg(axis).arg(static_cast<int>(mode)));
        return false;
    }
    long searchStep = searchPos ? static_cast<long>(homeRange) : -static_cast<long>(homeRange);

    double ppm = m_gtsMgr->pulsePerMm(axis);   // pulse/mm
    long searchStepPulse = searchPos ? static_cast<long>(homeRange * ppm) : -static_cast<long>(homeRange * ppm);

    // 回零开始
    emit logMessage(QStringLiteral("回零开始 模式=%1 Vel=%2 Acc=%3 Range=%4 Offset=%5")
        .arg(modeName).arg(homeVel, 0, 'f', 3).arg(homeAcc, 0, 'f', 6)
        .arg(homeRange, 0, 'f', 0).arg(homeOffset, 0, 'f', 0),Qt::darkGreen);

    // ── 步骤1: 梯形模式 ──
    m_lastError = GtsHal::prfTrap(axis);
    if (m_lastError != 0) {
        emit errorOccurred(axis, m_lastError, QStringLiteral("prfTrap: ") + lastErrorString());
        return false;
    }

    // ── 步骤2: 梯形参数 ──
    TTrapPrm prm;
    prm.acc = homeAcc * ppm;
    prm.dec = homeAcc * ppm;
    prm.velStart = 0.0;
    prm.smoothTime = 0;
    m_lastError = GtsHal::setTrapPrm(axis, prm);
    if (m_lastError != 0) {
        emit errorOccurred(axis, m_lastError, QStringLiteral("setTrapPrm: ") + lastErrorString());
        return false;
    }

    // ── 步骤3: 确定检测方式 ──
    bool useCapture = false;
    short captureType = 0;
    bool useDI = false;
    short diType = 0;
    int   triggerBit = 0;

    switch (mode) {
    case HomeMode::HomeMode_nLlimit:
        break;
    case HomeMode::HomeMode_pLlimit:
        break;
    case HomeMode::HomeMode_Home:
        useDI = true;
        diType = MC_HOME;
        triggerBit = 1;
        break;
    case HomeMode::HomeMode_HomeIndex:
        useCapture = true;
        captureType = 1;
        break;
    case HomeMode::HomeMode_Index:
        useCapture = true;
        captureType = 2;
        break;
    default: break;
    }

    if (useCapture) {
        m_lastError = GT_SetCaptureMode(axis, captureType);
        if (m_lastError != 0) {
            emit errorOccurred(axis, m_lastError,
                QStringLiteral("轴%1 GT_SetCaptureMode(%2) 失败")
                .arg(axis).arg(captureType));
            return false;
        }
        emit logMessage(QStringLiteral("轴%1 ").arg(axis) + QStringLiteral("硬件捕获模式已配置 captureType=%1").arg(captureType), Qt::darkGreen);
    }
    else if (useDI) {
        emit logMessage(QStringLiteral("轴%1 ").arg(axis) + QStringLiteral("检测方式=DI轮询(原点信号)"), Qt::darkGreen);
    }
    else {
        emit logMessage(QStringLiteral("轴%1 ").arg(axis) + QStringLiteral("检测方式=限位DI轮询"), Qt::darkGreen);
    }

    // ── 步骤4: 启动搜索运动 ──
    double curPos = profilePos(axis);
    long curPulse = static_cast<long>(curPos * ppm);
    long targetPulse = curPulse + searchStepPulse;
    long mask = 1L << (axis - 1);

    emit logMessage(QStringLiteral("轴%1 ").arg(axis) + QStringLiteral("启动搜索运动 curPos=%1mm targetPos=%2mm step=%3mm")
        .arg(curPos, 0, 'f', 1).arg(curPos + homeRange * (searchPos ? 1 : -1), 0, 'f', 1).arg(homeRange, 0, 'f', 1), Qt::darkGreen);

    m_lastError = GtsHal::setPos(axis, targetPulse);
    if (m_lastError != 0) {
        emit errorOccurred(axis, m_lastError, QStringLiteral("setPos: ") + lastErrorString());
        return false;
    }
    m_lastError = GtsHal::setVel(axis, homeVel * ppm);
    if (m_lastError != 0) {
        emit errorOccurred(axis, m_lastError, QStringLiteral("setVel: ") + lastErrorString());
        return false;
    }
    m_lastError = GtsHal::update(mask);
    if (m_lastError != 0) {
        emit errorOccurred(axis, m_lastError, QStringLiteral("update: ") + lastErrorString());
        return false;
    }
    emit logMessage(QStringLiteral("轴%1 ").arg(axis) + QStringLiteral("搜索运动已启动 GT_Update OK"), Qt::darkGreen);

    // ── 步骤5: 等待触发 ──
    long offsetPulse = static_cast<long>(homeOffset * ppm);   // mm → pulse

    if (useDI) {
        // === DI 检测模式(模式2: Home) ===
        emit logMessage(QStringLiteral("轴%1 ").arg(axis) + QStringLiteral("等待原点DI触发..."), Qt::darkGreen);
        emit logMessage(QStringLiteral("等待原点DI触发..."),Qt::darkGreen);
        long sts = 0;
        long diVal = 0;
        int axisBit = axis - 1;

        do {
            GtsHal::getSts(axis, &sts);
            GtsHal::getDi(diType, &diVal);
            QCoreApplication::processEvents();

            if (!(sts & 0x400)) {
                emit errorOccurred(axis, -1,
                    QStringLiteral("轴%1 回零失败:运动停止但未检测到原点信号 sts=0x%2 di=0x%3")
                    .arg(axis).arg(sts, 0, 16).arg(diVal, 0, 16));
                return false;
            }
        } while (((diVal >> axisBit) & 1) != triggerBit);

        emit logMessage(QStringLiteral("轴%1 ").arg(axis) + QStringLiteral("原点DI触发! di=0x%1 立即停止").arg(diVal, 0, 16), Qt::darkGreen);
        emit logMessage(QStringLiteral("原点DI触发! di=0x%1 立即停止").arg(diVal, 0, 16), Qt::darkGreen);

        stop(axis, 0);
        do {
            GtsHal::getSts(axis, &sts);
            QCoreApplication::processEvents();
        } while (sts & 0x400);
        emit logMessage(QStringLiteral("轴%1 ").arg(axis) + QStringLiteral("轴已停止"), Qt::darkGreen);

        double capPos = profilePos(axis);
        long capPulse = static_cast<long>(capPos * ppm);
        emit logMessage(QStringLiteral("轴%1 ").arg(axis) + QStringLiteral("触发位置=%1mm offset=%2mm → 移动到=%3pulse")
            .arg(capPos, 0, 'f', 1).arg(homeOffset, 0, 'f', 1).arg(capPulse + offsetPulse), Qt::darkGreen);

        long finalTarget = capPulse + offsetPulse;
        m_lastError = GtsHal::setPos(axis, finalTarget);
        if (m_lastError != 0) {
            emit errorOccurred(axis, m_lastError, QStringLiteral("setPos: ") + lastErrorString());
            return false;
        }
        m_lastError = GtsHal::update(mask);
        if (m_lastError != 0) {
            emit errorOccurred(axis, m_lastError, QStringLiteral("update: ") + lastErrorString());
            return false;
        }
        waitMotionDone(axis);
        emit logMessage(QStringLiteral("轴%1 ").arg(axis) + QStringLiteral("偏移移动完成"), Qt::darkGreen);
    }
    else if (useCapture) {
        // === 硬件捕获模式(模式3/4: Index) ===
        emit logMessage(QStringLiteral("轴%1 ").arg(axis) + QStringLiteral("等待硬件捕获(Index/Z相)..."), Qt::darkGreen);
        short capture = 0;
        long  capPos = 0;
        long  sts = 0;

        do {
            GtsHal::getSts(axis, &sts);
            GT_GetCaptureStatus(axis, &capture, &capPos);
            QCoreApplication::processEvents();

            if (!(sts & 0x400)) {
                emit errorOccurred(axis, -1,
                    QStringLiteral("轴%1 回零失败:运动停止但未捕获到信号 sts=0x%2 capture=%3")
                    .arg(axis).arg(sts, 0, 16).arg(capture));
                return false;
            }
        } while (capture == 0);

        emit logMessage(QStringLiteral("轴%1 ").arg(axis) + QStringLiteral("捕获 capPos=%1mm → 移动到=%2pulse")
            .arg(capPos / ppm, 0, 'f', 1).arg(capPos + offsetPulse), Qt::darkGreen);

        long finalTarget = capPos + offsetPulse;
        m_lastError = GtsHal::setPos(axis, finalTarget);
        if (m_lastError != 0) {
            emit errorOccurred(axis, m_lastError, QStringLiteral("setPos: ") + lastErrorString());
            return false;
        }
        m_lastError = GtsHal::update(mask);
        if (m_lastError != 0) {
            emit errorOccurred(axis, m_lastError, QStringLiteral("update: ") + lastErrorString());
            return false;
        }
        waitMotionDone(axis);
        emit logMessage(QStringLiteral("轴%1 ").arg(axis) + QStringLiteral("偏移移动完成"), Qt::darkGreen);
    }
    else {
        // === 限位模式(模式0/1)—— 与 500ms 定时器同机制的 DI 检测 ===
        QString lmtName = (mode == HomeMode::HomeMode_nLlimit) ? QStringLiteral("负限位") : QStringLiteral("正限位");
        emit logMessage(QStringLiteral("轴%1 ").arg(axis) + QStringLiteral("等待%1DI触发...").arg(lmtName), Qt::darkGreen);

        long sts = 0;
        long diVal = 0;
        short diType = (mode == HomeMode::HomeMode_nLlimit)
            ? MC_LIMIT_NEGATIVE
            : MC_LIMIT_POSITIVE;
        int axisBit = axis - 1;

        do {
            GtsHal::getSts(axis, &sts);
            GtsHal::getDi(diType, &diVal);
            QCoreApplication::processEvents();

            if (!(sts & 0x400)) break;
        } while (((diVal >> axisBit) & 1) == 0);

        GtsHal::getDi(diType, &diVal);

        if (((diVal >> axisBit) & 1) == 0) {
            emit errorOccurred(axis, -1,
                QStringLiteral("轴%1 回零失败:未触发限位"
                    "(搜索范围=%2 mm, sts=0x%3, di=0x%4)")
                .arg(axis).arg(static_cast<long>(homeRange)).arg(sts, 0, 16).arg(diVal, 0, 16));
            return false;
        }

        emit logMessage(QStringLiteral("轴%1 ").arg(axis) + QStringLiteral("%1DI触发! di=0x%2 立即停止")
            .arg(lmtName).arg(diVal, 0, 16), Qt::darkGreen);

        stop(axis, 0);
        do {
            GtsHal::getSts(axis, &sts);
            QCoreApplication::processEvents();
        } while (sts & 0x400);
        emit logMessage(QStringLiteral("轴%1 ").arg(axis) + QStringLiteral("轴已停止,清除限位状态"), Qt::darkGreen);

        GtsHal::clrSts(axis, axis);

        long escapeStep = searchPos ? -offsetPulse : offsetPulse;
        curPos = profilePos(axis);
        long curPulseLimit = static_cast<long>(curPos * ppm);
        emit logMessage(QStringLiteral("轴%1 ").arg(axis) + QStringLiteral("脱离限位 curPos=%1mm escape=%2mm → target=%3pulse")
            .arg(curPos, 0, 'f', 1).arg(homeOffset * (searchPos ? -1 : 1), 0, 'f', 1).arg(curPulseLimit + escapeStep), Qt::darkGreen);

        m_lastError = GtsHal::setPos(axis, curPulseLimit + escapeStep);
        if (m_lastError != 0) {
            emit errorOccurred(axis, m_lastError, QStringLiteral("setPos: ") + lastErrorString());
            return false;
        }
        m_lastError = GtsHal::update(mask);
        if (m_lastError != 0) {
            emit errorOccurred(axis, m_lastError, QStringLiteral("update: ") + lastErrorString());
            return false;
        }
        waitMotionDone(axis);
        emit logMessage(QStringLiteral("轴%1 ").arg(axis) + QStringLiteral("脱离限位+偏移完成"), Qt::darkGreen);
    }

    // ── 步骤6: 位置清零 ──
    emit logMessage(QStringLiteral("轴%1 ").arg(axis) + QStringLiteral("位置清零"), Qt::darkGreen);
    m_lastError = GtsHal::zeroPos(axis, axis);
    if (m_lastError != 0) {
        emit errorOccurred(axis, m_lastError, QStringLiteral("zeroPos: ") + lastErrorString());
        return false;
    }

    // 清除状态
    QThread::msleep(1000);
    GtsHal::clrSts(axis, axis);

    emit logMessage(QStringLiteral("轴%1 ").arg(axis) + QStringLiteral("回零完成"), Qt::darkGreen);
    emit motionDone(axis);
    return true;
}



bool MotionMgr::checkProfile(short profile) const
{
    if (profile < 1 || profile > m_gtsMgr->axisCount()) {
        return false;
    }
    return true;
}

// 改动：stepSize 类型从 long → double
bool MotionMgr::singleTrapMotion(short profile, double stepSize,
    double acc, double dec, int smoothTime, double vel)
{
    // 设为点位模式
    m_lastError = GtsHal::prfTrap(profile);
    if (m_lastError != 0) {
        emit errorOccurred(profile, m_lastError, QStringLiteral("prfTrap: ") + lastErrorString());
        return false;
    }

    // 设置梯形参数 —— 软件层 mm/ms² → pulse/ms²
    TTrapPrm prm = {};
    double ppm = m_gtsMgr->pulsePerMm(profile);
    prm.acc = acc * ppm;
    prm.dec = dec * ppm;
    prm.smoothTime = static_cast<short>(smoothTime);

    m_lastError = GtsHal::setTrapPrm(profile, prm);
    if (m_lastError != 0) {
        emit errorOccurred(profile, m_lastError, QStringLiteral("setTrapPrm: ") + lastErrorString());
        return false;
    }

    // ── 目标位置 = 当前位置 + 步长 ──
    double curPos = profilePos(profile);           // 板卡返回 mm
    long targetPulse = static_cast<long>(curPos * ppm) + static_cast<long>(stepSize * ppm);
    m_lastError = GtsHal::setPos(profile, targetPulse);
    if (m_lastError != 0) {
        emit errorOccurred(profile, m_lastError, QStringLiteral("setPos: ") + lastErrorString());
        return false;
    }

    // 设置速度 —— 软件层 mm/ms → pulse/ms
    m_lastError = GtsHal::setVel(profile, vel * ppm);
    if (m_lastError != 0) {
        emit errorOccurred(profile, m_lastError, QStringLiteral("setVel: ") + lastErrorString());
        return false;
    }

    // 启动运动
    long mask = 1L << (profile - 1);
    m_lastError = GtsHal::update(mask);
    if (m_lastError != 0) {
        emit errorOccurred(profile, m_lastError, QStringLiteral("update: ") + lastErrorString());
        return false;
    }

    return true;
}


// 等待运动完成(规划停止 bit10 = 0x400)
void MotionMgr::waitMotionDone(short profile)
{
    long sts = 0;
    do {
        GtsHal::getSts(profile, &sts);
        QCoreApplication::processEvents();  // 保持界面响应
    } while (sts & 0x400);  // 0x400 = 规划中,运动未完成
}


bool MotionMgr::setProfilePos(short profile, long pos) 
{
    if (!checkProfile(profile)) return false;
    m_lastError = GtsHal::setPrfPos(profile, pos);
    if (m_lastError != 0) {
        emit errorOccurred(profile, m_lastError, QStringLiteral("setPrfPos: ") + lastErrorString());
        return false;
    }
    return true;
}

double MotionMgr::profilePos(short profile) const 
{
    if (!checkProfile(profile)) return 0.0;
    double pos = 0.0;
    GtsHal::getPrfPos(profile, &pos);   // 返回 pulse（GTS 当量=1:1）
    double ppm = m_gtsMgr->pulsePerMm(profile);
    return (ppm > 0.0) ? pos / ppm : pos;
}

double MotionMgr::profileVel(short profile) const 
{
    if (!checkProfile(profile)) return 0.0;
    double vel = 0.0;
    GtsHal::getPrfVel(profile, &vel);   // 返回 pulse/ms（GTS 当量=1:1）
    double ppm = m_gtsMgr->pulsePerMm(profile);
    return (ppm > 0.0) ? vel / ppm : vel;
}

double MotionMgr::profileAcc(short profile) const 
{
    if (!checkProfile(profile)) return 0.0;
    double acc = 0.0;
    GtsHal::getPrfAcc(profile, &acc);
    return acc;
}

long MotionMgr::profileMode(short profile) const 
{
    if (!checkProfile(profile)) return -1;
    long mode = 0;
    GtsHal::getPrfMode(profile, &mode);
    return mode;
}

double MotionMgr::axisProfilePos(short axis) const 
{
    if (!checkProfile(axis)) return 0.0;
    double pos = 0.0;
    GtsHal::getAxisPrfPos(axis, &pos);
    return pos;
}

double MotionMgr::axisProfileVel(short axis) const 
{
    if (!checkProfile(axis)) return 0.0;
    double vel = 0.0;
    GtsHal::getAxisPrfVel(axis, &vel);
    return vel;
}

double MotionMgr::axisProfileAcc(short axis) const 
{
    if (!checkProfile(axis)) return 0.0;
    double acc = 0.0;
    GtsHal::getAxisPrfAcc(axis, &acc);
    return acc;
}

bool MotionMgr::setTargetPos(short profile, long pos) 
{
    if (!checkProfile(profile)) return false;
    m_lastError = GtsHal::setPos(profile, pos);
    if (m_lastError != 0) {
        emit errorOccurred(profile, m_lastError, QStringLiteral("setPos: ") + lastErrorString());
        return false;
    }
    return true;
}

bool MotionMgr::setTargetVel(short profile, double vel) 
{
    if (!checkProfile(profile)) return false;
    m_lastError = GtsHal::setVel(profile, vel);
    if (m_lastError != 0) {
        emit errorOccurred(profile, m_lastError, QStringLiteral("setVel: ") + lastErrorString());
        return false;
    }
    return true;
}

long MotionMgr::targetPos(short profile) const 
{
    if (!checkProfile(profile)) return 0;
    long pos = 0;
    GtsHal::getPos(profile, &pos);
    return pos;
}

double MotionMgr::targetVel(short profile) const 
{
    if (!checkProfile(profile)) return 0.0;
    double vel = 0.0;
    GtsHal::getVel(profile, &vel);
    return vel;
}

bool MotionMgr::update(long mask) 
{
    m_lastError = GtsHal::update(mask);
    if (m_lastError != 0) {
        emit errorOccurred(-1, m_lastError, QStringLiteral("update: ") + lastErrorString());
        return false;
    }
    return true;
}

bool MotionMgr::setProfileScale(short axis, long alpha, long beta) 
{
    if (!checkProfile(axis)) return false;
    m_lastError = GtsHal::setProfileScale(axis, alpha, beta);
    return m_lastError == 0;
}

bool MotionMgr::getProfileScale(short axis, long& alpha, long& beta) const 
{
    if (!checkProfile(axis)) return false;
    m_lastError = GtsHal::getProfileScale(axis, &alpha, &beta);
    return m_lastError == 0;
}


bool MotionMgr::setTrapMode(short profile) 
{
    if (!checkProfile(profile)) return false;
    m_lastError = GtsHal::prfTrap(profile);
    if (m_lastError != 0) {
        emit errorOccurred(profile, m_lastError, QStringLiteral("prfTrap: ") + lastErrorString());
        return false;
    }
    return true;
}

bool MotionMgr::setTrapParams(short profile, const TTrapPrm& prm) 
{
    if (!checkProfile(profile)) return false;
    m_lastError = GtsHal::setTrapPrm(profile, prm);
    if (m_lastError != 0) {
        emit errorOccurred(profile, m_lastError, QStringLiteral("setTrapPrm: ") + lastErrorString());
        return false;
    }
    return true;
}

bool MotionMgr::getTrapParams(short profile, TTrapPrm& prm) const 
{
    if (!checkProfile(profile)) return false;
    m_lastError = GtsHal::getTrapPrm(profile, &prm);
    return m_lastError == 0;
}

bool MotionMgr::getTrapTime(short profile, TTrapTime& time) const 
{
    if (!checkProfile(profile)) return false;
    m_lastError = GtsHal::getTrapTime(profile, &time);
    return m_lastError == 0;
}


bool MotionMgr::setJogMode(short profile) 
{
    if (!checkProfile(profile)) return false;
    m_lastError = GtsHal::prfJog(profile);
    if (m_lastError != 0) {
        emit errorOccurred(profile, m_lastError, QStringLiteral("prfJog: ") + lastErrorString());
        return false;
    }
    return true;
}

bool MotionMgr::setJogParams(short profile, const TJogPrm& prm) 
{
    if (!checkProfile(profile)) return false;
    m_lastError = GtsHal::setJogPrm(profile, prm);
    if (m_lastError != 0) {
        emit errorOccurred(profile, m_lastError, QStringLiteral("setJogPrm: ") + lastErrorString());
        return false;
    }
    return true;
}

bool MotionMgr::getJogParams(short profile, TJogPrm& prm) const 
{
    if (!checkProfile(profile)) return false;
    m_lastError = GtsHal::getJogPrm(profile, &prm);
    return m_lastError == 0;
}


bool MotionMgr::moveAbsolute(short profile, long pos, double vel, double acc, double dec) 
{
    if (!checkProfile(profile)) return false;

    TMoveAbsolutePrm prm;
    prm.pos = pos;
    prm.vel = vel;
    prm.acc = acc;
    prm.dec = dec;

    m_lastError = GtsHal::moveAbsolute(profile, prm);
    if (m_lastError != 0) {
        emit errorOccurred(profile, m_lastError, QStringLiteral("moveAbsolute: ") + lastErrorString());
        return false;
    }
    return true;
}

bool MotionMgr::moveVelocity(short profile, double vel, double acc) 
{
    if (!checkProfile(profile)) return false;

    TMoveVelocityPrm prm;
    prm.vel = vel;
    prm.acc = acc;

    m_lastError = GtsHal::moveVelocity(profile, prm);
    if (m_lastError != 0) {
        emit errorOccurred(profile, m_lastError, QStringLiteral("moveVelocity: ") + lastErrorString());
        return false;
    }
    return true;
}

bool MotionMgr::getMoveAbsoluteParams(short profile, TMoveAbsolutePrm& prm) const 
{
    if (!checkProfile(profile)) return false;
    m_lastError = GtsHal::getMoveAbsolute(profile, &prm);
    return m_lastError == 0;
}

bool MotionMgr::getMoveVelocityParams(short profile, TMoveVelocityPrm& prm) const 
{
    if (!checkProfile(profile)) return false;
    m_lastError = GtsHal::getMoveVelocity(profile, &prm);
    return m_lastError == 0;
}


bool MotionMgr::setPtMode(short profile, short mode) 
{
    if (!checkProfile(profile)) return false;
    m_lastError = GtsHal::prfPt(profile, mode);
    if (m_lastError != 0) {
        emit errorOccurred(profile, m_lastError, QStringLiteral("prfPt: ") + lastErrorString());
        return false;
    }
    return true;
}

bool MotionMgr::setPtLoop(short profile, long loop) 
{
    if (!checkProfile(profile)) return false;
    m_lastError = GtsHal::setPtLoop(profile, loop);
    return m_lastError == 0;
}

long MotionMgr::getPtLoop(short profile) const 
{
    if (!checkProfile(profile)) return 0;
    long loop = 0;
    GtsHal::getPtLoop(profile, &loop);
    return loop;
}

short MotionMgr::ptFreeSpace(short profile, short fifo) const 
{
    if (!checkProfile(profile)) return -1;
    short space = 0;
    GtsHal::ptSpace(profile, &space, fifo);
    return space;
}

bool MotionMgr::ptAddData(short profile, double pos, long time, short type, short fifo) 
{
    if (!checkProfile(profile)) return false;
    m_lastError = GtsHal::ptData(profile, pos, time, type, fifo);
    if (m_lastError != 0) {
        emit errorOccurred(profile, m_lastError, QStringLiteral("ptData: ") + lastErrorString());
        return false;
    }
    return true;
}

bool MotionMgr::ptAddDataWithSeg(short profile, double pos, long time,
    short type, long segNum, short fifo) 
{
    if (!checkProfile(profile)) return false;
    m_lastError = GtsHal::ptDataWN(profile, pos, time, type, segNum, fifo);
    if (m_lastError != 0) {
        emit errorOccurred(profile, m_lastError, QStringLiteral("ptDataWN: ") + lastErrorString());
        return false;
    }
    return true;
}

bool MotionMgr::ptClear(short profile, short fifo) 
{
    if (!checkProfile(profile)) return false;
    m_lastError = GtsHal::ptClear(profile, fifo);
    return m_lastError == 0;
}

bool MotionMgr::ptStart(long mask, long option) 
{
    m_lastError = GtsHal::ptStart(mask, option);
    if (m_lastError != 0) {
        emit errorOccurred(-1, m_lastError, QStringLiteral("ptStart: ") + lastErrorString());
        return false;
    }
    return true;
}

bool MotionMgr::setPtMemory(short profile, short memory) 
{
    if (!checkProfile(profile)) return false;
    m_lastError = GtsHal::setPtMemory(profile, memory);
    return m_lastError == 0;
}

short MotionMgr::getPtMemory(short profile) const 
{
    if (!checkProfile(profile)) return -1;
    short mem = 0;
    GtsHal::getPtMemory(profile, &mem);
    return mem;
}

long MotionMgr::ptCurrentSegment(short profile) const 
{
    if (!checkProfile(profile)) return -1;
    long seg = 0;
    GtsHal::ptGetSegNum(profile, &seg);
    return seg;
}

bool MotionMgr::ptAddDoBit(short profile, short doType, short index, short value, short fifo) 
{
    if (!checkProfile(profile)) return false;
    m_lastError = GtsHal::ptDoBit(profile, doType, index, value, fifo);
    if (m_lastError != 0) {
        emit errorOccurred(profile, m_lastError, QStringLiteral("ptDoBit: ") + lastErrorString());
        return false;
    }
    return true;
}

bool MotionMgr::ptAddAo(short profile, short aoType, short index, double value, short fifo) 
{
    if (!checkProfile(profile)) return false;
    m_lastError = GtsHal::ptAo(profile, aoType, index, value, fifo);
    if (m_lastError != 0) {
        emit errorOccurred(profile, m_lastError, QStringLiteral("ptAo: ") + lastErrorString());
        return false;
    }
    return true;
}


bool MotionMgr::setGearMode(short profile, short dir) 
{
    if (!checkProfile(profile)) return false;
    m_lastError = GtsHal::prfGear(profile, dir);
    if (m_lastError != 0) {
        emit errorOccurred(profile, m_lastError, QStringLiteral("prfGear: ") + lastErrorString());
        return false;
    }
    return true;
}

bool MotionMgr::setGearMaster(short profile, short masterIndex, short masterType, short masterItem) 
{
    if (!checkProfile(profile)) return false;
    m_lastError = GtsHal::setGearMaster(profile, masterIndex, masterType, masterItem);
    if (m_lastError != 0) {
        emit errorOccurred(profile, m_lastError, QStringLiteral("setGearMaster: ") + lastErrorString());
        return false;
    }
    return true;
}

bool MotionMgr::getGearMaster(short profile, short& masterIndex,
    short& masterType, short& masterItem) const 
{
    if (!checkProfile(profile)) return false;
    m_lastError = GtsHal::getGearMaster(profile, &masterIndex, &masterType, &masterItem);
    return m_lastError == 0;
}

bool MotionMgr::setGearRatio(short profile, long masterEven, long slaveEven, long masterSlope) 
{
    if (!checkProfile(profile)) return false;
    m_lastError = GtsHal::setGearRatio(profile, masterEven, slaveEven, masterSlope);
    if (m_lastError != 0) {
        emit errorOccurred(profile, m_lastError, QStringLiteral("setGearRatio: ") + lastErrorString());
        return false;
    }
    return true;
}

bool MotionMgr::getGearRatio(short profile, long& masterEven, long& slaveEven, long& masterSlope) const 
{
    if (!checkProfile(profile)) return false;
    m_lastError = GtsHal::getGearRatio(profile, &masterEven, &slaveEven, &masterSlope);
    return m_lastError == 0;
}

bool MotionMgr::gearStart(long mask) 
{
    m_lastError = GtsHal::gearStart(mask);
    if (m_lastError != 0) {
        emit errorOccurred(-1, m_lastError, QStringLiteral("gearStart: ") + lastErrorString());
        return false;
    }
    return true;
}

bool MotionMgr::setGearEvent(short profile, short event, long startPara0, long startPara1) 
{
    if (!checkProfile(profile)) return false;
    m_lastError = GtsHal::setGearEvent(profile, event, startPara0, startPara1);
    if (m_lastError != 0) {
        emit errorOccurred(profile, m_lastError, QStringLiteral("setGearEvent: ") + lastErrorString());
        return false;
    }
    return true;
}

bool MotionMgr::getGearEvent(short profile, short& event, long& startPara0, long& startPara1) const 
{
    if (!checkProfile(profile)) return false;
    m_lastError = GtsHal::getGearEvent(profile, &event, &startPara0, &startPara1);
    return m_lastError == 0;
}


bool MotionMgr::setFollowMode(short profile, short dir) 
{
    if (!checkProfile(profile)) return false;
    m_lastError = GtsHal::prfFollow(profile, dir);
    if (m_lastError != 0) {
        emit errorOccurred(profile, m_lastError, QStringLiteral("prfFollow: ") + lastErrorString());
        return false;
    }
    return true;
}

bool MotionMgr::setFollowMaster(short profile, short masterIndex, short masterType, short masterItem) 
{
    if (!checkProfile(profile)) return false;
    m_lastError = GtsHal::setFollowMaster(profile, masterIndex, masterType, masterItem);
    if (m_lastError != 0) {
        emit errorOccurred(profile, m_lastError, QStringLiteral("setFollowMaster: ") + lastErrorString());
        return false;
    }
    return true;
}

bool MotionMgr::getFollowMaster(short profile, short& masterIndex,
    short& masterType, short& masterItem) const 
{
    if (!checkProfile(profile)) return false;
    m_lastError = GtsHal::getFollowMaster(profile, &masterIndex, &masterType, &masterItem);
    return m_lastError == 0;
}

bool MotionMgr::setFollowLoop(short profile, long loop) 
{
    if (!checkProfile(profile)) return false;
    m_lastError = GtsHal::setFollowLoop(profile, loop);
    return m_lastError == 0;
}

long MotionMgr::getFollowLoop(short profile) const 
{
    if (!checkProfile(profile)) return 0;
    long loop = 0;
    GtsHal::getFollowLoop(profile, &loop);
    return loop;
}

bool MotionMgr::setFollowEvent(short profile, short event, short masterDir, long pos) 
{
    if (!checkProfile(profile)) return false;
    m_lastError = GtsHal::setFollowEvent(profile, event, masterDir, pos);
    if (m_lastError != 0) {
        emit errorOccurred(profile, m_lastError, QStringLiteral("setFollowEvent: ") + lastErrorString());
        return false;
    }
    return true;
}

bool MotionMgr::getFollowEvent(short profile, short& event, short& masterDir, long& pos) const 
{
    if (!checkProfile(profile)) return false;
    m_lastError = GtsHal::getFollowEvent(profile, &event, &masterDir, &pos);
    return m_lastError == 0;
}

short MotionMgr::followFreeSpace(short profile, short fifo) const 
{
    if (!checkProfile(profile)) return -1;
    short space = 0;
    GtsHal::followSpace(profile, &space, fifo);
    return space;
}

bool MotionMgr::followAddData(short profile, long masterSegment, double slaveSegment,
    short type, short fifo) 
{
    if (!checkProfile(profile)) return false;
    m_lastError = GtsHal::followData(profile, masterSegment, slaveSegment, type, fifo);
    if (m_lastError != 0) {
        emit errorOccurred(profile, m_lastError, QStringLiteral("followData: ") + lastErrorString());
        return false;
    }
    return true;
}

bool MotionMgr::followClear(short profile, short fifo) 
{
    if (!checkProfile(profile)) return false;
    m_lastError = GtsHal::followClear(profile, fifo);
    return m_lastError == 0;
}

bool MotionMgr::followStart(long mask, long option) 
{
    m_lastError = GtsHal::followStart(mask, option);
    if (m_lastError != 0) {
        emit errorOccurred(-1, m_lastError, QStringLiteral("followStart: ") + lastErrorString());
        return false;
    }
    return true;
}

bool MotionMgr::followSwitch(long mask) 
{
    m_lastError = GtsHal::followSwitch(mask);
    if (m_lastError != 0) {
        emit errorOccurred(-1, m_lastError, QStringLiteral("followSwitch: ") + lastErrorString());
        return false;
    }
    return true;
}

bool MotionMgr::setFollowMemory(short profile, short memory) 
{
    if (!checkProfile(profile)) return false;
    m_lastError = GtsHal::setFollowMemory(profile, memory);
    return m_lastError == 0;
}

short MotionMgr::getFollowMemory(short profile) const 
{
    if (!checkProfile(profile)) return -1;
    short mem = 0;
    GtsHal::getFollowMemory(profile, &mem);
    return mem;
}

bool MotionMgr::getFollowStatus(short profile, short& fifoNum, short& switchStatus) const 
{
    if (!checkProfile(profile)) return false;
    m_lastError = GtsHal::getFollowStatus(profile, &fifoNum, &switchStatus);
    return m_lastError == 0;
}


bool MotionMgr::setPvtMode(short profile) 
{
    if (!checkProfile(profile)) return false;
    m_lastError = GtsHal::prfPvt(profile);
    if (m_lastError != 0) {
        emit errorOccurred(profile, m_lastError, QStringLiteral("prfPvt: ") + lastErrorString());
        return false;
    }
    return true;
}

bool MotionMgr::setPvtLoop(short profile, long loop) 
{
    if (!checkProfile(profile)) return false;
    m_lastError = GtsHal::setPvtLoop(profile, loop);
    return m_lastError == 0;
}

bool MotionMgr::getPvtLoop(short profile, long& loopCount, long& loop) const 
{
    if (!checkProfile(profile)) return false;
    m_lastError = GtsHal::getPvtLoop(profile, &loopCount, &loop);
    return m_lastError == 0;
}

bool MotionMgr::pvtStatus(short profile, short& tableId, double& time) const 
{
    if (!checkProfile(profile)) return false;
    m_lastError = GtsHal::pvtStatus(profile, &tableId, &time);
    return m_lastError == 0;
}

bool MotionMgr::pvtTableClear(short tableId) 
{
    m_lastError = GtsHal::pvtTableClear(tableId);
    return m_lastError == 0;
}

bool MotionMgr::pvtStart(long mask) 
{
    m_lastError = GtsHal::pvtStart(mask);
    if (m_lastError != 0) {
        emit errorOccurred(-1, m_lastError, QStringLiteral("pvtStart: ") + lastErrorString());
        return false;
    }
    return true;
}

bool MotionMgr::pvtTableSelect(short profile, short tableId) 
{
    if (!checkProfile(profile)) return false;
    m_lastError = GtsHal::pvtTableSelect(profile, tableId);
    return m_lastError == 0;
}

bool MotionMgr::pvtTableSet(short tableId, long count, double* time, double* pos, double* vel) 
{
    m_lastError = GtsHal::pvtTable(tableId, count, time, pos, vel);
    if (m_lastError != 0) {
        emit errorOccurred(-1, m_lastError, QStringLiteral("pvtTable: ") + lastErrorString());
        return false;
    }
    return true;
}

bool MotionMgr::pvtTableSetEx(short tableId, long count, double* time, double* pos,
    double* velBegin, double* velEnd) 
{
    m_lastError = GtsHal::pvtTableEx(tableId, count, time, pos, velBegin, velEnd);
    if (m_lastError != 0) {
        emit errorOccurred(-1, m_lastError, QStringLiteral("pvtTableEx: ") + lastErrorString());
        return false;
    }
    return true;
}

bool MotionMgr::pvtTableSetComplete(short tableId, long count, double* time, double* pos,
    double* a, double* b, double* c,
    double velBegin, double velEnd) 
{
    m_lastError = GtsHal::pvtTableComplete(tableId, count, time, pos, a, b, c, velBegin, velEnd);
    if (m_lastError != 0) {
        emit errorOccurred(-1, m_lastError, QStringLiteral("pvtTableComplete: ") + lastErrorString());
        return false;
    }
    return true;
}

bool MotionMgr::pvtTableSetPercent(short tableId, long count, double* time, double* pos,
    double* percent, double velBegin) 
{
    m_lastError = GtsHal::pvtTablePercent(tableId, count, time, pos, percent, velBegin);
    if (m_lastError != 0) {
        emit errorOccurred(-1, m_lastError, QStringLiteral("pvtTablePercent: ") + lastErrorString());
        return false;
    }
    return true;
}


bool MotionMgr::moveTo(short profile, long pos, double vel, double acc, double dec) 
{
    if (!checkProfile(profile)) return false;

    // 设置梯形模式
    m_lastError = GtsHal::prfTrap(profile);
    if (m_lastError != 0) {
        emit errorOccurred(profile, m_lastError, QStringLiteral("prfTrap: ") + lastErrorString());
        return false;
    }

    // 设置梯形参数
    TTrapPrm trapPrm;
    trapPrm.acc = acc;
    trapPrm.dec = dec;
    trapPrm.velStart = 0.0;
    trapPrm.smoothTime = 0.0;

    m_lastError = GtsHal::setTrapPrm(profile, trapPrm);
    if (m_lastError != 0) {
        emit errorOccurred(profile, m_lastError, QStringLiteral("setTrapPrm: ") + lastErrorString());
        return false;
    }

    // 设置目标位置和速度
    m_lastError = GtsHal::setPos(profile, pos);
    if (m_lastError != 0) {
        emit errorOccurred(profile, m_lastError, QStringLiteral("setPos: ") + lastErrorString());
        return false;
    }

    m_lastError = GtsHal::setVel(profile, vel);
    if (m_lastError != 0) {
        emit errorOccurred(profile, m_lastError, QStringLiteral("setVel: ") + lastErrorString());
        return false;
    }

    // 启动运动
    m_lastError = GtsHal::update(1L << profile);
    if (m_lastError != 0) {
        emit errorOccurred(profile, m_lastError, QStringLiteral("update: ") + lastErrorString());
        return false;
    }

    emit motionDone(profile);
    return true;
}

bool MotionMgr::jog(short profile, double vel, double acc)
{
    if (!checkProfile(profile)) return false;

    // 设置为 Jog 模式
    m_lastError = GtsHal::prfJog(profile);
    if (m_lastError != 0) {
        emit errorOccurred(profile, m_lastError, QStringLiteral("prfJog: ") + lastErrorString());
        return false;
    }

    // 设置 Jog 参数
    TJogPrm jogPrm;
    jogPrm.acc = acc;
    jogPrm.dec = acc;
    jogPrm.smooth = 0.0;

    m_lastError = GtsHal::setJogPrm(profile, jogPrm);
    if (m_lastError != 0) {
        emit errorOccurred(profile, m_lastError, QStringLiteral("setJogPrm: ") + lastErrorString());
        return false;
    }

    m_lastError = GtsHal::setVel(profile, vel);
    if (m_lastError != 0) {
        emit errorOccurred(profile, m_lastError, QStringLiteral("setVel: ") + lastErrorString());
        return false;
    }

    // 启动
    m_lastError = GtsHal::update(1L << (profile - 1));
    if (m_lastError != 0) {
        emit errorOccurred(profile, m_lastError, QStringLiteral("update: ") + lastErrorString());
        return false;
    }

    return true;
}


bool MotionMgr::stop(short profile, long option) 
{
    if (!checkProfile(profile)) return false;
    long mask = 1L << (profile - 1);
    m_lastError = GtsHal::stop(mask, option);
    if (m_lastError != 0) {
        emit errorOccurred(profile, m_lastError, QStringLiteral("stop: ") + lastErrorString());
        return false;
    }
    return true;
}

QString MotionMgr::lastErrorString() const 
{
    return GtsErrorToString(m_lastError);
}
