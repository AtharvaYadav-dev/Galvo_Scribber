#include "SettingsWidget.h"

SettingsWidget::SettingsWidget(QWidget* parent)
    : QWidget(parent)
{
    ui.setupUi(this);
    ui.listWidget->setCurrentRow(0);
    connect(ui.listWidget, &QListWidget::currentRowChanged, ui.stackedWidget, &QStackedWidget::setCurrentIndex);
}

SettingsWidget::~SettingsWidget() {}

int SettingsWidget::addPage(const QString& name, QWidget* page)
{
    ui.listWidget->addItem(name);
    int index = ui.stackedWidget->addWidget(page);
    return index;
}

void SettingsWidget::setPage(int index, QWidget* page)
{
    QWidget* old = ui.stackedWidget->widget(index);
    if (old) {
        ui.stackedWidget->removeWidget(old);
        old->deleteLater();
    }
    ui.stackedWidget->insertWidget(index, page);
}

QWidget* SettingsWidget::pageWidget(int index) const
{
    return ui.stackedWidget->widget(index);
}

int SettingsWidget::currentIndex() const
{
    return ui.stackedWidget->currentIndex();
}
