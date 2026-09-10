#pragma once
#include <QWidget>
#include <QMap>

#include "ui_IOWidget.h"
#include "../../GtsCore/ControllerData.h"
#include "../../GtsCore/GtsMgr.h"

class IOWidget : public QWidget
{
    Q_OBJECT

public:
    IOWidget(QWidget* parent = nullptr, GtsMgr* mgr = nullptr);
    ~IOWidget();
    void setGtsTotalMgr(GtsMgr* mgr);

private:
    void InitUI();
    void InitTableDI();
    void InitTableDO();
    void connectPrivateSignal();
    void RefreshTable(QTableWidget* table, const std::vector<int>& status);

    void onDOCellClicked(int row, int col);
    void onDICellDoubleClicked(int row, int col);
    void onDOCellDoubleClicked(int row, int col);
    void onDescriptionEdited(int row, bool isDI);
 
public slots:
    void onDIUpdated(const DI& di);
    void onDOUpdated(const DO& dout);
    void onConfigReloaded();

private:
    Ui::CIOWidgetClass ui;
    GtsMgr* m_gtsMgr = nullptr;
    DO m_doState;
};
