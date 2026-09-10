#pragma once
#include <QWidget>
#include "ui_PreviewWidget.h"

#include "CWndOpenGL.h"

class EzdKernel;

class PreviewWidget : public QWidget
{
    Q_OBJECT

public:
    PreviewWidget(QWidget* parent = nullptr);
    ~PreviewWidget();

    void setEzcadKernel(EzdKernel* pKernel);
    void updateOpenGLRect();

private:
    Ui::CPreviewWidgetClass ui;
    CWndOpenGL m_CWndOpenGL;

private:
    void initUI();

protected:
    void showEvent(QShowEvent* event) override;
    void resizeEvent(QResizeEvent* event) override;

public slots:
    void onEntityChanged(E3_ID entId);
};
