#include <QJsonDocument>             
#include <QJsonObject>               
#include <QJsonArray>                
#include <QFile>                     
#include <QDir>                      
#include <QCoreApplication>          

#include "GtsMgr.h"
#include "GtsConfigMgr.h"
#include "GtsAxisMgr.h"


ConfigMgr::ConfigMgr(QObject* parent)
    : QObject(parent)
{
}

ConfigMgr::~ConfigMgr() 
{
    m_axisMgr = nullptr;
    m_axisCfg = nullptr;
}

bool ConfigMgr::isValidAxis(short axis) const 
{
    return (axis >= 0 && axis < 8);
}

// ============================================================
// 轴配置 JSON 持久化 & 板卡同步
// ============================================================

void ConfigMgr::injectDependencies(AxisConfig* cfg, GtsMgr* totalMgr, AxisMgr* axisMgr)
{
    m_axisCfg = cfg;
    m_gtsMgr = totalMgr;
    m_axisMgr = axisMgr;
}

QString ConfigMgr::axisConfigPath() const
{
    return QCoreApplication::applicationDirPath() + QStringLiteral("/Prospect/gtsConfig.json");
}

// 单轴 stuConfig → QJsonObject
static QJsonObject singleAxisToJson(short axis, const SingleAxisConfig& ax)
{
    QJsonObject scalePrf;
    scalePrf[QStringLiteral("alpha")] = static_cast<qint64>(ax.profileScale.alpha);
    scalePrf[QStringLiteral("beta")] = static_cast<qint64>(ax.profileScale.beta);

    QJsonObject scaleEnc;
    scaleEnc[QStringLiteral("alpha")] = static_cast<qint64>(ax.encScale.alpha);
    scaleEnc[QStringLiteral("beta")] = static_cast<qint64>(ax.encScale.beta);

    QJsonObject scaleObj;
    scaleObj[QStringLiteral("profile")] = scalePrf;
    scaleObj[QStringLiteral("encoder")] = scaleEnc;

    QJsonObject dacObj;
    dacObj[QStringLiteral("bias")] = static_cast<int>(ax.dacBias);
    dacObj[QStringLiteral("limit")] = static_cast<int>(ax.dacLimit);

    QJsonObject ctrlObj;
    ctrlObj[QStringLiteral("followErrorLimit")] = static_cast<qint64>(ax.followingErrorLimit);

    QJsonObject prfObj;
    prfObj[QStringLiteral("smoothStopDec")] = ax.smoothStopDec;
    prfObj[QStringLiteral("estopDec")] = ax.estopDec;

    QJsonObject modeObj;
    modeObj[QStringLiteral("controlMode")] = static_cast<int>(ax.ctrlMode);

    // 回零
    QJsonObject homeObj;
    homeObj[QStringLiteral("mode")] = static_cast<int>(ax.axisHomeConfig.homeMode);
    homeObj[QStringLiteral("vel")] = ax.axisHomeConfig.homeVel;
    homeObj[QStringLiteral("acc")] = ax.axisHomeConfig.homeAcc;
    homeObj[QStringLiteral("range")] = ax.axisHomeConfig.homeRange;
    homeObj[QStringLiteral("offset")] = ax.axisHomeConfig.homeOffset;

    // 限位
    QJsonObject limitObj;
    limitObj[QStringLiteral("posLimit")] = ax.axisLimit.posLimit;
    limitObj[QStringLiteral("negLimit")] = ax.axisLimit.negLimit;

    QJsonObject obj;
    obj[QStringLiteral("name")] = static_cast<int>(ax.name);
    obj[QStringLiteral("axis")] = axis;

    QJsonObject softScaleObj;
    softScaleObj[QStringLiteral("alpha")] = static_cast<qint64>(ax.softPulseScale.alpha);
    softScaleObj[QStringLiteral("beta")] = static_cast<qint64>(ax.softPulseScale.beta);
    obj[QStringLiteral("softPulseScale")] = softScaleObj;

    obj[QStringLiteral("scale")] = scaleObj;
    obj[QStringLiteral("dac")] = dacObj;
    obj[QStringLiteral("mode")] = modeObj;
    obj[QStringLiteral("control")] = ctrlObj;
    obj[QStringLiteral("profile")] = prfObj;
    obj[QStringLiteral("home")] = homeObj;
    obj[QStringLiteral("limit")] = limitObj;
    return obj;
}

bool ConfigMgr::saveAxisConfig(const QString& filePath)
{
    if (!m_axisCfg) return false;

    QString path = filePath.isEmpty() ? axisConfigPath() : filePath;

    QJsonArray axesArr;
    for (size_t i = 0; i < m_axisCfg->axes.size(); ++i)
        axesArr.append(singleAxisToJson(static_cast<short>(i + 1), m_axisCfg->axes[i]));

    QJsonObject root;
    root[QStringLiteral("version")] = 2;
    root[QStringLiteral("axisCount")] = static_cast<int>(m_axisCfg->axes.size());
    root[QStringLiteral("cardMode")] = static_cast<int>(m_gtsMgr->cardMode());
    root[QStringLiteral("axes")] = axesArr;

    QDir().mkpath(QFileInfo(path).absolutePath());

    QFile file(path);
    if (!file.open(QIODevice::WriteOnly | QIODevice::Truncate))
        return false;

    file.write(QJsonDocument(root).toJson(QJsonDocument::Indented));
    file.close();
    emit logMessage(QStringLiteral("所有设置已保存到板卡"));
    return true;
}

bool ConfigMgr::loadAxisConfig(const QString& filePath)
{
    if (!m_axisCfg) return false;

    QString path = filePath.isEmpty() ? axisConfigPath() : filePath;

    QFile file(path);
    if (!file.open(QIODevice::ReadOnly))
        return false;

    QByteArray data = file.readAll();
    file.close();

    QJsonParseError err;
    QJsonDocument doc = QJsonDocument::fromJson(data, &err);
    if (err.error != QJsonParseError::NoError || !doc.isObject())
        return false;

    QJsonObject root = doc.object();

    m_gtsMgr->setCardMode(static_cast<CardMode>(root.value(QStringLiteral("cardMode")).toInt(static_cast<int>(CardMode::Normal))));

    // 按 axisCount 初始化所有轴为默认值
    int count = m_gtsMgr->axisCount();
    m_axisCfg->axes.assign(count, SingleAxisConfig{});

    QJsonArray axesArr = root.value(QStringLiteral("axes")).toArray();
    for (int n = 0; n < axesArr.size() && n < count; ++n) {
        QJsonObject axObj = axesArr[n].toObject();
        int axis = axObj.value(QStringLiteral("axis")).toInt(0);
        if (axis < 1 || axis > count)
            continue;
        auto& ax = m_axisCfg->axes[axis - 1];

        // name
        ax.name = static_cast<AxisName>(axObj.value(QStringLiteral("name")).toInt(0));

        // softPulseScale
        QJsonObject softScaleObj = axObj.value(QStringLiteral("softPulseScale")).toObject();
        if (!softScaleObj.isEmpty()) {
            ax.softPulseScale.alpha = static_cast<long>(softScaleObj.value(QStringLiteral("alpha")).toDouble(100.0));
            ax.softPulseScale.beta = static_cast<long>(softScaleObj.value(QStringLiteral("beta")).toDouble(1.0));
        }

        // scale
        QJsonObject scaleObj = axObj.value(QStringLiteral("scale")).toObject();
        if (!scaleObj.isEmpty()) {
            QJsonObject prf = scaleObj.value(QStringLiteral("profile")).toObject();
            if (!prf.isEmpty()) {
                ax.profileScale.alpha = static_cast<long>(prf.value(QStringLiteral("alpha")).toDouble(1.0));
                ax.profileScale.beta = static_cast<long>(prf.value(QStringLiteral("beta")).toDouble(1.0));
            }
            QJsonObject enc = scaleObj.value(QStringLiteral("encoder")).toObject();
            if (!enc.isEmpty()) {
                ax.encScale.alpha = static_cast<long>(enc.value(QStringLiteral("alpha")).toDouble(1.0));
                ax.encScale.beta = static_cast<long>(enc.value(QStringLiteral("beta")).toDouble(1.0));
            }
            else {
                ax.encScale = ax.profileScale;
            }
        }

        // dac
        QJsonObject dacObj = axObj.value(QStringLiteral("dac")).toObject();
        if (!dacObj.isEmpty()) {
            ax.dacBias = static_cast<short>(dacObj.value(QStringLiteral("bias")).toInt(0));
            ax.dacLimit = static_cast<short>(dacObj.value(QStringLiteral("limit")).toInt(32767));
        }

        // control
        QJsonObject ctrlObj = axObj.value(QStringLiteral("control")).toObject();
        if (!ctrlObj.isEmpty()) {
            ax.followingErrorLimit = static_cast<long>(ctrlObj.value(QStringLiteral("followErrorLimit")).toDouble(32767.0));
        }

        // profile (stop decel)
        QJsonObject prfObj = axObj.value(QStringLiteral("profile")).toObject();
        if (!prfObj.isEmpty()) {
            ax.smoothStopDec = prfObj.value(QStringLiteral("smoothStopDec")).toDouble(100.0);
            ax.estopDec = prfObj.value(QStringLiteral("estopDec")).toDouble(1000.0);
        }

        // ControlMode
        QJsonObject modeObj = axObj.value(QStringLiteral("mode")).toObject();
        if (!modeObj.isEmpty()) {
            int m = modeObj.value(QStringLiteral("controlMode")).toInt(
                static_cast<int>(ControlMode::ClosedLoop));
            if (m >= 0 && m <= 2)
                ax.ctrlMode = static_cast<ControlMode>(m);
        }

        // 回零配置
        QJsonObject homeObj = axObj.value(QStringLiteral("home")).toObject();
        if (!homeObj.isEmpty()) {
            int hm = homeObj.value(QStringLiteral("mode")).toInt(
                static_cast<int>(HomeMode::HomeMode_nLlimit));
            ax.axisHomeConfig.homeMode = static_cast<HomeMode>(hm);
            ax.axisHomeConfig.homeVel = homeObj.value(QStringLiteral("vel")).toDouble(10.0);
            ax.axisHomeConfig.homeAcc = homeObj.value(QStringLiteral("acc")).toDouble(5.0);
            ax.axisHomeConfig.homeRange = homeObj.value(QStringLiteral("range")).toDouble(1000.0);
            ax.axisHomeConfig.homeOffset = homeObj.value(QStringLiteral("offset")).toDouble(0.0);
        }

        // 轴限位
        QJsonObject limitObj = axObj.value(QStringLiteral("limit")).toObject();
        if (!limitObj.isEmpty()) {
            ax.axisLimit.posLimit = limitObj.value(QStringLiteral("posLimit")).toDouble(0.0);
            ax.axisLimit.negLimit = limitObj.value(QStringLiteral("negLimit")).toDouble(0.0);
        }
    }

    emit configChanged();
    emit logMessage(QStringLiteral("配置文件加载成功: %1").arg(path), Qt::darkGreen);
    return true;
}


void ConfigMgr::readAllAxisConfigFromBoard()
{
    if (!m_axisCfg || !m_axisMgr) return;

    int count = m_gtsMgr->axisCount();
    m_axisCfg->axes.resize(count);

    for (short axis = 1; axis <= count; ++axis) {
        auto& ax = m_axisCfg->axes[axis - 1];

        m_axisMgr->getProfileScale(axis, ax.profileScale.alpha, ax.profileScale.beta);
        short ret = m_axisMgr->getEncoderScale(axis, ax.encScale.alpha, ax.encScale.beta);
        if (ret != 0)
            ax.encScale = ax.profileScale;

        ax.dacBias = m_axisMgr->getDacBias(axis);
        ax.dacLimit = m_axisMgr->getDacLimit(axis);

        ax.followingErrorLimit = m_axisMgr->getFollowErrorLimit(axis);

        double smooth = 100.0, abrupt = 1000.0;
        m_axisMgr->getStopDecel(axis, smooth, abrupt);
        ax.smoothStopDec = smooth;
        ax.estopDec = abrupt;
    }
}


void ConfigMgr::applyAllAxisConfigToBoard()
{
    if (!m_axisCfg || !m_axisMgr) return;

    for (short axis = 1; axis <= static_cast<short>(m_axisCfg->axes.size()); ++axis) {
        flushScaleToBoard(axis);
        flushDacToBoard(axis);
        flushFollowErrorToBoard(axis);
        flushStopDecelToBoard(axis);
        flushControlModeToBoard(axis);
    }
    emit logMessage(QStringLiteral("全部轴配置已刷入板卡"), Qt::darkGreen);
}

void ConfigMgr::setHomeConfig(short axis, HomeMode mode, double vel, double acc, double range, double offset)
{
    if (!m_axisCfg || axis < 1 || axis > static_cast<short>(m_axisCfg->axes.size())) return;
    auto& h = m_axisCfg->axes[axis - 1].axisHomeConfig;
    h.homeMode = mode;
    h.homeVel = vel;
    h.homeAcc = acc;
    h.homeRange = range;
    h.homeOffset = offset;

    emit logMessage(QStringLiteral("轴%1 回零 → 模式=%2 vel=%3 acc=%4 range=%5 offset=%6")
        .arg(axis).arg(static_cast<int>(mode))
        .arg(vel, 0, 'f', 2).arg(acc, 0, 'f', 2)
        .arg(range, 0, 'f', 2).arg(offset, 0, 'f', 3), Qt::darkGreen);
    emit configChanged();
}

bool ConfigMgr::loadConfigFile(const QString& filePath)
{
    short ret = GtsHal::loadConfig(filePath.toLocal8Bit().constData());
    if (ret == 0) {
        // 板卡 → 内存
        readAllAxisConfigFromBoard();

        // 内存 → JSON 文件
        saveAxisConfig();

        // 通知 UI 刷新
        emit configChanged();

        emit logMessage(QStringLiteral("配置文件加载成功: %1（已同步到内存和本地文件）").arg(filePath), Qt::darkGreen);
        return true;
    }
    else {
        emit logMessage(QStringLiteral("配置文件加载失败 (err=%1): %2").arg(ret).arg(filePath), Qt::red);
        return false;
    }
}



// ============================================================
// IO 描述持久化
// ============================================================

QString ConfigMgr::ioDescriptionPath() const
{
    return QCoreApplication::applicationDirPath() + QStringLiteral("/Prospect/ioDescription.json");
}

void ConfigMgr::loadIODescriptions()
{
    QFile file(ioDescriptionPath());
    if (!file.exists()) {
        m_customDIDesc.clear();
        for (int i = 0; i < 64; ++i) {
            QString def = defaultDIDescription(i);
            if (!def.isEmpty())
                m_customDIDesc[i] = def;
        }
        m_customDODesc.clear();
        for (int i = 0; i < 32; ++i) {
            QString def = defaultDODescription(i);
            if (!def.isEmpty())
                m_customDODesc[i] = def;
        }
        saveIODescriptions();
        emit configChanged();
        return;
    }

    if (!file.open(QIODevice::ReadOnly)) {
        qWarning() << "ConfigMgr: cannot open" << ioDescriptionPath()
            << ", using defaults";
        emit configChanged();
        return;   // 文件打不开 → map 仍是构造函数初始化的空，由 getter fallback 兜底
    }

    QJsonParseError err;
    QJsonDocument doc = QJsonDocument::fromJson(file.readAll(), &err);
    file.close();

    if (err.error != QJsonParseError::NoError || !doc.isObject()) {
        qWarning() << "ConfigMgr: invalid JSON in" << ioDescriptionPath()
            << ", using defaults";
        emit configChanged();
        return;
    }

    QJsonObject root = doc.object();

    auto loadMap = [&](const QString& key, QMap<int, QString>& map) {
        QJsonObject obj = root.value(key).toObject();
        for (auto it = obj.begin(); it != obj.end(); ++it) {
            bool ok = false;
            int r = it.key().toInt(&ok);
            if (ok && r >= 0) map[r] = it.value().toString();
        }
        };

    m_customDIDesc.clear();
    m_customDODesc.clear();
    loadMap(QStringLiteral("di"), m_customDIDesc);
    loadMap(QStringLiteral("do"), m_customDODesc);
    emit configChanged();
}



void ConfigMgr::saveIODescriptions() const
{
    QJsonObject diObj, doObj;
    for (auto it = m_customDIDesc.begin(); it != m_customDIDesc.end(); ++it)
        diObj[QString::number(it.key())] = it.value();
    for (auto it = m_customDODesc.begin(); it != m_customDODesc.end(); ++it)
        doObj[QString::number(it.key())] = it.value();

    QJsonObject root;
    root[QStringLiteral("version")] = 1;
    root[QStringLiteral("di")] = diObj;
    root[QStringLiteral("do")] = doObj;

    QDir().mkpath(QFileInfo(ioDescriptionPath()).absolutePath());

    QFile file(ioDescriptionPath());
    if (!file.open(QIODevice::WriteOnly | QIODevice::Truncate))
        return;

    file.write(QJsonDocument(root).toJson(QJsonDocument::Indented));
    file.close();
}

void ConfigMgr::setIODescription(int row, const QString& desc, bool isDI)
{
    if (isDI) {
        if (desc == defaultDIDescription(row))
            m_customDIDesc.remove(row);
        else
            m_customDIDesc[row] = desc;
    }
    else {
        if (desc == defaultDODescription(row))
            m_customDODesc.remove(row);
        else
            m_customDODesc[row] = desc;
    }
    saveIODescriptions();
}


QString ConfigMgr::getDIDescription(int row) const
{
    return m_customDIDesc.value(row); 
}

QString ConfigMgr::getDODescription(int row) const
{
    return m_customDODesc.value(row);
}




// ============================================================
// 单字段配置读写
// ============================================================

// ---------- 控制模式 ----------
void ConfigMgr::setControlMode(short axis, ControlMode mode)
{
    if (!m_axisCfg || axis < 1 || axis > m_gtsMgr->axisCount()) return;
    int i = axis - 1;
    m_axisCfg->axes[i].ctrlMode = mode;

    switch (mode) {
    case ControlMode::ClosedLoop:
        //GT_EncOn(axis);
        break;
    case ControlMode::OpenLoop:
    case ControlMode::Simulation:
        //GT_EncOff(axis);
        break;
    }
    emit logMessage(QStringLiteral("轴%1 控制模式 → %2").arg(axis).arg(static_cast<int>(mode)), Qt::darkGreen);
    emit configChanged();
}

ControlMode ConfigMgr::controlMode(short axis) const
{
    if (!m_axisCfg || axis < 1 || axis > m_gtsMgr->axisCount())
        return ControlMode::ClosedLoop;
    return m_axisCfg->axes[axis - 1].ctrlMode;
}

// ---------- 轴名称 ----------
void ConfigMgr::setAxisName(short axis, AxisName name)
{
    if (!m_axisCfg || axis < 1 || axis > m_gtsMgr->axisCount()) return;
    m_axisCfg->axes[axis - 1].name = name;
    emit configChanged();
}

AxisName ConfigMgr::axisName(short axis) const
{
    return (m_axisCfg && axis >= 1 && axis <= m_gtsMgr->axisCount())
        ? m_axisCfg->axes[axis - 1].name : AxisName::X;
}

// ---------- 软件脉冲系数 ----------
void ConfigMgr::setSoftPulseScale(short axis, long alpha, long beta)
{
    if (!m_axisCfg || axis < 1 || axis > m_gtsMgr->axisCount()) return;
    m_axisCfg->axes[axis - 1].softPulseScale.alpha = alpha;
    m_axisCfg->axes[axis - 1].softPulseScale.beta = beta;
    emit configChanged();
}

long ConfigMgr::softPulseAlpha(short axis) const
{
    return (m_axisCfg && axis >= 1 && axis <= m_gtsMgr->axisCount())
        ? m_axisCfg->axes[axis - 1].softPulseScale.alpha : 100;
}

long ConfigMgr::softPulseBeta(short axis) const
{
    return (m_axisCfg && axis >= 1 && axis <= m_gtsMgr->axisCount())
        ? m_axisCfg->axes[axis - 1].softPulseScale.beta : 1;
}

// ---------- profile 当量 ----------
void ConfigMgr::setProfileScale(short axis, long alpha, long beta)
{
    if (!m_axisCfg || !m_axisMgr || axis < 1 || axis > m_gtsMgr->axisCount()) return;
    int i = axis - 1;
    m_axisCfg->axes[i].profileScale = { alpha, beta };
    //m_axisMgr->setProfileScale(axis, alpha, beta);
    emit logMessage(QStringLiteral("轴%1 profile当量 → %2/%3").arg(axis).arg(alpha).arg(beta), Qt::darkGreen);
    emit configChanged();
}

long ConfigMgr::profileScaleAlpha(short axis) const
{
    return (m_axisCfg && axis >= 1 && axis <= m_gtsMgr->axisCount())
        ? m_axisCfg->axes[axis - 1].profileScale.alpha : 1;
}

long ConfigMgr::profileScaleBeta(short axis) const
{
    return (m_axisCfg && axis >= 1 && axis <= m_gtsMgr->axisCount())
        ? m_axisCfg->axes[axis - 1].profileScale.beta : 1;
}

// ---------- encoder 当量 ----------
void ConfigMgr::setEncoderScale(short axis, long alpha, long beta)
{
    if (!m_axisCfg || !m_axisMgr || axis < 1 || axis > m_gtsMgr->axisCount()) return;
    int i = axis - 1;
    m_axisCfg->axes[i].encScale = { alpha, beta };
    //m_axisMgr->setEncoderScale(axis, alpha, beta);
    emit logMessage(QStringLiteral("轴%1 encoder当量 → %2/%3").arg(axis).arg(alpha).arg(beta), Qt::darkGreen);
    emit configChanged();
}

long ConfigMgr::encoderScaleAlpha(short axis) const
{
    return (m_axisCfg && axis >= 1 && axis <= m_gtsMgr->axisCount())
        ? m_axisCfg->axes[axis - 1].encScale.alpha : 1;
}

long ConfigMgr::encoderScaleBeta(short axis) const
{
    return (m_axisCfg && axis >= 1 && axis <= m_gtsMgr->axisCount())
        ? m_axisCfg->axes[axis - 1].encScale.beta : 1;
}

// ---------- DAC ----------
void ConfigMgr::readDacConfig()
{
    if (!m_axisCfg || !m_axisMgr) return;
    for (short axis = 1; axis <= m_gtsMgr->axisCount(); ++axis) {
        int i = axis - 1;
        m_axisCfg->axes[i].dacBias = m_axisMgr->getDacBias(axis);
        m_axisCfg->axes[i].dacLimit = m_axisMgr->getDacLimit(axis);
    }
}

void ConfigMgr::setDacBias(short axis, short bias)
{
    if (!m_axisCfg || !m_axisMgr || axis < 1 || axis > m_gtsMgr->axisCount()) return;
    int i = axis - 1;
    m_axisCfg->axes[i].dacBias = bias;
    emit logMessage(QStringLiteral("轴%1 DAC零漂 → %2").arg(axis).arg(bias), Qt::darkGreen);
    emit configChanged();
}

void ConfigMgr::setDacLimit(short axis, short limit)
{
    if (!m_axisCfg || !m_axisMgr || axis < 1 || axis > m_gtsMgr->axisCount()) return;
    int i = axis - 1;
    m_axisCfg->axes[i].dacLimit = limit;
    emit logMessage(QStringLiteral("轴%1 DAC饱和极限 → %2").arg(axis).arg(limit), Qt::darkGreen);
    emit configChanged();
}

short ConfigMgr::dacBias(short axis) const
{
    return (m_axisCfg && axis >= 1 && axis <= m_gtsMgr->axisCount())
        ? m_axisCfg->axes[axis - 1].dacBias : 0;
}

short ConfigMgr::dacLimit(short axis) const
{
    return (m_axisCfg && axis >= 1 && axis <= m_gtsMgr->axisCount())
        ? m_axisCfg->axes[axis - 1].dacLimit : 32767;
}

// ---------- 跟随误差 ----------
void ConfigMgr::readFollowErrorLimit()
{
    if (!m_axisCfg || !m_axisMgr) return;
    for (short axis = 1; axis <= m_gtsMgr->axisCount(); ++axis) {
        int i = axis - 1;
        m_axisCfg->axes[i].followingErrorLimit = m_axisMgr->getFollowErrorLimit(axis);
    }
}

void ConfigMgr::setFollowErrorLimit(short axis, long error) 
{
    if (!m_axisCfg || !m_axisMgr || axis < 1 || axis > m_gtsMgr->axisCount()) return;
    int i = axis - 1;
    m_axisCfg->axes[i].followingErrorLimit = error;
    //m_axisMgr->setFollowErrorLimit(axis, error);
    emit logMessage(QStringLiteral("轴%1 跟随误差极限 → %2").arg(axis).arg(error), Qt::darkGreen);
    emit configChanged();
}

long ConfigMgr::followErrorLimit(short axis) const
{
    return (m_axisCfg && axis >= 1 && axis <= m_gtsMgr->axisCount())
        ? m_axisCfg->axes[axis - 1].followingErrorLimit : 32767;
}

// ---------- 停止减速度 ----------
void ConfigMgr::readStopDecel()
{
    if (!m_axisCfg || !m_axisMgr) return;
    for (short axis = 1; axis <= m_gtsMgr->axisCount(); ++axis) {
        int i = axis - 1;
        double smooth = 100.0, abrupt = 1000.0;
        m_axisMgr->getStopDecel(axis, smooth, abrupt);
        m_axisCfg->axes[i].smoothStopDec = smooth;
        m_axisCfg->axes[i].estopDec = abrupt;
    }
}

void ConfigMgr::setStopDecel(short axis, double smoothDec, double abruptDec)
{
    if (!m_axisCfg || !m_axisMgr || axis < 1 || axis > m_gtsMgr->axisCount()) return;
    int i = axis - 1;
    m_axisCfg->axes[i].smoothStopDec = smoothDec;
    m_axisCfg->axes[i].estopDec = abruptDec;
    //m_axisMgr->setStopDecel(axis, smoothDec, abruptDec);
    emit logMessage(QStringLiteral("轴%1 停止减速度 → 平滑=%2 急停=%3").arg(axis).arg(smoothDec, 0, 'f', 3).arg(abruptDec, 0, 'f', 3), Qt::darkGreen);
    emit configChanged();
}

double ConfigMgr::smoothStopDec(short axis) const
{
    return (m_axisCfg && axis >= 1 && axis <= m_gtsMgr->axisCount())
        ? m_axisCfg->axes[axis - 1].smoothStopDec : 100.0;
}

double ConfigMgr::estopDec(short axis) const
{
    return (m_axisCfg && axis >= 1 && axis <= m_gtsMgr->axisCount())
        ? m_axisCfg->axes[axis - 1].estopDec : 1000.0;
}

// ===== 回零参数 =====
void ConfigMgr::setHomeMode(short axis, HomeMode mode)
{
    if (!m_axisCfg || axis < 1 || axis > m_gtsMgr->axisCount()) return;
    int i = axis - 1;
    m_axisCfg->axes[i].axisHomeConfig.homeMode = mode;
    emit configChanged();
}

void ConfigMgr::setHomeVel(short axis, double vel)
{
    if (!m_axisCfg || axis < 1 || axis > m_gtsMgr->axisCount()) return;
    int i = axis - 1;
    m_axisCfg->axes[i].axisHomeConfig.homeVel = vel;
    emit configChanged();
}

void ConfigMgr::setHomeAcc(short axis, double acc)
{
    if (!m_axisCfg || axis < 1 || axis > m_gtsMgr->axisCount()) return;
    int i = axis - 1;
    m_axisCfg->axes[i].axisHomeConfig.homeAcc = acc;
    emit configChanged();
}

void ConfigMgr::setHomeRange(short axis, double range)
{
    if (!m_axisCfg || axis < 1 || axis > m_gtsMgr->axisCount()) return;
    int i = axis - 1;
    m_axisCfg->axes[i].axisHomeConfig.homeRange = range;
    emit configChanged();
}

void ConfigMgr::setHomeOffset(short axis, double offset)
{
    if (!m_axisCfg || axis < 1 || axis > m_gtsMgr->axisCount()) return;
    int i = axis - 1;
    m_axisCfg->axes[i].axisHomeConfig.homeOffset = offset;
    emit configChanged();
}

HomeMode ConfigMgr::homeModeValue(short axis) const
{
    return (m_axisCfg && axis >= 1 && axis <= m_gtsMgr->axisCount())
        ? m_axisCfg->axes[axis - 1].axisHomeConfig.homeMode : HomeMode::HomeMode_nLlimit;
}

double ConfigMgr::homeVel(short axis) const
{
    return (m_axisCfg && axis >= 1 && axis <= m_gtsMgr->axisCount())
        ? m_axisCfg->axes[axis - 1].axisHomeConfig.homeVel : 10.0;
}

double ConfigMgr::homeAcc(short axis) const
{
    return (m_axisCfg && axis >= 1 && axis <= m_gtsMgr->axisCount())
        ? m_axisCfg->axes[axis - 1].axisHomeConfig.homeAcc : 5.0;
}

double ConfigMgr::homeRange(short axis) const
{
    return (m_axisCfg && axis >= 1 && axis <= m_gtsMgr->axisCount())
        ? m_axisCfg->axes[axis - 1].axisHomeConfig.homeRange : 1000.0;
}

double ConfigMgr::homeOffset(short axis) const
{
    return (m_axisCfg && axis >= 1 && axis <= m_gtsMgr->axisCount())
        ? m_axisCfg->axes[axis - 1].axisHomeConfig.homeOffset : 0.0;
}

// ===== 轴限位 =====
void ConfigMgr::setPosLimit(short axis, double limit)
{
    if (!m_axisCfg || axis < 1 || axis > m_gtsMgr->axisCount()) return;
    int i = axis - 1;
    m_axisCfg->axes[i].axisLimit.posLimit = limit;
    emit logMessage(QStringLiteral("轴%1 正限位 → %2").arg(axis).arg(limit, 0, 'f', 1), Qt::darkGreen);
    emit configChanged();
}

void ConfigMgr::setNegLimit(short axis, double limit)
{
    if (!m_axisCfg || axis < 1 || axis > m_gtsMgr->axisCount()) return;
    int i = axis - 1;
    m_axisCfg->axes[i].axisLimit.negLimit = limit;
    emit logMessage(QStringLiteral("轴%1 负限位 → %2").arg(axis).arg(limit, 0, 'f', 1), Qt::darkGreen);
    emit configChanged();
}

double ConfigMgr::posLimit(short axis) const
{
    return (m_axisCfg && axis >= 1 && axis <= m_gtsMgr->axisCount())
        ? m_axisCfg->axes[axis - 1].axisLimit.posLimit : 0.0;
}

double ConfigMgr::negLimit(short axis) const
{
    return (m_axisCfg && axis >= 1 && axis <= m_gtsMgr->axisCount())
        ? m_axisCfg->axes[axis - 1].axisLimit.negLimit : 0.0;
}

// ============================================================
// flush —— 从内存刷入板卡（不修改内存）
// ============================================================

void ConfigMgr::flushScaleToBoard(short axis)
{
    if (!m_axisCfg || !m_axisMgr || axis < 1 || axis > m_gtsMgr->axisCount()) return;
    int i = axis - 1;
    m_axisMgr->setProfileScale(axis, m_axisCfg->axes[i].profileScale.alpha, m_axisCfg->axes[i].profileScale.beta);
    m_axisMgr->setEncoderScale(axis, m_axisCfg->axes[i].encScale.alpha, m_axisCfg->axes[i].encScale.beta);
    emit logMessage(QStringLiteral("轴%1 当量已刷入板卡").arg(axis), Qt::darkGreen);
}

void ConfigMgr::flushDacToBoard(short axis)
{
    if (!m_axisCfg || !m_axisMgr || axis < 1 || axis > m_gtsMgr->axisCount()) return;
    int i = axis - 1;
    m_axisMgr->setDacBias(axis, m_axisCfg->axes[i].dacBias);
    m_axisMgr->setDacLimit(axis, m_axisCfg->axes[i].dacLimit);
    emit logMessage(QStringLiteral("轴%1 DAC已刷入板卡").arg(axis), Qt::darkGreen);
}

void ConfigMgr::flushFollowErrorToBoard(short axis)
{
    if (!m_axisCfg || !m_axisMgr || axis < 1 || axis > m_gtsMgr->axisCount()) return;
    int i = axis - 1;
    m_axisMgr->setFollowErrorLimit(axis, m_axisCfg->axes[i].followingErrorLimit);
    emit logMessage(QStringLiteral("轴%1 跟随误差已刷入板卡").arg(axis), Qt::darkGreen);
}

void ConfigMgr::flushStopDecelToBoard(short axis)
{
    if (!m_axisCfg || !m_axisMgr || axis < 1 || axis > m_gtsMgr->axisCount()) return;
    int i = axis - 1;
    m_axisMgr->setStopDecel(axis, m_axisCfg->axes[i].smoothStopDec, m_axisCfg->axes[i].estopDec);
    emit logMessage(QStringLiteral("轴%1 停止减速度已刷入板卡").arg(axis), Qt::darkGreen);
}

void ConfigMgr::flushControlModeToBoard(short axis)
{
    if (!m_axisCfg || axis < 1 || axis > m_gtsMgr->axisCount()) return;
    int i = axis - 1;
    switch (m_axisCfg->axes[i].ctrlMode) {
    case ControlMode::ClosedLoop:
        GT_EncOn(axis);
        break;
    case ControlMode::OpenLoop:
    case ControlMode::Simulation:
        GT_EncOff(axis);
        break;
    }
    emit logMessage(QStringLiteral("轴%1 控制模式已刷入板卡").arg(axis), Qt::darkGreen);
}



// ================================================================
// 1. PID / 控制滤波
// ================================================================
bool ConfigMgr::setPID(short control, short index, const TPid& pid) 
{
    m_lastError = GtsHal::setPid(control, index, pid);
    if (m_lastError != 0) {
        emit errorOccurred(control, m_lastError, QStringLiteral("setPid: ") + lastErrorString());
        return false;
    }
    return true;
}

bool ConfigMgr::getPID(short control, short index, TPid& pid) const 
{
    m_lastError = GtsHal::getPid(control, index, &pid);
    return m_lastError == 0;
}

bool ConfigMgr::setControlFilter(short control, short index) 
{
    m_lastError = GtsHal::setControlFilter(control, index);
    if (m_lastError != 0) {
        emit errorOccurred(control, m_lastError, QStringLiteral("setControlFilter: ") + lastErrorString());
        return false;
    }
    return true;
}

short ConfigMgr::getControlFilter(short control) const 
{
    short index = 0;
    GtsHal::getControlFilter(control, &index);
    return index;
}

bool ConfigMgr::setKvffFilter(short control, short index, short kvffFilterExp, double accMax) 
{
    m_lastError = GtsHal::setKvffFilter(control, index, kvffFilterExp, accMax);
    if (m_lastError != 0) {
        emit errorOccurred(control, m_lastError, QStringLiteral("setKvffFilter: ") + lastErrorString());
        return false;
    }
    return true;
}

bool ConfigMgr::getKvffFilter(short control, short index, short& kvffFilterExp, double& accMax) const 
{
    m_lastError = GtsHal::getKvffFilter(control, index, &kvffFilterExp, &accMax);
    return m_lastError == 0;
}

bool ConfigMgr::setAxisBand(short axis, long band, long time) 
{
    if (!isValidAxis(axis)) {
        emit errorOccurred(axis, -1, QStringLiteral("轴号无效: %1").arg(axis));
        return false;
    }
    m_lastError = GtsHal::setAxisBand(axis, band, time);
    if (m_lastError != 0) {
        emit errorOccurred(axis, m_lastError, QStringLiteral("setAxisBand: ") + lastErrorString());
        return false;
    }
    return true;
}

bool ConfigMgr::getAxisBand(short axis, long& band, long& time) const 
{
    if (!isValidAxis(axis)) return false;
    m_lastError = GtsHal::getAxisBand(axis, &band, &time);
    return m_lastError == 0;
}

bool ConfigMgr::setControlConfigEx(short control, const TControlConfigEx& cfg) 
{
    m_lastError = GtsHal::setControlConfigEx(control, cfg);
    if (m_lastError != 0) {
        emit errorOccurred(control, m_lastError, QStringLiteral("setControlConfigEx: ") + lastErrorString());
        return false;
    }
    return true;
}

bool ConfigMgr::getControlConfigEx(short control, TControlConfigEx& cfg) const 
{
    m_lastError = GtsHal::getControlConfigEx(control, &cfg);
    return m_lastError == 0;
}

bool ConfigMgr::setControlSuperimposed(short control, short superimposedType, short superimposedIndex) 
{
    m_lastError = GtsHal::setControlSuperimposed(control, superimposedType, superimposedIndex);
    if (m_lastError != 0) {
        emit errorOccurred(control, m_lastError, QStringLiteral("setControlSuperimposed: ") + lastErrorString());
        return false;
    }
    return true;
}

bool ConfigMgr::getControlSuperimposed(short control, short& type, short& index) const 
{
    m_lastError = GtsHal::getControlSuperimposed(control, &type, &index);
    return m_lastError == 0;
}

// ================================================================
// 2. 背隙补偿
// ================================================================
bool ConfigMgr::setBacklash(short axis, long compValue, double compChangeValue, long compDir) 
{
    if (!isValidAxis(axis)) {
        emit errorOccurred(axis, -1, QStringLiteral("轴号无效: %1").arg(axis));
        return false;
    }
    m_lastError = GtsHal::setBacklash(axis, compValue, compChangeValue, compDir);
    if (m_lastError != 0) {
        emit errorOccurred(axis, m_lastError, QStringLiteral("setBacklash: ") + lastErrorString());
        return false;
    }
    return true;
}

bool ConfigMgr::getBacklash(short axis, long& compValue, double& compChangeValue, long& compDir) const 
{
    if (!isValidAxis(axis)) return false;
    m_lastError = GtsHal::getBacklash(axis, &compValue, &compChangeValue, &compDir);
    return m_lastError == 0;
}

// ================================================================
// 3. 丝杠补偿 / 2D 补偿
// ================================================================
bool ConfigMgr::setLeadScrewComp(short axis, short n, long startPos, long lenPos,  long* pCompPos, long* pCompNeg) 
{
    if (!isValidAxis(axis)) {
        emit errorOccurred(axis, -1, QStringLiteral("轴号无效: %1").arg(axis));
        return false;
    }
    m_lastError = GtsHal::setLeadScrewComp(axis, n, startPos, lenPos, pCompPos, pCompNeg);
    if (m_lastError != 0) {
        emit errorOccurred(axis, m_lastError, QStringLiteral("setLeadScrewComp: ") + lastErrorString());
        return false;
    }
    return true;
}

bool ConfigMgr::enableLeadScrewComp(short axis, short mode) 
{
    if (!isValidAxis(axis)) {
        emit errorOccurred(axis, -1, QStringLiteral("轴号无效: %1").arg(axis));
        return false;
    }
    m_lastError = GtsHal::enableLeadScrewComp(axis, mode);
    if (m_lastError != 0) {
        emit errorOccurred(axis, m_lastError, QStringLiteral("enableLeadScrewComp: ") + lastErrorString());
        return false;
    }
    return true;
}

bool ConfigMgr::getLeadScrewCompValue(short axis, short dir, long pos, long& compValue) const 
{
    if (!isValidAxis(axis)) return false;
    m_lastError = GtsHal::getLeadScrewCompInnerValue(axis, dir, pos, &compValue);
    return m_lastError == 0;
}

bool ConfigMgr::setLeadScrewCrossComp(short axis, short n, long startPos, long lenPos,
    long* pCompPos, long* pCompNeg, short link) 
{
    if (!isValidAxis(axis)) {
        emit errorOccurred(axis, -1, QStringLiteral("轴号无效: %1").arg(axis));
        return false;
    }
    m_lastError = GtsHal::setLeadScrewCrossComp(axis, n, startPos, lenPos, pCompPos, pCompNeg, link);
    if (m_lastError != 0) {
        emit errorOccurred(axis, m_lastError, QStringLiteral("setLeadScrewCrossComp: ") + lastErrorString());
        return false;
    }
    return true;
}

bool ConfigMgr::enableLeadScrewCrossComp(short axis, short mode)
{
    if (!isValidAxis(axis)) {
        emit errorOccurred(axis, -1, QStringLiteral("轴号无效: %1").arg(axis));
        return false;
    }
    m_lastError = GtsHal::enableLeadScrewCrossComp(axis, mode);
    if (m_lastError != 0) {
        emit errorOccurred(axis, m_lastError, QStringLiteral("enableLeadScrewCrossComp: ") + lastErrorString());
        return false;
    }
    return true;
}

bool ConfigMgr::setLeadScrewLink(short axis, short link) 
{
    if (!isValidAxis(axis)) {
        emit errorOccurred(axis, -1, QStringLiteral("轴号无效: %1").arg(axis));
        return false;
    }
    m_lastError = GtsHal::setLeadScrewLink(axis, link);
    if (m_lastError != 0) {
        emit errorOccurred(axis, m_lastError, QStringLiteral("setLeadScrewLink: ") + lastErrorString());
        return false;
    }
    return true;
}

short ConfigMgr::getLeadScrewLink(short axis) const 
{
    if (!isValidAxis(axis)) return -1;
    short link = 0;
    GtsHal::getLeadScrewLink(axis, &link);
    return link;
}

bool ConfigMgr::setCompensate2DTable(short idx, const TCompensate2DTable& tbl,
    long* pData, short externComp) 
{
    m_lastError = GtsHal::setCompensate2DTable(idx, tbl, pData, externComp);
    if (m_lastError != 0) {
        emit errorOccurred(idx, m_lastError, QStringLiteral("setCompensate2DTable: ") + lastErrorString());
        return false;
    }
    return true;
}

bool ConfigMgr::getCompensate2DTable(short idx, TCompensate2DTable& tbl) const 
{
    m_lastError = GtsHal::getCompensate2DTable(idx, &tbl);
    return m_lastError == 0;
}

bool ConfigMgr::setCompensate2D(short axis, const TCompensate2D& comp) 
{
    if (!isValidAxis(axis)) {
        emit errorOccurred(axis, -1, QStringLiteral("轴号无效: %1").arg(axis));
        return false;
    }
    m_lastError = GtsHal::setCompensate2D(axis, comp);
    if (m_lastError != 0) {
        emit errorOccurred(axis, m_lastError, QStringLiteral("setCompensate2D: ") + lastErrorString());
        return false;
    }
    return true;
}

bool ConfigMgr::getCompensate2D(short axis, TCompensate2D& comp) const 
{
    if (!isValidAxis(axis)) return false;
    m_lastError = GtsHal::getCompensate2D(axis, &comp);
    return m_lastError == 0;
}

double ConfigMgr::getCompensate2DValue(short axis) const 
{
    if (!isValidAxis(axis)) return 0.0;
    double val = 0.0;
    GtsHal::getCompensate2DValue(axis, &val);
    return val;
}

bool ConfigMgr::getCompensate(short axis, double& pitchError, double& crossError,
    double& backlashError, double& encPos, double& prfPos) const 
{
    if (!isValidAxis(axis)) return false;
    m_lastError = GtsHal::getCompensate(axis, &pitchError, &crossError,
        &backlashError, &encPos, &prfPos);
    return m_lastError == 0;
}

// ================================================================
// 4. 位置比较 (1D)
// ================================================================
bool ConfigMgr::setComparePort(short channel, short hsio0, short hsio1) 
{
    m_lastError = GtsHal::setComparePort(channel, hsio0, hsio1);
    if (m_lastError != 0) {
        emit errorOccurred(channel, m_lastError, QStringLiteral("setComparePort: ") + lastErrorString());
        return false;
    }
    return true;
}

bool ConfigMgr::comparePulse(short level, short outputType, short time) 
{
    m_lastError = GtsHal::comparePulse(level, outputType, time);
    if (m_lastError != 0) {
        emit errorOccurred(-1, m_lastError, QStringLiteral("comparePulse: ") + lastErrorString());
        return false;
    }
    return true;
}

bool ConfigMgr::compareStop() 
{
    m_lastError = GtsHal::compareStop();
    if (m_lastError != 0) {
        emit errorOccurred(-1, m_lastError, QStringLiteral("compareStop: ") + lastErrorString());
        return false;
    }
    return true;
}

bool ConfigMgr::compareStatus(short& status, long& count) const 
{
    m_lastError = GtsHal::compareStatus(&status, &count);
    return m_lastError == 0;
}

bool ConfigMgr::compareData(short encoder, short source, short pulseType, short startLevel,
    short time, long* pBuf1, short count1, long* pBuf2, short count2) 
{
    m_lastError = GtsHal::compareData(encoder, source, pulseType, startLevel, time,
        pBuf1, count1, pBuf2, count2);
    if (m_lastError != 0) {
        emit errorOccurred(encoder, m_lastError, QStringLiteral("compareData: ") + lastErrorString());
        return false;
    }
    return true;
}

bool ConfigMgr::compareLinear(short encoder, short channel, long startPos, long repeatTimes,
    long interval, short time, short source) 
{
    m_lastError = GtsHal::compareLinear(encoder, channel, startPos, repeatTimes,
        interval, time, source);
    if (m_lastError != 0) {
        emit errorOccurred(encoder, m_lastError, QStringLiteral("compareLinear: ") + lastErrorString());
        return false;
    }
    return true;
}

bool ConfigMgr::compareContinuePulseMode(short mode, short count, short standTime) 
{
    m_lastError = GtsHal::compareContinuePulseMode(mode, count, standTime);
    if (m_lastError != 0) {
        emit errorOccurred(-1, m_lastError, QStringLiteral("compareContinuePulseMode: ") + lastErrorString());
        return false;
    }
    return true;
}

// ================================================================
// 5. 2D 位置比较
// ================================================================
bool ConfigMgr::compare2DSetMode(short chn, short mode)
{
    m_lastError = GtsHal::compare2DMode(chn, mode);
    if (m_lastError != 0) {
        emit errorOccurred(chn, m_lastError, QStringLiteral("compare2DMode: ") + lastErrorString());
        return false;
    }
    return true;
}

bool ConfigMgr::compare2DPulse(short chn, short level, short outputType, short time) 
{
    m_lastError = GtsHal::compare2DPulse(chn, level, outputType, time);
    if (m_lastError != 0) {
        emit errorOccurred(chn, m_lastError, QStringLiteral("compare2DPulse: ") + lastErrorString());
        return false;
    }
    return true;
}

bool ConfigMgr::compare2DStop(short chn)
{
    m_lastError = GtsHal::compare2DStop(chn);
    if (m_lastError != 0) {
        emit errorOccurred(chn, m_lastError, QStringLiteral("compare2DStop: ") + lastErrorString());
        return false;
    }
    return true;
}

bool ConfigMgr::compare2DClear(short chn) 
{
    m_lastError = GtsHal::compare2DClear(chn);
    if (m_lastError != 0) {
        emit errorOccurred(chn, m_lastError, QStringLiteral("compare2DClear: ") + lastErrorString());
        return false;
    }
    return true;
}

bool ConfigMgr::compare2DStatus(short chn, short& status, long& count,
    short& fifo, short& fifoCount) const
{
    m_lastError = GtsHal::compare2DStatus(chn, &status, &count, &fifo, &fifoCount);
    return m_lastError == 0;
}

bool ConfigMgr::compare2DSetParams(short chn, const T2DComparePrm& prm) 
{
    m_lastError = GtsHal::compare2DSetPrm(chn, prm);
    if (m_lastError != 0) {
        emit errorOccurred(chn, m_lastError, QStringLiteral("compare2DSetPrm: ") + lastErrorString());
        return false;
    }
    return true;
}

bool ConfigMgr::compare2DData(short chn, short count, const T2DCompareData* pBuf, short fifo) 
{
    m_lastError = GtsHal::compare2DData(chn, count, pBuf, fifo);
    if (m_lastError != 0) {
        emit errorOccurred(chn, m_lastError, QStringLiteral("compare2DData: ") + lastErrorString());
        return false;
    }
    return true;
}

bool ConfigMgr::compare2DStart(short chn) 
{
    m_lastError = GtsHal::compare2DStart(chn);
    if (m_lastError != 0) {
        emit errorOccurred(chn, m_lastError, QStringLiteral("compare2DStart: ") + lastErrorString());
        return false;
    }
    return true;
}

bool ConfigMgr::compare2DClearData(short chn) 
{
    m_lastError = GtsHal::compare2DClearData(chn);
    if (m_lastError != 0) {
        emit errorOccurred(chn, m_lastError, QStringLiteral("compare2DClearData: ") + lastErrorString());
        return false;
    }
    return true;
}

bool ConfigMgr::compare2DSetPreOutTime(short chn, double preOutputTime) 
{
    m_lastError = GtsHal::compare2DSetPreOutTime(chn, preOutputTime);
    if (m_lastError != 0) {
        emit errorOccurred(chn, m_lastError, QStringLiteral("compare2DSetPreOutTime: ") + lastErrorString());
        return false;
    }
    return true;
}

// ================================================================
// 6. PosCompare (新版)
// ================================================================
bool ConfigMgr::setPosCompareMode(short index, const TPosCompareMode& mode) 
{
    m_lastError = GtsHal::setPosCompareMode(index, mode);
    if (m_lastError != 0) {
        emit errorOccurred(index, m_lastError, QStringLiteral("setPosCompareMode: ") + lastErrorString());
        return false;
    }
    return true;
}

bool ConfigMgr::getPosCompareMode(short index, TPosCompareMode& mode) const 
{
    m_lastError = GtsHal::getPosCompareMode(index, &mode);
    return m_lastError == 0;
}

bool ConfigMgr::posCompareStart(short index) 
{
    m_lastError = GtsHal::posCompareStart(index);
    if (m_lastError != 0) {
        emit errorOccurred(index, m_lastError, QStringLiteral("posCompareStart: ") + lastErrorString());
        return false;
    }
    return true;
}

bool ConfigMgr::posCompareStop(short index) 
{
    m_lastError = GtsHal::posCompareStop(index);
    if (m_lastError != 0) {
        emit errorOccurred(index, m_lastError, QStringLiteral("posCompareStop: ") + lastErrorString());
        return false;
    }
    return true;
}

bool ConfigMgr::posCompareClear(short index) 
{
    m_lastError = GtsHal::posCompareClear(index);
    if (m_lastError != 0) {
        emit errorOccurred(index, m_lastError, QStringLiteral("posCompareClear: ") + lastErrorString());
        return false;
    }
    return true;
}

bool ConfigMgr::posCompareStatus(short index, TPosCompareStatus& status) const 
{
    m_lastError = GtsHal::posCompareStatus(index, &status);
    return m_lastError == 0;
}

bool ConfigMgr::posCompareData(short index, const TPosCompareData& data) 
{
    m_lastError = GtsHal::posCompareData(index, data);
    if (m_lastError != 0) {
        emit errorOccurred(index, m_lastError, QStringLiteral("posCompareData: ") + lastErrorString());
        return false;
    }
    return true;
}

bool ConfigMgr::posCompareSetLinear(short index, const TPosCompareLinear& linear) 
{
    m_lastError = GtsHal::posCompareSetLinear(index, linear);
    if (m_lastError != 0) {
        emit errorOccurred(index, m_lastError, QStringLiteral("posCompareSetLinear: ") + lastErrorString());
        return false;
    }
    return true;
}

bool ConfigMgr::posCompareSetPsoParams(short index, const TPosComparePsoPrm& prm) 
{
    m_lastError = GtsHal::posCompareSetPsoPrm(index, prm);
    if (m_lastError != 0) {
        emit errorOccurred(index, m_lastError, QStringLiteral("posCompareSetPsoPrm: ") + lastErrorString());
        return false;
    }
    return true;
}

bool ConfigMgr::posCompareSetContinueMode(short index, const TPosCompareContinueMode& mode) 
{
    m_lastError = GtsHal::posCompareSetContinueMode(index, mode);
    if (m_lastError != 0) {
        emit errorOccurred(index, m_lastError, QStringLiteral("posCompareSetContinueMode: ") + lastErrorString());
        return false;
    }
    return true;
}

// ================================================================
// 7. 龙门 (Gantry)
// ================================================================
bool ConfigMgr::enableGantry(short master, short slave, double masterKp, double slaveKp) 
{
    m_lastError = GtsHal::enableGantry(master, slave, masterKp, slaveKp);
    if (m_lastError != 0) {
        emit errorOccurred(master, m_lastError, QStringLiteral("enableGantry: ") + lastErrorString());
        return false;
    }
    return true;
}

bool ConfigMgr::disableGantry() 
{
    m_lastError = GtsHal::disableGantry();
    if (m_lastError != 0) {
        emit errorOccurred(-1, m_lastError, QStringLiteral("disableGantry: ") + lastErrorString());
        return false;
    }
    return true;
}

bool ConfigMgr::setGantryErrorLimit(long errLmt) 
{
    m_lastError = GtsHal::setGantryErrLmt(errLmt);
    if (m_lastError != 0) {
        emit errorOccurred(-1, m_lastError, QStringLiteral("setGantryErrLmt: ") + lastErrorString());
        return false;
    }
    return true;
}

long ConfigMgr::getGantryErrorLimit() const 
{
    long limit = 0;
    GtsHal::getGantryErrLmt(&limit);
    return limit;
}

bool ConfigMgr::zeroGantryPos(short master, short slave) 
{
    m_lastError = GtsHal::zeroGantryPos(master, slave);
    if (m_lastError != 0) {
        emit errorOccurred(master, m_lastError, QStringLiteral("zeroGantryPos: ") + lastErrorString());
        return false;
    }
    return true;
}

bool ConfigMgr::setGantryMode(short group, short master, short slave,
    short mode, long syncErrorLimit) 
{
    m_lastError = GtsHal::setGantryMode(group, master, slave, mode, syncErrorLimit);
    if (m_lastError != 0) {
        emit errorOccurred(group, m_lastError, QStringLiteral("setGantryMode: ") + lastErrorString());
        return false;
    }
    return true;
}

bool ConfigMgr::getGantryMode(short group, short& master, short& slave,
    short& mode, long& syncErrorLimit) const 
{
    m_lastError = GtsHal::getGantryMode(group, &master, &slave, &mode, &syncErrorLimit);
    return m_lastError == 0;
}

bool ConfigMgr::setGantryPID(short group, const TPid& gantryPid, const TPid& yawPid) 
{
    m_lastError = GtsHal::setGantryPid(group, gantryPid, yawPid);
    if (m_lastError != 0) {
        emit errorOccurred(group, m_lastError, QStringLiteral("setGantryPid: ") + lastErrorString());
        return false;
    }
    return true;
}

bool ConfigMgr::getGantryPID(short group, TPid& gantryPid, TPid& yawPid) const 
{
    m_lastError = GtsHal::getGantryPid(group, &gantryPid, &yawPid);
    return m_lastError == 0;
}

bool ConfigMgr::gantryAxisOn(short group) 
{
    m_lastError = GtsHal::gantryAxisOn(group);
    if (m_lastError != 0) {
        emit errorOccurred(group, m_lastError, QStringLiteral("gantryAxisOn: ") + lastErrorString());
        return false;
    }
    return true;
}

bool ConfigMgr::gantryAxisOff(short group) 
{
    m_lastError = GtsHal::gantryAxisOff(group);
    if (m_lastError != 0) {
        emit errorOccurred(group, m_lastError, QStringLiteral("gantryAxisOff: ") + lastErrorString());
        return false;
    }
    return true;
}

// ================================================================
// 8. 手轮 (Handwheel)
// ================================================================
bool ConfigMgr::handwheelInit() 
{
    m_lastError = GtsHal::handwheelInit();
    if (m_lastError != 0) {
        emit errorOccurred(-1, m_lastError, QStringLiteral("handwheelInit: ") + lastErrorString());
        return false;
    }
    return true;
}

bool ConfigMgr::setHandwheelStopDecel(short slave, double decSmooth, double decAbrupt) 
{
    m_lastError = GtsHal::setHandwheelStopDec(slave, decSmooth, decAbrupt);
    if (m_lastError != 0) {
        emit errorOccurred(slave, m_lastError, QStringLiteral("setHandwheelStopDec: ") + lastErrorString());
        return false;
    }
    return true;
}

bool ConfigMgr::startHandwheel(short slave, short master, short masterEven, short slaveEven,
    short intervalTime, double acc, double dec, double vel,
    short stopWaitTime) 
{
    m_lastError = GtsHal::startHandwheel(slave, master, masterEven, slaveEven,
        intervalTime, acc, dec, vel, stopWaitTime);
    if (m_lastError != 0) {
        emit errorOccurred(slave, m_lastError, QStringLiteral("startHandwheel: ") + lastErrorString());
        return false;
    }
    return true;
}

bool ConfigMgr::endHandwheel(short slave) 
{
    m_lastError = GtsHal::endHandwheel(slave);
    if (m_lastError != 0) {
        emit errorOccurred(slave, m_lastError, QStringLiteral("endHandwheel: ") + lastErrorString());
        return false;
    }
    return true;
}

// ================================================================
// 9. 触发 (Trigger)
// ================================================================
bool ConfigMgr::setTrigger(short i, const TTrigger& trigger) 
{
    m_lastError = GtsHal::setTrigger(i, trigger);
    if (m_lastError != 0) {
        emit errorOccurred(i, m_lastError, QStringLiteral("setTrigger: ") + lastErrorString());
        return false;
    }
    return true;
}

bool ConfigMgr::getTrigger(short i, TTrigger& trigger) const 
{
    m_lastError = GtsHal::getTrigger(i, &trigger);
    return m_lastError == 0;
}

bool ConfigMgr::getTriggerStatus(short i, TTriggerStatus& status) const 
{
    m_lastError = GtsHal::getTriggerStatus(i, &status);
    return m_lastError == 0;
}

bool ConfigMgr::getTriggerStatusEx(short i, TTriggerStatusEx& statusEx) const 
{
    m_lastError = GtsHal::getTriggerStatusEx(i, &statusEx);
    return m_lastError == 0;
}

bool ConfigMgr::clearTriggerStatus(short i) 
{
    m_lastError = GtsHal::clearTriggerStatus(i);
    if (m_lastError != 0) {
        emit errorOccurred(i, m_lastError, QStringLiteral("clearTriggerStatus: ") + lastErrorString());
        return false;
    }
    return true;
}

bool ConfigMgr::getTriggerLatchValue(short i, long count, long* pValue,
    long* pCount, TLatchValueInfo* pInfo) const 
{
    m_lastError = GtsHal::getTriggerLatchValue(i, count, pValue, pCount, pInfo);
    return m_lastError == 0;
}

// ================================================================
// 10. 坐标变换
// ================================================================
bool ConfigMgr::setTransformOrthogonal(short index, const TTransformOrthogonal& data) 
{
    m_lastError = GtsHal::setTransformOrthogonal(index, data);
    if (m_lastError != 0) {
        emit errorOccurred(index, m_lastError, QStringLiteral("setTransformOrthogonal: ") + lastErrorString());
        return false;
    }
    return true;
}

bool ConfigMgr::getTransformOrthogonal(short index, TTransformOrthogonal& data) const 
{
    m_lastError = GtsHal::getTransformOrthogonal(index, &data);
    return m_lastError == 0;
}

bool ConfigMgr::getTransformOrthogonalPosition(short index, double& x, double& y) const 
{
    m_lastError = GtsHal::getTransformOrthogonalPosition(index, &x, &y);
    return m_lastError == 0;
}

bool ConfigMgr::setTransformPerpendicularity(short index, const TTransformPerpendicularity& data) 
{
    m_lastError = GtsHal::setTransformPerpendicularity(index, data);
    if (m_lastError != 0) {
        emit errorOccurred(index, m_lastError, QStringLiteral("setTransformPerpendicularity: ") + lastErrorString());
        return false;
    }
    return true;
}

bool ConfigMgr::getTransformPerpendicularity(short index, TTransformPerpendicularity& data) const 
{
    m_lastError = GtsHal::getTransformPerpendicularity(index, &data);
    return m_lastError == 0;
}

bool ConfigMgr::getTransformPerpendicularityPosition(short index, double& x, double& y, double& z) const 
{
    m_lastError = GtsHal::getTransformPerpendicularityPosition(index, &x, &y, &z);
    return m_lastError == 0;
}

// ================================================================
// 11. Smart Cutter
// ================================================================
bool ConfigMgr::setSmartCutterParams(short index, const TSmartCutterPrm& prm) 
{
    m_lastError = GtsHal::setSmartCutterPrm(index, prm);
    if (m_lastError != 0) {
        emit errorOccurred(index, m_lastError, QStringLiteral("setSmartCutterPrm: ") + lastErrorString());
        return false;
    }
    return true;
}

bool ConfigMgr::getSmartCutterParams(short index, TSmartCutterPrm& prm) const 
{
    m_lastError = GtsHal::getSmartCutterPrm(index, &prm);
    return m_lastError == 0;
}

bool ConfigMgr::smartCutterOn(short index) 
{
    m_lastError = GtsHal::smartCutterOn(index);
    if (m_lastError != 0) {
        emit errorOccurred(index, m_lastError, QStringLiteral("smartCutterOn: ") + lastErrorString());
        return false;
    }
    return true;
}

bool ConfigMgr::smartCutterOff(short index) 
{
    m_lastError = GtsHal::smartCutterOff(index);
    if (m_lastError != 0) {
        emit errorOccurred(index, m_lastError, QStringLiteral("smartCutterOff: ") + lastErrorString());
        return false;
    }
    return true;
}

bool ConfigMgr::getSmartCutterInfo(short index, TSmartCutterInfo& info) const 
{
    m_lastError = GtsHal::getSmartCutterInfo(index, &info);
    return m_lastError == 0;
}

bool ConfigMgr::setSmartCutterValue(short index, double radiusValue, double angleValue) 
{
    m_lastError = GtsHal::setSmartCutterValue(index, radiusValue, angleValue);
    if (m_lastError != 0) {
        emit errorOccurred(index, m_lastError, QStringLiteral("setSmartCutterValue: ") + lastErrorString());
        return false;
    }
    return true;
}

bool ConfigMgr::smartCutterStart(short index) 
{
    m_lastError = GtsHal::smartCutterStart(index);
    if (m_lastError != 0) {
        emit errorOccurred(index, m_lastError, QStringLiteral("smartCutterStart: ") + lastErrorString());
        return false;
    }
    return true;
}

// ================================================================
// 12. 自动对焦
// ================================================================
bool ConfigMgr::autoFocus(unsigned short mode, double kp, short reverse, short channel) 
{
    m_lastError = GtsHal::autoFocus(mode, kp, reverse, channel);
    if (m_lastError != 0) {
        emit errorOccurred(channel, m_lastError, QStringLiteral("autoFocus: ") + lastErrorString());
        return false;
    }
    return true;
}

bool ConfigMgr::setAutoFocusRefVol(double refVol, double maxVol, double minVol, short channel) 
{
    m_lastError = GtsHal::setAutoFocusRefVol(refVol, maxVol, minVol, channel);
    if (m_lastError != 0) {
        emit errorOccurred(channel, m_lastError, QStringLiteral("setAutoFocusRefVol: ") + lastErrorString());
        return false;
    }
    return true;
}

bool ConfigMgr::getAutoFocusStatus(unsigned short& status) const 
{
    m_lastError = GtsHal::getAutoFocusStatus(&status, 1);
    return m_lastError == 0;
}

bool ConfigMgr::configAutoFocus(short chnAdc, short channel) 
{
    m_lastError = GtsHal::configAutoFocus(chnAdc, channel);
    if (m_lastError != 0) {
        emit errorOccurred(channel, m_lastError, QStringLiteral("configAutoFocus: ") + lastErrorString());
        return false;
    }
    return true;
}

bool ConfigMgr::setAutoFocusAuxParams(double kf, double kd, double limitKd, short channel) 
{
    m_lastError = GtsHal::setAutoFocusAuxPrm(kf, kd, limitKd, channel);
    if (m_lastError != 0) {
        emit errorOccurred(channel, m_lastError, QStringLiteral("setAutoFocusAuxPrm: ") + lastErrorString());
        return false;
    }
    return true;
}

bool ConfigMgr::setAutoFocusDeadVoltage(double voltage, short channel) 
{
    m_lastError = GtsHal::setAutoFocusDeadVoltage(voltage, channel);
    if (m_lastError != 0) {
        emit errorOccurred(channel, m_lastError, QStringLiteral("setAutoFocusDeadVoltage: ") + lastErrorString());
        return false;
    }
    return true;
}

// ================================================================
// 13. 信号检测 / 滤波
// ================================================================
bool ConfigMgr::setSignalTimeFilter(short type, short index, double filterWidth) 
{
    m_lastError = GtsHal::setSignalTimeFilter(type, index, filterWidth);
    if (m_lastError != 0) {
        emit errorOccurred(index, m_lastError, QStringLiteral("setSignalTimeFilter: ") + lastErrorString());
        return false;
    }
    return true;
}

double ConfigMgr::getSignalTimeFilter(short type, short index) const 
{
    double width = 0.0;
    GtsHal::getSignalTimeFilter(type, index, &width);
    return width;
}

bool ConfigMgr::clearSignalDetect(short index) 
{
    m_lastError = GtsHal::clearSignalDetect(index);
    if (m_lastError != 0) {
        emit errorOccurred(index, m_lastError, QStringLiteral("clearSignalDetect: ") + lastErrorString());
        return false;
    }
    return true;
}

bool ConfigMgr::setSignalDetect(short index, short enable, const TSignalDetect& prm) 
{
    m_lastError = GtsHal::setSignalDetect(index, enable, prm);
    if (m_lastError != 0) {
        emit errorOccurred(index, m_lastError, QStringLiteral("setSignalDetect: ") + lastErrorString());
        return false;
    }
    return true;
}

bool ConfigMgr::getSignalDetect(short index, short& enable, TSignalDetect& prm) const 
{
    m_lastError = GtsHal::getSignalDetect(index, &enable, &prm);
    return m_lastError == 0;
}

bool ConfigMgr::getSignalDetectStatus(short index, TSignalDetectStatus& status) const 
{
    m_lastError = GtsHal::getSignalDetectStatus(index, &status);
    return m_lastError == 0;
}

// ================================================================
// 14. 变量
// ================================================================
bool ConfigMgr::setLongVar(short index, long value) 
{
    m_lastError = GtsHal::setLongVar(index, value);
    if (m_lastError != 0) {
        emit errorOccurred(index, m_lastError, QStringLiteral("setLongVar: ") + lastErrorString());
        return false;
    }
    return true;
}

long ConfigMgr::getLongVar(short index) const 
{
    long value = 0;
    GtsHal::getLongVar(index, &value);
    return value;
}

bool ConfigMgr::setDoubleVar(short index, double value) 
{
    m_lastError = GtsHal::setDoubleVar(index, value);
    if (m_lastError != 0) {
        emit errorOccurred(index, m_lastError, QStringLiteral("setDoubleVar: ") + lastErrorString());
        return false;
    }
    return true;
}

double ConfigMgr::getDoubleVar(short index) const 
{
    double value = 0.0;
    GtsHal::getDoubleVar(index, &value);
    return value;
}

bool ConfigMgr::setFlagVar(short index, short mode, short value) 
{
    m_lastError = GtsHal::setFlagVar(index, mode, value);
    if (m_lastError != 0) {
        emit errorOccurred(index, m_lastError, QStringLiteral("setFlagVar: ") + lastErrorString());
        return false;
    }
    return true;
}

bool ConfigMgr::getFlagVar(short index, short& mode, short& value) const 
{
    m_lastError = GtsHal::getFlagVar(index, &mode, &value);
    return m_lastError == 0;
}

// ================================================================
// 15. 脚本
// ================================================================
bool ConfigMgr::compile(const QString& fileName, TCompileInfo& wrongInfo) 
{
    m_lastError = GtsHal::compile(fileName.toLocal8Bit().constData(), &wrongInfo);
    if (m_lastError != 0) {
        emit errorOccurred(-1, m_lastError, QStringLiteral("compile: ") + lastErrorString());
        return false;
    }
    return true;
}

bool ConfigMgr::download(const QString& fileName) 
{
    m_lastError = GtsHal::download(fileName.toLocal8Bit().constData());
    if (m_lastError != 0) {
        emit errorOccurred(-1, m_lastError, QStringLiteral("download: ") + lastErrorString());
        return false;
    }
    return true;
}

bool ConfigMgr::getFunctionId(const QString& funName, short& funId) 
{
    m_lastError = GtsHal::getFunId(funName.toLocal8Bit().constData(), &funId);
    if (m_lastError != 0) {
        emit errorOccurred(-1, m_lastError, QStringLiteral("getFunId: ") + lastErrorString());
        return false;
    }
    return true;
}

bool ConfigMgr::bind(short thread, short funId, short page) 
{
    m_lastError = GtsHal::bind(thread, funId, page);
    if (m_lastError != 0) {
        emit errorOccurred(thread, m_lastError, QStringLiteral("bind: ") + lastErrorString());
        return false;
    }
    return true;
}

bool ConfigMgr::runThread(short thread) 
{
    m_lastError = GtsHal::runThread(thread);
    if (m_lastError != 0) {
        emit errorOccurred(thread, m_lastError, QStringLiteral("runThread: ") + lastErrorString());
        return false;
    }
    return true;
}

bool ConfigMgr::stopThread(short thread) 
{
    m_lastError = GtsHal::stopThread(thread);
    if (m_lastError != 0) {
        emit errorOccurred(thread, m_lastError, QStringLiteral("stopThread: ") + lastErrorString());
        return false;
    }
    return true;
}

bool ConfigMgr::pauseThread(short thread) 
{
    m_lastError = GtsHal::pauseThread(thread);
    if (m_lastError != 0) {
        emit errorOccurred(thread, m_lastError, QStringLiteral("pauseThread: ") + lastErrorString());
        return false;
    }
    return true;
}

bool ConfigMgr::getThreadStatus(short thread, TThreadSts& sts) const 
{
    m_lastError = GtsHal::getThreadSts(thread, &sts);
    return m_lastError == 0;
}

bool ConfigMgr::getVarId(const QString& funName, const QString& varName, TVarInfo& varInfo) const 
{
    m_lastError = GtsHal::getVarId(funName.toLocal8Bit().constData(),
        varName.toLocal8Bit().constData(), &varInfo);
    return m_lastError == 0;
}

bool ConfigMgr::setVarValue(short page, const TVarInfo& varInfo, double* pValue, short count) 
{
    m_lastError = GtsHal::setVarValue(page, varInfo, pValue, count);
    if (m_lastError != 0) {
        emit errorOccurred(page, m_lastError, QStringLiteral("setVarValue: ") + lastErrorString());
        return false;
    }
    return true;
}

bool ConfigMgr::getVarValue(short page, const TVarInfo& varInfo, double* pValue, short count) const 
{
    m_lastError = GtsHal::getVarValue(page, varInfo, pValue, count);
    return m_lastError == 0;
}

// ================================================================
// 16. 摇杆
// ================================================================
bool ConfigMgr::setJoystickMapAxis(short idx, short* axis) 
{
    m_lastError = GtsHal::setJoystickMapAxis(idx, axis);
    if (m_lastError != 0) {
        emit errorOccurred(idx, m_lastError, QStringLiteral("setJoystickMapAxis: ") + lastErrorString());
        return false;
    }
    return true;
}

bool ConfigMgr::getJoystickMapAxis(short idx, short* pAxis) const 
{
    m_lastError = GtsHal::getJoystickMapAxis(idx, pAxis);
    return m_lastError == 0;
}

bool ConfigMgr::joystickEnable(short idx, short enable) 
{
    m_lastError = GtsHal::joystickEnable(idx, enable);
    if (m_lastError != 0) {
        emit errorOccurred(idx, m_lastError, QStringLiteral("joystickEnable: ") + lastErrorString());
        return false;
    }
    return true;
}

bool ConfigMgr::setJoystickSerialPortParams(short idx, const TSericalPortPrm& prm) 
{
    m_lastError = GtsHal::setJoystickSericalPortPrm(idx, prm);
    if (m_lastError != 0) {
        emit errorOccurred(idx, m_lastError, QStringLiteral("setJoystickSericalPortPrm: ") + lastErrorString());
        return false;
    }
    return true;
}

bool ConfigMgr::getJoystickSerialPortParams(short idx, TSericalPortPrm& prm) const 
{
    m_lastError = GtsHal::getJoystickSericalPortPrm(idx, &prm);
    return m_lastError == 0;
}

bool ConfigMgr::joystickCheckEnable(short idx, short checkEnable) 
{
    m_lastError = GtsHal::joystickCheckEnable(idx, checkEnable);
    if (m_lastError != 0) {
        emit errorOccurred(idx, m_lastError, QStringLiteral("joystickCheckEnable: ") + lastErrorString());
        return false;
    }
    return true;
}

long ConfigMgr::getJoystickStatus(short idx) const 
{
    long sts = 0;
    GtsHal::getJoystickSts(idx, &sts);
    return sts;
}

long ConfigMgr::getJoystickValue(short idx) const 
{
    long val = 0;
    GtsHal::getJoystickValue(idx, &val);
    return val;
}

bool ConfigMgr::setJoystickMotionParams(short idx, const TJoystickMoitonPrm& prm) 
{
    m_lastError = GtsHal::setJoystickMotionPrm(idx, prm);
    if (m_lastError != 0) {
        emit errorOccurred(idx, m_lastError, QStringLiteral("setJoystickMotionPrm: ") + lastErrorString());
        return false;
    }
    return true;
}

bool ConfigMgr::getJoystickMotionParams(short idx, TJoystickMoitonPrm& prm) const 
{
    m_lastError = GtsHal::getJoystickMotionPrm(idx, &prm);
    return m_lastError == 0;
}

bool ConfigMgr::setJoystickMotionVel(short idx, const TJoystickMoitonVel& vel) 
{
    m_lastError = GtsHal::setJoystickMotionVel(idx, vel);
    if (m_lastError != 0) {
        emit errorOccurred(idx, m_lastError, QStringLiteral("setJoystickMotionVel: ") + lastErrorString());
        return false;
    }
    return true;
}

bool ConfigMgr::getJoystickMotionVel(short idx, TJoystickMoitonVel& vel) const 
{
    m_lastError = GtsHal::getJoystickMotionVel(idx, &vel);
    return m_lastError == 0;
}

bool ConfigMgr::joystickReset(short idx) 
{
    m_lastError = GtsHal::joystickReset(idx);
    if (m_lastError != 0) {
        emit errorOccurred(idx, m_lastError, QStringLiteral("joystickReset: ") + lastErrorString());
        return false;
    }
    return true;
}

// ================================================================
// 17. 轴叠加 / 输入整形 / 运动平滑
// ================================================================
bool ConfigMgr::setMotionSmooth(short axis, const TMotionSmooth& smooth) 
{
    if (!isValidAxis(axis)) {
        emit errorOccurred(axis, -1, QStringLiteral("轴号无效: %1").arg(axis));
        return false;
    }
    m_lastError = GtsHal::setMotionSmooth(axis, smooth);
    if (m_lastError != 0) {
        emit errorOccurred(axis, m_lastError, QStringLiteral("setMotionSmooth: ") + lastErrorString());
        return false;
    }
    return true;
}

bool ConfigMgr::getMotionSmooth(short axis, TMotionSmooth& smooth) const 
{
    if (!isValidAxis(axis)) return false;
    m_lastError = GtsHal::getMotionSmooth(axis, &smooth);
    return m_lastError == 0;
}

bool ConfigMgr::setAxisAddition(short axis, short dataType, short additionIndex, short additionType) 
{
    if (!isValidAxis(axis)) {
        emit errorOccurred(axis, -1, QStringLiteral("轴号无效: %1").arg(axis));
        return false;
    }
    m_lastError = GtsHal::setAxisAddition(axis, dataType, additionIndex, additionType);
    if (m_lastError != 0) {
        emit errorOccurred(axis, m_lastError, QStringLiteral("setAxisAddition: ") + lastErrorString());
        return false;
    }
    return true;
}

bool ConfigMgr::getAxisAddition(short axis, short dataType, short& additionIndex, short& additionType) const 
{
    if (!isValidAxis(axis)) return false;
    m_lastError = GtsHal::getAxisAddition(axis, dataType, &additionIndex, &additionType);
    return m_lastError == 0;
}

bool ConfigMgr::setAxisInputShaping(short axis, short enable, short count, double k) 
{
    if (!isValidAxis(axis)) {
        emit errorOccurred(axis, -1, QStringLiteral("轴号无效: %1").arg(axis));
        return false;
    }
    m_lastError = GtsHal::setAxisInputShaping(axis, enable, count, k);
    if (m_lastError != 0) {
        emit errorOccurred(axis, m_lastError, QStringLiteral("setAxisInputShaping: ") + lastErrorString());
        return false;
    }
    return true;
}

bool ConfigMgr::setMcOverride(short axis, short mode, double override, double smoothTime) 
{
    if (!isValidAxis(axis)) {
        emit errorOccurred(axis, -1, QStringLiteral("轴号无效: %1").arg(axis));
        return false;
    }
    m_lastError = GtsHal::setMcOverride(axis, mode, override, smoothTime);
    if (m_lastError != 0) {
        emit errorOccurred(axis, m_lastError, QStringLiteral("setMcOverride: ") + lastErrorString());
        return false;
    }
    return true;
}

bool ConfigMgr::getMcOverride(short axis, short mode, double& overrideTarget,
    double& smoothTime, double& overrideVal) const 
{
    if (!isValidAxis(axis)) return false;
    m_lastError = GtsHal::getMcOverride(axis, mode, &overrideTarget, &smoothTime, &overrideVal);
    return m_lastError == 0;
}

// ================================================================
// 18. 步进模式 / 输出电平
// ================================================================
bool ConfigMgr::setStepOutLevel(short axis, short type, short reverse) 
{
    if (!isValidAxis(axis)) {
        emit errorOccurred(axis, -1, QStringLiteral("轴号无效: %1").arg(axis));
        return false;
    }
    m_lastError = GtsHal::setStepOutLevel(axis, type, reverse);
    if (m_lastError != 0) {
        emit errorOccurred(axis, m_lastError, QStringLiteral("setStepOutLevel: ") + lastErrorString());
        return false;
    }
    return true;
}

bool ConfigMgr::getStepOutLevel(short axis, short type, short& reverse) const 
{
    if (!isValidAxis(axis)) return false;
    m_lastError = GtsHal::getStepOutLevel(axis, type, &reverse);
    return m_lastError == 0;
}

bool ConfigMgr::stepDir(short step) 
{
    m_lastError = GtsHal::stepDir(step);
    if (m_lastError != 0) {
        emit errorOccurred(step, m_lastError, QStringLiteral("stepDir: ") + lastErrorString());
        return false;
    }
    return true;
}

bool ConfigMgr::stepPulse(short step) 
{
    m_lastError = GtsHal::stepPulse(step);
    if (m_lastError != 0) {
        emit errorOccurred(step, m_lastError, QStringLiteral("stepPulse: ") + lastErrorString());
        return false;
    }
    return true;
}

bool ConfigMgr::stepOrthogonal(short step) 
{
    m_lastError = GtsHal::stepOrthogonal(step);
    if (m_lastError != 0) {
        emit errorOccurred(step, m_lastError, QStringLiteral("stepOrthogonal: ") + lastErrorString());
        return false;
    }
    return true;
}

bool ConfigMgr::getMachineWorkPos(short crd, short mode, double& machinePos, double& workPos) const 
{
    m_lastError = GtsHal::getMachineWorkPos(crd, mode, &machinePos, &workPos);
    return m_lastError == 0;
}

bool ConfigMgr::checkCrdLineTime(short crd, double x, double y, double z,
    double& velMax, double& acc, double& velEnd,
    double& time, long& errorCode) const 
{
    m_lastError = GtsHal::checkCrdLineTime(crd, x, y, z, &velMax, &acc, &velEnd, &time, &errorCode);
    return m_lastError == 0;
}

// ================================================================
// 19. 便利方法
// ================================================================
QString ConfigMgr::lastErrorString() const 
{
    return GtsErrorToString(m_lastError);
}
