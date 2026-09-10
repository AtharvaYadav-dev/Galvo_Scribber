#ifndef INTERPOLATIONMGR_H
#define INTERPOLATIONMGR_H

#include <QObject>
#include <QString>
#include <QColor>
#include "GtsHal.h"


// ============================================================
// InterpolationMgr — 多轴插补运动管理器
// 职责：管理坐标系中的多轴联动插补
//   - 坐标系配置
//   - 直线插补(2轴/3轴/4轴)
//   - 圆弧插补(XY/YZ/ZX/3D)
//   - 螺旋插补
//   - 缓冲区内操作 (IO/延时/DA)
//   - 启动/停止/状态查询
// ============================================================


class InterpolationMgr : public QObject {
    Q_OBJECT

private:
    mutable short m_lastError = 0;
    bool checkCrd(short crd) const;

public:
    explicit InterpolationMgr(QObject* parent = nullptr);
    ~InterpolationMgr();


    // 设置坐标系参数
    bool setCrdParams(short crd, const TCrdPrm& prm);
    // 获取坐标系参数
    bool getCrdParams(short crd, TCrdPrm& prm) const;
    // 设置坐标系平滑参数
    bool setCrdSmooth(short crd, const TCrdSmooth& smooth);
    // 获取坐标系平滑参数
    bool getCrdSmooth(short crd, TCrdSmooth& smooth) const;
    // 设置坐标系加加速度
    bool setCrdJerk(short crd, double jerkMax);
    // 获取坐标系加加速度
    double getCrdJerk(short crd) const;
    // 设置坐标系映射基轴
    bool setCrdMapBase(short crd, short base);
    // 获取坐标系映射基轴
    short getCrdMapBase(short crd) const;
    // 设置圆弧允许误差
    bool setArcAllowError(short crd, double error);
    // 设置坐标系停止减速度
    bool setCrdStopDecel(short crd, double decSmooth, double decAbrupt);
    // 获取坐标系停止减速度
    bool getCrdStopDecel(short crd, double& decSmooth, double& decAbrupt) const;
    // 2D 直线插补 (XY)
    bool lineXY(short crd, long x, long y, double synVel, double synAcc, double velEnd = 0, short fifo = 0);
    // 3D 直线插补 (XYZ)
    bool lineXYZ(short crd, long x, long y, long z, double synVel, double synAcc, double velEnd = 0, short fifo = 0);
    // 4D 直线插补 (XYZA)
    bool lineXYZA(short crd, long x, long y, long z, long a, double synVel, double synAcc, double velEnd = 0, short fifo = 0);
    // 2D 直线插补 - G0 快速定位模式
    bool lineXYG0(short crd, long x, long y, double synVel, double synAcc, short fifo = 0);
    // 3D 直线插补 - G0 快速定位模式
    bool lineXYZG0(short crd, long x, long y, long z, double synVel, double synAcc, short fifo = 0);
    // 4D 直线插补 - G0 快速定位模式
    bool lineXYZAG0(short crd, long x, long y, long z, long a, double synVel, double synAcc, short fifo = 0);
    // 通用多轴直线插补 (XYZACUVW)
    bool lineXYZACUVW(short crd, long* pPos, short posMask, double synVel, double synAcc, double velEnd = 0, short fifo = 0);
    // XY 平面圆弧 - 半径模式
    bool arcXYByRadius(short crd, long x, long y, double radius, short circleDir, double synVel, double synAcc, double velEnd = 0, short fifo = 0);
    // XY 平面圆弧 - 圆心模式
    bool arcXYByCenter(short crd, long x, long y, double xCenter, double yCenter, short circleDir, double synVel, double synAcc, double velEnd = 0, short fifo = 0);
    // YZ 平面圆弧 - 半径模式
    bool arcYZByRadius(short crd, long y, long z, double radius, short circleDir, double synVel, double synAcc, double velEnd = 0, short fifo = 0);
    // YZ 平面圆弧 - 圆心模式
    bool arcYZByCenter(short crd, long y, long z, double yCenter, double zCenter, short circleDir, double synVel, double synAcc, double velEnd = 0, short fifo = 0);
    // ZX 平面圆弧 - 半径模式
    bool arcZXByRadius(short crd, long z, long x, double radius, short circleDir, double synVel, double synAcc, double velEnd = 0, short fifo = 0);
    // ZX 平面圆弧 - 圆心模式
    bool arcZXByCenter(short crd, long z, long x, double zCenter, double xCenter, short circleDir, double synVel, double synAcc, double velEnd = 0, short fifo = 0);
    // 3D 空间圆弧 (XYZ)
    bool arcXYZ(short crd, long x, long y, long z, double interX, double interY, double interZ, double synVel, double synAcc, double velEnd = 0, short fifo = 0);
    // XY 平面圆弧 + Z 轴螺旋 - 半径模式
    bool helixXYRZ(short crd, long x, long y, long z, double radius, short circleDir, double synVel, double synAcc, double velEnd = 0, short fifo = 0);
    // XY 平面圆弧 + Z 轴螺旋 - 圆心模式
    bool helixXYCZ(short crd, long x, long y, long z, double xCenter, double yCenter, short circleDir, double synVel, double synAcc, double velEnd = 0, short fifo = 0);
    // 缓冲区 IO 操作
    bool bufIO(short crd, unsigned short doType, unsigned short doMask, unsigned short doValue, short fifo = 0);
    // 缓冲区延时
    bool bufDelay(short crd, unsigned short delayTime, short fifo = 0);
    // 缓冲区 DA 输出
    bool bufDA(short crd, short chn, short daValue, short fifo = 0);
    // 缓冲区单轴移动
    bool bufMove(short crd, short moveAxis, long pos, double vel, double acc, short modal, short fifo = 0);
    // 缓冲区齿轮移动
    bool bufGear(short crd, short gearAxis, long pos, short fifo = 0);
    // 缓冲区停止
    bool bufStop(short crd, long mask, long option, short fifo = 0);
    // 缓冲区 Jog 移动
    bool bufMoveJog(short crd, short moveAxis, double vel, double acc, short modal, short fifo = 0);
    // 启动插补运动
    bool start(short mask, short option = 0);
    // 单步启动插补
    bool startStep(short mask, short option = 0);
    // 设置单步模式
    bool setStepMode(short mask, short option = 0);
    // 清除插补缓冲区
    bool clear(short crd, short fifo = 0);
    // 查询插补 FIFO 剩余空间
    long freeSpace(short crd, short fifo = 0) const;
    // 查询插补状态
    bool status(short crd, short& running, long& segment, short fifo = 0) const;
    // 获取坐标系当前位置
    bool getCrdPosition(short crd, double* pPos) const;
    // 获取坐标系当前速度
    double getCrdVelocity(short crd) const;
    // 设置速度倍率
    bool setOverride(short crd, double synVelRatio);
    // 设置速度倍率 (版本2)
    bool setOverride2(short crd, double synVelRatio);
    // 设置最大速度倍率 (LA)
    bool setMaxOverrideLA(double maxSynVelRatio);
    // 设置用户段号
    bool setUserSegment(short crd, long segNum, short fifo = 0);
    // 获取用户段号
    long getUserSegment(short crd, short fifo = 0) const;
    // 获取剩余段数
    long getRemainingSegment(short crd, short fifo = 0) const;
    // 设置缓冲区模式
    bool setBufferMode(short crd, short bufferMode, short fifo = 0);
    // 获取缓冲区模式
    short getBufferMode(short crd, short fifo = 0) const;
    // 快速直线插补 (最常用：XY 移动到指定位置)
    bool moveToXY(short crd, long x, long y, double vel, double acc);
    // 停止插补运动
    bool stop(short crd, long option = 0);
    // 坐标系号是否有效
    bool isValidCrd(short crd) const;
    // 获取最后一次错误码
    short lastError() const { return m_lastError; }
    // 获取最后一次错误描述
    QString lastErrorString() const;

signals:
    // 插补运动完成 (坐标系号)
    void interpolationDone(short crd);
    // 发生错误 (坐标系号, 错误码, 描述)
    void errorOccurred(short crd, short errorCode, const QString& errorMsg);
    // 日志消息
    void logMessage(const QString& message, QColor color = Qt::black, const QString& source = "Gts");

};

#endif // INTERPOLATIONMGR_H
