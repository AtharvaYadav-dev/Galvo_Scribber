#include "EzcadMgr.h"
#include "MarkWorker.h"
#include <QCoreApplication>
#include <QThread>
#include <QProcess>

EzcadMgr::EzcadMgr(QObject* parent)
    : QObject(parent)
    , m_ezdKernel(new EzdKernel(nullptr))
{
}

EzcadMgr::~EzcadMgr()
{
    if (m_marker != INVALID)
        m_ezdKernel->E3_CloseMarker(m_marker);
    if (m_EM != INVALID)
        m_ezdKernel->E3_FreeEntMgr(m_EM);
    m_ezdKernel->E3_Close();
    delete m_ezdKernel;
}

bool EzcadMgr::initialize(InitialMode mode)
{
    QString workPath = QCoreApplication::applicationDirPath();
    E3_ERR err = m_ezdKernel->Initial((TCHAR*)workPath.data(), mode, nullptr);

    if (err != E3_ERR::ERR_SUCCESS) {
        QString msg;
        switch (err) {
        case E3_ERR::ERR_CLIENTID:
            msg = QStringLiteral("License验证失败");
            break;
        case E3_ERR::ERR_EZCADRUN:
            msg = QStringLiteral("Ezcad软件正在运行,请先关闭");
            break;
        default:
            msg = QStringLiteral("初始化失败,错误码: %1").arg((int)err);
            break;
        }
        emit errorOccurred((int)err, msg);
        return false;
    }

    m_EM = m_ezdKernel->E3_CreateEntMgr(0);              // 创建对象管理器
    m_marker = m_ezdKernel->E3_MarkerGetFirstValidId();  // 获取有效板卡

    int nLayerIndex = -1;
    m_ezdKernel->E3_GetCurLayerId(m_EM, m_curLayer, nLayerIndex);

    emit logMessage(QStringLiteral("初始化成功"),Qt::darkGreen);
    return true;
}

bool EzcadMgr::createHelloWorld()
{
    Pt2d pt = Pt2d();
    pt.X = 0; pt.Y = 0;
    QString text = "HelloWorld";
    m_ezdKernel->E3_CreateText_2(
        m_EM, 0, pt, (TCHAR*)text.data(),
        0, 100, 0.5, 0, 1, 0, 0, 0, 0,
        false, false, false, false, m_Ent);
    emit entityChanged(m_curLayer);
    return true;
}


bool EzcadMgr::openFile(const QString& filePath)
{
    if (m_EM == INVALID) {
        emit errorOccurred(-1, QStringLiteral("EntMgr未初始化,请先调用 initialize()"));
        return false;
    }

    E3_ERR err = m_ezdKernel->E3_OpenFileToEntMgr(
        (TCHAR*)filePath.data(), m_EM, FALSE, FALSE);

    if (err != E3_ERR::ERR_SUCCESS) {
        emit errorOccurred((int)err, QStringLiteral("打开文件失败: %1").arg(filePath));
        return false;
    }

    // 重新获取当前层（文件导入后 layer 结构可能变化）
    int nCount = 0, nCurLayerIndex = 0;
    m_ezdKernel->E3_GetLayerCount(m_EM, nCount, nCurLayerIndex);
    m_ezdKernel->E3_GetLayerId(m_EM, 0, m_curLayer);

    emit logMessage(QStringLiteral("打开文件成功: %1").arg(filePath), Qt::darkGreen);
    emit entityChanged(m_curLayer);
    m_curFilePath = filePath;

    int nCalTime = getCalcMarkTime();
    emit logMessage(QStringLiteral("预估打标时间: %1 ms").arg(nCalTime), Qt::darkGreen);

    return true;
}

bool EzcadMgr::saveFile(const QString& filePath)
{
    if (m_EM == INVALID) {
        emit errorOccurred(-1, QStringLiteral("EntMgr未初始化,请先调用 initialize()"));
        return false;
    }

    E3_ERR err = m_ezdKernel->E3_SaveEntMgrToFile(
        (TCHAR*)filePath.data(),
        m_EM,
        false,
        false,
        (TCHAR*)QStringLiteral("").data(),
        (TCHAR*)QStringLiteral("").data(),
        (TCHAR*)QStringLiteral("").data());

    if (err != E3_ERR::ERR_SUCCESS) {
        emit errorOccurred((int)err, QStringLiteral("保存文件失败:%1").arg(filePath));
        return false;
    }

    emit logMessage(QStringLiteral("保存文件成功:%1").arg(filePath), Qt::darkGreen);
    return true;
}

// ==================== F3 参数接口实现 ====================

bool EzcadMgr::openF3ParamDialog()
{
    if (m_marker == INVALID) {
        emit errorOccurred(-1, QStringLiteral("板卡未初始化,请先调用 initialize()"));
        return false;
    }

    BOOL res = 0;
    m_ezdKernel->E3_MarkerDlgSetCfg(m_marker, res);
    return true;
}

int EzcadMgr::getF3ParamInt(int index) const
{
    if (m_marker == INVALID) {
        return 0;
    }
    int nParam = 0;
    m_ezdKernel->E3_MarkerGetCfgParamInt(m_marker, index, nParam);
    return nParam;
}

bool EzcadMgr::setF3ParamInt(int index, int value)
{
    if (m_marker == INVALID) {
        emit errorOccurred(-1, QStringLiteral("板卡未初始化"));
        return false;
    }
    m_ezdKernel->E3_MarkerSetCfgParamInt(m_marker, index, value);
    return true;
}

double EzcadMgr::getF3ParamDouble(int index) const
{
    if (m_marker == INVALID) {
        return 0.0;
    }
    double dParam = 0.0;
    m_ezdKernel->E3_MarkerGetCfgParamDouble(m_marker, index, dParam);
    return dParam;
}

bool EzcadMgr::setF3ParamDouble(int index, double value)
{
    if (m_marker == INVALID) {
        emit errorOccurred(-1, QStringLiteral("板卡未初始化"));
        return false;
    }
    m_ezdKernel->E3_MarkerSetCfgParamDouble(m_marker, index, value);
    return true;
}

bool EzcadMgr::setF3ParamString(int index, const QString& value)
{
    if (m_marker == INVALID) {
        emit errorOccurred(-1, QStringLiteral("板卡未初始化"));
        return false;
    }
    m_ezdKernel->E3_MarkerSetParamString(m_marker, index, (TCHAR*)value.data());
    return true;
}

bool EzcadMgr::updateF3Param()
{
    if (m_marker == INVALID) {
        emit errorOccurred(-1, QStringLiteral("板卡未初始化"));
        return false;
    }
    m_ezdKernel->E3_MarkerUpdateParam(m_marker, true);
    return true;
}

// ==================== 标刻接口实现 ====================

bool EzcadMgr::markStart(int markMode)
{
    if (m_marker == INVALID || m_EM == INVALID)
    {
        emit errorOccurred(-1, QStringLiteral("板卡未初始化,请先调用 initialize"));
        return false;
    }

    if (m_isMarking)
    {
        emit errorOccurred(-1, QStringLiteral("当前正在标刻中..."));
        return false;
    }

    if (m_curFilePath.isEmpty())
    {
        emit errorOccurred(-1, QStringLiteral("当前没有打开文件,请先打开文件"));
        return false;
    }
    m_isMarking = true;
    emit marking();
    // 创建worker对象
    MarkWorker* worker = new MarkWorker();
    // 注入参数
    worker->setKernel(m_ezdKernel);
    worker->setMarkerId(m_marker);
    worker->setEntMgrId(m_EM);
    worker->setCurLayerId(m_curLayer);
    worker->setMarkMode(markMode);
    // 将 worker 移动到线程中
    QThread* thread = new QThread(this);
    worker->moveToThread(thread);
    // 线程启动 → 执行标刻
    connect(thread, &QThread::started, worker, &MarkWorker::doWork);

    // 标刻完成 → 清理线程 + 通知上层和日志显示
    connect(worker, &MarkWorker::workFinished, this,
        [this, thread, worker](bool userStop)
        {
            m_isMarking = false;

            // 清理：退出线程事件循环并等待
            thread->quit();
            thread->wait();
            worker->deleteLater();
            thread->deleteLater();

            emit logMessage(QStringLiteral("完成..."), Qt::darkGreen);
            emit markFinished(userStop);
        });

    emit logMessage(QStringLiteral("标刻线程中..."), Qt::darkGreen);
    thread->start();
    return true;
}

bool EzcadMgr::mark()
{
    emit logMessage(QStringLiteral("标刻..."), Qt::darkGreen);
    return markStart(0);
}

bool EzcadMgr::markStop()
{
    if (m_marker == INVALID) return false;

    m_ezdKernel->E3_MarkerStop(m_marker);
    emit logMessage(QStringLiteral("标刻停止"), Qt::darkGreen);
    return true;
}

bool EzcadMgr::redLightPreview()
{
    // 红光预览
    emit logMessage(QStringLiteral("红光预览..."), Qt::darkGreen);
    return markStart(0x00000002);
}

int EzcadMgr::getCalcMarkTime()
{
    if (m_marker == INVALID || m_EM == INVALID) {
        emit errorOccurred(-1, QStringLiteral("板卡未初始化"));
        return 0;
    }

    if (m_curFilePath.isEmpty()) {
        emit errorOccurred(-1, QStringLiteral("请先打开文件"));
        return 0;
    }

    // 计算模式 0x01000000：E3_MarkerMarkEnt2 内部仅计算标刻时间，不实际出光
    m_ezdKernel->E3_MarkerMarkEnt2(m_marker, m_EM, m_curLayer,
        (MarkEntMode)0x01000000, 0, 1);

    int nTimeMs = 0;
    m_ezdKernel->E3_MarkerGetCalcMarkTime(m_marker, nTimeMs);
    return nTimeMs;
}


int EzcadMgr::getMakingTime() const
{
    if (m_marker == INVALID) return 0;
    int nTimeMs = 0;
    m_ezdKernel->E3_MarkerGetMakingTime(m_marker, nTimeMs);
    return nTimeMs;
}

bool EzcadMgr::startEzcad(const QString& ez3FilePath)
{

    m_ezdKernel->E3_Close();

    // 启动 EzCad 进程
    QString ezcadExe = QCoreApplication::applicationDirPath() + "/EzCad3.exe";
    auto* proc = new QProcess(this);
    proc->start(ezcadExe, {ez3FilePath});

    // 进程结束后重新初始化并加载
    connect(proc, QOverload<int, QProcess::ExitStatus>::of(&QProcess::finished),
        this, [this, ez3FilePath, proc](int, QProcess::ExitStatus) {
            proc->deleteLater();

            QString workPath = QCoreApplication::applicationDirPath();
            m_ezdKernel->Initial((TCHAR*)workPath.data(), InitialMode::USB, nullptr);

            m_EM = m_ezdKernel->E3_CreateEntMgr(0);
            m_marker = m_ezdKernel->E3_MarkerGetFirstValidId();

            m_ezdKernel->E3_OpenFileToEntMgr2(
                (TCHAR*)ez3FilePath.data(), m_EM, FALSE, FALSE, FALSE);

            int nCount = 0, nCurLayerIndex = 0;
            m_ezdKernel->E3_GetLayerCount(m_EM, nCount, nCurLayerIndex);
            m_ezdKernel->E3_GetLayerId(m_EM, 0, m_curLayer);

            m_curFilePath = ez3FilePath;
            emit entityChanged(m_curLayer);
            emit logMessage(QStringLiteral("EzCad 编辑完成,已重新加载"), Qt::darkGreen);
        });

    return true;
}
