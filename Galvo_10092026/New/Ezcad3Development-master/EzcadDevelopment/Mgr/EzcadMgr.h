#pragma once
#include <QObject>
#include <QColor>

#include "EzcadKernel.h"

class CWndOpenGL;

class EzcadMgr : public QObject
{
    Q_OBJECT

public:
    explicit EzcadMgr(QObject* parent = nullptr);
    ~EzcadMgr();

    // 初始化
    bool initialize(InitialMode mode = InitialMode::USB);
    // 简单测试
    bool createHelloWorld();
    // 文件操作
    bool openFile(const QString& filePath);
    bool saveFile(const QString& filePath);
    // 获取 EzdKernel对象
    EzdKernel* kernel() const { return m_ezdKernel; }
    // 获取当前实体ID
    E3_ID currentEntityId() const { return m_curLayer; }
    // 获取当前文件路径
    QString currentFilePath() const { return m_curFilePath; }
    // 获取管理器ID
    E3_ID entMgrId() const { return m_EM; }

    // 参数接口
    // 打开F3参数设置对话框
    bool openF3ParamDialog();
    // 获取 Int 类型参数参数索引参见SystemIntParamKey 枚举
    int  getF3ParamInt(int index) const;
    // 设置 Int 类型参数
    bool setF3ParamInt(int index, int value);
    // 获取 Double 类型参数
    double getF3ParamDouble(int index) const;
    // 设置 Double 类型参数
    bool setF3ParamDouble(int index, double value);
    // 设置 String 类型参数
    bool setF3ParamString(int index, const QString& value);
    // 更新参数到库内部并保存到 INI 配置文件
    bool updateF3Param();

    // 标刻接口
    bool mark();
    // 停止标刻
    bool markStop();
    // 红光预览
    bool redLightPreview();
    // 是否正在标刻
    bool isMarking() const { return m_isMarking; }
    // 获取预估标刻时间(ms)
    int getCalcMarkTime();
    // 获取实际标刻时间(ms)
    int getMakingTime() const;

    // 启动 EzCad 编辑 ez3 文件（外部编辑完自动重载）
    bool startEzcad(const QString& ez3FilePath);

private:
    bool markStart(int markMode = 0);


signals:
    void errorOccurred(int errorCode, const QString& message, const QString& source = "Ezcad");
    void logMessage(const QString& message, QColor color = Qt::black, const QString& source = "Ezcad");
    void entityChanged(E3_ID entId);  // 实体变化时通知UI刷新
    void markFinished(bool userStop);
    void marking();

private:
    EzdKernel* m_ezdKernel = nullptr;
    E3_ID m_EM = INVALID;               //管理器ID
    E3_ID m_marker = INVALID;           //板卡ID       
    E3_ID m_curLayer = INVALID;         //当前图层ID
    E3_ID m_Ent = INVALID;              //当前实体ID
    // 标刻状态
    bool m_isMarking = false;
    // 当前打开文件
    QString m_curFilePath;

};
