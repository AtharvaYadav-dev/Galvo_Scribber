#include <QFileDialog>
#include <QDebug>

#include "GtsHal.h"
#include "GtsSettingWidget.h"
#include "../../GtsCore/GtsMgr.h"


GtsSettingWidget::GtsSettingWidget(QWidget* parent, GtsMgr* mgr)
    : QWidget(parent)
    , m_gtsMgr(mgr)
{
    ui.setupUi(this);

    QTimer::singleShot(100, this, [this]() {
        initUI();
        connectSignals();
        });

    if (mgr) {
        setGtsTotalMgr(mgr);
    }
}

GtsSettingWidget::~GtsSettingWidget()
{
    m_gtsMgr = nullptr;
}

void GtsSettingWidget::setGtsTotalMgr(GtsMgr* mgr)
{
    m_gtsMgr = mgr;
    if (mgr) {
        // 设置mgr同时链接信号和槽
        connect(mgr, &GtsMgr::configChanged, this, &GtsSettingWidget::onConfigChanged);
    }
}

void GtsSettingWidget::initUI()
{
    comboAddNumbers(ui.comboBox_axisId, 4);
    comboAddNumbers(ui.comboBox_dacId, 4);
    comboAddNumbers(ui.comboBox_controlId, 4);
    comboAddNumbers(ui.comboBox_profileId, 4);

    comboAddItems(ui.comboBox_controlMode, {
        QStringLiteral("闭环"),
        QStringLiteral("开环"),
        QStringLiteral("调试")
        });

    comboAddItems(ui.comboBox_homeMode, {
        QStringLiteral("负限位回零"),
        QStringLiteral("正限位回零"),
        QStringLiteral("原点回零"),
        QStringLiteral("原点+Index回零"),
        QStringLiteral("Index回零")
        });

    comboAddItems(ui.comboBox_gtsMode, {
        QStringLiteral("正常模式"),
        QStringLiteral("调试模式"),
        QStringLiteral("无板卡模式")
        });

    comboAddNumbers(ui.comboBox_axisIdHomeConfig, 4);

    comboAddItems(ui.comboBox_axisName, {
        QStringLiteral("X"), QStringLiteral("Y"),
        QStringLiteral("Z"), QStringLiteral("A"),
        });
}


void GtsSettingWidget::connectSignals()
{
    // 按钮
    connect(ui.pushButton_loadToBoard, &QPushButton::clicked, this, &GtsSettingWidget::onLoadConfigFile);
    connect(ui.pushButton_save, &QPushButton::clicked, this, &GtsSettingWidget::onApplyAndSave);
    connect(ui.pushButton_applyToBoard, &QPushButton::clicked, this, &GtsSettingWidget::onApplyToBoard);

    // DAC 通道切换
    connect(ui.comboBox_dacId, QOverload<int>::of(&QComboBox::currentIndexChanged), this, [this]() {
        short newId = ui.comboBox_dacId->currentText().toShort();
        if (m_prevDacId != newId && m_gtsMgr) {
            commitDacForAxis(m_prevDacId);
            m_prevDacId = newId;
        }
        refreshDacValues();
        });

    // 控制轴切换
    connect(ui.comboBox_controlId, QOverload<int>::of(&QComboBox::currentIndexChanged), this, [this]() {
        short newId = ui.comboBox_controlId->currentText().toShort();
        if (m_prevCtrlId != newId && m_gtsMgr) {
            commitFollowErrorForAxis(m_prevCtrlId);
            m_prevCtrlId = newId;
        }
        refreshFollowErrorLimit();
        });

    // Profile 切换(停止减速度)
    connect(ui.comboBox_profileId, QOverload<int>::of(&QComboBox::currentIndexChanged), this, [this]() {
        short newId = ui.comboBox_profileId->currentText().toShort();
        if (m_prevProfileId != newId && m_gtsMgr) {
            commitStopDecelForProfile(m_prevProfileId);
            m_prevProfileId = newId;
        }
        refreshStopDecel();
        });

    // 轴切换(Scale / ControlMode / AxisLimit 共用 comboBox_axisId)
    connect(ui.comboBox_axisId, QOverload<int>::of(&QComboBox::currentIndexChanged), this, [this]() {
        short newId = ui.comboBox_axisId->currentText().toShort();
        if (m_prevAxisId != newId && m_gtsMgr) {
            commitScaleForAxis(m_prevAxisId);
            commitControlModeForAxis(m_prevAxisId);
            commitAxisLimitForAxis(m_prevAxisId);
            m_prevAxisId = newId;
        }
        refreshScaleValues();
        refreshControlMode();
        refreshAxisLimit();
        refreshAxisName();
        refreshSoftPulseScale();
    });

    // 回零轴切换
    connect(ui.comboBox_axisIdHomeConfig, QOverload<int>::of(&QComboBox::currentIndexChanged), this, [this]() {
        short newId = ui.comboBox_axisIdHomeConfig->currentText().toShort();
        if (m_prevHomeAxisId != newId && m_gtsMgr) {
            commitHomeForAxis(m_prevHomeAxisId);
            m_prevHomeAxisId = newId;
        }
        refreshHomeConfig();
    });

    // 轴名切换
    connect(ui.comboBox_axisName, QOverload<int>::of(&QComboBox::currentIndexChanged), this, [this]() {
        if (m_refreshing) return;
        short axis = ui.comboBox_axisId->currentText().toShort();
        commitAxisNameForAxis(axis);
    });
}


void GtsSettingWidget::onLoadConfigFile()
{
    QString filePath = QFileDialog::getOpenFileName(this,
        QStringLiteral("选择配置文件"), QString(),
        QStringLiteral("配置文件 (*.cfg *.CFG);;所有文件 (*.*)"));
    if (filePath.isEmpty()) return;

    m_gtsMgr->configMgr()->loadConfigFile(filePath);
}

void GtsSettingWidget::onConfigChanged()
{
    if (m_refreshing) return;
    refreshDacValues();
    refreshFollowErrorLimit();
    refreshStopDecel();
    refreshScaleValues();
    refreshControlMode();
    refreshHomeConfig();
    refreshAxisLimit();
    refreshAxisName();
    refreshSoftPulseScale();
}


void GtsSettingWidget::onApplyAndSave()
{
    if (!m_gtsMgr) return;

    // 当前视图 → ConfigMgr 内存
    commitDacForAxis(ui.comboBox_dacId->currentText().toShort());
    commitFollowErrorForAxis(ui.comboBox_controlId->currentText().toShort());
    commitStopDecelForProfile(ui.comboBox_profileId->currentText().toShort());
    commitScaleForAxis(ui.comboBox_axisId->currentText().toShort());
    commitControlModeForAxis(ui.comboBox_axisId->currentText().toShort());
    commitAxisLimitForAxis(ui.comboBox_axisId->currentText().toShort());
    commitAxisNameForAxis(ui.comboBox_axisId->currentText().toShort());
    commitSoftPulseScaleForAxis(ui.comboBox_axisId->currentText().toShort());
    commitHomeForAxis(ui.comboBox_axisIdHomeConfig->currentText().toShort());

    // 内存 → JSON 文件
    m_gtsMgr->configMgr()->saveAxisConfig();
}

void GtsSettingWidget::onApplyToBoard()
{
    if (!m_gtsMgr) return;
    if (!m_gtsMgr->boardMgr()->isOpen()) return;

    // 先把当前视图提交到内存
    commitDacForAxis(ui.comboBox_dacId->currentText().toShort());
    commitFollowErrorForAxis(ui.comboBox_controlId->currentText().toShort());
    commitStopDecelForProfile(ui.comboBox_profileId->currentText().toShort());
    commitScaleForAxis(ui.comboBox_axisId->currentText().toShort());
    commitControlModeForAxis(ui.comboBox_axisId->currentText().toShort());
    commitAxisLimitForAxis(ui.comboBox_axisId->currentText().toShort());
    commitAxisNameForAxis(ui.comboBox_axisId->currentText().toShort());
    commitSoftPulseScaleForAxis(ui.comboBox_axisId->currentText().toShort());
    commitHomeForAxis(ui.comboBox_axisIdHomeConfig->currentText().toShort());

    // 内存 → 板卡
    m_gtsMgr->configMgr()->applyAllAxisConfigToBoard();
}


void GtsSettingWidget::refreshDacValues()
{
    if (m_refreshing) return;
    if (!m_gtsMgr) return;
    m_refreshing = true;
    short dac = ui.comboBox_dacId->currentText().toShort();
    ui.spinBox_zeroOffsetCompensation->setValue((int)m_gtsMgr->configMgr()->dacBias(dac));
    ui.spinBox_outputVoltageSaturationLimit->setValue((int)m_gtsMgr->configMgr()->dacLimit(dac));
    m_refreshing = false;
}

void GtsSettingWidget::refreshFollowErrorLimit()
{
    if (m_refreshing) return;
    if (!m_gtsMgr) return;
    m_refreshing = true;
    short ctrl = ui.comboBox_controlId->currentText().toShort();
    ui.spinBox_followingErrorLimit->setValue((int)m_gtsMgr->configMgr()->followErrorLimit(ctrl));
    m_refreshing = false;
}

void GtsSettingWidget::refreshStopDecel()
{
    if (m_refreshing) return;
    if (!m_gtsMgr) return;
    m_refreshing = true;
    short profile = ui.comboBox_profileId->currentText().toShort();
    ui.doubleSpinBox_smoothStopDec->setValue(m_gtsMgr->configMgr()->smoothStopDec(profile));
    ui.doubleSpinBox_smoothStopDec_2->setValue(m_gtsMgr->configMgr()->estopDec(profile));
    m_refreshing = false;
}

void GtsSettingWidget::refreshScaleValues()
{
    if (m_refreshing) return;
    if (!m_gtsMgr) return;
    m_refreshing = true;
    short axis = ui.comboBox_axisId->currentText().toShort();
    ui.spinBox_prfAlpha->setValue((int)m_gtsMgr->configMgr()->profileScaleAlpha(axis));
    ui.spinBox_prfBeta->setValue((int)m_gtsMgr->configMgr()->profileScaleBeta(axis));
    ui.spinBox_encAlpha->setValue((int)m_gtsMgr->configMgr()->encoderScaleAlpha(axis));
    ui.spinBox_encBeta->setValue((int)m_gtsMgr->configMgr()->encoderScaleBeta(axis));
    m_refreshing = false;
}

void GtsSettingWidget::refreshControlMode()
{
    if (m_refreshing) return;
    if (!m_gtsMgr) return;
    m_refreshing = true;
    short axis = ui.comboBox_axisId->currentText().toShort();
    int  mode = static_cast<int>(m_gtsMgr->configMgr()->controlMode(axis));
    ui.comboBox_controlMode->setCurrentIndex(mode);
    m_refreshing = false;
}

void GtsSettingWidget::refreshHomeConfig()
{
    if (m_refreshing) return;
    if (!m_gtsMgr) return;
    m_refreshing = true;
    short axis = ui.comboBox_axisIdHomeConfig->currentText().toShort();
    int mode = static_cast<int>(m_gtsMgr->configMgr()->homeModeValue(axis));
    ui.comboBox_homeMode->setCurrentIndex(mode);
    ui.doubleSpinBox_homeVel->setValue(m_gtsMgr->configMgr()->homeVel(axis));
    ui.doubleSpinBox_homeAcc->setValue(m_gtsMgr->configMgr()->homeAcc(axis));
    ui.doubleSpinBox_homeRange->setValue(m_gtsMgr->configMgr()->homeRange(axis));
    ui.doubleSpinBox_homeOffset->setValue(m_gtsMgr->configMgr()->homeOffset(axis));
    m_refreshing = false;
}

void GtsSettingWidget::refreshAxisLimit()
{
    if (m_refreshing) return;
    if (!m_gtsMgr) return;
    m_refreshing = true;
    short axis = ui.comboBox_axisId->currentText().toShort();
    ui.spinBox_pLimit->setValue((int)m_gtsMgr->configMgr()->posLimit(axis));
    ui.spinBox_nLimit->setValue((int)m_gtsMgr->configMgr()->negLimit(axis));
    m_refreshing = false;
}


void GtsSettingWidget::commitDacForAxis(short dac)
{
    auto* cfg = m_gtsMgr->configMgr();
    cfg->blockSignals(true);
    cfg->setDacBias(dac, (short)ui.spinBox_zeroOffsetCompensation->value());
    cfg->setDacLimit(dac, (short)ui.spinBox_outputVoltageSaturationLimit->value());
    cfg->blockSignals(false);
}

void GtsSettingWidget::commitFollowErrorForAxis(short ctrl)
{
    auto* cfg = m_gtsMgr->configMgr();
    cfg->blockSignals(true);
    cfg->setFollowErrorLimit(ctrl, ui.spinBox_followingErrorLimit->value());
    cfg->blockSignals(false);
}

void GtsSettingWidget::commitStopDecelForProfile(short profile)
{
    auto* cfg = m_gtsMgr->configMgr();
    cfg->blockSignals(true);
    cfg->setStopDecel(profile,
        ui.doubleSpinBox_smoothStopDec->value(),
        ui.doubleSpinBox_smoothStopDec_2->value());
    cfg->blockSignals(false);
}

void GtsSettingWidget::commitScaleForAxis(short axis)
{
    auto* cfg = m_gtsMgr->configMgr();
    cfg->blockSignals(true);
    cfg->setProfileScale(axis,
        ui.spinBox_prfAlpha->value(),
        ui.spinBox_prfBeta->value());
    cfg->setEncoderScale(axis,
        ui.spinBox_encAlpha->value(),
        ui.spinBox_encBeta->value());
    cfg->blockSignals(false);
}

void GtsSettingWidget::commitControlModeForAxis(short axis)
{
    auto* cfg = m_gtsMgr->configMgr();
    cfg->blockSignals(true);
    cfg->setControlMode(axis, static_cast<ControlMode>(ui.comboBox_controlMode->currentIndex()));
    cfg->blockSignals(false);
}

void GtsSettingWidget::commitHomeForAxis(short axis)
{
    auto* cfg = m_gtsMgr->configMgr();
    cfg->blockSignals(true);
    cfg->setHomeMode(axis, static_cast<HomeMode>(ui.comboBox_homeMode->currentIndex()));
    cfg->setHomeVel(axis, ui.doubleSpinBox_homeVel->value());
    cfg->setHomeAcc(axis, ui.doubleSpinBox_homeAcc->value());
    cfg->setHomeRange(axis, ui.doubleSpinBox_homeRange->value());
    cfg->setHomeOffset(axis, ui.doubleSpinBox_homeOffset->value());
    cfg->blockSignals(false);
}

void GtsSettingWidget::commitAxisLimitForAxis(short axis)
{
    auto* cfg = m_gtsMgr->configMgr();
    cfg->blockSignals(true);
    cfg->setPosLimit(axis, ui.spinBox_pLimit->value());
    cfg->setNegLimit(axis, ui.spinBox_nLimit->value());
    cfg->blockSignals(false);
}

void GtsSettingWidget::refreshAxisName()
{
    if (m_refreshing) return;
    if (!m_gtsMgr) return;
    m_refreshing = true;
    short axis = ui.comboBox_axisId->currentText().toShort();
    int idx = static_cast<int>(m_gtsMgr->configMgr()->axisName(axis));
    ui.comboBox_axisName->setCurrentIndex(idx);
    m_refreshing = false;
}

void GtsSettingWidget::commitAxisNameForAxis(short axis)
{
    auto* cfg = m_gtsMgr->configMgr();
    cfg->blockSignals(true);
    int idx = ui.comboBox_axisName->currentIndex();
    if (idx >= 0 && idx <= 3)
        cfg->setAxisName(axis, static_cast<AxisName>(idx));
    cfg->blockSignals(false);
}

void GtsSettingWidget::refreshSoftPulseScale()
{
    if (m_refreshing) return;
    if (!m_gtsMgr) return;
    m_refreshing = true;
    short axis = ui.comboBox_axisId->currentText().toShort();
    ui.spinBox_pluseAlpha->setValue((int)m_gtsMgr->configMgr()->softPulseAlpha(axis));
    ui.spinBox_pluseBeta->setValue((int)m_gtsMgr->configMgr()->softPulseBeta(axis));
    m_refreshing = false;
}

void GtsSettingWidget::commitSoftPulseScaleForAxis(short axis)
{
    auto* cfg = m_gtsMgr->configMgr();
    cfg->blockSignals(true);
    cfg->setSoftPulseScale(axis,
        ui.spinBox_pluseAlpha->value(),
        ui.spinBox_pluseBeta->value());
    cfg->blockSignals(false);
}