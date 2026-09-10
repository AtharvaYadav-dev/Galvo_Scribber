#include <QTimer>
#include <QPushButton>
#include <QFont>

#include "AxisControlWidget.h"

AxisControlWidget::AxisControlWidget(QWidget* parent)
    : QWidget(parent)
{
    ui.setupUi(this);
    initWidget();
    initConnections();
    updateBoardState(false);
}

AxisControlWidget::~AxisControlWidget()
{
    m_gtsMgr = nullptr;
}


void AxisControlWidget::setGtsTotalMgr(GtsMgr* mgr)
{
    if (m_gtsMgr) 
    {
        disconnect(m_gtsMgr, &GtsMgr::boardClockUpdated, this, &AxisControlWidget::onBoardClockUpdated);
        disconnect(m_gtsMgr, &GtsMgr::axisUpdated, this, &AxisControlWidget::onAxisUpdated);
        disconnect(m_gtsMgr, &GtsMgr::axisSettingUpdated, this, &AxisControlWidget::onAxisSettingUpdated);
    }
    m_gtsMgr = mgr;
    if (m_gtsMgr) 
    {
        connect(m_gtsMgr, &GtsMgr::boardClockUpdated, this, &AxisControlWidget::onBoardClockUpdated);
        connect(m_gtsMgr, &GtsMgr::axisUpdated, this, &AxisControlWidget::onAxisUpdated);
        connect(m_gtsMgr, &GtsMgr::axisSettingUpdated, this, &AxisControlWidget::onAxisSettingUpdated);
    }
}


void AxisControlWidget::initWidget()
{
    // 轴号下拉
    ui.comboBox_axisID->addItem(QStringLiteral("轴 1"));
    ui.comboBox_axisID->addItem(QStringLiteral("轴 2"));
    ui.comboBox_axisID->addItem(QStringLiteral("轴 3"));
    ui.comboBox_axisID->addItem(QStringLiteral("轴 4"));

    // 运动模式下拉
    ui.comboBox_Mode->addItem(QStringLiteral("点位运动(trap)"));
    ui.comboBox_Mode->addItem(QStringLiteral("Jog运动"));

    // RadioButton 禁用互斥,且禁止用户点击
    const QList<QRadioButton*> stateRadios = {
        ui.radioButton_servoEnable, ui.radioButton_sevorAlarm,
        ui.radioButton_nLimit,       ui.radioButton_pLimit,
        ui.radioButton_motionErr,    ui.radioButton_motionSts,
        ui.radioButton_eStop,        ui.radioButton_smoothStop,
    };
    for (QRadioButton* rb : stateRadios) {
        rb->setAutoExclusive(false);
        rb->setAttribute(Qt::WA_TransparentForMouseEvents, true);
    }

    // 等宽字体防止数据刷新时布局抖动
    const QList<QLabel*> numLabels = {
        ui.label_actPosData,      
        ui.label_actVelData,
        ui.label_tgtPosData,      
        ui.label_tgtVelData,
        ui.label_tgtAccData,
        ui.label_tgtPosDataPluse, 
        ui.label_tgtVelDataPluse,
        ui.label_tgtAccDataPluse,
    };

    QFont monoFont(QStringLiteral("Consolas"), 9);
    for (QLabel* lb : numLabels) {
        lb->setFont(monoFont);
        lb->setAlignment(Qt::AlignRight | Qt::AlignVCenter);
    }
}

void AxisControlWidget::initConnections()
{
    // Board 指示灯不可点击
    ui.radioButton_boardState->setAttribute(Qt::WA_TransparentForMouseEvents, true);

    QTimer::singleShot(0, this, [this]() {
        // 板卡按钮
        connect(ui.pushButton_openBoard, &QPushButton::clicked, this, &AxisControlWidget::onBtnClick);
        connect(ui.pushButton_closeBoard, &QPushButton::clicked, this, &AxisControlWidget::onBtnClick);
        connect(ui.pushButton_resetBoard, &QPushButton::clicked, this, &AxisControlWidget::onBtnClick);

        // 轴操作按钮
        connect(ui.pushButton_clearState, &QPushButton::clicked, this, &AxisControlWidget::onBtnClick);
        connect(ui.pushButton_sevorOn, &QPushButton::clicked, this, &AxisControlWidget::onBtnClick);
        connect(ui.pushButton_clearPos, &QPushButton::clicked, this, &AxisControlWidget::onBtnClick);
        connect(ui.pushButton_smoothStop, &QPushButton::clicked, this, &AxisControlWidget::onBtnClick);
        connect(ui.pushButton_eStop, &QPushButton::clicked, this, &AxisControlWidget::onBtnClick);
        connect(ui.pushButton_TarpActMotion, &QPushButton::clicked, this, &AxisControlWidget::onBtnClick);

        // Jog 按下/释放
        connect(ui.pushButton_jogPMotion, &QPushButton::pressed, this, [this]() { onJogPressed(1); });
        connect(ui.pushButton_jogPMotion, &QPushButton::released, this, [this]() { onJogReleased(); });
        connect(ui.pushButton_jogNMotion, &QPushButton::pressed, this, [this]() { onJogPressed(-1); });
        connect(ui.pushButton_jogNMotion, &QPushButton::released, this, [this]() { onJogReleased(); });

        // 下拉框
        connect(ui.comboBox_axisID, QOverload<int>::of(&QComboBox::currentIndexChanged),
            this, &AxisControlWidget::onComboBoxCurrentIndexChanged);
        connect(ui.comboBox_Mode, QOverload<int>::of(&QComboBox::currentIndexChanged),
            this, &AxisControlWidget::onComboBoxModeCurrentIndexChanged);

        // Trap 参数修改
        connect(ui.doubleSpinBox_trapMotionVel, &QSpinBox::editingFinished, this, &AxisControlWidget::onTrapParamChanged);
        connect(ui.doubleSpinBoxs_trapAcc, &QDoubleSpinBox::editingFinished, this, &AxisControlWidget::onTrapParamChanged);
        connect(ui.doubleSpinBoxs_trapDec, &QDoubleSpinBox::editingFinished, this, &AxisControlWidget::onTrapParamChanged);
        connect(ui.doubleSpinBox_trapLengthMm, &QDoubleSpinBox::editingFinished, this, &AxisControlWidget::onTrapParamChanged);
        connect(ui.spinBox_trapSmoothTime, &QSpinBox::editingFinished, this, &AxisControlWidget::onTrapParamChanged);
        connect(ui.spinBox_trapCycleTime, &QSpinBox::editingFinished, this, &AxisControlWidget::onTrapParamChanged);
        connect(ui.spinBox_TrapInPositionDelay, &QSpinBox::editingFinished, this, &AxisControlWidget::onTrapParamChanged);

        // Jog 参数修改
        connect(ui.doubleSpinBoxs_jogAcc, &QDoubleSpinBox::editingFinished, this, &AxisControlWidget::onJogParamChanged);
        connect(ui.doubleSpinBoxs_jogDec, &QDoubleSpinBox::editingFinished, this, &AxisControlWidget::onJogParamChanged);
        });
}

void AxisControlWidget::connectAxisSignals()
{
}


void AxisControlWidget::updateUIEnable(int index)
{
    if (index == 0) {
        // 点位运动
        ui.doubleSpinBox_jogVel->setEnabled(false);
        ui.doubleSpinBoxs_jogAcc->setEnabled(false);
        ui.doubleSpinBoxs_jogDec->setEnabled(false);
        ui.pushButton_jogPMotion->setEnabled(false);
        ui.pushButton_jogNMotion->setEnabled(false);

        ui.doubleSpinBox_trapMotionVel->setEnabled(true);
        ui.doubleSpinBoxs_trapAcc->setEnabled(true);
        ui.doubleSpinBoxs_trapDec->setEnabled(true);
        ui.doubleSpinBox_trapLengthMm->setEnabled(true);
        ui.spinBox_trapSmoothTime->setEnabled(true);
        ui.spinBox_trapCycleTime->setEnabled(true);
        ui.spinBox_TrapInPositionDelay->setEnabled(true);
        ui.pushButton_TarpActMotion->setEnabled(true);
    }
    else {
        // Jog 运动
        ui.doubleSpinBox_jogVel->setEnabled(true);
        ui.doubleSpinBoxs_jogAcc->setEnabled(true);
        ui.doubleSpinBoxs_jogDec->setEnabled(true);
        ui.pushButton_jogPMotion->setEnabled(true);
        ui.pushButton_jogNMotion->setEnabled(true);

        ui.doubleSpinBox_trapMotionVel->setEnabled(false);
        ui.doubleSpinBoxs_trapAcc->setEnabled(false);
        ui.doubleSpinBoxs_trapDec->setEnabled(false);
        ui.doubleSpinBox_trapLengthMm->setEnabled(false);
        ui.spinBox_trapSmoothTime->setEnabled(false);
        ui.spinBox_trapCycleTime->setEnabled(false);
        ui.spinBox_TrapInPositionDelay->setEnabled(false);
        ui.pushButton_TarpActMotion->setEnabled(false);
    }
}

// ==================== 板卡 ====================

void AxisControlWidget::updateBoardState(bool isOpen)
{
    ui.radioButton_boardState->setChecked(isOpen);
    if (isOpen) {
        ui.radioButton_boardState->setText(QStringLiteral("已打开"));
        ui.radioButton_boardState->setStyleSheet("QRadioButton { color: green; font-weight: bold; }");
    }
    else {
        ui.radioButton_boardState->setText(QStringLiteral("已关闭"));
        ui.radioButton_boardState->setStyleSheet("QRadioButton { color: red; }");
    }
}

void AxisControlWidget::onOpen()
{
    if (!m_gtsMgr) return;
    bool ok = m_gtsMgr->boardMgr()->open(0, 1);
    if (ok) {
        updateBoardState(true);
        short id = m_gtsMgr->boardMgr()->getCardNo();
        ui.label_boardIDData->setText(QString::number(id));
        QString fwVersion = m_gtsMgr->boardMgr()->firmwareVersion();
        ui.label_hardwareVerData->setText(fwVersion);
    }
}

void AxisControlWidget::onClose()
{
    if (!m_gtsMgr) return;
    bool ok = m_gtsMgr->boardMgr()->close();
    if (ok) updateBoardState(false);
}

void AxisControlWidget::onReset()
{
    if (!m_gtsMgr) return;
    bool ok = m_gtsMgr->boardMgr()->reset();
    if (ok) updateBoardState(false);
}


void AxisControlWidget::onClearState()
{
    if (!m_gtsMgr) return;
    m_gtsMgr->axisMgr()->clearStatus(m_axisId);
}

void AxisControlWidget::onServoOn()
{
    if (!m_gtsMgr) return;
    m_gtsMgr->axisMgr()->enable(m_axisId);
}

void AxisControlWidget::onServoOff()
{
    if (!m_gtsMgr) return;
    m_gtsMgr->axisMgr()->disable(m_axisId);
}

void AxisControlWidget::onClearPos()
{
    if (!m_gtsMgr) return;
    m_gtsMgr->axisMgr()->zeroPosition(m_axisId);
}

void AxisControlWidget::onSmoothStop()
{
    if (!m_gtsMgr) return;
    m_gtsMgr->axisMgr()->stop(m_axisId, 1);
}

void AxisControlWidget::onEStop()
{
    if (!m_gtsMgr) return;
    m_gtsMgr->axisMgr()->stop(m_axisId, 0);
}

void AxisControlWidget::onTrapMotion()
{
    if (!m_gtsMgr) return;
    int index = m_axisId - 1;
    if (index < 0 || index >= m_gtsMgr->axisCount()) return;

    m_gtsMgr->motionMgr()->trapMotion(m_axisId, m_gtsMgr->axisCfg()->axes[index].trapParam.lengthMm);
}

void AxisControlWidget::onJogPressed(int direction)
{
    if (!m_gtsMgr) return;
    int index = m_axisId - 1;

    bool ok = m_gtsMgr->motionMgr()->setJogParam(m_axisId, m_gtsMgr->axisCfg()->axes[index].jogParam);
    if (!ok) return;

    m_gtsMgr->motionMgr()->startJogMotion(m_axisId, direction);
}

void AxisControlWidget::onJogReleased()
{
    if (!m_gtsMgr) return;
    m_gtsMgr->axisMgr()->stop(m_axisId, 0);
}


void AxisControlWidget::onTrapParamChanged()
{
    if (m_updatingFromBoard) return;
    if (!m_gtsMgr) return;
    int index = m_axisId - 1;
    if (index < 0 || index >= m_gtsMgr->axisCount()) return;

    auto& tp = m_gtsMgr->axisCfg()->axes[index].trapParam;
    tp.motionVel = ui.doubleSpinBox_trapMotionVel->value();
    tp.acc = ui.doubleSpinBoxs_trapAcc->value();
    tp.dec = ui.doubleSpinBoxs_trapDec->value();
    tp.lengthMm = ui.doubleSpinBox_trapLengthMm->value();
    tp.somoothTime = ui.spinBox_trapSmoothTime->value();
    tp.cycleTimes = ui.spinBox_trapCycleTime->value();
    tp.delay = ui.spinBox_TrapInPositionDelay->value();
}

void AxisControlWidget::onJogParamChanged()
{
    if (m_updatingFromBoard) return;
    if (!m_gtsMgr) return;
    int index = m_axisId - 1;
    if (index < 0 || index >= m_gtsMgr->axisCount()) return;

    auto& jp = m_gtsMgr->axisCfg()->axes[index].jogParam;
    jp.motionVel = ui.doubleSpinBox_jogVel->value();
    jp.acc = ui.doubleSpinBoxs_jogAcc->value();
    jp.dec = ui.doubleSpinBoxs_jogDec->value();
}


void AxisControlWidget::onComboBoxCurrentIndexChanged(int index)
{
    m_axisId = index + 1;
    if (!m_gtsMgr || !m_gtsMgr->boardMgr()->isOpen()) return;

    const auto& tp = m_gtsMgr->axisCfg()->axes[index].trapParam;
    ui.doubleSpinBox_trapMotionVel->setValue(tp.motionVel);
    ui.doubleSpinBoxs_trapAcc->setValue(tp.acc);
    ui.doubleSpinBoxs_trapDec->setValue(tp.dec);
    ui.doubleSpinBox_trapLengthMm->setValue(tp.lengthMm);
    ui.spinBox_trapSmoothTime->setValue(tp.somoothTime);
    ui.spinBox_trapCycleTime->setValue(tp.cycleTimes);
    ui.spinBox_TrapInPositionDelay->setValue(tp.delay);

    // Jog 参数
    const auto& jp = m_gtsMgr->axisCfg()->axes[index].jogParam;
    ui.doubleSpinBox_jogVel->setValue(jp.motionVel);
    ui.doubleSpinBoxs_jogAcc->setValue(jp.acc);
    ui.doubleSpinBoxs_jogDec->setValue(jp.dec);

    // 运动模式
    ui.comboBox_Mode->setCurrentIndex(m_gtsMgr->getAxisRef(index)->prfMode);
}

void AxisControlWidget::onComboBoxModeCurrentIndexChanged(int index)
{
    if (!m_gtsMgr || !m_gtsMgr->boardMgr()->isOpen()) return;

    int axisIdx = m_axisId - 1;
    SingleAxisInfo* axis = m_gtsMgr->getAxisRef(axisIdx);
    if (!axis) return;

    bool ok = m_gtsMgr->motionMgr()->setAxisMotionMode(axis->axisIndex, index);
    if (ok) {
        updateUIEnable(index);
    }
}


void AxisControlWidget::onAxisUpdated(const std::vector<SingleAxisInfo>& axisInfo)
{
    m_updatingFromBoard = true;
    int index = m_axisId - 1;
    if (index < 0 || index >= (int)axisInfo.size()) return;
    const SingleAxisInfo& axis = axisInfo[index];

    // 状态指示灯
    ui.radioButton_servoEnable->setChecked(axis.isServoOn);
    ui.radioButton_nLimit->setChecked(axis.isNegLimit);
    ui.radioButton_pLimit->setChecked(axis.isPosLimit);
    ui.radioButton_motionErr->setChecked(axis.isMError);
    ui.radioButton_sevorAlarm->setChecked(axis.isAlarm);
    ui.radioButton_eStop->setChecked(axis.isAbruptStop);
    ui.radioButton_smoothStop->setChecked(axis.isSmoothStop);
    ui.radioButton_motionSts->setChecked(axis.isMotion);

    // 编码器数值
    ui.label_actPosData->setText(QString::number(axis.encPosMm, 'f', 3));
    ui.label_actVelData->setText(QString::number(axis.encVelMm, 'f', 3));

    // 规划器数值 (mm)
    ui.label_tgtPosData->setText(QString::number(axis.prfPosMm, 'f', 3));
    ui.label_tgtVelData->setText(QString::number(axis.prfVelMm, 'f', 3));
    ui.label_tgtAccData->setText(QString::number(axis.prfAccMm, 'f', 3));

    // 规划器数值 (pulse)
    ui.label_tgtPosDataPluse->setText(QString::number(axis.prfPosOriginal, 'f', 3));
    ui.label_tgtVelDataPluse->setText(QString::number(axis.prfVelOriginal, 'f', 3));
    ui.label_tgtAccDataPluse->setText(QString::number(axis.prfAccOriginal, 'f', 3));

    // 使能/失能按钮文字
    if (axis.isServoOn)
        ui.pushButton_sevorOn->setText(QStringLiteral("失能"));
    else
        ui.pushButton_sevorOn->setText(QStringLiteral("使能"));

    m_updatingFromBoard = false;
}

void AxisControlWidget::onAxisSettingUpdated(const std::vector<SingleAxisInfo>& axisInfo)
{
    m_updatingFromBoard = true;
    int index = m_axisId - 1;
    if (index < 0 || index >= (int)axisInfo.size()) return;
    const SingleAxisInfo& axis = axisInfo[index];

    ui.comboBox_Mode->setCurrentIndex(axis.prfMode);

    const auto& tp = m_gtsMgr->axisCfg()->axes[index].trapParam;
    ui.doubleSpinBox_trapMotionVel->setValue((int)tp.motionVel);
    ui.doubleSpinBox_trapLengthMm->setValue(tp.lengthMm);
    ui.doubleSpinBoxs_trapAcc->setValue(tp.acc);
    ui.doubleSpinBoxs_trapDec->setValue(tp.dec);
    ui.spinBox_trapSmoothTime->setValue(tp.somoothTime);
    ui.spinBox_trapCycleTime->setValue(tp.cycleTimes);
    ui.spinBox_TrapInPositionDelay->setValue(tp.delay);

    const auto& jp = m_gtsMgr->axisCfg()->axes[index].jogParam;
    ui.doubleSpinBox_jogVel->setValue(jp.motionVel);
    ui.doubleSpinBoxs_jogAcc->setValue(jp.acc);
    ui.doubleSpinBoxs_jogDec->setValue(jp.dec);

    updateUIEnable(ui.comboBox_Mode->currentIndex());
    m_updatingFromBoard = false;
}

// ==================== 时钟 ====================

void AxisControlWidget::onBoardClockUpdated(const Clock& clock)
{
    ui.label_clockData->setText(QString::number(clock.sysClock));
    ui.label_highPrecisionClockData->setText(QString::number(clock.highPrecClock));
}


void AxisControlWidget::onBtnClick()
{
    if (!m_gtsMgr) return;
    QPushButton* btn = qobject_cast<QPushButton*>(sender());
    if (!btn) return;

    QString objName = btn->objectName();

    if (objName == "pushButton_openBoard") {
        onOpen();
    }
    else if (objName == "pushButton_closeBoard") {
        onClose();
    }
    else if (objName == "pushButton_resetBoard") {
        onReset();
    }
    else if (objName == "pushButton_clearState") {
        onClearState();
    }
    else if (objName == "pushButton_sevorOn") {
        if (ui.pushButton_sevorOn->text() == QStringLiteral("使能"))
            onServoOn();
        else
            onServoOff();
    }
    else if (objName == "pushButton_clearPos") {
        onClearPos();
    }
    else if (objName == "pushButton_smoothStop") {
        onSmoothStop();
    }
    else if (objName == "pushButton_eStop") {
        onEStop();
    }
    else if (objName == "pushButton_TarpActMotion") {
        onTrapMotion();
    }
}
