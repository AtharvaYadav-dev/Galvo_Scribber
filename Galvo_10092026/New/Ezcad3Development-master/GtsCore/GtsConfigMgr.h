#ifndef CONFIGMGR_H
#define CONFIGMGR_H

#include <QObject>
#include <QString>
#include <QMap>
#include <QColor>

#include "ControllerData.h"
#include "GtsHal.h"

// ============================================================
// ConfigMgr — 配置管理器
// 职责:管理所有高级配置功能
// ============================================================

class GtsMgr;
class AxisMgr;
struct AxisConfig;

class ConfigMgr : public QObject 
{
    Q_OBJECT

private:
    mutable short m_lastError = 0;
    QMap<int, QString> m_customDIDesc;
    QMap<int, QString> m_customDODesc;
    GtsMgr* m_gtsMgr = nullptr;
    AxisMgr* m_axisMgr = nullptr;
    AxisConfig* m_axisCfg = nullptr;

public:
    // 注入gtsMgr共享数据(gtsMgr构造时调用一次)
    void injectDependencies(AxisConfig* cfg, GtsMgr* totalMgr, AxisMgr* axisMgr);
    // JSON 文件路径
    QString axisConfigPath() const;
    // 从 JSON 文件加载轴配置
    bool loadAxisConfig(const QString& filePath = QString());
    // 保存轴配置到 JSON 文件
    bool saveAxisConfig(const QString& filePath = QString());
    // 从板卡读取所有轴配置到 m_axisCfg
    void readAllAxisConfigFromBoard();
    // 将内存所有轴配置应用到板卡
    void applyAllAxisConfigToBoard();
    // 加载cfg配置然后写入,更新内存和本地json
    bool loadConfigFile(const QString& filePath);
    // 设置回零参数
    void setHomeConfig(short axis, HomeMode mode, double vel, double acc, double range, double offset);


    //  IO 描述配置
    QString ioDescriptionPath() const;
    void loadIODescriptions();
    void saveIODescriptions() const;

    const QMap<int, QString>& customDIDescriptions() const { return m_customDIDesc; }
    const QMap<int, QString>& customDODescriptions() const { return m_customDODesc; }
    void setIODescription(int row, const QString& desc, bool isDI);
    QString getDIDescription(int row) const;
    QString getDODescription(int row) const;

    // 控制模式
    void setControlMode(short axis, ControlMode mode);
    ControlMode controlMode(short axis) const;

    // 轴名称
    void setAxisName(short axis, AxisName name);
    AxisName axisName(short axis) const;

    // 软件脉冲系数 (pulse/mm)
    void setSoftPulseScale(short axis, long alpha, long beta);
    long softPulseAlpha(short axis) const;
    long softPulseBeta(short axis) const;

    // profile 当量
    void setProfileScale(short axis, long alpha, long beta);
    long profileScaleAlpha(short axis) const;
    long profileScaleBeta(short axis) const;

    // encoder 当量
    void setEncoderScale(short axis, long alpha, long beta);
    long encoderScaleAlpha(short axis) const;
    long encoderScaleBeta(short axis) const;

    // DAC
    void readDacConfig();
    void setDacBias(short axis, short bias);
    void setDacLimit(short axis, short limit);
    short dacBias(short axis) const;
    short dacLimit(short axis) const;

    // 跟随误差
    void readFollowErrorLimit();
    void setFollowErrorLimit(short axis, long error);
    long followErrorLimit(short axis) const;

    // 停止减速度
    void readStopDecel();
    void setStopDecel(short axis, double smoothDec, double abruptDec);
    double smoothStopDec(short axis) const;
    double estopDec(short axis) const;

    // 回零参数
    void setHomeMode(short axis, HomeMode mode);
    void setHomeVel(short axis, double vel);
    void setHomeAcc(short axis, double acc);
    void setHomeRange(short axis, double range);
    void setHomeOffset(short axis, double offset);
    HomeMode  homeModeValue(short axis) const;
    double    homeVel(short axis) const;
    double    homeAcc(short axis) const;
    double    homeRange(short axis) const;
    double    homeOffset(short axis) const;

    // 轴限位
    void setPosLimit(short axis, double limit);
    void setNegLimit(short axis, double limit);
    double posLimit(short axis) const;
    double negLimit(short axis) const;
    
    // 写入板卡
    void flushScaleToBoard(short axis);
    void flushDacToBoard(short axis);
    void flushFollowErrorToBoard(short axis);
    void flushStopDecelToBoard(short axis);
    void flushControlModeToBoard(short axis);


public:
    explicit ConfigMgr(QObject* parent = nullptr);
    ~ConfigMgr();

    // 设置 PID 参数
    bool setPID(short control, short index, const TPid& pid);
    // 获取 PID 参数
    bool getPID(short control, short index, TPid& pid) const;
    // 设置控制滤波器
    bool setControlFilter(short control, short index);
    // 获取控制滤波器索引
    short getControlFilter(short control) const;
    // 设置 Kvff 滤波器
    bool setKvffFilter(short control, short index, short kvffFilterExp, double accMax);
    // 获取 Kvff 滤波器
    bool getKvffFilter(short control, short index, short& kvffFilterExp, double& accMax) const;
    // 设置轴带宽
    bool setAxisBand(short axis, long band, long time);
    // 获取轴带宽
    bool getAxisBand(short axis, long& band, long& time) const;
    // 设置控制配置扩展
    bool setControlConfigEx(short control, const TControlConfigEx& cfg);
    // 获取控制配置扩展
    bool getControlConfigEx(short control, TControlConfigEx& cfg) const;
    // 设置控制叠加
    bool setControlSuperimposed(short control, short superimposedType, short superimposedIndex);
    // 获取控制叠加
    bool getControlSuperimposed(short control, short& type, short& index) const;
    // 设置背隙补偿
    bool setBacklash(short axis, long compValue, double compChangeValue, long compDir);
    // 获取背隙补偿
    bool getBacklash(short axis, long& compValue, double& compChangeValue, long& compDir) const;
    // 设置丝杠补偿表
    bool setLeadScrewComp(short axis, short n, long startPos, long lenPos, long* pCompPos, long* pCompNeg);
    // 使能丝杠补偿
    bool enableLeadScrewComp(short axis, short mode);
    // 获取丝杠补偿插值
    bool getLeadScrewCompValue(short axis, short dir, long pos, long& compValue) const;
    // 设置交叉丝杠补偿
    bool setLeadScrewCrossComp(short axis, short n, long startPos, long lenPos, long* pCompPos, long* pCompNeg, short link);
    // 使能交叉丝杠补偿
    bool enableLeadScrewCrossComp(short axis, short mode);
    // 设置丝杠链接
    bool setLeadScrewLink(short axis, short link);
    // 获取丝杠链接
    short getLeadScrewLink(short axis) const;
    // 设置 2D 补偿表
    bool setCompensate2DTable(short idx, const TCompensate2DTable& tbl, long* pData, short externComp = 0);
    // 获取 2D 补偿表
    bool getCompensate2DTable(short idx, TCompensate2DTable& tbl) const;
    // 设置 2D 补偿
    bool setCompensate2D(short axis, const TCompensate2D& comp);
    // 获取 2D 补偿
    bool getCompensate2D(short axis, TCompensate2D& comp) const;
    // 获取 2D 补偿值
    double getCompensate2DValue(short axis) const;
    // 获取综合补偿值
    bool getCompensate(short axis, double& pitchError, double& crossError, double& backlashError, double& encPos, double& prfPos) const;
    // 设置比较端口
    bool setComparePort(short channel, short hsio0, short hsio1);
    // 配置比较脉冲
    bool comparePulse(short level, short outputType, short time);
    // 停止比较
    bool compareStop();
    // 获取比较状态
    bool compareStatus(short& status, long& count) const;
    // 写入比较数据
    bool compareData(short encoder, short source, short pulseType, short startLevel, short time, long* pBuf1, short count1, long* pBuf2, short count2);
    // 设置线性比较
    bool compareLinear(short encoder, short channel, long startPos, long repeatTimes, long interval, short time, short source);
    // 设置连续脉冲模式
    bool compareContinuePulseMode(short mode, short count, short standTime);
    // 设置 2D 比较模式
    bool compare2DSetMode(short chn, short mode);
    // 配置 2D 比较脉冲
    bool compare2DPulse(short chn, short level, short outputType, short time);
    // 停止 2D 比较
    bool compare2DStop(short chn);
    // 清除 2D 比较
    bool compare2DClear(short chn);
    // 获取 2D 比较状态
    bool compare2DStatus(short chn, short& status, long& count, short& fifo, short& fifoCount) const;
    // 设置 2D 比较参数
    bool compare2DSetParams(short chn, const T2DComparePrm& prm);
    // 写入 2D 比较数据
    bool compare2DData(short chn, short count, const T2DCompareData* pBuf, short fifo);
    // 启动 2D 比较
    bool compare2DStart(short chn);
    // 清除 2D 比较数据
    bool compare2DClearData(short chn);
    // 设置 2D 比较预输出时间
    bool compare2DSetPreOutTime(short chn, double preOutputTime);
    // 设置 PosCompare 模式
    bool setPosCompareMode(short index, const TPosCompareMode& mode);
    // 获取 PosCompare 模式
    bool getPosCompareMode(short index, TPosCompareMode& mode) const;
    // 启动 PosCompare
    bool posCompareStart(short index);
    // 停止 PosCompare
    bool posCompareStop(short index);
    // 清除 PosCompare
    bool posCompareClear(short index);
    // 获取 PosCompare 状态
    bool posCompareStatus(short index, TPosCompareStatus& status) const;
    // 写入 PosCompare 数据
    bool posCompareData(short index, const TPosCompareData& data);
    // 设置 PosCompare 线性模式
    bool posCompareSetLinear(short index, const TPosCompareLinear& linear);
    // 设置 PosCompare PSO 参数
    bool posCompareSetPsoParams(short index, const TPosComparePsoPrm& prm);
    // 设置 PosCompare 连续模式
    bool posCompareSetContinueMode(short index, const TPosCompareContinueMode& mode);
    // 使能龙门
    bool enableGantry(short master, short slave, double masterKp, double slaveKp);
    // 禁止龙门
    bool disableGantry();
    // 设置龙门误差极限
    bool setGantryErrorLimit(long errLmt);
    // 获取龙门误差极限
    long getGantryErrorLimit() const;
    // 清零龙门位置
    bool zeroGantryPos(short master, short slave);
    // 设置龙门模式
    bool setGantryMode(short group, short master, short slave, short mode, long syncErrorLimit = 1000);
    // 获取龙门模式
    bool getGantryMode(short group, short& master, short& slave, short& mode, long& syncErrorLimit) const;
    // 设置龙门 PID
    bool setGantryPID(short group, const TPid& gantryPid, const TPid& yawPid);
    // 获取龙门 PID
    bool getGantryPID(short group, TPid& gantryPid, TPid& yawPid) const;
    // 龙门轴使能
    bool gantryAxisOn(short group);
    // 龙门轴禁止
    bool gantryAxisOff(short group);
    // 初始化手轮
    bool handwheelInit();
    // 设置手轮停止减速度
    bool setHandwheelStopDecel(short slave, double decSmooth, double decAbrupt);
    // 启动手轮
    bool startHandwheel(short slave, short master, short masterEven, short slaveEven, short intervalTime, double acc, double dec, double vel, short stopWaitTime);
    // 停止手轮
    bool endHandwheel(short slave);
    // 设置触发参数
    bool setTrigger(short i, const TTrigger& trigger);
    // 获取触发参数
    bool getTrigger(short i, TTrigger& trigger) const;
    // 获取触发状态
    bool getTriggerStatus(short i, TTriggerStatus& status) const;
    // 获取触发状态（扩展版）
    bool getTriggerStatusEx(short i, TTriggerStatusEx& statusEx) const;
    // 清除触发状态
    bool clearTriggerStatus(short i);
    // 获取触发锁存值
    bool getTriggerLatchValue(short i, long count, long* pValue, long* pCount, TLatchValueInfo* pInfo) const;
    // 设置正交坐标变换
    bool setTransformOrthogonal(short index, const TTransformOrthogonal& data);
    // 获取正交坐标变换
    bool getTransformOrthogonal(short index, TTransformOrthogonal& data) const;
    // 获取正交变换位置
    bool getTransformOrthogonalPosition(short index, double& x, double& y) const;
    // 设置垂直度坐标变换
    bool setTransformPerpendicularity(short index, const TTransformPerpendicularity& data);
    // 获取垂直度坐标变换
    bool getTransformPerpendicularity(short index, TTransformPerpendicularity& data) const;
    // 获取垂直度变换位置
    bool getTransformPerpendicularityPosition(short index, double& x, double& y, double& z) const;
    // 设置 Smart Cutter 参数
    bool setSmartCutterParams(short index, const TSmartCutterPrm& prm);
    // 获取 Smart Cutter 参数
    bool getSmartCutterParams(short index, TSmartCutterPrm& prm) const;
    // 开启 Smart Cutter
    bool smartCutterOn(short index);
    // 关闭 Smart Cutter
    bool smartCutterOff(short index);
    // 获取 Smart Cutter 信息
    bool getSmartCutterInfo(short index, TSmartCutterInfo& info) const;
    // 设置 Smart Cutter 值
    bool setSmartCutterValue(short index, double radiusValue, double angleValue);
    // 启动 Smart Cutter
    bool smartCutterStart(short index);
    // 自动对焦
    bool autoFocus(unsigned short mode, double kp, short reverse, short channel);
    // 设置自动对焦参考电压
    bool setAutoFocusRefVol(double refVol, double maxVol, double minVol, short channel);
    // 获取自动对焦状态
    bool getAutoFocusStatus(unsigned short& status) const;
    // 配置自动对焦 ADC 通道
    bool configAutoFocus(short chnAdc, short channel);
    // 设置自动对焦辅助参数
    bool setAutoFocusAuxParams(double kf, double kd, double limitKd, short channel);
    // 设置自动对焦死区电压
    bool setAutoFocusDeadVoltage(double voltage, short channel);
    // 设置信号时间滤波
    bool setSignalTimeFilter(short type, short index, double filterWidth);
    // 获取信号时间滤波
    double getSignalTimeFilter(short type, short index) const;
    // 清除信号检测
    bool clearSignalDetect(short index);
    // 设置信号检测
    bool setSignalDetect(short index, short enable, const TSignalDetect& prm);
    // 获取信号检测
    bool getSignalDetect(short index, short& enable, TSignalDetect& prm) const;
    // 获取信号检测状态
    bool getSignalDetectStatus(short index, TSignalDetectStatus& status) const;
    // 设置 Long 变量
    bool setLongVar(short index, long value);
    // 获取 Long 变量
    long getLongVar(short index) const;
    // 设置 Double 变量
    bool setDoubleVar(short index, double value);
    // 获取 Double 变量
    double getDoubleVar(short index) const;
    // 设置 Flag 变量
    bool setFlagVar(short index, short mode, short value);
    // 获取 Flag 变量
    bool getFlagVar(short index, short& mode, short& value) const;
    // 编译脚本
    bool compile(const QString& fileName, TCompileInfo& wrongInfo);
    // 下载脚本到板卡
    bool download(const QString& fileName);
    // 获取函数 ID
    bool getFunctionId(const QString& funName, short& funId);
    // 绑定线程
    bool bind(short thread, short funId, short page);
    // 启动线程
    bool runThread(short thread);
    // 停止线程
    bool stopThread(short thread);
    // 暂停线程
    bool pauseThread(short thread);
    // 获取线程状态
    bool getThreadStatus(short thread, TThreadSts& sts) const;
    // 获取变量 ID
    bool getVarId(const QString& funName, const QString& varName, TVarInfo& varInfo) const;
    // 设置变量值（通过 VarInfo）
    bool setVarValue(short page, const TVarInfo& varInfo, double* pValue, short count = 1);
    // 获取变量值（通过 VarInfo）
    bool getVarValue(short page, const TVarInfo& varInfo, double* pValue, short count = 1) const;
    // 设置摇杆轴映射
    bool setJoystickMapAxis(short idx, short* axis);
    // 获取摇杆轴映射
    bool getJoystickMapAxis(short idx, short* pAxis) const;
    // 使能摇杆
    bool joystickEnable(short idx, short enable);
    // 设置摇杆串口参数
    bool setJoystickSerialPortParams(short idx, const TSericalPortPrm& prm);
    // 获取摇杆串口参数
    bool getJoystickSerialPortParams(short idx, TSericalPortPrm& prm) const;
    // 设置摇杆检测使能
    bool joystickCheckEnable(short idx, short checkEnable);
    // 获取摇杆状态
    long getJoystickStatus(short idx) const;
    // 获取摇杆值
    long getJoystickValue(short idx) const;
    // 设置摇杆运动参数
    bool setJoystickMotionParams(short idx, const TJoystickMoitonPrm& prm);
    // 获取摇杆运动参数
    bool getJoystickMotionParams(short idx, TJoystickMoitonPrm& prm) const;
    // 设置摇杆运动速度
    bool setJoystickMotionVel(short idx, const TJoystickMoitonVel& vel);
    // 获取摇杆运动速度
    bool getJoystickMotionVel(short idx, TJoystickMoitonVel& vel) const;
    // 复位摇杆
    bool joystickReset(short idx);
    // 设置运动平滑
    bool setMotionSmooth(short axis, const TMotionSmooth& smooth);
    // 获取运动平滑
    bool getMotionSmooth(short axis, TMotionSmooth& smooth) const;
    // 设置轴叠加
    bool setAxisAddition(short axis, short dataType, short additionIndex, short additionType);
    // 获取轴叠加
    bool getAxisAddition(short axis, short dataType, short& additionIndex, short& additionType) const;
    // 设置轴输入整形
    bool setAxisInputShaping(short axis, short enable, short count, double k);
    // 设置 McOverride
    bool setMcOverride(short axis, short mode, double override, double smoothTime);
    // 获取 McOverride
    bool getMcOverride(short axis, short mode, double& overrideTarget, double& smoothTime, double& overrideVal) const;
    // 设置步进输出电平
    bool setStepOutLevel(short axis, short type, short reverse);
    // 获取步进输出电平
    bool getStepOutLevel(short axis, short type, short& reverse) const;
    // 步进方向模式
    bool stepDir(short step);
    // 步进脉冲模式
    bool stepPulse(short step);
    // 步进正交模式
    bool stepOrthogonal(short step);
    // 获取机器/工件坐标
    bool getMachineWorkPos(short crd, short mode, double& machinePos, double& workPos) const;
    // 检查插补线段时间
    bool checkCrdLineTime(short crd, double x, double y, double z, double& velMax, double& acc, double& velEnd, double& time, long& errorCode) const;
    // 轴号是否有效
    bool isValidAxis(short axis) const;
    // 获取最后一次错误码
    short lastError() const { return m_lastError; }
    // 获取最后一次错误描述
    QString lastErrorString() const;

signals:
    // 发生错误
    void errorOccurred(short channel, short errorCode, const QString& errorMsg);
    // 日志消息
    void logMessage(const QString& message, QColor color = Qt::black, const QString& source = "Gts");
    // 配置文件改变
    void configChanged();


};

#endif // CONFIGMGR_H
