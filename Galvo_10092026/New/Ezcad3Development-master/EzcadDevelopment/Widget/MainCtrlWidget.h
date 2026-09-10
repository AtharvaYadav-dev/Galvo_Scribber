#pragma once
#include <QWidget>
#include <QColor>

#include "ui_MainCtrlWidget.h"
#include "../../GtsCore/GtsMgr.h"

class GtsMgr;

class MainCtrlWidget : public QWidget
{
    Q_OBJECT

public:
    MainCtrlWidget(QWidget* parent = nullptr);
    ~MainCtrlWidget();

    void setGtsTotalMgr(GtsMgr* mgr);

private:
    Ui::CMainCtrlWidgetClass ui;
    GtsMgr* m_gtsMgr = nullptr;
    short m_axisId = 1;
    bool m_connectionsInitialized = false;

    void initConnections();
    short axisIdByName(AxisName name) const;

    // Jog 点动
    void onJogPressed(short axisId, int direction);
    void onJogReleased(short axisId);
    void onStopAll();

    // 点位移动 / 回零
    void onHome(short axisId);
    void onActMotion();

public slots:
    void onLogMessage(const QString& message, QColor color = Qt::black);
    void onErrMessage(int errorCode, const QString& message);
    void onAxisUpdated(const std::vector<SingleAxisInfo>& axisInfo);
};
