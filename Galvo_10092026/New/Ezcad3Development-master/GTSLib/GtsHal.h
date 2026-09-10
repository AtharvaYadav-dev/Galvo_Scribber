// ============================================================
// GtsHal.h — 固高 GTS-400 系列运动控制卡硬件抽象层
// 链接要求: gts.lib (或 gts_x64.lib) + gts.dll (运行时)
// ============================================================
#ifndef GTSHAL_H
#define GTSHAL_H

#include <cstddef>
#include <cstdint>

#include "gts.h"

// ============================================================
// 错误码转换为字符串(调试辅助)
// ============================================================
inline const char* GtsErrorToString(short errCode) {
    switch (errCode) {
    case 0:      return "GT_SUCCESS";
    case 1:      return "GT_ERROR";
    case 2:      return "GT_IMPL";
    case 3:      return "GT_NOT_IMPLE";
    case 4:      return "GT_NO_CARD";
    case 5:      return "GT_NO_DRIVER";
    case 6:      return "GT_NO_LICENSE";
    case 7:      return "GT_INVALID_PARAMETERS";
    case 8:      return "GT_OUT_OF_MEMORY";
    case 9:      return "GT_TIMEOUT";
    case 10:     return "GT_NO_RESOURCE";
    case 11:     return "GT_HARDWARE_ERROR";
    default: {
        if (errCode < 0) return "GT_UNKNOWN_NEGATIVE";
        return "GT_UNKNOWN";
    }
    }
}

// ============================================================
// GtsHal—所有GT_XXX函数的C++ 静态封装
// ============================================================

class GtsHal {
public:
    // ====================================================================
    // 1.板卡管理(Board Management)
    // ====================================================================
    static short getDllVersion(char** ppVersion) { return GT_GetDllVersion(ppVersion); }
    static short getVersion(char** ppVersion) { return GT_GetVersion(ppVersion); }
    static short getVersionEx(short type, TVersion* pVer) { return GT_GetVersionEx(type, pVer); }
    static short setCardNo(short index) { return GT_SetCardNo(index); }
    static short getCardNo(short* pIndex) { return GT_GetCardNo(pIndex); }
    static short open(short channel = 0, short param = 1) { return GT_Open(channel, param); }
    static short close() { return GT_Close(); }
    static short reset() { return GT_Reset(); }
    static short loadConfig(const char* pFile) { return GT_LoadConfig(const_cast<char*>(pFile)); }
    static short saveConfigToFile(const char* pFile) { return GT_SaveConfigToFile(const_cast<char*>(pFile)); }
    static short uploadConfig() { return GT_UploadConfig(); }
    static short downloadConfig() { return GT_DownloadConfig(); }
    static short getCardInfo(short* pCardNum, short* pCardType) { return GT_GetCardInfo(pCardNum, pCardType); }
    static short getDriverVersion(unsigned short* mainVer, unsigned short* slaveVer) { return GT_GetDriverVersion(mainVer, slaveVer); }
    static short getInterfaceBoardSts(short* pStatus) { return GT_GetInterfaceBoardSts(pStatus); }
    static short setInterfaceBoardSts(short type) { return GT_SetInterfaceBoardSts(type); }
    static short getClock(unsigned long* pClock, unsigned long* pLoop = nullptr) { return GT_GetClock(pClock, pLoop); }
    static short getClockHighPrecision(unsigned long* pClock) { return GT_GetClockHighPrecision(pClock); }
    static short delay(unsigned short time) { return GT_Delay(time); }
    static short delayHighPrecision(unsigned short time) { return GT_DelayHighPrecision(time); }
    static short setDeviceShareMax(short count) { return GT_SetDeviceShareMax(count); }

    // ====================================================================
    // 2. 轴控制 (Axis Control)
    // ====================================================================
    // 使能/禁止
    static short axisOn(short axis) { return GT_AxisOn(axis); }
    static short axisOff(short axis) { return GT_AxisOff(axis); }
    static short multiAxisOn(unsigned long mask) { return GT_MultiAxisOn(mask); }
    static short multiAxisOff(unsigned long mask) { return GT_MultiAxisOff(mask); }
    static short setAxisOnDelayTime(unsigned short ms) { return GT_SetAxisOnDelayTime(ms); }
    static short getAxisOnDelayTime(unsigned short* pMs) { return GT_GetAxisOnDelayTime(pMs); }
    // 停止
    static short stop(long mask, long option) { return GT_Stop(mask, option); }
    static short stopEx(long mask, long option) { return GT_StopEx(mask, option); }
    // 报警
    static short alarmOn(short axis) { return GT_AlarmOn(axis); }
    static short alarmOff(short axis) { return GT_AlarmOff(axis); }
    // 限位
    static short lmtsOn(short axis, short limitType = -1) { return GT_LmtsOn(axis, limitType); }
    static short lmtsOff(short axis, short limitType = -1) { return GT_LmtsOff(axis, limitType); }
    static short lmtSns(unsigned short sense) { return GT_LmtSns(sense); }
    // 状态
    static short getSts(short axis, long* pSts, short count = 1, unsigned long* pClock = nullptr) { return GT_GetSts(axis, pSts, count, pClock); }
    static short clrSts(short axis  = 1, short count = 1) { return GT_ClrSts(axis, count); }
    static short zeroPos(short axis = 1 , short count = 1) { return GT_ZeroPos(axis, count); }
    static short synchAxisPos(long mask) { return GT_SynchAxisPos(mask); }
    // 轴模式
    static short ctrlMode(short axis, short mode) { return GT_CtrlMode(axis, mode); }
    static short setAxisMode(short axis, short mode) { return GT_SetAxisMode(axis, mode); }
    static short getAxisMode(short axis, short* pMode) { return GT_GetAxisMode(axis, pMode); }
    // 跟随误差
    static short setPosErr(short control, long error) { return GT_SetPosErr(control, error); }
    static short getPosErr(short control, long* pError) { return GT_GetPosErr(control, pError); }
    static short setAxisFollowErrorMode(short axis, short mode) { return GT_SetAxisFollowErrorMode(axis, mode); }
    static short getAxisFollowErrorMode(short axis, short* pMode) { return GT_GetAxisFollowErrorMode(axis, pMode); }
    // 软限位
    static short setSoftLimit(short axis, long positive, long negative) { return GT_SetSoftLimit(axis, positive, negative); }
    static short getSoftLimit(short axis, long* pPositive, long* pNegative) { return GT_GetSoftLimit(axis, pPositive, pNegative); }
    // 停止减速
    static short setStopDec(short profile, double decSmooth, double decAbrupt) { return GT_SetStopDec(profile, decSmooth, decAbrupt); }
    static short getStopDec(short profile, double* pDecSmooth, double* pDecAbrupt) { return GT_GetStopDec(profile, pDecSmooth, pDecAbrupt); }
    static short setStopIo(short axis, short stopType, short inputType, short inputIndex) { return GT_SetStopIo(axis, stopType, inputType, inputIndex); }

    // ====================================================================
    // 3. 运动模式设置 (Profile Mode)
    // ====================================================================
    static short setPrfPos(short profile, long pos) { return GT_SetPrfPos(profile, pos); }
    static short getPrfPos(short profile, double* pValue, short count = 1, unsigned long* pClock = nullptr) { return GT_GetPrfPos(profile, pValue, count, pClock); }
    static short getPrfVel(short profile, double* pValue, short count = 1, unsigned long* pClock = nullptr) { return GT_GetPrfVel(profile, pValue, count, pClock); }
    static short getPrfAcc(short profile, double* pValue, short count = 1, unsigned long* pClock = nullptr) { return GT_GetPrfAcc(profile, pValue, count, pClock); }
    static short getPrfMode(short profile, long* pValue, short count = 1, unsigned long* pClock = nullptr) { return GT_GetPrfMode(profile, pValue, count, pClock); }
    static short getAxisPrfPos(short axis, double* pValue, short count = 1, unsigned long* pClock = nullptr) { return GT_GetAxisPrfPos(axis, pValue, count, pClock); }
    static short getAxisPrfVel(short axis, double* pValue, short count = 1, unsigned long* pClock = nullptr) { return GT_GetAxisPrfVel(axis, pValue, count, pClock); }
    static short getAxisPrfAcc(short axis, double* pValue, short count = 1, unsigned long* pClock = nullptr) { return GT_GetAxisPrfAcc(axis, pValue, count, pClock); }
    static short setPos(short profile, long pos) { return GT_SetPos(profile, pos); }
    static short getPos(short profile, long* pPos) { return GT_GetPos(profile, pPos); }
    static short update(long mask) { return GT_Update(mask); }
    static short setProfileScale(short axis, long alpha, long beta) { return GT_SetProfileScale(axis, alpha, beta); }
    static short getProfileScale(short axis, long* pAlpha, long* pBeta) { return GT_GetProfileScale(axis, pAlpha, pBeta); }


    // ====================================================================
    // 4. 梯形/点位运动 (Trapezoidal / Point-to-Point)
    // ================================================================
    static short setVel(short profile, double vel) { return GT_SetVel(profile, vel); }            //获取trap模式下的速度
    static short getVel(short profile, double* pVel) { return GT_GetVel(profile, pVel); }
    static short prfTrap(short profile) { return GT_PrfTrap(profile); }
    static short setTrapPrm(short profile, const TTrapPrm& prm) { return GT_SetTrapPrm(profile, const_cast<TTrapPrm*>(&prm)); }
    static short getTrapPrm(short profile, TTrapPrm* pPrm) { return GT_GetTrapPrm(profile, pPrm); }
    static short getTrapTime(short profile, TTrapTime* pTime) { return GT_GetTrapTime(profile, pTime); }
    static short prfJog(short profile) { return GT_PrfJog(profile); }
    static short setJogPrm(short profile, const TJogPrm& prm) { return GT_SetJogPrm(profile, const_cast<TJogPrm*>(&prm)); }
    static short getJogPrm(short profile, TJogPrm* pPrm) { return GT_GetJogPrm(profile, pPrm); }
    static short moveAbsolute(short profile, const TMoveAbsolutePrm& prm) { return GT_MoveAbsolute(profile, const_cast<TMoveAbsolutePrm*>(&prm)); }
    static short getMoveAbsolute(short profile, TMoveAbsolutePrm* pPrm) { return GT_GetMoveAbsolute(profile, pPrm); }
    static short moveAbsoluteEx(short profile, const TMoveAbsolutePrmEx& prm) { return GT_MoveAbsoluteEx(profile, const_cast<TMoveAbsolutePrmEx*>(&prm)); }
    static short getMoveAbsoluteEx(short profile, TMoveAbsolutePrmEx* pPrm) { return GT_GetMoveAbsoluteEx(profile, pPrm); }
    static short moveVelocity(short profile, const TMoveVelocityPrm& prm) { return GT_MoveVelocity(profile, const_cast<TMoveVelocityPrm*>(&prm)); }
    static short getMoveVelocity(short profile, TMoveVelocityPrm* pPrm) { return GT_GetMoveVelocity(profile, pPrm); }

    // ====================================================================
    // 5. PT 运动 (Position-Time)
    // ====================================================================
    static short prfPt(short profile, short mode = PT_MODE_STATIC) { return GT_PrfPt(profile, mode); }
    static short setPtLoop(short profile, long loop) { return GT_SetPtLoop(profile, loop); }
    static short getPtLoop(short profile, long* pLoop) { return GT_GetPtLoop(profile, pLoop); }
    static short ptSpace(short profile, short* pSpace, short fifo = 0) { return GT_PtSpace(profile, pSpace, fifo); }
    static short ptData(short profile, double pos, long time, short type = PT_SEGMENT_NORMAL, short fifo = 0) { return GT_PtData(profile, pos, time, type, fifo); }
    static short ptDataWN(short profile, double pos, long time, short type = PT_SEGMENT_NORMAL, long segNum = 0, short fifo = 0) { return GT_PtDataWN(profile, pos, time, type, segNum, fifo); }
    static short ptClear(short profile, short fifo = 0) { return GT_PtClear(profile, fifo); }
    static short ptStart(long mask, long option = 0) { return GT_PtStart(mask, option); }
    static short setPtMemory(short profile, short memory) { return GT_SetPtMemory(profile, memory); }
    static short getPtMemory(short profile, short* pMemory) { return GT_GetPtMemory(profile, pMemory); }
    static short ptGetSegNum(short profile, long* pSegNum) { return GT_PtGetSegNum(profile, pSegNum); }
    static short ptDoBit(short profile, short doType, short index, short value, short fifo) { return GT_PtDoBit(profile, doType, index, value, fifo); }
    static short ptAo(short profile, short aoType, short index, double value, short fifo) { return GT_PtAo(profile, aoType, index, value, fifo); }

    // ====================================================================
    // 6. Gear 运动 (电子齿轮)
    // ====================================================================
    static short prfGear(short profile, short dir = 0) { return GT_PrfGear(profile, dir); }
    static short setGearMaster(short profile, short masterIndex, short masterType = GEAR_MASTER_PROFILE, short masterItem = 0) { return GT_SetGearMaster(profile, masterIndex, masterType, masterItem); }
    static short getGearMaster(short profile, short* pMasterIndex, short* pMasterType = nullptr, short* pMasterItem = nullptr) { return GT_GetGearMaster(profile, pMasterIndex, pMasterType, pMasterItem); }
    static short setGearRatio(short profile, long masterEven, long slaveEven, long masterSlope = 0) { return GT_SetGearRatio(profile, masterEven, slaveEven, masterSlope); }
    static short getGearRatio(short profile, long* pMasterEven, long* pSlaveEven, long* pMasterSlope = nullptr) { return GT_GetGearRatio(profile, pMasterEven, pSlaveEven, pMasterSlope); }
    static short gearStart(long mask) { return GT_GearStart(mask); }
    static short setGearEvent(short profile, short event, long startPara0, long startPara1) { return GT_SetGearEvent(profile, event, startPara0, startPara1); }
    static short getGearEvent(short profile, short* pEvent, long* pStartPara0, long* pStartPara1) { return GT_GetGearEvent(profile, pEvent, pStartPara0, pStartPara1); }

    // ====================================================================
    // 7. Follow 运动 (电子凸轮)
    // ====================================================================
    static short prfFollow(short profile, short dir = 0) { return GT_PrfFollow(profile, dir); }
    static short setFollowMaster(short profile, short masterIndex, short masterType = FOLLOW_MASTER_PROFILE, short masterItem = 0) { return GT_SetFollowMaster(profile, masterIndex, masterType, masterItem); }
    static short getFollowMaster(short profile, short* pMasterIndex, short* pMasterType = nullptr, short* pMasterItem = nullptr) { return GT_GetFollowMaster(profile, pMasterIndex, pMasterType, pMasterItem); }
    static short setFollowLoop(short profile, long loop) { return GT_SetFollowLoop(profile, loop); }
    static short getFollowLoop(short profile, long* pLoop) { return GT_GetFollowLoop(profile, pLoop); }
    static short setFollowEvent(short profile, short event, short masterDir, long pos = 0) { return GT_SetFollowEvent(profile, event, masterDir, pos); }
    static short getFollowEvent(short profile, short* pEvent, short* pMasterDir, long* pPos = nullptr) { return GT_GetFollowEvent(profile, pEvent, pMasterDir, pPos); }
    static short followSpace(short profile, short* pSpace, short fifo = 0) { return GT_FollowSpace(profile, pSpace, fifo); }
    static short followData(short profile, long masterSegment, double slaveSegment, short type = FOLLOW_SEGMENT_NORMAL, short fifo = 0) { return GT_FollowData(profile, masterSegment, slaveSegment, type, fifo); }
    static short followClear(short profile, short fifo = 0) { return GT_FollowClear(profile, fifo); }
    static short followStart(long mask, long option = 0) { return GT_FollowStart(mask, option); }
    static short followSwitch(long mask) { return GT_FollowSwitch(mask); }
    static short setFollowMemory(short profile, short memory) { return GT_SetFollowMemory(profile, memory); }
    static short getFollowMemory(short profile, short* pMemory) { return GT_GetFollowMemory(profile, pMemory); }
    static short getFollowStatus(short profile, short* pFifoNum, short* pSwitchStatus) { return GT_GetFollowStatus(profile, pFifoNum, pSwitchStatus); }

    // ====================================================================
    // 8. PVT 运动
    // ====================================================================
    static short prfPvt(short profile) { return GT_PrfPvt(profile); }
    static short setPvtLoop(short profile, long loop) { return GT_SetPvtLoop(profile, loop); }
    static short getPvtLoop(short profile, long* pLoopCount, long* pLoop) { return GT_GetPvtLoop(profile, pLoopCount, pLoop); }
    static short pvtStatus(short profile, short* pTableId, double* pTime, short count = 1) { return GT_PvtStatus(profile, pTableId, pTime, count); }
    static short pvtTableClear(short tableId) { return GT_PvtTableClear(tableId); }
    static short pvtStart(long mask) { return GT_PvtStart(mask); }
    static short pvtTableSelect(short profile, short tableId) { return GT_PvtTableSelect(profile, tableId); }
    static short pvtTable(short tableId, long count, double* pTime, double* pPos, double* pVel) { return GT_PvtTable(tableId, count, pTime, pPos, pVel); }
    static short pvtTableEx(short tableId, long count, double* pTime, double* pPos, double* pVelBegin, double* pVelEnd) { return GT_PvtTableEx(tableId, count, pTime, pPos, pVelBegin, pVelEnd); }
    static short pvtTableComplete(short tableId, long count, double* pTime, double* pPos, double* pA, double* pB, double* pC, double velBegin = 0, double velEnd = 0) { return GT_PvtTableComplete(tableId, count, pTime, pPos, pA, pB, pC, velBegin, velEnd); }
    static short pvtTablePercent(short tableId, long count, double* pTime, double* pPos, double* pPercent, double velBegin = 0) { return GT_PvtTablePercent(tableId, count, pTime, pPos, pPercent, velBegin); }

    // ====================================================================
    // 9. 插补运动 (Interpolation / Coordinate System)
    // ====================================================================
    static short setCrdPrm(short crd, const TCrdPrm& prm) { return GT_SetCrdPrm(crd, const_cast<TCrdPrm*>(&prm)); }
    static short getCrdPrm(short crd, TCrdPrm* pPrm) { return GT_GetCrdPrm(crd, pPrm); }
    static short setCrdSmooth(short crd, const TCrdSmooth& smooth) { return GT_SetCrdSmooth(crd, const_cast<TCrdSmooth*>(&smooth)); }
    static short getCrdSmooth(short crd, TCrdSmooth* pSmooth) { return GT_GetCrdSmooth(crd, pSmooth); }
    static short setCrdJerk(short crd, double jerkMax) { return GT_SetCrdJerk(crd, jerkMax); }
    static short getCrdJerk(short crd, double* pJerkMax) { return GT_GetCrdJerk(crd, pJerkMax); }
    static short setCrdMapBase(short crd, short base) { return GT_SetCrdMapBase(crd, base); }
    static short getCrdMapBase(short crd, short* pBase) { return GT_GetCrdMapBase(crd, pBase); }
    static short setArcAllowError(short crd, double error) { return GT_SetArcAllowError(crd, error); }
    static short crdSpace(short crd, long* pSpace, short fifo = 0) { return GT_CrdSpace(crd, pSpace, fifo); }
    static short crdData(short crd, const TCrdData& data, short fifo = 0) { return GT_CrdData(crd, const_cast<TCrdData*>(&data), fifo); }
    static short crdDataCircle(short crd, const TCrdData& data, short fifo = 0) { return GT_CrdDataCircle(crd, const_cast<TCrdData*>(&data), fifo); }

    // 直线插补
    static short lnXY(short crd, long x, long y, double synVel, double synAcc, double velEnd = 0, short fifo = 0) { return GT_LnXY(crd, x, y, synVel, synAcc, velEnd, fifo); }
    static short lnXYZ(short crd, long x, long y, long z, double synVel, double synAcc, double velEnd = 0, short fifo = 0) { return GT_LnXYZ(crd, x, y, z, synVel, synAcc, velEnd, fifo); }
    static short lnXYZA(short crd, long x, long y, long z, long a, double synVel, double synAcc, double velEnd = 0, short fifo = 0) { return GT_LnXYZA(crd, x, y, z, a, synVel, synAcc, velEnd, fifo); }
    static short lnXYG0(short crd, long x, long y, double synVel, double synAcc, short fifo = 0) { return GT_LnXYG0(crd, x, y, synVel, synAcc, fifo); }
    static short lnXYZG0(short crd, long x, long y, long z, double synVel, double synAcc, short fifo = 0) { return GT_LnXYZG0(crd, x, y, z, synVel, synAcc, fifo); }
    static short lnXYZAG0(short crd, long x, long y, long z, long a, double synVel, double synAcc, short fifo = 0) { return GT_LnXYZAG0(crd, x, y, z, a, synVel, synAcc, fifo); }

    // 圆弧插补
    static short arcXYR(short crd, long x, long y, double radius, short circleDir, double synVel, double synAcc, double velEnd = 0, short fifo = 0) { return GT_ArcXYR(crd, x, y, radius, circleDir, synVel, synAcc, velEnd, fifo); }
    static short arcXYC(short crd, long x, long y, double xCenter, double yCenter, short circleDir, double synVel, double synAcc, double velEnd = 0, short fifo = 0) { return GT_ArcXYC(crd, x, y, xCenter, yCenter, circleDir, synVel, synAcc, velEnd, fifo); }
    static short arcYZR(short crd, long y, long z, double radius, short circleDir, double synVel, double synAcc, double velEnd = 0, short fifo = 0) { return GT_ArcYZR(crd, y, z, radius, circleDir, synVel, synAcc, velEnd, fifo); }
    static short arcYZC(short crd, long y, long z, double yCenter, double zCenter, short circleDir, double synVel, double synAcc, double velEnd = 0, short fifo = 0) { return GT_ArcYZC(crd, y, z, yCenter, zCenter, circleDir, synVel, synAcc, velEnd, fifo); }
    static short arcZXR(short crd, long z, long x, double radius, short circleDir, double synVel, double synAcc, double velEnd = 0, short fifo = 0) { return GT_ArcZXR(crd, z, x, radius, circleDir, synVel, synAcc, velEnd, fifo); }
    static short arcZXC(short crd, long z, long x, double zCenter, double xCenter, short circleDir, double synVel, double synAcc, double velEnd = 0, short fifo = 0) { return GT_ArcZXC(crd, z, x, zCenter, xCenter, circleDir, synVel, synAcc, velEnd, fifo); }
    static short arcXYZ(short crd, long x, long y, long z, double interX, double interY, double interZ, double synVel, double synAcc, double velEnd = 0, short fifo = 0) { return GT_ArcXYZ(crd, x, y, z, interX, interY, interZ, synVel, synAcc, velEnd, fifo); }

    // 螺旋插补
    static short helixXYRZ(short crd, long x, long y, long z, double radius, short circleDir, double synVel, double synAcc, double velEnd = 0, short fifo = 0) { return GT_HelixXYRZ(crd, x, y, z, radius, circleDir, synVel, synAcc, velEnd, fifo); }
    static short helixXYCZ(short crd, long x, long y, long z, double xCenter, double yCenter, short circleDir, double synVel, double synAcc, double velEnd = 0, short fifo = 0) { return GT_HelixXYCZ(crd, x, y, z, xCenter, yCenter, circleDir, synVel, synAcc, velEnd, fifo); }

    // 通用多轴
    static short lnXYZACUVW(short crd, long* pPos, short posMask, double synVel, double synAcc, double velEnd = 0, short fifo = 0) { return GT_LnXYZACUVW(crd, pPos, posMask, synVel, synAcc, velEnd, fifo); }

    // 缓冲区操作 (插补中的 IO/延时/激光等)
    static short bufIO(short crd, unsigned short doType, unsigned short doMask,unsigned short doValue, short fifo = 0) { return GT_BufIO(crd, doType, doMask, doValue, fifo); }
    static short bufDelay(short crd, unsigned short delayTime, short fifo = 0) {  return GT_BufDelay(crd, delayTime, fifo); }
    static short bufDA(short crd, short chn, short daValue, short fifo = 0) {   return GT_BufDA(crd, chn, daValue, fifo); }
    static short bufMove(short crd, short moveAxis, long pos, double vel, double acc,   short modal, short fifo = 0) {  return GT_BufMove(crd, moveAxis, pos, vel, acc, modal, fifo); }
    static short bufGear(short crd, short gearAxis, long pos, short fifo = 0) {   return GT_BufGear(crd, gearAxis, pos, fifo); }
    static short bufStop(short crd, long mask, long option, short fifo = 0) {   return GT_BufStop(crd, mask, option, fifo); }
    static short bufMoveJog(short crd, short moveAxis, double vel, double acc, short modal, short fifo = 0) { return GT_BufMoveJog(crd, moveAxis, vel, acc, modal, fifo); }
    static short crdStart(short mask, short option) { return GT_CrdStart(mask, option); }
    static short crdStartStep(short mask, short option) { return GT_CrdStartStep(mask, option); }
    static short crdStepMode(short mask, short option) { return GT_CrdStepMode(mask, option); }
    static short crdClear(short crd, short fifo) { return GT_CrdClear(crd, fifo); }
    static short crdStatus(short crd, short* pRun, long* pSegment, short fifo = 0) { return GT_CrdStatus(crd, pRun, pSegment, fifo);  }
    static short getCrdPos(short crd, double* pPos) { return GT_GetCrdPos(crd, pPos); }
    static short getCrdVel(short crd, double* pSynVel) { return GT_GetCrdVel(crd, pSynVel); }
    static short setOverride(short crd, double synVelRatio) { return GT_SetOverride(crd, synVelRatio); }
    static short setOverride2(short crd, double synVelRatio) { return GT_SetOverride2(crd, synVelRatio); }
    static short setMaxOverrideLA(double maxSynVelRatio) { return GT_SetMaxOverrideLA(maxSynVelRatio); }
    static short setCrdStopDec(short crd, double decSmooth, double decAbrupt) { return GT_SetCrdStopDec(crd, decSmooth, decAbrupt); }
    static short getCrdStopDec(short crd, double* pDecSmooth, double* pDecAbrupt) { return GT_GetCrdStopDec(crd, pDecSmooth, pDecAbrupt); }
    static short setUserSegNum(short crd, long segNum, short fifo = 0) { return GT_SetUserSegNum(crd, segNum, fifo); }
    static short getUserSegNum(short crd, long* pSegment, short fifo = 0) { return GT_GetUserSegNum(crd, pSegment, fifo); }
    static short getRemainderSegNum(short crd, long* pSegment, short fifo = 0) { return GT_GetRemainderSegNum(crd, pSegment, fifo); }
    static short setCrdBufferMode(short crd, short bufferMode, short fifo) { return GT_SetCrdBufferMode(crd, bufferMode, fifo); }
    static short getCrdBufferMode(short crd, short* pBufferMode, short fifo) { return GT_GetCrdBufferMode(crd, pBufferMode, fifo); }

    // ====================================================================
    // 10. 激光控制 (Laser Control)
    // ====================================================================
    static short laserPowerMode(short mode, double maxValue, double minValue,short channel = 0, short delayMode = 0) { return GT_LaserPowerMode(mode, maxValue, minValue, channel, delayMode); }
    static short laserPrfCmd(double outputCmd, short channel = 0) { return GT_LaserPrfCmd(outputCmd, channel); }
    static short laserOutFrq(double outFrq, short channel = 0) {  return GT_LaserOutFrq(outFrq, channel); }
    static short setPulseWidth(unsigned long width, short channel = 0) {   return GT_SetPulseWidth(width, channel);  }
    static short setWaitPulse(unsigned short mode, double waitPulseFrq, double waitPulseDuty, short channel = 0) {   return GT_SetWaitPulse(mode, waitPulseFrq, waitPulseDuty, channel); }
    static short setPreVltg(unsigned short mode, double voltageValue, short channel = 0) {   return GT_SetPreVltg(mode, voltageValue, channel); }
    static short setLevelDelay(unsigned short offDelay, unsigned short onDelay, short channel = 0) {  return GT_SetLevelDelay(offDelay, onDelay, channel);  }
    static short enaFPK(unsigned short time1, unsigned short time2, unsigned short laserOffDelay, short channel = 0) { return GT_EnaFPK(time1, time2, laserOffDelay, channel); }
    static short disFPK(short channel = 0) { return GT_DisFPK(channel); }
    static short setLaserMode(short mode) { return GT_SetLaserMode(mode); }
    static short setLaserDisMode(short mode, short source, long* pPos, double* pScale, short channel = 0) { return GT_SetLaserDisMode(mode, source, pPos, pScale, channel); }
    static short setLaserDisRatio(double* pRatio, double minPower, double maxPower,  short channel = 0) {  return GT_SetLaserDisRatio(pRatio, minPower, maxPower, channel); }
    static short zeroLaserOnTime(short channel) { return GT_ZeroLaserOnTime(channel); }
    static short getLaserOnTime(short channel, unsigned long* pTime) {  return GT_GetLaserOnTime(channel, pTime); }
    static short setLaserCrdMap(short channel, short map) { return GT_SetLaserCrdMap(channel, map); }
    static short getLaserCrdMap(short channel, short* pMap) { return GT_GetLaserCrdMap(channel, pMap); }
    static short setLaserFollowSpline(short tableId, long n, double* pX, double* pY,  double beginValue, double endValue, short channel = 0) {  return GT_SetLaserFollowSpline(tableId, n, pX, pY, beginValue, endValue, channel); }
    static short getLaserFollowSpline(short tableId, long n, double* pX, double* pY, double* pA, double* pB, double* pC, long* pCount, short channel = 0) { return GT_GetLaserFollowSpline(tableId, n, pX, pY, pA, pB, pC, pCount, channel); }

    // 缓冲区激光指令（在插补中调用）
    static short bufLaserOn(short crd, short fifo = 0, short channel = 0) { return GT_BufLaserOn(crd, fifo, channel); }
    static short bufLaserOff(short crd, short fifo = 0, short channel = 0) {  return GT_BufLaserOff(crd, fifo, channel);  }
    static short bufLaserPrfCmd(short crd, double laserPower, short fifo = 0, short channel = 0) {   return GT_BufLaserPrfCmd(crd, laserPower, fifo, channel); }
    static short bufLaserFollowRatio(short crd, double ratio, double minPower, double maxPower, short fifo = 0, short channel = 0) { return GT_BufLaserFollowRatio(crd, ratio, minPower, maxPower, fifo, channel); }
    static short bufLaserFollowMode(short crd, short source = 0, short fifo = 0, short channel = 0, double startPower = 0) { return GT_BufLaserFollowMode(crd, source, fifo, channel, startPower); }
    static short bufLaserFollowOff(short crd, short fifo = 0, short channel = 0) { return GT_BufLaserFollowOff(crd, fifo, channel); }
    static short bufLaserFollowSpline(short crd, short tableId, double minPower, double maxPower,   short fifo = 0, short channel = 0) {   return GT_BufLaserFollowSpline(crd, tableId, minPower, maxPower, fifo, channel); }
    static short bufLaserPrfFollow(short crd, double ratio, long minPower, long maxPower,  short fifo = 0, short channel = 0) { return GT_BufLaserPrfFollow(crd, ratio, minPower, maxPower, fifo, channel); }
    static short selectLaserDisTable(short channel, short index) {   return GT_SelectLaserDisTable(channel, index);  }
    static short getCurrentLaserDisTable(short channel, short* pIndex) {    return GT_GetCurrentLaserDisTable(channel, pIndex); }

    // ====================================================================
    // 11. IO 控制 (Digital IO)
    // ====================================================================
    static short setDo(short doType, long value) { return GT_SetDo(doType, value); }
    static short setDoBit(short doType, short doIndex, short value) {return GT_SetDoBit(doType, doIndex, value);  }
    static short getDo(short doType, long* pValue) { return GT_GetDo(doType, pValue); }
    static short setDoBitReverse(short doType, short doIndex, short value, short reverseTime) {  return GT_SetDoBitReverse(doType, doIndex, value, reverseTime); }
    static short setDoMask(short doType, unsigned short doMask, long value) {   return GT_SetDoMask(doType, doMask, value); }
    static short enableDoBitPulse(short doType, short doIndex,  unsigned short highLevelTime, unsigned short lowLevelTime,   long pulseNum, short firstLevel) {   return GT_EnableDoBitPulse(doType, doIndex, highLevelTime, lowLevelTime, pulseNum, firstLevel);  }
    static short disableDoBitPulse(short doType, short doIndex) {  return GT_DisableDoBitPulse(doType, doIndex); }

    static short getDi(short diType, long* pValue) { return GT_GetDi(diType, pValue); }
    static short getDiRaw(short diType, long* pValue) { return GT_GetDiRaw(diType, pValue); }
    static short getDiReverseCount(short diType, short diIndex, unsigned long* pReverseCount, short count = 1) { return GT_GetDiReverseCount(diType, diIndex, pReverseCount, count); }
    static short setDiReverseCount(short diType, short diIndex,  unsigned long* pReverseCount, short count = 1) {   return GT_SetDiReverseCount(diType, diIndex, pReverseCount, count); }
    static short setHSIOOpt(unsigned short value, short channel = 0) { return GT_SetHSIOOpt(value, channel); }
    static short getHSIOOpt(unsigned short* pValue, short channel = 0) {   return GT_GetHSIOOpt(pValue, channel); }

    // ====================================================================
    // 12. DAC / ADC
    // ====================================================================
    static short setDac(short dac, short* pValue, short count = 1) { return GT_SetDac(dac, pValue, count); }
    static short getDac(short dac, short* pValue, short count = 1, unsigned long* pClock = nullptr) {  return GT_GetDac(dac, pValue, count, pClock); }
    static short getAdc(short adc, double* pValue, short count = 1, unsigned long* pClock = nullptr) { return GT_GetAdc(adc, pValue, count, pClock); }
    static short getAdcValue(short adc, short* pValue, short count = 1, unsigned long* pClock = nullptr) { return GT_GetAdcValue(adc, pValue, count, pClock); }
    static short setAdcFilter(short adc, short filterTime) { return GT_SetAdcFilter(adc, filterTime); }
    static short setAdcConfig(short adc, const TAdcConfig& cfg) {  return GT_SetAdcConfig(adc, const_cast<TAdcConfig*>(&cfg)); }
    static short getAdcConfig(short adc, TAdcConfig* pCfg) { return GT_GetAdcConfig(adc, pCfg); }
    static short setAdcFilterPrm(short adc, double k) { return GT_SetAdcFilterPrm(adc, k); }
    static short getAdcFilterPrm(short adc, double* pk) { return GT_GetAdcFilterPrm(adc, pk); }
    static short setMtrBias(short dac, short bias) { return GT_SetMtrBias(dac, bias); }
    static short getMtrBias(short dac, short* pBias) { return GT_GetMtrBias(dac, pBias); }
    static short setMtrLmt(short dac, short limit) { return GT_SetMtrLmt(dac, limit); }
    static short getMtrLmt(short dac, short* pLimit) { return GT_GetMtrLmt(dac, pLimit); }

    // ====================================================================
    // 13. 编码器 (Encoder)
    // ====================================================================
    static short encSns(unsigned short sense) { return GT_EncSns(sense); }
    static short encOn(short encoder) { return GT_EncOn(encoder); }
    static short encOff(short encoder) { return GT_EncOff(encoder); }
    static short setEncPos(short encoder, long encPos) { return GT_SetEncPos(encoder, encPos); }
    static short getEncPos(short encoder, double* pValue, short count = 1,  unsigned long* pClock = nullptr) {  return GT_GetEncPos(encoder, pValue, count, pClock); }
    static short getEncPosPre(short encoder, double* pValue, short count = 1,  unsigned long* pClock = nullptr) {  return GT_GetEncPosPre(encoder, pValue, count, pClock); }
    static short getEncVel(short encoder, double* pValue, short count = 1,  unsigned long* pClock = nullptr) {  return GT_GetEncVel(encoder, pValue, count, pClock); }
    static short getAxisEncPos(short axis, double* pValue, short count = 1,unsigned long* pClock = nullptr) {  return GT_GetAxisEncPos(axis, pValue, count, pClock); }
    static short getAxisEncVel(short axis, double* pValue, short count = 1,   unsigned long* pClock = nullptr) {  return GT_GetAxisEncVel(axis, pValue, count, pClock);  }
    static short getAxisEncAcc(short axis, double* pValue, short count = 1, unsigned long* pClock = nullptr) {  return GT_GetAxisEncAcc(axis, pValue, count, pClock); }
    static short getAxisError(short axis, double* pValue, short count = 1,  unsigned long* pClock = nullptr) {   return GT_GetAxisError(axis, pValue, count, pClock); }
    static short setEncoderScale(short encoder, long alpha, long beta) {  return GT_SetEncoderScale(encoder, alpha, beta);  }
    static short getEncoderScale(short encoder, long* pAlpha, long* pBeta) {   return GT_GetEncoderScale(encoder, pAlpha, pBeta); }

    // 编码器响应检查
    static short setEncResponseCheck(short control, short dacThreshold, double minEncVel, long time) {  return GT_SetEncResponseCheck(control, dacThreshold, minEncVel, time); }
    static short getEncResponseCheck(short control, short* pDacThreshold,  double* pMinEncVel, long* pTime) {return GT_GetEncResponseCheck(control, pDacThreshold, pMinEncVel, pTime); }
    static short enableEncResponseCheck(short control) { return GT_EnableEncResponseCheck(control); }
    static short disableEncResponseCheck(short control) { return GT_DisableEncResponseCheck(control); }
    static short setEncoderOutSelect(short mode) { return GT_SetEncoderOutSelect(mode); }
    static short getEncoderOutSelect(short* pMode) { return GT_GetEncoderOutSelect(pMode); }

    // ====================================================================
    // 14. 捕获 (Capture)
    // ====================================================================
    static short setCaptureMode(short encoder, short mode) { return GT_SetCaptureMode(encoder, mode); }
    static short getCaptureMode(short encoder, short* pMode, short count = 1) {  return GT_GetCaptureMode(encoder, pMode, count);  }
    static short stopCapture(short encoder) { return GT_StopCapture(encoder); }
    static short getCaptureStatus(short encoder, short* pStatus, long* pValue,  short count = 1, unsigned long* pClock = nullptr) {   return GT_GetCaptureStatus(encoder, pStatus, pValue, count, pClock);  }
    static short getCaptureStatusEx(short encoder, short* pStatus, long* pValue,  double* pDoubleVar, unsigned long* pCaptureClock, short count = 1, unsigned long* pClock = nullptr) {  return GT_GetCaptureStatusEx(encoder, pStatus, pValue, pDoubleVar,   pCaptureClock, count, pClock); }
    static short setCaptureSense(short encoder, short mode, short sense) {  return GT_SetCaptureSense(encoder, mode, sense); }
    static short clearCaptureStatus(short encoder) { return GT_ClearCaptureStatus(encoder); }
    static short setCaptureRepeat(short encoder, short count) { return GT_SetCaptureRepeat(encoder, count); }
    static short getCaptureRepeatStatus(short encoder, short* pCount) {   return GT_GetCaptureRepeatStatus(encoder, pCount); }
    static short getCaptureRepeatPos(short encoder, long* pValue, short startNum, short count) {  return GT_GetCaptureRepeatPos(encoder, pValue, startNum, count); }
    static short setCaptureEncoder(short trigger, short encoder) {  return GT_SetCaptureEncoder(trigger, encoder); }
    static short getCaptureWidth(short trigger, short* pWidth, short count = 1) {   return GT_GetCaptureWidth(trigger, pWidth, count);  }

    // ====================================================================
    // 15. 回零 (Home)
    // ====================================================================
    static short homeInit() { return GT_HomeInit(); }
    static short home(short axis, long pos, double vel, double acc, long offset) {  return GT_Home(axis, pos, vel, acc, offset);  }
    static short index(short axis, long pos, long offset) { return GT_Index(axis, pos, offset); }
    static short homeStop(short axis, long pos, double vel, double acc) {   return GT_HomeStop(axis, pos, vel, acc); }
    static short homeSts(short axis, unsigned short* pStatus) { return GT_HomeSts(axis, pStatus); }
    static short goHome(short axis, const THomePrm& prm) {    return GT_GoHome(axis, const_cast<THomePrm*>(&prm));  }
    static short getHomePrm(short axis, THomePrm* pHomePrm) { return GT_GetHomePrm(axis, pHomePrm); }
    static short getHomeStatus(short axis, THomeStatus* pStatus) { return GT_GetHomeStatus(axis, pStatus); }
    static short executeStandardHome(short axis, const TStandardHomePrm& prm) {   return GT_ExecuteStandardHome(axis, const_cast<TStandardHomePrm*>(&prm));  }
    static short getStandardHomePrm(short axis, TStandardHomePrm* pPrm) {  return GT_GetStandardHomePrm(axis, pPrm); }
    static short getStandardHomeStatus(short axis, TStandardHomeStatus* pStatus) {  return GT_GetStandardHomeStatus(axis, pStatus);  }

    // ====================================================================
    // 16. PID / 控制滤波
    // ====================================================================
    static short setPid(short control, short index, const TPid& pid) {  return GT_SetPid(control, index, const_cast<TPid*>(&pid));   }
    static short getPid(short control, short index, TPid* pPid) {   return GT_GetPid(control, index, pPid);  }
    static short setControlFilter(short control, short index) {   return GT_SetControlFilter(control, index);  }
    static short getControlFilter(short control, short* pIndex) {  return GT_GetControlFilter(control, pIndex); }
    static short setKvffFilter(short control, short index, short kvffFilterExp, double accMax) {    return GT_SetKvffFilter(control, index, kvffFilterExp, accMax);  }
    static short getKvffFilter(short control, short index, short* pKvffFilterExp, double* pAccMax) {    return GT_GetKvffFilter(control, index, pKvffFilterExp, pAccMax);  }
    static short setAxisBand(short axis, long band, long time) {    return GT_SetAxisBand(axis, band, time);  }
    static short getAxisBand(short axis, long* pBand, long* pTime) {   return GT_GetAxisBand(axis, pBand, pTime); }
    static short setBacklash(short axis, long compValue, double compChangeValue, long compDir) {   return GT_SetBacklash(axis, compValue, compChangeValue, compDir);  }
    static short getBacklash(short axis, long* pCompValue, double* pCompChangeValue, long* pCompDir) {   return GT_GetBacklash(axis, pCompValue, pCompChangeValue, pCompDir);  }
    static short setControlConfigEx(short control, const TControlConfigEx& cfg) {  return GT_SetControlConfigEx(control, const_cast<TControlConfigEx*>(&cfg)); }
    static short getControlConfigEx(short control, TControlConfigEx* pCfg) {   return GT_GetControlConfigEx(control, pCfg);  }
    static short setControlSuperimposed(short control, short superimposedType, short superimposedIndex) {   return GT_SetControlSuperimposed(control, superimposedType, superimposedIndex); }
    static short getControlSuperimposed(short control, short* pType, short* pIndex) {   return GT_GetControlSuperimposed(control, pType, pIndex);  }

    // ====================================================================
    // 17. 手轮 (Handwheel)
    // ====================================================================
    static short handwheelInit() { return GT_HandwheelInit(); }
    static short setHandwheelStopDec(short slave, double decSmooth, double decAbrupt) {   return GT_SetHandwheelStopDec(slave, decSmooth, decAbrupt);  }
    static short startHandwheel(short slave, short master, short masterEven, short slaveEven, short intervalTime, double acc, double dec, double vel,  short stopWaitTime) {   return GT_StartHandwheel(slave, master, masterEven, slaveEven,    intervalTime, acc, dec, vel, stopWaitTime); }
    static short endHandwheel(short slave) { return GT_EndHandwheel(slave); }

    // ====================================================================
    // 18. 位置比较 (Position Compare)
    // ====================================================================
    static short setComparePort(short channel, short hsio0, short hsio1) { return GT_SetComparePort(channel, hsio0, hsio1); }
    static short comparePulse(short level, short outputType, short time) { return GT_ComparePulse(level, outputType, time); }
    static short compareStop() { return GT_CompareStop(); }
    static short compareStatus(short* pStatus, long* pCount) { return GT_CompareStatus(pStatus, pCount); }
    static short compareData(short encoder, short source, short pulseType, short startLevel, short time, long* pBuf1, short count1, long* pBuf2, short count2) { return GT_CompareData(encoder, source, pulseType, startLevel, time, pBuf1, count1, pBuf2, count2); }
    static short compareLinear(short encoder, short channel, long startPos, long repeatTimes,  long interval, short time, short source) { return GT_CompareLinear(encoder, channel, startPos, repeatTimes, interval, time, source); }
    static short compareContinuePulseMode(short mode, short count, short standTime) {  return GT_CompareContinuePulseMode(mode, count, standTime); }

    // 2D 位置比较
    static short compare2DMode(short chn, short mode) { return GT_2DCompareMode(chn, mode); }
    static short compare2DPulse(short chn, short level, short outputType, short time) {   return GT_2DComparePulse(chn, level, outputType, time);  }
    static short compare2DStop(short chn) { return GT_2DCompareStop(chn); }
    static short compare2DClear(short chn) { return GT_2DCompareClear(chn); }
    static short compare2DStatus(short chn, short* pStatus, long* pCount,  short* pFifo, short* pFifoCount, short* pBufCount = nullptr) {   return GT_2DCompareStatus(chn, pStatus, pCount, pFifo, pFifoCount, pBufCount);    }
    static short compare2DSetPrm(short chn, const T2DComparePrm& prm) {  return GT_2DCompareSetPrm(chn, const_cast<T2DComparePrm*>(&prm)); }
    static short compare2DData(short chn, short count, const T2DCompareData* pBuf, short fifo) {  return GT_2DCompareData(chn, count, const_cast<T2DCompareData*>(pBuf), fifo);  }
    static short compare2DStart(short chn) { return GT_2DCompareStart(chn); }
    static short compare2DClearData(short chn) { return GT_2DCompareClearData(chn); }
    static short compare2DSetPreOutTime(short chn, double preOutputTime) {   return GT_2DCompareSetPreOutTime(chn, preOutputTime);  }

    // ====================================================================
    // 19. Trigger (探针/触发)
    // ====================================================================
    static short setTrigger(short i, const TTrigger& trigger) {   return GT_SetTrigger(i, const_cast<TTrigger*>(&trigger));  }
    static short getTrigger(short i, TTrigger* pTrigger) { return GT_GetTrigger(i, pTrigger); }
    static short getTriggerStatus(short i, TTriggerStatus* pStatus, short count = 1) {   return GT_GetTriggerStatus(i, pStatus, count);  }
    static short getTriggerStatusEx(short i, TTriggerStatusEx* pStatusEx, short count = 1) {   return GT_GetTriggerStatusEx(i, pStatusEx, count);   }
    static short clearTriggerStatus(short i) { return GT_ClearTriggerStatus(i); }
    static short getTriggerLatchValue(short i, long count, long* pValue,   long* pCount, TLatchValueInfo* pInfo) {   return GT_GetTriggerLatchValue(i, count, pValue, pCount, pInfo);  }

    // ====================================================================
    // 20. 龙门 (Gantry)
    // ====================================================================
    static short enableGantry(short master, short slave, double masterKp, double slaveKp) {  return GT_EnableGantry(master, slave, masterKp, slaveKp);  }
    static short disableGantry() { return GT_DisableGantry(); }
    static short setGantryErrLmt(long errLmt) { return GT_SetGantryErrLmt(errLmt); }
    static short getGantryErrLmt(long* pErrLmt) { return GT_GetGantryErrLmt(pErrLmt); }
    static short zeroGantryPos(short master, short slave) { return GT_ZeroGantryPos(master, slave); }
    static short setGantryMode(short group, short master, short slave,   short mode, long syncErrorLimit = 1000) {   return GT_SetGantryMode(group, master, slave, mode, syncErrorLimit); }
    static short getGantryMode(short group, short* pMaster, short* pSlave,  short* pMode, long* pSyncErrorLimit) {    return GT_GetGantryMode(group, pMaster, pSlave, pMode, pSyncErrorLimit); }
    static short setGantryPid(short group, const TPid& gantryPid, const TPid& yawPid) {   return GT_SetGantryPid(group, const_cast<TPid*>(&gantryPid), const_cast<TPid*>(&yawPid)); }
    static short getGantryPid(short group, TPid* pGantryPid, TPid* pYawPid) {    return GT_GetGantryPid(group, pGantryPid, pYawPid);  }
    static short gantryAxisOn(short group) { return GT_GantryAxisOn(group); }
    static short gantryAxisOff(short group) { return GT_GantryAxisOff(group); }

    // ====================================================================
    // 21. 扩展模块 (Extension Module)
    // ====================================================================
    static short openExtMdl(const char* pDllName = nullptr) { return GT_OpenExtMdl(const_cast<char*>(pDllName)); }
    static short closeExtMdl() { return GT_CloseExtMdl(); }
    static short switchtoCardNoExtMdl(short card) { return GT_SwitchtoCardNoExtMdl(card); }
    static short resetExtMdl() { return GT_ResetExtMdl(); }
    static short loadExtConfig(const char* pFileName) {  return GT_LoadExtConfig(const_cast<char*>(pFileName));  }
    static short setExtIoValue(short mdl, unsigned short value) { return GT_SetExtIoValue(mdl, value); }
    static short getExtIoValue(short mdl, unsigned short* pValue) { return GT_GetExtIoValue(mdl, pValue); }
    static short setExtIoBit(short mdl, short index, unsigned short value) {    return GT_SetExtIoBit(mdl, index, value);  }
    static short getExtIoBit(short mdl, short index, unsigned short* pValue) {   return GT_GetExtIoBit(mdl, index, pValue);  }
    static short getExtAdValue(short mdl, short chn, unsigned short* pValue) {    return GT_GetExtAdValue(mdl, chn, pValue);   }
    static short getExtAdVoltage(short mdl, short chn, double* pValue) {   return GT_GetExtAdVoltage(mdl, chn, pValue);   }
    static short setExtDaValue(short mdl, short chn, unsigned short value) {     return GT_SetExtDaValue(mdl, chn, value);  }
    static short setExtDaVoltage(short mdl, short chn, double value) {     return GT_SetExtDaVoltage(mdl, chn, value);   }
    static short getExtMdlMode(short* pMode) { return GT_GetExtMdlMode(pMode); }
    static short setExtMdlMode(short mode) { return GT_SetExtMdlMode(mode); }
    static short getConfig(short mdl, TExtMdlCfgInfo* pInfo) { return GT_GetConfig(mdl, pInfo); }
    static short setConfig(short mdl, const TExtMdlCfgInfo& info) {    return GT_SetConfig(mdl, const_cast<TExtMdlCfgInfo*>(&info)); }

    // ====================================================================
    // 22. 自动对焦 (AutoFocus)
    // ====================================================================
    static short autoFocus(unsigned short mode, double kp, short reverse, short channel) {  return GT_AutoFocus(mode, kp, reverse, channel);  }
    static short setAutoFocusRefVol(double refVol, double maxVol, double minVol, short channel) {    return GT_SetAutoFocusRefVol(refVol, maxVol, minVol, channel); }
    static short getAutoFocusStatus(unsigned short* pStatus, short count) {  return GT_GetAutoFocusStatus(pStatus, count); }
    static short configAutoFocus(short chnAdc, short channel) {   return GT_ConfigAutoFocus(chnAdc, channel);  }
    static short setAutoFocusAuxPrm(double kf, double kd, double limitKd, short channel) {   return GT_SetAutoFocusAuxPrm(kf, kd, limitKd, channel);}
    static short setAutoFocusDeadVoltage(double voltage, short channel) {  return GT_SetAutoFocusDeadVoltage(voltage, channel); }

    // ====================================================================
    // 23. 坐标变换 (Transform)
    // ====================================================================
    static short setTransformOrthogonal(short index, const TTransformOrthogonal& data) {   return GT_SetTransformOrthogonal(index, const_cast<TTransformOrthogonal*>(&data));  }
    static short getTransformOrthogonal(short index, TTransformOrthogonal* pData) {  return GT_GetTransformOrthogonal(index, pData);  }
    static short getTransformOrthogonalPosition(short index, double* pX, double* pY) {  return GT_GetTransformOrthogonalPosition(index, pX, pY);  }
    static short setTransformPerpendicularity(short index, const TTransformPerpendicularity& data) {   return GT_SetTransformPerpendicularity(index, const_cast<TTransformPerpendicularity*>(&data));  }
    static short getTransformPerpendicularity(short index, TTransformPerpendicularity* pData) {   return GT_GetTransformPerpendicularity(index, pData);   }
    static short getTransformPerpendicularityPosition(short index, double* pX, double* pY, double* pZ) {   return GT_GetTransformPerpendicularityPosition(index, pX, pY, pZ); }

    // ====================================================================
    // 24. Smart Cutter
    // ====================================================================
    static short setSmartCutterPrm(short index, const TSmartCutterPrm& prm) {   return GT_SetSmartCutterPrm(index, const_cast<TSmartCutterPrm*>(&prm)); }
    static short getSmartCutterPrm(short index, TSmartCutterPrm* pPrm) {      return GT_GetSmartCutterPrm(index, pPrm); }
    static short smartCutterOn(short index) { return GT_SmartCutterOn(index); }
    static short smartCutterOff(short index) { return GT_SmartCutterOff(index); }
    static short getSmartCutterInfo(short index, TSmartCutterInfo* pInfo) {  return GT_GetSmartCutterInfo(index, pInfo); }
    static short setSmartCutterValue(short index, double radiusValue, double angleValue) {  return GT_SetSmartCutterValue(index, radiusValue, angleValue); }
    static short smartCutterStart(short index) { return GT_SmartCutterStart(index); }

    // ====================================================================
    // 25. 丝杠补偿 (Lead Screw Compensation)
    // ====================================================================
    static short setLeadScrewComp(short axis, short n, long startPos, long lenPos,  long* pCompPos, long* pCompNeg) {   return GT_SetLeadScrewComp(axis, n, startPos, lenPos, pCompPos, pCompNeg); }
    static short enableLeadScrewComp(short axis, short mode) {  return GT_EnableLeadScrewComp(axis, mode);   }
    static short getLeadScrewCompInnerValue(short axis, short dir, long pos, long* pCompValue) {   return GT_GetLeadScrewCompInnerValue(axis, dir, pos, pCompValue); }
    static short setLeadScrewCrossComp(short axis, short n, long startPos, long lenPos,  long* pCompPos, long* pCompNeg, short link) {   return GT_SetLeadScrewCrossComp(axis, n, startPos, lenPos, pCompPos, pCompNeg, link);  }
    static short enableLeadScrewCrossComp(short axis, short mode) {  return GT_EnableLeadScrewCrossComp(axis, mode);  }
    static short setLeadScrewLink(short axis, short link) { return GT_SetLeadScrewLink(axis, link); }
    static short getLeadScrewLink(short axis, short* pLink) { return GT_GetLeadScrewLink(axis, pLink); }

    // 2D 补偿
    static short setCompensate2DTable(short idx, const TCompensate2DTable& tbl, long* pData,   short externComp = 0) {   return GT_SetCompensate2DTable(idx, const_cast<TCompensate2DTable*>(&tbl), pData, externComp); }
    static short getCompensate2DTable(short idx, TCompensate2DTable* pTbl, short* pExternComp = nullptr) {  return GT_GetCompensate2DTable(idx, pTbl, pExternComp);   }
    static short setCompensate2D(short axis, const TCompensate2D& comp) {  return GT_SetCompensate2D(axis, const_cast<TCompensate2D*>(&comp));  }
    static short getCompensate2D(short axis, TCompensate2D* pComp) {  return GT_GetCompensate2D(axis, pComp); }
    static short getCompensate2DValue(short axis, double* pValue) {    return GT_GetCompensate2DValue(axis, pValue);   }
    static short getCompensate(short axis, double* pPitchError, double* pCrossError,  double* pBacklashError, double* pEncPos, double* pPrfPos) {     return GT_GetCompensate(axis, pPitchError, pCrossError, pBacklashError, pEncPos, pPrfPos); }

    // ====================================================================
    // 26. PCI 中断
    // ====================================================================
    static short interruptOn(TInterruptCallback pCallback) { return GT_InterruptOn(pCallback); }
    static short interruptOff() { return GT_InterruptOff(); }
    static short setInterruptMask(long mask) { return GT_SetInterruptMask(mask); }
    static short getInterruptMask(long* pMask) { return GT_GetInterruptMask(pMask); }
    static short interruptTrigger(short param) { return GT_InterruptTrigger(param); }

    // ====================================================================
    // 27. 脚本/编译 (Motion Program)
    // ====================================================================
    static short compile(const char* pFileName, TCompileInfo* pWrongInfo) {   return GT_Compile(const_cast<char*>(pFileName), pWrongInfo);  }
    static short download(const char* pFileName) {  return GT_Download(const_cast<char*>(pFileName));  }
    static short getFunId(const char* pFunName, short* pFunId) {    return GT_GetFunId(const_cast<char*>(pFunName), pFunId);  }
    static short bind(short thread, short funId, short page) { return GT_Bind(thread, funId, page); }
    static short runThread(short thread) { return GT_RunThread(thread); }
    static short stopThread(short thread) { return GT_StopThread(thread); }
    static short pauseThread(short thread) { return GT_PauseThread(thread); }
    static short getThreadSts(short thread, TThreadSts* pSts) { return GT_GetThreadSts(thread, pSts); }
    static short getVarId(const char* pFunName, const char* pVarName, TVarInfo* pVarInfo) {    return GT_GetVarId(const_cast<char*>(pFunName), const_cast<char*>(pVarName), pVarInfo); }
    static short setVarValue(short page, const TVarInfo& varInfo, double* pValue, short count = 1) {  return GT_SetVarValue(page, const_cast<TVarInfo*>(&varInfo), pValue, count);   }
    static short getVarValue(short page, const TVarInfo& varInfo, double* pValue, short count = 1) {    return GT_GetVarValue(page, const_cast<TVarInfo*>(&varInfo), pValue, count);  }

    // ====================================================================
    // 28. 变量 (Long/Double Variable)
    // ====================================================================
    static short setLongVar(short index, long value) { return GT_SetLongVar(index, value); }
    static short getLongVar(short index, long* pValue) { return GT_GetLongVar(index, pValue); }
    static short setDoubleVar(short index, double value) { return GT_SetDoubleVar(index, value); }
    static short getDoubleVar(short index, double* pValue) { return GT_GetDoubleVar(index, pValue); }
    static short setFlagVar(short index, short mode, short value) {    return GT_SetFlagVar(index, mode, value);  }
    static short getFlagVar(short index, short* pMode, short* pValue) {     return GT_GetFlagVar(index, pMode, pValue);  }

    // ====================================================================
    // 29. 信号检测 (Signal Detect / Time Filter)
    // ====================================================================
    static short setSignalTimeFilter(short type, short index, double filterWidth) {   return GT_SetSignalTimeFilter(type, index, filterWidth);  }
    static short getSignalTimeFilter(short type, short index, double* pFilterWidth) {   return GT_GetSignalTimeFilter(type, index, pFilterWidth); }
    static short clearSignalDetect(short index) { return GT_ClearSignalDetect(index); }
    static short setSignalDetect(short index, short enable, const TSignalDetect& prm) {   return GT_SetSignalDetect(index, enable, const_cast<TSignalDetect*>(&prm));  }
    static short getSignalDetect(short index, short* pEnable, TSignalDetect* pPrm) {   return GT_GetSignalDetect(index, pEnable, pPrm); }
    static short getSignalDetectStatus(short index, TSignalDetectStatus* pPrm) {   return GT_GetSignalDetectStatus(index, pPrm); }

    // ====================================================================
    // 30. 组合轴 / 运动平滑
    // ====================================================================
    static short setCombineAxes(short index, const TCombineAxes& data) {   return GT_SetCombineAxes(index, const_cast<TCombineAxes*>(&data));  }
    static short getCombineAxes(short index, TCombineAxes* pData) {   return GT_GetCombineAxes(index, pData); }
    static short combineAxesOn(short index) { return GT_CombineAxesOn(index); }
    static short combineAxesOff(short index) { return GT_CombineAxesOff(index); }
    static short getCombineAxesStatus(short index, TCombineAxesStatus* pStatus) {   return GT_GetCombineAxesStatus(index, pStatus); }
    static short setAxisAddition(short axis, short dataType, short additionIndex, short additionType) {   return GT_SetAxisAddition(axis, dataType, additionIndex, additionType);   }
    static short getAxisAddition(short axis, short dataType, short* pAdditionIndex, short* pAdditionType) {    return GT_GetAxisAddition(axis, dataType, pAdditionIndex, pAdditionType);  }
    static short setMotionSmooth(short axis, const TMotionSmooth& smooth) {   return GT_SetMotionSmooth(axis, const_cast<TMotionSmooth*>(&smooth));  }
    static short getMotionSmooth(short axis, TMotionSmooth* pSmooth) {     return GT_GetMotionSmooth(axis, pSmooth);  }

    // ====================================================================
    // 31. 摇杆 (Joystick)
    // ====================================================================
    static short setJoystickMapAxis(short idx, short* axis) { return GT_SetJoystickMapAxis(idx, axis); }
    static short getJoystickMapAxis(short idx, short* pAxis) { return GT_GetJoystickMapAxis(idx, pAxis); }
    static short joystickEnable(short idx, short enable) { return GT_JoystickEnable(idx, enable); }
    static short setJoystickSericalPortPrm(short idx, const TSericalPortPrm& prm) {  return GT_SetJoystickSericalPortPrm(idx, const_cast<TSericalPortPrm*>(&prm));   }
    static short getJoystickSericalPortPrm(short idx, TSericalPortPrm* pPrm) {    return GT_GetJoystickSericalPortPrm(idx, pPrm);   }
    static short joystickCheckEnable(short idx, short checkEnable) {    return GT_JoystickCheckEnable(idx, checkEnable);   }
    static short getJoystickSts(short idx, long* pSts) { return GT_GetJoystickSts(idx, pSts); }
    static short getJoystickValue(short idx, long* pValue) { return GT_GetJoystickValue(idx, pValue); }
    static short setJoystickMotionPrm(short idx, const TJoystickMoitonPrm& prm) {   return GT_SetJoystickMotionPrm(idx, const_cast<TJoystickMoitonPrm*>(&prm));  }
    static short getJoystickMotionPrm(short idx, TJoystickMoitonPrm* pPrm) {   return GT_GetJoystickMotionPrm(idx, pPrm);   }
    static short setJoystickMotionVel(short idx, const TJoystickMoitonVel& vel) {  return GT_SetJoystickMotionVel(idx, const_cast<TJoystickMoitonVel*>(&vel));  }
    static short getJoystickMotionVel(short idx, TJoystickMoitonVel* pVel) {      return GT_GetJoystickMotionVel(idx, pVel);  }
    static short joystickReset(short idx) { return GT_JoystickReset(idx); }

    // ====================================================================
    // 32. UUID / 其他杂项
    // ====================================================================
    static short getUuid(char* pCode, short count) { return GT_GetUuid(pCode, count); }
    static short setUuid(char* pCode, short count) { return GT_SetUuid(pCode, count); }
    static short getDisplayDip(short* pMode) { return GT_GetDisplayDip(pMode); }
    static short setDisplayDip(short mode) { return GT_SetDisplayDip(mode); }
    static short getMachineWorkPos(short crd, short mode, double* pMachinePos, double* pWorkPos) {   return GT_GetMachineWorkPos(crd, mode, pMachinePos, pWorkPos);  }
    static short checkCrdLineTime(short crd, double x, double y, double z,    double* pVelMax, double* pAcc, double* pVelEnd,   double* pTime, long* pErrorCode) {    return GT_CheckCrdLineTime(crd, x, y, z, pVelMax, pAcc, pVelEnd, pTime, pErrorCode);  }
    static short gpiSns(unsigned short sense) { return GT_GpiSns(sense); }
    static short setStepOutLevel(short axis, short type, short reverse) {  return GT_SetStepOutLevel(axis, type, reverse); }
    static short getStepOutLevel(short axis, short type, short* pReverse) {  return GT_GetStepOutLevel(axis, type, pReverse);  }
    static short stepDir(short step) { return GT_StepDir(step); }
    static short stepPulse(short step) { return GT_StepPulse(step); }
    static short stepOrthogonal(short step) { return GT_StepOrthogonal(step); }
    static short profileScale(short axis, short alpha, short beta) { return GT_ProfileScale(axis, alpha, beta); }
    static short encScale(short axis, short alpha, short beta) {  return GT_EncScale(axis, alpha, beta);  }
    static short setAxisInputShaping(short axis, short enable, short count, double k) {   return GT_SetAxisInputShaping(axis, enable, count, k);  }
    static short setMcOverride(short axis, short mode, double override, double smoothTime) {  return GT_SetMcOverride(axis, mode, override, smoothTime);   }
    static short getMcOverride(short axis, short mode, double* pOverrideTarget,    double* pSmoothTime, double* pOverride) {  return GT_GetMcOverride(axis, mode, pOverrideTarget, pSmoothTime, pOverride); }
    static short setCrdFollowLoop(short crd, unsigned long loop) { return GT_SetCrdFollowLoop(crd, loop); }
    static short getCrdFollowLoop(short crd, unsigned long* pLoop) { return GT_GetCrdFollowLoop(crd, pLoop); }
    static short setCrdFollowPrm(short crd, const TCrdFollowPrm& prm) {  return GT_SetCrdFollowPrm(crd, const_cast<TCrdFollowPrm*>(&prm));  }
    static short getCrdFollowPrm(short crd, TCrdFollowPrm* pPrm) { return GT_GetCrdFollowPrm(crd, pPrm); }
    static short bufFollowMaster(short crd, const TBufFollowMaster& data, short fifo = 0) {  return GT_BufFollowMaster(crd, const_cast<TBufFollowMaster*>(&data), fifo);   }
    static short bufFollowEventCross(short crd, const TBufFollowEventCross& data, short fifo = 0) {  return GT_BufFollowEventCross(crd, const_cast<TBufFollowEventCross*>(&data), fifo);  }
    static short bufFollowEventTrigger(short crd, const TBufFollowEventTrigger& data, short fifo = 0) {  return GT_BufFollowEventTrigger(crd, const_cast<TBufFollowEventTrigger*>(&data), fifo);}
    static short bufFollowStart(short crd, long masterSegment, long slaveSegment, long masterFrameWidth, short fifo = 0) {   return GT_BufFollowStart(crd, masterSegment, slaveSegment, masterFrameWidth, fifo);  }

    // ====================================================================
    // 33. PosCompare (新版本位置比较)
    // ====================================================================
    static short setPosCompareMode(short index, const TPosCompareMode& mode) {   return GT_SetPosCompareMode(index, const_cast<TPosCompareMode*>(&mode));  }
    static short getPosCompareMode(short index, TPosCompareMode* pMode) {    return GT_GetPosCompareMode(index, pMode);  }
    static short posCompareStart(short index) { return GT_PosCompareStart(index); }
    static short posCompareStop(short index) { return GT_PosCompareStop(index); }
    static short posCompareClear(short index) { return GT_PosCompareClear(index); }
    static short posCompareStatus(short index, TPosCompareStatus* pStatus) {    return GT_PosCompareStatus(index, pStatus);  }
    static short posCompareData(short index, const TPosCompareData& data) {   return GT_PosCompareData(index, const_cast<TPosCompareData*>(&data)); }
    static short posCompareSetLinear(short index, const TPosCompareLinear& linear) {    return GT_SetPosCompareLinear(index, const_cast<TPosCompareLinear*>(&linear));  }
    static short posCompareSetPsoPrm(short index, const TPosComparePsoPrm& prm) {   return GT_SetPosComparePsoPrm(index, const_cast<TPosComparePsoPrm*>(&prm)); }
    static short posCompareSetContinueMode(short index, const TPosCompareContinueMode& mode) {   return GT_SetPosCompareContinueMode(index, const_cast<TPosCompareContinueMode*>(&mode));   }
    static short bufPosCompareStart(short crd, short fifo, short index) {  return GT_BufPosCompareStart(crd, fifo, index); }
    static short bufPosCompareStop(short crd, short fifo, short index) {    return GT_BufPosCompareStop(crd, fifo, index); }
    static short bufPosComparePsoPrm(short crd, short index, const TPosComparePsoPrm& prm, short fifo) { return GT_BufPosComparePsoPrm(crd, index, const_cast<TPosComparePsoPrm*>(&prm), fifo); }

    // ====================================================================
    // 34. Laser PWM DAC
    // ====================================================================
    static short setLaserPwmDac(double pwmWidth, double frq, short* pDacValue, long count, short channel) { return GT_SetLaserPwmDac(pwmWidth, frq, pDacValue, count, channel); }
    static short laserPwmDacOn(short channel) { return GT_LaserPwmDacOn(channel); }
    static short laserPwmDacOff(short channel) { return GT_LaserPwmDacOff(channel); }
    static short setLaserDisTable1D(short count, double* pRatio, long* pPos, double minPower, double maxPower, double* pLimitPower, short channel = 0) { return GT_SetLaserDisTable1D(count, pRatio, pPos, minPower, maxPower, pLimitPower, channel); }
    static short setLaserFollowTable(short tableId, long n, double* pVel, double* pPower, short channel) { return GT_SetLaserFollowTable(tableId, n, pVel, pPower, channel); }
    static short getLaserFollowTable(short tableId, long n, double* pVel, double* pPower, long* pCount, short channel) { return GT_GetLaserFollowTable(tableId, n, pVel, pPower, pCount, channel); }
};

#endif // GTSHAL_H
