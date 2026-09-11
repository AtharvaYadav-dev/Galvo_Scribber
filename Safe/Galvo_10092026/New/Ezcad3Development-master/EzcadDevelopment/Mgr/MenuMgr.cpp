#include <QMenuBar>
#include <QMenu>
#include <QAction>
#include <QFileDialog>
#include <QWidget>

#include "MenuMgr.h"
#include "EzcadMgr.h"

MenuMgr::MenuMgr(QObject* parent)
    : QObject(parent)
{
}

MenuMgr::~MenuMgr()
{
}

void MenuMgr::setEzcadMgr(EzcadMgr* mgr)
{
    m_ezcadMgr = mgr;
}

void MenuMgr::setupMenuBar(QMenuBar* menuBar)
{
    if (!menuBar) return;

    menuBar->setStyleSheet(
        "QMenuBar {"
        "    background-color: #F5F5F5;"
        "}"
        "QMenuBar::item:selected {"
        "    background-color: #E0E0E0;"   // 选中时稍深一点
        "}"
        "QMenu {"
        "    background-color: #F5F5F5;"
        "    border: 1px solid #D0D0D0;"   // 轻微边框
        "}"
        "QMenu::item:selected {"
        "    background-color: #E0E0E0;"   // 菜单项 hover 效果
        "}"
    );

    m_fileMenu = menuBar->addMenu(QStringLiteral("文件(&F)"));

    m_openAction = m_fileMenu->addAction(QStringLiteral("打开(&O)"));
    m_openAction->setShortcut(QKeySequence::Open);   // Ctrl+O

    m_fileMenu->addSeparator();

    m_saveAction = m_fileMenu->addAction(QStringLiteral("保存(&S)"));
    m_saveAction->setShortcut(QKeySequence::Save);   // Ctrl+S

    m_openEzcadAction = m_fileMenu->addAction(QStringLiteral("打开Ezcad软件(&E)"));
    m_openEzcadAction->setShortcut(QKeySequence("Ctrl+E"));

    connect(m_openAction, &QAction::triggered, this, &MenuMgr::openRequested);
    connect(m_saveAction, &QAction::triggered, this, &MenuMgr::saveRequested);
    connect(m_openEzcadAction, &QAction::triggered, this, &MenuMgr::onOpenEzcadAction);
}


void MenuMgr::openRequested()
{
    if (!m_ezcadMgr) return;

    QWidget* parentWidget = qobject_cast<QWidget*>(parent());
    QString path = QFileDialog::getOpenFileName(
        parentWidget,
        QStringLiteral("选择文件"),
        QString(),
        QStringLiteral("ez3(*.ez3)"));

    if (path.isEmpty()) return;

    m_ezcadMgr->openFile(path);
}


void MenuMgr::saveRequested()
{
    if (!m_ezcadMgr) return;

    QWidget* parentWidget = qobject_cast<QWidget*>(parent());
    QString path = QFileDialog::getSaveFileName(
        parentWidget,
        QStringLiteral("保存文件"),
        QString(),
        QStringLiteral("Ez3(.ez3)|*.ez3"));

    if (path.isEmpty()) return;

    m_ezcadMgr->saveFile(path);
}

void MenuMgr::onOpenEzcadAction()
{
    if (!m_ezcadMgr) return;
    m_ezcadMgr->startEzcad(m_ezcadMgr->currentFilePath());
}
