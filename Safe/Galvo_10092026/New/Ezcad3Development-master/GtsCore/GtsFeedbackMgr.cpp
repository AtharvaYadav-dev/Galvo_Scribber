#include "GtsFeedbackMgr.h"
#include "GtsMgr.h"

FeedbackMgr::FeedbackMgr(GtsMgr* totalMgr, QObject* parent)
    : QObject(parent)
    , m_gtsMgr(totalMgr)
{
}

FeedbackMgr::~FeedbackMgr() 
{
    m_gtsMgr = nullptr;
}

bool FeedbackMgr::checkEncoder(short encoder) const 
{
    return (encoder >= 0 && encoder < m_gtsMgr->axisCount());
}

bool FeedbackMgr::checkAxis(short axis) const 
{
    return (axis >= 0 && axis < m_gtsMgr->axisCount());
}

// ================================================================
// 1. 编码器
// ================================================================
bool FeedbackMgr::setEncoderSense(unsigned short sense) 
{
    m_lastError = GtsHal::encSns(sense);
    if (m_lastError != 0) {
        emit errorOccurred(-1, m_lastError, QStringLiteral("encSns: ") + lastErrorString());
        return false;
    }
    return true;
}

bool FeedbackMgr::encoderOn(short encoder) 
{
    if (!checkEncoder(encoder)) {
        emit errorOccurred(encoder, -1, QStringLiteral("编码器号无效: %1").arg(encoder));
        return false;
    }
    m_lastError = GtsHal::encOn(encoder);
    if (m_lastError != 0) {
        emit errorOccurred(encoder, m_lastError, QStringLiteral("encOn: ") + lastErrorString());
        return false;
    }
    return true;
}

bool FeedbackMgr::encoderOff(short encoder) 
{
    if (!checkEncoder(encoder)) {
        emit errorOccurred(encoder, -1, QStringLiteral("编码器号无效: %1").arg(encoder));
        return false;
    }
    m_lastError = GtsHal::encOff(encoder);
    if (m_lastError != 0) {
        emit errorOccurred(encoder, m_lastError, QStringLiteral("encOff: ") + lastErrorString());
        return false;
    }
    return true;
}

bool FeedbackMgr::setEncoderPos(short encoder, long encPos) 
{
    if (!checkEncoder(encoder)) {
        emit errorOccurred(encoder, -1, QStringLiteral("编码器号无效: %1").arg(encoder));
        return false;
    }
    m_lastError = GtsHal::setEncPos(encoder, encPos);
    if (m_lastError != 0) {
        emit errorOccurred(encoder, m_lastError, QStringLiteral("setEncPos: ") + lastErrorString());
        return false;
    }
    return true;
}

double FeedbackMgr::encoderPos(short encoder) const 
{
    if (!checkEncoder(encoder)) return 0.0;
    double pos = 0.0;
    GtsHal::getEncPos(encoder, &pos);
    return pos;
}

double FeedbackMgr::encoderPosPreview(short encoder) const 
{
    if (!checkEncoder(encoder)) return 0.0;
    double pos = 0.0;
    GtsHal::getEncPosPre(encoder, &pos);
    return pos;
}

double FeedbackMgr::encoderVel(short encoder) const 
{
    if (!checkEncoder(encoder)) return 0.0;
    double vel = 0.0;
    GtsHal::getEncVel(encoder, &vel);
    return vel;
}

bool FeedbackMgr::setEncoderScale(short encoder, long alpha, long beta) 
{
    if (!checkEncoder(encoder)) {
        emit errorOccurred(encoder, -1, QStringLiteral("编码器号无效: %1").arg(encoder));
        return false;
    }
    m_lastError = GtsHal::setEncoderScale(encoder, alpha, beta);
    if (m_lastError != 0) {
        emit errorOccurred(encoder, m_lastError, QStringLiteral("setEncoderScale: ") + lastErrorString());
        return false;
    }
    return true;
}

bool FeedbackMgr::getEncoderScale(short encoder, long& alpha, long& beta) const 
{
    if (!checkEncoder(encoder)) return false;
    m_lastError = GtsHal::getEncoderScale(encoder, &alpha, &beta);
    return m_lastError == 0;
}

bool FeedbackMgr::setEncoderResponseCheck(short control, short dacThreshold,
    double minEncVel, long time) 
{
    m_lastError = GtsHal::setEncResponseCheck(control, dacThreshold, minEncVel, time);
    if (m_lastError != 0) {
        emit errorOccurred(control, m_lastError, QStringLiteral("setEncResponseCheck: ") + lastErrorString());
        return false;
    }
    return true;
}

bool FeedbackMgr::getEncoderResponseCheck(short control, short& dacThreshold,
    double& minEncVel, long& time) const 
{
    m_lastError = GtsHal::getEncResponseCheck(control, &dacThreshold, &minEncVel, &time);
    return m_lastError == 0;
}

bool FeedbackMgr::enableEncoderResponseCheck(short control) 
{
    m_lastError = GtsHal::enableEncResponseCheck(control);
    if (m_lastError != 0) {
        emit errorOccurred(control, m_lastError, QStringLiteral("enableEncResponseCheck: ") + lastErrorString());
        return false;
    }
    return true;
}

bool FeedbackMgr::disableEncoderResponseCheck(short control) 
{
    m_lastError = GtsHal::disableEncResponseCheck(control);
    if (m_lastError != 0) {
        emit errorOccurred(control, m_lastError, QStringLiteral("disableEncResponseCheck: ") + lastErrorString());
        return false;
    }
    return true;
}

bool FeedbackMgr::setEncoderOutputSelect(short mode) 
{
    m_lastError = GtsHal::setEncoderOutSelect(mode);
    if (m_lastError != 0) {
        emit errorOccurred(-1, m_lastError, QStringLiteral("setEncoderOutSelect: ") + lastErrorString());
        return false;
    }
    return true;
}

short FeedbackMgr::getEncoderOutputSelect() const
{
    short mode = 0;
    GtsHal::getEncoderOutSelect(&mode);
    return mode;
}

// ================================================================
// 2. 捕获 (Capture)
// ================================================================
bool FeedbackMgr::setCaptureMode(short encoder, short mode) 
{
    if (!checkEncoder(encoder)) {
        emit errorOccurred(encoder, -1, QStringLiteral("编码器号无效: %1").arg(encoder));
        return false;
    }
    m_lastError = GtsHal::setCaptureMode(encoder, mode);
    if (m_lastError != 0) {
        emit errorOccurred(encoder, m_lastError, QStringLiteral("setCaptureMode: ") + lastErrorString());
        return false;
    }
    return true;
}

short FeedbackMgr::getCaptureMode(short encoder) const 
{
    if (!checkEncoder(encoder)) return -1;
    short mode = 0;
    GtsHal::getCaptureMode(encoder, &mode);
    return mode;
}

bool FeedbackMgr::stopCapture(short encoder) 
{
    if (!checkEncoder(encoder)) {
        emit errorOccurred(encoder, -1, QStringLiteral("编码器号无效: %1").arg(encoder));
        return false;
    }
    m_lastError = GtsHal::stopCapture(encoder);
    if (m_lastError != 0) {
        emit errorOccurred(encoder, m_lastError, QStringLiteral("stopCapture: ") + lastErrorString());
        return false;
    }
    return true;
}

bool FeedbackMgr::getCaptureStatus(short encoder, short& status, long& value) const 
{
    if (!checkEncoder(encoder)) return false;
    m_lastError = GtsHal::getCaptureStatus(encoder, &status, &value);
    return m_lastError == 0;
}

bool FeedbackMgr::getCaptureStatusEx(short encoder, short& status, long& value,
    double& doubleVar, unsigned long& captureClock) const 
{
    if (!checkEncoder(encoder)) return false;
    m_lastError = GtsHal::getCaptureStatusEx(encoder, &status, &value,
        &doubleVar, &captureClock);
    return m_lastError == 0;
}

bool FeedbackMgr::setCaptureSense(short encoder, short mode, short sense) 
{
    if (!checkEncoder(encoder)) {
        emit errorOccurred(encoder, -1, QStringLiteral("编码器号无效: %1").arg(encoder));
        return false;
    }
    m_lastError = GtsHal::setCaptureSense(encoder, mode, sense);
    if (m_lastError != 0) {
        emit errorOccurred(encoder, m_lastError, QStringLiteral("setCaptureSense: ") + lastErrorString());
        return false;
    }
    return true;
}

bool FeedbackMgr::clearCaptureStatus(short encoder) 
{
    if (!checkEncoder(encoder)) {
        emit errorOccurred(encoder, -1, QStringLiteral("编码器号无效: %1").arg(encoder));
        return false;
    }
    m_lastError = GtsHal::clearCaptureStatus(encoder);
    if (m_lastError != 0) {
        emit errorOccurred(encoder, m_lastError, QStringLiteral("clearCaptureStatus: ") + lastErrorString());
        return false;
    }
    return true;
}

bool FeedbackMgr::setCaptureRepeat(short encoder, short count) 
{
    if (!checkEncoder(encoder)) {
        emit errorOccurred(encoder, -1, QStringLiteral("编码器号无效: %1").arg(encoder));
        return false;
    }
    m_lastError = GtsHal::setCaptureRepeat(encoder, count);
    if (m_lastError != 0) {
        emit errorOccurred(encoder, m_lastError, QStringLiteral("setCaptureRepeat: ") + lastErrorString());
        return false;
    }
    return true;
}

short FeedbackMgr::getCaptureRepeatStatus(short encoder) const 
{
    if (!checkEncoder(encoder)) return -1;
    short count = 0;
    GtsHal::getCaptureRepeatStatus(encoder, &count);
    return count;
}

bool FeedbackMgr::getCaptureRepeatPositions(short encoder, long* pValue,
    short startNum, short count) const 
{
    if (!checkEncoder(encoder)) return false;
    m_lastError = GtsHal::getCaptureRepeatPos(encoder, pValue, startNum, count);
    return m_lastError == 0;
}

bool FeedbackMgr::setCaptureEncoder(short trigger, short encoder) 
{
    m_lastError = GtsHal::setCaptureEncoder(trigger, encoder);
    if (m_lastError != 0) {
        emit errorOccurred(trigger, m_lastError, QStringLiteral("setCaptureEncoder: ") + lastErrorString());
        return false;
    }
    return true;
}

bool FeedbackMgr::getCaptureWidth(short trigger, short* pWidth) const 
{
    m_lastError = GtsHal::getCaptureWidth(trigger, pWidth);
    return m_lastError == 0;
}

// ================================================================
// 3. 回零 (Home)
// ================================================================
bool FeedbackMgr::homeInit() 
{
    m_lastError = GtsHal::homeInit();
    if (m_lastError != 0) {
        emit errorOccurred(-1, m_lastError, QStringLiteral("homeInit: ") + lastErrorString());
        return false;
    }
    return true;
}

bool FeedbackMgr::home(short axis, long pos, double vel, double acc, long offset) 
{
    if (!checkAxis(axis)) {
        emit errorOccurred(axis, -1, QStringLiteral("轴号无效: %1").arg(axis));
        return false;
    }
    m_lastError = GtsHal::home(axis, pos, vel, acc, offset);
    if (m_lastError != 0) {
        emit errorOccurred(axis, m_lastError, QStringLiteral("home: ") + lastErrorString());
        return false;
    }
    return true;
}

bool FeedbackMgr::homeIndex(short axis, long pos, long offset) 
{
    if (!checkAxis(axis)) {
        emit errorOccurred(axis, -1, QStringLiteral("轴号无效: %1").arg(axis));
        return false;
    }
    m_lastError = GtsHal::index(axis, pos, offset);
    if (m_lastError != 0) {
        emit errorOccurred(axis, m_lastError, QStringLiteral("index: ") + lastErrorString());
        return false;
    }
    return true;
}

bool FeedbackMgr::homeStop(short axis, long pos, double vel, double acc) 
{
    if (!checkAxis(axis)) {
        emit errorOccurred(axis, -1, QStringLiteral("轴号无效: %1").arg(axis));
        return false;
    }
    m_lastError = GtsHal::homeStop(axis, pos, vel, acc);
    if (m_lastError != 0) {
        emit errorOccurred(axis, m_lastError, QStringLiteral("homeStop: ") + lastErrorString());
        return false;
    }
    return true;
}

unsigned short FeedbackMgr::homeStatus(short axis) const 
{
    if (!checkAxis(axis)) return 0;
    unsigned short status = 0;
    GtsHal::homeSts(axis, &status);
    return status;
}

bool FeedbackMgr::goHome(short axis, const THomePrm& prm) 
{
    if (!checkAxis(axis)) {
        emit errorOccurred(axis, -1, QStringLiteral("轴号无效: %1").arg(axis));
        return false;
    }
    m_lastError = GtsHal::goHome(axis, prm);
    if (m_lastError != 0) {
        emit errorOccurred(axis, m_lastError, QStringLiteral("goHome: ") + lastErrorString());
        return false;
    }
    return true;
}

bool FeedbackMgr::getHomeParams(short axis, THomePrm& prm) const 
{
    if (!checkAxis(axis)) return false;
    m_lastError = GtsHal::getHomePrm(axis, &prm);
    return m_lastError == 0;
}

bool FeedbackMgr::getHomeStatus(short axis, THomeStatus& status) const 
{
    if (!checkAxis(axis)) return false;
    m_lastError = GtsHal::getHomeStatus(axis, &status);
    return m_lastError == 0;
}

bool FeedbackMgr::executeStandardHome(short axis, const TStandardHomePrm& prm) 
{
    if (!checkAxis(axis)) {
        emit errorOccurred(axis, -1, QStringLiteral("轴号无效: %1").arg(axis));
        return false;
    }
    m_lastError = GtsHal::executeStandardHome(axis, prm);
    if (m_lastError != 0) {
        emit errorOccurred(axis, m_lastError, QStringLiteral("executeStandardHome: ") + lastErrorString());
        return false;
    }
    return true;
}

bool FeedbackMgr::getStandardHomeParams(short axis, TStandardHomePrm& prm) const 
{
    if (!checkAxis(axis)) return false;
    m_lastError = GtsHal::getStandardHomePrm(axis, &prm);
    return m_lastError == 0;
}

bool FeedbackMgr::getStandardHomeStatus(short axis, TStandardHomeStatus& status) const 
{
    if (!checkAxis(axis)) return false;
    m_lastError = GtsHal::getStandardHomeStatus(axis, &status);
    return m_lastError == 0;
}

// ================================================================
// 4. 便捷方法
// ================================================================
bool FeedbackMgr::homeAxis(short axis, double vel, double acc, long homeOffset) 
{
    if (!checkAxis(axis)) {
        emit errorOccurred(axis, -1, QStringLiteral("轴号无效: %1").arg(axis));
        return false;
    }

    // 初始化回零模块
    GtsHal::homeInit();

    // 执行简易回零
    m_lastError = GtsHal::home(axis, 0, vel, acc, homeOffset);
    if (m_lastError != 0) {
        emit errorOccurred(axis, m_lastError, QStringLiteral("home: ") + lastErrorString());
        return false;
    }

    return true;
}

QString FeedbackMgr::lastErrorString() const 
{
    return GtsErrorToString(m_lastError);
}
