#pragma once
#include <QWidget>
#include "ui_AxisControlWidget.h"
#include "../../GtsCore/GtsMgr.h"

class GtsMgr;
struct Clock;

class AxisControlWidget : public QWidget
{
    Q_OBJECT

public:
    AxisControlWidget(QWidget* parent = nullptr);
    ~AxisControlWidget();
    void setGtsTotalMgr(GtsMgr* mgr);

private:
    Ui::CAxisControlWidgetClass ui;
    GtsMgr* m_gtsMgr = nullptr;

    bool  m_updatingFromBoard = false;
    short m_axisId = 1;
    short m_axisMode = 0;

    void initWidget();
    void initConnections();
    void connectAxisSignals();
    void updateUIEnable(int index);

    // °å¿¨
    void updateBoardState(bool isOpen);
    void onOpen();
    void onClose();
    void onReset();

    // Öá²Ù×÷
    void onClearState();
    void onServoOn();
    void onServoOff();
    void onClearPos();
    void onSmoothStop();
    void onEStop();
    void onTrapMotion();
    void onJogPressed(int direction);
    void onJogReleased();

public slots:
    void onBoardClockUpdated(const Clock& clock);
    void onAxisUpdated(const std::vector<SingleAxisInfo>& axisInfo);
    void onAxisSettingUpdated(const std::vector<SingleAxisInfo>& axisInfo);

private slots:
    void onBtnClick();
    void onTrapParamChanged();
    void onJogParamChanged();
    void onComboBoxCurrentIndexChanged(int index);
    void onComboBoxModeCurrentIndexChanged(int index);
};
