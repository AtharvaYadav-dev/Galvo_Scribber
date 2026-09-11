#ifndef MOTIONMGR_H
#define MOTIONMGR_H

#include <QObject>
#include <QString>
#include <QColor>
#include "GtsHal.h"
#include "ControllerData.h"

class GtsMgr;

// 循环 Trap 运动异步状态机
struct TrapCycleState {
    bool   active       = false;
    short  profile      = 0;
    double stepSize     = 0.0;
    double acc          = 0.0;
    double dec          = 0.0;
    int    smoothTime   = 0;
    double vel          = 0.0;
    int    totalTimes   = 0;
    int    currentStep  = 0;   // 已完成的步数(0=未开始, 每步正向+反向),
    double delayMs      = 0.0;
};

// ============================================================
// MotionMgr — 单轴运动管理器
// 职责：管理所有单轴运动模式
//       - 梯形/点位运动 (Trap)
//       - Jog 持续运动
//       - MoveAbsolute / MoveVelocity 便捷运动
//       - PT 位置-时间运动
//       - Gear 电子齿轮
//       - Follow 电子凸轮
//       - PVT 运动
// ============================================================

class MotionMgr : public QObject 
{
    Q_OBJECT

private:
    mutable short m_lastError = 0;
    GtsMgr* m_gtsMgr = nullptr;
    TrapCycleState m_trapCycle;        // 循环 Trap 异步状态

public:
    explicit MotionMgr(GtsMgr* totalMgr, QObject* parent = nullptr);
    ~MotionMgr();
    void setTotalMgr(GtsMgr* mgr) { m_gtsMgr = mgr; }

    //设置指定轴的运动模式
    bool setAxisMotionMode(short axis, short mode);
    // 读取规划器相关
    void getAxisMotionInfo(std::vector<SingleAxisInfo>& vecAxis);
    // 读取通用运动参数
    void getCommonMotionInfo(std::vector<SingleAxisInfo>& vecTrap);
    // 读取点位运动相关
    void getTrapMotionInfo(std::vector<SingleAxisInfo>& vecTrap);
    // 设置点位运动相关
    bool setTrapParam(short axisId, const TrapParam& param);
    // 启动点位运动(相对运动,步长可正可负) —— 长度版,内部自动做当量换算
    bool trapMotion(short profile, double lengthMm);
    // 同步版 trapMotion: 阻塞等待全部运动完成, 但 UI 不冻结
    bool trapMotionSync(short profile, double lengthMm);
    // 读取Jog 运动参数
    void getJogMotionInfo(std::vector<SingleAxisInfo>& vecAxis);
    // 设置Jog 运动参数
    bool setJogParam(short axisId, const JogParam& param);
    // 启动Jog运动(direction: +1 正方向, -1 反方向)
    bool startJogMotion(short profile, short direction);
    // 启动回零
    bool homeStart(short axis);


    // 使用梯形模式移动单轴到绝对位置
    bool moveTo(short profile, long pos, double vel, double acc = 100.0, double dec = 100.0);
    // 使用 Jog 模式持续运动
    bool jog(short profile, double vel, double acc = 100.0);
    // 停止单轴运动
    bool stop(short profile, long option = 0);
    // 取消循环 Trap 运动(异步安全停止)
    void cancelTrapCycle();
    // 获取最后一次错误码
    short lastError() const { return m_lastError; }
    // 获取最后一次错误描述
    QString lastErrorString() const;

private:
    // 检查规划器
    bool checkProfile(short profile) const;
    // 点位运动
    bool singleTrapMotion(short profile, double stepSize, double acc, double dec, int smoothTime, double vel);
    // 等待运动
    void waitMotionDone(short profile);
    // 启动点位运动
    bool startTrapMotion(short profile, double stepSize, const TrapParam& trapParam);

public:
    // 设置规划器位置
    bool setProfilePos(short profile, long pos);
    // 获取规划器位置
    double profilePos(short profile) const;
    // 获取规划器速度
    double profileVel(short profile) const;
    // 获取规划器加速度
    double profileAcc(short profile) const;
    // 获取规划器模式
    long profileMode(short profile) const;
    // 获取轴规划器位置
    double axisProfilePos(short axis) const;
    // 获取轴规划器速度
    double axisProfileVel(short axis) const;
    // 获取轴规划器加速度
    double axisProfileAcc(short axis) const;
    // 设置目标位置
    bool setTargetPos(short profile, long pos);
    // 设置目标速度
    bool setTargetVel(short profile, double vel);
    // 获取目标位置
    long targetPos(short profile) const;
    // 获取目标速度
    double targetVel(short profile) const;
    // 更新多个轴的运动参数
    bool update(long mask);
    // 设置/获取 Profile 缩放系数
    bool setProfileScale(short axis, long alpha, long beta);
    bool getProfileScale(short axis, long& alpha, long& beta) const;
    // 设置为梯形速度模式
    bool setTrapMode(short profile);
    // 设置梯形参数
    bool setTrapParams(short profile, const TTrapPrm& prm);
    // 获取梯形参数
    bool getTrapParams(short profile, TTrapPrm& prm) const;
    // 获取梯形运动时间信息
    bool getTrapTime(short profile, TTrapTime& time) const;
    // 设置为 Jog 模式
    bool setJogMode(short profile);
    // 设置 Jog 参数
    bool setJogParams(short profile, const TJogPrm& prm);
    // 获取 Jog 参数
    bool getJogParams(short profile, TJogPrm& prm) const;
    // 绝对位置运动(便捷接口)
    bool moveAbsolute(short profile, long pos, double vel, double acc = 0, double dec = 0);
    // 速度运动(便捷接口)
    bool moveVelocity(short profile, double vel, double acc = 0);
    // 获取运动参数
    bool getMoveAbsoluteParams(short profile, TMoveAbsolutePrm& prm) const;
    bool getMoveVelocityParams(short profile, TMoveVelocityPrm& prm) const;
    // 设置为 PT 模式
    bool setPtMode(short profile, short mode = PT_MODE_STATIC);
    // 设置 PT 循环次数
    bool setPtLoop(short profile, long loop);
    // 获取 PT 循环次数
    long getPtLoop(short profile) const;
    // 查询 PT FIFO 剩余空间
    short ptFreeSpace(short profile, short fifo = 0) const;
    // 添加 PT 数据段
    bool ptAddData(short profile, double pos, long time, short type = PT_SEGMENT_NORMAL, short fifo = 0);
    // 添加带段号的 PT 数据
    bool ptAddDataWithSeg(short profile, double pos, long time, short type = PT_SEGMENT_NORMAL, long segNum = 0, short fifo = 0);
    // 清除 PT FIFO
    bool ptClear(short profile, short fifo = 0);
    // 启动 PT 运动
    bool ptStart(long mask, long option = 0);
    // 设置/获取 PT 内存
    bool setPtMemory(short profile, short memory);
    short getPtMemory(short profile) const;
    // 获取当前 PT 段号
    long ptCurrentSegment(short profile) const;
    // PT 中添加 DO 操作
    bool ptAddDoBit(short profile, short doType, short index, short value, short fifo);
    // PT 中添加 AO 操作
    bool ptAddAo(short profile, short aoType, short index, double value, short fifo);
    // 设置为 Gear 模式
    bool setGearMode(short profile, short dir = 0);
    // 设置主轴
    bool setGearMaster(short profile, short masterIndex, short masterType = GEAR_MASTER_PROFILE, short masterItem = 0);
    // 获取主轴
    bool getGearMaster(short profile, short& masterIndex, short& masterType, short& masterItem) const;
    // 设置齿轮比
    bool setGearRatio(short profile, long masterEven, long slaveEven, long masterSlope = 0);
    // 获取齿轮比
    bool getGearRatio(short profile, long& masterEven, long& slaveEven, long& masterSlope) const;
    // 启动齿轮运动
    bool gearStart(long mask);
    // 设置齿轮事件
    bool setGearEvent(short profile, short event, long startPara0, long startPara1);
    // 获取齿轮事件
    bool getGearEvent(short profile, short& event, long& startPara0, long& startPara1) const;
    // 设置为 Follow 模式
    bool setFollowMode(short profile, short dir = 0);
    // 设置主轴
    bool setFollowMaster(short profile, short masterIndex,short masterType = FOLLOW_MASTER_PROFILE, short masterItem = 0);
    // 获取主轴
    bool getFollowMaster(short profile, short& masterIndex, short& masterType, short& masterItem) const;
    // 设置循环次数
    bool setFollowLoop(short profile, long loop);
    long getFollowLoop(short profile) const;
    // 设置跟随事件
    bool setFollowEvent(short profile, short event, short masterDir, long pos = 0);
    bool getFollowEvent(short profile, short& event, short& masterDir, long& pos) const;
    // 查询 FIFO 剩余空间
    short followFreeSpace(short profile, short fifo = 0) const;
    // 添加凸轮数据段
    bool followAddData(short profile, long masterSegment, double slaveSegment,short type = FOLLOW_SEGMENT_NORMAL, short fifo = 0);
    // 清除 FIFO
    bool followClear(short profile, short fifo = 0);
    // 启动跟随运动
    bool followStart(long mask, long option = 0);
    // 切换跟随
    bool followSwitch(long mask);
    // 设置/获取 Follow 内存
    bool setFollowMemory(short profile, short memory);
    short getFollowMemory(short profile) const;
    // 获取跟随状态
    bool getFollowStatus(short profile, short& fifoNum, short& switchStatus) const;
    // 设置为 PVT 模式
    bool setPvtMode(short profile);
    // 设置 PVT 循环
    bool setPvtLoop(short profile, long loop);
    bool getPvtLoop(short profile, long& loopCount, long& loop) const;
    // 获取 PVT 状态
    bool pvtStatus(short profile, short& tableId, double& time) const;
    // 清除 PVT 表
    bool pvtTableClear(short tableId);
    // 启动 PVT 运动
    bool pvtStart(long mask);
    // 选择 PVT 表
    bool pvtTableSelect(short profile, short tableId);
    // 写入 PVT 表(位置-速度模式)
    bool pvtTableSet(short tableId, long count, double* time, double* pos, double* vel);
    // 写入 PVT 表(起止速度模式)
    bool pvtTableSetEx(short tableId, long count, double* time, double* pos, double* velBegin, double* velEnd);
    // 写入 PVT 表(完全模式：三次多项式系数)
    bool pvtTableSetComplete(short tableId, long count, double* time, double* pos, double* a, double* b, double* c, double velBegin = 0, double velEnd = 0);
    // 写入 PVT 表(百分比模式)
    bool pvtTableSetPercent(short tableId, long count, double* time, double* pos, double* percent, double velBegin = 0);


private slots:
    // 循环 Trap 运动状态机驱动(递归自调度)
    void onTrapCycleStep(short profile);

signals:
    // 运动完成(轴号)
    void motionDone(short profile);
    // 发生错误 (轴号, 错误码, 描述)
    void errorOccurred(short profile, short errorCode, const QString& errorMsg);
    // 日志消息
    void logMessage(const QString& message, QColor color = Qt::black, const QString& source = "Gts");

};

#endif // MOTIONMGR_H
