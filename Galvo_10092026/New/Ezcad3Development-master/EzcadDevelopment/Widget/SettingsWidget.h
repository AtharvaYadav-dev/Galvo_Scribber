#pragma once

#include <QWidget>
#include "ui_SettingsWidget.h"

class SettingsWidget : public QWidget
{
    Q_OBJECT

public:
    SettingsWidget(QWidget* parent = nullptr);
    ~SettingsWidget();

    int  addPage(const QString& name, QWidget* page);
    void setPage(int index, QWidget* page);
    QWidget* pageWidget(int index) const;
    int  currentIndex() const;

private:
    Ui::CSettingsWidgetClass ui;
};

