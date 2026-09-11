#include "MainWidget.h"
#include "EzcadKernel.h"
#include "LaserCtrlWidget.h"
#include "MainCtrlWidget.h"

#include <QVBoxLayout>

MainWidget::MainWidget(QWidget* parent)
    : QWidget(parent)
{
    ui.setupUi(this);
    InitUI();

    m_pLaserCtrlWidget = new LaserCtrlWidget(this);
    QVBoxLayout* lay = new QVBoxLayout(ui.widget_laser);
    lay->setContentsMargins(0, 0, 0, 0);
    lay->addWidget(m_pLaserCtrlWidget);

    m_pMainCtrlWidget = new MainCtrlWidget(this);
    QVBoxLayout* mainCtrlLay = new QVBoxLayout(ui.widget_mainCtrl);
    mainCtrlLay->setContentsMargins(0, 0, 0, 0);
    mainCtrlLay->addWidget(m_pMainCtrlWidget);
}

MainWidget::~MainWidget()
{
}

void MainWidget::setEzcadKernel(EzdKernel* pKernel)
{
    if (m_pLaserCtrlWidget)
        m_pLaserCtrlWidget->setEzcadKernel(pKernel);
}

LaserCtrlWidget* MainWidget::laserCtrlWidget() const
{
    return m_pLaserCtrlWidget;
}

MainCtrlWidget* MainWidget::mainCtrlWidget() const
{
    return m_pMainCtrlWidget;
}

void MainWidget::InitUI()
{
    this->setStyleSheet("CMainWidget { background-color: #F5F5F5; }");
}
