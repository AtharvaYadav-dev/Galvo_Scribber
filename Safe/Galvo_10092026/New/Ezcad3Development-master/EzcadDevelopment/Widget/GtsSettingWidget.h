#pragma once

#include <QWidget>
#include "ui_GtsSettingWidget.h"

class GtsMgr;

class GtsSettingWidget : public QWidget
{
    Q_OBJECT

public:
    GtsSettingWidget(QWidget* parent = nullptr, GtsMgr* mgr = nullptr);
    ~GtsSettingWidget();
    void setGtsTotalMgr(GtsMgr* mgr);

private:
    void initUI();
    void connectSignals();
    // 刷新数据
    void refreshDacValues();
    void refreshFollowErrorLimit();
    void refreshStopDecel();
    void refreshScaleValues();
    void refreshControlMode();
    void refreshHomeConfig();
    void refreshAxisLimit();
    void refreshAxisName();
    void refreshSoftPulseScale();
    // 把当前 UI 值提交到 ConfigMgr
    void commitDacForAxis(short dac);
    void commitFollowErrorForAxis(short ctrl);
    void commitStopDecelForProfile(short profile);
    void commitScaleForAxis(short axis);
    void commitControlModeForAxis(short axis);
    void commitHomeForAxis(short axis);
    void commitAxisLimitForAxis(short axis);
    void commitAxisNameForAxis(short axis);
    void commitSoftPulseScaleForAxis(short axis);

private:
    Ui::CGtsSettingWidgetClass ui;
    GtsMgr* m_gtsMgr = nullptr;
    bool m_refreshing = false;   // 刷新期间屏蔽信号
    // 追踪各 combo 上一次的轴号，用于切轴时提交旧轴数据
    short m_prevDacId = 1;
    short m_prevCtrlId = 1;
    short m_prevProfileId = 1;
    short m_prevAxisId = 1;
    short m_prevHomeAxisId = 1;

private slots:
    void onApplyAndSave();
    void onApplyToBoard();
    void onLoadConfigFile();

public slots:
    void onConfigChanged();
};

// 工具函数
inline void comboAddNumbers(QComboBox* cb, int n)
{
    if (!cb) return;
    for (int i = 1; i <= n; ++i)
        cb->addItem(QString::number(i));
}

inline void comboAddItems(QComboBox* cb, std::initializer_list<QString> items)
{
    if (!cb) return;
    for (const auto& s : items)
        cb->addItem(s);
}
