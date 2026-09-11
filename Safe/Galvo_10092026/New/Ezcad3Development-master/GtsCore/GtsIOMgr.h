#ifndef IOMGR_H
#define IOMGR_H

#include <QObject>
#include <QString>
#include <QColor>
#include "GtsHal.h"

// ============================================================
// IOMgr — IO 管理器
// 职责：管理数字 IO、DAC/ADC、扩展模块
//   - 数字输出 (DO)
//   - 数字输入 (DI)
//   - 高速 IO (HSIO)
//   - DAC 输出 / ADC 输入
//   - 扩展模块 IO/AD/DA
// ============================================================


class IOMgr : public QObject {
    Q_OBJECT

private:
    mutable short m_lastError = 0;

public:
    explicit IOMgr(QObject* parent = nullptr);
    ~IOMgr();

    // 获取输入状态
    void getPLimitDI(std::vector<int>& limitDI);
    void getNLimitDI(std::vector<int>& limitDI);
    void getDriverAlarmDI(std::vector<int>& driverAlarm);
    void getHomeDI(std::vector<int>& home);
    void getGPI(std::vector<int>& gpi);
    void getArriveDI(std::vector<int>& arrive);
    void getHandwheelDI(std::vector<int>& handwheel);
    // 获取输出状态
    void getMotorEnableDO(std::vector<int>& motorEnable);
    void getClearAlarmDO(std::vector<int>& clearAlarm);
    void getGPO(std::vector<int>& gpo);
    // 设置输出状态
    void setMotorEnableDO(const std::vector<int>& motorEnable);
    void setClearAlarmDO(const std::vector<int>& clearAlarm);
    void setGPO(const std::vector<int>& gpo);


public:
    // 设置整组 DO 值
    bool setOutput(short doType, long value);
    // 设置单个 DO 位
    bool setOutputBit(short doType, short doIndex, short value);
    // 读取整组 DO 当前值
    long getOutput(short doType) const;
    // 设置 DO 位反向脉冲
    bool setOutputBitReverse(short doType, short doIndex, short value, short reverseTime);
    // 按掩码设置 DO
    bool setOutputMask(short doType, unsigned short doMask, long value);
    // 使能 DO 位脉冲输出
    bool enableOutputBitPulse(short doType, short doIndex, unsigned short highLevelTime, unsigned short lowLevelTime, long pulseNum, short firstLevel);
    // 禁止 DO 位脉冲输出
    bool disableOutputBitPulse(short doType, short doIndex);
    // 读取整组 DI 值
    long getInput(short diType) const;
    // 读取 DI 原始值（未滤波）
    long getInputRaw(short diType) const;
    // 获取 DI 反转计数
    bool getInputReverseCount(short diType, short diIndex, unsigned long* pReverseCount, short count = 1) const;
    // 设置 DI 反转计数
    bool setInputReverseCount(short diType, short diIndex, unsigned long* pReverseCount, short count = 1);
    // 设置高速 IO 选项
    bool setHSIOOpt(unsigned short value, short channel = 0);
    // 获取高速 IO 选项
    unsigned short getHSIOOpt(short channel = 0) const;
    // 设置 GPI 电平极性
    bool setGpiSense(unsigned short sense);
    // 设置 DAC 值
    bool setDAC(short dac, short* pValue, short count = 1);
    // 读取 DAC 当前值
    bool getDAC(short dac, short* pValue, short count = 1) const;
    // 设置电机偏置
    bool setMotorBias(short dac, short bias);
    // 获取电机偏置
    short getMotorBias(short dac) const;
    // 设置电机输出限幅
    bool setMotorLimit(short dac, short limit);
    // 获取电机输出限幅
    short getMotorLimit(short dac) const;
    // 读取 ADC 电压值（转换后）
    bool getADC(short adc, double* pValue, short count = 1) const;
    // 读取 ADC 原始值
    bool getADCValue(short adc, short* pValue, short count = 1) const;
    // 设置 ADC 滤波时间
    bool setADCFilter(short adc, short filterTime);
    // 设置 ADC 配置
    bool setADCConfig(short adc, const TAdcConfig& cfg);
    // 获取 ADC 配置
    bool getADCConfig(short adc, TAdcConfig& cfg) const;
    // 设置 ADC 滤波参数
    bool setADCFilterParam(short adc, double k);
    // 获取 ADC 滤波参数
    double getADCFilterParam(short adc) const;
    // 打开扩展模块 DLL
    bool openExtModule(const char* pDllName = nullptr);
    // 关闭扩展模块
    bool closeExtModule();
    // 切换扩展模块卡号
    bool switchExtModuleCardNo(short card);
    // 复位扩展模块
    bool resetExtModule();
    // 加载扩展模块配置
    bool loadExtConfig(const QString& filePath);
    // 设置扩展模块 IO 值
    bool setExtOutput(short mdl, unsigned short value);
    // 获取扩展模块 IO 值
    unsigned short getExtOutput(short mdl) const;
    // 设置扩展模块 IO 位
    bool setExtOutputBit(short mdl, short index, unsigned short value);
    // 获取扩展模块 IO 位
    unsigned short getExtOutputBit(short mdl, short index) const;
    // 获取扩展模块 AD 原始值
    unsigned short getExtADValue(short mdl, short chn) const;
    // 获取扩展模块 AD 电压值
    double getExtADVoltage(short mdl, short chn) const;
    // 设置扩展模块 DA 原始值
    bool setExtDAValue(short mdl, short chn, unsigned short value);
    // 设置扩展模块 DA 电压值
    bool setExtDAVoltage(short mdl, short chn, double value);
    // 获取扩展模块模式
    short getExtModuleMode() const;
    // 设置扩展模块模式
    bool setExtModuleMode(short mode);
    // 获取扩展模块配置
    bool getExtConfig(short mdl, TExtMdlCfgInfo& info) const;
    // 设置扩展模块配置
    bool setExtConfig(short mdl, const TExtMdlCfgInfo& info);
    // 快捷设置单个 DO 为高电平
    bool setOutputOn(short doType, short doIndex);
    // 快捷设置单个 DO 为低电平
    bool setOutputOff(short doType, short doIndex);
    // 快捷读取单个 DI 状态
    bool getInputBit(short diType, short diIndex) const;
    // 读取所有 IO 状态快照(用于界面刷新)
    struct IOSnapshot {
        long input;
        long output;
        unsigned long lastUpdate;
    };
    IOSnapshot takeSnapshot() const;

    // 获取最后一次错误码
    short lastError() const { return m_lastError; }
    // 获取最后一次错误描述
    QString lastErrorString() const;

signals:
    // 输入状态变化 (DI类型, 新值)
    void inputChanged(short diType, long value);
    // 发生错误 (错误码, 描述)
    void errorOccurred( short errorCode, const QString& errorMsg);
    // 日志消息
    void logMessage(const QString& message, QColor color = Qt::black, const QString& source = "Gts");

};

#endif // IOMGR_H
