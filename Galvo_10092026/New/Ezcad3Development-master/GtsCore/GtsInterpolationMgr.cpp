#include "GtsInterpolationMgr.h"

InterpolationMgr::InterpolationMgr(QObject* parent)
    : QObject(parent)
{
}

InterpolationMgr::~InterpolationMgr() 
{
    // 停止所有坐标系
    for (short crd = 0; crd < 2; crd++) {
        GtsHal::crdClear(crd, 0);
    }
}

bool InterpolationMgr::checkCrd(short crd) const 
{
    return (crd >= 0 && crd < CRD_MAX);
}


bool InterpolationMgr::setCrdParams(short crd, const TCrdPrm& prm) 
{
    if (!checkCrd(crd)) {
        emit errorOccurred(crd, -1, QStringLiteral("坐标系号无效: %1").arg(crd));
        return false;
    }
    m_lastError = GtsHal::setCrdPrm(crd, prm);
    if (m_lastError != 0) {
        emit errorOccurred(crd, m_lastError, QStringLiteral("setCrdPrm: ") + lastErrorString());
        return false;
    }
    return true;
}

bool InterpolationMgr::getCrdParams(short crd, TCrdPrm& prm) const 
{
    if (!checkCrd(crd)) return false;
    m_lastError = GtsHal::getCrdPrm(crd, &prm);
    return m_lastError == 0;
}

bool InterpolationMgr::setCrdSmooth(short crd, const TCrdSmooth& smooth) 
{
    if (!checkCrd(crd)) {
        emit errorOccurred(crd, -1, QStringLiteral("坐标系号无效: %1").arg(crd));
        return false;
    }
    m_lastError = GtsHal::setCrdSmooth(crd, smooth);
    if (m_lastError != 0) {
        emit errorOccurred(crd, m_lastError, QStringLiteral("setCrdSmooth: ") + lastErrorString());
        return false;
    }
    return true;
}

bool InterpolationMgr::getCrdSmooth(short crd, TCrdSmooth& smooth) const 
{
    if (!checkCrd(crd)) return false;
    m_lastError = GtsHal::getCrdSmooth(crd, &smooth);
    return m_lastError == 0;
}

bool InterpolationMgr::setCrdJerk(short crd, double jerkMax) 
{
    if (!checkCrd(crd)) {
        emit errorOccurred(crd, -1, QStringLiteral("坐标系号无效: %1").arg(crd));
        return false;
    }
    m_lastError = GtsHal::setCrdJerk(crd, jerkMax);
    if (m_lastError != 0) {
        emit errorOccurred(crd, m_lastError, QStringLiteral("setCrdJerk: ") + lastErrorString());
        return false;
    }
    return true;
}

double InterpolationMgr::getCrdJerk(short crd) const 
{
    if (!checkCrd(crd)) return 0.0;
    double jerk = 0.0;
    GtsHal::getCrdJerk(crd, &jerk);
    return jerk;
}

bool InterpolationMgr::setCrdMapBase(short crd, short base) 
{
    if (!checkCrd(crd)) {
        emit errorOccurred(crd, -1, QStringLiteral("坐标系号无效: %1").arg(crd));
        return false;
    }
    m_lastError = GtsHal::setCrdMapBase(crd, base);
    if (m_lastError != 0) {
        emit errorOccurred(crd, m_lastError, QStringLiteral("setCrdMapBase: ") + lastErrorString());
        return false;
    }
    return true;
}

short InterpolationMgr::getCrdMapBase(short crd) const 
{
    if (!checkCrd(crd)) return -1;
    short base = 0;
    GtsHal::getCrdMapBase(crd, &base);
    return base;
}

bool InterpolationMgr::setArcAllowError(short crd, double error) 
{
    if (!checkCrd(crd)) {
        emit errorOccurred(crd, -1, QStringLiteral("坐标系号无效: %1").arg(crd));
        return false;
    }
    m_lastError = GtsHal::setArcAllowError(crd, error);
    if (m_lastError != 0) {
        emit errorOccurred(crd, m_lastError, QStringLiteral("setArcAllowError: ") + lastErrorString());
        return false;
    }
    return true;
}

bool InterpolationMgr::setCrdStopDecel(short crd, double decSmooth, double decAbrupt) 
{
    if (!checkCrd(crd)) {
        emit errorOccurred(crd, -1, QStringLiteral("坐标系号无效: %1").arg(crd));
        return false;
    }
    m_lastError = GtsHal::setCrdStopDec(crd, decSmooth, decAbrupt);
    if (m_lastError != 0) {
        emit errorOccurred(crd, m_lastError, QStringLiteral("setCrdStopDec: ") + lastErrorString());
        return false;
    }
    return true;
}

bool InterpolationMgr::getCrdStopDecel(short crd, double& decSmooth, double& decAbrupt) const 
{
    if (!checkCrd(crd)) return false;
    m_lastError = GtsHal::getCrdStopDec(crd, &decSmooth, &decAbrupt);
    return m_lastError == 0;
}

bool InterpolationMgr::lineXY(short crd, long x, long y, double synVel, double synAcc,
    double velEnd, short fifo) 
{
    if (!checkCrd(crd)) {
        emit errorOccurred(crd, -1, QStringLiteral("坐标系号无效: %1").arg(crd));
        return false;
    }
    m_lastError = GtsHal::lnXY(crd, x, y, synVel, synAcc, velEnd, fifo);
    if (m_lastError != 0) {
        emit errorOccurred(crd, m_lastError, QStringLiteral("lnXY: ") + lastErrorString());
        return false;
    }
    return true;
}

bool InterpolationMgr::lineXYZ(short crd, long x, long y, long z, double synVel, double synAcc,
    double velEnd, short fifo) 
{
    if (!checkCrd(crd)) {
        emit errorOccurred(crd, -1, QStringLiteral("坐标系号无效: %1").arg(crd));
        return false;
    }
    m_lastError = GtsHal::lnXYZ(crd, x, y, z, synVel, synAcc, velEnd, fifo);
    if (m_lastError != 0) {
        emit errorOccurred(crd, m_lastError, QStringLiteral("lnXYZ: ") + lastErrorString());
        return false;
    }
    return true;
}

bool InterpolationMgr::lineXYZA(short crd, long x, long y, long z, long a,
    double synVel, double synAcc, double velEnd, short fifo) 
{
    if (!checkCrd(crd)) {
        emit errorOccurred(crd, -1, QStringLiteral("坐标系号无效: %1").arg(crd));
        return false;
    }
    m_lastError = GtsHal::lnXYZA(crd, x, y, z, a, synVel, synAcc, velEnd, fifo);
    if (m_lastError != 0) {
        emit errorOccurred(crd, m_lastError, QStringLiteral("lnXYZA: ") + lastErrorString());
        return false;
    }
    return true;
}

bool InterpolationMgr::lineXYG0(short crd, long x, long y, double synVel, double synAcc, short fifo) 
{
    if (!checkCrd(crd)) {
        emit errorOccurred(crd, -1, QStringLiteral("坐标系号无效: %1").arg(crd));
        return false;
    }
    m_lastError = GtsHal::lnXYG0(crd, x, y, synVel, synAcc, fifo);
    if (m_lastError != 0) {
        emit errorOccurred(crd, m_lastError, QStringLiteral("lnXYG0: ") + lastErrorString());
        return false;
    }
    return true;
}

bool InterpolationMgr::lineXYZG0(short crd, long x, long y, long z, double synVel, double synAcc, short fifo) 
{
    if (!checkCrd(crd)) {
        emit errorOccurred(crd, -1, QStringLiteral("坐标系号无效: %1").arg(crd));
        return false;
    }
    m_lastError = GtsHal::lnXYZG0(crd, x, y, z, synVel, synAcc, fifo);
    if (m_lastError != 0) {
        emit errorOccurred(crd, m_lastError, QStringLiteral("lnXYZG0: ") + lastErrorString());
        return false;
    }
    return true;
}

bool InterpolationMgr::lineXYZAG0(short crd, long x, long y, long z, long a,
    double synVel, double synAcc, short fifo) 
{
    if (!checkCrd(crd)) {
        emit errorOccurred(crd, -1, QStringLiteral("坐标系号无效: %1").arg(crd));
        return false;
    }
    m_lastError = GtsHal::lnXYZAG0(crd, x, y, z, a, synVel, synAcc, fifo);
    if (m_lastError != 0) {
        emit errorOccurred(crd, m_lastError, QStringLiteral("lnXYZAG0: ") + lastErrorString());
        return false;
    }
    return true;
}

bool InterpolationMgr::lineXYZACUVW(short crd, long* pPos, short posMask,
    double synVel, double synAcc, double velEnd, short fifo) 
{
    if (!checkCrd(crd)) {
        emit errorOccurred(crd, -1, QStringLiteral("坐标系号无效: %1").arg(crd));
        return false;
    }
    m_lastError = GtsHal::lnXYZACUVW(crd, pPos, posMask, synVel, synAcc, velEnd, fifo);
    if (m_lastError != 0) {
        emit errorOccurred(crd, m_lastError, QStringLiteral("lnXYZACUVW: ") + lastErrorString());
        return false;
    }
    return true;
}

bool InterpolationMgr::arcXYByRadius(short crd, long x, long y, double radius, short circleDir,
    double synVel, double synAcc, double velEnd, short fifo) 
{
    if (!checkCrd(crd)) {
        emit errorOccurred(crd, -1, QStringLiteral("坐标系号无效: %1").arg(crd));
        return false;
    }
    m_lastError = GtsHal::arcXYR(crd, x, y, radius, circleDir, synVel, synAcc, velEnd, fifo);
    if (m_lastError != 0) {
        emit errorOccurred(crd, m_lastError, QStringLiteral("arcXYR: ") + lastErrorString());
        return false;
    }
    return true;
}

bool InterpolationMgr::arcXYByCenter(short crd, long x, long y, double xCenter, double yCenter,
    short circleDir, double synVel, double synAcc,
    double velEnd, short fifo) 
{
    if (!checkCrd(crd)) {
        emit errorOccurred(crd, -1, QStringLiteral("坐标系号无效: %1").arg(crd));
        return false;
    }
    m_lastError = GtsHal::arcXYC(crd, x, y, xCenter, yCenter, circleDir, synVel, synAcc, velEnd, fifo);
    if (m_lastError != 0) {
        emit errorOccurred(crd, m_lastError, QStringLiteral("arcXYC: ") + lastErrorString());
        return false;
    }
    return true;
}

bool InterpolationMgr::arcYZByRadius(short crd, long y, long z, double radius, short circleDir,
    double synVel, double synAcc, double velEnd, short fifo) 
{
    if (!checkCrd(crd)) {
        emit errorOccurred(crd, -1, QStringLiteral("坐标系号无效: %1").arg(crd));
        return false;
    }
    m_lastError = GtsHal::arcYZR(crd, y, z, radius, circleDir, synVel, synAcc, velEnd, fifo);
    if (m_lastError != 0) {
        emit errorOccurred(crd, m_lastError, QStringLiteral("arcYZR: ") + lastErrorString());
        return false;
    }
    return true;
}

bool InterpolationMgr::arcYZByCenter(short crd, long y, long z, double yCenter, double zCenter,
    short circleDir, double synVel, double synAcc,
    double velEnd, short fifo) 
{
    if (!checkCrd(crd)) {
        emit errorOccurred(crd, -1, QStringLiteral("坐标系号无效: %1").arg(crd));
        return false;
    }
    m_lastError = GtsHal::arcYZC(crd, y, z, yCenter, zCenter, circleDir, synVel, synAcc, velEnd, fifo);
    if (m_lastError != 0) {
        emit errorOccurred(crd, m_lastError, QStringLiteral("arcYZC: ") + lastErrorString());
        return false;
    }
    return true;
}

bool InterpolationMgr::arcZXByRadius(short crd, long z, long x, double radius, short circleDir,
    double synVel, double synAcc, double velEnd, short fifo) 
{
    if (!checkCrd(crd)) {
        emit errorOccurred(crd, -1, QStringLiteral("坐标系号无效: %1").arg(crd));
        return false;
    }
    m_lastError = GtsHal::arcZXR(crd, z, x, radius, circleDir, synVel, synAcc, velEnd, fifo);
    if (m_lastError != 0) {
        emit errorOccurred(crd, m_lastError, QStringLiteral("arcZXR: ") + lastErrorString());
        return false;
    }
    return true;
}

bool InterpolationMgr::arcZXByCenter(short crd, long z, long x, double zCenter, double xCenter,
    short circleDir, double synVel, double synAcc,
    double velEnd, short fifo) 
{
    if (!checkCrd(crd)) {
        emit errorOccurred(crd, -1, QStringLiteral("坐标系号无效: %1").arg(crd));
        return false;
    }
    m_lastError = GtsHal::arcZXC(crd, z, x, zCenter, xCenter, circleDir, synVel, synAcc, velEnd, fifo);
    if (m_lastError != 0) {
        emit errorOccurred(crd, m_lastError, QStringLiteral("arcZXC: ") + lastErrorString());
        return false;
    }
    return true;
}

bool InterpolationMgr::arcXYZ(short crd, long x, long y, long z,
    double interX, double interY, double interZ,
    double synVel, double synAcc, double velEnd, short fifo) 
{
    if (!checkCrd(crd)) {
        emit errorOccurred(crd, -1, QStringLiteral("坐标系号无效: %1").arg(crd));
        return false;
    }
    m_lastError = GtsHal::arcXYZ(crd, x, y, z, interX, interY, interZ, synVel, synAcc, velEnd, fifo);
    if (m_lastError != 0) {
        emit errorOccurred(crd, m_lastError, QStringLiteral("arcXYZ: ") + lastErrorString());
        return false;
    }
    return true;
}

bool InterpolationMgr::helixXYRZ(short crd, long x, long y, long z, double radius, short circleDir,
    double synVel, double synAcc, double velEnd, short fifo) 
{
    if (!checkCrd(crd)) {
        emit errorOccurred(crd, -1, QStringLiteral("坐标系号无效: %1").arg(crd));
        return false;
    }
    m_lastError = GtsHal::helixXYRZ(crd, x, y, z, radius, circleDir, synVel, synAcc, velEnd, fifo);
    if (m_lastError != 0) {
        emit errorOccurred(crd, m_lastError, QStringLiteral("helixXYRZ: ") + lastErrorString());
        return false;
    }
    return true;
}

bool InterpolationMgr::helixXYCZ(short crd, long x, long y, long z, double xCenter, double yCenter,
    short circleDir, double synVel, double synAcc,
    double velEnd, short fifo) 
{
    if (!checkCrd(crd)) {
        emit errorOccurred(crd, -1, QStringLiteral("坐标系号无效: %1").arg(crd));
        return false;
    }
    m_lastError = GtsHal::helixXYCZ(crd, x, y, z, xCenter, yCenter, circleDir, synVel, synAcc, velEnd, fifo);
    if (m_lastError != 0) {
        emit errorOccurred(crd, m_lastError, QStringLiteral("helixXYCZ: ") + lastErrorString());
        return false;
    }
    return true;
}

bool InterpolationMgr::bufIO(short crd, unsigned short doType, unsigned short doMask,
    unsigned short doValue, short fifo) 
{
    if (!checkCrd(crd)) {
        emit errorOccurred(crd, -1, QStringLiteral("坐标系号无效: %1").arg(crd));
        return false;
    }
    m_lastError = GtsHal::bufIO(crd, doType, doMask, doValue, fifo);
    if (m_lastError != 0) {
        emit errorOccurred(crd, m_lastError, QStringLiteral("bufIO: ") + lastErrorString());
        return false;
    }
    return true;
}

bool InterpolationMgr::bufDelay(short crd, unsigned short delayTime, short fifo) 
{
    if (!checkCrd(crd)) {
        emit errorOccurred(crd, -1, QStringLiteral("坐标系号无效: %1").arg(crd));
        return false;
    }
    m_lastError = GtsHal::bufDelay(crd, delayTime, fifo);
    if (m_lastError != 0) {
        emit errorOccurred(crd, m_lastError, QStringLiteral("bufDelay: ") + lastErrorString());
        return false;
    }
    return true;
}

bool InterpolationMgr::bufDA(short crd, short chn, short daValue, short fifo) 
{
    if (!checkCrd(crd)) {
        emit errorOccurred(crd, -1, QStringLiteral("坐标系号无效: %1").arg(crd));
        return false;
    }
    m_lastError = GtsHal::bufDA(crd, chn, daValue, fifo);
    if (m_lastError != 0) {
        emit errorOccurred(crd, m_lastError, QStringLiteral("bufDA: ") + lastErrorString());
        return false;
    }
    return true;
}

bool InterpolationMgr::bufMove(short crd, short moveAxis, long pos, double vel, double acc,
    short modal, short fifo) 
{
    if (!checkCrd(crd)) {
        emit errorOccurred(crd, -1, QStringLiteral("坐标系号无效: %1").arg(crd));
        return false;
    }
    m_lastError = GtsHal::bufMove(crd, moveAxis, pos, vel, acc, modal, fifo);
    if (m_lastError != 0) {
        emit errorOccurred(crd, m_lastError, QStringLiteral("bufMove: ") + lastErrorString());
        return false;
    }
    return true;
}

bool InterpolationMgr::bufGear(short crd, short gearAxis, long pos, short fifo) 
{
    if (!checkCrd(crd)) {
        emit errorOccurred(crd, -1, QStringLiteral("坐标系号无效: %1").arg(crd));
        return false;
    }
    m_lastError = GtsHal::bufGear(crd, gearAxis, pos, fifo);
    if (m_lastError != 0) {
        emit errorOccurred(crd, m_lastError, QStringLiteral("bufGear: ") + lastErrorString());
        return false;
    }
    return true;
}

bool InterpolationMgr::bufStop(short crd, long mask, long option, short fifo) 
{
    if (!checkCrd(crd)) {
        emit errorOccurred(crd, -1, QStringLiteral("坐标系号无效: %1").arg(crd));
        return false;
    }
    m_lastError = GtsHal::bufStop(crd, mask, option, fifo);
    if (m_lastError != 0) {
        emit errorOccurred(crd, m_lastError, QStringLiteral("bufStop: ") + lastErrorString());
        return false;
    }
    return true;
}

bool InterpolationMgr::bufMoveJog(short crd, short moveAxis, double vel, double acc,
    short modal, short fifo) 
{
    if (!checkCrd(crd)) {
        emit errorOccurred(crd, -1, QStringLiteral("坐标系号无效: %1").arg(crd));
        return false;
    }
    m_lastError = GtsHal::bufMoveJog(crd, moveAxis, vel, acc, modal, fifo);
    if (m_lastError != 0) {
        emit errorOccurred(crd, m_lastError, QStringLiteral("bufMoveJog: ") + lastErrorString());
        return false;
    }
    return true;
}

bool InterpolationMgr::start(short mask, short option) 
{
    m_lastError = GtsHal::crdStart(mask, option);
    if (m_lastError != 0) {
        emit errorOccurred(-1, m_lastError, QStringLiteral("crdStart: ") + lastErrorString());
        return false;
    }
    return true;
}

bool InterpolationMgr::startStep(short mask, short option) 
{
    m_lastError = GtsHal::crdStartStep(mask, option);
    if (m_lastError != 0) {
        emit errorOccurred(-1, m_lastError, QStringLiteral("crdStartStep: ") + lastErrorString());
        return false;
    }
    return true;
}

bool InterpolationMgr::setStepMode(short mask, short option) 
{
    m_lastError = GtsHal::crdStepMode(mask, option);
    if (m_lastError != 0) {
        emit errorOccurred(-1, m_lastError, QStringLiteral("crdStepMode: ") + lastErrorString());
        return false;
    }
    return true;
}

bool InterpolationMgr::clear(short crd, short fifo) 
{
    if (!checkCrd(crd)) {
        emit errorOccurred(crd, -1, QStringLiteral("坐标系号无效: %1").arg(crd));
        return false;
    }
    m_lastError = GtsHal::crdClear(crd, fifo);
    if (m_lastError != 0) {
        emit errorOccurred(crd, m_lastError, QStringLiteral("crdClear: ") + lastErrorString());
        return false;
    }
    return true;
}

long InterpolationMgr::freeSpace(short crd, short fifo) const 
{
    if (!checkCrd(crd)) return -1;
    long space = 0;
    GtsHal::crdSpace(crd, &space, fifo);
    return space;
}

bool InterpolationMgr::status(short crd, short& running, long& segment, short fifo) const 
{
    if (!checkCrd(crd)) return false;
    m_lastError = GtsHal::crdStatus(crd, &running, &segment, fifo);
    return m_lastError == 0;
}

bool InterpolationMgr::getCrdPosition(short crd, double* pPos) const 
{
    if (!checkCrd(crd)) return false;
    m_lastError = GtsHal::getCrdPos(crd, pPos);
    return m_lastError == 0;
}

double InterpolationMgr::getCrdVelocity(short crd) const 
{
    if (!checkCrd(crd)) return 0.0;
    double vel = 0.0;
    GtsHal::getCrdVel(crd, &vel);
    return vel;
}

bool InterpolationMgr::setOverride(short crd, double synVelRatio) 
{
    if (!checkCrd(crd)) {
        emit errorOccurred(crd, -1, QStringLiteral("坐标系号无效: %1").arg(crd));
        return false;
    }
    m_lastError = GtsHal::setOverride(crd, synVelRatio);
    if (m_lastError != 0) {
        emit errorOccurred(crd, m_lastError, QStringLiteral("setOverride: ") + lastErrorString());
        return false;
    }
    return true;
}

bool InterpolationMgr::setOverride2(short crd, double synVelRatio) 
{
    if (!checkCrd(crd)) {
        emit errorOccurred(crd, -1, QStringLiteral("坐标系号无效: %1").arg(crd));
        return false;
    }
    m_lastError = GtsHal::setOverride2(crd, synVelRatio);
    if (m_lastError != 0) {
        emit errorOccurred(crd, m_lastError, QStringLiteral("setOverride2: ") + lastErrorString());
        return false;
    }
    return true;
}

bool InterpolationMgr::setMaxOverrideLA(double maxSynVelRatio) 
{
    m_lastError = GtsHal::setMaxOverrideLA(maxSynVelRatio);
    if (m_lastError != 0) {
        emit errorOccurred(-1, m_lastError, QStringLiteral("setMaxOverrideLA: ") + lastErrorString());
        return false;
    }
    return true;
}


bool InterpolationMgr::setUserSegment(short crd, long segNum, short fifo) 
{
    if (!checkCrd(crd)) {
        emit errorOccurred(crd, -1, QStringLiteral("坐标系号无效: %1").arg(crd));
        return false;
    }
    m_lastError = GtsHal::setUserSegNum(crd, segNum, fifo);
    if (m_lastError != 0) {
        emit errorOccurred(crd, m_lastError, QStringLiteral("setUserSegNum: ") + lastErrorString());
        return false;
    }
    return true;
}

long InterpolationMgr::getUserSegment(short crd, short fifo) const 
{
    if (!checkCrd(crd)) return -1;
    long seg = 0;
    GtsHal::getUserSegNum(crd, &seg, fifo);
    return seg;
}

long InterpolationMgr::getRemainingSegment(short crd, short fifo) const 
{
    if (!checkCrd(crd)) return -1;
    long seg = 0;
    GtsHal::getRemainderSegNum(crd, &seg, fifo);
    return seg;
}

bool InterpolationMgr::setBufferMode(short crd, short bufferMode, short fifo) 
{
    if (!checkCrd(crd)) {
        emit errorOccurred(crd, -1, QStringLiteral("坐标系号无效: %1").arg(crd));
        return false;
    }
    m_lastError = GtsHal::setCrdBufferMode(crd, bufferMode, fifo);
    if (m_lastError != 0) {
        emit errorOccurred(crd, m_lastError, QStringLiteral("setCrdBufferMode: ") + lastErrorString());
        return false;
    }
    return true;
}

short InterpolationMgr::getBufferMode(short crd, short fifo) const 
{
    if (!checkCrd(crd)) return -1;
    short mode = 0;
    GtsHal::getCrdBufferMode(crd, &mode, fifo);
    return mode;
}


bool InterpolationMgr::moveToXY(short crd, long x, long y, double vel, double acc) 
{
    // 快速直线移动：先清空缓冲区，添加直线段，启动
    if (!checkCrd(crd)) {
        emit errorOccurred(crd, -1, QStringLiteral("坐标系号无效: %1").arg(crd));
        return false;
    }

    // 清除缓冲区
    GtsHal::crdClear(crd, 0);
    GtsHal::crdClear(crd, 1);

    // 添加直线插补段
    m_lastError = GtsHal::lnXY(crd, x, y, vel, acc, 0, 0);
    if (m_lastError != 0) {
        emit errorOccurred(crd, m_lastError, QStringLiteral("lnXY: ") + lastErrorString());
        return false;
    }

    // 启动运动
    m_lastError = GtsHal::crdStart(1L << crd, 0);
    if (m_lastError != 0) {
        emit errorOccurred(crd, m_lastError, QStringLiteral("crdStart: ") + lastErrorString());
        return false;
    }

    return true;
}

bool InterpolationMgr::stop(short crd, long option) 
{
    if (!checkCrd(crd)) {
        emit errorOccurred(crd, -1, QStringLiteral("坐标系号无效: %1").arg(crd));
        return false;
    }
    long mask = 1L << crd;
    m_lastError = GtsHal::stop(mask, option);
    if (m_lastError != 0) {
        emit errorOccurred(crd, m_lastError, QStringLiteral("stop: ") + lastErrorString());
        return false;
    }
    return true;
}

QString InterpolationMgr::lastErrorString() const 
{
    return GtsErrorToString(m_lastError);
}
