#include <QTimer>
#include <QStyledItemDelegate>
#include <QInputDialog>

#include "IOWidget.h"

class StatusDelegate : public QStyledItemDelegate
{
public:
    using QStyledItemDelegate::QStyledItemDelegate;
    void initStyleOption(QStyleOptionViewItem* option,
        const QModelIndex& index) const override
    {
        QStyledItemDelegate::initStyleOption(option, index);
        option->state &= ~QStyle::State_Selected;
    }
};

IOWidget::IOWidget(QWidget* parent, GtsMgr* mgr)
    : QWidget(parent)
    , m_gtsMgr(mgr)
{
    ui.setupUi(this);
    InitUI();
    connectPrivateSignal();
}

IOWidget::~IOWidget()
{
    m_gtsMgr = nullptr;
}

void IOWidget::setGtsTotalMgr(GtsMgr* mgr)
{
    m_gtsMgr = mgr;
}

void IOWidget::InitUI()
{
    QTimer::singleShot(0, this, [this]() {
        InitTableDI();
        InitTableDO();
        });
}

static void InitTableCommon(QTableWidget* table, int totalRows,
    ConfigMgr* cfgMgr, bool isDI)
{
    table->setColumnCount(3);
    table->setHorizontalHeaderLabels({
        QStringLiteral("功能描述"),
        QStringLiteral("序号"),
        QStringLiteral("状态")
        });
    table->verticalHeader()->setVisible(false);
    table->setRowCount(totalRows);

    for (int i = 0; i < totalRows; ++i) {
        QString desc = cfgMgr
            ? (isDI ? cfgMgr->getDIDescription(i) : cfgMgr->getDODescription(i))
            : QString();

        table->setItem(i, 0, new QTableWidgetItem(desc));

        auto* idxItem = new QTableWidgetItem(QString::number((i % 8) + 1));
        idxItem->setTextAlignment(Qt::AlignCenter);
        table->setItem(i, 1, idxItem);

        auto* stsItem = new QTableWidgetItem(QStringLiteral("● 关"));
        stsItem->setTextAlignment(Qt::AlignCenter);
        table->setItem(i, 2, stsItem);
    }

    table->horizontalHeader()->setSectionResizeMode(0, QHeaderView::Stretch);
    table->horizontalHeader()->setSectionResizeMode(1, QHeaderView::Fixed);
    table->horizontalHeader()->setSectionResizeMode(2, QHeaderView::Fixed);
    table->setColumnWidth(1, 60);
    table->setColumnWidth(2, 90);
    table->setSelectionBehavior(QAbstractItemView::SelectRows);
    table->setEditTriggers(QAbstractItemView::NoEditTriggers);
    table->setStyleSheet(
        QStringLiteral(
            "QTableWidget::item:selected { background: rgba(0,160,0,40); color: inherit; }"
        ));
    table->setItemDelegateForColumn(2, new StatusDelegate(table));
}

void IOWidget::InitTableDI()
{
    ConfigMgr* cfg = m_gtsMgr ? m_gtsMgr->configMgr() : nullptr;
    InitTableCommon(ui.tableWidget_DI, 63, cfg, /*isDI=*/true);
}

void IOWidget::InitTableDO()
{
    ConfigMgr* cfg = m_gtsMgr ? m_gtsMgr->configMgr() : nullptr;
    InitTableCommon(ui.tableWidget_DO, 32, cfg, /*isDI=*/false);
}


void IOWidget::connectPrivateSignal()
{
    connect(ui.tableWidget_DO, &QTableWidget::cellClicked,
        this, &IOWidget::onDOCellClicked);

    connect(ui.tableWidget_DI, &QTableWidget::cellDoubleClicked,
        this, &IOWidget::onDICellDoubleClicked);
    connect(ui.tableWidget_DO, &QTableWidget::cellDoubleClicked,
        this, &IOWidget::onDOCellDoubleClicked);
}

void IOWidget::RefreshTable(QTableWidget* table, const std::vector<int>& status)
{
    for (int i = 0; i < (int)status.size(); ++i) {
        QTableWidgetItem* item = table->item(i, 2);
        if (!item) continue;
        if (status[i]) {
            item->setText(QStringLiteral("● 开"));
            item->setBackground(Qt::green);
        }
        else {
            item->setText(QStringLiteral("● 关"));
            item->setBackground(Qt::white);
        }
    }
}

void IOWidget::onDOCellClicked(int row, int col)
{
    if (col != 2) return;
    if (!m_gtsMgr) return;
    auto* ioMgr = m_gtsMgr->ioMgr();
    if (!ioMgr) return;

    if (row >= 0 && row < 8) {
        m_doState.servoOn[row] ^= 1;
        ioMgr->setMotorEnableDO(m_doState.servoOn);
    }
    else if (row >= 8 && row < 16) {
        int idx = row - 8;
        m_doState.almClear[idx] ^= 1;
        ioMgr->setClearAlarmDO(m_doState.almClear);
    }
    else if (row >= 16 && row < 32) {
        int idx = row - 16;
        m_doState.GPO[idx] ^= 1;
        ioMgr->setGPO(m_doState.GPO);
    }

    auto flat = m_doState.toFlatVector();
    QTableWidgetItem* item = ui.tableWidget_DO->item(row, 2);
    if (item) {
        if (flat[row]) {
            item->setText(QStringLiteral("● 开"));
            item->setBackground(Qt::green);
        }
        else {
            item->setText(QStringLiteral("● 关"));
            item->setBackground(Qt::white);
        }
    }
}

void IOWidget::onDIUpdated(const DI& di)
{
    RefreshTable(ui.tableWidget_DI, di.toFlatVector());
}

void IOWidget::onDOUpdated(const DO& dout)
{
    m_doState = dout;
    RefreshTable(ui.tableWidget_DO, dout.toFlatVector());
}

void IOWidget::onDICellDoubleClicked(int row, int col)
{
    if (col == 0)
        onDescriptionEdited(row, true);
}

void IOWidget::onDOCellDoubleClicked(int row, int col)
{
    if (col == 0)
        onDescriptionEdited(row, false);
}

void IOWidget::onDescriptionEdited(int row, bool isDI)
{
    QTableWidget* table = isDI ? ui.tableWidget_DI : ui.tableWidget_DO;
    QTableWidgetItem* item = table->item(row, 0);
    if (!item) return;

    bool ok = false;
    QString newText = QInputDialog::getText(
        this,
        QStringLiteral("编辑功能描述"),
        QStringLiteral("请输入新的描述:"),
        QLineEdit::Normal,
        item->text(),
        &ok);

    if (!ok || newText.isEmpty() || newText == item->text())
        return;

    item->setText(newText);
    if (m_gtsMgr)
        m_gtsMgr->configMgr()->setIODescription(row, newText, isDI);
}

void IOWidget::onConfigReloaded()
{
    ConfigMgr* cfg = m_gtsMgr ? m_gtsMgr->configMgr() : nullptr;
    if (!cfg) return;

    // 只刷新描述列
    for (int i = 0; i < ui.tableWidget_DI->rowCount(); ++i) {
        QTableWidgetItem* item = ui.tableWidget_DI->item(i, 0);
        if (item) item->setText(cfg->getDIDescription(i));
    }
    for (int i = 0; i < ui.tableWidget_DO->rowCount(); ++i) {
        QTableWidgetItem* item = ui.tableWidget_DO->item(i, 0);
        if (item) item->setText(cfg->getDODescription(i));
    }
}
