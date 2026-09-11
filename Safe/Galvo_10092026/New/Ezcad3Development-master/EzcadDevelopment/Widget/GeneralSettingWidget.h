#pragma once

#include <QWidget>
#include "ui_GeneralSettingWidget.h"

class GeneralMgr;

class GeneralSettingWidget : public QWidget
{
	Q_OBJECT

public:
	GeneralSettingWidget(QWidget *parent = nullptr);
	~GeneralSettingWidget();
	void setGeneralMgr(GeneralMgr* mgr);

private:
	Ui::GeneralSettingWidgetClass ui;
	GeneralMgr* m_generalMgr = nullptr;
	void onChoseDir();
	void onSave();
};

