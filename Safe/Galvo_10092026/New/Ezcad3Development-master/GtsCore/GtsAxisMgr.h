#ifndef AXISMGR_H
#define AXISMGR_H

#include <QObject>
#include <QString>
#include <Vector>
#include <QColor>
#include "GtsHal.h"

#include "ControllerData.h"

class GtsMgr;

class AxisMgr : public QObject {
    Q_OBJECT

private:
    mutable short m_lastError = 0;
    GtsMgr* m_gtsMgr = nullptr;

public:
    explicit AxisMgr(GtsMgr* totalMgr, QObject* parent = nullptr);
    ~AxisMgr();
    void setTotalMgr(GtsMgr* mgr) { m_gtsMgr = mgr; }

    // 获取轴状态
    void getAxisStatusAndMotionInfo(std::vector<SingleAxisInfo>& vecAxis);
    // profile 当量
    short setProfileScale(short axis, long alpha, long beta);
    short getProfileScale(short axis, long& alpha, long& beta);
    // encoder 当量
    short setEncoderScale(short axis, long alpha, long beta);
    short getEncoderScale(short axis, long& alpha, long& beta);

public:
    // 使能单个轴
    bool enable(short axis);
    // 禁止单个轴
    bool disable(short axis);
    // 使能多个轴(通过位掩码)
    bool enableMulti(unsigned long mask);
    // 禁止多个轴(通过位掩码)
    bool disableMulti(unsigned long mask);
    // 使能所有轴
    bool enableAll();
    // 禁止所有轴
    bool disableAll();
    // 查询单个轴是否已使能
    bool isEnabled(short axis) ;
    // 设置/获取轴使能时的延迟时间ms
    bool setOnDelayTime(unsigned short ms);
    unsigned short onDelayTime() ;
    // 停止单个轴
    // @param option 0=平滑  1=紧急停止
    bool stop(short axis, long option = 0);
    // 停止所有轴
    bool stopAll(long option = 0);
    // 停止多个轴(通过位掩码)
    bool stopMulti(long mask, long option = 0);
    // 开启报警
    bool alarmOn(short axis);
    // 关闭报警
    bool alarmOff(short axis);
    // 查询是否有报警
    bool isAlarm(short axis);
    // 开启限位（可指定正/负限位，-1=全部）
    bool limitOn(short axis, short limitType = -1);
    // 关闭限位
    bool limitOff(short axis, short limitType = -1);
    // 设置限位电平极性
    bool setLimitSense(unsigned short sense);
    // 设置软限位
    bool setSoftLimit(short axis, long positive, long negative);
    // 获取软限位
    bool getSoftLimit(short axis, long& positive, long& negative);
    // 获取轴状态(通过位掩码)
    long status(short axis);
    // 清除轴状态
    bool clearStatus(short axis);
    // 清零轴位置
    bool zeroPosition(short axis);
    // 同步多轴位置
    bool syncPosition(long mask);
    // 设置控制模式
    bool setControlMode(short axis, short mode);
    // 设置轴模式
    bool setAxisMode(short axis, short mode);
    // 获取轴模式
    short getAxisMode(short axis) ;
    // 设置跟随误差极限
    bool setFollowErrorLimit(short control, long error);
    // 获取跟随误差极限
    long getFollowErrorLimit(short control) ;
    // 设置跟随误差模式
    bool setFollowErrorMode(short axis, short mode);
    // 获取跟随误差模式
    short getFollowErrorMode(short axis);
    // 设置停止减速参数
    bool setStopDecel(short profile, double smooth, double abrupt);
    // 获取停止减速参数
    bool getStopDecel(short profile, double& smooth, double& abrupt);
    // 设置停止触发 IO
    bool setStopIO(short axis, short stopType, short inputType, short inputIndex);
    // 获取轴编码器位置
    double encoderPosition(short axis);
    // 获取轴编码器速度
    double encoderVelocity(short axis) ;
    // 获取轴编码器加速度
    double encoderAcceleration(short axis) ;
    // 获取轴规划器位置
    double prfPosition(short axis);
    // 获取轴规划器速度
    double prfVelocity(short axis);
    // 获取轴规划器加速度
    double prfAcceleration(short axis);
    // 获取轴跟踪误差
    double trackingError(short axis);
    // 轴号是否有效
    bool isValidAxis(short axis);
    // 获取最后一次错误码
    short lastError() { return m_lastError; }
    // 获取最后一次错误描述
    QString lastErrorString() ;
    // 获取轴状态文本描述
    static QString statusToString(long sts);
    // 设置步进脉冲输出模式 脉冲+方向
    bool setStepPulseDir(short step);
    // CCW/CW（双脉冲）
    bool setStepPulseCCW(short step);     
    // DAC 零漂补偿
    bool setDacBias(short dac, short bias);
    short getDacBias(short dac) const;
    // DAC 输出电压饱和极限
    bool setDacLimit(short dac, short limit);
    short getDacLimit(short dac) const;

signals:
    // 发生错误
    void errorOccurred(short axis, short errorCode, const QString& errorMsg);
    // 日志消息
    void logMessage(const QString& message, QColor color = Qt::black, const QString& source = "Gts");
};

#endif // AXISMGR_H
