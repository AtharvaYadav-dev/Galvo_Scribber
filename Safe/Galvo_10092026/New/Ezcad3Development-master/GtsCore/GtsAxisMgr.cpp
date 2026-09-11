#include <QMessageBox>

#include "GtsAxisMgr.h"
#include "GtsMgr.h"

AxisMgr::AxisMgr(GtsMgr* totalMgr, QObject* parent)
    : QObject(parent)
    , m_gtsMgr(totalMgr)
{
}

AxisMgr::~AxisMgr() 
{
    // 析构时禁止所有轴
    disableAll();
    m_gtsMgr = nullptr;
}

void AxisMgr::getAxisStatusAndMotionInfo(std::vector<SingleAxisInfo>& vecAxis)
{
    int n = m_gtsMgr->axisCount();
    if (n <= 0) return;
    if ((int)vecAxis.size() < n) vecAxis.resize(n);

    long sts = 0;
    for (short axis = 1; axis <= n; ++axis) {
        int idx = axis - 1;
        vecAxis[idx].axisIndex = axis;
        GtsHal::getSts(axis, &sts);
        vecAxis[idx].parseStatus(sts);

        // 规划器原始数据
        vecAxis[idx].prfPosOriginal = prfPosition(axis);   // pulse
        vecAxis[idx].prfVelOriginal = prfVelocity(axis);   // pulse/ms
        vecAxis[idx].prfAccOriginal = prfAcceleration(axis); // pulse/ms²

        // pulse → mm：乘 mmPerPulse (= alpha/beta)
        double mpp = m_gtsMgr->mmPerPulse(axis);
        vecAxis[idx].prfPosMm = vecAxis[idx].prfPosOriginal * mpp;   // mm
        vecAxis[idx].prfVelMm = vecAxis[idx].prfVelOriginal * mpp;   // mm/ms
        vecAxis[idx].prfAccMm = vecAxis[idx].prfAccOriginal * mpp;   // mm/ms²

        ControlMode mode = m_gtsMgr->configMgr()->controlMode(axis);

        // ── 开环/模拟：编码器 = 规划器 ──
        if (mode == ControlMode::OpenLoop || mode == ControlMode::Simulation) {
            vecAxis[idx].encPos = vecAxis[idx].prfPosOriginal;
            vecAxis[idx].encVel = vecAxis[idx].prfVelOriginal;
            vecAxis[idx].encPosMm = vecAxis[idx].prfPosMm;
            vecAxis[idx].encVelMm = vecAxis[idx].prfVelMm;
        }
        else {
            // ── 闭环：读真实编码器，同样需要脉冲→mm 换算 ──
            vecAxis[idx].encPos = encoderPosition(axis);   // pulse
            vecAxis[idx].encVel = encoderVelocity(axis);   // pulse/ms
            double ppm = m_gtsMgr->pulsePerMm(axis);
            if (ppm > 0.0) {
                vecAxis[idx].encPosMm = vecAxis[idx].encPos / ppm;
                vecAxis[idx].encVelMm = vecAxis[idx].encVel / ppm * 1000.0;
            }
        }
    }
}


short AxisMgr::setProfileScale(short axis, long alpha, long beta)
{
    return GT_ProfileScale(axis, static_cast<short>(alpha), static_cast<short>(beta));
}

short AxisMgr::getProfileScale(short axis, long& alpha, long& beta)
{
    return GT_GetProfileScale(axis, &alpha, &beta);
}

short AxisMgr::setEncoderScale(short axis, long alpha, long beta)
{
    return GtsHal::encScale(axis, static_cast<short>(alpha), static_cast<short>(beta));
}

short AxisMgr::getEncoderScale(short axis, long& alpha, long& beta)
{
    return GT_GetEncoderScale(axis, &alpha, &beta);
}


bool AxisMgr::isValidAxis(short axis)  
{
    bool valid = (axis > 0 && axis <= m_gtsMgr->axisCount());
    if (!valid) {
        emit errorOccurred(axis, -1, QStringLiteral("轴号无效: %1 (有效范围 1-%2)")
            .arg(axis).arg(m_gtsMgr->axisCount() - 1));
    }
    return valid;
}

bool AxisMgr::enable(short axis) 
{
    if (!isValidAxis(axis)) return false;

    m_lastError = GtsHal::axisOn(axis);

    QMessageBox::information(nullptr,
        QStringLiteral("GT_AxisOn 排查"),
        QStringLiteral("轴%1 enable: ret=%2 (%3)")
        .arg(axis)
        .arg(m_lastError)
        .arg(GtsErrorToString(m_lastError)));

    if (m_lastError != 0) {
        emit errorOccurred(axis, m_lastError, QStringLiteral("axisOn: ") + lastErrorString());
        return false;
    }
    emit logMessage(QStringLiteral("轴%1已使能").arg(axis));
    return true;
}

bool AxisMgr::disable(short axis)
{
    if (!isValidAxis(axis)) return false;

    m_lastError = GtsHal::axisOff(axis);
    if (m_lastError != 0) {
        return false;

    }
    emit logMessage(QStringLiteral("轴%1已禁用").arg(axis));
    return true;
}

bool AxisMgr::enableMulti(unsigned long mask) 
{
    m_lastError = GtsHal::multiAxisOn(mask);
    if (m_lastError != 0) {
        emit errorOccurred(-1, m_lastError, QStringLiteral("multiAxisOn: ") + lastErrorString());
        return false;
    }
    return true;
}

bool AxisMgr::disableMulti(unsigned long mask) 
{
    m_lastError = GtsHal::multiAxisOff(mask);
    if (m_lastError != 0) {
        emit errorOccurred(-1, m_lastError, QStringLiteral("multiAxisOff: ") + lastErrorString());
        return false;
    }
    return true;
}

bool AxisMgr::enableAll() 
{
    unsigned long mask = (1UL << m_gtsMgr->axisCount()) - 1;
    return enableMulti(mask);
}

bool AxisMgr::disableAll() 
{
    unsigned long mask = (1UL << m_gtsMgr->axisCount()) - 1;
    return disableMulti(mask);
}

bool AxisMgr::isEnabled(short axis)  
{
    if (!isValidAxis(axis)) return false;

    long sts = 0;
    GtsHal::getSts(axis, &sts);
    return (sts & 0x200) != 0;
}

bool AxisMgr::setOnDelayTime(unsigned short ms) 
{
    m_lastError = GtsHal::setAxisOnDelayTime(ms);
    return m_lastError == 0;
}

unsigned short AxisMgr::onDelayTime() 
{
    unsigned short ms = 0;
    GtsHal::getAxisOnDelayTime(&ms);
    return ms;
}


bool AxisMgr::stop(short axis, long option) 
{
    if (!isValidAxis(axis)) return false;
    long mask = 1L << (axis - 1);
    long stopOption = (option != 0) ? mask : 0;
    m_lastError = GtsHal::stop(mask, stopOption);
    if (m_lastError != 0) {
        emit errorOccurred(axis, m_lastError, QStringLiteral("stop: ") + lastErrorString());
        return false;
    }
    emit logMessage(QStringLiteral("轴%1%2").arg(axis).arg(stopOption ? QStringLiteral("已紧急停止") : QStringLiteral("已减速停止")), Qt::darkGreen);
    return true;
}

bool AxisMgr::stopAll(long option) 
{
    long mask = (1L << m_gtsMgr->axisCount()) - 1;
    m_lastError = GtsHal::stop(mask, option);
    if (m_lastError != 0) {
        emit errorOccurred(-1, m_lastError, QStringLiteral("stop: ") + lastErrorString());
        return false;
    }
    return true;
}

bool AxisMgr::stopMulti(long mask, long option) 
{
    m_lastError = GtsHal::stop(mask, option);
    if (m_lastError != 0) {
        emit errorOccurred(-1, m_lastError, QStringLiteral("stop: ") + lastErrorString());
        return false;
    }
    return true;
}


bool AxisMgr::alarmOn(short axis) 
{
    if (!isValidAxis(axis)) return false;

    m_lastError = GtsHal::alarmOn(axis);
    if (m_lastError != 0) {
        emit errorOccurred(axis, m_lastError, QStringLiteral("alarmOn: ") + lastErrorString());
        return false;
    }
    return true;
}

bool AxisMgr::alarmOff(short axis) 
{
    if (!isValidAxis(axis)) return false;

    m_lastError = GtsHal::alarmOff(axis);
    if (m_lastError != 0) {
        emit errorOccurred(axis, m_lastError, QStringLiteral("alarmOff: ") + lastErrorString());
        return false;
    }
    return true;
}

bool AxisMgr::isAlarm(short axis) 
{
    if (!isValidAxis(axis)) return false;

    long sts = 0;
    GtsHal::getSts(axis, &sts);
    return (sts & 0x02) != 0;
}

bool AxisMgr::limitOn(short axis, short limitType) 
{
    if (!isValidAxis(axis)) return false;

    m_lastError = GtsHal::lmtsOn(axis, limitType);
    if (m_lastError != 0) {
        emit errorOccurred(axis, m_lastError, QStringLiteral("lmtsOn: ") + lastErrorString());
        return false;
    }
    return true;
}

bool AxisMgr::limitOff(short axis, short limitType) 
{
    if (!isValidAxis(axis)) return false;

    m_lastError = GtsHal::lmtsOff(axis, limitType);
    if (m_lastError != 0) {
        emit errorOccurred(axis, m_lastError, QStringLiteral("lmtsOff: ") + lastErrorString());
        return false;
    }
    return true;
}

bool AxisMgr::setLimitSense(unsigned short sense) 
{
    m_lastError = GtsHal::lmtSns(sense);
    return m_lastError == 0;
}

bool AxisMgr::setSoftLimit(short axis, long positive, long negative) 
{
    if (!isValidAxis(axis)) return false;

    m_lastError = GtsHal::setSoftLimit(axis, positive, negative);
    if (m_lastError != 0) {
        emit errorOccurred(axis, m_lastError, QStringLiteral("setSoftLimit: ") + lastErrorString());
        return false;
    }
    return true;
}

bool AxisMgr::getSoftLimit(short axis, long& positive, long& negative) 
{
    if (!isValidAxis(axis)) return false;

    m_lastError = GtsHal::getSoftLimit(axis, &positive, &negative);
    return m_lastError == 0;
}


long AxisMgr::status(short axis) 
{
    if (!isValidAxis(axis)) return -1;

    long sts = 0;
    m_lastError = GtsHal::getSts(axis, &sts);
    return sts;
}

bool AxisMgr::clearStatus(short axis) 
{
    if (!isValidAxis(axis)) return false;

    m_lastError = GtsHal::clrSts(axis, axis);
    if (m_lastError != 0) {
        emit errorOccurred(axis, m_lastError, QStringLiteral("clrSts: ") + lastErrorString());
        return false;
    }
    emit logMessage(QStringLiteral("轴%1状态已清除").arg(axis));
    return true;
}

bool AxisMgr::zeroPosition(short axis) 
{
    if (!isValidAxis(axis)) return false;

    m_lastError = GtsHal::zeroPos(axis,axis);
    if (m_lastError != 0) {
        emit errorOccurred(axis, m_lastError, QStringLiteral("zeroPos: ") + lastErrorString());
        return false;
    }
    emit logMessage(QStringLiteral("轴%1位置已清零").arg(axis));
    return true;
}

bool AxisMgr::syncPosition(long mask) 
{
    m_lastError = GtsHal::synchAxisPos(mask);
    if (m_lastError != 0) {
        emit errorOccurred(-1, m_lastError, QStringLiteral("synchAxisPos: ") + lastErrorString());
        return false;
    }
    return true;
}


bool AxisMgr::setControlMode(short axis, short mode) 
{
    if (!isValidAxis(axis)) return false;

    m_lastError = GtsHal::ctrlMode(axis, mode);
    if (m_lastError != 0) {
        emit errorOccurred(axis, m_lastError, QStringLiteral("ctrlMode: ") + lastErrorString());
        return false;
    }
    return true;
}

bool AxisMgr::setAxisMode(short axis, short mode) 
{
    if (!isValidAxis(axis)) return false;

    m_lastError = GtsHal::setAxisMode(axis, mode);
    if (m_lastError != 0) {
        emit errorOccurred(axis, m_lastError, QStringLiteral("setAxisMode: ") + lastErrorString());
        return false;
    }
    return true;
}

short AxisMgr::getAxisMode(short axis) 
{
    if (!isValidAxis(axis)) return -1;

    short mode = 0;
    m_lastError = GtsHal::getAxisMode(axis, &mode);
    return mode;
}

bool AxisMgr::setFollowErrorLimit(short control, long error) 
{
    m_lastError = GtsHal::setPosErr(control, error);
    if (m_lastError != 0) {
        emit errorOccurred(control, m_lastError, QStringLiteral("setPosErr: ") + lastErrorString());
        return false;
    }
    return true;
}

long AxisMgr::getFollowErrorLimit(short control) 
{
    long error = 0;
    m_lastError = GtsHal::getPosErr(control, &error);
    return error;
}

bool AxisMgr::setFollowErrorMode(short axis, short mode) 
{
    if (!isValidAxis(axis)) return false;

    m_lastError = GtsHal::setAxisFollowErrorMode(axis, mode);
    if (m_lastError != 0) {
        emit errorOccurred(axis, m_lastError, QStringLiteral("setAxisFollowErrorMode: ") + lastErrorString());
        return false;
    }
    return true;
}

short AxisMgr::getFollowErrorMode(short axis) 
{
    if (!isValidAxis(axis)) return -1;

    short mode = 0;
    m_lastError = GtsHal::getAxisFollowErrorMode(axis, &mode);
    return mode;
}


bool AxisMgr::setStopDecel(short profile, double smooth, double abrupt) 
{
    m_lastError = GtsHal::setStopDec(profile, smooth, abrupt);
    if (m_lastError != 0) {
        emit errorOccurred(profile, m_lastError, QStringLiteral("setStopDec: ") + lastErrorString());
        return false;
    }
    return true;
}

bool AxisMgr::getStopDecel(short profile, double& smooth, double& abrupt) 
{
    m_lastError = GtsHal::getStopDec(profile, &smooth, &abrupt);
    return m_lastError == 0;
}

bool AxisMgr::setStopIO(short axis, short stopType, short inputType, short inputIndex) 
{
    if (!isValidAxis(axis)) return false;

    m_lastError = GtsHal::setStopIo(axis, stopType, inputType, inputIndex);
    if (m_lastError != 0) {
        emit errorOccurred(axis, m_lastError, QStringLiteral("setStopIo: ") + lastErrorString());
        return false;
    }
    return true;
}

double AxisMgr::encoderPosition(short axis) 
{
    if (!isValidAxis(axis)) return 0.0;

    double pos = 0.0;
    GtsHal::getAxisEncPos(axis, &pos);
    return pos;
}

double AxisMgr::encoderVelocity(short axis)
{
    if (!isValidAxis(axis)) return 0.0;

    double vel = 0.0;
    GtsHal::getAxisEncVel(axis, &vel);
    return vel;
}

double AxisMgr::encoderAcceleration(short axis) 
{
    if (!isValidAxis(axis)) return 0.0;

    double acc = 0.0;
    GtsHal::getAxisEncAcc(axis, &acc);
    return acc;
}

double AxisMgr::prfPosition(short axis)
{
    if (!isValidAxis(axis)) return 0.0;

    double pos = 0.0;
    GtsHal::getAxisPrfPos(axis, &pos);
    return pos;
}

double AxisMgr::prfVelocity(short axis)
{
    if (!isValidAxis(axis)) return 0.0;

    double vel = 0.0;
    GtsHal::getAxisPrfVel(axis, &vel);
    return vel;
}

double AxisMgr::prfAcceleration(short axis)
{
    if (!isValidAxis(axis)) return 0.0;

    double acc = 0.0;
    GtsHal::getAxisPrfAcc(axis, &acc);
    return acc;
}


double AxisMgr::trackingError(short axis) 
{
    if (!isValidAxis(axis)) return 0.0;

    double err = 0.0;
    GtsHal::getAxisError(axis, &err);
    return err;
}


QString AxisMgr::lastErrorString()
{
    return GtsErrorToString(m_lastError);
}

QString AxisMgr::statusToString(long sts) 
{
    QStringList desc;
    if (sts & 0x0001) desc << "使能中";
    if (sts & 0x0002) desc << "报警";
    if (sts & 0x0004) desc << "正限位";
    if (sts & 0x0008) desc << "负限位";
    if (sts & 0x0010) desc << "跟随误差超限";
    if (sts & 0x0020) desc << "运动中";
    if (sts & 0x0040) desc << "急停";
    if (sts & 0x0080) desc << "回零中";
    if (sts & 0x0100) desc << "正软限位";
    if (sts & 0x0200) desc << "负软限位";

    if (desc.isEmpty()) return QStringLiteral("正常");
    return desc.join(" | ");
}

bool AxisMgr::setStepPulseDir(short step)
{
    m_lastError = GtsHal::stepDir(step);
    if (m_lastError != 0) {
        emit errorOccurred(step, m_lastError, QStringLiteral("stepDir: ") + lastErrorString());
        return false;
    }
    return true;
}

bool AxisMgr::setStepPulseCCW(short step)
{
    m_lastError = GtsHal::stepPulse(step);
    if (m_lastError != 0) {
        emit errorOccurred(step, m_lastError, QStringLiteral("stepPulse: ") + lastErrorString());
        return false;
    }
    return true;
}

bool AxisMgr::setDacBias(short dac, short bias)
{
    m_lastError = GtsHal::setMtrBias(dac, bias);
    if (m_lastError != 0) {
        emit errorOccurred(dac, m_lastError, QStringLiteral("setMtrBias: ") + lastErrorString());
        return false;
    }
    return true;
}

short AxisMgr::getDacBias(short dac) const
{
    short bias = 0;
    GtsHal::getMtrBias(dac, &bias);
    return bias;
}

bool AxisMgr::setDacLimit(short dac, short limit)
{
    m_lastError = GtsHal::setMtrLmt(dac, limit);
    if (m_lastError != 0) {
        emit errorOccurred(dac, m_lastError, QStringLiteral("setMtrLmt: ") + lastErrorString());
        return false;
    }
    return true;
}

short AxisMgr::getDacLimit(short dac) const
{
    short limit = 0;
    GtsHal::getMtrLmt(dac, &limit);
    return limit;
}
