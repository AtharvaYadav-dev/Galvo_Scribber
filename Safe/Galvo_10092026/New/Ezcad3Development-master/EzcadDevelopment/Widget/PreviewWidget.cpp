#include <QShowEvent>
#include <QResizeEvent>
#include <QTimer>

#include "PreviewWidget.h"
#include "EzcadKernel.h"


PreviewWidget::PreviewWidget(QWidget* parent)
    : QWidget(parent)
{
    ui.setupUi(this);
}

PreviewWidget::~PreviewWidget()
{
}

void PreviewWidget::setEzcadKernel(EzdKernel* pKernel)
{
    if (!pKernel) return;
    m_CWndOpenGL.m_pEzcad3 = pKernel;
    ui.openGLWidget->m_pEzcad3 = pKernel;
    m_CWndOpenGL.m_WndOpenGL_Rect = ui.openGLWidget->rect();
}

void PreviewWidget::initUI()
{
    this->setStyleSheet("CMainWidget { background-color: #F5F5F5; }");
}

void PreviewWidget::updateOpenGLRect()
{
    if (!ui.openGLWidget) 
        return;
    QRect r = ui.openGLWidget->rect();
    ui.openGLWidget->m_WndOpenGL_Rect = ui.openGLWidget->rect();
    ui.openGLWidget->ZoomWorkSpace();
    ui.openGLWidget->update();
}

void PreviewWidget::showEvent(QShowEvent* event)
{
    QWidget::showEvent(event);
    QTimer::singleShot(0, this, [this]() {
        updateOpenGLRect();
        });
}

void PreviewWidget::resizeEvent(QResizeEvent* event)
{
    QWidget::resizeEvent(event);
    updateOpenGLRect();
}

void PreviewWidget::onEntityChanged(E3_ID entId)
{
    m_CWndOpenGL.m_idShowEnt = entId;
    m_CWndOpenGL.m_WndOpenGL_Rect = ui.openGLWidget->rect();
    m_CWndOpenGL.ZoomWorkSpace();
    ui.openGLWidget->update();
}
