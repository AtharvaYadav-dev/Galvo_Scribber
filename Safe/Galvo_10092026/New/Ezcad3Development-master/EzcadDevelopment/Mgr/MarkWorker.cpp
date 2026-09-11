#include "MarkWorker.h"

void MarkWorker::doWork()
{
    // 红光模式:先打开内置红光
    if (m_markMode == 0x00000002)
    {
        m_pEzdKernel->E3_MarkerSwitchRedLight(m_idMarker, TRUE);
    }

    int nErr = m_pEzdKernel->E3_MarkerMarkEnt2(
        m_idMarker,
        m_idEM,
        m_idCurLayer,
        (MarkEntMode)m_markMode,
        0,
        1);

    bool bUserStop = false;
    if (nErr == 100)    // 100 = 用户调了 E3_MarkerStop
    {
        bUserStop = true;
        // 红光模式：关闭内置红光
        if (m_markMode == 0x00000002)
        {
            m_pEzdKernel->E3_MarkerSwitchRedLight(m_idMarker, FALSE);
        }
    }
    emit workFinished(bUserStop);
}
