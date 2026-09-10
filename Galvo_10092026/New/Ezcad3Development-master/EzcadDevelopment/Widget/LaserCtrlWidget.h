#pragma once

#include <QWidget>
#include "ui_LaserCtrlWidget.h"
#include "CWndOpenGL.h"

class EzdKernel;
class EzcadMgr;

class LaserCtrlWidget : public QWidget
{
    Q_OBJECT

public:
    LaserCtrlWidget(QWidget* parent = nullptr);
    ~LaserCtrlWidget();

    void setEzcadKernel(EzdKernel* pKernel);
    void setEzcadMgr(EzcadMgr* pMgr);
    void updateOpenGLRect();

private:
    void initUI();
    void connectUISignalsAndSlots();

private:
    Ui::CLaserCtrlWidgetClass ui;
    CWndOpenGL m_CWndOpenGL;
    EzcadMgr* m_ezcadMgr = nullptr;

protected:
    void showEvent(QShowEvent* event) override;
    void resizeEvent(QResizeEvent* event) override;

public slots:
    void onEntityChanged(E3_ID entId);
};
