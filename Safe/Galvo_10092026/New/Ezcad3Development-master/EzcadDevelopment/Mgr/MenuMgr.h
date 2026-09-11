// Mgr/MenuMgr.h
#pragma once
#include <QObject>

class QMenu;
class QAction;
class QMenuBar;
class EzcadMgr;

class MenuMgr : public QObject
{
    Q_OBJECT

public:
    explicit MenuMgr(QObject* parent = nullptr);
    ~MenuMgr();

    void setupMenuBar(QMenuBar* menuBar);
    void setEzcadMgr(EzcadMgr* mgr);

private:
    QMenu* m_fileMenu = nullptr;
    QAction* m_openAction = nullptr;
    QAction* m_saveAction = nullptr;
    QAction* m_openEzcadAction = nullptr;
    QAction* m_settingsAction = nullptr;
    EzcadMgr* m_ezcadMgr = nullptr;

private slots:
    void openRequested();
    void saveRequested();
    void onOpenEzcadAction();
};
