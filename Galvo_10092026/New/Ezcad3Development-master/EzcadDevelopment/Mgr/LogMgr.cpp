#include "LogMgr.h"
#include <QCoreApplication>
#include <QDir>
#include <QTextStream>

LogMgr::LogMgr(QObject* parent)
    : QObject(parent)
    , m_logDir(QCoreApplication::applicationDirPath() + "/logs")
{
    QDir().mkpath(m_logDir);
    checkAndRotate();
}

LogMgr::~LogMgr()
{
    if (m_file.isOpen()) m_file.close();
}

void LogMgr::setLogDir(const QString& dir)
{
    if (dir.isEmpty() || dir == m_logDir) return;
    m_logDir = dir;
    QDir().mkpath(m_logDir);
    checkAndRotate();
}

void LogMgr::onLogMessage(const QString& msg, QColor color, const QString& source)
{
    QString ts = QDateTime::currentDateTime().toString("[HH:mm:ss.zzz] ");
    QString prefix = source.isEmpty() ? "" : "[" + source + "] ";
    writeLine(ts + prefix + msg);
    emit logMessage(ts + prefix + msg, color);
}

void LogMgr::onErrMessage(int errorCode, const QString& message, const QString& source)
{
    QString ts = QDateTime::currentDateTime().toString("[HH:mm:ss.zzz] ");
    QString prefix = source.isEmpty() ? "" : "[" + source + "] ";
    writeLine(ts + prefix + "[ERR " + QString::number(errorCode) + "] " + message);
    emit errorOccurred(errorCode, ts + prefix + message);
}


void LogMgr::writeLine(const QString& line)
{
    checkAndRotate();  // 写入前校验日期
    if (!m_file.isOpen()) return;
    QTextStream stream(&m_file);
    stream << line << "\n";
    stream.flush();
}

void LogMgr::checkAndRotate()
{
    QString today = QDateTime::currentDateTime().toString("yyyy-MM-dd");
    if (today == m_currentDate && m_file.isOpen())
        return;

    // 关闭旧文件
    if (m_file.isOpen())
        m_file.close();

    m_currentDate = today;
    QString filePath = m_logDir + "/" + m_currentDate + ".log";
    m_file.setFileName(filePath);
    m_file.open(QIODevice::Append | QIODevice::Text);
}
