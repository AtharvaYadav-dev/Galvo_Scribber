#pragma once
#include <QtWidgets/QMainWindow>

#include "ui_EzcadDevelopment.h"
#include "MainWidget.h"
#include "PreviewWidget.h"
#include "AxisControlWidget.h"
#include "SettingsWidget.h"
#include "IOWidget.h"

class EzcadMgr;
class GeneralMgr;
class MenuMgr;
class LogMgr;

class EzcadDevelopment : public QMainWindow
{
    Q_OBJECT

public:
    EzcadDevelopment(QWidget* parent = nullptr);
    ~EzcadDevelopment();

private:
    void initApplication();
    void createWidgets();
    void injectDependencies();
    void setupUi();
    void initUI();
    void initWidgets();
    void initMenu();

    void connectUISignalsAndSlots();
    void connectSignalsAndSlots();

private:
    Ui::EzcadDevelopmentClass ui;
    GeneralMgr* m_generalMgr = nullptr;
    MenuMgr* m_menuMgr = nullptr;

    MainWidget* m_mainWidget = nullptr;
    PreviewWidget* m_previewWidget = nullptr;
    AxisControlWidget* m_axisControlWidget = nullptr;
    SettingsWidget* m_settingsWidget = nullptr;
    IOWidget* m_IOWidget = nullptr;

protected:
    void resizeEvent(QResizeEvent* event) override;

private slots:
    void onBtnClick();
    void onBusinessReady();

};
