#include <QMessageBox>
#include <QTimer>
#include <QResizeEvent>
#include <QDateTime>

#include "EzcadDevelopment.h"
#include "LaserCtrlWidget.h"
#include "MainCtrlWidget.h"
#include "GtsSettingWidget.h"
#include "GeneralSettingWidget.h"
#include "../Mgr/GeneralMgr.h"
#include "../Mgr/EzcadMgr.h"
#include "../Mgr/MenuMgr.h"
#include "../Mgr/LogMgr.h"


EzcadDevelopment::EzcadDevelopment(QWidget* parent)
    : QMainWindow(parent)
{
    ui.setupUi(this);
    initUI();
    connectUISignalsAndSlots();
    initApplication();
}

EzcadDevelopment::~EzcadDevelopment()
{
}

void EzcadDevelopment::initUI()
{
    setWindowTitle("NoxDemo");
    setWindowIcon(QIcon(":/EzcadDevelopment/res/owl.png"));
    this->setStyleSheet("QMainWindow { background-color: #F5F5F5; }");

    QString buttonStyle =
        "QToolButton {"
        "  background-color: #e5e5e5;"
        "  border: 1px solid #c0c0c0;"
        "  border-radius: 4px;"
        "  color: #333333;"
        "  font-size: 12px;"
        "  padding: 5px;"
        "}"
        "QToolButton:hover {"
        "  background-color: #d5d5d5;"
        "}"
        "QToolButton:pressed {"
        "  background-color: #c0c0c0;"
        "}";

    ui.toolButton_main->setStyleSheet(buttonStyle);
    ui.toolButton_preview->setStyleSheet(buttonStyle);
    ui.toolButton_axis->setStyleSheet(buttonStyle);
    ui.toolButton_io->setStyleSheet(buttonStyle);
    ui.toolButton_cfg->setStyleSheet(buttonStyle);
    ui.toolButton_other->setStyleSheet(buttonStyle);

    ui.toolButton_main->setIconSize(QSize(50, 50));
    ui.toolButton_preview->setIconSize(QSize(50, 50));
    ui.toolButton_axis->setIconSize(QSize(50, 50));
    ui.toolButton_io->setIconSize(QSize(50, 50));
    ui.toolButton_cfg->setIconSize(QSize(50, 50));
    ui.toolButton_other->setIconSize(QSize(50, 50));

    ui.toolButton_main->setIcon(QIcon(":/EzcadDevelopment/res/Main.png"));
    ui.toolButton_preview->setIcon(QIcon(":/EzcadDevelopment/res/Preview.png"));
    ui.toolButton_axis->setIcon(QIcon(":/EzcadDevelopment/res/Axis.png"));
    ui.toolButton_cfg->setIcon(QIcon(":/EzcadDevelopment/res/Setting.png"));
    ui.toolButton_other->setIcon(QIcon(":/EzcadDevelopment/res/Model.png"));
    ui.toolButton_io->setIcon(QIcon(":/EzcadDevelopment/res/Io.png"));

    ui.toolButton_main->setFixedHeight(85);
    ui.toolButton_preview->setFixedHeight(85);
    ui.toolButton_axis->setFixedHeight(85);
    ui.toolButton_cfg->setFixedHeight(85);
    ui.toolButton_other->setFixedHeight(85);
    ui.toolButton_io->setFixedHeight(85);
    ui.toolButton_main->setToolButtonStyle(Qt::ToolButtonTextUnderIcon);
    ui.toolButton_preview->setToolButtonStyle(Qt::ToolButtonTextUnderIcon);
    ui.toolButton_axis->setToolButtonStyle(Qt::ToolButtonTextUnderIcon);
    ui.toolButton_cfg->setToolButtonStyle(Qt::ToolButtonTextUnderIcon);
    ui.toolButton_other->setToolButtonStyle(Qt::ToolButtonTextUnderIcon);
}


void EzcadDevelopment::initApplication()
{
    // 初始化管理器
    // 用 GeneralMgr 统一管理 EzcadMgr 和 LogMgr
    m_generalMgr = new GeneralMgr(this);
    // 初始化菜单
    initMenu();
    // 初始化界面
    initWidgets();
    // 连接信号
    connectSignalsAndSlots();
    // 延迟初始化 EzcadMgr
    m_generalMgr->initialize();
}

void EzcadDevelopment::createWidgets()
{
    m_mainWidget = new MainWidget(this);
    m_previewWidget = new PreviewWidget(this);
    m_axisControlWidget = new AxisControlWidget(this);
    m_settingsWidget = new SettingsWidget(this);
    m_IOWidget = new IOWidget(this);

    // 设置页子页面
    m_settingsWidget->addPage(QStringLiteral("通用"), new GeneralSettingWidget(m_settingsWidget));
    auto* gtsPage = new GtsSettingWidget(m_settingsWidget);
    m_settingsWidget->addPage(QStringLiteral("GTS"), gtsPage);
}

void EzcadDevelopment::injectDependencies()
{
    m_mainWidget->setEzcadKernel(m_generalMgr->kernel());
    m_mainWidget->laserCtrlWidget()->setEzcadMgr(m_generalMgr->ezcadMgr());
    m_mainWidget->mainCtrlWidget()->setGtsTotalMgr(m_generalMgr->gtsMgr());

    m_previewWidget->setEzcadKernel(m_generalMgr->kernel());

    m_axisControlWidget->setGtsTotalMgr(m_generalMgr->gtsMgr());

    m_IOWidget->setGtsTotalMgr(m_generalMgr->gtsMgr());

    auto* gtsPage = qobject_cast<GtsSettingWidget*>(m_settingsWidget->pageWidget(1));
    if (gtsPage) 
    {
        gtsPage->setGtsTotalMgr(m_generalMgr->gtsMgr());
    }

    auto* generalPage = qobject_cast<GeneralSettingWidget*>(m_settingsWidget->pageWidget(0));
    if (generalPage)
        generalPage->setGeneralMgr(m_generalMgr);
}

void EzcadDevelopment::setupUi()
{
    ui.stackedWidget->addWidget(m_mainWidget);
    ui.stackedWidget->addWidget(m_previewWidget);
    ui.stackedWidget->addWidget(m_axisControlWidget);
    ui.stackedWidget->addWidget(m_IOWidget);
    ui.stackedWidget->addWidget(m_settingsWidget);
    ui.stackedWidget->setCurrentWidget(m_mainWidget);
}

void EzcadDevelopment::initWidgets()
{
    createWidgets();
    injectDependencies();
    setupUi();
}


void EzcadDevelopment::initMenu()
{
    m_menuMgr = new MenuMgr(this);
    m_menuMgr->setupMenuBar(this->menuBar());
    m_menuMgr->setEzcadMgr(m_generalMgr->ezcadMgr());
}



void EzcadDevelopment::connectUISignalsAndSlots()
{
    connect(ui.toolButton_main, &QToolButton::clicked, this, &EzcadDevelopment::onBtnClick);
    connect(ui.toolButton_preview, &QToolButton::clicked, this, &EzcadDevelopment::onBtnClick);
    connect(ui.toolButton_axis, &QToolButton::clicked, this, &EzcadDevelopment::onBtnClick);
    connect(ui.toolButton_cfg, &QToolButton::clicked, this, &EzcadDevelopment::onBtnClick);
    connect(ui.toolButton_io, &QToolButton::clicked, this, &EzcadDevelopment::onBtnClick);
}

void EzcadDevelopment::connectSignalsAndSlots()
{
    EzcadMgr* ezcad = m_generalMgr->ezcadMgr();
    LogMgr* log = m_generalMgr->logMgr();
    GtsMgr* gtsTotalMgr = m_generalMgr->gtsMgr();
      
    if (ezcad) {
        if (m_previewWidget)
        {
            connect(ezcad, &EzcadMgr::entityChanged, m_previewWidget, &PreviewWidget::onEntityChanged);
        }
        if (m_mainWidget) 
        {
            connect(ezcad, &EzcadMgr::entityChanged, m_mainWidget->laserCtrlWidget(), &LaserCtrlWidget::onEntityChanged);
            // 所有日志汇总到logMgr,然后转给界面
            connect(log, &LogMgr::logMessage, m_mainWidget->mainCtrlWidget(), &MainCtrlWidget::onLogMessage);
            connect(log, &LogMgr::errorOccurred, m_mainWidget->mainCtrlWidget(), &MainCtrlWidget::onErrMessage);
        }
        if (m_settingsWidget)
        {
        }
        if (m_IOWidget)
        {
            connect(gtsTotalMgr, &GtsMgr::diUpdated, m_IOWidget, &IOWidget::onDIUpdated);
            connect(gtsTotalMgr, &GtsMgr::doUpdated, m_IOWidget, &IOWidget::onDOUpdated);
            connect(gtsTotalMgr, &GtsMgr::configChanged, m_IOWidget, &IOWidget::onConfigReloaded);
        }
        if (m_generalMgr)
        {
            connect(m_generalMgr, &GeneralMgr::initialized, this, &EzcadDevelopment::onBusinessReady);
        }
    }
}


void EzcadDevelopment::resizeEvent(QResizeEvent* event)
{
    QMainWindow::resizeEvent(event);
}


void EzcadDevelopment::onBtnClick()
{
    auto* btn = qobject_cast<QToolButton*>(sender());
    if (!btn) return;

    if (btn == ui.toolButton_main) {
        ui.stackedWidget->setCurrentWidget(m_mainWidget);
    }
    else if (btn == ui.toolButton_preview) {
        ui.stackedWidget->setCurrentWidget(m_previewWidget);
    }
    else if (btn == ui.toolButton_axis) {
        ui.stackedWidget->setCurrentWidget(m_axisControlWidget);
    }
    else if (btn == ui.toolButton_cfg) {
        ui.stackedWidget->setCurrentWidget(m_settingsWidget);
    }
    else if (btn == ui.toolButton_io) {
        ui.stackedWidget->setCurrentWidget(m_IOWidget);
    }
}

void EzcadDevelopment::onBusinessReady()
{
    m_generalMgr->gtsMgr()->configMgr()->loadAxisConfig();
    m_generalMgr->gtsMgr()->configMgr()->loadIODescriptions();
}