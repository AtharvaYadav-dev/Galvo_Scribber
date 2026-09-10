#include "GtsIOMgr.h"
#include <QMessageBox>

// ============================================================
// 构造/析构
// ============================================================
IOMgr::IOMgr(QObject* parent)
    : QObject(parent)
{
}

IOMgr::~IOMgr() 
{
}

void IOMgr::getPLimitDI(std::vector<int>& limitDI)
{
    long value = 0;
    m_lastError = GtsHal::getDi(MC_LIMIT_POSITIVE, &value);
    limitDI.clear();
    limitDI.resize(8);
    for (int i = 0; i < 8; ++i) {
        limitDI[i] = (value >> i) & 1;
    }
}

void IOMgr::getNLimitDI(std::vector<int>& limitDI)
{
    long value = 0;
    m_lastError = GtsHal::getDi(MC_LIMIT_NEGATIVE, &value);
    limitDI.clear();
    limitDI.resize(8);
    for (int i = 0; i < 8; ++i) {
        limitDI[i] = (value >> i) & 1;
    }
}

void IOMgr::getDriverAlarmDI(std::vector<int>& driverAlarm)
{
    long value = 0;
    m_lastError = GtsHal::getDi(MC_ALARM, &value);
    driverAlarm.clear();
    driverAlarm.resize(8);
    for (int i = 0; i < 8; ++i) {
        driverAlarm[i] = (value >> i) & 1;
    }

    //QString split;
    //for (int i = 0; i < 8; ++i) {
    //    split += QStringLiteral("位%1=%2  ").arg(i).arg(driverAlarm[i]);
    //}
    //QMessageBox::information(nullptr,
    //    QStringLiteral("getPLimitDI 排查"),
    //    QStringLiteral(
    //        "原始 long = 0x%1 (%2)\n"
    //        "拆分: %3")
    //    .arg((unsigned long)value, 8, 16, QChar('0'))
    //    .arg(value)
    //    .arg(split));
}

void IOMgr::getHomeDI(std::vector<int>& home)
{
    long value = 0;
    m_lastError = GtsHal::getDi(MC_HOME, &value);
    home.clear();
    home.resize(8);
    for (int i = 0; i < 8; ++i) {
        home[i] = (value >> i) & 1;
    }
}

void IOMgr::getGPI(std::vector<int>& gpi)
{
    long value = 0;
    m_lastError = GtsHal::getDi(MC_GPI, &value);
    gpi.clear();
    gpi.resize(16);
    for (int i = 0; i < 16; ++i) {
        gpi[i] = (value >> i) & 1;
    }
}

void IOMgr::getArriveDI(std::vector<int>& arrive)
{
    long value = 0;
    m_lastError = GtsHal::getDi(MC_ARRIVE, &value);
    arrive.clear();
    arrive.resize(8);
    for (int i = 0; i < 8; ++i) {
        arrive[i] = (value >> i) & 1;
    }
}

void IOMgr::getHandwheelDI(std::vector<int>& handwheel)
{
    long value = 0;
    m_lastError = GtsHal::getDi(MC_MPG, &value);
    handwheel.clear();
    handwheel.resize(8);
    for (int i = 0; i < 8; ++i) {
        handwheel[i] = (value >> i) & 1;
    }
}

void IOMgr::getMotorEnableDO(std::vector<int>& motorEnable)
{
    long value = 0;
    m_lastError = GtsHal::getDo(MC_ENABLE, &value);
    motorEnable.clear();
    motorEnable.resize(8);
    for (int i = 0; i < 8; ++i) {
        motorEnable[i] = (value >> i) & 1;
    }
}

void IOMgr::getClearAlarmDO(std::vector<int>& clearAlarm)
{
    long value = 0;
    m_lastError = GtsHal::getDo(MC_CLEAR, &value);
    clearAlarm.clear();
    clearAlarm.resize(8);
    for (int i = 0; i < 8; ++i) {
        clearAlarm[i] = (value >> i) & 1;
    }
}

void IOMgr::getGPO(std::vector<int>& gpo)
{
    long value = 0;
    m_lastError = GtsHal::getDo(MC_GPO, &value);
    gpo.clear();
    gpo.resize(16);
    for (int i = 0; i < 16; ++i) {
        gpo[i] = (value >> i) & 1;
    }
}

void IOMgr::setMotorEnableDO(const std::vector<int>& motorEnable)
{
    long value = 0;
    for (int i = 0; i < (int)motorEnable.size() && i < 8; ++i) {
        if (motorEnable[i]) value |= (1L << i);
    }
    m_lastError = GtsHal::setDo(MC_ENABLE, value);
    if (m_lastError != 0) {
        emit errorOccurred(m_lastError, QStringLiteral("setDo: ") + lastErrorString());
    }
}

void IOMgr::setClearAlarmDO(const std::vector<int>& clearAlarm)
{
    long value = 0;
    for (int i = 0; i < (int)clearAlarm.size() && i < 8; ++i) {
        if (clearAlarm[i]) value |= (1L << i);
    }
    m_lastError = GtsHal::setDo(MC_CLEAR, value);
    if (m_lastError != 0) {
        emit errorOccurred(m_lastError, QStringLiteral("setDo: ") + lastErrorString());
    }
}

void IOMgr::setGPO(const std::vector<int>& gpo)
{
    long value = 0;
    for (int i = 0; i < (int)gpo.size() && i < 16; ++i) {
        if (gpo[i]) value |= (1L << i);
    }
    m_lastError = GtsHal::setDo(MC_GPO, value);
    if (m_lastError != 0) {
        emit errorOccurred(m_lastError, QStringLiteral("setDo: ") + lastErrorString());
    }
}



// ================================================================
// 1. 数字输出 (DO)
// ================================================================
bool IOMgr::setOutput(short doType, long value) 
{
    m_lastError = GtsHal::setDo(doType, value);
    if (m_lastError != 0) {
        emit errorOccurred(m_lastError, QStringLiteral("setDo: ") + lastErrorString());
        return false;
    }
    return true;
}

bool IOMgr::setOutputBit(short doType, short doIndex, short value) 
{
    m_lastError = GtsHal::setDoBit(doType, doIndex, value);
    if (m_lastError != 0) {
        emit errorOccurred(m_lastError, QStringLiteral("setDoBit: ") + lastErrorString());
        return false;
    }
    return true;
}

long IOMgr::getOutput(short doType) const 
{
    long value = 0;
    m_lastError = GtsHal::getDo(doType, &value);
    return value;
}

bool IOMgr::setOutputBitReverse(short doType, short doIndex, short value, short reverseTime) 
{
    m_lastError = GtsHal::setDoBitReverse(doType, doIndex, value, reverseTime);
    if (m_lastError != 0) {
        emit errorOccurred(m_lastError, QStringLiteral("setDoBitReverse: ") + lastErrorString());
        return false;
    }
    return true;
}

bool IOMgr::setOutputMask(short doType, unsigned short doMask, long value) 
{
    m_lastError = GtsHal::setDoMask(doType, doMask, value);
    if (m_lastError != 0) {
        emit errorOccurred(m_lastError, QStringLiteral("setDoMask: ") + lastErrorString());
        return false;
    }
    return true;
}

bool IOMgr::enableOutputBitPulse(short doType, short doIndex,
    unsigned short highLevelTime, unsigned short lowLevelTime,
    long pulseNum, short firstLevel) 
{
    m_lastError = GtsHal::enableDoBitPulse(doType, doIndex, highLevelTime, lowLevelTime,
        pulseNum, firstLevel);
    if (m_lastError != 0) {
        emit errorOccurred(m_lastError, QStringLiteral("enableDoBitPulse: ") + lastErrorString());
        return false;
    }
    return true;
}

bool IOMgr::disableOutputBitPulse(short doType, short doIndex) 
{
    m_lastError = GtsHal::disableDoBitPulse(doType, doIndex);
    if (m_lastError != 0) {
        emit errorOccurred(m_lastError, QStringLiteral("disableDoBitPulse: ") + lastErrorString());
        return false;
    }
    return true;
}

// ================================================================
// 2. 数字输入 (DI)
// ================================================================
long IOMgr::getInput(short diType) const 
{
    long value = 0;
    m_lastError = GtsHal::getDi(diType, &value);
    return value;
}

long IOMgr::getInputRaw(short diType) const 
{
    long value = 0;
    m_lastError = GtsHal::getDiRaw(diType, &value);
    return value;
}

bool IOMgr::getInputReverseCount(short diType, short diIndex,
    unsigned long* pReverseCount, short count) const 
{
    m_lastError = GtsHal::getDiReverseCount(diType, diIndex, pReverseCount, count);
    return m_lastError == 0;
}

bool IOMgr::setInputReverseCount(short diType, short diIndex,
    unsigned long* pReverseCount, short count) 
{
    m_lastError = GtsHal::setDiReverseCount(diType, diIndex, pReverseCount, count);
    if (m_lastError != 0) {
        emit errorOccurred(m_lastError, QStringLiteral("setDiReverseCount: ") + lastErrorString());
        return false;
    }
    return true;
}

// ================================================================
// 3. 高速 IO (HSIO)
// ================================================================
bool IOMgr::setHSIOOpt(unsigned short value, short channel) 
{
    m_lastError = GtsHal::setHSIOOpt(value, channel);
    if (m_lastError != 0) {
        emit errorOccurred(m_lastError, QStringLiteral("setHSIOOpt: ") + lastErrorString());
        return false;
    }
    return true;
}

unsigned short IOMgr::getHSIOOpt(short channel) const 
{
    unsigned short value = 0;
    GtsHal::getHSIOOpt(&value, channel);
    return value;
}

bool IOMgr::setGpiSense(unsigned short sense) 
{
    m_lastError = GtsHal::gpiSns(sense);
    if (m_lastError != 0) {
        emit errorOccurred(m_lastError, QStringLiteral("gpiSns: ") + lastErrorString());
        return false;
    }
    return true;
}

// ================================================================
// 4. DAC 输出
// ================================================================
bool IOMgr::setDAC(short dac, short* pValue, short count) 
{
    m_lastError = GtsHal::setDac(dac, pValue, count);
    if (m_lastError != 0) {
        emit errorOccurred(m_lastError, QStringLiteral("setDac: ") + lastErrorString());
        return false;
    }
    return true;
}

bool IOMgr::getDAC(short dac, short* pValue, short count) const 
{
    m_lastError = GtsHal::getDac(dac, pValue, count);
    return m_lastError == 0;
}

bool IOMgr::setMotorBias(short dac, short bias) 
{
    m_lastError = GtsHal::setMtrBias(dac, bias);
    if (m_lastError != 0) {
        emit errorOccurred(m_lastError, QStringLiteral("setMtrBias: ") + lastErrorString());
        return false;
    }
    return true;
}

short IOMgr::getMotorBias(short dac) const 
{
    short bias = 0;
    GtsHal::getMtrBias(dac, &bias);
    return bias;
}

bool IOMgr::setMotorLimit(short dac, short limit) 
{
    m_lastError = GtsHal::setMtrLmt(dac, limit);
    if (m_lastError != 0) {
        emit errorOccurred(m_lastError, QStringLiteral("setMtrLmt: ") + lastErrorString());
        return false;
    }
    return true;
}

short IOMgr::getMotorLimit(short dac) const 
{
    short limit = 0;
    GtsHal::getMtrLmt(dac, &limit);
    return limit;
}

// ================================================================
// 5. ADC 输入
// ================================================================
bool IOMgr::getADC(short adc, double* pValue, short count) const 
{
    m_lastError = GtsHal::getAdc(adc, pValue, count);
    return m_lastError == 0;
}

bool IOMgr::getADCValue(short adc, short* pValue, short count) const 
{
    m_lastError = GtsHal::getAdcValue(adc, pValue, count);
    return m_lastError == 0;
}

bool IOMgr::setADCConfig(short adc, const TAdcConfig& cfg) 
{
    m_lastError = GtsHal::setAdcConfig(adc, cfg);
    if (m_lastError != 0) {
        emit errorOccurred(m_lastError, QStringLiteral("setAdcConfig: ") + lastErrorString());
        return false;
    }
    return true;
}

bool IOMgr::getADCConfig(short adc, TAdcConfig& cfg) const 
{
    m_lastError = GtsHal::getAdcConfig(adc, &cfg);
    return m_lastError == 0;
}

bool IOMgr::setADCFilter(short adc, short filterTime) 
{
    m_lastError = GtsHal::setAdcFilter(adc, filterTime);
    if (m_lastError != 0) {
        emit errorOccurred(m_lastError, QStringLiteral("setAdcFilter: ") + lastErrorString());
        return false;
    }
    return true;
}

bool IOMgr::setADCFilterParam(short adc, double k) 
{
    m_lastError = GtsHal::setAdcFilterPrm(adc, k);
    if (m_lastError != 0) {
        emit errorOccurred(m_lastError, QStringLiteral("setAdcFilterPrm: ") + lastErrorString());
        return false;
    }
    return true;
}

double IOMgr::getADCFilterParam(short adc) const 
{
    double k = 0.0;
    GtsHal::getAdcFilterPrm(adc, &k);
    return k;
}

// ================================================================
// 6. 扩展模块
// ================================================================
bool IOMgr::openExtModule(const char* pDllName) 
{
    m_lastError = GtsHal::openExtMdl(const_cast<char*>(pDllName));
    if (m_lastError != 0) {
        emit errorOccurred(m_lastError, QStringLiteral("openExtMdl: ") + lastErrorString());
        return false;
    }
    return true;
}

bool IOMgr::closeExtModule() 
{
    m_lastError = GtsHal::closeExtMdl();
    if (m_lastError != 0) {
        emit errorOccurred(m_lastError, QStringLiteral("closeExtMdl: ") + lastErrorString());
        return false;
    }
    return true;
}

bool IOMgr::switchExtModuleCardNo(short card) 
{
    m_lastError = GtsHal::switchtoCardNoExtMdl(card);
    if (m_lastError != 0) {
        emit errorOccurred(m_lastError, QStringLiteral("switchtoCardNoExtMdl: ") + lastErrorString());
        return false;
    }
    return true;
}

bool IOMgr::resetExtModule() 
{
    m_lastError = GtsHal::resetExtMdl();
    if (m_lastError != 0) {
        emit errorOccurred(m_lastError, QStringLiteral("resetExtMdl: ") + lastErrorString());
        return false;
    }
    return true;
}

bool IOMgr::loadExtConfig(const QString& filePath) 
{
    m_lastError = GtsHal::loadExtConfig(filePath.toLocal8Bit().constData());
    if (m_lastError != 0) {
        emit errorOccurred(m_lastError, QStringLiteral("loadExtConfig: ") + lastErrorString());
        return false;
    }
    return true;
}

bool IOMgr::setExtOutput(short mdl, unsigned short value) 
{
    m_lastError = GtsHal::setExtIoValue(mdl, value);
    if (m_lastError != 0) {
        emit errorOccurred(m_lastError, QStringLiteral("setExtIoValue: ") + lastErrorString());
        return false;
    }
    return true;
}

unsigned short IOMgr::getExtOutput(short mdl) const 
{
    unsigned short value = 0;
    GtsHal::getExtIoValue(mdl, &value);
    return value;
}

bool IOMgr::setExtOutputBit(short mdl, short index, unsigned short value) 
{
    m_lastError = GtsHal::setExtIoBit(mdl, index, value);
    if (m_lastError != 0) {
        emit errorOccurred(m_lastError, QStringLiteral("setExtIoBit: ") + lastErrorString());
        return false;
    }
    return true;
}

unsigned short IOMgr::getExtOutputBit(short mdl, short index) const 
{
    unsigned short value = 0;
    GtsHal::getExtIoBit(mdl, index, &value);
    return value;
}

unsigned short IOMgr::getExtADValue(short mdl, short chn) const 
{
    unsigned short value = 0;
    GtsHal::getExtAdValue(mdl, chn, &value);
    return value;
}

double IOMgr::getExtADVoltage(short mdl, short chn) const 
{
    double value = 0.0;
    GtsHal::getExtAdVoltage(mdl, chn, &value);
    return value;
}

bool IOMgr::setExtDAValue(short mdl, short chn, unsigned short value) 
{
    m_lastError = GtsHal::setExtDaValue(mdl, chn, value);
    if (m_lastError != 0) {
        emit errorOccurred(m_lastError, QStringLiteral("setExtDaValue: ") + lastErrorString());
        return false;
    }
    return true;
}

bool IOMgr::setExtDAVoltage(short mdl, short chn, double value) 
{
    m_lastError = GtsHal::setExtDaVoltage(mdl, chn, value);
    if (m_lastError != 0) {
        emit errorOccurred(m_lastError, QStringLiteral("setExtDaVoltage: ") + lastErrorString());
        return false;
    }
    return true;
}

short IOMgr::getExtModuleMode() const 
{
    short mode = 0;
    GtsHal::getExtMdlMode(&mode);
    return mode;
}

bool IOMgr::setExtModuleMode(short mode) 
{
    m_lastError = GtsHal::setExtMdlMode(mode);
    if (m_lastError != 0) {
        emit errorOccurred(m_lastError, QStringLiteral("setExtMdlMode: ") + lastErrorString());
        return false;
    }
    return true;
}

bool IOMgr::getExtConfig(short mdl, TExtMdlCfgInfo& info) const 
{
    m_lastError = GtsHal::getConfig(mdl, &info);
    return m_lastError == 0;
}

bool IOMgr::setExtConfig(short mdl, const TExtMdlCfgInfo& info) 
{
    m_lastError = GtsHal::setConfig(mdl, info);
    if (m_lastError != 0) {
        emit errorOccurred(m_lastError, QStringLiteral("setConfig: ") + lastErrorString());
        return false;
    }
    return true;
}

// ================================================================
// 7. 便利方法
// ================================================================
bool IOMgr::setOutputOn(short doType, short doIndex) 
{
    return setOutputBit(doType, doIndex, 1);
}

bool IOMgr::setOutputOff(short doType, short doIndex) 
{
    return setOutputBit(doType, doIndex, 0);
}

bool IOMgr::getInputBit(short diType, short diIndex) const 
{
    long value = getInput(diType);
    return (value & (1L << diIndex)) != 0;
}

IOMgr::IOSnapshot IOMgr::takeSnapshot() const 
{
    IOSnapshot snap;
    snap.input = getInput(MC_GPI);
    snap.output = getOutput(MC_GPO);
    unsigned long clk = 0;
    GtsHal::getClock(&clk, nullptr);
    snap.lastUpdate = clk;
    return snap;
}

QString IOMgr::lastErrorString() const 
{
    return GtsErrorToString(m_lastError);
}
