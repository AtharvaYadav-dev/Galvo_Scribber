#pragma once

#include <QWidget>
#include "ui_MainWidget.h"

class EzdKernel;
class LaserCtrlWidget;
class MainCtrlWidget;

class MainWidget : public QWidget
{
    Q_OBJECT

public:
    MainWidget(QWidget* parent = nullptr);
    ~MainWidget();

    void setEzcadKernel(EzdKernel* pKernel);
    LaserCtrlWidget* laserCtrlWidget() const;
    MainCtrlWidget* mainCtrlWidget() const;

private:
    Ui::CMainWidgetClass ui;
    LaserCtrlWidget* m_pLaserCtrlWidget = nullptr;
    MainCtrlWidget* m_pMainCtrlWidget = nullptr;

private:
    void InitUI();
};
