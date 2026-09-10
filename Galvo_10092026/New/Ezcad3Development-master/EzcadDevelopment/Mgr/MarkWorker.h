#pragma once
#include <QObject>
#include "EzcadKernel.h"

// 打标
class MarkWorker : public QObject
{
    Q_OBJECT

public:
    MarkWorker() = default;

    void setKernel(EzdKernel* pKernel) { m_pEzdKernel = pKernel; }
    void setMarkerId(E3_ID id) { m_idMarker = id; }
    void setEntMgrId(E3_ID id) { m_idEM = id; }
    void setCurLayerId(E3_ID id) { m_idCurLayer = id; }
    void setMarkMode(int mode) { m_markMode = mode; }

signals:
    /// 标刻完成
    void workFinished(bool userStop);

public slots:
    void doWork();

private:
    EzdKernel* m_pEzdKernel = nullptr;
    E3_ID m_idMarker = INVALID;
    E3_ID m_idEM = INVALID;
    E3_ID m_idCurLayer = INVALID;
    int   m_markMode = 0;
};
