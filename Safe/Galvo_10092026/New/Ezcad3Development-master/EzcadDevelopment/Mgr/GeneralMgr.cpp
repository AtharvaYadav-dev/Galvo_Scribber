#include <QTimer>
#include <QJsonDocument>
#include <QJsonObject>
#include <QFile>
#include <QDir>
#include <QCoreApplication>
#include <QFileInfo>

#include "GeneralMgr.h"
#include "EzcadMgr.h"
#include "LogMgr.h"
#include "../../GtsCore/GtsMgr.h"

GeneralMgr::GeneralMgr(QObject* parent)
    : QObject(parent)
    , m_ezcadMgr(new EzcadMgr(this))
    , m_logMgr(new LogMgr(this))
    , m_gtsMgr(new GtsMgr(this))
{
    loadGeneralConfig();
    if (!m_generalCfg.logPath.isEmpty())
        m_logMgr->setLogDir(m_generalCfg.logPath);

    initConnections();
}

GeneralMgr::~GeneralMgr() = default;

EzdKernel* GeneralMgr::kernel() const
{ 
    return m_ezcadMgr ? m_ezcadMgr->kernel() : nullptr; 
}


void GeneralMgr::initialize()
{
    // 确保先connect,再初始化
    QTimer::singleShot(0, this, [this]() {
        m_ezcadMgr->initialize(InitialMode::USB);

        emit initialized();

        });
}

void GeneralMgr::initConnections()
{
    // EzcadMgr → LogMgr(日志写入 + 转发到 UI)
    connect(m_ezcadMgr, &EzcadMgr::logMessage, m_logMgr, &LogMgr::onLogMessage);
    connect(m_ezcadMgr, &EzcadMgr::errorOccurred, m_logMgr, &LogMgr::onErrMessage);
    connect(m_gtsMgr, &GtsMgr::logMessage, m_logMgr, &LogMgr::onLogMessage);
    
    connect(m_gtsMgr, &GtsMgr::errorOccurred, this,
        [this](short axis, short errorCode, const QString& errorMsg) 
        {
            Q_UNUSED(axis);
            m_logMgr->onErrMessage(static_cast<int>(errorCode), errorMsg, QStringLiteral("Gts"));
        });    
}

QString GeneralMgr::generalConfigPath() const
{
    return QCoreApplication::applicationDirPath() + "/Prospect/GeneralConfig.json";
}

bool GeneralMgr::loadGeneralConfig()
{
    QFile file(generalConfigPath());
    if (!file.open(QIODevice::ReadOnly))
        return false;
    QJsonDocument doc = QJsonDocument::fromJson(file.readAll());
    file.close();
    if (!doc.isObject()) return false;
    QJsonObject obj = doc.object();
    m_generalCfg.logPath = obj.value("logPath").toString();
    return true;
}

bool GeneralMgr::saveGeneralConfig()
{
    QJsonObject obj;
    obj["logPath"] = m_generalCfg.logPath;

    QDir().mkpath(QFileInfo(generalConfigPath()).absolutePath());
    QFile file(generalConfigPath());
    if (!file.open(QIODevice::WriteOnly | QIODevice::Truncate))
        return false;
    file.write(QJsonDocument(obj).toJson(QJsonDocument::Indented));
    file.close();
    return true;
}
