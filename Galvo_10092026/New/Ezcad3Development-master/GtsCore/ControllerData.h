#pragma once

enum class CardMode : short
{
    Normal = 0,  // 正常模式
    Debug = 1,   // 调试模式
    NoCard = 2,  // 无板卡模拟模式
};

// 输入类型
enum class DIType : short
{ 
    LimitPositive = 0,   // MC_LIMIT_POSITIVE  正限位
    LimitNegative = 1,   // MC_LIMIT_NEGATIVE  负限位
    Alarm = 2,           // MC_ALARM           驱动报警
    Home = 3,            // MC_HOME            原点
    GPI = 4,             // MC_GPI             通用输入
    Arrive = 5,          // MC_ARRIVE          电机到位
    MPG = 6              // MC_MPG             手轮
};

// 输出类型
enum class DOType : short
{
    ServoOn = 0,   // MC_SERVO_ON  伺服使能
    AlmClear = 1,  // MC_ALM_CLEAR 报警清除
    GPO = 2        // MC_GPO       通用输出
};

// 输入类型转字符串
inline QString DITypeToString(DIType type)
{
    switch (type) {
    case DIType::LimitPositive: return QStringLiteral("正限位");
    case DIType::LimitNegative: return QStringLiteral("负限位");
    case DIType::Alarm:         return QStringLiteral("驱动报警");
    case DIType::Home:          return QStringLiteral("原点");
    case DIType::GPI:           return QStringLiteral("通用输入");
    case DIType::Arrive:        return QStringLiteral("电机到位");
    case DIType::MPG:           return QStringLiteral("手轮");
    default:                    return QStringLiteral("未知");
    }
}

// 脉冲输出模式
enum class PulseMode : short
{
    PulseDir = 0,   // 脉冲 + 方向
    CCW_CW = 1      // 双脉冲(正转/反转)
};

// IO极性
enum class IOPolarity : short
{
    Normal = 0,    // 正常
    Reverse = 1    // 取反
};

// 脉冲计数源
enum class PulseCountSource : short
{
    Encoder = 0,     // 编码器
    PulseCounter = 1 // 脉冲计数器
};

// 触发沿
enum class TriggerEdge : short
{
    Rising = 0,    // 上升沿
    Falling = 1    // 下降沿
};

// 控制模式
enum class ControlMode : short
{
    ClosedLoop = 0,   // 闭环:有电机 + 编码器
    OpenLoop = 1,     // 开环:有电机 + 脉冲计数器
    Simulation = 2    // 调试:无电机 + 脉冲计数器
};

// 轴名称
enum class AxisName : short
{
    X = 0, Y = 1, Z = 2, A = 3,
};

inline QString axisNameToString(AxisName n)
{
    switch (n) {
    case AxisName::X: return QStringLiteral("X");
    case AxisName::Y: return QStringLiteral("Y");
    case AxisName::Z: return QStringLiteral("Z");
    case AxisName::A: return QStringLiteral("A");
    default:          return QStringLiteral("?");
    }
}

enum class HomeMode : short
{
    HomeMode_nLlimit = 0,   // 负限位回零
    HomeMode_pLlimit = 1,   // 正限位回零
    HomeMode_Home = 2,      // 原点回零
    HomeMode_HomeIndex = 3, // 原点 + Index 回零
    HomeMode_Index = 4,     // Index 回零
};

// 板卡信息
struct CardInfo {
    short cardNum;
    short cardType;
};

// 驱动版本
struct DriverVersion {
    unsigned short mainVer;
    unsigned short slaveVer;
};

// DI 状态
struct DI
{
    std::vector<int> posLimit;    // 正限位,8 位
    std::vector<int> negLimit;    // 负限位,8 位
    std::vector<int> alarm;     // 驱动报警,8 位
    std::vector<int> home;      // 原点信号,8 位
    std::vector<int> GPI;       // 通用输入,16 位
    std::vector<int> arrive;    // 电机到位,8 位
    std::vector<int> handwheel; // 手轮输入,8 位

    DI() {
        posLimit.resize(8, 0);
        negLimit.resize(8, 0);
        alarm.resize(8, 0);
        home.resize(8, 0);
        GPI.resize(16, 0);
        arrive.resize(8, 0);
        handwheel.resize(8, 0);
    }

    // 展平为 64 位，与表格行号一一对应
    std::vector<int> toFlatVector() const {
        std::vector<int> flat;
        flat.insert(flat.end(), posLimit.begin(), posLimit.end());    // 0~7
        flat.insert(flat.end(), negLimit.begin(), negLimit.end());    // 8~15
        flat.insert(flat.end(), alarm.begin(), alarm.end());          // 16~23
        flat.insert(flat.end(), home.begin(), home.end());            // 24~31
        flat.insert(flat.end(), GPI.begin(), GPI.end());              // 32~47
        flat.insert(flat.end(), arrive.begin(), arrive.end());        // 48~55
        flat.insert(flat.end(), handwheel.begin(), handwheel.end());  // 56~63
        return flat;
    }
};

// DO 状态
struct DO
{
    std::vector<int> servoOn;   // 伺服使能,8 位
    std::vector<int> almClear;  // 报警清除,8 位
    std::vector<int> GPO;       // 通用输出,16 位

    DO() {
        servoOn.resize(8, 0);
        almClear.resize(8, 0);
        GPO.resize(16, 0);
    }

    std::vector<int> toFlatVector() const {
        std::vector<int> flat;
        flat.insert(flat.end(), servoOn.begin(), servoOn.end());    // 0~7
        flat.insert(flat.end(), almClear.begin(), almClear.end());  // 8~15
        flat.insert(flat.end(), GPO.begin(), GPO.end());            // 16~31
        return flat;
    }
};

// 时钟
struct Clock {
    unsigned long sysClock;            // 系统时钟
    unsigned long highPrecClock;       // 高精度时钟

    Clock() : sysClock(0), highPrecClock(0) {}
};

// 当量
struct ScaleFactor
{
    long alpha = 1;
    long beta = 1;
};

// 轴限位
struct AxisLimit
{
    double posLimit = 0.0;
    double negLimit = 0.0;
};

// 回零参数
struct AxisHomeConfig
{
    enum HomeMode homeMode = HomeMode::HomeMode_nLlimit;
    double homeVel = 10.0; // 回零速度 mm/ms = m/s
    double homeAcc = 5.0;  // 回零加速度 mm/ms^2 = m/s^2
    double homeRange = 1000.0; // 回零距离 mm
    double homeOffset = 0.0;// 回零偏移 mm
};

// 点位运动(trap)参数
struct TrapParam
{
    double motionVel;       // 运动速度 mm/ms = m/s
    double lengthMm;        // 运动距离 mm
    double acc;             // 加速度 mm/ms^2 = m/s^2
    double dec;             // 减速度 mm/ms^2 = m/s^2
    int somoothTime;        // 平滑时间 ms
    int cycleTimes;         // 循环次数
    int delay;              // 到位延时 ms

    TrapParam()
        : motionVel(0.01)
        , lengthMm(1.0)
        , acc(0.01)
        , dec(0.01)
        , somoothTime(0)
        , cycleTimes(0)
        , delay(0)
    {
    }
};

// jog运动参数
struct JogParam
{
    double motionVel;       // 运动速度 mm/ms = m/s
    double acc;             // 加速度 mm/ms^2 = m/s^2
    double dec;             // 减速度 mm/ms^2 = m/s^2
    double smoothTime;      // 平滑时间 ms

    JogParam()
        : motionVel(0.01)
        , acc(0.01)
        , dec(0.01)
        , smoothTime(0.0)
    {
    }
};

// 单轴配置
struct SingleAxisConfig
{
    AxisName name = AxisName::X;
    // alpha(mm) / beta(pulse), 1/100 即 1mm = 100pulse
    ScaleFactor softPulseScale{ 1, 100 };
    // 规划器当量
    ScaleFactor profileScale{ 1, 1 };
    // 编码器当量
    ScaleFactor encScale{ 1, 1 };
    // 轴模式
    ControlMode ctrlMode = ControlMode::ClosedLoop;
    // 轴限位
    AxisLimit axisLimit;
    // 回零参数
    AxisHomeConfig axisHomeConfig;
    // trap点位运动参数
    TrapParam trapParam;
    // jog运动参数
    JogParam jogParam;
    // DAC零漂
    short dacBias = 0;
    // DAC饱和极限
    short dacLimit = 32767;
    // 跟随误差限
    long  followingErrorLimit = 32767;
    // 平滑停止加速度 mm/ms^2 = m/s^2
    double smoothStopDec = 100.0; 
    // 急停加速度 mm/ms^2 = m/s^2
    double estopDec = 0.1;
};


// 轴配置集合
struct AxisConfig
{
    std::vector<SingleAxisConfig> axes;
};


// 轴信息
struct SingleAxisInfo
{
    // 轴状态
    short axisIndex;    // 轴号1-4
    bool isAlarm;       // 报警
    bool isMError;      // 跟随误差越限
    bool isPosLimit;    // 正限位触发
    bool isNegLimit;    // 负限位触发
    bool isSmoothStop;  // 平滑停止
    bool isAbruptStop;  // 急停
    bool isServoOn;     // 伺服使能
    bool isMotion;      // 规划器运动

    // ===== 规划器 =====
    double prfPosOriginal;    // 规划位置原始数据,已经经过当量换算
    double prfVelOriginal;    // 规划速度原始数据,已经经过当量换算
    double prfAccOriginal;    // 规划加速度原始数据,已经经过当量换算
    double prfPosMm;  // mm
    double prfVelMm;  // mm/ms = m/s
    double prfAccMm;  // mm/ms² = m/s²
    long prfMode;     // 运动模式
    long axisStatus;  // 轴状态

    // ===== 编码器 =====
    double encPos;    // 编码器位置
    double encVel;    // 编码器速度
    double encPosMm;  // 编码器换算位置(单位:mm)
    double encVelMm;  // 编码器换算速度(单位:mm/ms)

    SingleAxisInfo()
        : axisIndex(0)
        , isAlarm(false)
        , isMError(false)
        , isPosLimit(false)
        , isNegLimit(false)
        , isSmoothStop(false)
        , isAbruptStop(false)
        , isServoOn(false)
        , isMotion(false)
        , prfPosOriginal(0.0)
        , prfVelOriginal(0.0)
        , prfAccOriginal(0.0)
        , prfPosMm(0.0)
        , prfVelMm(0.0)
        , prfAccMm(0.0)
        , prfMode(0)
        , axisStatus(0)
        , encPos(0.0)
        , encVel(0.0)
        , encPosMm(0.0)
        , encVelMm(0.0)
    {
    }
    // 解析轴状态
    void parseStatus(long status) {
        axisStatus = status;
        isAlarm = (status & 0x02) != 0;
        isMError = (status & 0x10) != 0;
        isPosLimit = (status & 0x20) != 0;
        isNegLimit = (status & 0x40) != 0;
        isSmoothStop = (status & 0x80) != 0;
        isAbruptStop = (status & 0x100) != 0;
        isServoOn = (status & 0x200) != 0;
        isMotion = (status & 0x400) != 0;
    }
};

// 轴信息集合
struct AxisInfo
{
    std::vector<SingleAxisInfo> items;
    AxisInfo() = default;
    explicit AxisInfo(int count) : items(count) {}
};

// 运动模式转字符串
static QString motionModeToString(long mode)
{
    switch (mode) {
    case 0:  return QStringLiteral("点位运动(Trap)");
    case 1:  return QStringLiteral("Jog");
    case 2:  return QStringLiteral("PT");
    case 3:  return QStringLiteral("电子齿轮(Gear)");
    case 4:  return QStringLiteral("Follow");
    case 5:  return QStringLiteral("插补(Interpolation)");
    case 6:  return QStringLiteral("PVT");
    default: return QStringLiteral("未知(%1)").arg(mode);
    }
}

struct IODefault {
    int start;
    int count;
    const char* desc;
};

static const IODefault s_diDefaults[] = {
    {  0,  8, "正限位信号0xF"    },
    {  8,  8, "负限位信号0xF"    },
    { 16,  8, "驱动报警0xF"      },
    { 24,  8, "原点信号0xF"      },
    { 32, 16, "通用输入0xFFFF"    },
    { 48,  8, "电机到位0xF"      },
    { 56,  7, "手轮输入0x7F"     },
};

static const IODefault s_doDefaults[] = {
    {  0,  8, "伺服使能0xF"      },
    {  8,  8, "报警清除0xFF"     },
    { 16, 16, "通用输出0xFFFF"   },
};

static QString lookupDefault(int row, const IODefault* table, int count)
{
    for (int i = 0; i < count; ++i) {
        if (row >= table[i].start && row < table[i].start + table[i].count)
            return QString::fromLocal8Bit(table[i].desc);
    }
    return QString();
}

static QString defaultDIDescription(int row)
{
    return lookupDefault(row, s_diDefaults,
        sizeof(s_diDefaults) / sizeof(s_diDefaults[0]));
}

static QString defaultDODescription(int row)
{
    return lookupDefault(row, s_doDefaults,
        sizeof(s_doDefaults) / sizeof(s_doDefaults[0]));
}