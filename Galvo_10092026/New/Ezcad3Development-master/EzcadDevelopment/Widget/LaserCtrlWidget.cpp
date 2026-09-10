#include <QShowEvent>
#include <QResizeEvent>
#include <QTimer>

#include "LaserCtrlWidget.h"
#include "EzcadKernel.h"
#include "../Mgr/EzcadMgr.h"

LaserCtrlWidget::LaserCtrlWidget(QWidget* parent)
    : QWidget(parent)
{
    ui.setupUi(this);
    initUI();
}

LaserCtrlWidget::~LaserCtrlWidget()
{
}

void LaserCtrlWidget::setEzcadKernel(EzdKernel* pKernel)
{
    if (!pKernel) return;
    m_CWndOpenGL.m_pEzcad3 = pKernel;
    ui.previewWnd->m_pEzcad3 = pKernel;
    m_CWndOpenGL.m_WndOpenGL_Rect = ui.previewWnd->rect();
}

void LaserCtrlWidget::setEzcadMgr(EzcadMgr* pMgr)
{
    if (!pMgr) return;
    m_ezcadMgr = pMgr;

    // 标刻完成更新
    connect(m_ezcadMgr, &EzcadMgr::markFinished, this, [this](bool) {
        ui.lcdNumber_markTime->display(m_ezcadMgr->getMakingTime());
        ui.toolButton_mark->setEnabled(true);
        ui.toolButton_redLight->setEnabled(true);
        });

    // 标刻中
    connect(m_ezcadMgr, &EzcadMgr::marking, this, [this]() {
        ui.toolButton_mark->setEnabled(false);
        ui.toolButton_redLight->setEnabled(false);
        });
}

void LaserCtrlWidget::updateOpenGLRect()
{
    if (!ui.previewWnd)
        return;
    ui.previewWnd->m_WndOpenGL_Rect = ui.previewWnd->rect();
    ui.previewWnd->ZoomWorkSpace();
    ui.previewWnd->update();
}

void LaserCtrlWidget::initUI()
{
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

    ui.toolButton_redLight->setIconSize(QSize(50, 50));
    ui.toolButton_mark->setIconSize(QSize(50, 50));
    ui.toolButton_markParam->setIconSize(QSize(50, 50));
    ui.toolButton_stop->setIconSize(QSize(50, 50));

    ui.toolButton_redLight->setIcon(QIcon(":/EzcadDevelopment/res/Redlight.png"));
    ui.toolButton_mark->setIcon(QIcon(":/EzcadDevelopment/res/Mark.png"));
    ui.toolButton_markParam->setIcon(QIcon(":/EzcadDevelopment/res/Param.png"));
    ui.toolButton_stop->setIcon(QIcon(":/EzcadDevelopment/res/Stop.png"));

    ui.toolButton_redLight->setToolButtonStyle(Qt::ToolButtonTextUnderIcon);
    ui.toolButton_mark->setToolButtonStyle(Qt::ToolButtonTextUnderIcon);
    ui.toolButton_markParam->setToolButtonStyle(Qt::ToolButtonTextUnderIcon);
    ui.toolButton_stop->setToolButtonStyle(Qt::ToolButtonTextUnderIcon);

    ui.toolButton_redLight->setStyleSheet(buttonStyle);
    ui.toolButton_mark->setStyleSheet(buttonStyle);
    ui.toolButton_markParam->setStyleSheet(buttonStyle);
    ui.toolButton_stop->setStyleSheet(buttonStyle);

    ui.toolButton_redLight->setShortcut(QKeySequence(Qt::Key_F1));
    ui.toolButton_redLight->setToolTip(QStringLiteral("红光 (F1)"));
    ui.toolButton_mark->setShortcut(QKeySequence(Qt::Key_F2));
    ui.toolButton_mark->setToolTip(QStringLiteral("标刻 (F2)"));
    ui.toolButton_markParam->setShortcut(QKeySequence(Qt::Key_F3));
    ui.toolButton_markParam->setToolTip(QStringLiteral("标刻参数 (F3)"));
    ui.toolButton_stop->setShortcut(QKeySequence(Qt::Key_F4));
    ui.toolButton_stop->setToolTip(QStringLiteral("停止 (F4)"));

    connectUISignalsAndSlots();
}

void LaserCtrlWidget::connectUISignalsAndSlots()
{
    // 标刻参数 F3
    connect(ui.toolButton_markParam, &QToolButton::clicked, this, [this]() {
        if (m_ezcadMgr)
            m_ezcadMgr->openF3ParamDialog();
        });

    // 红光 F1
    connect(ui.toolButton_redLight, &QToolButton::clicked, this, [this]() {
        if (m_ezcadMgr)
            m_ezcadMgr->redLightPreview();
        });

    // 标刻 F2
    connect(ui.toolButton_mark, &QToolButton::clicked, this, [this]() {
        if (m_ezcadMgr) {
            m_ezcadMgr->mark();
        }
        });

    // 停止 F4
    connect(ui.toolButton_stop, &QToolButton::clicked, this, [this]() {
        if (m_ezcadMgr)
            m_ezcadMgr->markStop();
        });
}


void LaserCtrlWidget::showEvent(QShowEvent* event)
{
    QWidget::showEvent(event);
    QTimer::singleShot(0, this, [this]() {
        updateOpenGLRect();
        });
}

void LaserCtrlWidget::resizeEvent(QResizeEvent* event)
{
    QWidget::resizeEvent(event);
    updateOpenGLRect();
}

void LaserCtrlWidget::onEntityChanged(E3_ID entId)
{
    m_CWndOpenGL.m_idShowEnt = entId;
    m_CWndOpenGL.m_WndOpenGL_Rect = ui.previewWnd->rect();
    m_CWndOpenGL.ZoomWorkSpace();
    ui.previewWnd->update();
}
