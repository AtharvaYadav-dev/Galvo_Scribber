#ifndef TOTALMGR_H
#define TOTALMGR_H

#include <QObject>
#include <QColor>
#include <QTimer>
#include <memory>
#include <vector>

#include "GtsBoardMgr.h"
#include "GtsAxisMgr.h"
#include "GtsMotionMgr.h"
#include "GtsInterpolationMgr.h"
#include "GtsIOMgr.h"
#include "GtsFeedbackMgr.h"
#include "GtsConfigMgr.h"

// GtsMgr — 总管理器
class GtsMgr : public QObject 
{
    Q_OBJECT

private:
    // 板卡模式
    CardMode m_cardMode = CardMode::Normal;
    // 是否初始化
    bool m_initialized = false;
    // 刷新数据定时器
    QTimer* m_refreshTimer = nullptr;
    // 轴数
    int m_axisCount = 4;
    // 板卡时钟
    Clock m_clocks;
    // 轴数据
    AxisInfo m_axisInfo;
    // DI
    DI m_di;
    // DO
    DO m_do;
    // 配置
    AxisConfig m_cfg;

    // 板卡的管理类
    std::unique_ptr<BoardMgr> m_boardMgr;
    std::unique_ptr<AxisMgr> m_axisMgr;
    std::unique_ptr<MotionMgr> m_motionMgr;
    std::unique_ptr<InterpolationMgr> m_interpolationMgr;
    std::unique_ptr<IOMgr> m_ioMgr;
    std::unique_ptr<ConfigMgr> m_configMgr;
    std::unique_ptr<FeedbackMgr> m_feedbackMgr;

public:
    explicit GtsMgr(QObject* parent = nullptr);
    ~GtsMgr();

    // 板卡管理器
    BoardMgr* boardMgr() const { return m_boardMgr.get(); }
    // 轴管理器
    AxisMgr* axisMgr() const { return m_axisMgr.get(); }
    // 运动管理器
    MotionMgr* motionMgr() const { return m_motionMgr.get(); }
    // 插补管理器
    InterpolationMgr* interpolationMgr() const { return m_interpolationMgr.get(); }
    // IO管理器
    IOMgr* ioMgr() const { return m_ioMgr.get(); }
    // 反馈管理器
    FeedbackMgr* feedbackMgr() const { return m_feedbackMgr.get(); }
    // 配置管理器
    ConfigMgr* configMgr() const { return m_configMgr.get(); }
    // 轴配置数据
    AxisConfig* axisCfg() { return &m_cfg; }
    // 板卡模式
    CardMode cardMode() const { return m_cardMode; }
    // 设置板卡模式
    void setCardMode(CardMode mode) { m_cardMode = mode; }

public:
    // 返回轴数
    int axisCount() const { return m_axisCount; }
    // 获取轴数据的指针
    SingleAxisInfo* getAxisRef(int index) { if (index < 0 || index >= (int)m_axisInfo.items.size()) { return nullptr; }return &m_axisInfo.items[index]; }
    // 是否正在刷新
    bool isRefreshing() const { return m_refreshTimer->isActive(); };
    // 启动刷新实时数据
    void startRefresh(int intervalMs = 300);
    // 停止刷新实时数据
    void stopRefresh();                   
    // 板卡打开后的初始化
    void initAfterBoardOpened();
    // 板卡关闭后的清理
    void cleanupAfterBoardClosed();
    // ── 当量换算工具 ──
    double pulsePerMm(short profile) const;          // 脉冲/mm 系数
    double mmPerPulse(short profile) const;          // mm/脉冲 系数
    long   mmToPulse(short profile, double mm) const; // mm → pulse
    double mmpsToPulsePerMs(short profile, double mmps) const;   // mm/s → pulse/ms
    double mmps2ToPulsePerMs2(short profile, double mmps2) const; // mm/s² → pulse/ms²
    double pulseToMm(short profile, long pulse) const; // pulse → mm（显示用）


signals:
    // 板卡时钟更新
    void boardClockUpdated(const Clock& clock);
    // 轴实时数据更新
    void axisUpdated(const std::vector<SingleAxisInfo>& axisInfo);
    // 轴参数更新
    void axisSettingUpdated(const std::vector<SingleAxisInfo>& axisInfo);
    // DI 更新
    void diUpdated(const DI& di);
    // DO 更新
    void doUpdated(const DO& do_);
    // 发生错误
    void errorOccurred(short axis, short errorCode, const QString& errorMsg);
    // 日志消息
    void logMessage(const QString& message, QColor color = Qt::black, const QString& source = "Gts");
    // 配置变化
    void configChanged();
    
private slots:
    // 定时读取刷新数据
    void onRefreshTimeout();
    // 转发错误发生
    void onErrorOccurred(short axis, short errorCode, const QString& errorMsg);
    // 转发日志信息
    void onLogMessage(const QString& message, QColor color = Qt::black, const QString& source = "Gts");
    // 转发配置变化
    void onConfigChanged();

};

#endif // TOTALMGR_H
