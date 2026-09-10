#ifndef BOARDMGR_H
#define BOARDMGR_H

#include <QObject>
#include <QString>
#include <QColor>

#include "GtsHal.h"
#include "ControllerData.h"

class GtsMgr;

class BoardMgr : public QObject 
{
    Q_OBJECT

private:
    GtsMgr* m_gtsMgr = nullptr;
    bool m_isOpen = false;
    short m_cardNo = 0;
    short m_lastError = 0;

public:
    explicit BoardMgr(GtsMgr* totalMgr, QObject* parent = nullptr);
    ~BoardMgr();

    // 设置总管理器指针
    void setTotalMgr(GtsMgr* mgr) { m_gtsMgr = mgr; }
    // 是否打开
    bool isOpen() const { return m_isOpen; }
    // 获取板卡编号
    short getCardNo() const { return m_cardNo; }
    // 获取最后一次错误码
    short lastError() const { return m_lastError; }
    // 获取时钟
    Clock getClocks();

public:
    // 打开板卡
    bool open(short channel = 0, short param = 1);
    // 关闭板卡
    bool close();
    // 复位板卡软复位
    bool reset();
    // 设置当前操作的板卡编号
    bool setCardNo(short index);
    // 获取当前板卡编号
    short getCardNo();
    // 从文件加载配置
    bool loadConfig(const QString& filePath);
    // 保存当前配置到文件
    bool saveConfig(const QString& filePath);
    // 从板卡上传配置到主机内存
    bool uploadConfig();
    // 将主机内存配置下载到板卡
    bool downloadConfig();
    // 获取 DLL 版本号字符串
    QString dllVersion() const;
    // 获取固件版本号字符串
    QString firmwareVersion() const;
    // 获取板卡信息
    CardInfo cardInfo() const;
    // 获取驱动版本
    DriverVersion driverVersion() const;
    // 获取接口板状态
    short interfaceBoardStatus() const;
    // 设置接口板状态
    bool setInterfaceBoardStatus(short type);
    // 获取系统时钟计数值
    unsigned long clock() const;
    // 获取高精度时钟计数值
    unsigned long clockHighPrecision() const;
    // 延时(毫秒级)
    bool delay(unsigned short milliseconds);
    // 高精度延时（微秒级）
    bool delayHighPrecision(unsigned short microseconds);
    // 开启中断(注册回调)
    bool interruptOn(short (*pCallback)(TInterrupt));
    // 关闭中断
    bool interruptOff();
    // 设置中断掩码
    bool setInterruptMask(long mask);
    // 获取中断掩码
    long interruptMask() const;
    // 触发软件中断
    bool triggerInterrupt(short param);
    // 获取板卡 UUID
    QString uuid() const;
    // 设置板卡 UUID
    bool setUuid(const QString& code);
    // 获取/设置 Display DIP 状态
    short displayDip() const;
    bool setDisplayDip(short mode);
    // 获取设备共享最大数
    bool setDeviceShareMax(short count);
    // 获取最后一次错误描述
    QString lastErrorString() const;

signals:
    // 发生错误
    void errorOccurred(short axis, short errorCode, const QString& errorMsg);
    // 日志消息
    void logMessage(const QString& message, QColor color = Qt::black, const QString& source = "Gts");
};

#endif // BOARDMGR_H
