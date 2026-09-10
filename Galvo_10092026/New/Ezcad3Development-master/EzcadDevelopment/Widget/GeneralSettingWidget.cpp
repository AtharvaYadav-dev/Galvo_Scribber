#include "GeneralSettingWidget.h"
#include "../Mgr/GeneralMgr.h"
#include <QFileDialog>

GeneralSettingWidget::GeneralSettingWidget(QWidget *parent)
	: QWidget(parent)
{
	ui.setupUi(this);
	connect(ui.pushButton_choseDir, &QPushButton::clicked, this, &GeneralSettingWidget::onChoseDir);
	connect(ui.pushButton_save, &QPushButton::clicked, this, &GeneralSettingWidget::onSave);
}

GeneralSettingWidget::~GeneralSettingWidget()
{}

void GeneralSettingWidget::setGeneralMgr(GeneralMgr* mgr)
{
	m_generalMgr = mgr;
	if (m_generalMgr)
		ui.lineEdit_logPath->setText(m_generalMgr->logPath());
}

void GeneralSettingWidget::onChoseDir()
{
	QString dir = QFileDialog::getExistingDirectory(this, QStringLiteral(""), ui.lineEdit_logPath->text());
	if (!dir.isEmpty())
		ui.lineEdit_logPath->setText(dir);
}

void GeneralSettingWidget::onSave()
{
	if (!m_generalMgr) return;
	m_generalMgr->setLogPath(ui.lineEdit_logPath->text());
	m_generalMgr->saveGeneralConfig();
}

