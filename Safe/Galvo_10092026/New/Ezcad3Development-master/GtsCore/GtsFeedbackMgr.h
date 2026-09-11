#ifndef FEEDBACKMGR_H
#define FEEDBACKMGR_H

#include <QObject>
#include <QString>
#include <QColor>
#include "GtsHal.h"

class GtsMgr;

// ============================================================
// FeedbackMgr — 反馈管理器（编码器 + 捕获 + 回零）
// 职责：
//   - 编码器读写、极性、缩放、响应检查
//   - 位置捕获 (Home/Index/Probe/HSIO)
//   - 回零运动 (标准回零/自定义回零)
// ============================================================

class FeedbackMgr : public QObject 
{
    Q_OBJECT

private:
    GtsMgr* m_gtsMgr = nullptr;
    mutable short m_lastError = 0;

    bool checkEncoder(short encoder) const;
    bool checkAxis(short axis) const;

public:
    explicit FeedbackMgr(GtsMgr* totalMgr, QObject* parent = nullptr);
    ~FeedbackMgr();

    // 设置编码器极性
    bool setEncoderSense(unsigned short sense);
    // 使能编码器
    bool encoderOn(short encoder);
    // 禁止编码器
    bool encoderOff(short encoder);
    // 设置编码器位置
    bool setEncoderPos(short encoder, long encPos);
    // 获取编码器位置
    double encoderPos(short encoder) const;
    // 获取编码器位置（预览值，未更新锁存）
    double encoderPosPreview(short encoder) const;
    // 获取编码器速度
    double encoderVel(short encoder) const;
    // 设置编码器缩放系数
    bool setEncoderScale(short encoder, long alpha, long beta);
    // 获取编码器缩放系数
    bool getEncoderScale(short encoder, long& alpha, long& beta) const;
    // 设置编码器响应检查
    bool setEncoderResponseCheck(short control, short dacThreshold,   double minEncVel, long time);
    // 获取编码器响应检查参数
    bool getEncoderResponseCheck(short control, short& dacThreshold, double& minEncVel, long& time) const;
    // 使能编码器响应检查
    bool enableEncoderResponseCheck(short control);
    // 禁止编码器响应检查
    bool disableEncoderResponseCheck(short control);
    // 设置编码器输出选择
    bool setEncoderOutputSelect(short mode);
    // 获取编码器输出选择
    short getEncoderOutputSelect() const;
    // 设置捕获模式
    bool setCaptureMode(short encoder, short mode);
    // 获取捕获模式
    short getCaptureMode(short encoder) const;
    // 停止捕获
    bool stopCapture(short encoder);
    // 获取捕获状态
    bool getCaptureStatus(short encoder, short& status, long& value) const;
    // 获取捕获状态（扩展版，含双精度值和时钟）
    bool getCaptureStatusEx(short encoder, short& status, long& value, double& doubleVar, unsigned long& captureClock) const;
    // 设置捕获触发沿
    bool setCaptureSense(short encoder, short mode, short sense);
    // 清除捕获状态
    bool clearCaptureStatus(short encoder);
    // 设置重复捕获次数
    bool setCaptureRepeat(short encoder, short count);
    // 获取重复捕获剩余次数
    short getCaptureRepeatStatus(short encoder) const;
    // 获取重复捕获位置序列
    bool getCaptureRepeatPositions(short encoder, long* pValue, short startNum, short count) const;
    // 设置捕获触发的编码器源
    bool setCaptureEncoder(short trigger, short encoder);
    // 获取捕获脉宽
    bool getCaptureWidth(short trigger, short* pWidth) const;
    // 初始化回零模块
    bool homeInit();
    // 简易回零
    bool home(short axis, long pos, double vel, double acc, long offset);
    // 索引回零
    bool homeIndex(short axis, long pos, long offset);
    // 停止回零
    bool homeStop(short axis, long pos, double vel, double acc);
    // 查询回零状态
    unsigned short homeStatus(short axis) const;
    // 标准回零（高级版）
    bool goHome(short axis, const THomePrm& prm);
    // 获取回零参数
    bool getHomeParams(short axis, THomePrm& prm) const;
    // 获取回零状态（结构体版）
    bool getHomeStatus(short axis, THomeStatus& status) const;
    // 执行标准回零流程
    bool executeStandardHome(short axis, const TStandardHomePrm& prm);
    // 获取标准回零参数
    bool getStandardHomeParams(short axis, TStandardHomePrm& prm) const;
    // 获取标准回零状态
    bool getStandardHomeStatus(short axis, TStandardHomeStatus& status) const;
    // 一键回零（最常用接口）
    bool homeAxis(short axis, double vel, double acc, long homeOffset = 0);
    // 轴号是否有效
    bool isValidChannel(short ch) const;
    // 获取最后一次错误码
    short lastError() const { return m_lastError; }
    // 获取最后一次错误描述
    QString lastErrorString() const;

signals:
    // 捕获触发 (编码器号, 捕获值)
    void captureTriggered(short encoder, long value);
    // 回零完成 (轴号)
    void homeDone(short axis);
    // 回零失败 (轴号, 错误码)
    void homeFailed(short axis, short errorCode);
    // 发生错误 (通道号, 错误码, 描述)
    void errorOccurred(short channel, short errorCode, const QString& errorMsg);
    // 日志消息
    void logMessage(const QString& message, QColor color = Qt::black, const QString& source = "Gts");

};

#endif // FEEDBACKMGR_H
