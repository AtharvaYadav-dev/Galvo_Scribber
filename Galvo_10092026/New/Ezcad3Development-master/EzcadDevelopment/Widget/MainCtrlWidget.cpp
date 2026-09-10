#include <QMessageBox>

#include "MainCtrlWidget.h"

MainCtrlWidget::MainCtrlWidget(QWidget* parent)
    : QWidget(parent)
{
    ui.setupUi(this);

    for (short i = 0; i < 4; ++i)
        ui.comboBox_axisID->addItem(axisNameToString(static_cast<AxisName>(i)));
}

MainCtrlWidget::~MainCtrlWidget()
{
}


void MainCtrlWidget::initConnections()
{
    connect(ui.comboBox_axisID, QOverload<int>::of(&QComboBox::currentIndexChanged), this, [this](int index) { m_axisId = index + 1; });

    short idX = axisIdByName(AxisName::X);
    short idY = axisIdByName(AxisName::Y);
    short idZ = axisIdByName(AxisName::Z);

    // Jog X 轴
    connect(ui.toolButton_PlusX, &QToolButton::pressed, this, [this, idX]() { onJogPressed(idX, 1); });
    connect(ui.toolButton_PlusX, &QToolButton::released, this, [this, idX]() { onJogReleased(idX); });
    connect(ui.toolButton_MinusX, &QToolButton::pressed, this, [this, idX]() { onJogPressed(idX, -1); });
    connect(ui.toolButton_MinusX, &QToolButton::released, this, [this, idX]() { onJogReleased(idX); });

    // Jog Y 轴
    connect(ui.toolButton_PlusY, &QToolButton::pressed, this, [this, idY]() { onJogPressed(idY, 1); });
    connect(ui.toolButton_PlusY, &QToolButton::released, this, [this, idY]() { onJogReleased(idY); });
    connect(ui.toolButton_MinusY, &QToolButton::pressed, this, [this, idY]() { onJogPressed(idY, -1); });
    connect(ui.toolButton_MinusY, &QToolButton::released, this, [this, idY]() { onJogReleased(idY); });

    // Jog Z 轴
    connect(ui.toolButton_PlusZ, &QToolButton::pressed, this, [this, idZ]() { onJogPressed(idZ, 1); });
    connect(ui.toolButton_PlusZ, &QToolButton::released, this, [this, idZ]() { onJogReleased(idZ); });
    connect(ui.toolButton_MinusZ, &QToolButton::pressed, this, [this, idZ]() { onJogPressed(idZ, -1); });
    connect(ui.toolButton_MinusZ, &QToolButton::released, this, [this, idZ]() { onJogReleased(idZ); });

    // 停止全部
    connect(ui.toolButton_Stop, &QToolButton::clicked, this, &MainCtrlWidget::onStopAll);

    // 回零
    connect(ui.pushButtonHomeX, &QPushButton::clicked, this, [this, idX]() { onHome(idX); });
    connect(ui.pushButtonHomeY, &QPushButton::clicked, this, [this, idY]() { onHome(idY); });
    connect(ui.pushButtonHomeZ, &QPushButton::clicked, this, [this, idZ]() { onHome(idZ); });

    // 启动运动(点位移动)
    connect(ui.pushButton_ActMotion, &QPushButton::clicked, this, &MainCtrlWidget::onActMotion);
}


void MainCtrlWidget::setGtsTotalMgr(GtsMgr* mgr)
{
    if (m_gtsMgr) {
        disconnect(m_gtsMgr, &GtsMgr::axisUpdated, this, &MainCtrlWidget::onAxisUpdated);
    }
    m_gtsMgr = mgr;
    if (m_gtsMgr) {
        connect(m_gtsMgr, &GtsMgr::axisUpdated, this, &MainCtrlWidget::onAxisUpdated);
        connect(m_gtsMgr, &GtsMgr::configChanged, this, [this]() {
            if (!m_connectionsInitialized) {
                initConnections();
                m_connectionsInitialized = true;
            }
        });
    }
}


void MainCtrlWidget::onJogPressed(short axisId, int direction)
{
    if (!m_gtsMgr) return;

    int index = axisId - 1;

    auto& jp = m_gtsMgr->axisCfg()->axes[index].jogParam;
    bool ok = m_gtsMgr->motionMgr()->setJogParam(axisId, jp);
    if (!ok) return;

    m_gtsMgr->motionMgr()->startJogMotion(axisId, direction);
}

void MainCtrlWidget::onJogReleased(short axisId)
{
    if (!m_gtsMgr) return;
    m_gtsMgr->axisMgr()->stop(axisId, 0);
}

void MainCtrlWidget::onStopAll()
{
    if (!m_gtsMgr) return;
    for (short id = 1; id <= m_gtsMgr->axisCount(); ++id) {
        m_gtsMgr->axisMgr()->stop(id, 0);
    }
}


void MainCtrlWidget::onHome(short axisId)
{
    if (!m_gtsMgr) return;
    m_gtsMgr->motionMgr()->homeStart(axisId);
}


void MainCtrlWidget::onActMotion()
{
    if (!m_gtsMgr) return;

    int index = m_axisId - 1;

    auto& tp = m_gtsMgr->axisCfg()->axes[index].trapParam;
    tp.motionVel = ui.doubleSpinBox_Vel->value();
    tp.acc = ui.doubleSpinBoxs_Acc->value();
    tp.dec = ui.doubleSpinBoxs_Dec->value();
    tp.lengthMm = ui.spinBox_trapStepSize1->value();

    m_gtsMgr->motionMgr()->setTrapParam(m_axisId, tp);

    m_gtsMgr->motionMgr()->trapMotion(m_axisId, tp.lengthMm);
}


void MainCtrlWidget::onAxisUpdated(const std::vector<SingleAxisInfo>& axisInfo)
{
    auto updatePos = [&](AxisName name, QLabel* label) {
        short id = axisIdByName(name);
        if (id > 0 && id <= (short)axisInfo.size())
            label->setText(QString::number(axisInfo[id - 1].encPosMm, 'f', 1));
    };
    updatePos(AxisName::X, ui.label_actPosDataX);
    updatePos(AxisName::Y, ui.label_actPosDataY);
    updatePos(AxisName::Z, ui.label_actPosDataZ);
}

// ==================== 日志 ====================

void MainCtrlWidget::onErrMessage(int errorCode, const QString& message)
{
    QTextCursor cursor = ui.plainTextEdit_log->textCursor();
    cursor.movePosition(QTextCursor::End);
    QTextCharFormat charFormat;
    charFormat.setForeground(Qt::red);
    cursor.setCharFormat(charFormat);

    cursor.insertText(message + " errorCode = " + QString::number(errorCode) + "\n");
    ui.plainTextEdit_log->setTextCursor(cursor);
    ui.plainTextEdit_log->ensureCursorVisible();
}

void MainCtrlWidget::onLogMessage(const QString& msg, QColor color)
{
    QTextCursor cursor = ui.plainTextEdit_log->textCursor();
    cursor.movePosition(QTextCursor::End);
    QTextCharFormat charFormat;
    charFormat.setForeground(color);
    cursor.setCharFormat(charFormat);

    cursor.insertText(msg + "\n");
    ui.plainTextEdit_log->setTextCursor(cursor);
    ui.plainTextEdit_log->ensureCursorVisible();
}

short MainCtrlWidget::axisIdByName(AxisName name) const
{
    if (!m_gtsMgr) return 0;
    auto* cfg = m_gtsMgr->axisCfg();
    for (int i = 0; i < (int)cfg->axes.size(); ++i) {
        if (cfg->axes[i].name == name)
            return static_cast<short>(i + 1);
    }
    return 0;
}
