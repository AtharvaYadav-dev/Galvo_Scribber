#pragma once
#include <QObject>
#include <QString>

class EzcadMgr;
class LogMgr;
class EzdKernel;
class GtsMgr;

// 通用配置
struct GeneralConfig 
{
    QString logPath;
};

// 通用管理器
class GeneralMgr : public QObject
{
    Q_OBJECT

public:
    explicit GeneralMgr(QObject* parent = nullptr);
    ~GeneralMgr();

    // 延迟初始化 EzcadMgr
    void initialize();

    // 子管理器访问
    EzcadMgr* ezcadMgr() const { return m_ezcadMgr; }
    GtsMgr* gtsMgr() const { return m_gtsMgr; }
    LogMgr* logMgr()   const { return m_logMgr; }
    EzdKernel* kernel() const ;

    // 常规配置读写
    QString generalConfigPath() const;
    bool loadGeneralConfig();
    bool saveGeneralConfig();

    // 配置访问
    QString logPath() const { return m_generalCfg.logPath; }
    void setLogPath(const QString& path) { m_generalCfg.logPath = path; }

private:
    void initConnections();   // 内部信号连线


    GeneralConfig m_generalCfg;
    EzcadMgr* m_ezcadMgr = nullptr;
    LogMgr* m_logMgr = nullptr;
    GtsMgr* m_gtsMgr = nullptr;

signals:
    void initialized();
};
