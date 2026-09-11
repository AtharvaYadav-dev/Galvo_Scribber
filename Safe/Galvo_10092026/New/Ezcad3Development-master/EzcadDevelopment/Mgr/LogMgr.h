#pragma once
#include <QObject>
#include <QFile>
#include <QColor>
#include <QDateTime>

class LogMgr : public QObject
{
    Q_OBJECT

public:
    explicit LogMgr(QObject* parent = nullptr);
    ~LogMgr();
    void setLogDir(const QString& dir);

private:
    void writeLine(const QString& line);
    void checkAndRotate();

    QString m_logDir;
    QString m_currentDate;
    QFile   m_file;

signals:
    void logMessage(const QString& msg, QColor color);
    void errorOccurred(int errorCode, const QString& message);

public slots:
    void onLogMessage(const QString& msg, QColor color = Qt::black, const QString& source = QString());
    void onErrMessage(int errorCode, const QString& message, const QString& source = QString());
};
