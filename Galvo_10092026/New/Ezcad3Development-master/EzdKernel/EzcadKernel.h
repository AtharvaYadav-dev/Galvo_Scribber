
/*********************************
导出日期:2026/4/8 14:35:06
文档版本:Ver:1.2.9.6 Date:2026.04.08 L0 
*********************************/

#ifndef EZDKERNEL_H
#define EZDKERNEL_H

#ifndef _UNICODE
#define _UNICODE 
#endif
#ifndef UNICODE
#define UNICODE 
#endif

#ifdef __linux__
#include <dlfcn.h>
#include <unistd.h>
#include "WinToLinux.h"

#else
#include <tchar.h>
#include <windows.h>
#include <libloaderapi.h>
#endif
#include <string>
#include <cstring>
#include <locale>
#include <codecvt>
#include <vector>
#include "INIParser.h"

//********** E3_ID_Define **********
typedef INT_PTR E3_ID;
#define  INVALID 0 
//**********************************

//********** Struct_Define ********** 
	/// <summary>
	/// 2D对象坐标类型定义
	/// </summary>
struct Pt2d
{
public:
    Pt2d() { X = 0; Y = 0; }
    ~Pt2d() {}
    Pt2d(const double fx, const double fy) { X = fx; Y = fy; }
    double X = 0;
    double Y = 0;
    bool operator==(const Pt2d& rhs) const noexcept
    {
        return X == rhs.X && Y == rhs.Y;
    }
};

	/// <summary>
	/// 3D对象坐标类型定义
	/// </summary>
struct Pt3d
{
public:
    Pt3d() { X = 0; Y = 0; Z = 0; }
    Pt3d(const double fx, const double fy, const double fz) { X = fx; Y = fy; Z = fz; }
    ~Pt3d() {}
    double X = 0;
    double Y = 0;
    double Z = 0;
    void Set(const double& fx, const double& fy, const double& fz) { X = fx; Y = fy; Z = fz; }
    bool operator==(const Pt3d& rhs) const noexcept
    {
        return X == rhs.X && Y == rhs.Y && Z == rhs.Z;
    }
};

	/// <summary>
	/// 对象包装盒类型定义
	/// </summary>
struct Box2d
{
    Pt2d PosA;
    Pt2d PosB;
};

		/// <summary>
		/// 填充参数结构体定义
		/// </summary>
struct HatchParam
{
    //HatchParam的尺寸(默认是136即可)//20260323由120改为136
    int m_nHatchParamSize = 136;
    //填充使能
    int m_bEnableHatch = 0;
    //整体计算
    int m_bAllCalc = 0;
    //绕边
    int m_bFollowEdge = 0;
    //平均分布填充线
    int m_bAverageLine = 0;
    //反转
    int m_bLoopReverse = 0;
    //交叉填充
    int m_bCross = 0;
    //填充类型(0-6依次对应填充类型中从单向填充开始依次对应)
    int m_nHatchType = 0;
    //填充笔号
    int m_nPenNo = 0;
    //填充线间距
    double m_dHatchLineDist = 0.1;
    //填充线角度
    double m_dHatchAngle = 0;
    //填充线边距
    double m_dHatchEdgeDist = 0;
    //填充线起始偏移距离
    double m_dHatchStartOffset = 0;
    //填充线结束偏移距离
    double m_dHatchEndOffset = 0;
    //使能自动旋转
    int m_bEnableAutoRotate = 0;
    //旋转角度
    double m_dHatchRotateAngle = 0;
    //直线缩进
    double m_dHatchLineReduction = 0;
    //环间距
    double m_dHatchLoopDist = 0;
    //边界环数
    int m_nEdgeLoop = 0;
    //填充次数
    int m_nCycCount = 1;
    // 点填充间距
    double m_dHatchPointDist = 0;
    // 点填充模式
    int m_bHatchPointMode = 0;
};

		/// <summary>
		/// 分割参数类型定义
		/// </summary>
struct SplitBox
{
    double X1 = 0;
    double Y1 = 0;
    double X2 = 0;
    double Y2 = 0;
};

		/// <summary>
		/// 字型对象定义
		/// </summary>
struct FontRecord
{
    //字体名字
    TCHAR szFontName[256];
    //字体属性
    unsigned short dwFontAttrib = 0;
};

		/// <summary>
		/// 背景显示所用数据结构体.
		/// </summary>
struct BackBmpParam
{
    //位图宽度
    int nWidth = 0;
    //位图高度
    int nHeight = 0;
    //位图位数
    int nBitCount = 0;
    //m_pBMI中像素数据位置
    HWND pBits;
    //图像显示的位置的左下角X坐标
    double dShowPosLB_X = 0;
    //图像显示的位置的左下角Y坐标
    double dShowPosLB_Y = 0;
    //图像显示的位置的右上角X坐标
    double dShowPosRT_X = 0;
    //图像显示的位置的右上角Y坐标
    double dShowPosRT_Y = 0;
};


//**********************************

//********** Enum_Define **********
//执行结果码定义
enum E3_ERR
		{
			/// <summary>
			/// 函数运行成功
			/// </summary>
			ERR_SUCCESS = 0,
			/// <summary>
			/// 执行失败
			/// </summary>
			ERR_FAIL = 1,
			/// <summary>
			/// 错误输入参数
			ERR_ERRORPARAM = 2,
			/// <summary>
			/// 打开文件失败
			/// </summary>
			ERR_OPENFILE = 3,
			/// <summary>
			/// 没有加工对象
			/// </summary>
			ERR_NOENTITY = 4,
			/// <summary>
			/// ezcad已经运行
			/// </summary>
			ERR_EZCADRUN = 5,
			/// <summary>
			/// 客户ID不对
			/// </summary>
			ERR_CLIENTID = 6,
			/// <summary>
			/// 找不到卡
			/// </summary>
			ERR_NODEVICE = 7,
			/// <summary>
			/// 不支持的功能
			/// </summary>
			ERR_NOTSUPPORT = 8,
			/// <summary>
			/// 内存错误
			/// </summary>
			ERR_MEMORY = 9,
			/// <summary>
			/// 无法写程序,因为列表已经满
			/// </summary>
			ERR_WRITELISTFAIL2 = 10, 
			/// <summary>
			/// 校验码错误
			/// </summary>
			ERR_CHECKCODEERROR = 11,
			/// <summary>
			/// 无效的命令码
			/// </summary>
			ERR_INVALID_CMD = 21,
			/// <summary>
			/// 当前状态下不能执行此命令
			/// </summary>
			ERR_CANNT_RUN = 23,
			/// <summary>
			/// 执行命令超时
			/// </summary>
			ERR_CMD_OUTTIME = 24,
			/// <summary>
			/// 设备未注册
			/// </summary>
			ERR_UNREG = 25,
			/// <summary>
			/// 硬件校验未通过
			/// </summary>
			ERR_HWDISABLE = 26,
			/// <summary>
			/// 无法清空列表,因为列表正在执行
			/// </summary>
			ERR_CLEARLISTFAIL = 27,
			/// <summary>
			/// 用户中断标刻
			/// </summary>
			ERR_USER_STOP = 100,
			/// <summary>
			/// 无效的设备句柄
			/// </summary>
			ERR_INVALID_HAN = 101,
			/// <summary>
			/// 无效卡号
			/// </summary>
			ERR_INVALID_CARD = 102,
			/// <summary>
			/// 已经注册了
			/// </summary>
			ERR_ALREADY_REG = 103,
			/// <summary>
			/// 发现中断标刻信号
			/// </summary>
			ERR_STOPSIGNAL = 110,
			/// <summary>
			/// 超出加工范围
			/// </summary>
			ERR_OUTRANGE = 120,
			/// <summary>
			/// 飞行速度太快
			/// </summary>
			ERR_FLYSPEEDFAST = 121,
			/// <summary>
			/// 当前加工内容重复
			/// </summary>
			ERR_CONTENTREPEAT = 122,
			/// <summary>
			/// 连接服务器失败
			/// </summary>
			ERR_CONNECTHOST = 130,
			/// <summary>
			/// 安全门被打开
			/// </summary>
			ERR_DOOROPEN = 131,
			/// <summary>
			/// 用户中断扩展轴运动
			/// </summary>
			ERR_USER_AXISSTOP = 140,
			/// <summary>
			/// 异常
			/// </summary>
			ERR_ASSERT = 200,
			/// <summary>
			/// 没有曲面
			/// </summary>
			ERR_NOMESH = 301,
			/// <summary>
			/// 扩展轴没有回零
			/// </summary>
			ERR_NOTHOME = 400,
			/// <summary>
			/// 扩展轴移动失败
			/// </summary>
			ERR_MOVEFAIL = 403,
			/// <summary>
			/// 扩展轴左硬限位触发
			/// </summary>
			ERR_HARDLEFTLIMIT= 404,
			/// <summary>
			/// 扩展轴右硬限位触发
			/// </summary>
			ERR_HARDRIGHTLIMIT= 405,
			/// <summary>
			/// 网络通讯异常
			/// </summary>
			ERR_ETHERR = 406,
};

		/// <summary>
		/// F3参数Int值类型查询索引定义
		/// </summary>
		enum class F3IntParamKey
		{
			/// <summary>
			/// 未定义;
			/// </summary>
			Int_0,
			/// <summary>
			/// 区域-振镜2 = X;1=使能;0=未使能;
			/// </summary>
			Int_1,
			/// <summary>
			/// 区域-反转X;1=使能;0=未使能;
			/// </summary>
			Int_2,
			/// <summary>
			/// 区域-反转Y;1=使能;0=未使能;
			/// </summary>
			Int_3,
			/// <summary>
			/// 区域-校正-使用校正文件;1=使能;0=未使能;
			/// </summary>
			Int_4,
			/// <summary>
			/// 区域-加工后是否去指定位置;1=使能;0=未使能;
			/// </summary>
			Int_5,
			/// <summary>
			/// 激光器类型;0=CO2;1=YAG;2=FIBER;3=SPI;4=QCW;映射到[LaserCategory]枚举;
			/// </summary>
			Int_6,
			/// <summary>
			/// CO2是否使能预电离;1=使能;0=未使能;
			/// </summary>
			Int_7,
			/// <summary>
			/// 未定义;
			/// </summary>
			Int_8,
			/// <summary>
			/// 超脉冲模式;
			/// </summary>
			Int_9,
			/// <summary>
			/// CO2-预电离-脉冲宽度(us);
			/// </summary>
			Int_10,
			/// <summary>
			/// CO2-预电离-脉冲频率(Hz);
			/// </summary>
			Int_11,
			/// <summary>
			/// YAG脉宽反转;1=使能;0=未使能;
			/// </summary>
			Int_12,
			/// <summary>
			/// YAG当首脉冲抑制结束时开Q开关;1=使能;0=未使能;
			/// </summary>
			Int_13,
			/// <summary>
			/// YAG首脉冲抑制(us);
			/// </summary>
			Int_14,
			/// <summary>
			/// 使能电流模拟输出;
			/// </summary>
			Int_15,
			/// <summary>
			/// 使能模拟首脉冲抑制;
			/// </summary>
			Int_16,
			/// <summary>
			/// YAG首脉冲抑制从低到高;
			/// </summary>
			Int_17,
			/// <summary>
			/// 抑制使能阈值时间T1;
			/// </summary>
			Int_18,
			/// <summary>
			/// 抑制使能预知时间T2;
			/// </summary>
			Int_19,
			/// <summary>
			/// 光纤激光器类型;映射到[FiberCategory]枚举.;
			/// </summary>
			Int_20,
			/// <summary>
			/// 是否MO常开;
			/// </summary>
			Int_21,
			/// <summary>
			/// 是否卡有使能列表开关Mo指令;
			/// </summary>
			Int_22,
			/// <summary>
			/// 是否使能光纤激光器的漏光处理;
			/// </summary>
			Int_23,
			/// <summary>
			/// 是否使能光纤激光器的脉冲宽度参数;
			/// </summary>
			Int_24,
			/// <summary>
			/// 激光全局-禁止检测激光状态;1=使能;0=未使能;
			/// </summary>
			Int_25,
			/// <summary>
			/// 是否使能频率tickle模式;
			/// </summary>
			Int_26,
			/// <summary>
			/// 开启MO延时;
			/// </summary>
			Int_27,
			/// <summary>
			/// SPI波形使能;
			/// </summary>
			Int_28,
			/// <summary>
			/// SPI连续模式;
			/// </summary>
			Int_29,
			/// <summary>
			/// 红光指示-红光指示-显示轮廓;1=使能;0=未使能;
			/// </summary>
			Int_30,
			/// <summary>
			/// 红光连续模式;
			/// </summary>
			Int_31,
			/// <summary>
			/// 端口-输出-红光指示-端口;-1=无;最大15;
			/// </summary>
			Int_32,
			/// <summary>
			/// 端口-输出-红光指示-低电平有效;1=使能;0=未使能;
			/// </summary>
			Int_33,
			/// <summary>
			/// 端口-输入-红光指示开始端口-端口;-1=无;最大15;
			/// </summary>
			Int_34,
			/// <summary>
			/// 端口-输入-红光指示开始端口-低电平有效;1=使能;0=未使能;
			/// </summary>
			Int_35,
			/// <summary>
			/// 端口-输入-开始标刻端口;-1=无;最大15;
			/// </summary>
			Int_36,
			/// <summary>
			/// 端口-输入-开始标刻端口-低电平有效;1=使能;0=未使能;
			/// </summary>
			Int_37,
			/// <summary>
			/// 端口-输入-开始标刻端口-开始信号脉冲模式;1=使能;0=未使能;
			/// </summary>
			Int_38,
			/// <summary>
			/// 使能标刻开始信号锁存模式;
			/// </summary>
			Int_39,
			/// <summary>
			/// 端口-输出-标刻结束信号-端口;-1=无;最大15;
			/// </summary>
			Int_40,
			/// <summary>
			/// 端口-输出-标刻结束信号-低电平有效;1=使能;0=未使能;
			/// </summary>
			Int_41,
			/// <summary>
			/// 端口-输出-标刻结束信号-脉冲宽度[ms];1-1000000;
			/// </summary>
			Int_42,
			/// <summary>
			/// 结束标刻延时;
			/// </summary>
			Int_43,
			/// <summary>
			/// 端口-输出-标刻输出口-端口;-1=无;最大15;
			/// </summary>
			Int_44,
			/// <summary>
			/// 端口-输出-标刻输出口-低电平有效;1=使能;0=未使能;
			/// </summary>
			Int_45,
			/// <summary>
			/// 其他-开始标刻延时;0-100000;
			/// </summary>
			Int_46,
			/// <summary>
			/// 飞行标刻-飞行标刻-使能;1=使能;0=未使能;
			/// </summary>
			Int_47,
			/// <summary>
			/// 端口-输入-安全门端口-端口;-1=无;最大15;
			/// </summary>
			Int_48,
			/// <summary>
			/// 端口-输入-安全门端口-低电平有效;1=使能;0=未使能;
			/// </summary>
			Int_49,
			/// <summary>
			/// 端口-输出-激光电源输出口-端口;-1=无;最大15;
			/// </summary>
			Int_50,
			/// <summary>
			/// 端口-输出-激光电源输出口-低电平有效;1=使能;0=未使能;
			/// </summary>
			Int_51,
			/// <summary>
			/// 端口-输入-激光器准备好端口-端口;-1=无;最大15;
			/// </summary>
			Int_52,
			/// <summary>
			/// 端口-输入-激光器准备好端口-低电平有效;1=使能;0=未使能;
			/// </summary>
			Int_53,
			/// <summary>
			/// 激光准备好输出端口, 激光报警信号;
			/// </summary>
			Int_54,
			/// <summary>
			/// 激光准备好输出端口低电平有效;
			/// </summary>
			Int_55,
			/// <summary>
			/// 激光器休眠时间;
			/// </summary>
			Int_56,
			/// <summary>
			/// 总零件数目;
			/// </summary>
			Int_57,
			/// <summary>
			/// 使能显示开始标刻对话框;
			/// </summary>
			Int_58,
			/// <summary>
			/// 其他-加工到指定数目后禁止加工;1=使能;0=未使能;
			/// </summary>
			Int_59,
			/// <summary>
			/// 其他-自动复位加工次数;1=使能;0=未使能;
			/// </summary>
			Int_60,
			/// <summary>
			/// 停止加工输入端口-输入端口-高电平有效;Bit形式,0xffff,从低到高,bit=1代表这位端口使能高电平有效;
			/// </summary>
			Int_61,
			/// <summary>
			/// 停止加工输入端口-输入端口-低电平有效;Bit形式,0xffff,从低到高,bit=1代表这位端口使能低电平有效;
			/// </summary>
			Int_62,
			/// <summary>
			/// 使能支持外部文件;
			/// </summary>
			Int_63,
			/// <summary>
			/// 使能密码;
			/// </summary>
			Int_64,
			/// <summary>
			/// 光纤更改脉冲宽度的延时;
			/// </summary>
			Int_65,
			/// <summary>
			/// 是否使能光纤激光器的脉冲宽度索引模式;
			/// </summary>
			Int_66,
			/// <summary>
			/// 未定义;
			/// </summary>
			Int_67,
			/// <summary>
			/// 未定义;
			/// </summary>
			Int_68,
			/// <summary>
			/// 未定义;
			/// </summary>
			Int_69,
			/// <summary>
			/// Z轴是否反转;
			/// </summary>
			Int_70,
			/// <summary>
			/// 振镜输出模式, Xy2-100, Sl2-100.....;
			/// </summary>
			Int_71,
			/// <summary>
			/// 列表大小;
			/// </summary>
			Int_72,
			/// <summary>
			/// 飞行标刻-硬件模拟模式-使能;1=使能;0=未使能;
			/// </summary>
			Int_73,
			/// <summary>
			/// 飞行标刻-飞行标刻-编码器信号反向;1=使能;0=未使能;
			/// </summary>
			Int_74,
			/// <summary>
			/// 飞行标刻-飞行标刻-编码器只接A相;1=使能;0=未使能;
			/// </summary>
			Int_75,
			/// <summary>
			/// 飞行标刻-其他-使能流水线方向从右到左;1=使能;0=未使能;
			/// </summary>
			Int_76,
			/// <summary>
			/// 飞行标刻-其他-使能保持加工对象的顺序;1=使能;0=未使能;
			/// </summary>
			Int_77,
			/// <summary>
			/// 使能3D功能;
			/// </summary>
			Int_78,
			/// <summary>
			/// 光纤脉冲索引模式;
			/// </summary>
			Int_79,
			/// <summary>
			/// 未定义;
			/// </summary>
			Int_80,
			/// <summary>
			/// 使能波形控制;
			/// </summary>
			Int_81,
			/// <summary>
			/// 激光控制-频率-频率延时[ms];0-10000;
			/// </summary>
			Int_82,
			/// <summary>
			/// 输入IO掩码;
			/// </summary>
			Int_83,
			/// <summary>
			/// 输出IO掩码;
			/// </summary>
			Int_84,
			/// <summary>
			/// 其他-使能首次开启激光延时时间;1=使能;0=未使能;
			/// </summary>
			Int_85,
			/// <summary>
			/// 其他-使能首次开启激光延时时间-激光开启时间(us);
			/// </summary>
			Int_86,
			/// <summary>
			/// 光纤脉冲宽度的单位 0=ns 1=ps;
			/// </summary>
			Int_87,
			/// <summary>
			/// 笔参数显示优化参数;
			/// </summary>
			Int_88,
			/// <summary>
			/// 笔参数显示抖动参数;
			/// </summary>
			Int_89,
			/// <summary>
			/// 笔参数显示其他项;
			/// </summary>
			Int_90,
			/// <summary>
			/// 笔参数显示详细参数说明;
			/// </summary>
			Int_91,
			/// <summary>
			/// 笔参数显示功率渐变;
			/// </summary>
			Int_92,
			/// <summary>
			/// 笔参数显示速度渐变;
			/// </summary>
			Int_93,
			/// <summary>
			/// 使能密码;
			/// </summary>
			Int_94,
			/// <summary>
			/// 其他-条码点加工模式;0=正常模式;1=快速点模式;与97,155索引参数互斥;
			/// </summary>
			Int_95,
			/// <summary>
			/// DLC单列表模式;
			/// </summary>
			Int_96,
			/// <summary>
			/// 其他-条码点加工模式;0=未使能快速线模式;1=使能快速线模式;与95,155索引参数互斥;
			/// </summary>
			Int_97,
			/// <summary>
			/// 动态聚焦-动态聚焦-使能;1=使能;0=未使能;
			/// </summary>
			Int_98,
			/// <summary>
			/// 振镜-振镜-振镜类型;0=XY2_100_16;1=XY2_100_18;4=SL2_100_20;5=JCZ_100_18;6=CANON_20;7=CANON_64;8=XY2_100_16FB;9=RAYLASE_XY2_100;10=JCZ_100_24;;
			/// </summary>
			Int_99,
			/// <summary>
			/// 振镜-振镜-使能分析模式;1=使能;0=未使能;
			/// </summary>
			Int_100,
			/// <summary>
			/// 其他-每个对象后加延时[us];1-10000000;
			/// </summary>
			Int_101,
			/// <summary>
			/// 扩展轴方案-扩展轴方案;0=NONE;1=X;2=Y;3=Z;4=A;5=XY;6=XZ;7=YZ;8=XA;9=YA;10=ZA;11=XYZ;12=XYA;13=XZA;14=YZA;15=XYZA;16=XY_Sphere;17=XYZA_Free;
			/// </summary>
			Int_102,
			/// <summary>
			/// 焊接-焊接-使能;1=使能;0=未使能;
			/// </summary>
			Int_103,
			/// <summary>
			/// 端口-输入-Z分层-端口;-1=无;最大15;
			/// </summary>
			Int_104,
			/// <summary>
			/// 端口-输入-Z分层-低电平有效;1=使能;0=未使能;
			/// </summary>
			Int_105,
			/// <summary>
			/// 端口-输出-Z分层-端口;-1=无;最大15;
			/// </summary>
			Int_106,
			/// <summary>
			/// 端口-输出-Z分层-低电平有效;1=使能;0=未使能;
			/// </summary>
			Int_107,
			/// <summary>
			/// 输出端口Z分层端口脉冲宽度(1ms= 1000);
			/// </summary>
			Int_108,
			/// <summary>
			/// 激光控制-频率-PWM开启延时[us];0-1000000;
			/// </summary>
			Int_109,
			/// <summary>
			/// 其他-禁止隐藏的笔参数;1=使能;0=未使能;
			/// </summary>
			Int_110,
			/// <summary>
			/// 红光指示-红光指示-禁止扩展轴移动;1=使能;0=未使能;
			/// </summary>
			Int_111,
			/// <summary>
			/// 振镜-振镜-自动模式-使能自动调整;1=使能;0=未使能;
			/// </summary>
			Int_112,
			/// <summary>
			/// 振镜-振镜-自动模式-到位时间[us];10-1000000;
			/// </summary>
			Int_113,
			/// <summary>
			/// 振镜-振镜-自动模式-到位时间限制[us];10-1000000;
			/// </summary>
			Int_114,
			/// <summary>
			/// 激光错误复位信号为低;
			/// </summary>
			Int_115,
			/// <summary>
			/// 激光远程信号为低;
			/// </summary>
			Int_116,
			/// <summary>
			/// 飞行连续模式;
			/// </summary>
			Int_117,
			/// <summary>
			/// 其他-双点模式;1=使能;0=未使能;
			/// </summary>
			Int_118,
			/// <summary>
			/// 更改波形延时;
			/// </summary>
			Int_119,
			/// <summary>
			/// 笔参数显示延时;
			/// </summary>
			Int_120,
			/// <summary>
			/// 笔参数显示跳转;
			/// </summary>
			Int_121,
			/// <summary>
			/// 隐藏笔按钮;
			/// </summary>
			Int_122,
			/// <summary>
			/// 转镜功能;
			/// </summary>
			Int_123,
			/// <summary>
			/// 其他-激光开始延时只在起始段有效;1=使能;0=未使能;
			/// </summary>
			Int_124,
			/// <summary>
			/// 编码器是否互换使用 Y为1;
			/// </summary>
			Int_125,
			/// <summary>
			/// 编码器2信号反向;
			/// </summary>
			Int_126,
			/// <summary>
			/// 编码器2信号只有A;
			/// </summary>
			Int_127,
			/// <summary>
			/// 编码器2使能;
			/// </summary>
			Int_128,
			/// <summary>
			/// 笔参数显示匀速标刻参数;
			/// </summary>
			Int_129,
			/// <summary>
			/// 激光全局-禁止同步PRR信号;1=使能;0=未使能;
			/// </summary>
			Int_130,
			/// <summary>
			/// 其他-点模式中振镜跟随鼠标移动;1=使能;0=未使能;
			/// </summary>
			Int_131,
			/// <summary>
			/// 振镜优先模式;
			/// </summary>
			Int_132,
			/// <summary>
			/// 振镜自动调整模式;
			/// </summary>
			Int_133,
			/// <summary>
			/// 使能SKYWRITE模式;
			/// </summary>
			Int_134,
			/// <summary>
			/// SKYWRITE模式;
			/// </summary>
			Int_135,
			/// <summary>
			/// 未定义;
			/// </summary>
			Int_136,
			/// <summary>
			/// 未定义;
			/// </summary>
			Int_137,
			/// <summary>
			/// YAG类型;
			/// </summary>
			Int_138,
			/// <summary>
			/// 使能待机功率;
			/// </summary>
			Int_139,
			/// <summary>
			/// 端口-输出-激光故障-端口;-1=无;最大15;
			/// </summary>
			Int_140,
			/// <summary>
			/// 端口-输出-激光故障-低电平有效;1=使能;0=未使能;
			/// </summary>
			Int_141,
			/// <summary>
			/// 其他-断电自动保护文件;1=使能;0=未使能;
			/// </summary>
			Int_142,
			/// <summary>
			/// 未定义;
			/// </summary>
			Int_143,
			/// <summary>
			/// 振镜-振镜-使能跳转参数表模式;1=使能;0=未使能;
			/// </summary>
			Int_144,
			/// <summary>
			/// 总加工时间;
			/// </summary>
			Int_145,
			/// <summary>
			/// 总加工时间ms;
			/// </summary>
			Int_146,
			/// <summary>
			/// 其他-结束标刻延时;0-100000;
			/// </summary>
			Int_147,
			/// <summary>
			/// 端口-输出-飞行速度监测-端口;-1=无;最大15;
			/// </summary>
			Int_148,
			/// <summary>
			/// 端口-输出-飞行速度监测-低电平有效;1=使能;0=未使能;
			/// </summary>
			Int_149,
			/// <summary>
			/// 其他-禁止标刻圆模式;1=使能;0=未使能;
			/// </summary>
			Int_150,
			/// <summary>
			/// 振镜-振镜-首次跳转延时[us];-10000-10000;
			/// </summary>
			Int_151,
			/// <summary>
			/// 红光指示-红光指示-指示矩形模式;1=使能;0=未使能;
			/// </summary>
			Int_152,
			/// <summary>
			/// Z扩展轴模式下不移动对象的Z坐标;
			/// </summary>
			Int_153,
			/// <summary>
			/// 红光指示-红光指示-更新动态对象;1=使能;0=未使能;
			/// </summary>
			Int_154,
			/// <summary>
			/// 其他-条码点加工模式;0=未使能步距模式;1=使能步距模式;与95,97索引参数互斥;
			/// </summary>
			Int_155,
			/// <summary>
			/// 端口-输出-其他-使能激光器扩展输出口;1=使能;0=未使能;
			/// </summary>
			Int_156,
			/// <summary>
			/// 端口-输出-标刻失败端口-端口;-1=无;最大15;
			/// </summary>
			Int_157,
			/// <summary>
			/// 端口-输出-标刻失败端口-低电平有效;1=使能;0=未使能;
			/// </summary>
			Int_158,
			/// <summary>
			/// 端口-输出-标刻失败端口-脉冲宽度[ms];1-1000000;
			/// </summary>
			Int_159,
			/// <summary>
			/// 未定义;
			/// </summary>
			Int_160,
			/// <summary>
			/// 动态聚焦-动态聚焦-速度场-使能;1=使能;0=未使能;
			/// </summary>
			Int_161,
			/// <summary>
			/// 动态聚焦-动态聚焦-能量场-使能;1=使能;0=未使能;
			/// </summary>
			Int_162,
			/// <summary>
			/// 动态聚焦-曲线分布模式;0=一次分布;1=二次分布;2=三次分布;
			/// </summary>
			Int_163,
			/// <summary>
			/// 端口-输出-标刻输出口-整个加工周期有效;1=使能;0=未使能;
			/// </summary>
			Int_164,
			/// <summary>
			/// 显示频率线性变化参数;
			/// </summary>
			Int_165,
			/// <summary>
			/// 端口-输出-激光开光同步-端口;-1=无;最大15;
			/// </summary>
			Int_166,
			/// <summary>
			/// 端口-输出-激光开光同步-低电平有效;1=使能;0=未使能;
			/// </summary>
			Int_167,
			/// <summary>
			/// 脉宽更改后拉低MO, 拉低后需要拉高, 中间保持的时间和点击红光后拉低mo的时间一样;
			/// </summary>
			Int_168,
			/// <summary>
			/// CO2-使能首脉冲抑制;1=使能;0=未使能;
			/// </summary>
			Int_169,
			/// <summary>
			/// 飞行标刻-最小触发距离-使能;1=使能;0=未使能;
			/// </summary>
			Int_170,
			/// <summary>
			/// 飞行标刻-最小触发时间-使能;1=使能;0=未使能;
			/// </summary>
			Int_171,
			/// <summary>
			/// QCW红光需要反转;
			/// </summary>
			Int_172,
			/// <summary>
			/// 其他-单点重复加工模式;1=使能;0=未使能;
			/// </summary>
			Int_173,
			/// <summary>
			/// 填充笔参数使用Ezcad2旧模式;
			/// </summary>
			Int_174,
			/// <summary>
			/// 飞行标刻-其他-使能打散填充对象;1=使能;0=未使能;
			/// </summary>
			Int_175,
			/// <summary>
			/// 红光指示-红光指示-不刷新加工时间;1=使能;0=未使能;
			/// </summary>
			Int_176,
			/// <summary>
			/// 其他-使能标刻暂停模式;1=使能;0=未使能;
			/// </summary>
			Int_177,
			/// <summary>
			/// 红光指示-红光指示-禁止内部IO输出;1=使能;0=未使能;
			/// </summary>
			Int_178,
			/// <summary>
			/// 其他-使能圆弧标刻命令;1=使能;0=未使能;
			/// </summary>
			Int_179,
			/// <summary>
			/// 滤波时间;
			/// </summary>
			Int_180,
			/// <summary>
			/// QCW激光器类型(0: QCW-YLM 1:QCW-YLR);
			/// </summary>
			Int_181,
			/// <summary>
			/// QCW禁止检查脉宽极限值;
			/// </summary>
			Int_182,
			/// <summary>
			/// 红光指示-红光指示-不标刻的时候总是打开红光;1=使能;0=未使能;
			/// </summary>
			Int_183,
			/// <summary>
			/// 飞行标刻-其他-使能禁止排序;1=使能;0=未使能;
			/// </summary>
			Int_184,
			/// <summary>
			/// 输入端口-安全门端口;
			/// </summary>
			Int_185,
			/// <summary>
			/// 其他-切片对象一次只加工一层;1=使能;0=未使能;
			/// </summary>
			Int_186,
			/// <summary>
			/// 端口-输入-开始标刻端口-禁止锁存开始信号;1=使能;0=未使能;
			/// </summary>
			Int_187,
			/// <summary>
			/// 其他-禁止连续加工模式的优化模式;1=使能;0=未使能;
			/// </summary>
			Int_188,
			/// <summary>
			/// 其他-保证产品完整标记结束;1=使能;0=未使能;
			/// </summary>
			Int_189,
			/// <summary>
			/// 激光全局-禁止修改笔参数时改变激光器参数;1=使能;0=未使能;
			/// </summary>
			Int_190,
			/// <summary>
			/// 其他-加工时自动更改曲线方向;1=使能;0=未使能;
			/// </summary>
			Int_191,
			/// <summary>
			/// 激光全局-使能加工中检查激光器状态;1=使能;0=未使能;
			/// </summary>
			Int_192,
			/// <summary>
			/// 未定义;
			/// </summary>
			Int_193,
			/// <summary>
			/// 振镜-振镜XY延时-使能;1=使能;0=未使能;
			/// </summary>
			Int_194,
			/// <summary>
			/// 振镜-振镜XY延时-延时[us]0-10000;
			/// </summary>
			Int_195,
			/// <summary>
			/// 端口-输出-其他-关闭电源时保存输出口;1=使能;0=未使能;
			/// </summary>
			Int_196,
			/// <summary>
			/// 端口-输出-其他-加工中不检查开始端口;1=使能;0=未使能;
			/// </summary>
			Int_197,
			/// <summary>
			/// 未定义;
			/// </summary>
			Int_198,
			/// <summary>
			/// 未定义;
			/// </summary>
			Int_199,
			/// <summary>
			/// 区域-检查加工范围;1=使能;0=未使能;
			/// </summary>
			Int_200,
			/// <summary>
			/// 振镜-振镜-反馈模式;0=NONE;1=Actual Position;2=Actual velocity;3=Position eror;4=Status;
			/// </summary>
			Int_201,
			/// <summary>
			/// 区域-校正-是否使能内部校正;1=使能;0=未使能;
			/// </summary>
			Int_202,
			/// <summary>
			/// 其他-硬件抖动;1=使能;0=未使能;
			/// </summary>
			Int_203,
			/// <summary>
			/// 飞行标刻-飞行标刻-编码器AB相互换;1=使能;0=未使能;
			/// </summary>
			Int_204,
			/// <summary>
			/// 未定义;
			/// </summary>
			Int_205,
			/// <summary>
			/// 未定义;
			/// </summary>
			Int_206,
			/// <summary>
			/// 端口-输出-设备状态灯;1=使能;0=未使能;
			/// </summary>
			Int_207,
			/// <summary>
			/// 端口-输出-设备状态灯-低电平有效;1=使能;0=未使能;
			/// </summary>
			Int_208,
			/// <summary>
			/// 端口-输出-设备状态灯-Red端口;-1=无;最大15;
			/// </summary>
			Int_209,
			/// <summary>
			/// 端口-输出-设备状态灯-Green端口;-1=无;最大15;
			/// </summary>
			Int_210,
			/// <summary>
			/// 端口-输出-设备状态灯-Yellow端口;-1=无;最大15;
			/// </summary>
			Int_211,
			/// <summary>
			/// 其他-使用内部加工循环;1=使能;0=未使能;
			/// </summary>
			Int_212,
			/// <summary>
			/// 振镜-振镜-自动模式-使能退出处理模式;1=使能;0=未使能;
			/// </summary>
			Int_213,
			/// <summary>
			/// 激光全局-使能APM模式;1=使能;0=未使能;
			/// </summary>
			Int_214,
			/// <summary>
			/// 未定义;
			/// </summary>
			Int_215,
			/// <summary>
			/// 未定义;
			/// </summary>
			Int_216,
			/// <summary>
			/// 使能功率输出2;
			/// </summary>
			Int_217,
			/// <summary>
			/// 未定义;
			/// </summary>
			Int_218,
			/// <summary>
			/// 未定义;
			/// </summary>
			Int_219,
			/// <summary>
			/// 未定义;
			/// </summary>
			Int_220,
			/// <summary>
			/// 未定义;
			/// </summary>
			Int_221,
			/// <summary>
			/// 未定义;
			/// </summary>
			Int_222,
			/// <summary>
			/// 未定义;
			/// </summary>
			Int_223,
			/// <summary>
			/// 未定义;
			/// </summary>
			Int_224,
			/// <summary>
			/// 激光全局-开始加工前先设置激光参数;1=使能;0=未使能;
			/// </summary>
			Int_225,
			/// <summary>
			/// 未定义;
			/// </summary>
			Int_226,
			/// <summary>
			/// 未定义;
			/// </summary>
			Int_227,
			/// <summary>
			/// 未定义;
			/// </summary>
			Int_228,
			/// <summary>
			/// 未定义;
			/// </summary>
			Int_229,
			/// <summary>
			/// 未定义;
			/// </summary>
			Int_230,
			/// <summary>
			/// 未定义;
			/// </summary>
			Int_231,
			/// <summary>
			/// 未定义;
			/// </summary>
			Int_232,
			/// <summary>
			/// 未定义;
			/// </summary>
			Int_233,
			/// <summary>
			/// 未定义;
			/// </summary>
			Int_234,
			/// <summary>
			/// 未定义;
			/// </summary>
			Int_235,
			/// <summary>
			/// 未定义;
			/// </summary>
			Int_236,
			/// <summary>
			/// 未定义;
			/// </summary>
			Int_237,
			/// <summary>
			/// 未定义;
			/// </summary>
			Int_238,
			/// <summary>
			/// 未定义;
			/// </summary>
			Int_239,
			/// <summary>
			/// 未定义;
			/// </summary>
			Int_240,
			/// <summary>
			/// 未定义;
			/// </summary>
			Int_241,
			/// <summary>
			/// 未定义;
			/// </summary>
			Int_242,
			/// <summary>
			/// 未定义;
			/// </summary>
			Int_243,
			/// <summary>
			/// 未定义;
			/// </summary>
			Int_244,
			/// <summary>
			/// 未定义;
			/// </summary>
			Int_245,
			/// <summary>
			/// 未定义;
			/// </summary>
			Int_246,
			/// <summary>
			/// 未定义;
			/// </summary>
			Int_247,
			/// <summary>
			/// 未定义;
			/// </summary>
			Int_248,
			/// <summary>
			/// 未定义;
			/// </summary>
			Int_249,
			/// <summary>
			/// 未定义;
			/// </summary>
			Int_250,
			/// <summary>
			/// 未定义;
			/// </summary>
			Int_251,
			/// <summary>
			/// 未定义;
			/// </summary>
			Int_252,
			/// <summary>
			/// 未定义;
			/// </summary>
			Int_253,
			/// <summary>
			/// 未定义;
			/// </summary>
			Int_254,
			/// <summary>
			/// 未定义;
			/// </summary>
			Int_255,
			/// <summary>
			/// 未定义;
			/// </summary>
			Int_256,
			/// <summary>
			/// 未定义;
			/// </summary>
			Int_257,
			/// <summary>
			/// 未定义;
			/// </summary>
			Int_258,
			/// <summary>
			/// 未定义;
			/// </summary>
			Int_259,
			/// <summary>
			/// 未定义;
			/// </summary>
			Int_260,
			/// <summary>
			/// 未定义;
			/// </summary>
			Int_261,
			/// <summary>
			/// 未定义;
			/// </summary>
			Int_262,
			/// <summary>
			/// 未定义;
			/// </summary>
			Int_263,
			/// <summary>
			/// 未定义;
			/// </summary>
			Int_264,
			/// <summary>
			/// 未定义;
			/// </summary>
			Int_265,
			/// <summary>
			/// 未定义;
			/// </summary>
			Int_266,
			/// <summary>
			/// 未定义;
			/// </summary>
			Int_267,
			/// <summary>
			/// 未定义;
			/// </summary>
			Int_268,
			/// <summary>
			/// 未定义;
			/// </summary>
			Int_269,
			/// <summary>
			/// 未定义;
			/// </summary>
			Int_270,
			/// <summary>
			/// 未定义;
			/// </summary>
			Int_271,
			/// <summary>
			/// 未定义;
			/// </summary>
			Int_272,
			/// <summary>
			/// 未定义;
			/// </summary>
			Int_273,
			/// <summary>
			/// 未定义;
			/// </summary>
			Int_274,
			/// <summary>
			/// 未定义;
			/// </summary>
			Int_275,
			/// <summary>
			/// 未定义;
			/// </summary>
			Int_276,
			/// <summary>
			/// 未定义;
			/// </summary>
			Int_277,
			/// <summary>
			/// 未定义;
			/// </summary>
			Int_278,
			/// <summary>
			/// 未定义;
			/// </summary>
			Int_279,
			/// <summary>
			/// 未定义;
			/// </summary>
			Int_280,
			/// <summary>
			/// 未定义;
			/// </summary>
			Int_281,
			/// <summary>
			/// 未定义;
			/// </summary>
			Int_282,
			/// <summary>
			/// 未定义;
			/// </summary>
			Int_283,
			/// <summary>
			/// 未定义;
			/// </summary>
			Int_284,
			/// <summary>
			/// 未定义;
			/// </summary>
			Int_285,
			/// <summary>
			/// 未定义;
			/// </summary>
			Int_286,
			/// <summary>
			/// 未定义;
			/// </summary>
			Int_287,
			/// <summary>
			/// 未定义;
			/// </summary>
			Int_288,
			/// <summary>
			/// 未定义;
			/// </summary>
			Int_289,
			/// <summary>
			/// 未定义;
			/// </summary>
			Int_290,
			/// <summary>
			/// 未定义;
			/// </summary>
			Int_291,
			/// <summary>
			/// 未定义;
			/// </summary>
			Int_292,
			/// <summary>
			/// 未定义;
			/// </summary>
			Int_293,
			/// <summary>
			/// 未定义;
			/// </summary>
			Int_294,
			/// <summary>
			/// 未定义;
			/// </summary>
			Int_295,
			/// <summary>
			/// 未定义;
			/// </summary>
			Int_296,
			/// <summary>
			/// 未定义;
			/// </summary>
			Int_297,
			/// <summary>
			/// 未定义;
			/// </summary>
			Int_298,
			/// <summary>
			/// 未定义;
			/// </summary>
			Int_299,
		};

		/// <summary>
		/// F3参数Double值类型查询索引定义
		/// </summary>
		enum class F3DoubleParamKey
		{
			/// <summary>
			/// 区域-尺寸(毫米);
			/// </summary>
			Double_0,
			/// <summary>
			/// 区域-变换-偏移X[mm];-10000-10000;
			/// </summary>
			Double_1,
			/// <summary>
			/// 区域-变换-偏移Y[mm];-10000-10000;
			/// </summary>
			Double_2,
			/// <summary>
			/// 区域-变换-角度;-10000-10000;
			/// </summary>
			Double_3,
			/// <summary>
			/// 区域-加工后去指定位置-X[mm];-10000-10000;
			/// </summary>
			Double_4,
			/// <summary>
			/// 区域-加工后去指定位置-Y[mm];-10000-10000;
			/// </summary>
			Double_5,
			/// <summary>
			/// 区域-加工后去指定位置-Z[mm];-10000-10000;
			/// </summary>
			Double_6,
			/// <summary>
			/// 区域-极限参数-离散误差[mm];0.0001-1;
			/// </summary>
			Double_7,
			/// <summary>
			/// 区域-极限参数-最小直线的长度[mm];0.0001-1;
			/// </summary>
			Double_8,
			/// <summary>
			/// 激光控制-频率-最小频率[kHz];0.00001-10000;
			/// </summary>
			Double_9,
			/// <summary>
			/// 激光控制-频率-最大频率[kHz];0.001-10000;
			/// </summary>
			Double_10,
			/// <summary>
			/// CO2首脉冲抑制起始功率;
			/// </summary>
			Double_11,
			/// <summary>
			/// CO2首脉冲步进增量功率;
			/// </summary>
			Double_12,
			/// <summary>
			/// 默认电流;
			/// </summary>
			Double_13,
			/// <summary>
			/// 首脉冲抑制电压2;
			/// </summary>
			Double_14,
			/// <summary>
			/// 首脉冲抑制电压1;
			/// </summary>
			Double_15,
			/// <summary>
			/// 电流映射实际比例(10);
			/// </summary>
			Double_16,
			/// <summary>
			/// 电流映射实际比例(20);
			/// </summary>
			Double_17,
			/// <summary>
			/// 电流映射实际比例(30);
			/// </summary>
			Double_18,
			/// <summary>
			/// 电流映射实际比例(40);
			/// </summary>
			Double_19,
			/// <summary>
			/// 电流映射实际比例(50);
			/// </summary>
			Double_20,
			/// <summary>
			/// 电流映射实际比例(60);
			/// </summary>
			Double_21,
			/// <summary>
			/// 电流映射实际比例(70);
			/// </summary>
			Double_22,
			/// <summary>
			/// 电流映射实际比例(80);
			/// </summary>
			Double_23,
			/// <summary>
			/// 电流映射实际比例(90);
			/// </summary>
			Double_24,
			/// <summary>
			/// 电流映射实际比例(100);
			/// </summary>
			Double_25,
			/// <summary>
			/// 电流映射电流(0);
			/// </summary>
			Double_26,
			/// <summary>
			/// 电流映射电流(1);
			/// </summary>
			Double_27,
			/// <summary>
			/// 电流映射电流(2);
			/// </summary>
			Double_28,
			/// <summary>
			/// 电流映射电流(3);
			/// </summary>
			Double_29,
			/// <summary>
			/// 电流映射电流(4);
			/// </summary>
			Double_30,
			/// <summary>
			/// 电流映射电流(5);
			/// </summary>
			Double_31,
			/// <summary>
			/// 电流映射电流(6);
			/// </summary>
			Double_32,
			/// <summary>
			/// 电流映射电流(7);
			/// </summary>
			Double_33,
			/// <summary>
			/// 电流映射电流(8);
			/// </summary>
			Double_34,
			/// <summary>
			/// 电流映射电流(9);
			/// </summary>
			Double_35,
			/// <summary>
			/// 电流映射电流(10);
			/// </summary>
			Double_36,
			/// <summary>
			/// 功率映射(0);
			/// </summary>
			Double_37,
			/// <summary>
			/// 功率映射(10);
			/// </summary>
			Double_38,
			/// <summary>
			/// 功率映射(20);
			/// </summary>
			Double_39,
			/// <summary>
			/// 功率映射(30);
			/// </summary>
			Double_40,
			/// <summary>
			/// 功率映射(40);
			/// </summary>
			Double_41,
			/// <summary>
			/// 功率映射(50);
			/// </summary>
			Double_42,
			/// <summary>
			/// 功率映射(60);
			/// </summary>
			Double_43,
			/// <summary>
			/// 功率映射(70);
			/// </summary>
			Double_44,
			/// <summary>
			/// 功率映射(80);
			/// </summary>
			Double_45,
			/// <summary>
			/// 功率映射(90);
			/// </summary>
			Double_46,
			/// <summary>
			/// 功率映射(100);
			/// </summary>
			Double_47,
			/// <summary>
			/// 预电离频率;
			/// </summary>
			Double_48,
			/// <summary>
			/// 待机功率;
			/// </summary>
			Double_49,
			/// <summary>
			/// 区域-极限参数-最小跳转速度[mm/s];0.001-1000000;
			/// </summary>
			Double_50,
			/// <summary>
			/// 区域-极限参数-最大跳转速度[mm/s];0.001-1000000;
			/// </summary>
			Double_51,
			/// <summary>
			/// 红光指示-红光指示-红光速度[mm/s];1-100000;
			/// </summary>
			Double_52,
			/// <summary>
			/// 红光指示-红光指示-尺寸比例X;-10-10;
			/// </summary>
			Double_53,
			/// <summary>
			/// 红光指示-红光指示-尺寸比例Y;-10-10;
			/// </summary>
			Double_54,
			/// <summary>
			/// 红光指示-红光指示-偏移位置X[mm];-10000-10000;
			/// </summary>
			Double_55,
			/// <summary>
			/// 红光指示-红光指示-偏移位置Y[mm];-10000-10000;
			/// </summary>
			Double_56,
			/// <summary>
			/// 飞行标刻-飞行标刻-飞行系数[um/系数];例:F3参数=80,读出0.08;
			/// </summary>
			Double_57,
			/// <summary>
			/// 飞行标刻-其他-飞行误差修正系数;0.01-10;
			/// </summary>
			Double_58,
			/// <summary>
			/// qcwEmission enable延时;
			/// </summary>
			Double_59,
			/// <summary>
			/// 飞行标刻-硬件模拟模式-模拟飞行速度X;-0.01-10000;
			/// </summary>
			Double_60,
			/// <summary>
			/// 最大脉宽 ms;
			/// </summary>
			Double_61,
			/// <summary>
			/// 最小脉宽 ms;
			/// </summary>
			Double_62,
			/// <summary>
			/// 振镜-振镜-自动模式-到位误差[mm];0.0001-100;
			/// </summary>
			Double_63,
			/// <summary>
			/// 振镜-振镜-自动模式-跳转速度[mm/s];0.001-1000000;
			/// </summary>
			Double_64,
			/// <summary>
			/// IO稳定时间;
			/// </summary>
			Double_65,
			/// <summary>
			/// 飞行系数2;
			/// </summary>
			Double_66,
			/// <summary>
			/// 飞行标刻-硬件模拟模式-模拟飞行速度Y;-0.01-10000;
			/// </summary>
			Double_67,
			/// <summary>
			/// 区域变换偏移Z;
			/// </summary>
			Double_68,
			/// <summary>
			/// 其他-使能首次开启激光延时时间-激光冷却时间[ms];
			/// </summary>
			Double_69,
			/// <summary>
			/// 未定义;
			/// </summary>
			Double_70,
			/// <summary>
			/// 未定义;
			/// </summary>
			Double_71,
			/// <summary>
			/// 未定义;
			/// </summary>
			Double_72,
			/// <summary>
			/// 待机功率比率;
			/// </summary>
			Double_73,
			/// <summary>
			/// 红光指示-红光指示-扩展轴速度倍率[%];0.01-100;
			/// </summary>
			Double_74,
			/// <summary>
			/// 激光输出模拟量最小值;
			/// </summary>
			Double_75,
			/// <summary>
			/// 激光输出模拟量最大值;
			/// </summary>
			Double_76,
			/// <summary>
			/// 其他-快速划线出光比例;1-100;
			/// </summary>
			Double_77,
			/// <summary>
			/// 最大飞行速度;
			/// </summary>
			Double_78,
			/// <summary>
			/// 激光全局-激光迟滞时间[us];
			/// </summary>
			Double_79,
			/// <summary>
			/// 其他-使能首次开启激光延时时间-首笔加速距离[mm];
			/// </summary>
			Double_80,
			/// <summary>
			/// 动态聚焦-动态聚焦-速度场-比率;0-5;
			/// </summary>
			Double_81,
			/// <summary>
			/// 动态聚焦-动态聚焦-能量场-比率;0-5;
			/// </summary>
			Double_82,
			/// <summary>
			/// 动态聚焦-细分精度比率;0-1;
			/// </summary>
			Double_83,
			/// <summary>
			/// 端口-输出-激光开光同步-开始延时[us];0.01-1000000;
			/// </summary>
			Double_84,
			/// <summary>
			/// 端口-输出-激光开光同步-结束延时[us];0.01-1000000;
			/// </summary>
			Double_85,
			/// <summary>
			/// CO2-首脉冲抑制-起始脉冲宽度(us);
			/// </summary>
			Double_86,
			/// <summary>
			/// CO2-首脉冲抑制-脉冲宽度增量(us);
			/// </summary>
			Double_87,
			/// <summary>
			/// 飞行标刻-最小触发距离-距离;0.01-10000;
			/// </summary>
			Double_88,
			/// <summary>
			/// 飞行标刻-最小触发时间-时间;0.01-100000;
			/// </summary>
			Double_89,
			/// <summary>
			/// 加工时间的显示系数;
			/// </summary>
			Double_90,
			/// <summary>
			/// 激光全局-线性变换中的最小直线长度[mm];0-100;
			/// </summary>
			Double_91,
			/// <summary>
			/// 其他-单点间隔延时[us];0-1000000;
			/// </summary>
			Double_92,
			/// <summary>
			/// 飞行标刻-其他-开始点跳转长度;0.001-100;
			/// </summary>
			Double_93,
			/// <summary>
			/// 区域-校正-内部校正-X方向比例(百分数, 标准软件66, 读出0.66);0-1000;
			/// </summary>
			Double_94,
			/// <summary>
			/// 区域-校正-内部校正-Y方向比例(百分数, 标准软件66, 读出0.66);0-1000;
			/// </summary>
			Double_95,
			/// <summary>
			/// 区域-校正-内部校正-X方向枕形系数;0.001-10;
			/// </summary>
			Double_96,
			/// <summary>
			/// 区域-校正-内部校正-Y方向枕形系数;0.001-10;
			/// </summary>
			Double_97,
			/// <summary>
			/// 区域-校正-内部校正-X方向平行四边形系数;0.001-10;
			/// </summary>
			Double_98,
			/// <summary>
			/// 区域-校正-内部校正-Y方向平行四边形系数;0.001-10;
			/// </summary>
			Double_99,
			/// <summary>
			/// 区域-校正-内部校正-X方向体形系数;0.001-10;
			/// </summary>
			Double_100,
			/// <summary>
			/// 区域-校正-内部校正-Y方向体形系数;0.001-10;
			/// </summary>
			Double_101,
			/// <summary>
			/// 区域-校正-内部校正-变换比例X;0-1000;
			/// </summary>
			Double_102,
			/// <summary>
			/// 区域-校正-内部校正-变换比例Y;0-1000;
			/// </summary>
			Double_103,
			/// <summary>
			/// 飞行标刻-其他-X补偿系数;-180-180;
			/// </summary>
			Double_104,
			/// <summary>
			/// 红光指示-红光指示-偏移Z[mm];-10000-10000;
			/// </summary>
			Double_105,
			/// <summary>
			/// 激光控制-频率-PWM占空比[%];0-100;例:100%=0.1;
			/// </summary>
			Double_106,
			/// <summary>
			/// 飞行标刻-其他-旋转角度;-180-180;
			/// </summary>
			Double_107,
			/// <summary>
			/// 未定义;
			/// </summary>
			Double_108,
			/// <summary>
			/// 未定义;
			/// </summary>
			Double_109,
			/// <summary>
			/// 未定义;
			/// </summary>
			Double_110,
			/// <summary>
			/// 未定义;
			/// </summary>
			Double_111,
			/// <summary>
			/// 未定义;
			/// </summary>
			Double_112,
			/// <summary>
			/// 未定义;
			/// </summary>
			Double_113,
			/// <summary>
			/// 未定义;
			/// </summary>
			Double_114,
			/// <summary>
			/// 未定义;
			/// </summary>
			Double_115,
			/// <summary>
			/// 未定义;
			/// </summary>
			Double_116,
			/// <summary>
			/// 未定义;
			/// </summary>
			Double_117,
			/// <summary>
			/// 未定义;
			/// </summary>
			Double_118,
			/// <summary>
			/// 未定义;
			/// </summary>
			Double_119,
			/// <summary>
			/// 未定义;
			/// </summary>
			Double_120,
			/// <summary>
			/// 未定义;
			/// </summary>
			Double_121,
			/// <summary>
			/// 未定义;
			/// </summary>
			Double_122,
			/// <summary>
			/// 未定义;
			/// </summary>
			Double_123,
			/// <summary>
			/// 未定义;
			/// </summary>
			Double_124,
			/// <summary>
			/// 区域-极限参数-最小标刻速度[mm/s];0.001-1000000;
			/// </summary>
			Double_125,
			/// <summary>
			/// 区域-极限参数-最大标刻速度[mm/s];0.001-1000000;
			/// </summary>
			Double_126,
			/// <summary>
			/// 未定义;
			/// </summary>
			Double_127,
			/// <summary>
			/// 未定义;
			/// </summary>
			Double_128,
			/// <summary>
			/// 未定义;
			/// </summary>
			Double_129,
			/// <summary>
			/// 未定义;
			/// </summary>
			Double_130,
			/// <summary>
			/// 未定义;
			/// </summary>
			Double_131,
			/// <summary>
			/// 未定义;
			/// </summary>
			Double_132,
			/// <summary>
			/// 未定义;
			/// </summary>
			Double_133,
			/// <summary>
			/// 未定义;
			/// </summary>
			Double_134,
			/// <summary>
			/// 未定义;
			/// </summary>
			Double_135,
			/// <summary>
			/// 未定义;
			/// </summary>
			Double_136,
			/// <summary>
			/// 未定义;
			/// </summary>
			Double_137,
			/// <summary>
			/// 未定义;
			/// </summary>
			Double_138,
			/// <summary>
			/// 未定义;
			/// </summary>
			Double_139,
			/// <summary>
			/// 未定义;
			/// </summary>
			Double_140,
			/// <summary>
			/// 未定义;
			/// </summary>
			Double_141,
			/// <summary>
			/// 未定义;
			/// </summary>
			Double_142,
			/// <summary>
			/// 未定义;
			/// </summary>
			Double_143,
			/// <summary>
			/// 未定义;
			/// </summary>
			Double_144,
			/// <summary>
			/// 未定义;
			/// </summary>
			Double_145,
			/// <summary>
			/// 未定义;
			/// </summary>
			Double_146,
			/// <summary>
			/// 未定义;
			/// </summary>
			Double_147,
			/// <summary>
			/// 未定义;
			/// </summary>
			Double_148,
			/// <summary>
			/// 未定义;
			/// </summary>
			Double_149,
			/// <summary>
			/// 未定义;
			/// </summary>
			Double_150,
			/// <summary>
			/// 未定义;
			/// </summary>
			Double_151,
			/// <summary>
			/// 未定义;
			/// </summary>
			Double_152,
			/// <summary>
			/// 未定义;
			/// </summary>
			Double_153,
			/// <summary>
			/// 未定义;
			/// </summary>
			Double_154,
			/// <summary>
			/// 未定义;
			/// </summary>
			Double_155,
			/// <summary>
			/// 未定义;
			/// </summary>
			Double_156,
			/// <summary>
			/// 未定义;
			/// </summary>
			Double_157,
			/// <summary>
			/// 未定义;
			/// </summary>
			Double_158,
			/// <summary>
			/// 未定义;
			/// </summary>
			Double_159,
			/// <summary>
			/// 未定义;
			/// </summary>
			Double_160,
			/// <summary>
			/// 未定义;
			/// </summary>
			Double_161,
			/// <summary>
			/// 未定义;
			/// </summary>
			Double_162,
			/// <summary>
			/// 未定义;
			/// </summary>
			Double_163,
			/// <summary>
			/// 未定义;
			/// </summary>
			Double_164,
			/// <summary>
			/// 未定义;
			/// </summary>
			Double_165,
			/// <summary>
			/// 未定义;
			/// </summary>
			Double_166,
			/// <summary>
			/// 未定义;
			/// </summary>
			Double_167,
			/// <summary>
			/// 未定义;
			/// </summary>
			Double_168,
			/// <summary>
			/// 未定义;
			/// </summary>
			Double_169,
			/// <summary>
			/// 未定义;
			/// </summary>
			Double_170,
			/// <summary>
			/// 未定义;
			/// </summary>
			Double_171,
			/// <summary>
			/// 未定义;
			/// </summary>
			Double_172,
			/// <summary>
			/// 未定义;
			/// </summary>
			Double_173,
			/// <summary>
			/// 未定义;
			/// </summary>
			Double_174,
			/// <summary>
			/// 未定义;
			/// </summary>
			Double_175,
			/// <summary>
			/// 未定义;
			/// </summary>
			Double_176,
			/// <summary>
			/// 未定义;
			/// </summary>
			Double_177,
			/// <summary>
			/// 未定义;
			/// </summary>
			Double_178,
			/// <summary>
			/// 未定义;
			/// </summary>
			Double_179,
			/// <summary>
			/// 未定义;
			/// </summary>
			Double_180,
			/// <summary>
			/// 未定义;
			/// </summary>
			Double_181,
			/// <summary>
			/// 未定义;
			/// </summary>
			Double_182,
			/// <summary>
			/// 未定义;
			/// </summary>
			Double_183,
			/// <summary>
			/// 未定义;
			/// </summary>
			Double_184,
			/// <summary>
			/// 未定义;
			/// </summary>
			Double_185,
			/// <summary>
			/// 未定义;
			/// </summary>
			Double_186,
			/// <summary>
			/// 未定义;
			/// </summary>
			Double_187,
			/// <summary>
			/// 未定义;
			/// </summary>
			Double_188,
			/// <summary>
			/// 未定义;
			/// </summary>
			Double_189,
			/// <summary>
			/// 未定义;
			/// </summary>
			Double_190,
			/// <summary>
			/// 未定义;
			/// </summary>
			Double_191,
			/// <summary>
			/// 未定义;
			/// </summary>
			Double_192,
			/// <summary>
			/// 未定义;
			/// </summary>
			Double_193,
			/// <summary>
			/// 未定义;
			/// </summary>
			Double_194,
			/// <summary>
			/// 未定义;
			/// </summary>
			Double_195,
			/// <summary>
			/// 未定义;
			/// </summary>
			Double_196,
			/// <summary>
			/// 未定义;
			/// </summary>
			Double_197,
			/// <summary>
			/// 未定义;
			/// </summary>
			Double_198,
			/// <summary>
			/// 未定义;
			/// </summary>
			Double_199,
		};

		/// <summary>
		/// F3参数String值类型查询索引定义
		/// </summary>
		enum class F3StringParamKey
		{
			/// <summary>
			/// F3密码;
			/// </summary>
			String_0,
			/// <summary>
			/// 校正文件路径;
			/// </summary>
			String_1,
			/// <summary>
			/// 停止端口信号说明0;
			/// </summary>
			String_2,
			/// <summary>
			/// 停止端口信号说明1;
			/// </summary>
			String_3,
			/// <summary>
			/// 停止端口信号说明2;
			/// </summary>
			String_4,
			/// <summary>
			/// 停止端口信号说明3;
			/// </summary>
			String_5,
			/// <summary>
			/// 停止端口信号说明4;
			/// </summary>
			String_6,
			/// <summary>
			/// 停止端口信号说明5;
			/// </summary>
			String_7,
			/// <summary>
			/// 未定义;
			/// </summary>
			String_8,
			/// <summary>
			/// 停止端口信号说明6;
			/// </summary>
			String_9,
			/// <summary>
			/// 停止端口信号说明7;
			/// </summary>
			String_10,
			/// <summary>
			/// 停止端口信号说明8;
			/// </summary>
			String_11,
			/// <summary>
			/// 停止端口信号说明9;
			/// </summary>
			String_12,
			/// <summary>
			/// 未定义;
			/// </summary>
			String_13,
			/// <summary>
			/// 未定义;
			/// </summary>
			String_14,
			/// <summary>
			/// 未定义;
			/// </summary>
			String_15,
			/// <summary>
			/// 未定义;
			/// </summary>
			String_16,
			/// <summary>
			/// 未定义;
			/// </summary>
			String_17,
			/// <summary>
			/// 未定义;
			/// </summary>
			String_18,
			/// <summary>
			/// 未定义;
			/// </summary>
			String_19,
			/// <summary>
			/// 未定义;
			/// </summary>
			String_20,
			/// <summary>
			/// 未定义;
			/// </summary>
			String_21,
			/// <summary>
			/// 未定义;
			/// </summary>
			String_22,
			/// <summary>
			/// 未定义;
			/// </summary>
			String_23,
			/// <summary>
			/// 未定义;
			/// </summary>
			String_24,
			/// <summary>
			/// 未定义;
			/// </summary>
			String_25,
			/// <summary>
			/// 未定义;
			/// </summary>
			String_26,
			/// <summary>
			/// 未定义;
			/// </summary>
			String_27,
			/// <summary>
			/// 未定义;
			/// </summary>
			String_28,
			/// <summary>
			/// 未定义;
			/// </summary>
			String_29,
			/// <summary>
			/// 未定义;
			/// </summary>
			String_30,
			/// <summary>
			/// 未定义;
			/// </summary>
			String_31,
			/// <summary>
			/// 未定义;
			/// </summary>
			String_32,
			/// <summary>
			/// 未定义;
			/// </summary>
			String_33,
			/// <summary>
			/// 未定义;
			/// </summary>
			String_34,
			/// <summary>
			/// 未定义;
			/// </summary>
			String_35,
			/// <summary>
			/// 未定义;
			/// </summary>
			String_36,
			/// <summary>
			/// 未定义;
			/// </summary>
			String_37,
			/// <summary>
			/// 未定义;
			/// </summary>
			String_38,
			/// <summary>
			/// 未定义;
			/// </summary>
			String_39,
			/// <summary>
			/// 未定义;
			/// </summary>
			String_40,
			/// <summary>
			/// 未定义;
			/// </summary>
			String_41,
			/// <summary>
			/// 未定义;
			/// </summary>
			String_42,
			/// <summary>
			/// 未定义;
			/// </summary>
			String_43,
			/// <summary>
			/// 未定义;
			/// </summary>
			String_44,
			/// <summary>
			/// 未定义;
			/// </summary>
			String_45,
			/// <summary>
			/// 未定义;
			/// </summary>
			String_46,
			/// <summary>
			/// 未定义;
			/// </summary>
			String_47,
			/// <summary>
			/// 未定义;
			/// </summary>
			String_48,
			/// <summary>
			/// 未定义;
			/// </summary>
			String_49,
		};

		/// <summary>
		/// 文本Int参数数组定义
		/// </summary>
		enum class TextIntParam
		{
			/// <summary>
			/// 字体序号,GetAllFont获取对应名称的字体的序号;
			/// </summary>
			FnPIdx_0,
			/// <summary>
			/// 字符间距类型:自动间距 = 0;指定间距 = 1;中心间距 = 2;
			/// </summary>
			FnPIdx_1,
			/// <summary>
			/// 对齐类型:居左对齐 = 0;居中对齐 = 1;居右对齐 = 2;
			/// </summary>
			FnPIdx_2,
			/// <summary>
			/// 垂直排列:水平 = 0;垂直 = 1;
			/// </summary>
			FnPIdx_3,
			/// <summary>
			/// 粗体模式:非粗体 = 0;粗体 = 1;
			/// </summary>
			FnPIdx_4,
			/// <summary>
			/// 斜体模式:非斜体 = 0;斜体 = 1;
			/// </summary>
			FnPIdx_5,
			/// <summary>
			/// 变量文本:非使能变量文本 = 0;使能变量文本 = 1;(此参数为预留参数，默认为0即可);
			/// </summary>
			FnPIdx_6,
			/// <summary>
			/// 圆弧文本:非使能圆弧文本 = 0;使能圆弧文本 = 1;
			/// </summary>
			FnPIdx_7,
			/// <summary>
			/// 是否使能圆弧文本角度限制:不使能 = 0;使能 = 1;
			/// </summary>
			FnPIdx_8,
			/// <summary>
			/// 圆弧文本属性设置:都不反转 = 0;排序反转 = 1;上下反转 = 2;排序及上下都反转 = 3;
			/// </summary>
			FnPIdx_9,
			/// <summary>
			/// 是否使能支持分割字符:非使能=0;使能=1;
			/// </summary>
			FnPIdx_10,
			/// <summary>
			/// 是否加工自己:分割字符串后不加工自己 = 0;加工自己 = 1;
			/// </summary>
			FnPIdx_11,
			/// <summary>
			/// 固定尺寸:使能固定尺寸 = 0;不使能固定尺寸 = 1;
			/// </summary>
			FnPIdx_12,
			/// <summary>
			/// 保存加工内容到文件属性: 保存加工内容到文件 = 0x0001;保存加工时间到文件 = 0x0002;判断内容是否重复=0x0004;固定文本尺寸时禁止改变文字宽度=0x0010;;
			/// </summary>
			FnPIdx_13,
			/// <summary>
			/// 在路径上的放置方式:基准 = 0;顶部 = 1;底部 = 2;中心 = 3;自由 = 4;
			/// </summary>
			FnPIdx_14,
			/// <summary>
			/// 在路径上的排列方向:正向 = 0;反向 = 1;
			/// </summary>
			FnPIdx_15,
			/// <summary>
			/// 在路径上的字符变换模式(两种模式分别是0，1);
			/// </summary>
			FnPIdx_16,
			/// <summary>
			/// 阵列类型: 先左到右,再下到上 = 0;先下到上,再左到右 = 1;先左右往返,再下到上 = 2;先下上往返,再左到右 = 3;
			/// </summary>
			FnPIdx_17,
			/// <summary>
			/// X方向阵列数目 [1-100];
			/// </summary>
			FnPIdx_18,
			/// <summary>
			/// Y方向阵列数目 [1-100];
			/// </summary>
			FnPIdx_19,
			/// <summary>
			/// 文本内容长度;
			/// </summary>
			FnPIdx_20,
			/// <summary>
			/// 保存文件路径长度(高级中输出文本到指定文件的路径长度);
			/// </summary>
			FnPIdx_21,
			/// <summary>
			/// 是否已经填充:否 = 0;是 = 1;
			/// </summary>
			FnPIdx_22,
			/// <summary>
			/// 变量单元数量(使能变量文本后添加的变量的个数);
			/// </summary>
			FnPIdx_23,
		};

		/// <summary>
		/// 文本Double参数数组定义 
		/// </summary>
		enum class TextDoubleParam
		{
			/// <summary>
			/// X坐标,对象左下角基准点X坐标;
			/// </summary>
			FCdPIdx_0,
			/// <summary>
			/// Y坐标,对象左下角基准点Y坐标;
			/// </summary>
			FCdPIdx_1,
			/// <summary>
			/// 字符高度;
			/// </summary>
			FCdPIdx_2,
			/// <summary>
			/// 字符宽度;
			/// </summary>
			FCdPIdx_3,
			/// <summary>
			/// 空字符宽度;
			/// </summary>
			FCdPIdx_4,
			/// <summary>
			/// 角度倾斜;
			/// </summary>
			FCdPIdx_5,
			/// <summary>
			/// 字符间距;
			/// </summary>
			FCdPIdx_6,
			/// <summary>
			/// 行间距;
			/// </summary>
			FCdPIdx_7,
			/// <summary>
			/// 圆弧文本直径;
			/// </summary>
			FCdPIdx_8,
			/// <summary>
			/// 圆弧文本基准角度;
			/// </summary>
			FCdPIdx_9,
			/// <summary>
			/// 圆弧文本角度限制;
			/// </summary>
			FCdPIdx_10,
			/// <summary>
			/// 固定文本X长度(高级里面使能固定文本后,需填写固定文本长度);
			/// </summary>
			FCdPIdx_11,
			/// <summary>
			/// 文字基准长度;
			/// </summary>
			FCdPIdx_12,
			/// <summary>
			/// 路径偏移距离;
			/// </summary>
			FCdPIdx_13,
			/// <summary>
			/// X方向阵列距离;
			/// </summary>
			FCdPIdx_14,
			/// <summary>
			/// Y方向阵列距离;
			/// </summary>
			FCdPIdx_15,
		};

		/// <summary>
		/// 条码参数数组定义
		/// </summary>
		enum class BarcodeIntParam 
		{
			/// <summary>
			///  对象类型:1=一维码;2=二维码;
			/// </summary>
			BnPIdx_0,
			/// <summary>
			///  校验位:0=不支持校验;1=支持校验;
			/// </summary>
			BnPIdx_1,
			/// <summary>
			///  反转:0=不反转;1=反转;
			/// </summary>
			BnPIdx_2,
			/// <summary>
			///  条码固定尺寸:0=不使能固定尺寸;1=使能固定尺寸;
			/// </summary>
			BnPIdx_3,
			/// <summary>
			///  使能内部填充线:0=不使能;1=使能;;
			/// </summary>
			BnPIdx_4,
			/// <summary>
			///  条码模式:0=标准模式;1=矩形;2=圆;3=点;;
			/// </summary>
			BnPIdx_5,
			/// <summary>
			///  黑白反转:0=不使能;1=使能;;
			/// </summary>
			BnPIdx_6,
			/// <summary>
			///  PDF417自定义条码行数;
			/// </summary>
			BnPIdx_7,
			/// <summary>
			///  PDF417自定义条码列数;
			/// </summary>
			BnPIdx_8,
			/// <summary>
			///  错误纠正级别;
			/// </summary>
			BnPIdx_9,
			/// <summary>
			///  条码版本号:最小尺寸为0, 依次增加;;
			/// </summary>
			BnPIdx_10,
			/// <summary>
			///  固定文本X长度:高级里使能固定文本后, 需填写固定文本长度;
			/// </summary>
			BnPIdx_11,
			/// <summary>
			///  PDF417码缩短模式:0=不使能;1=使能;
			/// </summary>
			BnPIdx_12,
			/// <summary>
			///  点倍数:值范围:1-5;
			/// </summary>
			BnPIdx_13,
			/// <summary>
			///  显示人可识别字符:0=不显示;1=显示;
			/// </summary>
			BnPIdx_14,
			/// <summary>
			///  可识别字符笔号:范围:1-255;
			/// </summary>
			BnPIdx_15,
			/// <summary>
			///  显示校验码:0=不显示;1=显示;
			/// </summary>
			BnPIdx_16,
			/// <summary>
			///  填充可识别字符:0=不填充;1=填充;
			/// </summary>
			BnPIdx_17,
			/// <summary>
			///  轮廓:0=不使能;1=使能;
			/// </summary>
			BnPIdx_18,
			/// <summary>
			///  轮廓优先加工:0=不优先;1=优先;
			/// </summary>
			BnPIdx_19,
			/// <summary>
			///  可识别字符固定尺寸:0=不识别;1=可识别;
			/// </summary>
			BnPIdx_20,
			/// <summary>
			///  使能转义字符[DM码转义~]:0=不使能;1=使能;
			/// </summary>
			BnPIdx_21,
			/// <summary>
			///  语言编码, 默认0:437=ANSI(7Bit 1252);850=Latin-1(ISO 8859-1);932=日文;949=韩文;936=简体中文GBK;950=繁体中文BIG5;54936=GB18030;65001=unicode UFT-8;
			/// </summary>
			BnPIdx_22,
		};

		/// <summary>
		/// 条码造型数组定义 
		/// </summary>
		enum class BarcodeCulptDoubleParam
		{
			/// <summary>
			/// 一维码条码高;
			/// </summary>
			BDPIdx_0,
			/// <summary>
			/// 窄条模块宽,一维码单元模块尺寸;
			/// </summary>
			BDPIdx_1,
			/// <summary>
			/// 固定尺寸X;
			/// </summary>
			BDPIdx_2,
			/// <summary>
			/// 固定尺寸Y;
			/// </summary>
			BDPIdx_3,
			/// <summary>
			/// 一维码条比例系数0;
			/// </summary>
			BDPIdx_4,
			/// <summary>
			/// 一维码条比例系数1;
			/// </summary>
			BDPIdx_5,
			/// <summary>
			/// 一维码条比例系数2;
			/// </summary>
			BDPIdx_6,
			/// <summary>
			/// 一维码条比例系数3;
			/// </summary>
			BDPIdx_7,
			/// <summary>
			/// 一维码空比例系数0;
			/// </summary>
			BDPIdx_8,
			/// <summary>
			/// 一维码空比例系数1;
			/// </summary>
			BDPIdx_9,
			/// <summary>
			/// 一维码空比例系数2;
			/// </summary>
			BDPIdx_10,
			/// <summary>
			/// 一维码空比例系数3;
			/// </summary>
			BDPIdx_11,
			/// <summary>
			/// 空白字符比例;
			/// </summary>
			BDPIdx_12,
			/// <summary>
			/// 内部填充线间距;
			/// </summary>
			BDPIdx_13,
			/// <summary>
			/// 激光光斑直径;
			/// </summary>
			BDPIdx_14,
			/// <summary>
			/// 二维码窄条模块宽;
			/// </summary>
			BDPIdx_15,
			/// <summary>
			/// 左静区比例;
			/// </summary>
			BDPIdx_16,
			/// <summary>
			/// 中间静区比例;
			/// </summary>
			BDPIdx_17,
			/// <summary>
			/// 右静区比例;
			/// </summary>
			BDPIdx_18,
			/// <summary>
			/// 顶部静区比例;
			/// </summary>
			BDPIdx_19,
			/// <summary>
			/// 底部静区比例;
			/// </summary>
			BDPIdx_20,
			/// <summary>
			/// 人可识别字符高度;
			/// </summary>
			BDPIdx_21,
			/// <summary>
			/// 人可识别字符宽度;
			/// </summary>
			BDPIdx_22,
			/// <summary>
			/// 文本X偏移;
			/// </summary>
			BDPIdx_23,
			/// <summary>
			/// 文本Y偏移;
			/// </summary>
			BDPIdx_24,
			/// <summary>
			/// 文本间距;
			/// </summary>
			BDPIdx_25,
			/// <summary>
			/// 人可识别字符固定尺寸X;
			/// </summary>
			BDPIdx_26,
			/// <summary>
			/// 人可识别字符固定尺寸Y;
			/// </summary>
			BDPIdx_27,
		};

		/// <summary>
		/// 图像参数Int型数组定义 
		/// </summary>
		enum class ImageIntParam
		{
			/// <summary>
			/// 位图参数枚举所定义:<see cref="BmpAttributeBitKey"/>BmpAttributeBitKey;
			/// </summary>
			Index_0,
			/// <summary>
			/// 扫描参数枚举所定义:<see cref="BmpScanBitKey"/>BmpScanBitKey;
			/// </summary>
			Index_1,
			/// <summary>
			/// 固定参考点序号:左上=0;上中=1;右上=2;左中=3;中心=4;右中=5;左下=6;下中=7;右下=8;
			/// </summary>
			Index_2,
			/// <summary>
			/// XDPI;
			/// </summary>
			Index_3,
			/// <summary>
			/// YDPI;
			/// </summary>
			Index_4,
			/// <summary>
			/// 位图扫描增量模式:1=开启;0=关闭;
			/// </summary>
			Index_5,
			/// <summary>
			/// 位图扫描增量值:1=开启;0=关闭;
			/// </summary>
			Index_6,
			/// <summary>
			/// 低于阈值灰度数据不加工:1=开启;0=关闭;
			/// </summary>
			Index_7,
			/// <summary>
			/// 最低灰度值:范围:0-256;
			/// </summary>
			Index_8,
			/// <summary>
			/// 灰度功率曲线节点数(最大256);
			/// </summary>
			Index_9,
		};

		/// <summary>
		/// 图像参数Double型数组定义 
		/// </summary>
		enum class ImageDoubleParam
		{
			/// <summary>
			/// X尺寸;
			/// </summary>
			IdPIdx_0,
			/// <summary>
			/// Y尺寸;
			/// </summary>
			IdPIdx_1,
			/// <summary>
			/// 打点模式单点最大时间;
			/// </summary>
			IdPIdx_2,
			/// <summary>
			/// 双向扫描补偿;
			/// </summary>
			IdPIdx_3,
			/// <summary>
			/// 加速距离;
			/// </summary>
			IdPIdx_4,
			/// <summary>
			/// 减速距离;
			/// </summary>
			IdPIdx_5,
			/// <summary>
			/// 亮度值;
			/// </summary>
			IdPIdx_6,
			/// <summary>
			/// 对比度值;
			/// </summary>
			IdPIdx_7,
		};

		/// <summary>
		/// 激光器状态位定义 
		/// </summary>
		enum class LaserStateBitKey 
		{
			/// <summary>
			/// 激光器发射反馈:1=正常;0=异常;
			/// </summary>
			LSBit_0,
			/// <summary>
			/// 主电源启动反馈:1=正常;0=异常;
			/// </summary>
			LSBit_1,
			/// <summary>
			/// 系统上电反馈:1=正常;0=异常;
			/// </summary>
			LSBit_2,
			/// <summary>
			/// 激光器异常状态反馈:1=正常;0=异常;
			/// </summary>
			LSBit_3,
			/// <summary>
			/// 未定义;
			/// </summary>
			LSBit_4,
			/// <summary>
			/// 激光输出状态:1=打开;0=关闭;
			/// </summary>
			LSBit_5,
			/// <summary>
			/// 红光输出状态:1=打开;0=关闭;
			/// </summary>
			LSBit_6,
			/// <summary>
			/// 错误复位输出状态:1=打开;0=关闭;
			/// </summary>
			LSBit_7,
		};

		/// <summary>
		/// 板卡运行状态定义
		/// </summary>
		enum class CardRunStateBitKey
		{
			/// <summary>
			/// 加工过程中振镜位置是否超出最大加工幅面:0x1=振镜已超出最大加工幅面;0x0=振镜未超出最大加工幅面;
			/// </summary>
			CRBit_0,
		};

		/// <summary>
		/// 矢量文件属性位域值定义
		/// </summary>
		enum class VectorAttributeBitKey
		{
			/// <summary>
			/// 动态文件加工时重新载入;
			/// </summary>
			DYNFILE = 0x1000,
			/// <summary>
			/// 固定文件输入宽;
			/// </summary>
			WIDTH = 0x2000,
			/// <summary>
			/// 固定文件输入高;
			/// </summary>
			HEIGHT = 0x4000,
			/// <summary>
			/// 自动连接断开的曲线;
			/// </summary>
			AUTOCONNECTCURVE = 0x0100,
			/// <summary>
			/// 自动优化路径;
			/// </summary>
			OPTIMIZEPATH = 0x0200,
		};

		/// <summary>
		/// USB掉卡监控消息值定义
		/// </summary>
		enum class USBMonitorMsg
		{
			/// <summary>
			/// 发现掉卡;
			/// </summary>
			WM_REMOVE = 1041,
			/// <summary>
			/// 找到新卡;
			/// </summary>
			WM_ARRIVE = 1042,
		};

		/// <summary>
		/// Enum_Ezcad3系统参数Int类型参数,可利用INI读取工具读取和设置,文件位于PARAM\SysParam.ini
		/// </summary>
		enum class Ez3SysIntParamKey
		{
			/// <summary>
			/// 未定义;
			/// </summary>
			INT0,
			/// <summary>
			/// 未定义;
			/// </summary>
			INT1,
			/// <summary>
			/// 未定义;
			/// </summary>
			INT2,
			/// <summary>
			/// 未定义;
			/// </summary>
			INT3,
			/// <summary>
			/// 未定义;
			/// </summary>
			INT4,
			/// <summary>
			/// 未定义;
			/// </summary>
			INT5,
			/// <summary>
			/// 使能使用软件必须输入密码 0-1;
			/// </summary>
			INT6,
			/// <summary>
			/// 未定义;
			/// </summary>
			INT7,
			/// <summary>
			/// 使能自动备份 0-1;
			/// </summary>
			INT8,
			/// <summary>
			/// 自动备份时间;
			/// </summary>
			INT9,
			/// <summary>
			/// 使能显示圆形空间 0-1;
			/// </summary>
			INT10,
			/// <summary>
			/// 使能显示工作空间 0-1;
			/// </summary>
			INT11,
			/// <summary>
			/// 使能显示中心十字线 0-1;
			/// </summary>
			INT12,
			/// <summary>
			/// 使能显示网格 0-1;
			/// </summary>
			INT13,
			/// <summary>
			/// 未定义;
			/// </summary>
			INT14,
			/// <summary>
			/// 未定义;
			/// </summary>
			INT15,
			/// <summary>
			/// 未定义;
			/// </summary>
			INT16,
			/// <summary>
			/// 未定义;
			/// </summary>
			INT17,
			/// <summary>
			/// 轴回零点方式 0-8  排布方向:左下=1 中下=2 右下=3 右中=4 右上=5 中上=6 左上=7 左中=8 中心=0;
			/// </summary>
			INT18,
			/// <summary>
			/// 未定义;
			/// </summary>
			INT19,
			/// <summary>
			/// 未定义;
			/// </summary>
			INT20,
			/// <summary>
			/// 未定义;
			/// </summary>
			INT21,
			/// <summary>
			/// 未定义;
			/// </summary>
			INT22,
			/// <summary>
			/// 未定义;
			/// </summary>
			INT23,
			/// <summary>
			/// 未定义;
			/// </summary>
			INT24,
			/// <summary>
			/// 未定义;
			/// </summary>
			INT25,
			/// <summary>
			/// 未定义;
			/// </summary>
			INT26,
			/// <summary>
			/// 未定义;
			/// </summary>
			INT27,
			/// <summary>
			/// 未定义;
			/// </summary>
			INT28,
			/// <summary>
			/// 未定义;
			/// </summary>
			INT29,
			/// <summary>
			/// 未定义;
			/// </summary>
			INT30,
			/// <summary>
			/// 未定义;
			/// </summary>
			INT31,
			/// <summary>
			/// 未定义;
			/// </summary>
			INT32,
			/// <summary>
			/// 未定义;
			/// </summary>
			INT33,
			/// <summary>
			/// 未定义;
			/// </summary>
			INT34,
			/// <summary>
			/// 未定义;
			/// </summary>
			INT35,
			/// <summary>
			/// 未定义;
			/// </summary>
			INT36,
			/// <summary>
			/// 未定义;
			/// </summary>
			INT37,
			/// <summary>
			/// 未定义;
			/// </summary>
			INT38,
			/// <summary>
			/// 未定义;
			/// </summary>
			INT39,
			/// <summary>
			/// 未定义;
			/// </summary>
			INT40,
			/// <summary>
			/// 未定义;
			/// </summary>
			INT41,
			/// <summary>
			/// 未定义;
			/// </summary>
			INT42,
			/// <summary>
			/// 未定义;
			/// </summary>
			INT43,
			/// <summary>
			/// 未定义;
			/// </summary>
			INT44,
			/// <summary>
			/// 未定义;
			/// </summary>
			INT45,
			/// <summary>
			/// 未定义;
			/// </summary>
			INT46,
			/// <summary>
			/// 未定义;
			/// </summary>
			INT47,
			/// <summary>
			/// 未定义;
			/// </summary>
			INT48,
			/// <summary>
			/// 未定义;
			/// </summary>
			INT49,
			/// <summary>
			/// 未定义;
			/// </summary>
			INT50,
			/// <summary>
			/// 未定义;
			/// </summary>
			INT51,
			/// <summary>
			/// 未定义;
			/// </summary>
			INT52,
			/// <summary>
			/// 未定义;
			/// </summary>
			INT53,
			/// <summary>
			/// 未定义;
			/// </summary>
			INT54,
			/// <summary>
			/// 未定义;
			/// </summary>
			INT55,
			/// <summary>
			/// 未定义;
			/// </summary>
			INT56,
			/// <summary>
			/// 未定义;
			/// </summary>
			INT57,
			/// <summary>
			/// 未定义;
			/// </summary>
			INT58,
			/// <summary>
			/// 未定义;
			/// </summary>
			INT59,
			/// <summary>
			/// 未定义;
			/// </summary>
			INT60,
			/// <summary>
			/// 未定义;
			/// </summary>
			INT61,
			/// <summary>
			/// 未定义;
			/// </summary>
			INT62,
			/// <summary>
			/// 未定义;
			/// </summary>
			INT63,
			/// <summary>
			/// 未定义;
			/// </summary>
			INT64,
			/// <summary>
			/// 未定义;
			/// </summary>
			INT65,
			/// <summary>
			/// 未定义;
			/// </summary>
			INT66,
			/// <summary>
			/// 未定义;
			/// </summary>
			INT67,
			/// <summary>
			/// 未定义;
			/// </summary>
			INT68,
			/// <summary>
			/// 未定义;
			/// </summary>
			INT69,
			/// <summary>
			/// 未定义;
			/// </summary>
			INT70,
			/// <summary>
			/// 未定义;
			/// </summary>
			INT71,
			/// <summary>
			/// 未定义;
			/// </summary>
			INT72,
			/// <summary>
			/// 未定义;
			/// </summary>
			INT73,
			/// <summary>
			/// 未定义;
			/// </summary>
			INT74,
			/// <summary>
			/// 未定义;
			/// </summary>
			INT75,
			/// <summary>
			/// 未定义;
			/// </summary>
			INT76,
			/// <summary>
			/// 未定义;
			/// </summary>
			INT77,
			/// <summary>
			/// 未定义;
			/// </summary>
			INT78,
			/// <summary>
			/// 未定义;
			/// </summary>
			INT79,
			/// <summary>
			/// 未定义;
			/// </summary>
			INT80,
			/// <summary>
			/// 未定义;
			/// </summary>
			INT81,
			/// <summary>
			/// 未定义;
			/// </summary>
			INT82,
			/// <summary>
			/// 使能快速显示优化 0-1;
			/// </summary>
			INT83,
			/// <summary>
			/// 使能显示曲线方向 0-1;
			/// </summary>
			INT84,
			/// <summary>
			/// 未定义;
			/// </summary>
			INT85,
			/// <summary>
			/// 未定义;
			/// </summary>
			INT86,
			/// <summary>
			/// 未定义;
			/// </summary>
			INT87,
			/// <summary>
			/// 未定义;
			/// </summary>
			INT88,
			/// <summary>
			/// 未定义;
			/// </summary>
			INT89,
			/// <summary>
			/// 未定义;
			/// </summary>
			INT90,
			/// <summary>
			/// 未定义;
			/// </summary>
			INT91,
			/// <summary>
			/// 未定义;
			/// </summary>
			INT92,
			/// <summary>
			/// 最大计算线程数 1-12;
			/// </summary>
			INT93,
			/// <summary>
			/// 曲面计算精度 0-3;
			/// </summary>
			INT94,
			/// <summary>
			/// 未定义;
			/// </summary>
			INT95,
			/// <summary>
			/// 使能TCP/IP服务器 0-1;
			/// </summary>
			INT96,
			/// <summary>
			/// TCP/IP服务器通讯端口 0-65535;
			/// </summary>
			INT97,
			/// <summary>
			/// 未定义;
			/// </summary>
			INT98,
			/// <summary>
			/// 使能软件关闭时自动保存当前文件 0-1;
			/// </summary>
			INT99,
			/// <summary>
			/// 未定义;
			/// </summary>
			INT100,
			/// <summary>
			/// 未定义;
			/// </summary>
			INT101,
			/// <summary>
			/// 使能禁止显示文件处理过程对话框 0-1;
			/// </summary>
			INT102,
			/// <summary>
			/// 使能禁止显示计算过程对话框 0-1;
			/// </summary>
			INT103,
			/// <summary>
			/// 未定义;
			/// </summary>
			INT104,
			/// <summary>
			/// 绘制像素精度 1-5;
			/// </summary>
			INT105,
			/// <summary>
			/// 使能显示透明位图 0-1;
			/// </summary>
			INT106,
			/// <summary>
			/// 浮点数精度 3-7;
			/// </summary>
			INT107,
			/// <summary>
			/// 使能掉线自动连接 0-1;
			/// </summary>
			INT108,
			/// <summary>
			/// 掉线自动连接间隔时间;
			/// </summary>
			INT109,
			/// <summary>
			/// 未定义;
			/// </summary>
			INT110,
			/// <summary>
			/// 显示透明位图的透明百分比 0-100;
			/// </summary>
			INT111,
			/// <summary>
			/// 自动命名对象 0-1;
			/// </summary>
			INT112,
			/// <summary>
			/// 未定义;
			/// </summary>
			INT113,
			/// <summary>
			/// 使能禁止UNDO 0-1;
			/// </summary>
			INT114,
			/// <summary>
			/// 未定义;
			/// </summary>
			INT115,
			/// <summary>
			/// 未定义;
			/// </summary>
			INT116,
			/// <summary>
			/// 未定义;
			/// </summary>
			INT117,
			/// <summary>
			/// 未定义;
			/// </summary>
			INT118,
			/// <summary>
			/// 未定义;
			/// </summary>
			INT119,
			/// <summary>
			/// 未定义;
			/// </summary>
			INT120,
			/// <summary>
			/// 矢量图使能UTF-8编码 0-1;
			/// </summary>
			INT121,
			/// <summary>
			/// 未定义;
			/// </summary>
			INT122,
			/// <summary>
			/// 未定义;
			/// </summary>
			INT123,
			/// <summary>
			/// 未定义;
			/// </summary>
			INT124,
			/// <summary>
			/// 未定义;
			/// </summary>
			INT125,
			/// <summary>
			/// 未定义;
			/// </summary>
			INT126,
			/// <summary>
			/// 未定义;
			/// </summary>
			INT127,
			/// <summary>
			/// 未定义;
			/// </summary>
			INT128,
			/// <summary>
			/// 未定义;
			/// </summary>
			INT129,
			/// <summary>
			/// 未定义;
			/// </summary>
			INT130,
			/// <summary>
			/// 未定义;
			/// </summary>
			INT131,
		};

		/// <summary>
		/// Enum_Ezcad3系统参数Double类型参数,可利用INI读取工具读取和设置,文件位于PARAM\SysParam.ini
		/// </summary>
		enum class Ez3SysDoubleParamKey
		{
			/// <summary>
			/// 空间左下角X坐标点;
			/// </summary>
			DOUBLE0,
			/// <summary>
			/// 空间左下角Y坐标点;
			/// </summary>
			DOUBLE1,
			/// <summary>
			/// 空间尺寸宽度;
			/// </summary>
			DOUBLE2,
			/// <summary>
			/// 空间尺寸高度;
			/// </summary>
			DOUBLE3,
			/// <summary>
			/// 未定义;
			/// </summary>
			DOUBLE4,
			/// <summary>
			/// 未定义;
			/// </summary>
			DOUBLE5,
			/// <summary>
			/// 水平粘贴偏移;
			/// </summary>
			DOUBLE6,
			/// <summary>
			/// 垂直粘贴偏移;
			/// </summary>
			DOUBLE7,
			/// <summary>
			/// 键盘操控微调距离;
			/// </summary>
			DOUBLE8,
			/// <summary>
			/// 键盘操控大调整比例;
			/// </summary>
			DOUBLE9,
			/// <summary>
			/// 键盘操控旋转角度;
			/// </summary>
			DOUBLE10,
			/// <summary>
			/// 轴X零点位置;
			/// </summary>
			DOUBLE11,
			/// <summary>
			/// 轴Y零点位置;
			/// </summary>
			DOUBLE12,
			/// <summary>
			/// 网格间距 毫米;
			/// </summary>
			DOUBLE13,
			/// <summary>
			/// 未定义;
			/// </summary>
			DOUBLE14,
			/// <summary>
			/// 未定义;
			/// </summary>
			DOUBLE15,
			/// <summary>
			/// 未定义;
			/// </summary>
			DOUBLE16,
			/// <summary>
			/// 未定义;
			/// </summary>
			DOUBLE17,
			/// <summary>
			/// 未定义;
			/// </summary>
			DOUBLE18,
			/// <summary>
			/// 未定义;
			/// </summary>
			DOUBLE19,
			/// <summary>
			/// 未定义;
			/// </summary>
			DOUBLE20,
			/// <summary>
			/// 未定义;
			/// </summary>
			DOUBLE21,
			/// <summary>
			/// 未定义;
			/// </summary>
			DOUBLE22,
			/// <summary>
			/// 未定义;
			/// </summary>
			DOUBLE23,
			/// <summary>
			/// 未定义;
			/// </summary>
			DOUBLE24,
			/// <summary>
			/// 未定义;
			/// </summary>
			DOUBLE25,
			/// <summary>
			/// 未定义;
			/// </summary>
			DOUBLE26,
			/// <summary>
			/// 未定义;
			/// </summary>
			DOUBLE27,
			/// <summary>
			/// 未定义;
			/// </summary>
			DOUBLE28,
			/// <summary>
			/// 未定义;
			/// </summary>
			DOUBLE29,
			/// <summary>
			/// 未定义;
			/// </summary>
			DOUBLE30,
			/// <summary>
			/// 未定义;
			/// </summary>
			DOUBLE31,
			/// <summary>
			/// 未定义;
			/// </summary>
			DOUBLE32,
			/// <summary>
			/// 未定义;
			/// </summary>
			DOUBLE33,
			/// <summary>
			/// 未定义;
			/// </summary>
			DOUBLE34,
			/// <summary>
			/// 未定义;
			/// </summary>
			DOUBLE35,
			/// <summary>
			/// 未定义;
			/// </summary>
			DOUBLE36,
			/// <summary>
			/// 未定义;
			/// </summary>
			DOUBLE37,
			/// <summary>
			/// 未定义;
			/// </summary>
			DOUBLE38,
			/// <summary>
			/// 未定义;
			/// </summary>
			DOUBLE39,
			/// <summary>
			/// 未定义;
			/// </summary>
			DOUBLE40,
			/// <summary>
			/// 未定义;
			/// </summary>
			DOUBLE41,
			/// <summary>
			/// 未定义;
			/// </summary>
			DOUBLE42,
			/// <summary>
			/// 未定义;
			/// </summary>
			DOUBLE43,
			/// <summary>
			/// 未定义;
			/// </summary>
			DOUBLE44,
			/// <summary>
			/// 未定义;
			/// </summary>
			DOUBLE45,
			/// <summary>
			/// 未定义;
			/// </summary>
			DOUBLE46,
			/// <summary>
			/// 未定义;
			/// </summary>
			DOUBLE47,
			/// <summary>
			/// 未定义;
			/// </summary>
			DOUBLE48,
			/// <summary>
			/// 未定义;
			/// </summary>
			DOUBLE49,
			/// <summary>
			/// 未定义;
			/// </summary>
			DOUBLE50,
			/// <summary>
			/// 未定义;
			/// </summary>
			DOUBLE51,
			/// <summary>
			/// 未定义;
			/// </summary>
			DOUBLE52,
			/// <summary>
			/// 未定义;
			/// </summary>
			DOUBLE53,
			/// <summary>
			/// 未定义;
			/// </summary>
			DOUBLE54,
			/// <summary>
			/// 未定义;
			/// </summary>
			DOUBLE55,
			/// <summary>
			/// 未定义;
			/// </summary>
			DOUBLE56,
			/// <summary>
			/// 未定义;
			/// </summary>
			DOUBLE57,
			/// <summary>
			/// 未定义;
			/// </summary>
			DOUBLE58,
			/// <summary>
			/// 未定义;
			/// </summary>
			DOUBLE59,
			/// <summary>
			/// 未定义;
			/// </summary>
			DOUBLE60,
			/// <summary>
			/// 未定义;
			/// </summary>
			DOUBLE61,
			/// <summary>
			/// 未定义;
			/// </summary>
			DOUBLE62,
			/// <summary>
			/// 未定义;
			/// </summary>
			DOUBLE63,
			/// <summary>
			/// 未定义;
			/// </summary>
			DOUBLE64,
			/// <summary>
			/// 未定义;
			/// </summary>
			DOUBLE65,
			/// <summary>
			/// 未定义;
			/// </summary>
			DOUBLE66,
			/// <summary>
			/// 未定义;
			/// </summary>
			DOUBLE67,
			/// <summary>
			/// 未定义;
			/// </summary>
			DOUBLE68,
			/// <summary>
			/// 未定义;
			/// </summary>
			DOUBLE69,
			/// <summary>
			/// 未定义;
			/// </summary>
			DOUBLE70,
			/// <summary>
			/// 未定义;
			/// </summary>
			DOUBLE71,
			/// <summary>
			/// 未定义;
			/// </summary>
			DOUBLE72,
			/// <summary>
			/// 未定义;
			/// </summary>
			DOUBLE73,
			/// <summary>
			/// 未定义;
			/// </summary>
			DOUBLE74,
			/// <summary>
			/// 未定义;
			/// </summary>
			DOUBLE75,
			/// <summary>
			/// 未定义;
			/// </summary>
			DOUBLE76,
			/// <summary>
			/// 未定义;
			/// </summary>
			DOUBLE77,
			/// <summary>
			/// 未定义;
			/// </summary>
			DOUBLE78,
			/// <summary>
			/// 未定义;
			/// </summary>
			DOUBLE79,
			/// <summary>
			/// 未定义;
			/// </summary>
			DOUBLE80,
			/// <summary>
			/// 未定义;
			/// </summary>
			DOUBLE81,
			/// <summary>
			/// 未定义;
			/// </summary>
			DOUBLE82,
			/// <summary>
			/// 未定义;
			/// </summary>
			DOUBLE83,
			/// <summary>
			/// 未定义;
			/// </summary>
			DOUBLE84,
			/// <summary>
			/// 未定义;
			/// </summary>
			DOUBLE85,
			/// <summary>
			/// 未定义;
			/// </summary>
			DOUBLE86,
			/// <summary>
			/// 未定义;
			/// </summary>
			DOUBLE87,
			/// <summary>
			/// 未定义;
			/// </summary>
			DOUBLE88,
			/// <summary>
			/// 未定义;
			/// </summary>
			DOUBLE89,
			/// <summary>
			/// 未定义;
			/// </summary>
			DOUBLE90,
			/// <summary>
			/// 未定义;
			/// </summary>
			DOUBLE91,
			/// <summary>
			/// 未定义;
			/// </summary>
			DOUBLE92,
			/// <summary>
			/// 未定义;
			/// </summary>
			DOUBLE93,
			/// <summary>
			/// 未定义;
			/// </summary>
			DOUBLE94,
			/// <summary>
			/// 未定义;
			/// </summary>
			DOUBLE95,
			/// <summary>
			/// 未定义;
			/// </summary>
			DOUBLE96,
			/// <summary>
			/// 未定义;
			/// </summary>
			DOUBLE97,
			/// <summary>
			/// 未定义;
			/// </summary>
			DOUBLE98,
			/// <summary>
			/// 未定义;
			/// </summary>
			DOUBLE99,
			/// <summary>
			/// 未定义;
			/// </summary>
			DOUBLE100,
			/// <summary>
			/// 未定义;
			/// </summary>
			DOUBLE101,
			/// <summary>
			/// 未定义;
			/// </summary>
			DOUBLE102,
		};

		/// <summary>
		/// Enum_Ezcad3系统参数Color类型参数,可利用INI读取工具读取和设置,文件位于PARAM\SysParam.ini
		/// </summary>
		enum class Ez3SysColorParamKey
		{
			/// <summary>
			///  背景颜色值;
			/// </summary>
			COLOR0,
			/// <summary>
			///  工作空间颜色值;
			/// </summary>
			COLOR1,
			/// <summary>
			///  网格颜色值;
			/// </summary>
			COLOR2,
			/// <summary>
			///  未定义;
			/// </summary>
			COLOR3,
			/// <summary>
			///  辅助线颜色值;
			/// </summary>
			COLOR4,
			/// <summary>
			///  未定义;
			/// </summary>
			COLOR5,
			/// <summary>
			///  未定义;
			/// </summary>
			COLOR6,
			/// <summary>
			///  未定义;
			/// </summary>
			COLOR7,
			/// <summary>
			///  未定义;
			/// </summary>
			COLOR8,
			/// <summary>
			///  未定义;
			/// </summary>
			COLOR9,
			/// <summary>
			///  未定义;
			/// </summary>
			COLOR10,
			/// <summary>
			///  未定义;
			/// </summary>
			COLOR11,
			/// <summary>
			///  未定义;
			/// </summary>
			COLOR12,
			/// <summary>
			///  未定义;
			/// </summary>
			COLOR13,
			/// <summary>
			///  未定义;
			/// </summary>
			COLOR14,
			/// <summary>
			///  未定义;
			/// </summary>
			COLOR15,
			/// <summary>
			///  未定义;
			/// </summary>
			COLOR16,
			/// <summary>
			///  未定义;
			/// </summary>
			COLOR17,
			/// <summary>
			///  未定义;
			/// </summary>
			COLOR18,
			/// <summary>
			///  未定义;
			/// </summary>
			COLOR19,
			/// <summary>
			///  未定义;
			/// </summary>
			COLOR20,
			/// <summary>
			///  未定义;
			/// </summary>
			COLOR21,
			/// <summary>
			///  未定义;
			/// </summary>
			COLOR22,
			/// <summary>
			///  未定义;
			/// </summary>
			COLOR23,
			/// <summary>
			///  未定义;
			/// </summary>
			COLOR24,
			/// <summary>
			///  未定义;
			/// </summary>
			COLOR25,
			/// <summary>
			///  STL颜色值;
			/// </summary>
			COLOR26,
		};

		/// <summary>
		/// Enum_Ezcad3系统参数String类型参数,可利用INI读取工具读取和设置,文件位于PARAM\SysParam.ini
		/// </summary>
		enum class Ez3SysStringParamKey
		{
			/// <summary>
			/// 未定义;
			/// </summary>
			STRING0,
			/// <summary>
			/// 未定义;
			/// </summary>
			STRING1,
			/// <summary>
			/// 未定义;
			/// </summary>
			STRING2,
			/// <summary>
			/// 未定义;
			/// </summary>
			STRING3,
			/// <summary>
			/// 未定义;
			/// </summary>
			STRING4,
			/// <summary>
			/// 未定义;
			/// </summary>
			STRING5,
			/// <summary>
			/// 未定义;
			/// </summary>
			STRING6,
			/// <summary>
			/// 未定义;
			/// </summary>
			STRING7,
			/// <summary>
			/// 未定义;
			/// </summary>
			STRING8,
			/// <summary>
			/// 未定义;
			/// </summary>
			STRING9,
			/// <summary>
			/// 未定义;
			/// </summary>
			STRING10,
			/// <summary>
			/// 未定义;
			/// </summary>
			STRING11,
			/// <summary>
			/// 未定义;
			/// </summary>
			STRING12,
			/// <summary>
			/// 未定义;
			/// </summary>
			STRING13,
			/// <summary>
			/// 未定义;
			/// </summary>
			STRING14,
			/// <summary>
			/// 未定义;
			/// </summary>
			STRING15,
			/// <summary>
			/// 未定义;
			/// </summary>
			STRING16,
			/// <summary>
			/// 未定义;
			/// </summary>
			STRING17,
			/// <summary>
			/// 未定义;
			/// </summary>
			STRING18,
			/// <summary>
			/// 未定义;
			/// </summary>
			STRING19,
			/// <summary>
			/// 未定义;
			/// </summary>
			STRING20,
			/// <summary>
			/// 未定义;
			/// </summary>
			STRING21,
			/// <summary>
			/// 未定义;
			/// </summary>
			STRING22,
			/// <summary>
			/// 未定义;
			/// </summary>
			STRING23,
			/// <summary>
			/// 未定义;
			/// </summary>
			STRING24,
			/// <summary>
			/// 未定义;
			/// </summary>
			STRING25,
			/// <summary>
			/// 未定义;
			/// </summary>
			STRING26,
			/// <summary>
			/// 未定义;
			/// </summary>
			STRING27,
			/// <summary>
			/// 未定义;
			/// </summary>
			STRING28,
			/// <summary>
			/// 未定义;
			/// </summary>
			STRING29,
			/// <summary>
			/// 未定义;
			/// </summary>
			STRING30,
			/// <summary>
			/// 未定义;
			/// </summary>
			STRING31,
			/// <summary>
			/// 未定义;
			/// </summary>
			STRING32,
			/// <summary>
			/// 未定义;
			/// </summary>
			STRING33,
			/// <summary>
			/// 未定义;
			/// </summary>
			STRING34,
			/// <summary>
			/// 未定义;
			/// </summary>
			STRING35,
			/// <summary>
			/// 未定义;
			/// </summary>
			STRING36,
			/// <summary>
			/// 未定义;
			/// </summary>
			STRING37,
			/// <summary>
			/// 未定义;
			/// </summary>
			STRING38,
			/// <summary>
			/// 未定义;
			/// </summary>
			STRING39,
			/// <summary>
			/// 未定义;
			/// </summary>
			STRING40,
			/// <summary>
			/// 未定义;
			/// </summary>
			STRING41,
			/// <summary>
			/// 未定义;
			/// </summary>
			STRING42,
			/// <summary>
			/// 未定义;
			/// </summary>
			STRING43,
			/// <summary>
			/// 未定义;
			/// </summary>
			STRING44,
			/// <summary>
			/// 未定义;
			/// </summary>
			STRING45,
			/// <summary>
			/// 未定义;
			/// </summary>
			STRING46,
			/// <summary>
			/// 未定义;
			/// </summary>
			STRING47,
			/// <summary>
			/// 未定义;
			/// </summary>
			STRING48,
			/// <summary>
			/// 未定义;
			/// </summary>
			STRING49,
			/// <summary>
			/// 未定义;
			/// </summary>
			STRING50,
			/// <summary>
			/// TCP/IP服务器通讯IP地址;
			/// </summary>
			STRING51,
			/// <summary>
			/// 未定义;
			/// </summary>
			STRING52,
			/// <summary>
			/// 未定义;
			/// </summary>
			STRING53,
			/// <summary>
			/// 未定义;
			/// </summary>
			STRING54,
		};

		/// <summary>
		/// 列表加工工作模式定义
		/// </summary>
		enum class ListReadyMode:uint32_t
		{
			/// <summary>
			/// 静态标刻;
			/// </summary>
			StaticMark = 0x00000000,
			/// <summary>
			/// 屏蔽ESC键盘消息;
			/// </summary>
			DisableEsc = 0x00000001,
			/// <summary>
			/// 红光指示;
			/// </summary>
			RedLight = 0x00000002,
			/// <summary>
			/// 禁止复位列表(可用于子列表);
			/// </summary>
			DisableResetList = 0x00000004,
			/// <summary>
			/// 飞行标刻;
			/// </summary>
			FlyMark = 0x00000400,
			/// <summary>
			/// 焊接模式;
			/// </summary>
			WeldMode = 0x00002000,
			/// <summary>
			/// 只下发数据不加工;
			/// </summary>
			SendDataNotMark = 0x00008000,
			/// <summary>
			/// 控制变量文本不更新;
			/// </summary>
			VariableTextNotUpdate= 0x0020000,
			/// <summary>
			/// 禁止飞行打标自动排序;
			/// </summary>
			FlyMarkDataNotSort = 0x00200000,
			/// <summary>
			/// 计算模式(用于预估加工时间);
			/// </summary>
			CalculateMode = 0x01000000,
			/// <summary>
			/// 脱机模式;
			/// </summary>
			Offline = 0x02000000,
		};
ListReadyMode operator|(ListReadyMode a, ListReadyMode b);
ListReadyMode& operator|=(ListReadyMode& a, ListReadyMode b);
ListReadyMode& operator&=(ListReadyMode& a, ListReadyMode b);
ListReadyMode operator~(ListReadyMode a);

		/// <summary>
		/// 普通标刻接口工作模式定义
		/// </summary>
		enum class MarkEntMode:uint32_t
		{
			/// <summary>
			/// 静态标刻;
			/// </summary>
			StaticMark = 0x00000000,
			/// <summary>
			/// 屏蔽ESC键盘消息;
			/// </summary>
			DisableEsc = 0x00000001,
			/// <summary>
			/// 红光指示;
			/// </summary>
			RedLight = 0x00000002,
			/// <summary>
			/// 飞行标刻;
			/// </summary>
			FlyMark = 0x00000400,
			/// <summary>
			/// 焊接模式;
			/// </summary>
			WeldMode = 0x00002000,
			/// <summary>
			/// 只下发数据不加工;
			/// </summary>
			SendDataNotMark = 0x00008000,
			/// <summary>
			/// 计算模式_用于预估加工时间;
			/// </summary>
			CalculateMode = 0x01000000,
		};
MarkEntMode operator|(MarkEntMode a, MarkEntMode b);
MarkEntMode& operator|=(MarkEntMode& a, MarkEntMode b);
MarkEntMode& operator&=(MarkEntMode& a, MarkEntMode b);
MarkEntMode operator~(MarkEntMode a);

/// <summary>
/// 创建控制器对象时所指定类型的标志.
/// </summary>
enum class ControlType
{
			/// <summary>
			/// 延时器.;
			/// </summary>
			TimerDelay = 1,
			/// <summary>
			/// 输入口.;
			/// </summary>
			Input = 2,
			/// <summary>
			/// 输出口.;
			/// </summary>
			Output = 3,
			/// <summary>
			/// 扩展轴.;
			/// </summary>
			Extaxis = 5,
			/// <summary>
			/// 编码器距离.;
			/// </summary>
			Encoder = 9,
		};

		/// <summary>
		/// 字体类型属性定义
		/// </summary>
		enum class FontType
		{
			/// <summary>
			/// JczSingle字型;
			/// </summary>
			JSF = 0x1001,
			/// <summary>
			/// TrueType字型;
			/// </summary>
			TTF = 0x0002,
			/// <summary>
			/// DotMatrix字型;
			/// </summary>
			DMF = 0x0004,
			/// <summary>
			/// BarCode字型;
			/// </summary>
			BCF = 0x0008,
			/// <summary>
			/// SHX字型;
			/// </summary>
			SHX = 0x0010,
		};

		/// <summary>
		/// 对象类型属性信息定义
		/// </summary>
		enum class EntityTypeBitKey
		{
			/// <summary>
			/// 非对象类型;
			/// </summary>
			NONE = 0x0000,
			/// <summary>
			/// 二维曲线;
			/// </summary>
			CURVE2D = 0x0001,
			/// <summary>
			/// 二维点;
			/// </summary>
			POINT2D = 0x0002,
			/// <summary>
			/// 二维矩形;
			/// </summary>
			RECT2D = 0x0003,
			/// <summary>
			/// 二维圆;
			/// </summary>
			CIRCLE2D = 0x0004,
			/// <summary>
			/// 二维椭圆;
			/// </summary>
			ELLIPSE2D = 0x0005,
			/// <summary>
			/// 二维多边形;
			/// </summary>
			POLYGON2D = 0x0006,
			/// <summary>
			/// 二维螺旋线;
			/// </summary>
			SPIRAL2D = 0x0007,
			/// <summary>
			/// 未知类型;
			/// </summary>
			UNKNOW = 0x0008,
			/// <summary>
			/// 三维曲线;
			/// </summary>
			CURVE3D = 0x000a,
			/// <summary>
			/// 图形集合;
			/// </summary>
			GROUP = 0x0010,
			/// <summary>
			/// 填充;
			/// </summary>
			HATCH_GROUP = 0x0020,
			/// <summary>
			/// 图形组合;
			/// </summary>
			COMBINE = 0x0030,
			/// <summary>
			/// 位图;
			/// </summary>
			BITMAP = 0x0040,
			/// <summary>
			/// 向量文件对象;
			/// </summary>
			VECTORFILE = 0x0050,
			/// <summary>
			/// 超级文字;
			/// </summary>
			SUPERTEXT = 0x0800,
			/// <summary>
			/// 控制对象;
			/// </summary>
			CONTROL = 0x1000,
			/// <summary>
			/// 延时器;
			/// </summary>
			TIMERDELAY = 0x2000,
			/// <summary>
			/// IO输入对象;
			/// </summary>
			IOINPUT = 0x3000,
			/// <summary>
			/// IO输出对象;
			/// </summary>
			IOOUTPUT = 0x4000,
			/// <summary>
			/// 扩展轴对象;
			/// </summary>
			EXTAXIS = 0x5000,
			/// <summary>
			/// 飞标流水线移动距离;
			/// </summary>
			FLYMOVEDIST = 0x6000,
			/// <summary>
			/// 图层对象;
			/// </summary>
			LAYER = 0x9000,
		};

		/// <summary>
		/// 曲线点连接标志位
		/// </summary>
		enum class CurveConnectFlag
		{
			/// <summary>
			/// 起点与起点相连;
			/// </summary>
			StartAndStart = 0x01,
			/// <summary>
			/// 起点与末点相连;
			/// </summary>
			StartAndEnd = 0x02,
			/// <summary>
			/// 末点与起点相连;
			/// </summary>
			EndAndStart = 0x04,
			/// <summary>
			/// 末点与末点相连;
			/// </summary>
			EndAndEnd = 0x08,
		};

		/// <summary>
		/// 图像扫描参数位域值定义
		/// </summary>
		enum class BmpScanBitKey
		{
			/// <summary>
			/// 空;
			/// </summary>
			NONE = 0x0000,
			/// <summary>
			/// 图像反转;
			/// </summary>
			INVERT = 0x0001,
			/// <summary>
			/// 图像灰度;
			/// </summary>
			GRAY = 0x0002,
			/// <summary>
			/// 图像亮度;
			/// </summary>
			LIGHT = 0x0004,
			/// <summary>
			/// 网点处理;
			/// </summary>
			DITHER = 0x0010,
			/// <summary>
			/// 镜像X;
			/// </summary>
			MIRRORX = 0x0020,
			/// <summary>
			/// 镜像Y;
			/// </summary>
			MIRRORY = 0x0040,
			/// <summary>
			/// 隔行错位;
			/// </summary>
			OFFSETPT = 0x0100,
			/// <summary>
			/// 优化模式;
			/// </summary>
			OPTIMIZE = 0x0200,
			/// <summary>
			/// 扫描反转;
			/// </summary>
			SCANREVERSE = 0x0400,
			/// <summary>
			/// 双向扫描;
			/// </summary>
			BIDIR = 0x1000,
			/// <summary>
			/// Y向扫描;
			/// </summary>
			YDIR = 0x2000,
			/// <summary>
			/// 打点模式;
			/// </summary>
			DRILL = 0x4000,
			/// <summary>
			/// 调整功率;
			/// </summary>
			POWER = 0x8000,
		};

		/// <summary>
		/// 图像特性参数位域值定义
		/// </summary>
		enum class BmpAttributeBitKey
		{
			/// <summary>
			/// 空;
			/// </summary>
			NONE = 0x0000,
			/// <summary>
			/// 动态文件;
			/// </summary>
			DYNFILE = 0x1000,
			/// <summary>
			/// 固定文件输入宽;
			/// </summary>
			WIDTH = 0x2000,
			/// <summary>
			/// 固定文件输入高;
			/// </summary>
			HEIGHT = 0x4000,
			/// <summary>
			/// 固定DPI;
			/// </summary>
			DPI = 0x8000,
			/// <summary>
			/// 是否使能真实位图DPI;
			/// </summary>
			DPITRUE = 0x10000,
		};

/// <summary>
/// Enum_初始化模式定义.
/// </summary>
enum class InitialMode
{
			/// <summary>
			/// 此模式遵循[Controller.ini]配置文件中配置;
			/// </summary>
			ByCfg,
			/// <summary>
			/// USB模式,兼容PCIE,此模式遵循[Controller.ini]配置文件中配置;
			/// </summary>
			USB = ByCfg,
			/// <summary>
			/// 网络模式,此模式遵循[Controller.ini]配置文件中配置;
			/// </summary>
			Ethernet = ByCfg,
			/// <summary>
			/// SPI模式(仅linux平台有效);
			/// </summary>
			SPI,
			/// <summary>
			/// 同USB模式,此模式为程序直接修改[Controller.ini]配置,遵循程序设置;
			/// </summary>
			USB_ChangeCfg,
			/// <summary>
			/// 同网络模式,此模式为程序直接修改[Controller.ini]配置,遵循程序设置;
			/// </summary>
			Ethernet_ChangeCfg,
			/// <summary>
			/// 同网络模式,此模式只针对硬件版本是V4卡,此模式为程序直接修改[Controller.ini]配置,遵循程序设置;
			/// </summary>
			Ethernet2_ChangeCfg,
			/// <summary>
			/// 同SPI模式,此模式为程序直接修改[Controller.ini]配置,遵循程序设置;
			/// </summary>
			SPI_ChangeCfg,
		};

/// <summary>
/// 日志类型.
/// </summary>
enum class LogType
{
			/// <summary>
			/// 信息.;
			/// </summary>
			Info,
			/// <summary>
			/// 警告.;
			/// </summary>
			Warning,
			/// <summary>
			/// 错误.;
			/// </summary>
			Error,
		};

/// <summary>
/// 日志等级.
/// </summary>
enum class LogLevel
{
			/// <summary>
			/// 简洁.;
			/// </summary>
			Concise = 0x01,
			/// <summary>
			/// 标准.;
			/// </summary>
			Normal = 0x02,
			/// <summary>
			/// 详细.;
			/// </summary>
			Detailed = 0x04,
			/// <summary>
			/// 密集.;
			/// </summary>
			Dense = 0x08,
			/// <summary>
			/// 循环.;
			/// </summary>
			Recurrently = 0x10,
		};

/// <summary>
/// 对象属性克隆标志.
/// </summary>
enum class EntityPropertyCloneFlag : unsigned short
{
			/// <summary>
			/// 水平单向.;
			/// </summary>
			HorizontalBidirection = 0,
			/// <summary>
			/// 垂直单向.;
			/// </summary>
			VerticalBidirection= 1,
			/// <summary>
			/// 水平双向.;
			/// </summary>
			HorizontalUnidirection= 2,
			/// <summary>
			/// 垂直双向.;
			/// </summary>
			VerticalUnidirection= 3,
		};

/// <summary>
/// 曲线链上段的类型.
/// </summary>
enum class EntitySectType : unsigned short
{
			/// <summary>
			/// NULL;
			/// </summary>
			SECTTYPE_NULL = 0x0000,
			/// <summary>
			/// 点;
			/// </summary>
			SECTTYPE_POINT2D = 0x0001,
			/// <summary>
			/// 弧线;
			/// </summary>
			SECTTYPE_ARC2D = 0x0002,
			/// <summary>
			/// 圆;
			/// </summary>
			SECTTYPE_CIRCLE2D = 0x0003,
			/// <summary>
			/// 椭圆;
			/// </summary>
			SECTTYPE_ELLIPSE2D = 0x0004,
			/// <summary>
			/// 直线;
			/// </summary>
			SECTTYPE_LINE2D = 0x0100,
			/// <summary>
			/// 贝塞尔;
			/// </summary>
			SECTTYPE_BEZIER2D = 0x0300,
		};

/// <summary>
/// 曲线链上段上的点类型标志.
/// </summary>
enum class SectNodeFlag : unsigned short
{
			/// <summary>
			/// 节点选中标志;
			/// </summary>
			NODEFLAG_PICK = 0x0001,
			/// <summary>
			/// 节点平滑连接;
			/// </summary>
			NODEFLAG_SMOOTH = 0x0002,
			/// <summary>
			/// 节点对称连接;
			/// </summary>
			NODEFLAG_SYMMETRY = 0x0004,
		};

/// <summary>
/// 激光器种类标志.
/// </summary>
enum class LaserCategory : unsigned short
{
			/// <summary>
			/// CO2种类;
			/// </summary>
			LC_CO2 = 0,
			/// <summary>
			/// YAG种类;
			/// </summary>
			LC_YAG = 1,
			/// <summary>
			/// FIBER种类;
			/// </summary>
			LC_FIBER = 2,
			/// <summary>
			/// SPI种类;
			/// </summary>
			LC_SPI = 3,
			/// <summary>
			/// QCW种类;
			/// </summary>
			LC_QCW = 4,
		};

/// <summary>
/// 激光器光纤种类标志.
/// </summary>
enum class FiberCategory : unsigned short
{
			/// <summary>
			/// IPG_YLP(Type:D);
			/// </summary>
			FIBER_IPG_YLP_Type_D,
			/// <summary>
			/// IPG_YLPM(Type:D);
			/// </summary>
			FIBER_IPG_YLPM_Type_D,
			/// <summary>
			/// IPG_YLPP(Type:E);
			/// </summary>
			FIBER_IPG_YLPP_Type_E,
			/// <summary>
			/// IPG_YLPN_1X100(Type:YLP-HP-A);
			/// </summary>
			FIBER_IPG_YLPN_1X100_Type_YLP_HP_A,
			/// <summary>
			/// IPG_YLPN_1X120(Type:E);
			/// </summary>
			FIBER_IPG_YLPN_1X120_Type_E,
			/// <summary>
			/// IPG_YLPN_2X200(Type:E);
			/// </summary>
			FIBER_IPG_YLPN_2X200_Type_E,
			/// <summary>
			/// IPG_YLP_UV(Type:E);
			/// </summary>
			FIBER_IPG_YLP_UV_Type_E,
			/// <summary>
			/// IPG_YLPN_SKAM(Type:G);
			/// </summary>
			FIBER_IPG_YLPN_SKAM_Type_G,
			/// <summary>
			/// IPG_YLPN_R(Type:YLP-HP-B);
			/// </summary>
			FIBER_IPG_YLPN_R_Type_YLP_HP_B,
			/// <summary>
			/// RAYCUS;
			/// </summary>
			FIBER_RAYCUS,
			/// <summary>
			/// RAYCUS MOPA;
			/// </summary>
			FIBER_RAYCUS_MOPA,
			/// <summary>
			/// QUANTEL_M20HF;
			/// </summary>
			FIBER_QUANTEL_M20HF,
			/// <summary>
			/// QUANTEL_M20;
			/// </summary>
			FIBER_QUANTEL_M20,
			/// <summary>
			/// QUANTEL_M20EG;
			/// </summary>
			FIBER_QUANTEL_M20EG,
			/// <summary>
			/// QUANTEL_M30EG;
			/// </summary>
			FIBER_QUANTEL_M30EG,
			/// <summary>
			/// MANLIGHT_P;
			/// </summary>
			FIBER_MANLIGHT_P,
			/// <summary>
			/// VGEN_YPFL;
			/// </summary>
			FIBER_VGEN_YPFL,
			/// <summary>
			/// JPT;
			/// </summary>
			FIBER_JPT,
			/// <summary>
			/// EO;
			/// </summary>
			FIBER_EO,
			/// <summary>
			/// Orion Laser;
			/// </summary>
			FIBER_Orion_Laser,
			/// <summary>
			/// BRIMO Laser;
			/// </summary>
			FIBER_BRIMO_Laser,
			/// <summary>
			/// GZ_YFPN(Type:D);
			/// </summary>
			FIBER_GZ_YFPN_Type_D,
			/// <summary>
			/// GZ_YFPP(Type:D);
			/// </summary>
			FIBER_GZ_YFPP_Type_D,
			/// <summary>
			/// MaxP_MFPT(Type:D);
			/// </summary>
			FIBER_MaxP_MFPT_Type_D,
			/// <summary>
			/// MAX;
			/// </summary>
			FIBER_MAX,
		};

//**********************************

/// <summary>
/// 日志回调接口委托.
/// <param name="str">日志信息.</param>
/// <param name="ownerId">消息所有者ID,默认0,可协商.</param>
/// <param name="level">日志级别.</param>
/// <param name="msgType">日志类别.</param>
/// </summary>
typedef void (*LogCallbackHandler)(const TCHAR* str, int ownerId, LogLevel level, LogType msgType);

        /// <summary>
        /// 得到当前窗体的句柄
        /// </summary>
        /// <returns></returns>
typedef HWND (*getForegroundWindow)(void); 

/// <summary>
/// <para>API编码:[67236723]</para>
/// 接口说明:1.强制停止扩展轴运动； 2.当轴以速度模式（E3_MarkerSetStepperAxisVelocityMode）进行移动，用此接口停止； 3.当轴为非等待模式下运动，用此接口停止；
/// <para>文档定位:硬件-资源-运动轴-动作</para>
/// </summary>
/// <param name="idMarker">:板卡ID</param>
/// <param name="axis">:需要操作的扩展轴序号；取值范围0-5</param>
typedef E3_ERR (*e3_AxisStopForce)(E3_ID idMarker,int axis);

/// <summary>
/// <para>API编码:[12305230]</para>
/// 接口说明:清除指定层ID中的子对象
/// <para>文档定位:数据-对象操作-对象间操作</para>
/// </summary>
/// <param name="idLayer">:指定层ID</param>
/// <param name="bUpdateParentInfo">:是否更新对象列表；true更新，false不更新</param>
typedef E3_ERR (*e3_ClearLayerAllChild)(E3_ID idLayer,BOOL bUpdateParentInfo);

/// <summary>
/// <para>API编码:[35667791]</para>
/// 接口说明:得到模拟输入口(ADC1~ADC4)的模拟量；
/// <para>文档定位:硬件-资源-模拟量IO-读</para>
/// </summary>
/// <param name="idMarker">:板卡ID</param>
/// <param name="PortNum">:模拟量输入端口；取值范围1-4；</param>
/// <param name="AnalogValue">:得到模拟量对应的bit值;当卡是MCS时，电压-10V到10V对应410到3686</param>
typedef E3_ERR (*e3_Get3DPrintAnalogOutput)(E3_ID idMarker,unsigned char PortNum,unsigned short& AnalogValue);

/// <summary>
/// <para>API编码:[43922762]</para>
/// 接口说明:得到指定对象ID的三组填充参数;
/// <para>文档定位:数据-填充相关</para>
/// </summary>
/// <param name="idEnt">:对象ID</param>
/// <param name="bEnableContour">:是否使能轮廓;true使能，false不使能</param>
/// <param name="bContourFirst">:是否使能轮廓优先;true使能，false不使能；</param>
/// <param name="param1">:填充参数1</param>
/// <param name="param2">:填充参数2</param>
/// <param name="param3">:填充参数3</param>
typedef E3_ERR (*e3_GetEntHatchParam)(E3_ID idEnt,BOOL& bEnableContour,BOOL& bContourFirst,HatchParam& param1,HatchParam& param2,HatchParam& param3);

/// <summary>
/// <para>API编码:[12099349]</para>
/// 接口说明:1.得到填充对象中的填充部分（填充线对象）,一个填充对象解散之后会有轮廓和填充线对象及若干轮廓对象，此接口得到的就是填充线对象,轮廓则利用[E3_GetEntParam1]接口来获取.
/// <para>文档定位:数据-对象操作-对象ID关系</para>
/// </summary>
/// <param name="idEnt">:对象ID</param>
/// <param name="idEntHatch">:填充属性的对象ID</param>
typedef E3_ERR (*e3_GetEntParam3)(E3_ID idEnt,E3_ID& idEntHatch);

/// <summary>
/// <para>API编码:[68119134]</para>
/// 接口说明:1.得到slc文件中的指定层序号对应的对象ID，Z值和slc文件总层数，最小Z值，层厚，外包盒的最小最大坐标； 2.得到的对象ID，需要用接口E3_AddEntityToChild添加到指定层；
/// <para>文档定位:数据-3D操作</para>
/// </summary>
/// <param name="idEM">:对象管理器ID</param>
/// <param name="strFile">:slc文件完整路径</param>
/// <param name="nLayerIndex">:slc文件层序号</param>
/// <param name="nTotalLayerCount">:slc文件总层数</param>
/// <param name="dMinZLevel">:slc文件最小Z值</param>
/// <param name="dLayerThickness">:slc文件层厚</param>
/// <param name="dZ">:层序号对应的Z值</param>
/// <param name="bHaveExtents">:文件是否包括外轮廓数据;true包含，false不包含</param>
/// <param name="ptExtentsMin">:外轮廓的最小值</param>
/// <param name="ptExtentsMax">:外轮廓的最大值</param>
/// <param name="idNewEnt">:层序号对应的对象ID</param>
typedef E3_ERR (*e3_GetOneLayerFromSlcFile2)(E3_ID idEM,TCHAR* strFile,int nLayerIndex,int& nTotalLayerCount,double& dMinZLevel,double& dLayerThickness,double& dZ,BOOL& bHaveExtents,Pt3d& ptExtentsMin,Pt3d& ptExtentsMax,E3_ID& idNewEnt);

/// <summary>
/// <para>API编码:[54919416]</para>
/// 接口说明:1.标刻九点校正标准图形（田字格图形）； 2.使用默认参数标刻，不受是否使能校正加载校正文件，是否修改振镜镜像等影响；
/// <para>文档定位:硬件-资源-振镜-校正</para>
/// </summary>
/// <param name="idMarker">:板卡ID</param>
/// <param name="nRectSizeDa">:标准图形对应的DA值</param>
/// <param name="nPointSizeDa">:用于区别方向的标志位对应的DA值</param>
typedef E3_ERR (*e3_MarkCorStdPoint)(E3_ID idMarker,int nRectSizeDa,int nPointSizeDa);

/// <summary>
/// <para>API编码:[01874792]</para>
/// 接口说明:得到MCS板卡上输入口的值；
/// <para>文档定位:硬件-资源-数字量IN-查询</para>
/// </summary>
/// <param name="idMarker">:板卡ID</param>
/// <param name="wPortData">:1.输入口对应的bit值; 2.共16个输入口，端口从0到15； 3.假设端口nPort，端口对应的值为usPortValue=1nPort，参数usInputData&usPortValue==usPortValue， 表明端口nPort有输入；</param>
typedef E3_ERR (*e3_MarkerGetExtInputPortStatus)(E3_ID idMarker,WORD& wPortData);

/// <summary>
/// <para>API编码:[78477434]</para>
/// 接口说明:得到MCS板卡上输出口的值；
/// <para>文档定位:硬件-资源-数字量OUT-查询</para>
/// </summary>
/// <param name="idMarker">:板卡ID</param>
/// <param name="wPortData">:1.输出口对应的bit值; 2.共24个输出口，端口从0到23； 3.假设端口nPort，端口对应的值为unPortValue=1nPort，参数unOutputData&unPortValue==unPortValue， 表明端口nPort有输出；</param>
typedef E3_ERR (*e3_MarkerGetExtOutputPort)(E3_ID idMarker,unsigned int& wPortData);

/// <summary>
/// <para>API编码:[32825130]</para>
/// 接口说明:1.列表功能； 2.选择打标使用的校正表序号； 3.校正表序号需要用接口E3_MarkerSetCorFile2进行设置；
/// <para>文档定位:硬件-资源-振镜-校正</para>
/// </summary>
/// <param name="idMarker">:板卡ID</param>
/// <param name="indexTable">:校正表号;取值范围1-4</param>
/// <param name="bEnableCor">:是否使用校正； 默认true</param>
typedef E3_ERR (*e3_MarkerSelectCorTableToList)(E3_ID idMarker,int indexTable,BOOL bEnableCor);

/// <summary>
/// <para>API编码:[92816036]</para>
/// 接口说明:给指定板卡设置指定的校正文件，需要校正文件完整路径；
/// <para>文档定位:硬件-资源-振镜-校正</para>
/// </summary>
/// <param name="idMarker">:板卡ID</param>
/// <param name="szFileName[256]">:校正文件完整路径</param>
typedef E3_ERR (*e3_MarkerSetCorFile)(E3_ID idMarker,TCHAR szFileName[256]);

/// <summary>
/// <para>API编码:[94693559]</para>
/// 接口说明:设置MCS板卡上的输出口；
/// <para>文档定位:硬件-资源-数字量OUT-动作</para>
/// </summary>
/// <param name="idMarker">:板卡ID</param>
/// <param name="wPortData">:1.输出口对应的bit值; 2.共24个输出口，端口从0到23； 3.假设端口nPort，端口对应的值为unPortValue=1nPort，参数unOutputData&unPortValue==unPortValue， 表明端口nPort有输出；</param>
typedef E3_ERR (*e3_MarkerSetExtOutputPort)(E3_ID idMarker,unsigned int wPortData);

/// <summary>
/// <para>API编码:[17999409]</para>
/// 接口说明:1.轴速度模式； 2.轴根据设定的速度限制参数（最小速度、最大速度和加速度）运动到设定的目标速度，之后一直按照设定的速度无目的的运行
/// <para>文档定位:硬件-资源-运动轴-动作</para>
/// </summary>
/// <param name="idMarker">:板卡ID</param>
/// <param name="nAxisNo">:扩展轴序号;取值范围0-5</param>
/// <param name="dVelocity">:目标速度</param>
typedef E3_ERR (*e3_MarkerSetStepperAxisVelocityMode)(E3_ID idMarker,int nAxisNo,double dVelocity);

/// <summary>
/// <para>API编码:[49368220]</para>
/// 接口说明:将对象里的子对象进行排序
/// <para>文档定位:数据-对象操作-对象间操作</para>
/// </summary>
/// <param name="idEnt">:对象ID</param>
/// <param name="bYFirst">:是否按Y优先排序;true是，false否</param>
/// <param name="bMinToMax">:坐标从小到大排序;true坐标从小到大排序，false坐标从大大小排序</param>
/// <param name="bEnChangeDir">:是否可以改变曲线的方向；true改变曲线方向，false不改变曲线方向</param>
/// <param name="nFlag">:默认为0</param>
typedef E3_ERR (*e3_ResortEntChilds)(E3_ID idEnt,BOOL bYFirst,BOOL bMinToMax,BOOL bEnChangeDir,int nFlag);

/// <summary>
/// <para>API编码:[64761820]</para>
/// 接口说明:将对象里的子对象的最短路径进行排序,从第一个对象出发，以每个子对象的中心点为判断依据排序
/// <para>文档定位:数据-对象操作-对象间操作</para>
/// </summary>
/// <param name="idEnt">:对象ID</param>
/// <param name="nFlag">:默认为0</param>
typedef E3_ERR (*e3_ResortEntChilds2)(E3_ID idEnt,int nFlag);

/// <summary>
/// <para>API编码:[34850423]</para>
/// 接口说明:设置模拟输出口(DAC1~DAC4)的值；
/// <para>文档定位:硬件-资源-模拟量IO-写</para>
/// </summary>
/// <param name="idMarker">:板卡ID</param>
/// <param name="PortNum">:模拟量输出端口;取值范围1-4</param>
/// <param name="AnalogValue">:1.模拟量值对应的bit值 2.电压值0-10V对应0-65535；</param>
typedef E3_ERR (*e3_Set3DPrintAnalogOutput)(E3_ID idMarker,unsigned char PortNum,unsigned short AnalogValue);

/// <summary>
/// <para>API编码:[46931907]</para>
/// 接口说明:设置板卡上的PWM1和PWM2的值;
/// <para>文档定位:硬件-资源-模拟量IO-写</para>
/// </summary>
/// <param name="idMarker">:板卡ID</param>
/// <param name="PwmNo">:PWM端口;取值范围1-2</param>
/// <param name="Freq">:1.设置频率； 2.输出频率等于20Mhz/unFreq</param>
/// <param name="Width">:1设置脉冲宽度； 2.输出脉宽等于unPulseWidth*0.05（一个脉宽是50ns）</param>
typedef E3_ERR (*e3_Set3DPrintPWMOutput)(E3_ID idMarker,unsigned char PwmNo,unsigned int Freq,unsigned int Width);

/// <summary>
/// <para>API编码:[03311905]</para>
/// 接口说明:生成并保存九点校正文件到指定路径下
/// <para>文档定位:硬件-资源-振镜-校正</para>
/// </summary>
/// <param name="idMarker">:板卡ID</param>
/// <param name="nDaSize">:标刻标准九点图形时的DA值；与接口E3_MarkCorStdPoint中参数nRectSizeDa一致</param>
/// <param name="nMode">:确定振镜的方向；取值范围0-7； 0：[X=振镜1][Y=振镜2]; 1：[X=振镜1,反向][Y=振镜2]; 2：[X=振镜1,反向][Y=振镜2,反向]; 3：[X=振镜1][Y=振镜2,反向]; 4：[X=振镜2,反向][Y=振镜1]; 5：[X=振镜2,反向][Y=振镜1,反向]; 6：[X=振镜2][Y=振镜1,反向]; 7：[X=振镜2][Y=振镜1]; 每个取值都代表一种标准九点图形，每个图形只是方向不同，此值需要与E3_MarkCorStdPoint标刻出来的图形一致；</param>
/// <param name="ptCoor[9][2]">:1.九点实际测量值； 2.每个点坐标是到中心十字线的距离； 3.点的顺序为左上角第一个点，从左到右，从上到下；</param>
typedef E3_ERR (*e3_Set3x3PointCor)(E3_ID idMarker,int nDaSize,int nMode,double ptCoor[9][2]);

/// <summary>
/// <para>API编码:[44397002]</para>
/// 接口说明:生成并保存多点校正文件到指定路径下
/// <para>文档定位:硬件-资源-振镜-校正</para>
/// </summary>
/// <param name="idMarker">:板卡ID</param>
/// <param name="dFieldSize">:多点数据的理论区域；最外围两点中心点间距；</param>
/// <param name="row">:多点校正的列数,需要是奇数</param>
/// <param name="col">:多点校正的列数,需要是奇数</param>
/// <param name="ptCoor[][2]">:1.多点实际测量值； 2.每个点坐标到中心点的距离，数值带正负号； 3.点的顺序为左下角为第一个点，从左到右，从下到上；</param>
typedef E3_ERR (*e3_SetMultiPointCor)(E3_ID idMarker,double dFieldSize,int row,int col,double ptCoor[][2]);

/// <summary>
/// <para>API编码:[72889431]</para>
/// 接口说明:互换指定序号的两层对象顺序
/// <para>文档定位:数据-对象操作-对象间操作</para>
/// </summary>
/// <param name="idEM">:对象管理器ID</param>
/// <param name="nLayerIndex1">:要互换的第1个图层序号，取值范围从0开始</param>
/// <param name="nLayerIndex2">:要互换的第2个图层序号，取值范围从0开始</param>
/// <param name="bUndo">:预留参数,默认False</param>
/// <param name="strUndoName">:预留参数,默认 ""</param>
typedef E3_ERR (*e3_ChangeOrderLayer)(E3_ID idEM,int nLayerIndex1,int nLayerIndex2,BOOL bUndo,TCHAR* strUndoName);

/// <summary>
/// <para>API编码:[51167952]</para>
/// 接口说明:1.多张打标卡时，只能用此接口释放扩展轴； 2.单卡时，可以用此接口释放扩展轴；
/// <para>文档定位:硬件-资源-运动轴-动作</para>
/// </summary>
/// <param name="idMarker">:板卡ID</param>
typedef E3_ERR (*e3_CloseMotionMgrOfMarker)(E3_ID idMarker);

/// <summary>
/// <para>API编码:[17932665]</para>
/// 接口说明:导入stl文件
/// <para>文档定位:数据-3D操作</para>
/// </summary>
/// <param name="idEM">:对象管理器ID</param>
/// <param name="strStlFile">:stl文件完整路径</param>
/// <param name="bAddMode">:是否为追加模式;true为追加模式，false覆盖上次导入的stl文件</param>
/// <param name="bPick">:预留参数,默认false;</param>
typedef E3_ERR (*e3_CreateAddStlFile)(E3_ID idEM,TCHAR* strStlFile,BOOL bAddMode,BOOL bPick);

/// <summary>
/// <para>API编码:[16838888]</para>
/// 接口说明:创建三阶贝塞尔曲线
/// <para>文档定位:数据-标准图元-创建</para>
/// </summary>
/// <param name="idEM">:对象管理器ID</param>
/// <param name="nPen">:笔号，范围0-255</param>
/// <param name="ptLines">:1.曲线对应的点数组； 2.数组长度为4+3(n-1),n=1;</param>
/// <param name="nPointCount">:为数组ptLines的长度；</param>
/// <param name="reserved1">:预留接口.默认值:flase</param>
/// <param name="reserved2">:预留接口.默认值:flase</param>
/// <param name="reserved3">:预留接口.默认值""</param>
typedef E3_ERR (*e3_CreateBeziers)(E3_ID idEM,int nPen,Pt2d* ptLines,int nPointCount,BOOL reserved1,BOOL reserved2,TCHAR* reserved3);

/// <summary>
/// <para>API编码:[37103428]</para>
/// 接口说明:1.创建三阶贝塞尔曲线； 2.如果添加多条贝塞尔曲线，可以将参数bUpdateParentInfo设置为false，在最后一次添加的时候设置成true，这样可以避免大量创建时由于更新对象列表导致卡顿；
/// <para>文档定位:数据-标准图元-创建</para>
/// </summary>
/// <param name="idEM">:对象管理器ID</param>
/// <param name="nPen">:笔号，范围0-255</param>
/// <param name="ptLines">:1.曲线对应的点数组； 2.数组长度为4+3(n-1),n=1;</param>
/// <param name="nPointCount">:为数组ptLines的长度；</param>
/// <param name="bUpdateParentInfo">:是否更新列表信息；true为更新，false为不更新</param>
/// <param name="idNewEnt">:创建贝塞尔曲线对象ID</param>
typedef E3_ERR (*e3_CreateBeziers_2)(E3_ID idEM,int nPen,Pt2d* ptLines,int nPointCount,BOOL bUpdateParentInfo,E3_ID& idNewEnt);

/// <summary>
/// <para>API编码:[30342248]</para>
/// 接口说明:删除填充对象的填充属性；
/// <para>文档定位:数据-填充相关</para>
/// </summary>
/// <param name="idEM">:对象管理器ID</param>
/// <param name="idEnt">:对象ID</param>
/// <param name="reserved1">:预留接口，默认值false</param>
/// <param name="reserved2">:预留接口，默认值为“”</param>
typedef E3_ERR (*e3_DelEntHatchParam)(E3_ID idEM,E3_ID idEnt,BOOL reserved1,TCHAR* reserved2);

/// <summary>
/// <para>API编码:[25181608]</para>
/// 接口说明:删除填充对象的填充属性；
/// <para>文档定位:数据-填充相关</para>
/// </summary>
/// <param name="idEM">:对象管理器ID</param>
/// <param name="idEnt">:对象ID</param>
typedef E3_ERR (*e3_DelEntHatchParam_2)(E3_ID idEM,E3_ID idEnt);

/// <summary>
/// <para>API编码:[92495733]</para>
/// 接口说明:删除指定对象的所有子对象，不删除它自己;比如删除层对象中的所有对象；
/// <para>文档定位:数据-对象操作-对象间操作</para>
/// </summary>
/// <param name="idEnt">:对象ID</param>
typedef E3_ERR (*e3_DeleteAllChildOfEnt)(E3_ID idEnt);

/// <summary>
/// <para>API编码:[04369686]</para>
/// 接口说明:删除指定对象
/// <para>文档定位:数据-对象操作-对象通用读写</para>
/// </summary>
/// <param name="idEnt">:对象ID</param>
typedef E3_ERR (*e3_DeleteEnt)(E3_ID idEnt);

/// <summary>
/// <para>API编码:[11781849]</para>
/// 接口说明:删除指定序号的层对象
/// <para>文档定位:数据-对象操作-对象通用读写</para>
/// </summary>
/// <param name="idEM">:对象管理器ID</param>
/// <param name="nLayerindex">:指定层序号；取值范围从0开始</param>
/// <param name="reserved1">:预留接口，默认值false</param>
/// <param name="reserved2">:预留接口，默认值为“”</param>
typedef E3_ERR (*e3_DeleteLayer)(E3_ID idEM,int nLayerindex,BOOL reserved1,TCHAR* reserved2);

/// <summary>
/// <para>API编码:[16622624]</para>
/// 接口说明:删除指定序号的层对象
/// <para>文档定位:数据-对象操作-对象通用读写</para>
/// </summary>
/// <param name="idEM">:对象管理器ID</param>
/// <param name="nLayerindex">:指定层序号；取值范围从0开始</param>
typedef E3_ERR (*e3_DeleteLayer2)(E3_ID idEM,int nLayerindex);

/// <summary>
/// <para>API编码:[81875862]</para>
/// 接口说明:1.造型，包括焊接对象，修剪对象，交叉对象； 2.当修剪的时候，两个对象ID输入接口的顺序会影响结果；其它两种造型不会受对象顺序影响；
/// <para>文档定位:数据-对象操作-对象间操作</para>
/// </summary>
/// <param name="idEM">:对象管理器ID</param>
/// <param name="idEnt1">:对象ID1</param>
/// <param name="idEnt2">:对象ID2</param>
/// <param name="nMode">:造型模式； 1.nMode=0 焊接对象； 2.nMode=1 修剪对象； 3.nMode=2 交叉对象；</param>
/// <param name="nPen">:造型之后对象的笔号；取值范围0-255</param>
/// <param name="reserved1">:预留接口，默认值false</param>
/// <param name="reserved2">:预留接口，默认值为“”</param>
typedef E3_ERR (*e3_DistortionEntity)(E3_ID idEM,E3_ID idEnt1,E3_ID idEnt2,int nMode,int nPen,BOOL reserved1,TCHAR* reserved2);

/// <summary>
/// <para>API编码:[88335574]</para>
/// 接口说明:1.造型，包括焊接对象，修剪对象，交叉对象； 2.当修剪的时候，两个对象ID输入接口的顺序会影响结果；其它两种造型不会受对象顺序影响；
/// <para>文档定位:数据-对象操作-对象间操作</para>
/// </summary>
/// <param name="idEM">:对象管理器ID</param>
/// <param name="idEnt1">:对象ID1</param>
/// <param name="idEnt2">:对象ID2</param>
/// <param name="nMode">:造型模式； 1.nMode=0 焊接对象； 2.nMode=1 修剪对象； 3.nMode=2 交叉对象；</param>
/// <param name="nPen">:造型之后对象的笔号；取值范围0-255</param>
typedef E3_ERR (*e3_DistortionEntity_2)(E3_ID idEM,E3_ID idEnt1,E3_ID idEnt2,int nMode,int nPen);

/// <summary>
/// <para>API编码:[30210049]</para>
/// 接口说明:生成并保存多点校正文件
/// <para>文档定位:硬件-资源-振镜-校正</para>
/// </summary>
/// <param name="strOldCorFile">:旧校正文件完整路径；此校正文件为打标多点时使用的校正文件；</param>
/// <param name="strNewCorFile">:生成新的校正文件完整路径</param>
/// <param name="ptGridReal">:1.多点实际测量值； 2.每个点坐标到中心点的距离，数值带正负号； 3.点的顺序为左下角为第一个点，从左到右，从下到上；</param>
/// <param name="nCountX">:多点X方向个数</param>
/// <param name="nCountY">:多点Y方向个数</param>
/// <param name="dGridLBX">:点阵左下角X理论坐标</param>
/// <param name="dGridLBY">:点阵左下角Y理论坐标</param>
/// <param name="dGridDisX">:点阵X方向理论间距</param>
/// <param name="dGridDisY">:点阵X方向理论间距</param>
typedef BOOL (*e3_FunCF)(TCHAR* strOldCorFile,TCHAR* strNewCorFile,Pt2d* ptGridReal,int nCountX,int nCountY,double dGridLBX,double dGridLBY,double dGridDisX,double dGridDisY);

/// <summary>
/// <para>API编码:[77011660]</para>
/// 接口说明:生成并保存九点校正文件
/// <para>文档定位:硬件-资源-振镜-校正</para>
/// </summary>
/// <param name="idMarker">:板卡ID</param>
/// <param name="strNewFile">:保存九点校正文件完整路径</param>
/// <param name="nPointMode">:确定振镜的方向；取值范围0-7； 0：[X=振镜1][Y=振镜2]; 1：[X=振镜1,反向][Y=振镜2]; 2：[X=振镜1,反向][Y=振镜2,反向]; 3：[X=振镜1][Y=振镜2,反向]; 4：[X=振镜2,反向][Y=振镜1]; 5：[X=振镜2,反向][Y=振镜1,反向]; 6：[X=振镜2][Y=振镜1,反向]; 7：[X=振镜2][Y=振镜1]; 每个取值都代表一种标准九点图形，每个图形只是方向不同，此值需要与E3_MarkCorStdPoint2标刻出来的图形一致；</param>
/// <param name="dPts">:1.九点实际测量值； 2.每个点坐标是到中心十字线的距离； 3.点的顺序为左上角第一个点，从左到右，从上到下；</param>
/// <param name="dFiledSize">:1.标刻幅面大小（一般就是指场镜的理论值，比如是110的场镜，这个值就是可以填写110）； 2.与接口E3_MarkCorStdPoint2中参数dFiledSize保持一致</param>
/// <param name="dBoxSize">:1.标刻矩形尺寸（标准九点图形的尺寸，要给多大的幅面做矫正）； 2.与接口E3_MarkCorStdPoint2中参数dBoxSize保持一致</param>
typedef BOOL (*e3_FunCF9)(E3_ID idMarker,TCHAR* strNewFile,int nPointMode,Pt2d* dPts,double dFiledSize,double dBoxSize);

/// <summary>
/// <para>API编码:[40863716]</para>
/// 接口说明:获取填充参数，可以得到三组填充参数
/// <para>文档定位:数据-填充相关</para>
/// </summary>
/// <param name="idEnt">:对象ID</param>
/// <param name="bEnableContour">:是否使能轮廓;true使能，false不使能</param>
/// <param name="bContourFirst">:是否使能轮廓优先;true使能，false不使能；</param>
/// <param name="param1">:填充参数1</param>
/// <param name="param2">:填充参数2</param>
/// <param name="param3">:填充参数3</param>
typedef E3_ERR (*e3_GetHatchParam)(E3_ID idEnt,BOOL& bEnableContour,BOOL& bContourFirst,HatchParam& param1,HatchParam& param2,HatchParam& param3);

/// <summary>
/// <para>API编码:[26453245]</para>
/// 接口说明:获取填充参数，最多可以得到八组填充参数
/// <para>文档定位:数据-填充相关</para>
/// </summary>
/// <param name="idEnt">:对象ID</param>
/// <param name="bEnableContour">:是否使能轮廓;true使能，false不使能</param>
/// <param name="bContourFirst">:是否使能轮廓优先;true使能，false不使能；</param>
/// <param name="nHatchParamCount">:得到填充参数的组数</param>
/// <param name="pParam">:填充参数；可以传入填充参数数组的第一个元素</param>
typedef E3_ERR (*e3_GetHatchParam2)(E3_ID idEnt,BOOL& bEnableContour,BOOL& bContourFirst,int& nHatchParamCount,HatchParam* pParam);

/// <summary>
/// <para>API编码:[04351611]</para>
/// 接口说明:得到指定路径下stl模型的尺寸
/// <para>文档定位:数据-3D操作</para>
/// </summary>
/// <param name="idEM">:对象管理器ID</param>
/// <param name="strStlFile">:stl文件完整路径</param>
/// <param name="minx">:stl模型的最小X坐标;</param>
/// <param name="miny">:stl模型的最小Y坐标;</param>
/// <param name="maxx">:stl模型的最大X坐标;</param>
/// <param name="maxy">:stl模型的最大Y坐标;</param>
/// <param name="minz">:stl模型的最小Z坐标;</param>
/// <param name="maxz">:stl模型的最大Z坐标;</param>
typedef E3_ERR (*e3_GetStlFileSize)(E3_ID idEM,TCHAR* strStlFile,double& minx,double& miny,double& maxx,double& maxy,double& minz,double& maxz);

/// <summary>
/// <para>API编码:[45830240]</para>
/// 接口说明:1.填充指定对象; 2.当被填充的对象为非填充对象时，只能用此接口； 3.当被填充的对象时填充对象，可以用此接口，也可以用E3_SetHatchParam或者E3_SetHatchParam2修改填充参数 4.非填充对象填充之后，对象ID会发生变化
/// <para>文档定位:数据-填充相关</para>
/// </summary>
/// <param name="idEnt">:对象ID</param>
/// <param name="bEnableContour">:是否使能轮廓;true使能，false不使能</param>
/// <param name="bContourFirst">:是否使能轮廓优先;true使能，false不使能；</param>
/// <param name="param1">:填充参数1</param>
/// <param name="param2">:填充参数2</param>
/// <param name="param3">:得到填充参数3</param>
typedef E3_ERR (*e3_HatchEnt)(E3_ID idEnt,int bEnableContour,int bContourFirst,HatchParam param1,HatchParam param2,HatchParam param3);

/// <summary>
/// <para>API编码:[76283542]</para>
/// 接口说明:1.填充指定对象，最多八组填充参数； 2.当被填充的对象为非填充对象时，只能用此接口； 3.当被填充的对象时填充对象，可以用此接口，也可以用E3_SetHatchParam或者E3_SetHatchParam2修改填充参数
/// <para>文档定位:数据-填充相关</para>
/// </summary>
/// <param name="idEnt">:对象ID</param>
/// <param name="bEnableContour">:是否使能轮廓;true使能，false不使能</param>
/// <param name="bContourFirst">:是否使能轮廓优先;true使能，false不使能；</param>
/// <param name="nHatchParamCount">:填充参数数组paramList长度；范围1-8</param>
/// <param name="pParam">:填充参数数组</param>
/// <param name="idEntHatch">:填充之后的对象ID</param>
typedef E3_ERR (*e3_HatchEnt2)(E3_ID idEnt,BOOL bEnableContour,BOOL bContourFirst,int nHatchParamCount,HatchParam* pParam,E3_ID& idEntHatch);

/// <summary>
/// <para>API编码:[48449352]</para>
/// 接口说明:背景填充，用对象idEntBack当背景填充对象idEnt
/// <para>文档定位:数据-填充相关</para>
/// </summary>
/// <param name="idEnt">:对象ID</param>
/// <param name="idEntBack">:背景对象ID</param>
/// <param name="bEnableContour">:是否使能轮廓;true使能，false不使能</param>
/// <param name="bContourFirst">:是否使能轮廓优先;true使能，false不使能；</param>
/// <param name="bDeleteOldEnt">:是否删除</param>
/// <param name="idNewEnt">:填充后得到的填充对象的ID</param>
typedef E3_ERR (*e3_HatchEntByBack)(E3_ID idEnt,E3_ID idEntBack,BOOL bEnableContour,BOOL bContourFirst,BOOL bDeleteOldEnt,E3_ID& idNewEnt);

/// <summary>
/// <para>API编码:[45079026]</para>
/// 接口说明:1.多张打标卡时，只能用此接口初始化扩展轴； 2.单卡时，可以用此接口初始化扩展轴；
/// <para>文档定位:硬件-资源-运动轴-动作</para>
/// </summary>
/// <param name="idMarker">:板卡ID</param>
/// <param name="nIndexOfParamFile">:配置文件对应的序号； 从0开始，nIndexOfParamFile=0使用参数文件Motors.ini; nIndexOfParamFile=1使用Motors1.ini; nIndexOfParamFile=2使用Motors2.ini；以此类推；</param>
typedef E3_ERR (*e3_InitMotorMgrOfMarker)(E3_ID idMarker,int nIndexOfParamFile);

/// <summary>
/// <para>API编码:[43163621]</para>
/// 接口说明:判断指定序号的扩展轴是否有故障
/// <para>文档定位:硬件-资源-运动轴-查询</para>
/// </summary>
/// <param name="idMarker">:板卡ID</param>
/// <param name="axis">:扩展轴序号;取值范围0-5</param>
/// <param name="bIsFault">:序号对应的扩展轴是否有故障；true表示存在故障,false不存在故障</param>
typedef E3_ERR (*e3_IsAxisHaveFault)(E3_ID idMarker,int axis,BOOL& bIsFault);

/// <summary>
/// <para>API编码:[18270977]</para>
/// 接口说明:判断指定序号的扩展轴是否使能零点，是否已经回过零
/// <para>文档定位:硬件-资源-运动轴-查询</para>
/// </summary>
/// <param name="idMarker">:板卡ID</param>
/// <param name="axis">:扩展轴序号;取值范围0-5</param>
/// <param name="bIsHaveHome">:扩展轴是否使能零点;true使能了零点，false未使能零点</param>
/// <param name="bIsAlreadyFindHome">:扩展轴是否已经回过零;true扩展轴已经回过零，false扩展轴未回过零；</param>
typedef E3_ERR (*e3_IsAxisHaveHome)(E3_ID idMarker,int axis,BOOL& bIsHaveHome,BOOL& bIsAlreadyFindHome);

/// <summary>
/// <para>API编码:[75546172]</para>
/// 接口说明:判断指定序号的扩展轴是否正在运动
/// <para>文档定位:硬件-资源-振镜-状态查询</para>
/// </summary>
/// <param name="idMarker">:板卡ID</param>
/// <param name="axis">:扩展轴序号;取值范围0-5</param>
/// <param name="bIsMoving">:扩展轴是否正在运动；true扩展轴正在运动，false扩展轴为静止</param>
typedef E3_ERR (*e3_IsAxisMoving)(E3_ID idMarker,int axis,BOOL& bIsMoving);

/// <summary>
/// <para>API编码:[84116983]</para>
/// 接口说明:1.标刻九点校正标准图形（田字格图形）； 2.使用默认参数标刻，不受是否使能校正加载校正文件，是否修改振镜镜像等影响；
/// <para>文档定位:硬件-资源-振镜-校正</para>
/// </summary>
/// <param name="idMarker">:板卡ID</param>
/// <param name="dFieldSize">:标刻幅面大小（标刻幅面大小一般就是指场镜的理论值，比如是110的场镜，这个值就是可以填写110）,单位毫米;</param>
/// <param name="dBoxSize">:标刻矩形尺寸（要给多大的幅面做矫正）,单位毫米;</param>
typedef E3_ERR (*e3_MarkCorStdPoint2)(E3_ID idMarker,double dFieldSize,double dBoxSize);

/// <summary>
/// <para>API编码:[24343039]</para>
/// 接口说明:1.选择打标使用的校正表序号； 2.校正表序号需要用接口E3_MarkerSetCorFile2进行设置；
/// <para>文档定位:硬件-资源-振镜-校正</para>
/// </summary>
/// <param name="idMarker">:板卡ID</param>
/// <param name="indexTable">:校正表号;取值范围1-4</param>
/// <param name="bEnableCor">:是否使用校正； 默认true</param>
typedef E3_ERR (*e3_MarkerSelectCorTable)(E3_ID idMarker,int indexTable,BOOL bEnableCor);

/// <summary>
/// <para>API编码:[58887993]</para>
/// 接口说明:镜像指定对象
/// <para>文档定位:数据-对象操作-对象通用读写</para>
/// </summary>
/// <param name="idEnt">:对象ID</param>
/// <param name="dCenx">:镜像中心X坐标</param>
/// <param name="dCeny">:镜像中心Y坐标</param>
/// <param name="bMirrorX">:是否X方向镜像;true镜像，false不镜像</param>
/// <param name="bMirrorY">:是否Y方向镜像;true镜像，false不镜像；</param>
typedef E3_ERR (*e3_MirrorEnt)(E3_ID idEnt,double dCenx,double dCeny,BOOL bMirrorX,BOOL bMirrorY);

/// <summary>
/// <para>API编码:[18149409]</para>
/// 接口说明:移动指定对象到指定序号，用于调整对象在对象列表中的顺序
/// <para>文档定位:数据-对象操作-对象间操作</para>
/// </summary>
/// <param name="idEM">:对象管理器ID</param>
/// <param name="idEnt">:对象ID</param>
/// <param name="nIndex">:对象列表中的序号;取值范围从0开始；</param>
typedef E3_ERR (*e3_MoveEntToIndex)(E3_ID idEM,E3_ID idEnt,int nIndex);

/// <summary>
/// <para>API编码:[27419263]</para>
/// 接口说明:指定对象Z方向移动指定距离
/// <para>文档定位:数据-对象操作-对象通用读写</para>
/// </summary>
/// <param name="idEnt">:对象ID</param>
/// <param name="dMoveZ">:Z方向移动的距离</param>
typedef E3_ERR (*e3_MoveEntZ)(E3_ID idEnt,double dMoveZ);

/// <summary>
/// <para>API编码:[12175561]</para>
/// 接口说明:1.旋转和移动指定对象； 2.指定对象先绕指定中心旋转,然后移动指定距离
/// <para>文档定位:数据-对象操作-对象通用读写</para>
/// </summary>
/// <param name="idEnt">:对象ID</param>
/// <param name="dMoveX">:X方向移动距离</param>
/// <param name="dMoveY">:Y方向移动距离</param>
/// <param name="dCenterX">:旋转中心x坐标</param>
/// <param name="dCenterY">:旋转中心y坐标</param>
/// <param name="dRotateAng">:1.旋转角度（弧度值）; 2.正值为逆时针旋转，负值为顺时针;</param>
typedef E3_ERR (*e3_MoveRotateEnt)(E3_ID idEnt,double dMoveX,double dMoveY,double dCenterX,double dCenterY,double dRotateAng);

/// <summary>
/// <para>API编码:[31129690]</para>
/// 接口说明:1.对指定对象进行投影，包裹等； 2.圆柱包裹，球面包裹不需要stl文件，其它动作需要先加载stl文件
/// <para>文档定位:数据-3D操作</para>
/// </summary>
/// <param name="idEM">:对象管理器ID</param>
/// <param name="idEnt">:对象ID</param>
/// <param name="nProjectMode">:投影模式:    0：投影模式;    1：包裹;    2：圆柱包裹;    3：球面包裹;    4：旋转体包裹;    5：包裹XY;</param>
/// <param name="bDownProject">:是否为下曲面投影</param>
/// <param name="dLimetZ">:Z极限值；小于Z极限值的部分将不进行投影</param>
/// <param name="dDefaultZ">:默认Z值</param>
/// <param name="bRemoveNoInter">:是否移除未相交线段；true移除，false保留</param>
/// <param name="bCylinderX">:当模式选0包裹时，true为X方向包裹，否则为Y方向包裹</param>
/// <param name="dCylinderDiameter">:圆柱包裹，球面包裹时的直径</param>
typedef E3_ERR (*e3_ProjectEnt_2)(E3_ID idEM,E3_ID idEnt,int nProjectMode,BOOL bDownProject,double dLimetZ,double dDefaultZ,BOOL bRemoveNoInter,BOOL bCylinderX,double dCylinderDiameter);

/// <summary>
/// <para>API编码:[51171353]</para>
/// 接口说明:保存Ez3文件
/// <para>文档定位:数据-文件读写</para>
/// </summary>
/// <param name="pStrFileName">:ez3文件完整路径</param>
/// <param name="idEM">:对象管理器ID</param>
/// <param name="bSelect">:是否仅保存当前选中内容;true保存当前选中内容, false保存全部内容</param>
/// <param name="bPreImage">:是否保存预览图.true保存预览图,false不保存预览图</param>
/// <param name="strAuthor">:作者信息.默认为空("");</param>
/// <param name="strTime">:时间信息.默认为空("");</param>
/// <param name="strNotes">:备注信息.默认为空("");</param>
typedef E3_ERR (*e3_SaveEntMgrToFile)(TCHAR* pStrFileName,E3_ID idEM,BOOL bSelect,BOOL bPreImage,TCHAR* strAuthor,TCHAR* strTime,TCHAR* strNotes);

/// <summary>
/// <para>API编码:[81432735]</para>
/// 接口说明:保存扩展轴参数到指定配置文件中;配置文件参考E3_InitMotorMgrOfMarker中的nIndexOfMotorFile
/// <para>文档定位:硬件-资源-运动轴-配置</para>
/// </summary>
/// <param name="idMarker">:板卡ID</param>
typedef E3_ERR (*e3_SaveMotionMgrParamToFile)(E3_ID idMarker);

/// <summary>
/// <para>API编码:[20852974]</para>
/// 接口说明:1.修改填充参数； 2.当对象为填充对象时，使用此接口修改填充参数；
/// <para>文档定位:数据-填充相关</para>
/// </summary>
/// <param name="idEM">:对象管理器ID</param>
/// <param name="idEnt">:对象ID</param>
/// <param name="bEnableContour">:是否使能轮廓;true使能，false不使能</param>
/// <param name="bContourFirst">:是否使能轮廓优先;true使能，false不使能；</param>
/// <param name="param1">:填充参数1</param>
/// <param name="param2">:填充参数2</param>
/// <param name="param3">:填充参数3</param>
typedef E3_ERR (*e3_SetHatchParam)(E3_ID idEM,E3_ID idEnt,BOOL bEnableContour,BOOL bContourFirst,HatchParam param1,HatchParam param2,HatchParam param3);

/// <summary>
/// <para>API编码:[23608755]</para>
/// 接口说明:1.修改填充参数，最多可以设置八组填充参数； 2.当对象为填充对象时，使用此接口修改填充参数；
/// <para>文档定位:数据-填充相关</para>
/// </summary>
/// <param name="idEM">:对象管理器ID</param>
/// <param name="idEnt">:对象ID</param>
/// <param name="bEnableContour">:是否使能轮廓;true使能，false不使能</param>
/// <param name="bContourFirst">:是否使能轮廓优先;true使能，false不使能；</param>
/// <param name="nHatchParamCount">:填充参数数组paramList长度；范围1-8</param>
/// <param name="pParam">:填充参数数组</param>
typedef E3_ERR (*e3_SetHatchParam2)(E3_ID idEM,E3_ID idEnt,BOOL bEnableContour,BOOL bContourFirst,int nHatchParamCount,HatchParam* pParam);

/// <summary>
/// <para>API编码:[70124665]</para>
/// 接口说明:1.设置是否多头同步和同步使用的输入输出口； 2.需要有硬件支持；
/// <para>文档定位:环境-控制卡-配置</para>
/// </summary>
/// <param name="b">:是否使能同步功能;true使能同步功能，不使能同步功能</param>
/// <param name="nInportIndex">:输入口端口</param>
/// <param name="nOutportIndex">:输出口端口</param>
typedef E3_ERR (*e3_SetMultiCardSyn)(BOOL b,int nInportIndex,int nOutportIndex);

/// <summary>
/// <para>API编码:[06519769]</para>
/// 接口说明:设置是否按照曲线同步
/// <para>文档定位:环境-控制卡-配置</para>
/// </summary>
/// <param name="b">:是否按照曲线同步；true 按曲线同步，false按照对象同步</param>
typedef E3_ERR (*e3_SetMultiCardSynEveryCurve)(BOOL b);

/// <summary>
/// <para>API编码:[21675899]</para>
/// 接口说明:设置是否同步完成
/// <para>文档定位:环境-控制卡-配置</para>
/// </summary>
/// <param name="b">:是否同步完成；true同步完成，false不用同步完成</param>
typedef E3_ERR (*e3_SetMultiCardSynWhenFinish)(BOOL b);

/// <summary>
/// <para>API编码:[84332886]</para>
/// 接口说明:将指定路径的stl文件进行切片到指定图层中
/// <para>文档定位:数据-3D操作</para>
/// </summary>
/// <param name="idLayer">:图层ID</param>
/// <param name="strStlFile">:stl文件完整路径</param>
/// <param name="strName">:切片后对象名称前缀</param>
/// <param name="bZUpToDown">:按照从上到下的顺序切片;true从上到下进行切片，false从下到上进行切片;影响切片之后对象顺序;</param>
/// <param name="dMinZ">:切片范围最小Z坐标</param>
/// <param name="dMaxZ">:切片范围最大Z坐标</param>
/// <param name="dThickness">:切片层厚</param>
typedef E3_ERR (*e3_SliceStlFile)(E3_ID idLayer,TCHAR* strStlFile,TCHAR* strName,BOOL bZUpToDown,double dMinZ,double dMaxZ,double dThickness);

/// <summary>
/// <para>API编码:[81150769]</para>
/// 接口说明:将指定路径的stl文件进行切片到指定图层中，并将切片之后的对象进行移动
/// <para>文档定位:数据-3D操作</para>
/// </summary>
/// <param name="idLayer">:图层ID</param>
/// <param name="strStlFile">:stl文件完整路径</param>
/// <param name="strName">:切片后对象名称前缀</param>
/// <param name="bZUpToDown">:按照从上到下的顺序切片;true从上到下进行切片，false从下到上进行切片;影响切片之后对象顺序;</param>
/// <param name="dMinZ">:切片范围最小Z坐标</param>
/// <param name="dMaxZ">:切片范围最大Z坐标</param>
/// <param name="dThickness">:切片层厚</param>
/// <param name="dStlOffsetX">:X方向偏移量</param>
/// <param name="dStlOffsetY">:Y方向偏移量</param>
/// <param name="dStlOffsetZ">:Z方向偏移量</param>
/// <param name="nFlag">:默认0</param>
typedef E3_ERR (*e3_SliceStlFile2)(E3_ID idLayer,TCHAR* strStlFile,TCHAR* strName,BOOL bZUpToDown,double dMinZ,double dMaxZ,double dThickness,double dStlOffsetX,double dStlOffsetY,double dStlOffsetZ,int nFlag);

/// <summary>
/// <para>API编码:[35744039]</para>
/// 接口说明:得到当前层中对象的个数和所有对象的总的最小最大坐标
/// <para>文档定位:数据-对象操作-对象通用读写</para>
/// </summary>
/// <param name="idEM">:对象管理器ID</param>
/// <param name="nEntCount">:当前层中对象的个数</param>
/// <param name="minx">:最小X坐标</param>
/// <param name="miny">:最小X坐标</param>
/// <param name="maxx">:最大X坐标</param>
/// <param name="maxy">:最大Y坐标</param>
typedef E3_ERR (*e3_GetAllEntCount)(E3_ID idEM,int& nEntCount,double& minx,double& miny,double& maxx,double& maxy);

/// <summary>
/// <para>API编码:[15349028]</para>
/// 接口说明:将指定序号层设置为当前层
/// <para>文档定位:数据-对象操作-对象通用读写</para>
/// </summary>
/// <param name="idEM">:对象管理器ID</param>
/// <param name="nLayerIndex">:层序号</param>
typedef E3_ERR (*e3_SetCurLayer)(E3_ID idEM,int nLayerIndex);

/// <summary>
/// <para>API编码:[08420886]</para>
/// 接口说明:设置文本信息，比如字体，对齐方式，坐标，字符高度间距等
/// <para>文档定位:数据-标准图元-编辑-文本类型-文本</para>
/// </summary>
/// <param name="idEM">:对象管理器ID</param>
/// <param name="idEnt">:文本对象ID</param>
/// <param name="nMaxParamN">:整型数组最大长度，默认24</param>
/// <param name="nParam">:整型数组，包括字体序号，字符间距类型等</param>
/// <param name="nMaxParamD">:浮点型数组最大长度，默认16</param>
/// <param name="dParam">:浮点型数组，包括XY坐标，字符高度宽度等；</param>
/// <param name="strText">:文本对象内容，长度为4098</param>
/// <param name="strExtFile">:文本内容打标之后保存到txt中，txt文件的完整路径，长度255</param>
/// <param name="reserved1">:预留接口</param>
/// <param name="reserved2">:预留接口</param>
typedef E3_ERR (*e3_SetEntTextInfo)(E3_ID idEM,E3_ID idEnt,int nMaxParamN,int* nParam,int nMaxParamD,double* dParam,TCHAR* strText,TCHAR* strExtFile,BOOL reserved1,TCHAR* reserved2);

/// <summary>
/// <para>API编码:[67169458]</para>
/// 接口说明:设置文本信息，比如字体，对齐方式，坐标，字符高度间距等
/// <para>文档定位:数据-标准图元-编辑-文本类型-文本</para>
/// </summary>
/// <param name="idEM">:对象管理器ID</param>
/// <param name="idEnt">:文本对象ID</param>
/// <param name="nMaxParamN">:整型数组最大长度，默认24</param>
/// <param name="nParam">:整型数组，包括字体序号，字符间距类型等</param>
/// <param name="nMaxParamD">:浮点型数组最大长度，默认16</param>
/// <param name="dParam">:浮点型数组，包括XY坐标，字符高度宽度等；</param>
/// <param name="strText">:文本对象内容，长度为4098</param>
/// <param name="strExtFile">:文本内容打标之后保存到txt中，txt文件的完整路径，长度255</param>
typedef E3_ERR (*e3_SetEntTextInfo_2)(E3_ID idEM,E3_ID idEnt,int nMaxParamN,int* nParam,int nMaxParamD,double* dParam,TCHAR* strText,TCHAR* strExtFile);

/// <summary>
/// <para>API编码:[98721922]</para>
/// 接口说明:设置对象笔号
/// <para>文档定位:数据-笔参数相关</para>
/// </summary>
/// <param name="idEnt">:对象ID</param>
/// <param name="nPen">:笔号，取值范围0-255</param>
typedef E3_ERR (*e3_SetEntPen)(E3_ID idEnt,int nPen);

/// <summary>
/// <para>API编码:[73288904]</para>
/// 接口说明:设置对象以及子对象笔号
/// <para>文档定位:数据-笔参数相关</para>
/// </summary>
/// <param name="idEnt">:对象ID</param>
/// <param name="nPen">:笔号，取值范围0-255</param>
/// <param name="nFlag">:是否对子对象生效，0x01 对子对象生效</param>
typedef E3_ERR (*e3_SetEntPen2)(E3_ID idEnt,int nPen,int nFlag);

/// <summary>
/// <para>API编码:[79548685]</para>
/// 接口说明:设置对象Z值
/// <para>文档定位:数据-对象操作-对象通用读写</para>
/// </summary>
/// <param name="idEnt">:对象ID</param>
/// <param name="z">:对象设置的Z值</param>
/// <param name="bChangeAllChildZ">:是否对子对象的Z值属性进行修改；true为修改，false为不修改；</param>
typedef E3_ERR (*e3_SetEntityZ)(E3_ID idEnt,double z,BOOL bChangeAllChildZ);

/// <summary>
/// <para>API编码:[06024193]</para>
/// 接口说明:设置对象A值
/// <para>文档定位:数据-对象操作-对象通用读写</para>
/// </summary>
/// <param name="idEnt">:对象ID</param>
/// <param name="a">:对象设置的A值</param>
/// <param name="bChangeAllChildA">:是否对子对象的A值属性进行修改；true为修改，false为不修改；</param>
typedef E3_ERR (*e3_SetEntityA)(E3_ID idEnt,double a,BOOL  bChangeAllChildA);

/// <summary>
/// <para>API编码:[06055636]</para>
/// 接口说明:设置对象名称,包括层名称
/// <para>文档定位:数据-对象操作-对象通用读写</para>
/// </summary>
/// <param name="idEnt">:对象ID</param>
/// <param name="szEntName">:对象名称，长度99</param>
typedef E3_ERR (*e3_SetEntityName)(E3_ID idEnt,TCHAR* szEntName);

/// <summary>
/// <para>API编码:[84855759]</para>
/// 接口说明:得到板卡的当前状态
/// <para>文档定位:环境-控制卡-操作</para>
/// </summary>
/// <param name="idMarker">:板卡ID</param>
/// <param name="data">:板卡的状态,取值 0Ready， 1Run， 2Pause， 3Error</param>
typedef E3_ERR (*e3_MarkerGetState)(E3_ID idMarker,WORD& data);

/// <summary>
/// <para>API编码:[40200356]</para>
/// 接口说明:获取校正文件校正范围，与F3参数中的区域尺寸一致
/// <para>文档定位:数据-对象操作-对象通用读写</para>
/// </summary>
/// <param name="idMarker">:板卡ID</param>
/// <param name="x">:X方向范围</param>
/// <param name="y">:Y方向范围</param>
typedef E3_ERR (*e3_MarkerGetRange)(E3_ID idMarker,double& x,double& y);

/// <summary>
/// <para>API编码:[28744430]</para>
/// 接口说明:得到控制卡加工数量寄存器数据，与接口E3_MarkerChangeMarkCountToList搭配使用
/// <para>文档定位:数据-对象操作-对象通用读写</para>
/// </summary>
/// <param name="idMarker">:板卡ID</param>
/// <param name="n">:计数数值</param>
typedef E3_ERR (*e3_MarkerGetMarkCount)(E3_ID idMarker,int& n);

/// <summary>
/// <para>API编码:[45436009]</para>
/// 接口说明:得到板卡中硬件信息
/// <para>文档定位:环境-控制卡-操作</para>
/// </summary>
/// <param name="idMarker">:板卡ID</param>
/// <param name="szType[256]">:板卡类型</param>
/// <param name="szVersion[256]">:板卡版本号</param>
/// <param name="szFunInfo[256]">:功能代码</param>
/// <param name="szID[256]">:激光接口卡版本</param>
typedef E3_ERR (*e3_MarkerGetHardInfo)(E3_ID idMarker,TCHAR szType[256],TCHAR szVersion[256],TCHAR szFunInfo[256],TCHAR szID[256]);

/// <summary>
/// <para>API编码:[75890477]</para>
/// 接口说明:1.得到加工预估时间； 2.先将标刻类型选为计算模式0x01000000,调用E3_MarkerMarkEnt2
/// <para>文档定位:硬件-组合动作-动作指令</para>
/// </summary>
/// <param name="idMarker">:板卡ID</param>
/// <param name="nTimeMs">:得到的预估时间，单位ms</param>
typedef E3_ERR (*e3_MarkerGetCalcMarkTime)(E3_ID idMarker,int& nTimeMs);

/// <summary>
/// <para>API编码:[33789418]</para>
/// 接口说明:得到文本信息，比如字体，对齐方式，坐标，字符高度间距等
/// <para>文档定位:数据-标准图元-编辑-文本类型-文本</para>
/// </summary>
/// <param name="idEnt">:对象ID</param>
/// <param name="nMaxParamN">:整型数组最大长度，默认24</param>
/// <param name="nParam">:整型数组，包括字体序号，字符间距类型等</param>
/// <param name="nMaxParamD">:浮点型数组最大长度，默认16</param>
/// <param name="dParam">:浮点型数组，包括XY坐标，字符高度宽度等；</param>
typedef E3_ERR (*e3_GetTextInfo)(E3_ID idEnt,int nMaxParamN,int* nParam,int nMaxParamD,double* dParam);

/// <summary>
/// <para>API编码:[29286958]</para>
/// 接口说明:获取文本对象中的内容
/// <para>文档定位:数据-标准图元-编辑-文本类型-文本</para>
/// </summary>
/// <param name="idEnt">:对象ID</param>
/// <param name="index">:保留参数，默认0</param>
/// <param name="nMaxCharLen">:文本对象内容最大长度，默认4098</param>
/// <param name="pStr">:文本对象内容</param>
typedef E3_ERR (*e3_GetTextStringInfo)(E3_ID idEnt,int index,int nMaxCharLen,TCHAR* pStr);

/// <summary>
/// <para>API编码:[37711635]</para>
/// 接口说明:1.获取板卡SN； 2.SN是通过拨码或者程序写到板卡中的，从0开始
/// <para>文档定位:环境-控制卡-操作</para>
/// </summary>
/// <param name="idMarker">:板卡ID</param>
/// <param name="sn">:板卡SN</param>
typedef E3_ERR (*e3_GetMarkerSN)(E3_ID idMarker,int& sn);

/// <summary>
/// <para>API编码:[00452547]</para>
/// 接口说明:得到指定对象外包盒的最小最大坐标和对象是否为空
/// <para>文档定位:数据-对象操作-对象通用读写</para>
/// </summary>
/// <param name="idEnt">:对象ID</param>
/// <param name="pageMinx">:外包盒的最小X坐标</param>
/// <param name="pageMiny">:外包盒的最小Y坐标</param>
/// <param name="pageMaxx">:外包盒的最大X坐标</param>
/// <param name="pageMaxy">:外包盒的最大Y坐标</param>
/// <param name="bIsEmpty">:内容是否为空;true内容为空,false内容不为空</param>
typedef E3_ERR (*e3_GetEntityRange)(E3_ID idEnt,double& pageMinx,double& pageMiny,double& pageMaxx,double& pageMaxy,BOOL& bIsEmpty);

/// <summary>
/// <para>API编码:[27501726]</para>
/// 接口说明:得到指定对象名称
/// <para>文档定位:数据-对象操作-对象通用读写</para>
/// </summary>
/// <param name="idEnt">:对象ID</param>
/// <param name="szEntName[256]">:对象名称</param>
typedef E3_ERR (*e3_GetEntityName)(E3_ID idEnt,TCHAR szEntName[256]);

/// <summary>
/// <para>API编码:[37497213]</para>
/// 接口说明:得到指定层中对象个数
/// <para>文档定位:数据-对象操作-对象通用读写</para>
/// </summary>
/// <param name="idLayer">:图层ID</param>
/// <param name="nCount">:对象个数</param>
typedef E3_ERR (*e3_GetEntCountInLayer)(E3_ID idLayer,int& nCount);

/// <summary>
/// <para>API编码:[67096585]</para>
/// 接口说明:得到指定对象中子对象的个数，比如群组中子对象个数或者层对象中对象个数
/// <para>文档定位:数据-对象操作-对象通用读写</para>
/// </summary>
/// <param name="idEnt">:对象ID</param>
/// <param name="n">:子对象个数</param>
typedef E3_ERR (*e3_GetEntChildCount)(E3_ID idEnt,int& n);

/// <summary>
/// <para>API编码:[72200004]</para>
/// 接口说明:得到指定对象的基本信息，包括对象类型，对象笔号，对象名称，对象尺寸
/// <para>文档定位:数据-对象操作-对象通用读写</para>
/// </summary>
/// <param name="idEnt">:对象ID</param>
/// <param name="type">:对象类型</param>
/// <param name="nPen">:笔号；取值范围0-255</param>
/// <param name="strName[256]">:对象名称</param>
/// <param name="box">:外包盒尺寸</param>
/// <param name="z">:Z坐标</param>
/// <param name="a">:A坐标</param>
typedef E3_ERR (*e3_GetEntBaseInfo)(E3_ID idEnt,int& type,int& nPen,TCHAR strName[256],Box2d& box,double& z,double& a);

/// <summary>
/// <para>API编码:[00148051]</para>
/// 接口说明:将指定对象中线段按照精度要求进行连接
/// <para>文档定位:数据-对象操作-对象通用读写</para>
/// </summary>
/// <param name="idEnt">:对象ID</param>
/// <param name="err">:当两条线首首或者首尾或者尾首或者尾尾距离小于等于设定值值，进行连接</param>
/// <param name="nConnectFlag">:连接方式；  0x01 首首相连  0x02首尾相连  0x04尾首相连  0x08尾尾相连</param>
typedef E3_ERR (*e3_AutoConnectChildCurve)(E3_ID idEnt,double err,int nConnectFlag);

/// <summary>
/// <para>API编码:[18601890]</para>
/// 接口说明:将指定对象中相交的线段按照精度去交叉点
/// <para>文档定位:数据-对象操作-对象通用读写</para>
/// </summary>
/// <param name="idEnt">:对象ID</param>
/// <param name="dCrossLen">:相交线段去掉的线段长度</param>
/// <param name="idNewEntGroup">:去掉交叉点之后新的对象ID,需要用接口E3_AddEntityToChild添加到指定层中</param>
typedef E3_ERR (*e3_AutoBreakCrossEntChilds)(E3_ID idEnt,double dCrossLen,E3_ID& idNewEntGroup);

/// <summary>
/// <para>API编码:[53160759]</para>
/// 接口说明:将指定对象添加到其它对象的前后
/// <para>文档定位:数据-对象操作-对象间操作</para>
/// </summary>
/// <param name="idEM">:对象管理器ID</param>
/// <param name="idEntNew">:新的对象ID，比如E3_CopyEntity得到的复制对象</param>
/// <param name="idEntOther">:另一个对象的ID,指已经存在的对象</param>
/// <param name="bBeforeOther">:是否添加到另一个对象在对象列表中的前面；true表示idEnt添加到idEntOther前,false表示idEnt添加到idEntOther后；</param>
typedef E3_ERR (*e3_AddEntityToOther)(E3_ID idEM,E3_ID idEntNew,E3_ID idEntOther,BOOL bBeforeOther);

/// <summary>
/// <para>API编码:[61149045]</para>
/// 接口说明:将新对象添加到父对象中
/// <para>文档定位:数据-对象操作-对象间操作</para>
/// </summary>
/// <param name="idEM">:对象管理器ID</param>
/// <param name="idEntNew">:新的对象ID，比如E3_CopyEntity得到的复制对象</param>
/// <param name="idEntNewParent">:父对象ID,比如层对象</param>
/// <param name="bToHead">:是否添加到父对象的第一个；true添加到父对象第一个，false添加到父对象最后一个</param>
typedef E3_ERR (*e3_AddEntityToChild)(E3_ID idEM,E3_ID idEntNew,E3_ID idEntNewParent,BOOL bToHead);

/// <summary>
/// <para>API编码:[46481962]</para>
/// 接口说明:标刻多点十字线阵列或者圆阵列
/// <para>文档定位:硬件-资源-振镜-校正</para>
/// </summary>
/// <param name="idMarker">:板卡ID</param>
/// <param name="nPtnum">:多点数目,ptBuf的长度</param>
/// <param name="ptBuf">:多点中心坐标</param>
/// <param name="dLen">:十字线的长度或者圆直径</param>
/// <param name="bMarkCenter">:是否标刻中心标志符;true会标刻X,false不标刻；</param>
/// <param name="bCircleMode">:是否为圆模式；true标刻填充圆，false标刻十字线</param>
typedef E3_ERR (*e3_MarkCrossLines)(E3_ID idMarker,int nPtnum,Pt2d* ptBuf,double dLen,BOOL bMarkCenter,BOOL bCircleMode);

/// <summary>
/// <para>API编码:[36455892]</para>
/// 接口说明:1.释放指定对象所占的内存； 2.比如E3_CopyEntity之后，并没有将拷贝的新对象添加到层里，这时候需要释放对象内存，否则软件所占内存会增加
/// <para>文档定位:数据-对象操作-对象ID关系</para>
/// </summary>
/// <param name="idEnt">:对象ID</param>
typedef E3_ERR (*e3_FreeEntity)(E3_ID idEnt);

/// <summary>
/// <para>API编码:[83289762]</para>
/// 接口说明:添加3D曲线对象
/// <para>文档定位:数据-标准图元-创建</para>
/// </summary>
/// <param name="idEM">:管理器ID</param>
/// <param name="nPen">:添加曲线所用笔号[0,255]</param>
/// <param name="ptLines">:添加的3D曲线点集数组</param>
/// <param name="nPointCount">:添加的3D曲线的实际点数量</param>
/// <param name="bUpdateParentInfo">:是否更新列表</param>
/// <param name="idEnt">:新创建对象的id</param>
typedef E3_ERR (*e3_CreateLines3d_2)(E3_ID idEM,int nPen,Pt3d* ptLines,int nPointCount,BOOL bUpdateParentInfo,E3_ID& idEnt);

/// <summary>
/// <para>API编码:[31035919]</para>
/// 接口说明:添加3D曲线对象
/// <para>文档定位:数据-标准图元-创建</para>
/// </summary>
/// <param name="idEM">:管理器ID</param>
/// <param name="nPen">:添加曲线所用笔号[0,255]</param>
/// <param name="ptLines">:添加的3D曲线点集数组</param>
/// <param name="nPointCount">:添加的3D曲线的实际点数量</param>
typedef E3_ERR (*e3_CreateLines3d)(E3_ID idEM,int nPen,Pt3d* ptLines,int nPointCount);

/// <summary>
/// <para>API编码:[73283338]</para>
/// 接口说明:添加SVG曲线对象
/// <para>文档定位:数据-标准图元-创建</para>
/// </summary>
/// <param name="idEM">:管理器ID</param>
/// <param name="nPen">:添加曲线所用笔号[0,255]</param>
/// <param name="pSvgStr">:svg path路径字符串</param>
/// <param name="bUpdateParentInfo">:是否更新列表</param>
/// <param name="idEnt">:新创建SVG对象的id</param>
typedef E3_ERR (*e3_CreateSvgPath)(E3_ID idEM,int nPen,TCHAR* pSvgStr,BOOL bUpdateParentInfo,E3_ID& idEnt);

/// <summary>
/// <para>API编码:[38005460]</para>
/// 接口说明:添加SVG曲线对象
/// <para>文档定位:数据-标准图元-创建</para>
/// </summary>
/// <param name="idEM">:管理器ID</param>
/// <param name="nPen">:添加曲线所用笔号[0,255]</param>
/// <param name="pSvgStr">:svg path路径字符串</param>
/// <param name="bPick">:预留接口.默认值:flase</param>
/// <param name="bUndo">:预留接口.默认值:flase</param>
/// <param name="strUndoName">:预留接口.默认值:""</param>
typedef E3_ERR (*e3_CreateSvgPath_2)(E3_ID idEM,int nPen,TCHAR* pSvgStr,BOOL bPick,BOOL bUndo,TCHAR* strUndoName);

/// <summary>
/// <para>API编码:[87918644]</para>
/// 接口说明:字符串形式的IP地址转换为32位无符号整形数据
/// <para>文档定位:环境-控制卡-配置</para>
/// </summary>
/// <param name="IPString[16]">:需要转换的IP地址，按照点分十进制表示形式，16位字节数据，低位先发，包括结束符”\0”</param>
/// <param name="&IP">:转换完成的IP地址，32位无符号整形，按照Bit Endian Byte Order顺序排列</param>
typedef BOOL (*e3_EthConvertStringToIP)(char IPString[16],unsigned int &IP);

/// <summary>
/// <para>API编码:[42714315]</para>
/// 接口说明:根据将已知的DLC 板卡IP地址分配到注册表中
/// <para>文档定位:环境-控制卡-配置</para>
/// </summary>
/// <param name="IPAddr">:板卡IP地址</param>
typedef E3_ERR (*e3_EthRegisterCardByIP)(unsigned int IPAddr);

/// <summary>
/// <para>API编码:[04904722]</para>
/// 接口说明:得到指定投影对象参数（当前有投影获取设置正常，当前无投影调用此接口返回值2）
/// <para>文档定位:数据-3D操作</para>
/// </summary>
/// <param name="idEnt">:对象ID</param>
/// <param name="nProjectMode">:投影模式： 0投影 1包裹 2圆柱包裹3：球面包裹 4：旋转体包裹 5包裹xy</param>
/// <param name="dLimetZ">:z极限值</param>
/// <param name="dDefaultZ">:默认z</param>
/// <param name="bDownProject">:下投影</param>
/// <param name="bRemoveNoInter">:移除未相交点</param>
/// <param name="dBrokenZTol">:移除未相交点垂直线断开的阈值</param>
/// <param name="bCylinderX">:绕X轴</param>
/// <param name="dCylinderDiameter">:圆柱直径</param>
/// <param name="nAlignMode">:对齐模式</param>
/// <param name="dAlignOffset">:对齐偏移</param>
/// <param name="bCurveReducePt">:对曲线进行自动减点</param>
/// <param name="dCurveReducePtTol">:自动减点计算误差</param>
typedef E3_ERR (*e3_GetProjectEntParam)(E3_ID idEnt,int& nProjectMode,double& dLimetZ,double& dDefaultZ,BOOL& bDownProject,BOOL& bRemoveNoInter,double& dBrokenZTol,BOOL& bCylinderX,double& dCylinderDiameter,int& nAlignMode,double& dAlignOffset,BOOL& bCurveReducePt,double& dCurveReducePtTol);

/// <summary>
/// <para>API编码:[37414844]</para>
/// 接口说明:标刻一组点
/// <para>文档定位:硬件-加工动作-列表命令-对象级列表命令</para>
/// </summary>
/// <param name="idMarker">:板卡ID</param>
/// <param name="type">:默认为0</param>
/// <param name="pen">:笔号[0,255]</param>
/// <param name="ptNum">:标刻点数</param>
/// <param name="nFlag">:标刻标志位，</param>
/// <param name="ptBuf[][2]">:标刻点坐标数组</param>
typedef E3_ERR (*e3_MarkerPointsToList)(E3_ID idMarker,int type,int pen,int ptNum,int nFlag,double ptBuf[][2]);

/// <summary>
/// <para>API编码:[76501316]</para>
/// 接口说明:设置错误复位信号
/// <para>文档定位:硬件-资源-激光-配置</para>
/// </summary>
/// <param name="idMarker">:板卡ID</param>
typedef E3_ERR (*e3_MarkerResetLaserError)(E3_ID idMarker);

/// <summary>
/// <para>API编码:[55026092]</para>
/// 接口说明:保存CFG文件
/// <para>文档定位:环境-控制卡-配置</para>
/// </summary>
/// <param name="idMarker">:板卡ID</param>
typedef E3_ERR (*e3_MarkerSaveCfg)(E3_ID idMarker);

/// <summary>
/// <para>API编码:[20948937]</para>
/// 接口说明:检测输入口在不同的列表索引对象之间跳转；（列表执行等待，检查输入口的状态满足条件之后，列表运行到相对应的列表索引对象处开始执行列表，列表索引对象之前指令不再执行，若不满足条件则一直等待）
/// <para>文档定位:硬件-组合动作-列表命令-列表过程命令</para>
/// </summary>
/// <param name="idMarker">:板卡ID</param>
/// <param name="wMask">:端口 端口 Bit0表示端口0， Bit1表示端口1...... （端口掩码：需检测的端口号，如要测试端口0和端口1的状态，此值为3）</param>
/// <param name="wLevel">:端口满足条件后的比较值 bit=1表示高电平，bit=0表示低电平，（若掩码为3，需检测端口1为高电平时，此值则为2，需检测端口0和端口1均为高电平时，此值则为3）</param>
/// <param name="nIndex">:跳转到的索引号[0-255]</param>
typedef E3_ERR (*e3_MarkerSetInputJumpIndexToList)(E3_ID idMarker,WORD wMask,WORD wLevel,int nIndex);

/// <summary>
/// <para>API编码:[07805088]</para>
/// 接口说明:投影指定对象
/// <para>文档定位:数据-3D操作</para>
/// </summary>
/// <param name="idEM">:管理器ID</param>
/// <param name="idEnt">:对象ID</param>
/// <param name="nProjectMode">:模式</param>
/// <param name="bDownProject">:从下往上投影</param>
/// <param name="dLimetZ">:Z极限值</param>
/// <param name="dDefaultZ">:Z默认值</param>
/// <param name="bRemoveNoInter">:移除未相交点</param>
/// <param name="bCylinderX">:</param>
/// <param name="dCylinderDiameter">:</param>
/// <param name="bUndo">:预留参数默认false</param>
/// <param name="strUndo">:预留接口，默认空</param>
typedef E3_ERR (*e3_ProjectEnt)(E3_ID idEM,E3_ID idEnt,int nProjectMode,BOOL bDownProject,double dLimetZ,double dDefaultZ,BOOL bRemoveNoInter,BOOL bCylinderX,double dCylinderDiameter,BOOL bUndo,TCHAR* strUndo);

/// <summary>
/// <para>API编码:[74390126]</para>
/// 接口说明:投影对象删除投影
/// <para>文档定位:数据-3D操作</para>
/// </summary>
/// <param name="idEnt">:对象ID</param>
typedef E3_ERR (*e3_ProjectEntDelete)(E3_ID idEnt);

/// <summary>
/// <para>API编码:[51831403]</para>
/// 接口说明:设置指定投影对象参数（当前无投影调用此接口返回值2）
/// <para>文档定位:数据-3D操作</para>
/// </summary>
/// <param name="idEnt">:对象ID</param>
/// <param name="nProjectMode">:投影模式： 0投影 1包裹 2圆柱包裹3：球面包裹 4：旋转体包裹 5包裹xy</param>
/// <param name="dLimetZ">:z极限值</param>
/// <param name="dDefaultZ">:默认z</param>
/// <param name="bDownProject">:下投影</param>
/// <param name="bRemoveNoInter">:移除未相交点</param>
/// <param name="dBrokenZTol">:移除未相交点垂直线断开的阈值</param>
/// <param name="bCylinderX">:绕X轴</param>
/// <param name="dCylinderDiameter">:圆柱直径</param>
/// <param name="nAlignMode">:对齐模式</param>
/// <param name="dAlignOffset">:对齐偏移</param>
/// <param name="bCurveReducePt">:对曲线进行自动减点</param>
/// <param name="dCurveReducePtTol">:自动减点计算误差</param>
typedef E3_ERR (*e3_SetProjectEntParam)(E3_ID idEnt,int nProjectMode,double dLimetZ,double dDefaultZ,BOOL bDownProject,BOOL bRemoveNoInter,double dBrokenZTol,BOOL bCylinderX,double dCylinderDiameter,int nAlignMode,double dAlignOffset,BOOL bCurveReducePt,double dCurveReducePtTol);

/// <summary>
/// <para>API编码:[94857247]</para>
/// 接口说明:开启winsock接口库（一般程序开始时调用）
/// <para>文档定位:环境-控制卡-配置</para>
/// </summary>
typedef BOOL (*e3_WSAStartUp)();

/// <summary>
/// <para>API编码:[97303186]</para>
/// 接口说明:添加图层（此接口需用得到层id接口得到层id）
/// <para>文档定位:数据-对象操作-对象通用读写</para>
/// </summary>
/// <param name="idEM">:管理器ID</param>
/// <param name="bUndo">:预留接口默认false</param>
/// <param name="strUndoName">:预留接口，默认""</param>
typedef E3_ERR (*e3_AddLayer)(E3_ID idEM,BOOL bUndo,TCHAR* strUndoName);

/// <summary>
/// <para>API编码:[97753596]</para>
/// 接口说明:添加图层（此接口可返回添加的层id）
/// <para>文档定位:数据-对象操作-对象通用读写</para>
/// </summary>
/// <param name="idEM">:管理器ID</param>
/// <param name="idNewLayer">:返回的图层id</param>
typedef E3_ERR (*e3_AddNewLayer)(E3_ID idEM,E3_ID& idNewLayer);

/// <summary>
/// <para>API编码:[26883381]</para>
/// 接口说明:对对象的曲线中的直线进行自动减点
/// <para>文档定位:数据-对象操作-对象间操作</para>
/// </summary>
/// <param name="idEnt">:对象ID</param>
/// <param name="dMinDistTol">:曲线离散误差（mm）</param>
typedef E3_ERR (*e3_AutoReduceCurvePt)(E3_ID idEnt,double dMinDistTol);

/// <summary>
/// <para>API编码:[71801712]</para>
/// 接口说明:关闭控制卡
/// <para>文档定位:环境-初始化以及释放</para>
/// </summary>
/// <param name="idMarker">:控制卡的ID;</param>
typedef E3_ERR (*e3_CloseMarker)(E3_ID idMarker);

/// <summary>
/// <para>API编码:[05546620]</para>
/// 接口说明:复制对象
/// <para>文档定位:数据-对象操作-对象间操作</para>
/// </summary>
/// <param name="idEnt">:被复制对象的ID</param>
typedef E3_ID (*e3_CopyEntity)(E3_ID idEnt);

/// <summary>
/// <para>API编码:[27363120]</para>
/// 接口说明:添加圆（新添加对象id需使用得到对象id接口获取）
/// <para>文档定位:数据-标准图元-创建</para>
/// </summary>
/// <param name="idEM">:管理器ID</param>
/// <param name="nPen">:笔号[0,255]</param>
/// <param name="pt1">:圆中心坐标</param>
/// <param name="pt2">:圆半径,此坐标与圆心坐标距离即为半径.</param>
/// <param name="bPick">:预留接口.默认值:flase</param>
/// <param name="bUndo">:预留接口.默认值:flase</param>
/// <param name="strUndoName">:预留接口.默认值:""</param>
typedef E3_ERR (*e3_CreateCircle)(E3_ID idEM,int nPen,Pt2d pt1,Pt2d pt2,BOOL bPick,BOOL bUndo,TCHAR* strUndoName);

/// <summary>
/// <para>API编码:[88719874]</para>
/// 接口说明:添加圆(新添加对象ID此接口直接返回)
/// <para>文档定位:数据-标准图元-创建</para>
/// </summary>
/// <param name="idEM">:管理器ID</param>
/// <param name="nPen">:笔号[0,255]</param>
/// <param name="pt1">:圆中心坐标</param>
/// <param name="pt2">:圆半径坐标,此坐标与圆心坐标距离即为半径.</param>
/// <param name="bUpdateParentInfo">:是否更新列表信息，若不更新对象列表信息,最后更新,避免大量创建时由于更新对象列表导致的卡顿</param>
/// <param name="idNewEnt">:返回添加对象ID</param>
typedef E3_ERR (*e3_CreateCircle_2)(E3_ID idEM,int nPen,Pt2d pt1,Pt2d pt2,BOOL bUpdateParentInfo,E3_ID& idNewEnt);

/// <summary>
/// <para>API编码:[45813410]</para>
/// 接口说明:创建控制器,将控制器添加到管理器中,类型与标准软件中相同
/// <para>文档定位:数据-标准图元-创建</para>
/// </summary>
/// <param name="idEM">:管理器ID</param>
/// <param name="nPen">:笔号[0,255]</param>
/// <param name="nControlType">:控制器类型1=延时器;2=输入端口; 3=输出端口; 4=Unkonw;(预留) 5=扩展轴; 6=输入口跳转; 7=索引; 8=CCD; 9=编码器移动距离</param>
/// <param name="bPick">:预留接口.默认值:flase</param>
/// <param name="bUndo">:预留接口.默认值:flase</param>
/// <param name="strUndoName">:预留接口.默认值:""</param>
typedef E3_ERR (*e3_CreateControl)(E3_ID idEM,int nPen,int nControlType,BOOL bPick,BOOL bUndo,TCHAR* strUndoName);

/// <summary>
/// <para>API编码:[85456471]</para>
/// 接口说明:创建控制器,将控制器添加到管理器中,类型与标准软件中相同
/// <para>文档定位:数据-标准图元-创建</para>
/// </summary>
/// <param name="idEM">:管理器ID</param>
/// <param name="nPen">:笔号[0,255]</param>
/// <param name="nControlType">:控制器类型1=延时器;2=输入端口; 3=输出端口; 4=Unkonw;(预留) 5=扩展轴; 6=输入口跳转; 7=索引; 8=CCD; 9=编码器移动距离</param>
/// <param name="bUpdateParentInfo">:是否更新列表信息，若不更新对象列表信息,最后更新,避免大量创建时由于更新对象列表导致的卡顿</param>
/// <param name="idNewEnt">:返回添加对象ID</param>
typedef E3_ERR (*e3_CreateControl_2)(E3_ID idEM,int nPen,int nControlType,BOOL bUpdateParentInfo,E3_ID& idNewEnt);

/// <summary>
/// <para>API编码:[91838111]</para>
/// 接口说明:添加椭圆
/// <para>文档定位:数据-标准图元-创建</para>
/// </summary>
/// <param name="idEM">:管理器ID</param>
/// <param name="nPen">:笔号[0,255]</param>
/// <param name="pt1">:椭圆外包盒左下角坐标</param>
/// <param name="pt2">:椭圆外包盒右上角坐标</param>
/// <param name="bPick">:预留接口.默认值:flase</param>
/// <param name="bUndo">:预留接口.默认值:flase</param>
/// <param name="strUndoName">:预留接口.默认值:""</param>
typedef E3_ERR (*e3_CreateEllipse)(E3_ID idEM,int nPen,Pt2d pt1,Pt2d pt2,BOOL bPick,BOOL bUndo,TCHAR* strUndoName);

/// <summary>
/// <para>API编码:[89444728]</para>
/// 接口说明:添加椭圆
/// <para>文档定位:数据-标准图元-创建</para>
/// </summary>
/// <param name="idEM">:管理器ID</param>
/// <param name="nPen">:笔号[0,255]</param>
/// <param name="pt1">:椭圆外包盒左下角坐标</param>
/// <param name="pt2">:椭圆外包盒右上角坐标</param>
/// <param name="bUpdateParentInfo">:是否更新列表信息，若不更新对象列表信息,最后更新,避免大量创建时由于更新对象列表导致的卡顿</param>
/// <param name="idNewEnt">:返回添加对象ID</param>
typedef E3_ERR (*e3_CreateEllipse_2)(E3_ID idEM,int nPen,Pt2d pt1,Pt2d pt2,BOOL bUpdateParentInfo,E3_ID& idNewEnt);

/// <summary>
/// <para>API编码:[64805740]</para>
/// 接口说明:添加线段
/// <para>文档定位:数据-标准图元-创建</para>
/// </summary>
/// <param name="idEM">:管理器ID</param>
/// <param name="nPen">:笔号[0,255]</param>
/// <param name="ptLines">:线段的点集数组</param>
/// <param name="nPointCount">:添加点的数量（实际添加的点数量）</param>
/// <param name="bPick">:预留接口.默认值:flase</param>
/// <param name="bUndo">:预留接口.默认值:flase</param>
/// <param name="strUndoName">:预留接口.默认值:""</param>
typedef E3_ERR (*e3_CreateLines)(E3_ID idEM,int nPen,Pt2d* ptLines,int nPointCount,BOOL bPick,BOOL bUndo,TCHAR* strUndoName);

/// <summary>
/// <para>API编码:[96973526]</para>
/// 接口说明:添加线段
/// <para>文档定位:数据-标准图元-创建</para>
/// </summary>
/// <param name="idEM">:管理器ID</param>
/// <param name="nPen">:笔号[0,255]</param>
/// <param name="ptLines">:线段的点集数组</param>
/// <param name="nPointCount">:添加点的数量（实际添加的点数量）</param>
/// <param name="bUpdateParentInfo">:是否更新列表信息，若不更新对象列表信息,最后更新,避免大量创建时由于更新对象列表导致的卡顿</param>
/// <param name="idEnt">:返回添加对象ID</param>
typedef E3_ERR (*e3_CreateLines_2)(E3_ID idEM,int nPen,Pt2d* ptLines,int nPointCount,BOOL bUpdateParentInfo,E3_ID& idEnt);

/// <summary>
/// <para>API编码:[84889825]</para>
/// 接口说明:添加点对象
/// <para>文档定位:数据-标准图元-创建</para>
/// </summary>
/// <param name="idEM">:管理器ID</param>
/// <param name="nPen">:笔号[0,255]</param>
/// <param name="pts">:线段的点集数组</param>
/// <param name="nPointCount">:添加点的数量（实际添加的点数量）</param>
/// <param name="reserved1">:预留接口.默认值:flase</param>
/// <param name="reserved2">:预留接口.默认值:flase</param>
/// <param name="reserved3">:预留接口.默认值:""</param>
typedef E3_ERR (*e3_CreatePoints)(E3_ID idEM,int nPen,Pt2d* pts,int nPointCount,BOOL reserved1,BOOL reserved2,TCHAR* reserved3);

/// <summary>
/// <para>API编码:[43447856]</para>
/// 接口说明:添加点对象
/// <para>文档定位:数据-标准图元-创建</para>
/// </summary>
/// <param name="idEM">:管理器ID</param>
/// <param name="nPen">:笔号[0,255]</param>
/// <param name="pts">:线段的点集数组</param>
/// <param name="nPointCount">:添加点的数量（实际添加的点数量）</param>
/// <param name="bUpdateParentInfo">:是否更新列表信息，若不更新对象列表信息,最后更新,避免大量创建时由于更新对象列表导致的卡顿</param>
/// <param name="idNewEnt">:返回添加对象ID</param>
typedef E3_ERR (*e3_CreatePoints_2)(E3_ID idEM,int nPen,Pt2d* pts,int nPointCount,BOOL bUpdateParentInfo,E3_ID& idNewEnt);

/// <summary>
/// <para>API编码:[67951084]</para>
/// 接口说明:添加六边形对象
/// <para>文档定位:数据-标准图元-创建</para>
/// </summary>
/// <param name="idEM">:管理器ID</param>
/// <param name="nPen">:笔号[0,255]</param>
/// <param name="pt1">:六边形外切圆的左下角坐标</param>
/// <param name="pt2">:六边形外切圆的右上角坐标</param>
/// <param name="bPick">:预留接口.默认值:flase</param>
/// <param name="bUndo">:预留接口.默认值:flase</param>
/// <param name="strUndoName">:预留接口.默认值:""</param>
typedef E3_ERR (*e3_CreatePolygon)(E3_ID idEM,int nPen,Pt2d pt1,Pt2d pt2,BOOL bPick,BOOL bUndo,TCHAR* strUndoName);

/// <summary>
/// <para>API编码:[96717837]</para>
/// 接口说明:添加六边形对象
/// <para>文档定位:数据-标准图元-创建</para>
/// </summary>
/// <param name="idEM">:管理器ID</param>
/// <param name="nPen">:笔号[0,255]</param>
/// <param name="pt1">:六边形外切圆的左下角坐标</param>
/// <param name="pt2">:六边形外切圆的右上角坐标</param>
/// <param name="bUpdateParentInfo">:是否更新列表信息，若不更新对象列表信息,最后更新,避免大量创建时由于更新对象列表导致的卡顿</param>
/// <param name="idNewEnt">:返回添加对象ID</param>
typedef E3_ERR (*e3_CreatePolygon_2)(E3_ID idEM,int nPen,Pt2d pt1,Pt2d pt2,BOOL bUpdateParentInfo,E3_ID& idNewEnt);

/// <summary>
/// <para>API编码:[81677020]</para>
/// 接口说明:添加矩形
/// <para>文档定位:数据-标准图元-创建</para>
/// </summary>
/// <param name="idEM">:管理器ID</param>
/// <param name="nPen">:笔号[0,255]</param>
/// <param name="pt1">:矩形左下脚下x，y坐标</param>
/// <param name="pt2">:矩形外包盒右上角坐标</param>
/// <param name="bPick">:预留接口.默认值:flase</param>
/// <param name="bUndo">:预留接口.默认值:flase</param>
/// <param name="strUndoName">:预留接口.默认值:""</param>
typedef E3_ERR (*e3_CreateRect)(E3_ID idEM,int nPen,Pt2d pt1,Pt2d pt2,BOOL bPick,BOOL bUndo,TCHAR* strUndoName);

/// <summary>
/// <para>API编码:[71254326]</para>
/// 接口说明:添加矩形
/// <para>文档定位:数据-标准图元-创建</para>
/// </summary>
/// <param name="idEM">:管理器ID</param>
/// <param name="nPen">:笔号[0,255]</param>
/// <param name="pt1">:矩形左下脚下x，y坐标</param>
/// <param name="pt2">:矩形外包盒右上角坐标</param>
/// <param name="bUpdateParentInfo">:是否更新列表信息，若不更新对象列表信息,最后更新,避免大量创建时由于更新对象列表导致的卡顿</param>
/// <param name="idNewEnt">:返回添加对象ID</param>
typedef E3_ERR (*e3_CreateRect_2)(E3_ID idEM,int nPen,Pt2d pt1,Pt2d pt2,BOOL bUpdateParentInfo,E3_ID& idNewEnt);

/// <summary>
/// <para>API编码:[69225644]</para>
/// 接口说明:添加螺旋线
/// <para>文档定位:数据-标准图元-创建</para>
/// </summary>
/// <param name="idEM">:管理器ID</param>
/// <param name="nPen">:笔号[0,255]</param>
/// <param name="pt1">:螺旋中心坐标</param>
/// <param name="pt2">:螺旋半径坐标 （X 坐标为中心坐标+半径长度，Y坐标为中心坐标）</param>
/// <param name="bPick">:预留接口.默认值:flase</param>
/// <param name="bUndo">:预留接口.默认值:flase</param>
/// <param name="strUndoName">:预留接口.默认值:""</param>
typedef E3_ERR (*e3_CreateSpiral)(E3_ID idEM,int nPen,Pt2d pt1,Pt2d pt2,BOOL bPick,BOOL bUndo,TCHAR* strUndoName);

/// <summary>
/// <para>API编码:[70475483]</para>
/// 接口说明:添加螺旋线
/// <para>文档定位:数据-标准图元-创建</para>
/// </summary>
/// <param name="idEM">:管理器ID</param>
/// <param name="nPen">:笔号[0,255]</param>
/// <param name="pt1">:螺旋中心坐标</param>
/// <param name="pt2">:螺旋半径坐标 （X 坐标为中心坐标+半径长度，Y坐标为中心坐标）</param>
/// <param name="bUpdateParentInfo">:是否更新列表信息，若不更新对象列表信息,最后更新,避免大量创建时由于更新对象列表导致的卡顿</param>
/// <param name="idNewEnt">:返回添加对象ID</param>
typedef E3_ERR (*e3_CreateSpiral_2)(E3_ID idEM,int nPen,Pt2d pt1,Pt2d pt2,BOOL bUpdateParentInfo,E3_ID& idNewEnt);

/// <summary>
/// <para>API编码:[87849520]</para>
/// 接口说明:添加文本条码
/// <para>文档定位:数据-标准图元-创建</para>
/// </summary>
/// <param name="idEM">:管理器ID</param>
/// <param name="nPen">:笔号[0,255]</param>
/// <param name="ptBase">:工作空间中XY左下脚位置</param>
/// <param name="str">:添加的文本内容.0-4098个字符</param>
/// <param name="nFontId">:此字体在系统中所有字体的中的序号.调用E3_GetAllFontRecord得到此序号字体的名字及类型</param>
/// <param name="dTextHeight">:字符高度.默认10</param>
/// <param name="dTextWidthRatio">:字符宽度与字符高度比例.默认50</param>
/// <param name="nTextSpaceType">:文本间距模式:      0：自动模式;     1：边框间距;     2：中心间距;</param>
/// <param name="dTextSpace">:文本间距.默认2.5</param>
/// <param name="dTextAngle">:字体弧度（弧度值）</param>
/// <param name="nAlignType">:0:左对齐; 1:中心对齐; 2:右对齐;</param>
/// <param name="dNullCharWidthRatio">:空字符宽度比例.默认0.34</param>
/// <param name="dLineSpace">:行间距.默认0.21</param>
/// <param name="bVerText">:字体排列方向.True:为竖向排列</param>
/// <param name="bBold">:粗体</param>
/// <param name="bItalic">:斜体</param>
/// <param name="reserved1">:预留接口.默认值:flase</param>
/// <param name="reserved2">:预留接口.默认值:flase</param>
/// <param name="reserved3">:预留接口.默认值:""</param>
typedef E3_ERR (*e3_CreateText)(E3_ID idEM,int nPen,Pt2d ptBase,TCHAR* str,int nFontId,double dTextHeight,double dTextWidthRatio,int nTextSpaceType,double dTextSpace,double dTextAngle,int nAlignType,double dNullCharWidthRatio,double dLineSpace,BOOL bVerText,BOOL bBold,BOOL bItalic,BOOL reserved1,BOOL reserved2,TCHAR* reserved3);

/// <summary>
/// <para>API编码:[83009595]</para>
/// 接口说明:添加文本条码
/// <para>文档定位:数据-标准图元-创建</para>
/// </summary>
/// <param name="idEM">:管理器ID</param>
/// <param name="nPen">:笔号[0,255]</param>
/// <param name="ptBase">:工作空间中XY左下脚位置</param>
/// <param name="str">:添加的文本内容.0-4098个字符</param>
/// <param name="nFontId">:此字体在系统中所有字体的中的序号.调用E3_GetAllFontRecord得到此序号字体的名字及类型</param>
/// <param name="dTextHeight">:字符高度.默认10</param>
/// <param name="dTextWidthRatio">:字符宽度与字符高度比例.默认50</param>
/// <param name="nTextSpaceType">:文本间距模式:      0：自动模式;     1：边框间距;     2：中心间距;</param>
/// <param name="dTextSpace">:文本间距.默认2.5</param>
/// <param name="dTextAngle">:字体弧度（弧度值）</param>
/// <param name="nAlignType">:0:左对齐; 1:中心对齐;  2:右对齐;</param>
/// <param name="dNullCharWidthRatio">:空字符宽度比例.默认0.34</param>
/// <param name="dLineSpace">:行间距.默认0.21</param>
/// <param name="bVerText">:字体排列方向.True:为竖向排列</param>
/// <param name="bBold">:粗体</param>
/// <param name="bItalic">:斜体</param>
/// <param name="bUpdateParentInfo">:是否更新列表信息，若不更新对象列表信息,最后更新,避免大量创建时由于更新对象列表导致的卡顿</param>
/// <param name="idNewEnt">:返回添加对象ID</param>
typedef E3_ERR (*e3_CreateText_2)(E3_ID idEM,int nPen,Pt2d ptBase,TCHAR* str,int nFontId,double dTextHeight,double dTextWidthRatio,int nTextSpaceType,double dTextSpace,double dTextAngle,int nAlignType,double dNullCharWidthRatio,double dLineSpace,BOOL bVerText,BOOL bBold,BOOL bItalic,BOOL bUpdateParentInfo,E3_ID& idNewEnt);

/// <summary>
/// <para>API编码:[65402300]</para>
/// 接口说明:得到当前层ID和层索引
/// <para>文档定位:数据-对象操作-对象ID关系</para>
/// </summary>
/// <param name="idEM">:管理器ID</param>
/// <param name="idLayer">:返回的层ID</param>
/// <param name="nLayerId">:返回的层索引</param>
typedef E3_ERR (*e3_GetCurLayerId)(E3_ID idEM,E3_ID& idLayer,int& nLayerId);

/// <summary>
/// <para>API编码:[87172203]</para>
/// 接口说明:得到指定管理器中的图层数和当前层索引
/// <para>文档定位:数据-对象操作-对象ID关系</para>
/// </summary>
/// <param name="idEM">:管理器ID</param>
/// <param name="nLayerCount">:返回的指定管理器中图层数目</param>
/// <param name="nCurLayer">:返回的层索引</param>
typedef E3_ERR (*e3_GetLayerCount)(E3_ID idEM,int& nLayerCount,int& nCurLayer);

/// <summary>
/// <para>API编码:[15276306]</para>
/// 接口说明:得到指定管理器中指定序号的图层ID
/// <para>文档定位:数据-对象操作-对象ID关系</para>
/// </summary>
/// <param name="idEM">:管理器ID</param>
/// <param name="nLayerIndex">:层索引</param>
/// <param name="idLayer">:返回的指定层的ID</param>
typedef E3_ERR (*e3_GetLayerId)(E3_ID idEM,int nLayerIndex,E3_ID& idLayer);

/// <summary>
/// <para>API编码:[76258762]</para>
/// 接口说明:添加矢量文件
/// <para>文档定位:数据-标准图元-创建</para>
/// </summary>
/// <param name="pStrFileName">:矢量文件全路径</param>
/// <param name="idEM">:管理器ID</param>
/// <param name="bUndo">:预留参数 默认false</param>
/// <param name="strUndoName">:预留参数 默认为""</param>
typedef E3_ERR (*e3_ImportFileToEntMgr)(TCHAR* pStrFileName,E3_ID idEM,BOOL bUndo,TCHAR* strUndoName);

/// <summary>
/// <para>API编码:[70355257]</para>
/// 接口说明:添加矢量文件
/// <para>文档定位:数据-标准图元-创建</para>
/// </summary>
/// <param name="pStrFileName">:矢量文件全路径</param>
/// <param name="idEM">:管理器ID</param>
/// <param name="bUpdateParentInfo">:是否更新列表信息，若不更新对象列表信息,最后更新,避免大量创建时由于更新对象列表导致的卡顿</param>
/// <param name="idNewEnt">:返回添加对象ID</param>
typedef E3_ERR (*e3_ImportFileToEntMgr_2)(TCHAR* pStrFileName,E3_ID idEM,BOOL bUpdateParentInfo,E3_ID& idNewEnt);

/// <summary>
/// <para>API编码:[22276893]</para>
/// 接口说明:标刻圆弧（起始点为当前振镜所在点，从当前点开始标刻一段指定角度的圆弧）
/// <para>文档定位:硬件-组合动作-列表命令-对象级列表命令</para>
/// </summary>
/// <param name="idMarker">:板卡ID</param>
/// <param name="ptCen">:圆心坐标</param>
/// <param name="dAng">:角度，单位为（度）</param>
/// <param name="bIsFirstPt">:圆弧是否是一段曲线的第一段</param>
/// <param name="bLaserFreqSyn">:如果是第一段是否要进行激光信号同步</param>
typedef E3_ERR (*e3_MarkerArcMarkToPtList)(E3_ID idMarker,Pt3d ptCen,double dAng,BOOL bIsFirstPt,BOOL bLaserFreqSyn);

/// <summary>
/// <para>API编码:[49222656]</para>
/// 接口说明:振镜跳转到指定点
/// <para>文档定位:硬件-组合动作-列表命令-对象级列表命令</para>
/// </summary>
/// <param name="idMarker">:板卡ID</param>
/// <param name="pt">:指定点坐标</param>
typedef E3_ERR (*e3_MarkerBasicJumpToPtList)(E3_ID idMarker,Pt3d pt);

/// <summary>
/// <para>API编码:[29732565]</para>
/// 接口说明:标刻到指定点
/// <para>文档定位:硬件-组合动作-列表命令-对象级列表命令</para>
/// </summary>
/// <param name="idMarker">:板卡ID</param>
/// <param name="pt">:指定点坐标</param>
/// <param name="bIsFirstPt">:是否是第一个点</param>
/// <param name="bLaserFreqSyn">:如果是第一段是否要进行激光信号同步</param>
typedef E3_ERR (*e3_MarkerBasicMarkToPtList)(E3_ID idMarker,Pt3d pt,BOOL bIsFirstPt,BOOL bLaserFreqSyn);

/// <summary>
/// <para>API编码:[92398974]</para>
/// 接口说明:设置指定笔号参数加工（如标刻到指定点等无指定笔号的的接口使用）
/// <para>文档定位:硬件-组合动作-列表命令-列表过程命令</para>
/// </summary>
/// <param name="idMarker">:板卡ID</param>
/// <param name="nPen">:笔号[0,255]</param>
typedef E3_ERR (*e3_MarkerBasicSetPenList)(E3_ID idMarker,int nPen);

/// <summary>
/// <para>API编码:[31015533]</para>
/// 接口说明:检查激光器状态
/// <para>文档定位:硬件-资源-激光-状态查询</para>
/// </summary>
/// <param name="idMarker">:板卡ID</param>
/// <param name="isOk">:激光器状态是否正常</param>
typedef E3_ERR (*e3_MarkerCheckLaserState)(E3_ID idMarker,BOOL& isOk);

/// <summary>
/// <para>API编码:[42892184]</para>
/// 接口说明:增加缓存数据
/// <para>文档定位:硬件-组合动作-动作指令</para>
/// </summary>
/// <param name="idMarker">:板卡ID</param>
/// <param name="pStr1">:设置的对象名字pStr1对应的字符串</param>
/// <param name="pStr2">:设置的对象名字pStr2对应的字符串</param>
/// <param name="pStr3">:设置的对象名字pStr3对应的字符串</param>
/// <param name="pStr4">:设置的对象名字pStr4对应的字符串</param>
/// <param name="pStr5">:设置的对象名字pStr5对应的字符串</param>
/// <param name="pStr6">:设置的对象名字pStr6对应的字符串</param>
typedef E3_ERR (*e3_MarkerContinueBufferAdd)(E3_ID idMarker,TCHAR* pStr1,TCHAR* pStr2,TCHAR* pStr3,TCHAR* pStr4,TCHAR* pStr5,TCHAR* pStr6);

/// <summary>
/// <para>API编码:[03445085]</para>
/// 接口说明:清除缓存区
/// <para>文档定位:硬件-组合动作-动作指令</para>
/// </summary>
/// <param name="idMarker">:板卡ID</param>
typedef E3_ERR (*e3_MarkerContinueBufferClear)(E3_ID idMarker);

/// <summary>
/// <para>API编码:[61383545]</para>
/// 接口说明:得到已加工数目和缓存区剩余个数
/// <para>文档定位:硬件-资源-激光-状态查询</para>
/// </summary>
/// <param name="idMarker">:板卡ID</param>
/// <param name="nTotalMarkCount">:返回的从开始加工到现在已经完整加工的次数</param>
/// <param name="nBufferLeftCount">:当前缓存区剩余中未开始处理的个数（有可能数据已经处理，当时还未开始加工）,缓存区数据数最大为8</param>
typedef E3_ERR (*e3_MarkerContinueBufferGetParam)(E3_ID idMarker,int& nTotalMarkCount,int& nBufferLeftCount);

/// <summary>
/// <para>API编码:[39900765]</para>
/// 接口说明:设置发送零件数已经结束的标志
/// <para>文档定位:硬件-组合动作-动作指令</para>
/// </summary>
/// <param name="idMarker">:板卡ID</param>
typedef E3_ERR (*e3_MarkerContinueBufferPartFinish)(E3_ID idMarker);

/// <summary>
/// <para>API编码:[59480047]</para>
/// 接口说明:设置缓存区文本对象的名字
/// <para>文档定位:硬件-组合动作-动作指令</para>
/// </summary>
/// <param name="idMarker">:板卡ID</param>
/// <param name="nNum">:设置后面有几个字符串有效</param>
/// <param name="pStr1">:设置缓存区字符串的对象名</param>
/// <param name="pStr2">:设置缓存区字符串的对象名</param>
/// <param name="pStr3">:设置缓存区字符串的对象名</param>
/// <param name="pStr4">:设置缓存区字符串的对象名</param>
/// <param name="pStr5">:设置缓存区字符串的对象名</param>
/// <param name="pStr6">:设置缓存区字符串的对象名</param>
typedef E3_ERR (*e3_MarkerContinueBufferSetTextName)(E3_ID idMarker,int nNum,TCHAR* pStr1,TCHAR* pStr2,TCHAR* pStr3,TCHAR* pStr4,TCHAR* pStr5,TCHAR* pStr6);

/// <summary>
/// <para>API编码:[52588617]</para>
/// 接口说明:开始缓存区加工，如何缓存区没数据会一直等待数据
/// <para>文档定位:硬件-组合动作-动作指令</para>
/// </summary>
/// <param name="idMarker">:板卡ID</param>
/// <param name="idEM">:管理器ID</param>
/// <param name="idEntParent">:层ID</param>
typedef E3_ERR (*e3_MarkerContinueBufferStart)(E3_ID idMarker,E3_ID idEM,E3_ID idEntParent);

/// <summary>
/// <para>API编码:[92504541]</para>
/// 接口说明:开始循环
/// <para>文档定位:硬件-组合动作-列表命令-列表过程命令</para>
/// </summary>
/// <param name="idMarker">:板卡ID</param>
typedef E3_ERR (*e3_MarkerDoLoopToList)(E3_ID idMarker);

/// <summary>
/// <para>API编码:[30764560]</para>
/// 接口说明:脱机使能
/// <para>文档定位:硬件-组合动作-列表命令-列表过程命令</para>
/// </summary>
/// <param name="idMarker">:板卡ID</param>
/// <param name="bOffline">:是否使能脱机 ,true为使能</param>
typedef E3_ERR (*e3_MarkerEnableOffLineMode)(E3_ID idMarker,BOOL bOffline);

/// <summary>
/// <para>API编码:[23560627]</para>
/// 接口说明:仅加工不发送数据
/// <para>文档定位:环境-控制卡-操作</para>
/// </summary>
/// <param name="idMarker">:板卡ID</param>
/// <param name="bWaitForFinish">:是否等到加工结束返回 true:是</param>
/// <param name="nFlag">:加工标志位 0:加工</param>
typedef E3_ERR (*e3_MarkerExecuteAndWaitFinish)(E3_ID idMarker,BOOL bWaitForFinish,int nFlag);

/// <summary>
/// <para>API编码:[32545702]</para>
/// 接口说明:获取板卡运行状态
/// <para>文档定位:硬件-资源-振镜-状态查询</para>
/// </summary>
/// <param name="idMarker">:板卡ID</param>
/// <param name="nStatus">:板卡运行状态,一共32Bit,每Bit分别代表不同的状态,具体请查看状态表;BIT0:加工过程中振镜位置是否超出最大加工幅面; 0x1=振镜已超出最大加工幅面;0x0=振镜未超出最大加工幅面;</param>
typedef E3_ERR (*e3_MarkerGetBoardRunningStatus)(E3_ID idMarker,unsigned int& nStatus);

/// <summary>
/// <para>API编码:[76468645]</para>
/// 接口说明:得到激光器状态（F3是否检测激光器的启用/关闭不影响此接口的状态）
/// <para>文档定位:硬件-资源-激光-状态查询</para>
/// </summary>
/// <param name="idMarker">:板卡ID</param>
/// <param name="data">:激光器状态,                                                                                                                                                                                                                                                                                                            QCW:详情查看;BIT0 :激光器发射反馈: 1=正常;0=异常;BIT1 主电源启动反馈:1=正常;0=异常;BIT2 系统上电反馈:1=正常;0=异常;BIT3 激光器异常状态反馈:1=正常;0=异常;BIT4 ;BIT5 激光输出状态:1=打开;0=关闭;BIT6 红光输出状态:1=打开;0=关闭;BIT7 错误复位输出状态:1=打开;0=关闭; FIBER:BIT0-3 激光状态反馈，BIT4:MO, BIT5:AP       TYPE:E/G BIT0-BIT2激光状态反馈  BIT4:MO, BIT5:AP BIT6:红光输出                                                                                                                                SPI:BIT0-3 激光状态反馈 BIT5:激光输出, BIT6 红光输出 1表示输出                                                                                                                                                                                                       CO2/YAG:BIT0-BIT3 激光状态反馈 BIT5:激光输出, BIT6 红光输出， 1表示输出状态</param>
typedef E3_ERR (*e3_MarkerGetLaserState)(E3_ID idMarker,WORD& data);

/// <summary>
/// <para>API编码:[81935943]</para>
/// 接口说明:得到当前已发列表总数
/// <para>文档定位:环境-控制卡-操作</para>
/// </summary>
/// <param name="idMarker">:板卡ID</param>
/// <param name="nCount">:返回的当前已发列表总数</param>
typedef E3_ERR (*e3_MarkerGetListTotalCount)(E3_ID idMarker,int& nCount);

/// <summary>
/// <para>API编码:[65544265]</para>
/// 接口说明:获取实际加工时间
/// <para>文档定位:环境-控制卡-操作</para>
/// </summary>
/// <param name="idMarker">:板卡ID</param>
/// <param name="nTimeMs">:返回的加工时间（ms）</param>
typedef E3_ERR (*e3_MarkerGetMakingTime)(E3_ID idMarker,int& nTimeMs);

/// <summary>
/// <para>API编码:[99472409]</para>
/// 接口说明:得到振镜坐标
/// <para>文档定位:硬件-资源-振镜-状态查询</para>
/// </summary>
/// <param name="idMarker">:板卡ID</param>
/// <param name="x">:当前振镜x坐标</param>
/// <param name="y">:当前振镜y坐标</param>
/// <param name="z">:当前振镜z坐标</param>
typedef E3_ERR (*e3_MarkerGetPos)(E3_ID idMarker,double& x,double& y,double& z);

/// <summary>
/// <para>API编码:[36876632]</para>
/// 接口说明:脱机开始标志
/// <para>文档定位:环境-控制卡-操作</para>
/// </summary>
/// <param name="idMarker">:板卡ID</param>
/// <param name="nFileIndex">:层序号</param>
typedef E3_ERR (*e3_MarkerOffLineModeStart)(E3_ID idMarker,int nFileIndex);

/// <summary>
/// <para>API编码:[36890195]</para>
/// 接口说明:脱机结束标志
/// <para>文档定位:硬件-组合动作-列表命令-列表过程命令</para>
/// </summary>
/// <param name="idMarker">:板卡ID</param>
typedef E3_ERR (*e3_MarkerOffLineModeStop)(E3_ID idMarker);

/// <summary>
/// <para>API编码:[39894918]</para>
/// 接口说明:暂停继续（在列表外部需要继续暂停的指令时）
/// <para>文档定位:环境-控制卡-操作</para>
/// </summary>
/// <param name="idMarker">:板卡ID</param>
typedef E3_ERR (*e3_MarkerRestartList)(E3_ID idMarker);

/// <summary>
/// <para>API编码:[70824257]</para>
/// 接口说明:脱机下传
/// <para>文档定位:硬件-组合动作-列表命令-列表过程命令</para>
/// </summary>
/// <param name="idMarker">:板卡ID</param>
/// <param name="nFileCount">:图层个数</param>
typedef E3_ERR (*e3_MarkerSendOfflineMainProgram)(E3_ID idMarker,int nFileCount);

/// <summary>
/// <para>API编码:[82331401]</para>
/// 接口说明:确保当前数据缓存区的数据已经发送到卡里，并且卡里已经执行列表
/// <para>文档定位:硬件-组合动作-列表命令-列表过程命令</para>
/// </summary>
/// <param name="idMarker">:板卡ID</param>
typedef E3_ERR (*e3_MarkerSentBufToCardAndRunList)(E3_ID idMarker);

/// <summary>
/// <para>API编码:[32151152]</para>
/// 接口说明:暂停（在列表外部需要时调用）
/// <para>文档定位:环境-控制卡-操作</para>
/// </summary>
/// <param name="idMarker">:板卡ID</param>
typedef E3_ERR (*e3_MarkerSetPause)(E3_ID idMarker);

/// <summary>
/// <para>API编码:[59798804]</para>
/// 接口说明:停止加工
/// <para>文档定位:环境-控制卡-操作</para>
/// </summary>
/// <param name="idMarker">:板卡ID</param>
typedef E3_ERR (*e3_MarkerStop)(E3_ID idMarker);

/// <summary>
/// <para>API编码:[48871173]</para>
/// 接口说明:是否开启激光器内置红光
/// <para>文档定位:硬件-资源-数字量OUT-动作</para>
/// </summary>
/// <param name="idMarker">:板卡ID</param>
/// <param name="bOn">:开启/关闭激光内置红光 true：开启</param>
typedef E3_ERR (*e3_MarkerSwitchRedLight)(E3_ID idMarker,BOOL bOn);

/// <summary>
/// <para>API编码:[46297679]</para>
/// 接口说明:设置循环开始标志
/// <para>文档定位:硬件-组合动作-列表命令-列表过程命令</para>
/// </summary>
/// <param name="idMarker">:板卡ID</param>
typedef E3_ERR (*e3_MarkertSetLoopStartToList)(E3_ID idMarker);

/// <summary>
/// <para>API编码:[83858236]</para>
/// 接口说明:等待列表命令实际执行结束
/// <para>文档定位:硬件-组合动作-列表命令-列表过程命令</para>
/// </summary>
/// <param name="idMarker">:板卡ID</param>
typedef E3_ERR (*e3_MarkerWaitForFinish)(E3_ID idMarker);

/// <summary>
/// <para>API编码:[42062835]</para>
/// 接口说明:设置输入信号参数. 列表执行到此后会等待外触发信号，有相应信号才往下执行其他操作，若为脉冲模式，外触发脉宽30us,电平模式下200
/// <para>文档定位:硬件-加工动作-列表命令-对象级列表命令</para>
/// </summary>
/// <param name="idMarker">:板卡ID</param>
/// <param name="wMask">:设置的端口值.0-65535; 一般为位域设置,按照二进制位</param>
/// <param name="wLevel">:端口满足条件之后的比较值; 一般为0或1</param>
/// <param name="bIsFollowAvail">:等待IO中振镜是否跟随(在飞行中,等待IO会暂停列表,但是流水线在移动,振镜的位置可以选择是否等待或者跟随流水线移动)</param>
typedef E3_ERR (*e3_MarkerWaitForInputToList)(E3_ID idMarker,WORD wMask,WORD wLevel,BOOL bIsFollowAvail);

/// <summary>
/// <para>API编码:[63535317]</para>
/// 接口说明:设置输出口.（控制命令） 可以用于标刻输出或者标刻结束输出等动作. Bit0是In0的状态,Bit0=1表示In0为高电平,Bit0=0表示In0为低电平. Bit1是In1的状态,Bit1=1表示In1为高电平,Bit1=0表示In1为低电平,依次类推. 如果设置值为5，表示OUT0,OUT2是高电平，其他端口都是低电平
/// <para>文档定位:硬件-资源-数字量OUT-动作</para>
/// </summary>
/// <param name="idMarker">:板卡ID</param>
/// <param name="data">:设置的输出的端口值.0-65535</param>
typedef E3_ERR (*e3_MarkerWritePort)(E3_ID idMarker,WORD data);

/// <summary>
/// <para>API编码:[92854590]</para>
/// 接口说明:列表设置输出口.此接口为列表加工时输出口，接口指令是写入板卡， 在程序中调用此函数来输出数据到当前输出端口。Bit0是In0的状态,Bit0=1表示In0为高电平,Bit0= 0表示In0为低电平；Bit1是In1的状态,Bit1=1表示In1为高电平,Bit1=0表示In1为低电平；依次类推。如果获取值为2， 表示OUT1是高电平，其他端口都是低电平
/// <para>文档定位:硬件-资源-数字量OUT-动作</para>
/// </summary>
/// <param name="idMarker">:板卡ID</param>
/// <param name="data">:设置的输出的端口值.0-65535</param>
typedef E3_ERR (*e3_MarkerWritePortToList)(E3_ID idMarker,WORD data);

/// <summary>
/// <para>API编码:[83151043]</para>
/// 接口说明:错切指定对象
/// <para>文档定位:数据-对象操作-对象间操作</para>
/// </summary>
/// <param name="idEnt">:对象ID</param>
/// <param name="nPos">:nPos为对象变换的9个基准点                                                                                                                                                                                                                                                                //6 5 4 //7 8 3 //0 1 2</param>
/// <param name="angx">:X方向倾斜角度，单位为度</param>
/// <param name="angy">:Y方向倾斜角度，单位为度</param>
typedef E3_ERR (*e3_ShearEnt)(E3_ID idEnt,int nPos,double angx,double angy);

/// <summary>
/// <para>API编码:[62839199]</para>
/// 接口说明:分割对象
/// <para>文档定位:数据-对象操作-对象间操作</para>
/// </summary>
/// <param name="idEnt">:对象ID</param>
/// <param name="pBoxs">:分割盒列表 分割盒传值：矩形最小坐标/最大坐标</param>
/// <param name="nBoxCount">:分割盒数量, 因为不同开发语言的缘故，需用明确的长度参数，以便于结构体数组长度内存确定</param>
/// <param name="dSplitErr">:边界计算误差，一般为0.001就行</param>
/// <param name="dArcTol">:曲线离散误差，一般为0.01就行</param>
/// <param name="strNewEntNamePrefix">:分割后对象名标识前缀</param>
typedef E3_ERR (*e3_SplitEntByBox)(E3_ID idEnt,SplitBox* pBoxs,int nBoxCount,double dSplitErr,double dArcTol,TCHAR* strNewEntNamePrefix);

/// <summary>
/// <para>API编码:[65800117]</para>
/// 接口说明:分割对象
/// <para>文档定位:数据-对象操作-对象ID关系</para>
/// </summary>
/// <param name="idEnt">:对象ID</param>
/// <param name="pBoxs">:分割盒列表 分割盒传值：矩形最小坐标/最大坐标</param>
/// <param name="nBoxCount">:分割盒数量, 因为不同开发语言的缘故，需用明确的长度参数，以便于结构体数组长度内存确定</param>
/// <param name="dSplitErr">:边界计算误差，一般为0.001就行</param>
/// <param name="dArcTol">:曲线离散误差，一般为0.01就行</param>
/// <param name="bNoCutEntity">:禁止切割对象,此功能使能后不会对对象进行切分,而是对分割区域中存在的很多小对象进行群组.</param>
/// <param name="bNotCutSmallEnt">:不对小于dSmallSize的对象进行分割,此功能为当分割区域内,存在整体曲线超出分割区域但是小于设定的最小分割尺寸,则不分割而是完整纳入当前分割区域,如果超出则按照分割区域边界切分.</param>
/// <param name="dSmallSize">:分割最小尺寸</param>
/// <param name="bEnableOverlap">:对填充对象进行错位分割,此功能使能后会对分割盒自动增加错位尺寸,之后对对象分割,在增加的错位尺寸内进行间隔对曲线端点进行增加减少,进行交错分割,用于错开开关光点.</param>
/// <param name="dOverlapSize">:错位分割尺寸</param>
/// <param name="strNewEntNamePrefix">:分割后对象名标识前缀</param>
typedef E3_ERR (*e3_SplitEntByBox2)(E3_ID idEnt,SplitBox* pBoxs,int nBoxCount,double dSplitErr,double dArcTol,BOOL bNoCutEntity,BOOL bNotCutSmallEnt,double dSmallSize,BOOL bEnableOverlap,double dOverlapSize,TCHAR* strNewEntNamePrefix);

/// <summary>
/// <para>API编码:[82735176]</para>
/// 接口说明:对指定的对象,沿指定的0,0,0 到ptAxisX,y,z  构成的轴线旋转,然后按照MOVEXYZ移动.
/// <para>文档定位:数据-3D操作</para>
/// </summary>
/// <param name="idEnt">:对象ID</param>
/// <param name="dMoveX">:X方向移动相对距离</param>
/// <param name="dMoveY">:Y方向移动相对距离</param>
/// <param name="dMoveZ">:Z方向移动相对距离</param>
/// <param name="ptAxisX">:旋转轴线的x坐标</param>
/// <param name="ptAxisY">:轴线的Y坐标</param>
/// <param name="ptAxisZ">:轴线的Z坐标</param>
/// <param name="fRadAngle">:旋转角度</param>
/// <param name="dTol">:精度</param>
/// <param name="idNewEnt">:旋转移动操作后返回的新的对象ID</param>
typedef E3_ERR (*e3_TransormEnt3dRotate)(E3_ID idEnt,double dMoveX,double dMoveY,double dMoveZ,double ptAxisX,double ptAxisY,double ptAxisZ,double fRadAngle,double dTol,E3_ID& idNewEnt);

/// <summary>
/// <para>API编码:[98999986]</para>
/// 接口说明:对STL模型,沿指定的0,0,0 到ptAxisX,y,z  构成的轴线旋转,然后按照MOVEXYZ移动.（三个旋转轴向量ptAxisX，ptAxisY, ptAxisZ不可同时为0）.
/// <para>文档定位:数据-3D操作</para>
/// </summary>
/// <param name="idLayer">:图层ID</param>
/// <param name="dMoveX">:X方向移动相对距离</param>
/// <param name="dMoveY">:Y方向移动相对距离</param>
/// <param name="dMoveZ">:Z方向移动相对距离</param>
/// <param name="ptAxisX">:旋转轴线的x坐标</param>
/// <param name="ptAxisY">:旋转轴线的y坐标</param>
/// <param name="ptAxisZ">:旋转轴线的z坐标</param>
/// <param name="fRadAngle">:旋转角度</param>
typedef E3_ERR (*e3_TransormStlRotate)(E3_ID idLayer,double dMoveX,double dMoveY,double dMoveZ,double ptAxisX,double ptAxisY,double ptAxisZ,double fRadAngle);

/// <summary>
/// <para>API编码:[50631982]</para>
/// 接口说明:获取QCW波形输出参数,此接口序号为2_2,与同名_2的接口声明无区别,但是底层是控制独立的硬件模块.也可以说这个是控制着第二路硬件模块.
/// <para>文档定位:数据-笔参数相关</para>
/// </summary>
/// <param name="idEM">:管理器ID</param>
/// <param name="nPenNo">:笔号[0,255]</param>
/// <param name="bLaserContMode">:是否使能连续模式，true为是</param>
/// <param name="bEnableWeldWave">:是否使能波形输出，true为是</param>
/// <param name="nMaxCount">:波形最大段数，此值最大为64段</param>
/// <param name="dWeldWavePower">:波形输出功率，功率范围[0,100]</param>
/// <param name="dWeldWaveWidthMs">:波形脉宽,64个脉宽值的和不可超过笔参数中设置的脉宽值</param>
typedef E3_ERR (*e3_GetPenParamWeldWave2_2)(E3_ID idEM,int nPenNo,BOOL& bLaserContMode,BOOL& bEnableWeldWave,int& nMaxCount,double* dWeldWavePower,double* dWeldWaveWidthMs);

/// <summary>
/// <para>API编码:[53590283]</para>
/// 接口说明:设置QCW波形2输出参数,此接口序号为2_2,与同名_2的接口声明无区别,但是底层是控制独立的硬件模块.也可以说这个是控制着第二路硬件模块.
/// <para>文档定位:数据-笔参数相关</para>
/// </summary>
/// <param name="idEM">:管理器ID</param>
/// <param name="nPenNo">:笔号[0,255]</param>
/// <param name="bLaserContMode">:是否使能连续模式，true为是</param>
/// <param name="bEnableWeldWave">:是否使能波形输出，true为是</param>
/// <param name="nMaxCount">:波形最大段数，此值最大为64段</param>
/// <param name="dWeldWavePower">:波形输出功率，功率范围[0,100]</param>
/// <param name="dWeldWaveWidthMs">:波形脉宽,64个脉宽值的和不可超过笔参数中设置的脉宽值</param>
typedef E3_ERR (*e3_SetPenParamWeldWave2_2)(E3_ID idEM,int nPenNo,BOOL bLaserContMode,BOOL bEnableWeldWave,int nMaxCount,double* dWeldWavePower,double* dWeldWaveWidthMs);

/// <summary>
/// <para>API编码:[68430511]</para>
/// 接口说明:插值拟合非均匀B样条曲线
/// <para>文档定位:数据-标准图元-创建</para>
/// </summary>
/// <param name="nFlag">:内置标志，固定为0</param>
/// <param name="nPointNum">:曲线点集数量</param>
/// <param name="ptBuf[][2]">:曲线点集数据</param>
/// <param name="idNewCurveEnt">:添加到对象管理器中的曲线ID</param>
typedef E3_ERR (*e3_BSplineInterFitCurve)(int nFlag,int nPointNum,double ptBuf[][2],E3_ID& idNewCurveEnt);

/// <summary>
/// <para>API编码:[09594498]</para>
/// 接口说明:获取对象管理器指定笔号脉宽索引
/// <para>文档定位:数据-笔参数相关</para>
/// </summary>
/// <param name="idEM">:对象管理器ID</param>
/// <param name="nPenNo">:笔号</param>
/// <param name="nLaserParamIndex">:返回脉宽索引</param>
typedef E3_ERR (*e3_GetPenParamLaserParamIndex)(E3_ID idEM,int nPenNo,int& nLaserParamIndex);

/// <summary>
/// <para>API编码:[87778931]</para>
/// 接口说明:得到条码黑白信息
/// <para>文档定位:数据-对象操作-对象通用读写</para>
/// </summary>
/// <param name="idEnt">:对象ID</param>
/// <param name="nRow">:条码行数</param>
/// <param name="nCol">:条码列数</param>
/// <param name="pDataBuf">:条码二维黑白点信息</param>
typedef E3_ERR (*e3_GetTextBarcodeInfo3)(E3_ID idEnt,int nRow,int nCol,BYTE* pDataBuf);

/// <summary>
/// <para>API编码:[14771780]</para>
/// 接口说明:跳转到列表指定索引位置
/// <para>文档定位:硬件-组合动作-列表命令-列表过程命令</para>
/// </summary>
/// <param name="idMarker">:控制卡ID</param>
/// <param name="index">:列表索引</param>
typedef E3_ERR (*e3_MarkeDirectJumpToIndexToList)(E3_ID idMarker,int index);

/// <summary>
/// <para>API编码:[24389001]</para>
/// 接口说明:获取指定计数器计数值
/// <para>文档定位:硬件-资源-寄存器-读</para>
/// </summary>
/// <param name="idMarker">:控制卡ID</param>
/// <param name="index">:计数器索引</param>
/// <param name="nCount">:</param>
typedef E3_ERR (*e3_MarkerGetMarkCount2)(E3_ID idMarker,int index,unsigned int& nCount);

/// <summary>
/// <para>API编码:[51276588]</para>
/// 接口说明:设置指定索引计数器值
/// <para>文档定位:硬件-资源-寄存器-写</para>
/// </summary>
/// <param name="idMarker">:控制卡ID</param>
/// <param name="index">:当前寄存器索引值.</param>
/// <param name="nCount">:当前寄存器的计数器值</param>
typedef E3_ERR (*e3_MarkerSetMarkCount)(E3_ID idMarker,int index,unsigned int nCount);

/// <summary>
/// <para>API编码:[97446379]</para>
/// 接口说明:设置指定索引计数器值
/// <para>文档定位:硬件-资源-寄存器-写</para>
/// </summary>
/// <param name="idMarker">:控制卡ID</param>
/// <param name="index">:当前寄存器索引值</param>
/// <param name="nCount">:当前寄存器的计数器值</param>
typedef E3_ERR (*e3_MarkerSetMarkCountToList)(E3_ID idMarker,int index,unsigned int nCount);

/// <summary>
/// <para>API编码:[35469982]</para>
/// 接口说明:开启USB通讯监控断线设置输出口状态
/// <para>文档定位:环境-控制卡-配置</para>
/// </summary>
/// <param name="idMarker">:控制卡ID</param>
/// <param name="TimeInterval">:时间间隔</param>
/// <param name="IsSetOutputPort">:USB断线输出口是否输出信号</param>
/// <param name="OutputPort">:输出端口</param>
/// <param name="OutputLevel">:端口电平状态</param>
typedef E3_ERR (*e3_MarkerStartUSBMonitorProcess)(E3_ID idMarker,unsigned short TimeInterval,unsigned char IsSetOutputPort,unsigned char OutputPort,unsigned char OutputLevel);

/// <summary>
/// <para>API编码:[67703348]</para>
/// 接口说明:列表循环，此循环可嵌套于Loop循环使用，但不可反向嵌套Loop循环
/// <para>文档定位:硬件-组合动作-列表命令-列表过程命令</para>
/// </summary>
/// <param name="idMarker">:控制卡ID</param>
typedef E3_ERR (*e3_MarkertRepeatToList)(E3_ID idMarker);

/// <summary>
/// <para>API编码:[90834687]</para>
/// 接口说明:列表循环结尾标志命令
/// <para>文档定位:硬件-组合动作-列表命令-列表过程命令</para>
/// </summary>
/// <param name="idMarker">:控制卡ID</param>
/// <param name="RepeatNumber">:循环次数==0xFFFFFFFF 无限循环 范围[1,0xffffffff]</param>
typedef E3_ERR (*e3_MarkertUntilToList)(E3_ID idMarker,unsigned int RepeatNumber);

/// <summary>
/// <para>API编码:[37954707]</para>
/// 接口说明:设置指定笔参数脉冲索引
/// <para>文档定位:数据-笔参数相关</para>
/// </summary>
/// <param name="idEM">:对象管理器ID</param>
/// <param name="nPenNo">:笔号</param>
/// <param name="nLaserParamIndex">:脉宽索引</param>
typedef E3_ERR (*e3_SetPenParamLaserParamIndex)(E3_ID idEM,int nPenNo,int nLaserParamIndex);

/// <summary>
/// <para>API编码:[86632813]</para>
/// 接口说明:循环体中指定计数器自加
/// <para>文档定位:硬件-资源-寄存器-写</para>
/// </summary>
/// <param name="idMarker">:控制卡ID</param>
/// <param name="Index">:计数器索引</param>
/// <param name="IncCounter">:自加值</param>
typedef E3_ERR (*e3_MarkerSetAutoIncCounterToList)(E3_ID idMarker,unsigned short Index,unsigned short IncCounter);

/// <summary>
/// <para>API编码:[57224956]</para>
/// 接口说明:获取对象所属管理器
/// <para>文档定位:数据-对象操作-对象通用读写</para>
/// </summary>
/// <param name="idEnt">:对象ID</param>
/// <param name="idEntMgr">:管理器ID</param>
typedef E3_ERR (*e3_GetEntMgr)(E3_ID idEnt,E3_ID& idEntMgr);

/// <summary>
/// <para>API编码:[31515403]</para>
/// 接口说明:获取对象属性
/// <para>文档定位:数据-对象操作-对象通用读写</para>
/// </summary>
/// <param name="idEnt">:对象ID</param>
/// <param name="minx">:最小X坐标</param>
/// <param name="miny">:最小Y坐标</param>
/// <param name="maxx">:最大X坐标</param>
/// <param name="maxy">:最大Y坐标</param>
/// <param name="minz">:最小Z坐标</param>
/// <param name="maxz">:最大Z坐标</param>
/// <param name="penNo">:笔号</param>
typedef E3_ERR (*e3_GetEntParam)(E3_ID idEnt,double& minx,double& miny,double& maxx,double& maxy,double& minz,double& maxz,int& penNo);

/// <summary>
/// <para>API编码:[80946951]</para>
/// 接口说明:获取第一个序列子对象
/// <para>文档定位:数据-对象操作-对象通用读写</para>
/// </summary>
/// <param name="idEnt">:对象ID</param>
/// <param name="idEntChild">:子对象ID</param>
typedef E3_ERR (*e3_GetEntParam1)(E3_ID idEnt,E3_ID& idEntChild);

/// <summary>
/// <para>API编码:[15487756]</para>
/// 接口说明:获取第一序列同级对象,也即[E3_GetEntParam1]接口得到子对象的下一个序号的对象,之后由此接口迭代获得所有排序的对象.
/// <para>文档定位:数据-对象操作-对象通用读写</para>
/// </summary>
/// <param name="idEnt">:对象ID</param>
/// <param name="idEntNext">:子对象ID</param>
typedef E3_ERR (*e3_GetEntParam2)(E3_ID idEnt,E3_ID& idEntNext);

/// <summary>
/// <para>API编码:[75510903]</para>
/// 接口说明:获取指定对象的笔号，注意得到的是对象本身的笔号，并不代表其子对象的笔号。这个在群组和填充时需要注意.
/// <para>文档定位:数据-对象操作-对象通用读写</para>
/// </summary>
/// <param name="idEnt">:对象ID</param>
/// <param name="nPen">:笔号</param>
typedef E3_ERR (*e3_GetEntPen)(E3_ID idEnt,int& nPen);

/// <summary>
/// <para>API编码:[00041454]</para>
/// 接口说明:查询条码详细信息，使用E3_GetLayerId得到层id, E3_FindEntInLayerByIndex得到指定对象ID, E3_GetAllFontCount获得当前系统包含字体数量，E3_GetAllFontRecord获得字体类型及名称用于条码字体类型及明码名称的设置.
/// <para>文档定位:数据-对象操作-对象通用读写</para>
/// </summary>
/// <param name="idEnt">:对象ID</param>
/// <param name="nMaxParamN">:最大整形数据.默认23</param>
/// <param name="nParam">:条码属性数组,每一位代表一个属性,具体请查看附录;</param>
/// <param name="nMaxParamD">:最大浮点型数据.默认值28;</param>
/// <param name="dParam">:条码造型数组,每一位代表一个造型参数,具体请查看附录;</param>
/// <param name="strFontName[256]">:条码字体类型名称;</param>
/// <param name="strTextFontName[256]">:明码字体名称;</param>
/// <param name="param1">:第一组填充参数;</param>
/// <param name="param2">:第二组填充参数;</param>
/// <param name="param3">:第三组填充参数;</param>
typedef E3_ERR (*e3_GetTextBarcodeInfo)(E3_ID idEnt,int nMaxParamN,int* nParam,int nMaxParamD,double* dParam,TCHAR strFontName[256],TCHAR strTextFontName[256],HatchParam& param1,HatchParam& param2,HatchParam& param3);

/// <summary>
/// <para>API编码:[08057877]</para>
/// 接口说明:查询条码类型及行列数.
/// <para>文档定位:数据-对象操作-对象通用读写</para>
/// </summary>
/// <param name="idEnt">:对象ID</param>
/// <param name="strText[256]">:条码数据内容</param>
/// <param name="nSizeMode">:条码版本号</param>
/// <param name="nRow">:行数;</param>
/// <param name="nCol">:列数</param>
typedef E3_ERR (*e3_GetTextBarcodeInfo2)(E3_ID idEnt,TCHAR strText[256],int& nSizeMode,int& nRow,int& nCol);

/// <summary>
/// <para>API编码:[35931452]</para>
/// 接口说明:得到二维码尺寸的接口
/// <para>文档定位:数据-对象操作-对象通用读写</para>
/// </summary>
/// <param name="idEnt">:对象ID</param>
/// <param name="nPointMode">:条码模式（4=螺旋 3=点 1=矩形 2=圆 0=标准模式）;</param>
/// <param name="dPointSize">:尺寸;</param>
/// <param name="bFixedSize">:是否使用固定尺寸;</param>
/// <param name="dFixedSizeX">:固定X尺寸;</param>
/// <param name="dFixedSizeY">:固定Y尺寸;</param>
typedef E3_ERR (*e3_GetTextBarcodeInfo4)(E3_ID idEnt,int& nPointMode,double& dPointSize,BOOL& bFixedSize,double& dFixedSizeX,double& dFixedSizeY);

/// <summary>
/// <para>API编码:[79555907]</para>
/// 接口说明:获取条码螺旋线模式参数.
/// <para>文档定位:数据-对象操作-对象通用读写</para>
/// </summary>
/// <param name="idEnt">:对象ID</param>
/// <param name="nInsideLoop">:内边界环数;</param>
/// <param name="nOutsideLoop">:外边界环数;</param>
/// <param name="bSpiralInsideToOutside">:由内向外;</param>
/// <param name="dSpiralPitchDist">:螺旋线螺距mm;</param>
/// <param name="dSpiralMinRadius">:最小半径mm;</param>
typedef E3_ERR (*e3_GetTextBarcodeInfo5)(E3_ID idEnt,int& nInsideLoop,int& nOutsideLoop,BOOL& bSpiralInsideToOutside,double& dSpiralPitchDist,double& dSpiralMinRadius);

/// <summary>
/// <para>API编码:[92243035]</para>
/// 接口说明:获取条码编码模式.
/// <para>文档定位:数据-对象操作-对象通用读写</para>
/// </summary>
/// <param name="idEnt">:对象ID</param>
/// <param name="nEncodeMode">:编码模式 0：Auto 1:Numeric 2:Alpha Numeric 3:Byte 4:Kanji;</param>
/// <param name="nCheckLevel">:错误纠正级：0-3 对应LMQH;</param>
/// <param name="nMaskPattern">:掩码：0-8对应auto 0-7;</param>
typedef E3_ERR (*e3_GetTextBarcodeInfo6)(E3_ID idEnt,int& nEncodeMode,int& nCheckLevel,int& nMaskPattern);

/// <summary>
/// <para>API编码:[49755439]</para>
/// 接口说明:用于获取指定ID对象的文本内容.
/// <para>文档定位:数据-对象操作-对象ID关系</para>
/// </summary>
/// <param name="idEnt">:对象ID</param>
/// <param name="pStr[256]">:指定ID的文本内容;</param>
typedef E3_ERR (*e3_GetTextByID)(E3_ID idEnt,TCHAR pStr[256]);

/// <summary>
/// <para>API编码:[06560219]</para>
/// 接口说明:验证条码内容是否有效，有效是指是否符合该条码类型的编码规则，编码规则可见标准软件条码信息说明.
/// <para>文档定位:数据-对象操作-对象通用读写</para>
/// </summary>
/// <param name="nMaxParamN">:最大整形数据.默认值23;</param>
/// <param name="nParam">:具体请查看字体类型附录;</param>
/// <param name="nMaxParamD">:最大浮点型数据.默认值28;</param>
/// <param name="dParam">:具体请查看字体造型参数附录;</param>
/// <param name="strFontName">:条码字体类型;</param>
/// <param name="strText">:条码文本内容;</param>
/// <param name="bIsValid">:是否为条码有效:True:有效;</param>
typedef E3_ERR (*e3_IsBarcodeTextValid)(int nMaxParamN,int* nParam,int nMaxParamD,double* dParam,TCHAR* strFontName,TCHAR* strText,BOOL& bIsValid);

/// <summary>
/// <para>API编码:[79735281]</para>
/// 接口说明:插入计数值. 计数值相当于在板卡中添加一个标志位，每次加1计录列表加工数目.
/// <para>文档定位:硬件-资源-寄存器-写</para>
/// </summary>
/// <param name="idMarker">:控制卡ID</param>
/// <param name="n">:每次计数的增量，每次加的个数.固定为1;</param>
typedef E3_ERR (*e3_MarkerChangeMarkCountToList)(E3_ID idMarker,int n);

/// <summary>
/// <para>API编码:[80865706]</para>
/// 接口说明:设置条码详细信息. 使用E3_GetLayerId得到层id, E3_FindEntInLayerByIndex得到指定对象ID, E3_GetAllFontCount获得当前系统包含字体数量，E3_GetAllFontRecord获得字体类型及名称用于条码字体类型及明码名称的设置.
/// <para>文档定位:数据-对象操作-对象通用读写</para>
/// </summary>
/// <param name="idEM">:对象管理器ID</param>
/// <param name="idEnt">:对象ID</param>
/// <param name="nMaxParamN">:最大整形数据.默认23;</param>
/// <param name="nParam">:条码属性数组,每一位代表一个属性,具体请查看附录;</param>
/// <param name="nMaxParamD">:最大浮点型数据.默认值28;</param>
/// <param name="dParam">:条码造型数组,每一位代表一个造型参数,具体请查看附录;</param>
/// <param name="str1">:条码字体类型名称,0-255;</param>
/// <param name="str2">:明码字体名称,0-255;</param>
/// <param name="param1">:第一组填充参数;</param>
/// <param name="param2">:第二组填充参数;</param>
/// <param name="param3">:第三组填充参数;</param>
/// <param name="strText">:文本内容,0-4098;</param>
/// <param name="reserved1">:预留接口.默认值:flase;</param>
/// <param name="reserved2">:预留接口.默认值:"";</param>
typedef E3_ERR (*e3_SetTextBarcodeInfo)(E3_ID idEM,E3_ID idEnt,int nMaxParamN,int* nParam,int nMaxParamD,double* dParam,TCHAR* str1,TCHAR* str2,HatchParam param1,HatchParam param2,HatchParam param3,TCHAR* strText,BOOL reserved1,TCHAR* reserved2);

/// <summary>
/// <para>API编码:[36748373]</para>
/// 接口说明:设置二维码尺寸的接口，调用此接口后需调用E3_SetTextBarcodeInfo才可让设置尺寸接口设置成功
/// <para>文档定位:数据-对象操作-对象通用读写</para>
/// </summary>
/// <param name="idEnt">:对象ID</param>
/// <param name="nPointMode">:条码模式（4=螺旋 3=点 1=矩形 2=圆 0=标准模式）;</param>
/// <param name="dPointSize">:尺寸;</param>
/// <param name="bFixedSize">:是否使用固定尺寸;</param>
/// <param name="dFixedSizeX">:固定X尺寸;</param>
/// <param name="dFixedSizeY">:固定Y尺寸;</param>
typedef E3_ERR (*e3_SetTextBarcodeInfo4)(E3_ID idEnt,int nPointMode,double dPointSize,BOOL bFixedSize,double dFixedSizeX,double dFixedSizeY);

/// <summary>
/// <para>API编码:[87689862]</para>
/// 接口说明:设置条码螺旋线模式参数，调用此接口后需调用E3_SetTextBarcodeInfo才可让设置尺寸接口设置成功.
/// <para>文档定位:数据-对象操作-对象通用读写</para>
/// </summary>
/// <param name="idEnt">:对象ID</param>
/// <param name="nInsideLoop">:内边界环数;</param>
/// <param name="nOutsideLoop">:外边界环数;</param>
/// <param name="bSpiralInsideToOutside">:由内向外;</param>
/// <param name="dSpiralPitchDist">:螺旋线螺距mm;</param>
/// <param name="dSpiralMinRadius">:最小半径mm;</param>
typedef E3_ERR (*e3_SetTextBarcodeInfo5)(E3_ID idEnt,int nInsideLoop,int nOutsideLoop,BOOL bSpiralInsideToOutside,double dSpiralPitchDist,double dSpiralMinRadius);

/// <summary>
/// <para>API编码:[55834520]</para>
/// 接口说明:设置条码编码模式.
/// <para>文档定位:数据-对象操作-对象通用读写</para>
/// </summary>
/// <param name="idEnt">:对象ID</param>
/// <param name="nEncodeMode">:编码模式 0：Auto 1:Numeric 2:Alpha Numeric 3:Byte 4:Kanji;</param>
/// <param name="nCheckLevel">:错误纠正级 0-3 对应 LMQH</param>
/// <param name="nMaskPattern">:掩码 0-8 对应 auto 0-7</param>
typedef E3_ERR (*e3_SetTextBarcodeInfo6)(E3_ID idEnt,int nEncodeMode,int nCheckLevel,int nMaskPattern);

/// <summary>
/// <para>API编码:[44573425]</para>
/// 接口说明:设置条码详细信息. 使用E3_GetLayerId得到层id, E3_FindEntInLayerByIndex得到指定对象ID, E3_GetAllFontCount获得当前系统包含字体数量，E3_GetAllFontRecord获得字体类型及名称用于条码字体类型及明码名称的设置.
/// <para>文档定位:数据-对象操作-对象通用读写</para>
/// </summary>
/// <param name="idEM">:对象管理器ID</param>
/// <param name="idEnt">:对象ID</param>
/// <param name="nMaxParamN">:最大整形数据.默认23;</param>
/// <param name="nParam">:条码属性数组,每一位代表一个属性,具体请查看附录;</param>
/// <param name="nMaxParamD">:最大浮点型数据.默认值28;</param>
/// <param name="dParam">:条码造型数组,每一位代表一个造型参数,具体请查看附录;</param>
/// <param name="str1">:条码字体类型名称,0-255;</param>
/// <param name="str2">:明码字体名称,0-255;</param>
/// <param name="param1">:第一组填充参数;</param>
/// <param name="param2">:第二组填充参数;</param>
/// <param name="param3">:第三组填充参数;</param>
/// <param name="strText">:文本内容,0-4098;</param>
typedef E3_ERR (*e3_SetTextBarcodeInfo_2)(E3_ID idEM,E3_ID idEnt,int nMaxParamN,int* nParam,int nMaxParamD,double* dParam,TCHAR* str1,TCHAR* str2,HatchParam param1,HatchParam param2,HatchParam param3,TCHAR* strText);

/// <summary>
/// <para>API编码:[92336735]</para>
/// 接口说明:得到对象基础信息2.
/// <para>文档定位:数据-对象操作-对象通用读写</para>
/// </summary>
/// <param name="idEnt">:对象ID</param>
/// <param name="type">:对象类型</param>
/// <param name="nPen">:对象笔号</param>
/// <param name="strName[256]">:对象名字</param>
/// <param name="box">:对象外包盒</param>
/// <param name="z">:对象z坐标</param>
/// <param name="a">:对象A坐标</param>
/// <param name="dSizeZ">:Z方向落差</param>
typedef E3_ERR (*e3_GetEntBaseInfo2)(E3_ID idEnt,int& type,int& nPen,TCHAR strName[256],Box2d& box,double& z,double& a,double& dSizeZ);

/// <summary>
/// <para>API编码:[35370579]</para>
/// 接口说明:得到对象基础信息3.
/// <para>文档定位:数据-对象操作-对象通用读写</para>
/// </summary>
/// <param name="idEnt">:对象ID</param>
/// <param name="type">:对象类型</param>
/// <param name="nPen">:对象笔号</param>
/// <param name="strName[256]">:对象名字</param>
/// <param name="box">:对象外包盒</param>
/// <param name="z">:对象z坐标</param>
/// <param name="a">:对象A坐标</param>
/// <param name="nMarkCount">:重复加工次数</param>
typedef E3_ERR (*e3_GetEntBaseInfo3)(E3_ID idEnt,int& type,int& nPen,TCHAR strName[256],Box2d& box,double& z,double& a,int& nMarkCount);

/// <summary>
/// <para>API编码:[03288115]</para>
/// 接口说明:得到卡配置参数中各个类型参数的总数
/// <para>文档定位:环境-控制卡-配置</para>
/// </summary>
/// <param name="idMarker">:控制卡ID</param>
/// <param name="nParamInt">:int类型参数总数</param>
/// <param name="nParamDouble">:double类型参数总数</param>
/// <param name="nParamStr">:string类型参数总数</param>
typedef E3_ERR (*e3_GetParamCount)(E3_ID idMarker,int& nParamInt,int& nParamDouble,int& nParamStr);

/// <summary>
/// <para>API编码:[31526290]</para>
/// 接口说明:获取笔参数
/// <para>文档定位:数据-笔参数相关</para>
/// </summary>
/// <param name="idEM">:管理器ID</param>
/// <param name="nPenNo">:笔号</param>
/// <param name="pStrName[256]">:笔名称</param>
/// <param name="clr">:笔颜色</param>
/// <param name="bDisableMark">:使能</param>
/// <param name="bUseDefParam">:使用默认</param>
/// <param name="nMarkLoop">:加工次数</param>
/// <param name="dMarkSpeed">:标刻速度mm/s</param>
/// <param name="dPowerRatio">:功率%</param>
/// <param name="dCurrent">:电流A</param>
/// <param name="dFreq">:频率HZ</param>
/// <param name="dQPulseWidth">:脉冲宽度us|ns</param>
/// <param name="nStartTC">:开始延时us</param>
/// <param name="nLaserOffTC">:关闭延时us</param>
/// <param name="nEndTC">:结束延时us</param>
/// <param name="nPolyTC">:拐角延时us</param>
/// <param name="dJumpSpeed">:跳转速度mm/s</param>
/// <param name="nMinJumpDelayTCUs">:最小跳转延时us</param>
/// <param name="nMaxJumpDelayTCUs">:最大跳转延时us</param>
/// <param name="dJumpLengthLimit">:跳转长度极限mm</param>
/// <param name="dPointTimeMs">:打点时间ms</param>
/// <param name="nSpiSpiContinueMode">:SPI连续模式</param>
/// <param name="nSpiWave">:SPI波形选择</param>
/// <param name="nYagMarkMode">:YAG优化填充模式</param>
/// <param name="bPulsePointMode">:脉冲点模式</param>
/// <param name="nPulseNum">:脉冲点数</param>
/// <param name="bEnableACCMode">:使能加速模式</param>
/// <param name="dEndComp">:末点补偿</param>
/// <param name="dAccDist">:加速距离mm</param>
/// <param name="dBreakAngle">:中断角度(89)（弧度值）;已经被淘汰，暂时保留</param>
/// <param name="bWobbleMode">:抖动模式(false);已经升级，目前版本不再使用这个参数</param>
/// <param name="bWobbleDiameter">:抖动直径(1)mm;已经升级，目前版本不再使用这个参数</param>
/// <param name="bWobbleDist">:抖动距离(0.5)mm;已经升级，目前版本不再使用这个参数</param>
typedef E3_ERR (*e3_GetPenParam)(E3_ID idEM,int nPenNo,TCHAR pStrName[256],int& clr,BOOL& bDisableMark,BOOL& bUseDefParam,int& nMarkLoop,double& dMarkSpeed,double& dPowerRatio,double& dCurrent,double& dFreq,double& dQPulseWidth,int& nStartTC,int& nLaserOffTC,int& nEndTC,int& nPolyTC,double& dJumpSpeed,int& nMinJumpDelayTCUs,int& nMaxJumpDelayTCUs,double& dJumpLengthLimit,double& dPointTimeMs,BOOL& nSpiSpiContinueMode,int& nSpiWave,int& nYagMarkMode,BOOL& bPulsePointMode,int& nPulseNum,BOOL& bEnableACCMode,double& dEndComp,double& dAccDist,double& dBreakAngle,BOOL& bWobbleMode,double& bWobbleDiameter,double& bWobbleDist);

/// <summary>
/// <para>API编码:[88005718]</para>
/// 接口说明:得到优化模式参数
/// <para>文档定位:数据-笔参数相关</para>
/// </summary>
/// <param name="idEM">:管理器ID</param>
/// <param name="nPenNo">:笔号</param>
/// <param name="bOpitmize">:使能优化模式</param>
/// <param name="dScanberBiDirOffset">:双向偏移</param>
/// <param name="dAccDist">:加速距离</param>
/// <param name="dEndDist">:结束距离</param>
typedef E3_ERR (*e3_GetPenParamExt4)(E3_ID idEM,int nPenNo,BOOL& bOpitmize,double& dScanberBiDirOffset,double& dAccDist,double& dEndDist);

/// <summary>
/// <para>API编码:[26334623]</para>
/// 接口说明:获取焊接参数
/// <para>文档定位:数据-笔参数相关</para>
/// </summary>
/// <param name="idEM">:管理器ID</param>
/// <param name="nPenNo">:笔号</param>
/// <param name="nMarkLoop">:加工数目</param>
/// <param name="bAveragePtMode">:是否平均分布所有点</param>
/// <param name="dPointDist">:点间距</param>
/// <param name="nPulseNum">:每点脉冲数</param>
typedef E3_ERR (*e3_GetPenParamExt5)(E3_ID idEM,int nPenNo,int& nMarkLoop,BOOL& bAveragePtMode,double& dPointDist,int& nPulseNum);

/// <summary>
/// <para>API编码:[41430745]</para>
/// 接口说明:得到当前标刻状态信息
/// <para>文档定位:环境-控制卡-配置</para>
/// </summary>
/// <param name="idMarker">:控制卡ID</param>
/// <param name="bHaveMsg">:当前加工中是否存在消息</param>
/// <param name="strMsg[256]">:调用接口后返回的消息内容</param>
/// <param name="nPartCount">:返回当前加工的对象总数</param>
/// <param name="nPartTime">:返回对象加工次数</param>
typedef E3_ERR (*e3_MarkerGetMsg)(E3_ID idMarker,BOOL& bHaveMsg,TCHAR strMsg[256],int& nPartCount,int& nPartTime);

/// <summary>
/// <para>API编码:[55234352]</para>
/// 接口说明:读取控制卡的Double类型的参数集合.
/// <para>文档定位:环境-控制卡-配置</para>
/// </summary>
/// <param name="idMarker">:控制卡ID</param>
/// <param name="nMaxParamCount">:给定最大double参数个数</param>
/// <param name="pParamDouble">:读取到的double类型的参数值数组</param>
typedef E3_ERR (*e3_MarkerGetParamDouble)(E3_ID idMarker,int nMaxParamCount,double* pParamDouble);

/// <summary>
/// <para>API编码:[32962026]</para>
/// 接口说明:读取控制卡的Int类型的参数集合.
/// <para>文档定位:环境-控制卡-配置</para>
/// </summary>
/// <param name="idMarker">:控制卡ID</param>
/// <param name="nMaxParamCount">:给定最大int参数个数</param>
/// <param name="pParamInt">:读取到的int类型的参数值数组</param>
typedef E3_ERR (*e3_MarkerGetParamInt)(E3_ID idMarker,int nMaxParamCount,int* pParamInt);

/// <summary>
/// <para>API编码:[08031012]</para>
/// 接口说明:读取控制卡的string类型的参数集合.
/// <para>文档定位:环境-控制卡-配置</para>
/// </summary>
/// <param name="idMarker">:控制卡ID</param>
/// <param name="nParamId">:读取string类型参数的索引ID</param>
/// <param name="pParamInt[256]">:读取到的string类型得参数值</param>
typedef E3_ERR (*e3_MarkerGetParamString)(E3_ID idMarker,int nParamId,TCHAR pParamInt[256]);

/// <summary>
/// <para>API编码:[83918892]</para>
/// 接口说明:USB连接侦测功能的初始化启动
/// <para>文档定位:环境-初始化以及释放</para>
/// </summary>
/// <param name="pWndMonitor">:侦测结果通过系统消息泵来传送,这里要给定接收消息的目标窗体句柄.</param>
typedef E3_ERR (*e3_MarkerInitUsbMonitor)(HWND pWndMonitor);

/// <summary>
/// <para>API编码:[87588443]</para>
/// 接口说明:列表系统的终结指令,板卡执行列表系统时执行到这一条指令后会退出列表系统.
/// <para>文档定位:硬件-组合动作-列表命令-列表过程命令</para>
/// </summary>
/// <param name="idMarker">:控制卡ID</param>
typedef E3_ERR (*e3_MarkerListEndToList)(E3_ID idMarker);

/// <summary>
/// <para>API编码:[92701320]</para>
/// 接口说明:设置控制卡的Double类型参数
/// <para>文档定位:环境-控制卡-配置</para>
/// </summary>
/// <param name="idMarker">:控制卡ID</param>
/// <param name="nMaxParamCount">:给定设置最大double参数个数</param>
/// <param name="pParamDouble">:要设置的参数数组</param>
typedef E3_ERR (*e3_MarkerSetParamDouble)(E3_ID idMarker,int nMaxParamCount,double* pParamDouble);

/// <summary>
/// <para>API编码:[36329220]</para>
/// 接口说明:设置控制卡的Int类型参数
/// <para>文档定位:环境-控制卡-配置</para>
/// </summary>
/// <param name="idMarker">:控制卡ID</param>
/// <param name="nMaxParamCount">:给定设置最大int参数个数</param>
/// <param name="pParamInt">:要设置的参数数组</param>
typedef E3_ERR (*e3_MarkerSetParamInt)(E3_ID idMarker,int nMaxParamCount,int* pParamInt);

/// <summary>
/// <para>API编码:[27230083]</para>
/// 接口说明:流水线高低速偏差校正表
/// <para>文档定位:环境-控制卡-配置</para>
/// </summary>
/// <param name="idMarker">:控制卡ID</param>
/// <param name="Enable">:是否使能: 0x0=失能; 0x1=使能;</param>
/// <param name="TableSize">:指定校正表大小,最大32组;每组两个元素位置,最大也即64个数组元素.</param>
/// <param name="TableAddr">:校正表速度差值,示例: [0]速度值,单位mm/s; [1]补偿值,单位mm; [2]速度值,单位mm/s; [3]补偿值,单位mm; [...]速度值,单位mm/s; [...+1]补偿值,单位mm;</param>
typedef E3_ERR (*e3_MarkerLoadFlyDistanceCorrectionTable)(E3_ID idMarker,unsigned char Enable,unsigned char TableSize,float* TableAddr);

/// <summary>
/// <para>API编码:[77449635]</para>
/// 接口说明:通过对象ID修改对象的内容,仅限文本类型对象
/// <para>文档定位:数据-标准图元-编辑-文本类型-文本</para>
/// </summary>
/// <param name="idEnt">:对象ID</param>
/// <param name="strTextNew">:新的内容字符</param>
typedef E3_ERR (*e3_ChangeTextById)(E3_ID idEnt,TCHAR* strTextNew);

/// <summary>
/// <para>API编码:[60245749]</para>
/// 接口说明:通过对象名称修改对象的内容,仅限文本类型对象
/// <para>文档定位:数据-标准图元-编辑-文本类型-文本</para>
/// </summary>
/// <param name="idLayer">:图层ID</param>
/// <param name="strEntName">:对象的名称</param>
/// <param name="strTextNew">:新的内容字符</param>
typedef E3_ERR (*e3_ChangeTextByName)(E3_ID idLayer,TCHAR* strEntName,TCHAR* strTextNew);

/// <summary>
/// <para>API编码:[85868531]</para>
/// 接口说明:关闭函数库
/// <para>文档定位:环境-初始化以及释放</para>
/// </summary>
typedef E3_ERR (*e3_Close)();

/// <summary>
/// <para>API编码:[39650013]</para>
/// 接口说明:将位图文件添加到管理器中. 支持BMP,JPG,JPEG,GIF,TGA,PNG,TIF,TIFF. *上述支持类型在Windows版本系统上测试通过
/// <para>文档定位:数据-标准图元-创建</para>
/// </summary>
/// <param name="idEM">:管理器ID</param>
/// <param name="nPen">:笔号</param>
/// <param name="strBmpFile">:文件路径</param>
/// <param name="nBmpAttrib">:位图属性.详细请参见附录</param>
/// <param name="nScanAttrib">:扫描参数,详细请参见附录</param>
/// <param name="ptBase">:工作空间中XY左下脚位置</param>
/// <param name="reserved1">:预留接口.默认值:flase</param>
/// <param name="reserved2">:预留接口.默认值:flase</param>
/// <param name="reserved3">:预留接口.默认值:""</param>
typedef E3_ERR (*e3_CreateBitmap)(E3_ID idEM,int nPen,TCHAR* strBmpFile,int nBmpAttrib,int nScanAttrib,Pt2d ptBase,BOOL reserved1,BOOL reserved2,TCHAR* reserved3);

/// <summary>
/// <para>API编码:[50941709]</para>
/// 接口说明:将位图文件添加到管理器中. 支持BMP,JPG,JPEG,GIF,TGA,PNG,TIF,TIFF. *上述支持类型在Windows版本系统上测试通过
/// <para>文档定位:数据-标准图元-创建</para>
/// </summary>
/// <param name="idEM">:管理器ID</param>
/// <param name="nPen">:笔号</param>
/// <param name="strBmpFile">:文件路径</param>
/// <param name="nBmpAttrib">:位图属性.详细请参见附录</param>
/// <param name="nScanAttrib">:扫描参数,详细请参见附录</param>
/// <param name="ptBase">:工作空间中XY左下脚位置</param>
/// <param name="bUpdateParentInfo">:是否更新列表信息</param>
/// <param name="idNewEnt">:返回添加对象ID</param>
typedef E3_ERR (*e3_CreateBitmap_2)(E3_ID idEM,int nPen,TCHAR* strBmpFile,int nBmpAttrib,int nScanAttrib,Pt2d ptBase,BOOL bUpdateParentInfo,E3_ID& idNewEnt);

/// <summary>
/// <para>API编码:[23385706]</para>
/// 接口说明:创建对象管理器,管理器为软件运行的容器，标准软件中设置对象为mm，若此接口设置为英寸，对象尺寸会由mm转化为英寸
/// <para>文档定位:环境-初始化以及释放</para>
/// </summary>
/// <param name="nUnitType">:创建对象管理器的单位=.0单位为毫米，=1单位为英寸</param>
typedef E3_ID (*e3_CreateEntMgr)(int nUnitType);

/// <summary>
/// <para>API编码:[21346364]</para>
/// 接口说明:在调用E3_Initial前有效.可以使用此函数设置是否弹出控制卡丢失的对话框,调用此函数即不显示弹框
/// <para>文档定位:环境-初始化以及释放</para>
/// </summary>
typedef void (*e3_DisableInitialPrompt)();

/// <summary>
/// <para>API编码:[76596691]</para>
/// 接口说明:显示填充进度条
/// <para>文档定位:数据-填充相关</para>
/// </summary>
/// <param name="b">:是否使能</param>
typedef E3_ERR (*e3_EnableShowHatchProcess)(BOOL b);

/// <summary>
/// <para>API编码:[97609081]</para>
/// 接口说明:得到指定图层指定索引的对象id
/// <para>文档定位:数据-对象操作-对象ID关系</para>
/// </summary>
/// <param name="idLayer">:图层ID</param>
/// <param name="nEntIndex">:要获取对象ID的对象索引号</param>
/// <param name="idEnt">:返回的对象ID</param>
typedef E3_ERR (*e3_FindEntInLayerByIndex)(E3_ID idLayer,int nEntIndex,E3_ID& idEnt);

/// <summary>
/// <para>API编码:[51828854]</para>
/// 接口说明:得到指定图层指定对象名称的id
/// <para>文档定位:数据-对象操作-对象ID关系</para>
/// </summary>
/// <param name="idLayer">:图层ID</param>
/// <param name="strEntName">:对象的名称</param>
/// <param name="idEnt">:返回的对象ID</param>
typedef E3_ERR (*e3_FindEntInLayerByName)(E3_ID idLayer,TCHAR* strEntName,E3_ID& idEnt);

/// <summary>
/// <para>API编码:[13797725]</para>
/// 接口说明:释放对象管理器
/// <para>文档定位:环境-初始化以及释放</para>
/// </summary>
/// <param name="idEM">:管理器ID</param>
typedef E3_ERR (*e3_FreeEntMgr)(E3_ID idEM);

/// <summary>
/// <para>API编码:[01389431]</para>
/// 接口说明:得到指定对象的预览图片
/// <para>文档定位:数据-对象操作-对象间操作</para>
/// </summary>
/// <param name="idEnt">:对象ID</param>
/// <param name="nParam">:为0即可</param>
/// <param name="bmpwidth">:窗口的像素宽</param>
/// <param name="bmpheight">:窗口的像素高</param>
/// <param name="dLogOriginX">:窗口的左下角对应点的x向逻辑坐标</param>
/// <param name="dLogOriginY">:窗口的左下角对应点的y向逻辑坐标</param>
/// <param name="dLogScale">:窗口对应的逻辑尺寸与窗口像素尺寸的比例</param>
typedef int (*e3_GetEntBitmap)(E3_ID idEnt,int nParam,int bmpwidth,int bmpheight,double dLogOriginX,double dLogOriginY,double dLogScale);

/// <summary>
/// <para>API编码:[00290942]</para>
/// 接口说明:获取加工参数库中的参数的数量
/// <para>文档定位:数据-笔参数相关</para>
/// </summary>
/// <param name="nCount">:返回参数的数量</param>
typedef E3_ERR (*e3_GetParamLibCount)(int& nCount);

/// <summary>
/// <para>API编码:[89145991]</para>
/// 接口说明:获取加工参数库中的指定位置的参数名
/// <para>文档定位:数据-笔参数相关</para>
/// </summary>
/// <param name="nIndex">:将要获取参数名的从0开始的下标</param>
/// <param name="strName[256]">:获取到对应下标参数的参数名</param>
typedef E3_ERR (*e3_GetParamLibName)(int nIndex,TCHAR strName[256]);

/// <summary>
/// <para>API编码:[59069335]</para>
/// 接口说明:得到激光扩展输出口索引
/// <para>文档定位:硬件-资源-激光-配置</para>
/// </summary>
/// <param name="idEM">:管理器ID</param>
/// <param name="nPenNo">:笔号</param>
/// <param name="_nLasetExtOutputIndex">:扩展输出口索引</param>
typedef E3_ERR (*e3_GetPenParamExtOutputIndex)(E3_ID idEM,int nPenNo,int& _nLasetExtOutputIndex);

/// <summary>
/// <para>API编码:[11534671]</para>
/// 接口说明:得到频率渐变参数
/// <para>文档定位:数据-笔参数相关</para>
/// </summary>
/// <param name="idEM">:管理器ID</param>
/// <param name="nPenNo">:笔号</param>
/// <param name="bAccSegEnable">:使能起始</param>
/// <param name="dAccSegStartRatio">:起始比例</param>
/// <param name="dAccSegLen">:起始长度;起始频率渐变的长度</param>
/// <param name="bDecSegEnable">:使能结束</param>
/// <param name="dDecSegStartRatio">:结束频率比例%;实际频率为当前加工参数频率乘此百分比</param>
/// <param name="dDecSegLen">:结束长度;结束频率渐变的长度</param>
typedef E3_ERR (*e3_GetPenParamFreqRamp)(E3_ID idEM,int nPenNo,BOOL& bAccSegEnable,double& dAccSegStartRatio,double& dAccSegLen,BOOL& bDecSegEnable,double& dDecSegStartRatio,double& dDecSegLen);

/// <summary>
/// <para>API编码:[56708316]</para>
/// 接口说明:得到指定笔号的激光滞后时间
/// <para>文档定位:数据-笔参数相关</para>
/// </summary>
/// <param name="idEM">:管理器ID</param>
/// <param name="nPenNo">:笔号</param>
/// <param name="bEnable">:是否使能激光滞后时间</param>
/// <param name="nTimeUs">:激光滞后时间us</param>
typedef E3_ERR (*e3_GetPenParamLaserLagTime)(E3_ID idEM,int nPenNo,BOOL& bEnable,int& nTimeUs);

/// <summary>
/// <para>API编码:[89121745]</para>
/// 接口说明:得到功率渐变参数
/// <para>文档定位:数据-笔参数相关</para>
/// </summary>
/// <param name="idEM">:管理器ID</param>
/// <param name="nPenNo">:笔号</param>
/// <param name="bAccSegEnable">:使能起始</param>
/// <param name="dAccSegStartRatio">:实际出光功率为当前加工参数功率乘此百分比</param>
/// <param name="dAccSegLen">:起始长度;起始功率渐变的长度</param>
/// <param name="bDecSegEnable">:使能结束</param>
/// <param name="dDecSegStartRatio">:结束功率比例%;实际出光功率为当前加工参数功率乘此百分比</param>
/// <param name="dDecSegLen">:结束长度;结束功率渐变的长度</param>
typedef E3_ERR (*e3_GetPenParamPowerRamp)(E3_ID idEM,int nPenNo,BOOL& bAccSegEnable,double& dAccSegStartRatio,double& dAccSegLen,BOOL& bDecSegEnable,double& dDecSegStartRatio,double& dDecSegLen);

/// <summary>
/// <para>API编码:[50713168]</para>
/// 接口说明:获取匀速笔标刻参数
/// <para>文档定位:数据-笔参数相关</para>
/// </summary>
/// <param name="idEM">:管理器ID</param>
/// <param name="nPenNo">:笔号</param>
/// <param name="bSkyWrite">:使能</param>
/// <param name="nSkyWriteMode">:匀速模式</param>
/// <param name="dSkyWriteLimitAngle">:极限角度</param>
/// <param name="nSkyWriteNprev">:导入周期.默认10us</param>
/// <param name="nSkyWriteNpost">:导出周期.默认10us</param>
/// <param name="dSkyWriteTimelag">:滞后时间us</param>
/// <param name="nSkyWriteLaserOnShift">:漂移时间us</param>
typedef E3_ERR (*e3_GetPenParamSkyWriting)(E3_ID idEM,int nPenNo,BOOL& bSkyWrite,int& nSkyWriteMode,double& dSkyWriteLimitAngle,int& nSkyWriteNprev,int& nSkyWriteNpost,double& dSkyWriteTimelag,int& nSkyWriteLaserOnShift);

/// <summary>
/// <para>API编码:[33388533]</para>
/// 接口说明:得到速度渐变参数
/// <para>文档定位:数据-笔参数相关</para>
/// </summary>
/// <param name="idEM">:管理器ID</param>
/// <param name="nPenNo">:笔号</param>
/// <param name="bAccSegEnable">:使能起始</param>
/// <param name="dAccSegStartRatio">:起始速度比例%;实际振镜摆动为当前加工参数速度乘此百分比</param>
/// <param name="dAccSegLen">:起始长度;起始速度渐变的长度</param>
/// <param name="bDecSegEnable">:使能结束</param>
/// <param name="dDecSegStartRatio">:结束比例%;实际振镜摆动速度为当前加工参数速度乘此百分比</param>
/// <param name="dDecSegLen">:结束长度;结束速度渐变的长度</param>
typedef E3_ERR (*e3_GetPenParamSpeedRamp)(E3_ID idEM,int nPenNo,BOOL& bAccSegEnable,double& dAccSegStartRatio,double& dAccSegLen,BOOL& bDecSegEnable,double& dDecSegStartRatio,double& dDecSegLen);

/// <summary>
/// <para>API编码:[13651106]</para>
/// 接口说明:获取步距标刻参数
/// <para>文档定位:数据-笔参数相关</para>
/// </summary>
/// <param name="idEM">:管理器ID</param>
/// <param name="nPenNo">:笔号</param>
/// <param name="bEnableStepMode">:步距模式</param>
/// <param name="dMarkStep">:优化长度</param>
typedef E3_ERR (*e3_GetPenParamStep)(E3_ID idEM,int nPenNo,BOOL& bEnableStepMode,double& dMarkStep);

/// <summary>
/// <para>API编码:[55255427]</para>
/// 接口说明:获取QCW波形输出
/// <para>文档定位:数据-笔参数相关</para>
/// </summary>
/// <param name="idEM">:管理器ID</param>
/// <param name="nPenNo">:笔号</param>
/// <param name="dWeldWavePower">:功率（每个功率[0,100]）</param>
/// <param name="dWeldWaveWidthMs">:脉宽（ms）(64个脉宽值的和不可超过笔参数中设置的总脉宽);[0,63]</param>
typedef E3_ERR (*e3_GetPenParamWeldWave)(E3_ID idEM,int nPenNo,double* dWeldWavePower,double* dWeldWaveWidthMs);

/// <summary>
/// <para>API编码:[72576032]</para>
/// 接口说明:获取QCW波形输出（与不带2的相比多了是否使能连续模式及是否使能波形输出两个参数）.
/// <para>文档定位:数据-笔参数相关</para>
/// </summary>
/// <param name="idEM">:管理器ID</param>
/// <param name="nPenNo">:笔号</param>
/// <param name="bLaserContMode">:是否使能连续模式（true为使能）</param>
/// <param name="bEnableWeldWave">:是否使能波形输出(true为使能)</param>
/// <param name="nMaxCount">:波形输出最大组数;[0,63]</param>
/// <param name="dWeldWavePower">:功率（每个功率[0,100]）</param>
/// <param name="dWeldWaveWidthMs">:脉宽（ms）(64个脉宽值的和不可超过笔参数中设置的总脉宽);[0,63]</param>
typedef E3_ERR (*e3_GetPenParamWeldWave2)(E3_ID idEM,int nPenNo,BOOL& bLaserContMode,BOOL& bEnableWeldWave,int& nMaxCount,double* dWeldWavePower,double* dWeldWaveWidthMs);

/// <summary>
/// <para>API编码:[19400799]</para>
/// 接口说明:获取抖动参数
/// <para>文档定位:数据-笔参数相关</para>
/// </summary>
/// <param name="idEM">:管理器ID</param>
/// <param name="nPenNo">:笔号</param>
/// <param name="bWobbleMode">:使能抖动</param>
/// <param name="nWobbleType">:抖动类型(5种：分别为螺旋线，正弦曲线，椭圆，垂直8字，水平8字)</param>
/// <param name="dWobbleDiameter">:直径mm</param>
/// <param name="dWobbleDiameterB">:抖动直径2 (mm)</param>
/// <param name="dWobbleDist">:抖动距离 mm</param>
typedef E3_ERR (*e3_GetPenParamWobble)(E3_ID idEM,int nPenNo,BOOL& bWobbleMode,int& nWobbleType,double& dWobbleDiameter,double& dWobbleDiameterB,double& dWobbleDist);

/// <summary>
/// <para>API编码:[44967736]</para>
/// 接口说明:获取抖动的相对速度
/// <para>文档定位:数据-笔参数相关</para>
/// </summary>
/// <param name="idEM">:管理器ID</param>
/// <param name="nPenNo">:笔号</param>
/// <param name="dWobbleIncSpeed">:抖动的相对速度</param>
typedef E3_ERR (*e3_GetPenParamWobbleIncSpeed)(E3_ID idEM,int nPenNo,double& dWobbleIncSpeed);

/// <summary>
/// <para>API编码:[06231488]</para>
/// 接口说明:初始化开发库
/// <para>文档定位:环境-初始化以及释放</para>
/// </summary>
/// <param name="strWorkPath">:Ezcad3.exe所处的目录的全路径名称，例如C:\WorkBook\20180528\EzCAD3\Debug</param>
/// <param name="nFlag">:否是测试模式,默认0</param>
typedef E3_ERR (*e3_Initial)(TCHAR* strWorkPath,int nFlag);

/// <summary>
/// <para>API编码:[30913458]</para>
/// 接口说明:监视USB-关闭设备检测
/// <para>文档定位:环境-初始化以及释放</para>
/// </summary>
typedef E3_ERR (*e3_MarkerCloseUsbMonitor)();

/// <summary>
/// <para>API编码:[16692804]</para>
/// 接口说明:设置等待延时
/// <para>文档定位:硬件-组合动作-列表命令-对象级列表命令</para>
/// </summary>
/// <param name="idMarker">:控制卡ID</param>
/// <param name="us">:延时时间（单位：us）</param>
typedef E3_ERR (*e3_MarkerDelayUsToList)(E3_ID idMarker,double us);

/// <summary>
/// <para>API编码:[13101121]</para>
/// 接口说明:打开设备参数窗体.会弹出库中集成的参数设置窗体.进行对系统的参数设置
/// <para>文档定位:环境-控制卡-配置</para>
/// </summary>
/// <param name="idMarker">:控制卡ID</param>
/// <param name="bReturnOk">:是否修改设备参数(若点击确认返回true)</param>
typedef E3_ERR (*e3_MarkerDlgSetCfg)(E3_ID idMarker,BOOL& bReturnOk);

/// <summary>
/// <para>API编码:[70751330]</para>
/// 接口说明:得到F3参数double型参数值
/// <para>文档定位:环境-控制卡-配置</para>
/// </summary>
/// <param name="idMarker">:控制卡ID</param>
/// <param name="nIndex">:索引值</param>
/// <param name="dParam">:当前索引的double的参数值</param>
typedef E3_ERR (*e3_MarkerGetCfgParamDouble)(E3_ID idMarker,int nIndex,double& dParam);

/// <summary>
/// <para>API编码:[44416657]</para>
/// 接口说明:得到F3参数Int型参数值
/// <para>文档定位:环境-控制卡-配置</para>
/// </summary>
/// <param name="idMarker">:控制卡ID</param>
/// <param name="nIndex">:索引值</param>
/// <param name="nParam">:当前索引的Int的参数值</param>
typedef E3_ERR (*e3_MarkerGetCfgParamInt)(E3_ID idMarker,int nIndex,int& nParam);

/// <summary>
/// <para>API编码:[85205858]</para>
/// 接口说明:查看控制卡的关联对象管理器,此接口使用的前提为使用了[E3_MarkerSetEntMgr]接口
/// <para>文档定位:环境-控制卡-操作</para>
/// </summary>
/// <param name="idMarker">:控制卡ID</param>
/// <param name="idEM">:传出关联当前控制卡的管理器ID</param>
typedef E3_ERR (*e3_MarkerGetEntMgr)(E3_ID idMarker,E3_ID& idEM);

/// <summary>
/// <para>API编码:[52307060]</para>
/// 接口说明:获取有效的控制卡的ID,单卡设备仅需执行一次，多卡设备需要多次执行，直到返回0，每台计算机最多支持8张卡，没有找到控制卡，会得到虚拟的卡ID
/// <para>文档定位:环境-控制卡-操作</para>
/// </summary>
typedef E3_ID (*e3_MarkerGetFirstValidId)();

/// <summary>
/// <para>API编码:[89013925]</para>
/// 接口说明:监视USB-启动设备检测
/// <para>文档定位:环境-初始化以及释放</para>
/// </summary>
/// <param name="hWndMonitor">:当前窗体的句柄</param>
typedef E3_ERR (*e3_MarkerInitUsbMonitor2)(HWND hWndMonitor);

/// <summary>
/// <para>API编码:[34048802]</para>
/// 接口说明:振镜以指定速度运动到指定位置（可见标准软件F3参数中振镜移动）
/// <para>文档定位:硬件-资源-振镜-动作</para>
/// </summary>
/// <param name="idMarker">:控制卡ID</param>
/// <param name="x">:X坐标</param>
/// <param name="y">:Y坐标</param>
/// <param name="z">:Z坐标</param>
/// <param name="spd">:指定速度</param>
typedef E3_ERR (*e3_MarkerJumpTo)(E3_ID idMarker,double x,double y,double z,double spd);

/// <summary>
/// <para>API编码:[81185209]</para>
/// 接口说明:单独控制激光开关
/// <para>文档定位:硬件-资源-激光-动作</para>
/// </summary>
/// <param name="idMarker">:控制卡ID</param>
/// <param name="nPenNo">:笔号</param>
/// <param name="bOn">:激光开关true开</param>
typedef E3_ERR (*e3_MarkerLaserOn)(E3_ID idMarker,int nPenNo,BOOL bOn);

/// <summary>
/// <para>API编码:[40056189]</para>
/// 接口说明:列表直接出激光接口
/// <para>文档定位:硬件-组合动作-列表命令-节点级列表命令</para>
/// </summary>
/// <param name="idMarker">:控制卡ID</param>
/// <param name="bOn">:是否可以开激光（true为开激光）</param>
typedef E3_ERR (*e3_MarkerLaserOnToList)(E3_ID idMarker,BOOL bOn);

/// <summary>
/// <para>API编码:[54509179]</para>
/// 接口说明:待列表结束后执行清理与复位,列表流程必须. 放在[E3_MarkerWaitForFinish]接口之后,顺序不能错
/// <para>文档定位:硬件-组合动作-列表命令-列表过程命令</para>
/// </summary>
/// <param name="idMarker">:控制卡ID</param>
typedef E3_ERR (*e3_MarkerListEnd)(E3_ID idMarker);

/// <summary>
/// <para>API编码:[27869676]</para>
/// 接口说明:标刻准备. 开启列表，E3_MarkerStop接口会中断列表，若用列表需重新开启列表
/// <para>文档定位:硬件-加工动作-列表命令-列表过程命令</para>
/// </summary>
/// <param name="idMarker">:控制卡ID</param>
/// <param name="idEM">:管理器ID</param>
/// <param name="nFlag">:工作标识类型: 0x000000000 = 静态标刻; 0x000000002 = 红光指示; 0x000000400 =飞行标刻; 0x000002000 = 焊接模式; 0x000008000 =（只下发数据不加工）; 0x000200000 = 禁止飞行打标自动排序; 0x001000000 = 计算模式（用于预估加工时间）; 0x002000000 = 脱机模式;</param>
typedef E3_ERR (*e3_MarkerListReady)(E3_ID idMarker,E3_ID idEM,ListReadyMode nFlag);

/// <summary>
/// <para>API编码:[36257416]</para>
/// 接口说明:标刻或者红光预览指定对象. 标刻或者红光预览指定对象,与E3_MarkerGetFirstValidId获得板卡ID，E3_CreateEntMgr获得管理器ID，E3_FindEntInLayerByIndex获得指定对象ID配合使用，此接口红光指示时只是振镜摆动，若需出实际红光，可调用IO中设置输出口接口进行设置，红光是否显示轮廓可在程序同目录下的EZCAD3软件中进行设置，计算模式用于预估加工时间不会实际出光且记录标刻时间至板卡. 标刻接口是阻塞式,当标刻接口返回就代表加工完成,不过可能由于通讯等问题,状态变更会有一点点延时,但是并不明显.不过要考虑这一点,一般编写时会在标刻接口返回后在下一行加一个一毫秒的延时
/// <para>文档定位:硬件-资源-激光-动作</para>
/// </summary>
/// <param name="idMarker">:控制卡ID</param>
/// <param name="idEM">:管理器ID</param>
/// <param name="idEnt">:对象ID或层ID</param>
/// <param name="nMarkFlag">:工作标识类型:   0x0000       = 静态标刻;    0x0002       = 红光指示;   0x0400       = 飞行标刻;   0x000002000  = 焊接模式;   0x01000000   = 计算模式（用于预估加工时间）;   0x000008000  = 只下发数据不加工;</param>
/// <param name="nStartPartNum">:从第几个对象开始标刻</param>
/// <param name="nMaxPartCount">:标刻最大个数</param>
typedef E3_ERR (*e3_MarkerMarkEnt2)(E3_ID idMarker,E3_ID idEM,E3_ID idEnt,MarkEntMode nMarkFlag,int nStartPartNum,int nMaxPartCount);

/// <summary>
/// <para>API编码:[01404368]</para>
/// 接口说明:标刻指定对象，添加到列表，此接口需配合E3_MarkerListReady ,E3_MarkerListEnd, E3_MarkerWaitForFinish三个接口一起使用
/// <para>文档定位:硬件-组合动作-列表命令-对象级列表命令</para>
/// </summary>
/// <param name="idMarker">:控制卡ID</param>
/// <param name="idEnt">:对象ID或层ID</param>
typedef E3_ERR (*e3_MarkerMarkEntToList2)(E3_ID idMarker,E3_ID idEnt);

/// <summary>
/// <para>API编码:[16269043]</para>
/// 接口说明:按笔号标刻指定对象，添加到列表
/// <para>文档定位:硬件-组合动作-列表命令-对象级列表命令</para>
/// </summary>
/// <param name="idMarker">:控制卡ID</param>
/// <param name="idEnt">:对象ID或层ID</param>
/// <param name="nPenNo">:笔号</param>
typedef E3_ERR (*e3_MarkerMarkEntToListByPen)(E3_ID idMarker,E3_ID idEnt,int nPenNo);

/// <summary>
/// <para>API编码:[85883362]</para>
/// 接口说明:标刻一条2D曲线. 标刻一条指定参数的2D曲线，此接口需配合E3_MarkerListReady ,E3_MarkerListEnd, E3_MarkerWaitForFinish三个接口一起使用
/// <para>文档定位:数据-标准图元-创建</para>
/// </summary>
/// <param name="idMarker">:控制卡ID</param>
/// <param name="type">:保留,默认0</param>
/// <param name="pen">:笔号</param>
/// <param name="ptNum">:曲线顶点数</param>
/// <param name="nFlag">:0x0002 红光指示  0x0000 静态标刻 =0x0400飞行标刻</param>
/// <param name="ptBuf">:曲线顶点数组;ptBuf点坐标组；ptBuf[n,0]表示第n个点的x坐标，ptBuf[n,1]表示第n个点的y坐标,ptBuf[n,2]表示第n个点的z坐标</param>
typedef E3_ERR (*e3_MarkerOneCurveToList)(E3_ID idMarker,int type,int pen,int ptNum,ListReadyMode nFlag,Pt2d* ptBuf);

/// <summary>
/// <para>API编码:[35178069]</para>
/// 接口说明:读输入口. 在程序中调用此函数来读入当前输入端口的数据. Bit0是In0的状态,Bit0=1表示In0为高电平,Bit0=0表示In0为低电平. Bit1是In1的状态,Bit1=1表示In1为高电平,Bit1=0表示In1为低电平,依次类推. 如果获取值为5，表示IN0,IN2是高电平，其他端口都是低电平
/// <para>文档定位:硬件-资源-数字量IN-查询</para>
/// </summary>
/// <param name="idMarker">:控制卡ID</param>
/// <param name="data">:读取到的端入口值</param>
typedef E3_ERR (*e3_MarkerReadPort)(E3_ID idMarker,WORD& data);

/// <summary>
/// <para>API编码:[59779327]</para>
/// 接口说明:计数复位,复位列表计数的数目
/// <para>文档定位:硬件-资源-寄存器-写</para>
/// </summary>
/// <param name="idMarker">:控制卡ID</param>
typedef E3_ERR (*e3_MarkerResetMarkCount)(E3_ID idMarker);

/// <summary>
/// <para>API编码:[55511348]</para>
/// 接口说明:设置F3参数double型参数值
/// <para>文档定位:环境-控制卡-配置</para>
/// </summary>
/// <param name="idMarker">:控制卡ID</param>
/// <param name="nIndex">:索引值</param>
/// <param name="dParam">:当前索引的double的参数值</param>
typedef E3_ERR (*e3_MarkerSetCfgParamDouble)(E3_ID idMarker,int nIndex,double dParam);

/// <summary>
/// <para>API编码:[15491583]</para>
/// 接口说明:设置F3参数Int型参数值
/// <para>文档定位:环境-控制卡-配置</para>
/// </summary>
/// <param name="idMarker">:控制卡ID</param>
/// <param name="nIndex">:索引值</param>
/// <param name="nParam">:当前索引的Int的参数值</param>
typedef E3_ERR (*e3_MarkerSetCfgParamInt)(E3_ID idMarker,int nIndex,int nParam);

/// <summary>
/// <para>API编码:[81296136]</para>
/// 接口说明:给控制卡发送校正表
/// <para>文档定位:环境-控制卡-配置</para>
/// </summary>
/// <param name="idMarker">:控制卡ID</param>
/// <param name="szFileName[256]">:校正文件路径</param>
/// <param name="indexTable">:内校正表序号,范围: 1-4</param>
typedef E3_ERR (*e3_MarkerSetCorFile2)(E3_ID idMarker,TCHAR szFileName[256],int indexTable);

/// <summary>
/// <para>API编码:[80607194]</para>
/// 接口说明:关联控制卡与对象管理器,在不需要使用模板的情况下,直接控制激光器进行开关光,则需要使用此接口,一般在初始化成功之后调用即可
/// <para>文档定位:环境-控制卡-配置</para>
/// </summary>
/// <param name="idMarker">:控制卡ID</param>
/// <param name="idEM">:管理器ID</param>
typedef E3_ERR (*e3_MarkerSetEntMgr)(E3_ID idMarker,E3_ID idEM);

/// <summary>
/// <para>API编码:[83152820]</para>
/// 接口说明:设置F3参数string型参数值
/// <para>文档定位:环境-控制卡-配置</para>
/// </summary>
/// <param name="idMarker">:控制卡ID</param>
/// <param name="nParamId">:参数索引</param>
/// <param name="pParamStr">:该索引对应的字符串</param>
typedef E3_ERR (*e3_MarkerSetParamString)(E3_ID idMarker,int nParamId,TCHAR* pParamStr);

/// <summary>
/// <para>API编码:[65299578]</para>
/// 接口说明:监视USB-关闭设备检测
/// <para>文档定位:环境-初始化以及释放</para>
/// </summary>
/// <param name="idMarker">:获取到新的控制卡ID</param>
typedef E3_ERR (*e3_MarkerUsbMonitorGetNewDevice)(E3_ID& idMarker);

/// <summary>
/// <para>API编码:[82400246]</para>
/// 接口说明:删除参数库中对应名称的参数配置
/// <para>文档定位:数据-笔参数相关</para>
/// </summary>
/// <param name="strName">:参数配置的名称</param>
typedef E3_ERR (*e3_ParamLibDeleteName)(TCHAR* strName);

/// <summary>
/// <para>API编码:[11044294]</para>
/// 接口说明:更新保存给定笔号到对应参数名称的参数配置
/// <para>文档定位:数据-笔参数相关</para>
/// </summary>
/// <param name="idEM">:管理器ID</param>
/// <param name="nPenNo">:笔号</param>
/// <param name="strName">:参数配置的名称</param>
typedef E3_ERR (*e3_ParamLibSavePenToName)(E3_ID idEM,int nPenNo,TCHAR* strName);

/// <summary>
/// <para>API编码:[60153944]</para>
/// 接口说明:从参数库读取给定名称参数配置设置到给定的笔号
/// <para>文档定位:数据-笔参数相关</para>
/// </summary>
/// <param name="idEM">:管理器ID</param>
/// <param name="nPenNo">:笔号</param>
/// <param name="strName">:参数配置的名称</param>
typedef E3_ERR (*e3_ParamLibSetPenFromName)(E3_ID idEM,int nPenNo,TCHAR* strName);

/// <summary>
/// <para>API编码:[82265331]</para>
/// 接口说明:设置图像参数
/// <para>文档定位:数据-标准图元-编辑-位图类型</para>
/// </summary>
/// <param name="idEM">:管理器ID</param>
/// <param name="idEnt">:对象ID</param>
/// <param name="nParamBuf">:整形数据.这里的整形数组长度为50,其中每一位元都存储一个参数,通过设置这个数组来进行图像的修改</param>
/// <param name="dParamBuf">:这里的浮点型数组长度为8,其中每一位元都存储一个参数,通过设置这个数组来进行图像的修改</param>
/// <param name="bGrayScaleBuf">:灰度功率表.长度为256,默认数元值与下标一致,例如:     _grayTables[0] = (byte)0;     _grayTables[1] = (byte)1;     ......     _grayTables[255] = (byte)255;     如果想要呈现不同不同功率不同灰度效果,可以修改此数组,ezcad3中存在此功能,可在ezcad3中事先查看效果.之后用接口实现</param>
/// <param name="str1">:位图对象文件路径</param>
/// <param name="reserved1">:预留参数,默认false</param>
/// <param name="reserved2">:预留参数,默认""</param>
typedef E3_ERR (*e3_SetBmpFileInfo)(E3_ID idEM,E3_ID idEnt,int* nParamBuf,double* dParamBuf,BYTE* bGrayScaleBuf,TCHAR* str1,BOOL reserved1,TCHAR* reserved2);

/// <summary>
/// <para>API编码:[73078029]</para>
/// 接口说明:设置图像参数2
/// <para>文档定位:数据-标准图元-编辑-位图类型</para>
/// </summary>
/// <param name="idEM">:管理器ID</param>
/// <param name="idEnt">:对象ID</param>
/// <param name="nParamBuf">:整形数据.这里的整形数组长度为50,其中每一位元都存储一个参数,通过设置这个数组来进行图像的修改</param>
/// <param name="dParamBuf">:这里的浮点型数组长度为8,其中每一位元都存储一个参数,通过设置这个数组来进行图像的修改</param>
/// <param name="bGrayScaleBuf">:灰度功率表.长度为256,默认数元值与下标一致,例如:     _grayTables[0] = (byte)0;     _grayTables[1] = (byte)1;     ......     _grayTables[255] = (byte)255;     如果想要呈现不同不同功率不同灰度效果,可以修改此数组,ezcad3中存在此功能,可在ezcad3中事先查看效果.之后用接口实现</param>
/// <param name="str1">:位图对象文件路径</param>
typedef E3_ERR (*e3_SetBmpFileInfo_2)(E3_ID idEM,E3_ID idEnt,int* nParamBuf,double* dParamBuf,BYTE* bGrayScaleBuf,TCHAR* str1);

/// <summary>
/// <para>API编码:[66351540]</para>
/// 接口说明:设置软件读取语言文件.只对设备参数窗体语言生效，默认为英文
/// <para>文档定位:环境-初始化以及释放</para>
/// </summary>
/// <param name="strFile">:语言包路径</param>
typedef E3_ERR (*e3_SetLanguageFile)(TCHAR* strFile);

/// <summary>
/// <para>API编码:[55082481]</para>
/// 接口说明:设置笔参数
/// <para>文档定位:数据-笔参数相关</para>
/// </summary>
/// <param name="idEM">:管理器ID</param>
/// <param name="nPenNo">:笔号</param>
/// <param name="pStrName">:笔名称</param>
/// <param name="clr">:笔颜色</param>
/// <param name="bDisableMark">:使能</param>
/// <param name="bUseDefParam">:使用默认</param>
/// <param name="nMarkLoop">:加工次数</param>
/// <param name="dMarkSpeed">:标刻速度mm/s</param>
/// <param name="dPowerRatio">:功率%</param>
/// <param name="dCurrent">:电流A</param>
/// <param name="dFreq">:频率HZ</param>
/// <param name="dQPulseWidth">:脉冲宽度us|ns</param>
/// <param name="nStartTC">:开始延时us</param>
/// <param name="nLaserOffTC">:关闭延时us</param>
/// <param name="nEndTC">:结束延时us</param>
/// <param name="nPolyTC">:拐角延时us</param>
/// <param name="dJumpSpeed">:跳转速度mm/s</param>
/// <param name="nMinJumpDelayTCUs">:最小跳转延时us</param>
/// <param name="nMaxJumpDelayTCUs">:最大跳转延时us</param>
/// <param name="dJumpLengthLimit">:跳转长度极限mm</param>
/// <param name="dPointTimeMs">:打点时间ms</param>
/// <param name="nSpiSpiContinueMode">:SPI连续模式</param>
/// <param name="nSpiWave">:SPI波形选择</param>
/// <param name="nYagMarkMode">:YAG优化填充模式</param>
/// <param name="bPulsePointMode">:脉冲点模式</param>
/// <param name="nPulseNum">:脉冲点数</param>
/// <param name="bEnableACCMode">:使能加速模式</param>
/// <param name="dEndComp">:末点补偿</param>
/// <param name="dAccDist">:加速距离mm</param>
/// <param name="dBreakAngle">:中断角度(89)（弧度值）;已经被淘汰，暂时保留</param>
/// <param name="bWobbleMode">:抖动模式(false);已经升级，目前版本不再使用这个参数</param>
/// <param name="bWobbleDiameter">:抖动直径(1)mm;已经升级，目前版本不再使用这个参数</param>
/// <param name="bWobbleDist">:抖动距离(0.5)mm;已经升级，目前版本不再使用这个参数</param>
typedef E3_ERR (*e3_SetPenParam)(E3_ID idEM,int nPenNo,TCHAR* pStrName,int clr,BOOL bDisableMark,BOOL bUseDefParam,int nMarkLoop,double dMarkSpeed,double dPowerRatio,double dCurrent,double dFreq,double dQPulseWidth,int nStartTC,int nLaserOffTC,int nEndTC,int nPolyTC,double dJumpSpeed,int nMinJumpDelayTCUs,int nMaxJumpDelayTCUs,double dJumpLengthLimit,double dPointTimeMs,BOOL nSpiSpiContinueMode,int nSpiWave,int nYagMarkMode,BOOL bPulsePointMode,int nPulseNum,BOOL bEnableACCMode,double dEndComp,double dAccDist,double dBreakAngle,BOOL bWobbleMode,double bWobbleDiameter,double bWobbleDist);

/// <summary>
/// <para>API编码:[91206111]</para>
/// 接口说明:设置优化模式参数
/// <para>文档定位:数据-笔参数相关</para>
/// </summary>
/// <param name="idEM">:管理器ID</param>
/// <param name="nPenNo">:笔号</param>
/// <param name="bOpitmize">:使能优化模式</param>
/// <param name="dScanberBiDirOffset">:双向偏移</param>
/// <param name="dAccDist">:加速距离</param>
/// <param name="dEndDist">:末点补偿</param>
typedef E3_ERR (*e3_SetPenParamExt4)(E3_ID idEM,int nPenNo,BOOL bOpitmize,double dScanberBiDirOffset,double dAccDist,double dEndDist);

/// <summary>
/// <para>API编码:[79888088]</para>
/// 接口说明:设置笔参数数模块的焊接参数
/// <para>文档定位:数据-笔参数相关</para>
/// </summary>
/// <param name="idEM">:管理器ID</param>
/// <param name="nPenNo">:笔号</param>
/// <param name="nMarkLoop">:加工数目</param>
/// <param name="bAveragePtMode">:是否平均分布所有点（true为是）</param>
/// <param name="dPointDist">:点间距</param>
/// <param name="nPulseNum">:每点脉冲数</param>
typedef E3_ERR (*e3_SetPenParamExt5)(E3_ID idEM,int nPenNo,int nMarkLoop,BOOL bAveragePtMode,double dPointDist,int nPulseNum);

/// <summary>
/// <para>API编码:[14208434]</para>
/// 接口说明:设置激光扩展输出口索引
/// <para>文档定位:数据-笔参数相关</para>
/// </summary>
/// <param name="idEM">:管理器ID</param>
/// <param name="nPenNo">:笔号</param>
/// <param name="nLasetExtOutputIndex">:扩展输出口索引</param>
typedef E3_ERR (*e3_SetPenParamExtOutputIndex)(E3_ID idEM,int nPenNo,int nLasetExtOutputIndex);

/// <summary>
/// <para>API编码:[18689610]</para>
/// 接口说明:设置频率渐变参数
/// <para>文档定位:数据-笔参数相关</para>
/// </summary>
/// <param name="idEM">:管理器ID</param>
/// <param name="nPenNo">:笔号</param>
/// <param name="bAccSegEnable">:使能起始</param>
/// <param name="dAccSegStartRatio">:起始比例</param>
/// <param name="dAccSegLen">:起始长度;起始频率渐变的长度</param>
/// <param name="bDecSegEnable">:使能结束</param>
/// <param name="dDecSegStartRatio">:结束频率比例%;实际频率为当前加工参数频率乘此百分比</param>
/// <param name="dDecSegLen">:结束长度;结束频率渐变的长度</param>
typedef E3_ERR (*e3_SetPenParamFreqRamp)(E3_ID idEM,int nPenNo,BOOL bAccSegEnable,double dAccSegStartRatio,double dAccSegLen,BOOL bDecSegEnable,double dDecSegStartRatio,double dDecSegLen);

/// <summary>
/// <para>API编码:[39409173]</para>
/// 接口说明:设置指定笔号的激光滞后时间
/// <para>文档定位:数据-笔参数相关</para>
/// </summary>
/// <param name="idEM">:管理器ID</param>
/// <param name="nPenNo">:笔号</param>
/// <param name="bEnable">:是否使能激光滞后时间</param>
/// <param name="nTimeUs">:激光滞后时间us</param>
typedef E3_ERR (*e3_SetPenParamLaserLagTime)(E3_ID idEM,int nPenNo,BOOL bEnable,int nTimeUs);

/// <summary>
/// <para>API编码:[69830454]</para>
/// 接口说明:设置功率渐变参数
/// <para>文档定位:数据-笔参数相关</para>
/// </summary>
/// <param name="idEM">:管理器ID</param>
/// <param name="nPenNo">:笔号</param>
/// <param name="bAccSegEnable">:使能起始</param>
/// <param name="dAccSegStartRatio">:实际出光功率为当前加工参数功率乘此百分比</param>
/// <param name="dAccSegLen">:起始长度;起始功率渐变的长度</param>
/// <param name="bDecSegEnable">:使能结束</param>
/// <param name="dDecSegStartRatio">:结束功率比例%;实际出光功率为当前加工参数功率乘此百分比</param>
/// <param name="dDecSegLen">:结束长度;结束功率渐变的长度</param>
typedef E3_ERR (*e3_SetPenParamPowerRamp)(E3_ID idEM,int nPenNo,BOOL bAccSegEnable,double dAccSegStartRatio,double dAccSegLen,BOOL bDecSegEnable,double dDecSegStartRatio,double dDecSegLen);

/// <summary>
/// <para>API编码:[42859443]</para>
/// 接口说明:设置匀速笔标刻参数
/// <para>文档定位:数据-笔参数相关</para>
/// </summary>
/// <param name="idEM">:管理器ID</param>
/// <param name="nPenNo">:笔号</param>
/// <param name="bSkyWrite">:使能</param>
/// <param name="nSkyWriteMode">:匀速模式</param>
/// <param name="dSkyWriteLimitAngle">:极限角度</param>
/// <param name="nSkyWriteNprev">:导入周期.默认10us</param>
/// <param name="nSkyWriteNpost">:导出周期.默认10us</param>
/// <param name="dSkyWriteTimelag">:滞后时间us</param>
/// <param name="nSkyWriteLaserOnShift">:漂移时间us</param>
typedef E3_ERR (*e3_SetPenParamSkyWriting)(E3_ID idEM,int nPenNo,BOOL bSkyWrite,int nSkyWriteMode,double dSkyWriteLimitAngle,int nSkyWriteNprev,int nSkyWriteNpost,double dSkyWriteTimelag,int nSkyWriteLaserOnShift);

/// <summary>
/// <para>API编码:[48941785]</para>
/// 接口说明:设置速度渐变参数
/// <para>文档定位:数据-笔参数相关</para>
/// </summary>
/// <param name="idEM">:管理器ID</param>
/// <param name="nPenNo">:笔号</param>
/// <param name="bAccSegEnable">:使能起始</param>
/// <param name="dAccSegStartRatio">:起始速度比例%;实际振镜摆动为当前加工参数速度乘此百分比</param>
/// <param name="dAccSegLen">:起始长度;起始速度渐变的长度</param>
/// <param name="bDecSegEnable">:使能结束</param>
/// <param name="dDecSegStartRatio">:结束比例%;实际振镜摆动速度为当前加工参数速度乘此百分比</param>
/// <param name="dDecSegLen">:结束长度;结束速度渐变的长度</param>
typedef E3_ERR (*e3_SetPenParamSpeedRamp)(E3_ID idEM,int nPenNo,BOOL bAccSegEnable,double dAccSegStartRatio,double dAccSegLen,BOOL bDecSegEnable,double dDecSegStartRatio,double dDecSegLen);

/// <summary>
/// <para>API编码:[15439842]</para>
/// 接口说明:设置步距标刻参数
/// <para>文档定位:数据-笔参数相关</para>
/// </summary>
/// <param name="idEM">:管理器ID</param>
/// <param name="nPenNo">:笔号</param>
/// <param name="bEnableStepMode">:步距模式</param>
/// <param name="dMarkStep">:优化长度</param>
typedef E3_ERR (*e3_SetPenParamStep)(E3_ID idEM,int nPenNo,BOOL bEnableStepMode,double dMarkStep);

/// <summary>
/// <para>API编码:[93238538]</para>
/// 接口说明:设置QCW波形输出
/// <para>文档定位:数据-笔参数相关</para>
/// </summary>
/// <param name="idEM">:管理器ID</param>
/// <param name="nPenNo">:笔号</param>
/// <param name="dWeldWavePower">:功率（每个功率[0,100]）</param>
/// <param name="dWeldWaveWidthMs">:脉宽（ms）(64个脉宽值的和不可超过笔参数中设置的总脉宽);[0,63]</param>
typedef E3_ERR (*e3_SetPenParamWeldWave)(E3_ID idEM,int nPenNo,double* dWeldWavePower,double* dWeldWaveWidthMs);

/// <summary>
/// <para>API编码:[54255338]</para>
/// 接口说明:设置QCW波形输出,E3_SetPenParamWeldWave的参数扩展.
/// <para>文档定位:数据-笔参数相关</para>
/// </summary>
/// <param name="idEM">:管理器ID</param>
/// <param name="nPenNo">:笔号</param>
/// <param name="bLaserContMode">:是否使能连续模式（true为使能）</param>
/// <param name="bEnableWeldWave">:是否使能波形输出(true为使能)</param>
/// <param name="nMaxCount">:波形输出最大组数;[0,63]</param>
/// <param name="dWeldWavePower">:功率（每个功率[0,100]）</param>
/// <param name="dWeldWaveWidthMs">:脉宽（ms）(64个脉宽值的和不可超过笔参数中设置的总脉宽);[0,63]</param>
typedef E3_ERR (*e3_SetPenParamWeldWave2)(E3_ID idEM,int nPenNo,BOOL bLaserContMode,BOOL bEnableWeldWave,int nMaxCount,double* dWeldWavePower,double* dWeldWaveWidthMs);

/// <summary>
/// <para>API编码:[99975243]</para>
/// 接口说明:设置抖动参数
/// <para>文档定位:数据-笔参数相关</para>
/// </summary>
/// <param name="idEM">:管理器ID</param>
/// <param name="nPenNo">:笔号</param>
/// <param name="bWobbleMode">:使能抖动</param>
/// <param name="nWobbleType">:抖动类型(5种：分别为螺旋线，正弦曲线，椭圆，垂直8字，水平8字)</param>
/// <param name="dWobbleDiameter">:直径mm</param>
/// <param name="dWobbleDiameterB">:抖动直径2 (mm)</param>
/// <param name="dWobbleDist">:抖动距离 mm</param>
typedef E3_ERR (*e3_SetPenParamWobble)(E3_ID idEM,int nPenNo,BOOL bWobbleMode,int nWobbleType,double dWobbleDiameter,double dWobbleDiameterB,double dWobbleDist);

/// <summary>
/// <para>API编码:[01564414]</para>
/// 接口说明:设置抖动的相对速度
/// <para>文档定位:数据-笔参数相关</para>
/// </summary>
/// <param name="idEM">:管理器ID</param>
/// <param name="nPenNo">:笔号</param>
/// <param name="dWobbleIncSpeed">:抖动的相对速度</param>
typedef E3_ERR (*e3_SetPenParamWobbleIncSpeed)(E3_ID idEM,int nPenNo,double dWobbleIncSpeed);

/// <summary>
/// <para>API编码:[12265534]</para>
/// 接口说明:获取所有的字体数
/// <para>文档定位:环境-字库管理</para>
/// </summary>
/// <param name="nFontCount">:字体总数（包括TTF,JSF，条码……）</param>
typedef E3_ERR (*e3_GetAllFontCount)(int& nFontCount);

/// <summary>
/// <para>API编码:[17802958]</para>
/// 接口说明:获取在所有字体中指定位置的字体记录
/// <para>文档定位:环境-字库管理</para>
/// </summary>
/// <param name="id">:在字体总数中的字体位置</param>
/// <param name="strName">:字体名</param>
/// <param name="attrib">:字体属性，JSF(attrib&0x1001)!=0  TTF(attrib&0x02)!=0 点阵DMF(attrib&0x04)!=0  条码BCF(attrib&0x08)!=0 SHX(attrib&0x10)!=0</param>
typedef E3_ERR (*e3_GetAllFontRecord)(int id,TCHAR* strName,unsigned short& attrib);

/// <summary>
/// <para>API编码:[71980031]</para>
/// 接口说明:根据层ID得到当前层的stl模型尺寸
/// <para>文档定位:数据-显示-3D显示</para>
/// </summary>
/// <param name="idLayer">:图层ID</param>
/// <param name="minx">:Stl模型的左下角X坐标</param>
/// <param name="miny">:Stl模型的左下角Y坐标</param>
/// <param name="maxx">:Stl模型的右上角X坐标</param>
/// <param name="maxy">:Stl模型的右上角Y坐标</param>
/// <param name="minz">:Stl模型的最小Z坐标</param>
/// <param name="maxz">:Stl模型的最大Z坐标</param>
typedef E3_ERR (*e3_GetMeshSize)(E3_ID idLayer,double& minx,double& miny,double& maxx,double& maxy,double& minz,double& maxz);

/// <summary>
/// <para>API编码:[04546726]</para>
/// 接口说明:是否开启振镜补偿，关闭时，振镜标刻和流水线移动无关
/// <para>文档定位:硬件-加工动作-列表命令-列表过程命令</para>
/// </summary>
/// <param name="idMarker">:板卡ID</param>
/// <param name="bEnableFlyX">:使能x</param>
/// <param name="bEnableFlyY">:使能y</param>
typedef E3_ERR (*e3_MarkerEnableFlyCorrectionToList)(E3_ID idMarker,BOOL bEnableFlyX,BOOL bEnableFlyY);

/// <summary>
/// <para>API编码:[40029126]</para>
/// 接口说明:设置飞行模拟速度，无编码器时必须执行这个，F3中的是设置不能直接执行
/// <para>文档定位:硬件-组合动作-动作指令</para>
/// </summary>
/// <param name="idMarker">:板卡ID</param>
/// <param name="bEnableSimuFly">:是否使能模拟，直接修改了cfg参数</param>
/// <param name="dSpeedX">:模拟速度</param>
typedef E3_ERR (*e3_MarkerSetFlySimuSpeed)(E3_ID idMarker,BOOL bEnableSimuFly,double dSpeedX);

/// <summary>
/// <para>API编码:[73417617]</para>
/// 接口说明:清除在标刻过程中接到的IO信号，在等待IO信号前设置，可避免误触发
/// <para>文档定位:硬件-组合动作-动作指令</para>
/// </summary>
/// <param name="idMarker">:板卡ID</param>
/// <param name="nPort">:端口值</param>
typedef E3_ERR (*e3_MarkerClearWaitForInputLock)(E3_ID idMarker,int nPort);

/// <summary>
/// <para>API编码:[42475852]</para>
/// 接口说明:使能飞行，如果飞行标刻，需F3参数使能飞行，E3_MarkerListReady里设置飞行状态，并使能飞行
/// <para>文档定位:硬件-加工动作-列表命令-列表过程命令</para>
/// </summary>
/// <param name="idMarker">:板卡ID</param>
/// <param name="b">:使能</param>
typedef E3_ERR (*e3_MarkerFlyEnableToList)(E3_ID idMarker,BOOL b);

/// <summary>
/// <para>API编码:[07723568]</para>
/// 接口说明:清除流水线（飞行）补偿，清除前必须用E3_MarkerFlyEnableToList关闭飞行，不然有可能清除失败
/// <para>文档定位:硬件-组合动作-列表命令-列表过程命令</para>
/// </summary>
/// <param name="idMarker">:板卡ID</param>
typedef E3_ERR (*e3_MarkerFlyResetDistanceToList)(E3_ID idMarker);

/// <summary>
/// <para>API编码:[17984852]</para>
/// 接口说明:飞行等待距离
/// <para>文档定位:硬件-组合动作-列表命令-列表过程命令</para>
/// </summary>
/// <param name="idMarker">:板卡ID</param>
/// <param name="dFlyDist">:等距的距离，与飞行补偿对应</param>
/// <param name="bIsFollowAvail">:在等待过程中振镜是否跟随流水线移动</param>
typedef E3_ERR (*e3_MarkerFlyWaitForDistToList)(E3_ID idMarker,double dFlyDist,BOOL bIsFollowAvail);

/// <summary>
/// <para>API编码:[51684669]</para>
/// 接口说明:获取编码器脉冲数
/// <para>文档定位:硬件-组合动作-动作指令</para>
/// </summary>
/// <param name="idMarker">:板卡ID</param>
/// <param name="index">:编码器，1为X,2为Y</param>
/// <param name="nCount">:返回的编码器脉冲数</param>
typedef E3_ERR (*e3_MarkerGetFlyEncoder)(E3_ID idMarker,int index,unsigned int& nCount);

/// <summary>
/// <para>API编码:[88602152]</para>
/// 接口说明:获取流水线速度
/// <para>文档定位:硬件-组合动作-动作指令</para>
/// </summary>
/// <param name="idMarker">:板卡ID</param>
/// <param name="index">:编码器，1为X,2为Y</param>
/// <param name="dSpeed">:速度</param>
typedef E3_ERR (*e3_MarkerGetSpeedOfFly)(E3_ID idMarker,int index,double& dSpeed);

/// <summary>
/// <para>API编码:[08667501]</para>
/// 接口说明:获取当前输出口的状态值
/// <para>文档定位:硬件-资源-数字量OUT-查询</para>
/// </summary>
/// <param name="idMarker">:板卡ID</param>
/// <param name="data">:输出口的值</param>
typedef E3_ERR (*e3_MarkerGetWritePort)(E3_ID idMarker,WORD& data);

/// <summary>
/// <para>API编码:[69969995]</para>
/// 接口说明:清除振镜补偿，在清除前需要用E3_MarkerEnableFlyCorrectionToList关闭使能
/// <para>文档定位:硬件-资源-数字量OUT-查询</para>
/// </summary>
/// <param name="idMarker">:板卡ID</param>
/// <param name="bResetX">:使能x方向清除</param>
/// <param name="bResetY">:使能y方向清除</param>
typedef E3_ERR (*e3_MarkerResetDistanceToList)(E3_ID idMarker,BOOL bResetX,BOOL bResetY);

/// <summary>
/// <para>API编码:[90771974]</para>
/// 接口说明:设置输出口，掩码模式. 当mask参数的bit为1时,则设置这个bit的端口被打开,默认是低电平输出. 当data参数的bit为1时,则设置对应的端口以高电平模式输出,其余不为1的bit,则默认低电平输出.
/// <para>文档定位:硬件-资源-数字量OUT-动作</para>
/// </summary>
/// <param name="idMarker">:板卡ID</param>
/// <param name="wPortMask">:输出口掩码</param>
/// <param name="wPortLevel">:设置的输出口值</param>
typedef E3_ERR (*e3_MarkerSetOutputPortWithMask)(E3_ID idMarker,WORD wPortMask,WORD wPortLevel);

/// <summary>
/// <para>API编码:[05422563]</para>
/// 接口说明:设置输出口，只有掩码上的设置有效，list命令
/// <para>文档定位:硬件-资源-数字量OUT-动作</para>
/// </summary>
/// <param name="idMarker">:板卡ID</param>
/// <param name="wPortMask">:端口掩码:1有效,0无效;</param>
/// <param name="wPortLevel">:目标值:1高,0低;</param>
typedef E3_ERR (*e3_MarkerSetOutputPortWithMaskToList)(E3_ID idMarker,WORD wPortMask,WORD wPortLevel);

/// <summary>
/// <para>API编码:[55675362]</para>
/// 接口说明:设置系统对于输入口的处理模式,是否是脉冲模式,是否是高低电平有效,通过此接口设定.支持动态设置,但不支持运行中设置(运行中代表开启了列表或调用了Markent2)
/// <para>文档定位:硬件-资源-数字量IN-配置</para>
/// </summary>
/// <param name="idMarker">:板卡ID</param>
/// <param name="bPulseMode">:是否是脉冲信号</param>
/// <param name="bLowVaild">:脉冲模式，true下降沿，false上升沿。电平模式，true低电平，false高电平</param>
typedef E3_ERR (*e3_SetInputPortWorkMode)(E3_ID idMarker,BOOL bPulseMode,BOOL bLowVaild);

/// <summary>
/// <para>API编码:[97652297]</para>
/// 接口说明:把文本对象分离成字符对象,添加到idEntParent容器对象的尾部. 一般的idEntParent为图层ID,但是也可以传入对象ID,但对象ID必须为群组对象,如果是群组对象会将分离后的文本对象添加到群组对象子对象的尾部.
/// <para>文档定位:数据-标准图元-编辑-文本类型-文本</para>
/// </summary>
/// <param name="idEnt">:对象ID</param>
/// <param name="idEntParent">:分离对象添加到的父对象ID</param>
/// <param name="bTextLeftToRight">:分离字符的方式，false从右到左，true从左到右</param>
/// <param name="dArcTol">:曲线离散成直线的误差</param>
typedef E3_ERR (*e3_SplitTextToChars)(E3_ID idEnt,E3_ID idEntParent,BOOL bTextLeftToRight,double dArcTol);

/// <summary>
/// <para>API编码:[49432465]</para>
/// 接口说明:读取license信息
/// <para>文档定位:环境-激活码</para>
/// </summary>
/// <param name="BYTEInfo[10240]">:</param>
typedef E3_ERR (*e3_BitGetInfo)(BYTE BYTEInfo[10240]);

/// <summary>
/// <para>API编码:[94893641]</para>
/// 接口说明:将对象转为曲线
/// <para>文档定位:数据-对象操作-对象间操作</para>
/// </summary>
/// <param name="idEnt">:对象ID</param>
/// <param name="nParamFlag">:默认0</param>
/// <param name="bDeleteOldEnt">:是否删除旧曲线</param>
/// <param name="idNewCurveEnt">:转换后的曲线组</param>
typedef E3_ERR (*e3_ChangeEntToCurve)(E3_ID idEnt,int nParamFlag,BOOL bDeleteOldEnt,E3_ID& idNewCurveEnt);

/// <summary>
/// <para>API编码:[30609132]</para>
/// 接口说明:获取指定文本对象的字体类型，以及是否是条码
/// <para>文档定位:数据-标准图元-编辑-文本类型-条码</para>
/// </summary>
/// <param name="idEnt">:对象ID</param>
/// <param name="strFontName[256]">:字体名</param>
/// <param name="bIsbarcode">:是否有效</param>
typedef E3_ERR (*e3_GetTextFontName)(E3_ID idEnt,TCHAR strFontName[256],BOOL& bIsbarcode);

/// <summary>
/// <para>API编码:[40121504]</para>
/// 接口说明:群组对象
/// <para>文档定位:数据-对象操作-对象间操作</para>
/// </summary>
/// <param name="idEnts">:被群组的对象ID</param>
/// <param name="nEntCount">:群组的数目</param>
/// <param name="idEntGroup">:群组对象ID</param>
typedef E3_ERR (*e3_GroupEnt)(E3_ID* idEnts,int nEntCount,E3_ID& idEntGroup);

/// <summary>
/// <para>API编码:[63259186]</para>
/// 接口说明:解散群组
/// <para>文档定位:数据-对象操作-对象间操作</para>
/// </summary>
/// <param name="idEntGroup">:群组对象ID</param>
typedef E3_ERR (*e3_UnGroupEnt)(E3_ID idEntGroup);

/// <summary>
/// <para>API编码:[67084108]</para>
/// 接口说明:解散群组
/// <para>文档定位:数据-对象操作-对象间操作</para>
/// </summary>
/// <param name="idEntGroup">:群组对象ID</param>
/// <param name="nFlag">:0x1，禁止通过笔号解散子对象</param>
typedef E3_ERR (*e3_UnGroupEnt2)(E3_ID idEntGroup,int nFlag);

/// <summary>
/// <para>API编码:[03226969]</para>
/// 接口说明:在指定窗口绘制数据库中对象的预览图
/// <para>文档定位:数据-显示-2D显示</para>
/// </summary>
/// <param name="hDC">:绘图相关联的句柄</param>
/// <param name="idEnt">:要显示的层ID或对象ID</param>
/// <param name="nParam">:默认为0</param>
/// <param name="bmpwidth">:窗口的像素宽</param>
/// <param name="bmpheight">:窗口的像素高</param>
/// <param name="dLogOriginX">:窗口的左下角对应点的x向逻辑坐标</param>
/// <param name="dLogOriginY">:窗口的左下角对应点的y向逻辑坐标</param>
/// <param name="dLogScale">:窗口对应的逻辑尺寸与窗口像素尺寸的比例</param>
typedef E3_ERR (*e3_DrawEnt2)(HDC hDC,E3_ID idEnt,int nParam,int bmpwidth,int bmpheight,double dLogOriginX,double dLogOriginY,double dLogScale);

/// <summary>
/// <para>API编码:[11767624]</para>
/// 接口说明:在指定窗口绘制数据库中对象的预览图，并添加背景图
/// <para>文档定位:数据-显示-2D显示</para>
/// </summary>
/// <param name="hDC">:绘图相关联的句柄</param>
/// <param name="idEnt">:要显示的层ID或对象ID</param>
/// <param name="nParam">:默认为0</param>
/// <param name="bmpwidth">:窗口的像素宽</param>
/// <param name="bmpheight">:窗口的像素高</param>
/// <param name="dLogOriginX">:窗口的左下角对应点的x向逻辑坐标</param>
/// <param name="dLogOriginY">:窗口的左下角对应点的y向逻辑坐标</param>
/// <param name="dLogScale">:窗口对应的逻辑尺寸与窗口像素尺寸的比例</param>
/// <param name="pBackBmpParam">:背景图的图像参数</param>
typedef E3_ERR (*e3_DrawEnt3)(HDC hDC,E3_ID idEnt,int nParam,int bmpwidth,int bmpheight,double dLogOriginX,double dLogOriginY,double dLogScale,BackBmpParam* pBackBmpParam);

/// <summary>
/// <para>API编码:[52841796]</para>
/// 接口说明:获取数据库中对象的预览图的HBITMAP
/// <para>文档定位:数据-显示-2D显示</para>
/// </summary>
/// <param name="strEzdFileName">:预览文档的路径</param>
typedef HBITMAP (*e3_GetEzdFilePrevBitmap)(TCHAR* strEzdFileName);

/// <summary>
/// <para>API编码:[44348519]</para>
/// 接口说明:比对序号为nCounterIndex的计数器的当前值与nCompareValue的大小，当nCounterIndex对应的计数器（0-255）的值大于nCompareValue则跳转到索引序号为nListIndex所在行，否则按顺序执行下一条命令。
/// <para>文档定位:硬件-加工动作-列表命令-列表过程命令</para>
/// </summary>
/// <param name="idMarker">:接口使用的板卡ID</param>
/// <param name="nCounterIndex">:计数器的序号</param>
/// <param name="nCompareValue">:比对的数值</param>
/// <param name="nListIndex">:跳转到的索引序号</param>
/// <param name="CompareCond">:</param>
typedef E3_ERR (*e3_MarkerConditionJumpToIndexToList)(E3_ID idMarker,int nCounterIndex,unsigned int nCompareValue,int nListIndex,unsigned char CompareCond);

/// <summary>
/// <para>API编码:[89133678]</para>
/// 接口说明:查询飞行视觉应用中相机触发拍照定位的次数和加工次数
/// <para>文档定位:硬件-资源-寄存器-读</para>
/// </summary>
/// <param name="idMarker">:接口使用的板卡ID</param>
/// <param name="CameraObjectCount">:相机触发拍照定位次数</param>
/// <param name="MarkObjectCount">:加工次数</param>
typedef E3_ERR (*e3_MarkerGetFlyCameraObjectCount)(E3_ID idMarker,unsigned short& CameraObjectCount,unsigned short& MarkObjectCount);

/// <summary>
/// <para>API编码:[81708651]</para>
/// 接口说明:在列表中插入一个索引序号，跳转指令通过索引序号引导跳转到当前行。
/// <para>文档定位:硬件-资源-寄存器-写</para>
/// </summary>
/// <param name="idMarker">:接口使用的板卡ID</param>
/// <param name="nIndex">:索引序号值</param>
typedef E3_ERR (*e3_MarkerSetIndexToList)(E3_ID idMarker,int nIndex);

/// <summary>
/// <para>API编码:[80557629]</para>
/// 接口说明:设置文档加工时的矩阵，通过3x3矩阵支持设置平移，旋转，缩放，错切。
/// <para>文档定位:硬件-加工动作-列表命令-变换</para>
/// </summary>
/// <param name="idMarker">:接口使用的板卡ID</param>
/// <param name="dMatrix">:3x3变换矩阵</param>
typedef E3_ERR (*e3_MarkerSetTransformMatrix)(E3_ID idMarker,double* dMatrix);

/// <summary>
/// <para>API编码:[86915055]</para>
/// 接口说明:设置文档加工时的移动旋转量，不对文档进行修改，先以（dCenterX,?dCenterY）为旋转中心，旋转dRotateAng（弧度），再分别沿X向和Y向平移dMoveX，?dMoveY。
/// <para>文档定位:硬件-组合动作-列表命令-变换</para>
/// </summary>
/// <param name="idMarker">:接口使用的板卡ID</param>
/// <param name="dMoveX">:沿X方向的平移距离</param>
/// <param name="dMoveY">:沿Y方向的平移距离</param>
/// <param name="dCenterX">:旋转中心的X坐标值</param>
/// <param name="dCenterY">:旋转中心的Y坐标值</param>
/// <param name="dRotateAng">:旋转弧度值</param>
typedef E3_ERR (*e3_MarkerSetTransformMatrix2)(E3_ID idMarker,double dMoveX,double dMoveY,double dCenterX,double dCenterY,double dRotateAng);

/// <summary>
/// <para>API编码:[10908885]</para>
/// 接口说明:将3x3矩阵按序号写入板卡相应的寄存器中，以备后续使用，最多支持32个寄存器。
/// <para>文档定位:硬件-加工动作-列表命令-变换</para>
/// </summary>
/// <param name="idMarker">:接口使用的板卡ID</param>
/// <param name="n">:写入寄存器的序号（0-31）</param>
/// <param name="mtx">:3x3变换矩阵</param>
typedef E3_ERR (*e3_MarkerSetTransformMatrixByIndex)(E3_ID idMarker,int n,double* mtx);

/// <summary>
/// <para>API编码:[94646535]</para>
/// 接口说明:加载ez3文件到数据库中
/// <para>文档定位:数据-文件读写</para>
/// </summary>
/// <param name="pStrFileName">:ez3文件的路径</param>
/// <param name="idEM">:要放在的资源管理器ID</param>
/// <param name="bAddMode">:是否为增加模式（不清空当前数据库）</param>
/// <param name="bUndo">:当前操作是否加入到撤销，重做功能</param>
typedef E3_ERR (*e3_OpenFileToEntMgr)(TCHAR* pStrFileName,E3_ID idEM,BOOL bAddMode,BOOL bUndo);

/// <summary>
/// <para>API编码:[02376573]</para>
/// 接口说明:加载ez3文件到数据库中
/// <para>文档定位:数据-文件读写</para>
/// </summary>
/// <param name="pStrFileName">:ez3文件的路径</param>
/// <param name="idEM">:要放在的资源管理器ID</param>
/// <param name="bAddMode">:是否为增加模式（不清空当前数据库）</param>
/// <param name="bUndo">:当前操作是否加入到撤销，重做功能</param>
/// <param name="bShowProgressDlg">:是否显示加载文件进度条窗口</param>
typedef E3_ERR (*e3_OpenFileToEntMgr2)(TCHAR* pStrFileName,E3_ID idEM,BOOL bAddMode,BOOL bUndo,BOOL bShowProgressDlg);

/// <summary>
/// <para>API编码:[47824490]</para>
/// 接口说明:设置扩展轴的参数
/// <para>文档定位:硬件-资源-运动轴-配置</para>
/// </summary>
/// <param name="idMarker">:控制卡ID</param>
/// <param name="axis">:操作的轴序号</param>
/// <param name="bEnable">:是否使能扩展轴</param>
/// <param name="bInvert">:是否反转</param>
/// <param name="bOutNeg">:是否共阴极输出</param>
/// <param name="bRotaryAxis">:是否为旋转轴</param>
/// <param name="dDistPerRound">:转一圈的距离</param>
/// <param name="dPulsePerRound">:每转脉冲数</param>
/// <param name="dMinVel">:最小速度</param>
/// <param name="dMaxVel">:最大速度</param>
/// <param name="dAcceleration">:加速度</param>
/// <param name="dDeceleration">:减速度</param>
/// <param name="dBacklash">:反向间隙</param>
/// <param name="bEnFeedback">:是否使能编码器</param>
/// <param name="dPosErrFollow">:跟随误差</param>
/// <param name="bSAcc">:使能s曲线</param>
/// <param name="dJerk">:加速程度</param>
/// <param name="bEnableSoftLimit">:是否使能软限位</param>
/// <param name="dMinSoftLimit">:软限位最小坐标</param>
/// <param name="dMaxSoftLimit">:软限位最大坐标</param>
/// <param name="bEnableHome">:是否使能零点</param>
/// <param name="bHomeLowValid">:零点是否低电平有效</param>
/// <param name="bHomeDirPos">:是否正向回零</param>
/// <param name="bHomeFindIndex">:回零时是否寻找索引</param>
/// <param name="dHomePos">:零点的坐标</param>
/// <param name="dHomingFindVel">:找零点速度</param>
/// <param name="dHomingLeaveVel">:离开零点速度</param>
/// <param name="bHomeFinishGotoPos">:是否使能回零结束去指定位置</param>
/// <param name="dHomeFinishGotoPos">:回零结束的指定位置</param>
/// <param name="bEnableLimit">:是否使能限位</param>
/// <param name="bLimitLowValid">:限位是否低电平有效</param>
/// <param name="bMarkFinishGotoStartPoint">:加工完是否回到起始位置</param>
/// <param name="bEnableAccurateHome">:是否使能精确回零</param>
typedef E3_ERR (*e3_SetAxisParam2)(E3_ID idMarker,int axis,BOOL bEnable,BOOL bInvert,BOOL bOutNeg,BOOL   bRotaryAxis,double dDistPerRound,double dPulsePerRound,double dMinVel,double dMaxVel,double dAcceleration,double dDeceleration,double dBacklash,BOOL bEnFeedback,double dPosErrFollow,BOOL   bSAcc,double dJerk,BOOL  bEnableSoftLimit,double dMinSoftLimit,double dMaxSoftLimit,BOOL   bEnableHome,BOOL   bHomeLowValid,BOOL   bHomeDirPos,BOOL bHomeFindIndex,double dHomePos,double dHomingFindVel,double dHomingLeaveVel,BOOL  bHomeFinishGotoPos,double dHomeFinishGotoPos,BOOL   bEnableLimit,BOOL  bLimitLowValid,BOOL  bMarkFinishGotoStartPoint,BOOL   bEnableAccurateHome);

/// <summary>
/// <para>API编码:[22425743]</para>
/// 接口说明:设置扩展轴的参数
/// <para>文档定位:硬件-资源-运动轴-配置</para>
/// </summary>
/// <param name="idMarker">:控制卡ID</param>
/// <param name="axis">:操作的轴序号</param>
/// <param name="bEnable">:是否使能扩展轴</param>
/// <param name="bInvert">:是否反转</param>
/// <param name="bOutNeg">:是否共阴极输出</param>
/// <param name="bRotaryAxis">:是否为旋转轴</param>
/// <param name="dDistPerRound">:转一圈的距离</param>
/// <param name="dPulsePerRound">:每转脉冲数</param>
/// <param name="dMinVel">:最小速度</param>
/// <param name="dMaxVel">:最大速度</param>
/// <param name="dAcceleration">:加速度</param>
/// <param name="dDeceleration">:减速度</param>
/// <param name="dBacklash">:反向间隙</param>
/// <param name="bEnFeedback">:是否使能编码器</param>
/// <param name="dPosErrFollow">:跟随误差</param>
/// <param name="bSAcc">:使能s曲线</param>
/// <param name="dJerk">:加速程度</param>
/// <param name="bEnableSoftLimit">:是否使能软限位</param>
/// <param name="dMinSoftLimit">:软限位最小坐标</param>
/// <param name="dMaxSoftLimit">:软限位最大坐标</param>
/// <param name="bEnableHome">:是否使能零点</param>
/// <param name="bHomeLowValid">:零点是否低电平有效</param>
/// <param name="bHomeDirPos">:是否正向回零</param>
/// <param name="bHomeFindIndex">:回零时是否寻找索引</param>
/// <param name="dHomePos">:零点的坐标</param>
/// <param name="dHomingFindVel">:找零点速度</param>
/// <param name="dHomingLeaveVel">:离开零点速度</param>
/// <param name="bHomeFinishGotoPos">:是否使能回零结束去指定位置</param>
/// <param name="dHomeFinishGotoPos">:回零结束的指定位置</param>
/// <param name="bEnableLimit">:是否使能限位</param>
/// <param name="bLimitLowValid">:限位是否低电平有效</param>
/// <param name="bMarkFinishGotoStartPoint">:加工完是否回到起始位置</param>
typedef E3_ERR (*e3_SetAxisParam)(E3_ID idMarker,int axis,BOOL bEnable,BOOL bInvert,BOOL bOutNeg,BOOL   bRotaryAxis,double dDistPerRound,double dPulsePerRound,double dMinVel,double dMaxVel,double dAcceleration,double dDeceleration,double dBacklash,BOOL bEnFeedback,double dPosErrFollow,BOOL   bSAcc,double dJerk,BOOL  bEnableSoftLimit,double dMinSoftLimit,double dMaxSoftLimit,BOOL   bEnableHome,BOOL   bHomeLowValid,BOOL   bHomeDirPos,BOOL bHomeFindIndex,double dHomePos,double dHomingFindVel,double dHomingLeaveVel,BOOL  bHomeFinishGotoPos,double dHomeFinishGotoPos,BOOL   bEnableLimit,BOOL  bLimitLowValid,BOOL  bMarkFinishGotoStartPoint);

/// <summary>
/// <para>API编码:[04827805]</para>
/// 接口说明:设置轴点位运动参数
/// <para>文档定位:硬件-资源-运动轴-配置</para>
/// </summary>
/// <param name="idMarker">:接口使用的板卡ID</param>
/// <param name="axis">:操作的轴序号</param>
/// <param name="dStartSpeed">:起始速度</param>
/// <param name="dMaxSpeed">:最大速度</param>
/// <param name="dAccSpeed">:加速度</param>
typedef E3_ERR (*e3_SetAxisSpeedParam)(E3_ID idMarker,int axis,double dStartSpeed,double dMaxSpeed,double dAccSpeed);

/// <summary>
/// <para>API编码:[93293524]</para>
/// 接口说明:当前轴回零
/// <para>文档定位:硬件-资源-运动轴-动作</para>
/// </summary>
/// <param name="idMarker">:接口使用的板卡ID</param>
/// <param name="axis">:操作的轴序号</param>
/// <param name="bWaitForMoveFinish">:是否等待动作完成</param>
typedef E3_ERR (*e3_AxisHome)(E3_ID idMarker,int axis,BOOL bWaitForMoveFinish);

/// <summary>
/// <para>API编码:[67106153]</para>
/// 接口说明:当前轴回零
/// <para>文档定位:硬件-资源-运动轴-动作</para>
/// </summary>
/// <param name="idMarker">:接口使用的板卡ID</param>
/// <param name="axis">:操作的轴序号</param>
/// <param name="bWaitForMoveFinish">:是否等待动作完成</param>
/// <param name="bSHowWnd">:是否显示回零窗口</param>
typedef E3_ERR (*e3_AxisHome2)(E3_ID idMarker,int axis,BOOL bWaitForMoveFinish,BOOL bSHowWnd);

/// <summary>
/// <para>API编码:[47882942]</para>
/// 接口说明:轴移动到指定坐标位置
/// <para>文档定位:硬件-资源-运动轴-动作</para>
/// </summary>
/// <param name="idMarker">:接口使用的板卡ID</param>
/// <param name="axis">:操作的轴序号</param>
/// <param name="dGoalCoor">:目标坐标位置</param>
/// <param name="bWaitForMoveFinish">:是否等待动作完成</param>
typedef E3_ERR (*e3_AxisMoveTo)(E3_ID idMarker,int axis,double dGoalCoor,BOOL bWaitForMoveFinish);

/// <summary>
/// <para>API编码:[10495038]</para>
/// 接口说明:设置是否回零正常
/// <para>文档定位:硬件-资源-运动轴-配置</para>
/// </summary>
/// <param name="idMarker">:接口使用的板卡ID</param>
/// <param name="axis">:操作的轴序号</param>
/// <param name="bIsAlreadyFindHome">:是否已经正常回零</param>
typedef E3_ERR (*e3_AxisSetFlag)(E3_ID idMarker,int axis,BOOL bIsAlreadyFindHome);

/// <summary>
/// <para>API编码:[95469915]</para>
/// 接口说明:中断当前轴运动
/// <para>文档定位:硬件-资源-运动轴-动作</para>
/// </summary>
/// <param name="idMarker">:接口使用的板卡ID</param>
/// <param name="axis">:操作的轴序号</param>
typedef E3_ERR (*e3_AxisStopMoving)(E3_ID idMarker,int axis);

/// <summary>
/// <para>API编码:[76937869]</para>
/// 接口说明:获取轴的当前坐标
/// <para>文档定位:硬件-资源-运动轴-查询</para>
/// </summary>
/// <param name="idMarker">:接口使用的板卡ID</param>
/// <param name="axis">:操作的轴序号</param>
/// <param name="dCoor">:轴坐标值</param>
typedef E3_ERR (*e3_GetAxisCoor)(E3_ID idMarker,int axis,double& dCoor);

/// <summary>
/// <para>API编码:[83820310]</para>
/// 接口说明:获取轴的当前编码器坐标
/// <para>文档定位:硬件-资源-编码器-查询</para>
/// </summary>
/// <param name="idMarker">:接口使用的板卡ID</param>
/// <param name="axis">:操作的轴序号</param>
/// <param name="dCoor">:编码器坐标值</param>
typedef E3_ERR (*e3_GetAxisFBCoor)(E3_ID idMarker,int axis,double& dCoor);

/// <summary>
/// <para>API编码:[41492024]</para>
/// 接口说明:获取轴的运动参数
/// <para>文档定位:硬件-资源-运动轴-查询</para>
/// </summary>
/// <param name="idMarker">:控制卡ID</param>
/// <param name="axis">:操作的轴序号</param>
/// <param name="bEnable">:是否使能扩展轴</param>
/// <param name="bInvert">:是否反转</param>
/// <param name="bOutNeg">:是否共阴极输出</param>
/// <param name="bRotaryAxis">:是否为旋转轴</param>
/// <param name="dDistPerRound">:转一圈的距离</param>
/// <param name="dPulsePerRound">:每转脉冲数</param>
/// <param name="dMinVel">:最小速度</param>
/// <param name="dMaxVel">:最大速度</param>
/// <param name="dAcceleration">:加速度</param>
/// <param name="dDeceleration">:减速度</param>
/// <param name="dBacklash">:反向间隙</param>
/// <param name="bEnFeedback">:是否使能编码器</param>
/// <param name="dPosErrFollow">:跟随误差</param>
/// <param name="bSAcc">:使能s曲线</param>
/// <param name="dJerk">:加速程度</param>
/// <param name="bEnableSoftLimit">:是否使能软限位</param>
/// <param name="dMinSoftLimit">:软限位最小坐标</param>
/// <param name="dMaxSoftLimit">:软限位最大坐标</param>
/// <param name="bEnableHome">:是否使能零点</param>
/// <param name="&bHomeLowValid">:零点是否低电平有效</param>
/// <param name="bHomeDirPos">:是否正向回零</param>
/// <param name="bHomeFindIndex">:回零时是否寻找索引</param>
/// <param name="dHomePos">:零点的坐标</param>
/// <param name="dHomingFindVel">:找零点速度</param>
/// <param name="dHomingLeaveVel">:离开零点速度</param>
/// <param name="bHomeFinishGotoPos">:是否使能回零结束去指定位置</param>
/// <param name="&dHomeFinishGotoPos">:回零结束的指定位置</param>
/// <param name="&bEnableLimit">:是否使能限位</param>
/// <param name="bLimitLowValid">:限位是否低电平有效</param>
/// <param name="bMarkFinishGotoStartPoint">:加工完是否回到起始位置</param>
typedef E3_ERR (*e3_GetAxisParam)(E3_ID idMarker,int axis,BOOL& bEnable,BOOL& bInvert,BOOL& bOutNeg,BOOL& bRotaryAxis,double& dDistPerRound,double& dPulsePerRound,double& dMinVel,double& dMaxVel,double& dAcceleration,double& dDeceleration,double& dBacklash,BOOL& bEnFeedback,double& dPosErrFollow,BOOL& bSAcc,double& dJerk,BOOL& bEnableSoftLimit,double& dMinSoftLimit,double& dMaxSoftLimit,BOOL& bEnableHome,BOOL &bHomeLowValid,BOOL& bHomeDirPos,BOOL& bHomeFindIndex,double& dHomePos,double& dHomingFindVel,double& dHomingLeaveVel,BOOL& bHomeFinishGotoPos,double &dHomeFinishGotoPos,BOOL &bEnableLimit,BOOL& bLimitLowValid,BOOL& bMarkFinishGotoStartPoint);

/// <summary>
/// <para>API编码:[29335272]</para>
/// 接口说明:获取轴当前状态
/// <para>文档定位:硬件-资源-运动轴-查询</para>
/// </summary>
/// <param name="idMarker">:接口使用的板卡ID</param>
/// <param name="axis">:操作的轴序号</param>
/// <param name="wStatus">:bit状态值: Bit0:  = 1 轴运动;  = 0 轴停止; Bit1:  = 1 左限位高电平;  = 0 左限位低电平; Bit2:  = 1 右限位高电平;  = 0 右限位低电平; Bit3:  = 1 原点高电平;  = 0 原点低电平;</param>
typedef E3_ERR (*e3_GetAxisStatus)(E3_ID idMarker,int axis,WORD& wStatus);

/// <summary>
/// <para>API编码:[65751693]</para>
/// 接口说明:初始化所有轴
/// <para>文档定位:硬件-资源-运动轴-配置</para>
/// </summary>
/// <param name="idMarker">:接口使用的板卡ID</param>
typedef E3_ERR (*e3_InitAllAxis)(E3_ID idMarker);

/// <summary>
/// <para>API编码:[34345432]</para>
/// 接口说明:设置cfg文件的参数
/// <para>文档定位:环境-控制卡-配置</para>
/// </summary>
/// <param name="idMarker">:接口使用的板卡ID</param>
/// <param name="strFile">:cfg文件的位置</param>
/// <param name="nIntParamCount">:int类型参数的数量</param>
/// <param name="nParamBuf">:int类型参数的数组</param>
/// <param name="nDoubleParamCount">:double类型参数的数量</param>
/// <param name="dParamBuf">:double类型参数的数组</param>
typedef E3_ERR (*e3_SetCfgFileParam)(E3_ID idMarker,TCHAR* strFile,int nIntParamCount,int* nParamBuf,int nDoubleParamCount,double* dParamBuf);

/// <summary>
/// <para>API编码:[74736044]</para>
/// 接口说明:设置对象的填充参数
/// <para>文档定位:数据-填充相关</para>
/// </summary>
/// <param name="idEM">:目标所在的资源管理器ID</param>
/// <param name="idEnt">:填充的对象ID</param>
/// <param name="bEnableContour">:是否使能轮廓</param>
/// <param name="bContourFirst">:是否使能轮廓优先</param>
/// <param name="param1">:填充参数1</param>
/// <param name="param2">:填充参数2</param>
/// <param name="param3">:填充参数3</param>
/// <param name="bUndo">:是否加入到撤销，重做</param>
/// <param name="strUndo">:撤销，重做字符串</param>
typedef E3_ERR (*e3_SetEntHatchParam)(E3_ID idEM,E3_ID idEnt,BOOL bEnableContour,BOOL bContourFirst,HatchParam param1,HatchParam param2,HatchParam param3,BOOL bUndo,TCHAR* strUndo);

/// <summary>
/// <para>API编码:[32057454]</para>
/// 接口说明:飞行等待相机位置到位
/// <para>文档定位:硬件-组合动作-列表命令-列表过程命令</para>
/// </summary>
/// <param name="idMarker">:接口使用的板卡ID</param>
/// <param name="dFlyDistance">:相机与振镜之间的固定间距</param>
/// <param name="bIsFollowAvail">:在飞行等待的过程中振镜位置是否随流水线一起保持运动</param>
typedef E3_ERR (*e3_FlyWaitCameraPositioningToList)(E3_ID idMarker,double dFlyDistance,BOOL bIsFollowAvail);

/// <summary>
/// <para>API编码:[89202892]</para>
/// 接口说明:按照序号递增规则，加工时自动选择矩阵变换（0-31进行循环）
/// <para>文档定位:硬件-组合动作-列表命令-变换</para>
/// </summary>
/// <param name="idMarker">:接口使用的板卡ID</param>
/// <param name="ExceptionFlag">:0x1 当前变换无效时，对象直接加工，不进行旋转   0x2 当前变换无效时，对象不加工，振镜正常摆，不出光</param>
typedef E3_ERR (*e3_MarkerAutoSelectListMatirxToList2)(E3_ID idMarker,unsigned short ExceptionFlag);

/// <summary>
/// <para>API编码:[99119811]</para>
/// 接口说明:按序号选择矩阵变换并设置使能
/// <para>文档定位:硬件-组合动作-列表命令-变换</para>
/// </summary>
/// <param name="idMarker">:接口使用的板卡ID</param>
/// <param name="n">:变换矩阵的序号</param>
/// <param name="bEnable">:是否使能变换</param>
typedef E3_ERR (*e3_MarkerSelectTransMatirxToList)(E3_ID idMarker,int n,BOOL bEnable);

/// <summary>
/// <para>API编码:[76891828]</para>
/// 接口说明:按序号选择矩阵变换并设置使能
/// <para>文档定位:硬件-组合动作-列表命令-变换</para>
/// </summary>
/// <param name="idMarker">:接口使用的板卡ID</param>
/// <param name="n">:变换矩阵的序号</param>
/// <param name="bEnable">:是否使能变换</param>
/// <param name="ExceptionFlag">:0x1 当前变换无效时，对象直接加工，不进行旋转   0x2 当前变换无效时，对象不加工，振镜正常摆，不出光</param>
typedef E3_ERR (*e3_MarkerSelectTransMatirxToList2)(E3_ID idMarker,int n,BOOL bEnable,unsigned short ExceptionFlag);

/// <summary>
/// <para>API编码:[52189106]</para>
/// 接口说明:设置加工时所有对象的先绕旋转中心旋转指定角度，然后平移指定距离。不改变原文档。
/// <para>文档定位:环境-控制卡-配置</para>
/// </summary>
/// <param name="idMarker">:接口使用的板卡ID</param>
/// <param name="dMoveX">:沿X方向的平移距离</param>
/// <param name="dMoveY">:沿Y方向的平移距离</param>
/// <param name="dCenterX">:旋转中心的X坐标值</param>
/// <param name="dCenterY">:旋转中心的Y坐标值</param>
/// <param name="dRotateAng">:旋转弧度值</param>
typedef E3_ERR (*e3_MarkerSetRotateMoveParam)(E3_ID idMarker,double dMoveX,double dMoveY,double dCenterX,double dCenterY,double dRotateAng);

/// <summary>
/// <para>API编码:[07127413]</para>
/// 接口说明:将移动，旋转变换按序号写入板卡相应的寄存器中，以备后续使用，最多支持32个寄存器。
/// <para>文档定位:硬件-组合动作-列表命令-变换</para>
/// </summary>
/// <param name="idMarker">:接口使用的板卡ID</param>
/// <param name="n">:写入寄存器的序号（0-31）</param>
/// <param name="dMoveX">:沿X方向的平移距离</param>
/// <param name="dMoveY">:沿Y方向的平移距离</param>
/// <param name="dCenterX">:旋转中心的X坐标值</param>
/// <param name="dCenterY">:旋转中心的Y坐标值</param>
/// <param name="dRotateAng">:旋转弧度值</param>
typedef E3_ERR (*e3_MarkerSetTransformMatrixByIndex2)(E3_ID idMarker,int n,double dMoveX,double dMoveY,double dCenterX,double dCenterY,double dRotateAng);

/// <summary>
/// <para>API编码:[44335471]</para>
/// 接口说明:将移动，旋转变换按序号写入板卡相应的寄存器中，以备后续使用，最多支持32个寄存器。
/// <para>文档定位:硬件-组合动作-列表命令-变换</para>
/// </summary>
/// <param name="idMarker">:接口使用的板卡ID</param>
/// <param name="n">:写入寄存器的序号（0-31）</param>
/// <param name="dMoveX">:沿X方向的平移距离</param>
/// <param name="dMoveY">:沿Y方向的平移距离</param>
/// <param name="dCenterX">:旋转中心的X坐标值</param>
/// <param name="dCenterY">:旋转中心的Y坐标值</param>
/// <param name="dRotateAng">:旋转弧度值</param>
/// <param name="Avail">:0x1当前变换有效  0x0当前变换无效</param>
typedef E3_ERR (*e3_MarkerSetTransformMatrixByIndex3)(E3_ID idMarker,int n,double dMoveX,double dMoveY,double dCenterX,double dCenterY,double dRotateAng,unsigned char Avail);

/// <summary>
/// <para>API编码:[67014622]</para>
/// 接口说明:拉伸对象
/// <para>文档定位:数据-对象操作-对象通用读写</para>
/// </summary>
/// <param name="idEnt">:拉伸对象ID</param>
/// <param name="dCenx">:拉伸中心X坐标</param>
/// <param name="dCeny">:拉伸中心Y坐标</param>
/// <param name="dScaleX">:X方向拉伸比例</param>
/// <param name="dScaleY">:Y方向拉伸比例</param>
typedef E3_ERR (*e3_ScaleEnt)(E3_ID idEnt,double dCenx,double dCeny,double dScaleX,double dScaleY);

/// <summary>
/// <para>API编码:[41055991]</para>
/// 接口说明:设置板卡主循环IO检测流程
/// <para>文档定位:硬件-加工动作-动作指令</para>
/// </summary>
/// <param name="idMarker">:控制卡ID</param>
/// <param name="PortMask">:要检查端口的端口掩膜</param>
/// <param name="PortValue">:满足条件的端口比较值</param>
/// <param name="bEnable">:0x1 启动主循环IO检测流程 0x0  关闭主循环IO检测流程</param>
/// <param name="dIOAvailTime">:输入口电平有效时间(ms)</param>
typedef E3_ERR (*e3_StartMainLoopIOCheckProcess)(E3_ID idMarker,unsigned int PortMask,unsigned int PortValue,unsigned char bEnable,double dIOAvailTime);

/// <summary>
/// <para>API编码:[14090013]</para>
/// 接口说明:使用设置F3参数接口后，更新F3参数.
/// <para>文档定位:硬件-资源-激光-配置</para>
/// </summary>
/// <param name="idMarker">:板卡ID; </param>
/// <param name="bSaveCfg">:是否保存文件至cfg文件. True=是;</param>
typedef E3_ERR (*e3_MarkerUpdateParam)(E3_ID idMarker,BOOL bSaveCfg);

/// <summary>
/// <para>API编码:[25432468]</para>
/// 接口说明:得到对象信息
/// <para>文档定位:数据-对象操作-对象通用读写</para>
/// </summary>
/// <param name="idEnt">:对象ID</param>
/// <param name="nFlag">:属性页,对象属性超过本接口所能承载的数量后,可以输入分页参数</param>
/// <param name="np1">:int类型属性信息1</param>
/// <param name="np2">:int类型属性信息2</param>
/// <param name="np3">:int类型属性信息3</param>
/// <param name="np4">:int类型属性信息4</param>
/// <param name="np5">:int类型属性信息5</param>
/// <param name="np6">:int类型属性信息6</param>
/// <param name="dp1">:double类型属性信息1</param>
/// <param name="dp2">:double类型属性信息2</param>
/// <param name="dp3">:double类型属性信息3</param>
/// <param name="dp4">:double类型属性信息4</param>
/// <param name="dp5">:double类型属性信息5</param>
/// <param name="dp6">:double类型属性信息6</param>
/// <param name="str1[256]">:字符型信息</param>
/// <param name="pParam1">:Byte形数组</param>
typedef E3_ERR (*e3_GetEntInfo)(E3_ID idEnt,int nFlag,int& np1,int& np2,int& np3,int& np4,int& np5,int& np6,double& dp1,double& dp2,double& dp3,double& dp4,double& dp5,double& dp6,TCHAR str1[256],void* pParam1);

/// <summary>
/// <para>API编码:[81821961]</para>
/// 接口说明:设置对象信息
/// <para>文档定位:数据-对象操作-对象通用读写</para>
/// </summary>
/// <param name="idEM">:管理器ID</param>
/// <param name="idEnt">:对象ID</param>
/// <param name="nFlag">:属性页,对象属性超过本接口所能承载的数量后,可以输入分页参数</param>
/// <param name="np1">:int类型属性信息1</param>
/// <param name="np2">:int类型属性信息2</param>
/// <param name="np3">:int类型属性信息3</param>
/// <param name="np4">:int类型属性信息4</param>
/// <param name="np5">:int类型属性信息5</param>
/// <param name="np6">:int类型属性信息6</param>
/// <param name="dp1">:double类型属性信息1</param>
/// <param name="dp2">:double类型属性信息2</param>
/// <param name="dp3">:double类型属性信息3</param>
/// <param name="dp4">:double类型属性信息4</param>
/// <param name="dp5">:double类型属性信息5</param>
/// <param name="dp6">:double类型属性信息6</param>
/// <param name="str1">:字符型信息</param>
/// <param name="bUndo">:预留,默认False</param>
/// <param name="strUndo">:预留,默认""</param>
typedef E3_ERR (*e3_SetEntInfo)(E3_ID idEM,E3_ID idEnt,int nFlag,int np1,int np2,int np3,int np4,int np5,int np6,double dp1,double dp2,double dp3,double dp4,double dp5,double dp6,TCHAR* str1,BOOL bUndo,TCHAR* strUndo);

/// <summary>
/// <para>API编码:[74334088]</para>
/// 接口说明:设置对象信息接口2
/// <para>文档定位:数据-对象操作-对象通用读写</para>
/// </summary>
/// <param name="idEM">:管理器ID</param>
/// <param name="idEnt">:对象ID</param>
/// <param name="nFlag">:属性页,对象属性超过本接口所能承载的数量后,可以输入分页参数</param>
/// <param name="np1">:int类型属性信息1</param>
/// <param name="np2">:int类型属性信息2</param>
/// <param name="np3">:int类型属性信息3</param>
/// <param name="np4">:int类型属性信息4</param>
/// <param name="np5">:int类型属性信息5</param>
/// <param name="np6">:int类型属性信息6</param>
/// <param name="dp1">:double类型属性信息1</param>
/// <param name="dp2">:double类型属性信息2</param>
/// <param name="dp3">:double类型属性信息3</param>
/// <param name="dp4">:double类型属性信息4</param>
/// <param name="dp5">:double类型属性信息5</param>
/// <param name="dp6">:double类型属性信息6</param>
/// <param name="str1">:字符型信息</param>
typedef E3_ERR (*e3_SetEntInfo_2)(E3_ID idEM,E3_ID idEnt,int nFlag,int np1,int np2,int np3,int np4,int np5,int np6,double dp1,double dp2,double dp3,double dp4,double dp5,double dp6,TCHAR* str1);

/// <summary>
/// <para>API编码:[35784011]</para>
/// 接口说明:读取输出口状态,与[E3_MarkerGetWritePort]不同,[E3_MarkerGetWritePort]接口是读取的库内部缓存值,而此接口读取的是板卡真实值.
/// <para>文档定位:硬件-资源-数字量OUT-查询</para>
/// </summary>
/// <param name="idMarker">:控制卡ID.</param>
/// <param name="wCurOutPort">:返回的状态值.</param>
typedef E3_ERR (*e3_MarkerGetOutputPortStatus)(E3_ID idMarker,WORD& wCurOutPort);

/// <summary>
/// <para>API编码:[56613766]</para>
/// 接口说明:将对象转化为点对象,可以是文本，也可以是矩形等
/// <para>文档定位:数据-对象操作-对象间操作</para>
/// </summary>
/// <param name="idEnt">:对象ID</param>
/// <param name="nParamFlag">:默认为0</param>
/// <param name="bAveragePt">:nPointNum的点数是否平均分布 true的时候平均分布</param>
/// <param name="nPointNum">:平均分布的点数</param>
/// <param name="dPointDist">:非平均分布的时候，点间距</param>
/// <param name="dArcTol">:精度，默认0.01</param>
/// <param name="bDeleteOldEnt">:是否删除旧对象，true删除旧对象</param>
/// <param name="idNewEnt">:点组对象ID</param>
typedef E3_ERR (*e3_ChangeEntToPoints)(E3_ID idEnt,int nParamFlag,BOOL bAveragePt,int nPointNum,double dPointDist,double dArcTol,BOOL bDeleteOldEnt,E3_ID& idNewEnt);

/// <summary>
/// <para>API编码:[23803992]</para>
/// 接口说明:标刻一条3D线段，列表命令
/// <para>文档定位:硬件-加工动作-列表命令-节点级列表命令</para>
/// </summary>
/// <param name="idMarker">:控制卡ID</param>
/// <param name="type">:默认0</param>
/// <param name="pen">:笔号</param>
/// <param name="ptNum">:ptBuf的长度</param>
/// <param name="nFlag">:与E3_MarkerMarkEnt2中的nMarkFlag一致</param>
/// <param name="ptBuf">:线段顶点数组[,3]</param>
typedef E3_ERR (*e3_MarkerOneCurveToList2)(E3_ID idMarker,int type,int pen,int ptNum,ListReadyMode nFlag,Pt3d* ptBuf);

/// <summary>
/// <para>API编码:[79218581]</para>
/// 接口说明:得到激光接口板卡类型 0X0001STD 0X0002SPI 0X0003QCW 0X0004FIBER 0X0005PolyScan 0X1001JCZ_LASER
/// <para>文档定位:环境-控制卡-操作</para>
/// </summary>
/// <param name="idMarker">:控制卡ID</param>
/// <param name="id">:扩展卡类型对应的类型</param>
typedef E3_ERR (*e3_MarkerGetLaserBoardTypeID)(E3_ID idMarker,int& id);

/// <summary>
/// <para>API编码:[36382979]</para>
/// 接口说明:获取变量文本信息
/// <para>文档定位:数据-标准图元-编辑-文本类型-变量文本</para>
/// </summary>
/// <param name="idEnt">:对象ID</param>
/// <param name="nMaxCount">:节点长度</param>
/// <param name="wTypes">:节点类型</param>
/// <param name="wFlags">:节点参数</param>
typedef E3_ERR (*e3_GetTextElementInfo)(E3_ID idEnt,int nMaxCount,WORD* wTypes,WORD* wFlags);

/// <summary>
/// <para>API编码:[76139045]</para>
/// 接口说明:获取变量文本_固定文本
/// <para>文档定位:数据-标准图元-编辑-文本类型-变量文本</para>
/// </summary>
/// <param name="idEnt">:对象ID</param>
/// <param name="index">:节点序号</param>
/// <param name="pStr[256]">:固定文本内容</param>
typedef E3_ERR (*e3_GetTextElementStr)(E3_ID idEnt,int index,TCHAR pStr[256]);

/// <summary>
/// <para>API编码:[67467089]</para>
/// 接口说明:获取变量文本_序列号信息
/// <para>文档定位:数据-标准图元-编辑-文本类型-变量文本</para>
/// </summary>
/// <param name="idEnt">:文本对象ID</param>
/// <param name="index">:节点序号</param>
/// <param name="nSnIncrement">:序列号增量</param>
/// <param name="nSnMarksPer">:每个加工数</param>
/// <param name="nSnCurMarksNum">:当前加工数</param>
/// <param name="nSerialCharType">:序列号类型（SC_TYPE_DEC）</param>
/// <param name="nSerialChar">:序列号进制字符数</param>
/// <param name="bEnableFilter">:是否启用过滤</param>
/// <param name="timeReset1">:重置时间</param>
/// <param name="bEnReset1">:是否重置</param>
/// <param name="pStr1[256]">:启示序号</param>
/// <param name="pStr2[256]">:当前序号</param>
/// <param name="pStr3[256]">:最大序号</param>
/// <param name="pFilter1[256]">:过滤内容1</param>
/// <param name="pFilter2[256]">:过滤内容2</param>
/// <param name="pFilter3[256]">:过滤内容3</param>
/// <param name="pFilter4[256]">:过滤内容4</param>
/// <param name="pFilter5[256]">:过滤内容5</param>
typedef E3_ERR (*e3_GetTextElementSerialNo)(E3_ID idEnt,int index,int& nSnIncrement,int& nSnMarksPer,int& nSnCurMarksNum,int& nSerialCharType,int& nSerialChar,BOOL& bEnableFilter,int& timeReset1,BOOL& bEnReset1,TCHAR pStr1[256],TCHAR pStr2[256],TCHAR pStr3[256],TCHAR pFilter1[256],TCHAR pFilter2[256],TCHAR pFilter3[256],TCHAR pFilter4[256],TCHAR pFilter5[256]);

/// <summary>
/// <para>API编码:[93622729]</para>
/// 接口说明:获取变量文本序列号扩展信息
/// <para>文档定位:数据-标准图元-编辑-文本类型-变量文本</para>
/// </summary>
/// <param name="idEnt">:变量文本ID</param>
/// <param name="index">:节点序号</param>
/// <param name="indexChar">:自定义序列号字符序号</param>
/// <param name="pStr[256]">:自定义序列号指定序号字符串</param>
typedef E3_ERR (*e3_GetTextElementSerialNo2)(E3_ID idEnt,int index,int indexChar,TCHAR pStr[256]);

/// <summary>
/// <para>API编码:[49677502]</para>
/// 接口说明:获取变量文本日期信息
/// <para>文档定位:数据-标准图元-编辑-文本类型-变量文本</para>
/// </summary>
/// <param name="idEnt">:变量文本ID</param>
/// <param name="index">:节点序号</param>
/// <param name="nDateType">:日期类型</param>
/// <param name="nDateOffsetType">:日期偏移类型</param>
/// <param name="nDateOffset">:日期偏移量</param>
/// <param name="bEnableDefYear">:周类型默认按1月1日开始计算</param>
typedef E3_ERR (*e3_GetTextElementDate)(E3_ID idEnt,int index,int& nDateType,int& nDateOffsetType,int& nDateOffset,int& bEnableDefYear);

/// <summary>
/// <para>API编码:[07344239]</para>
/// 接口说明:变量文本日期具体信息
/// <para>文档定位:数据-标准图元-编辑-文本类型-变量文本</para>
/// </summary>
/// <param name="idEnt">:变量文本ID</param>
/// <param name="index">:节点序号</param>
/// <param name="indexChar">:字符序号</param>
/// <param name="pStr[256]">:字符</param>
typedef E3_ERR (*e3_GetTextElementDate2)(E3_ID idEnt,int index,int indexChar,TCHAR pStr[256]);

/// <summary>
/// <para>API编码:[48032134]</para>
/// 接口说明:变量文本时刻信息
/// <para>文档定位:数据-标准图元-编辑-文本类型-变量文本</para>
/// </summary>
/// <param name="idEnt">:变量文本ID</param>
/// <param name="index">:节点序号</param>
/// <param name="nTimeType">:时刻类型0,24小时 1,12小时 2,分钟 3,秒钟 4时间段</param>
/// <param name="nStartTime[24]">:时间段开始时间列表</param>
/// <param name="nEndTime[24]">:时间段结束时间列表</param>
typedef E3_ERR (*e3_GetTextElementTime)(E3_ID idEnt,int index,int& nTimeType,int nStartTime[24],int nEndTime[24]);

/// <summary>
/// <para>API编码:[37884216]</para>
/// 接口说明:时间段自定义文本
/// <para>文档定位:数据-标准图元-编辑-文本类型-变量文本</para>
/// </summary>
/// <param name="idEnt">:变量文本ID</param>
/// <param name="index">:节点序号</param>
/// <param name="indexChar">:时间段序号</param>
/// <param name="pStr[256]">:时间段对应文本内容</param>
typedef E3_ERR (*e3_GetTextElementTime2)(E3_ID idEnt,int index,int indexChar,TCHAR pStr[256]);

/// <summary>
/// <para>API编码:[37152633]</para>
/// 接口说明:TCPIP通讯文本
/// <para>文档定位:数据-标准图元-编辑-文本类型-变量文本</para>
/// </summary>
/// <param name="idEnt">:变量文本ID</param>
/// <param name="index">:节点序号</param>
/// <param name="nPort">:服务器端口</param>
/// <param name="bUnicode">:是否UNICODE编码</param>
/// <param name="pStr1[256]">:服务器IP地址</param>
/// <param name="pStr2[256]">:请求字段命令</param>
typedef E3_ERR (*e3_GetTextElementTcpip)(E3_ID idEnt,int index,int& nPort,BOOL& bUnicode,TCHAR pStr1[256],TCHAR pStr2[256]);

/// <summary>
/// <para>API编码:[20032220]</para>
/// 接口说明:串口通讯文本
/// <para>文档定位:数据-标准图元-编辑-文本类型-变量文本</para>
/// </summary>
/// <param name="idEnt">:变量文本ID</param>
/// <param name="index">:节点序号</param>
/// <param name="nPort">:上位机端口</param>
/// <param name="bUnicode">:是否UNICODE编码</param>
/// <param name="nBaudRate">:波特率</param>
/// <param name="nDataBits">:数据位</param>
/// <param name="nStopBits">:停止位</param>
/// <param name="nParity">:是否效验</param>
/// <param name="pStr1[256]">:请求字段命令</param>
typedef E3_ERR (*e3_GetTextElementCom)(E3_ID idEnt,int index,int& nPort,BOOL& bUnicode,int& nBaudRate,int& nDataBits,int& nStopBits,int& nParity,TCHAR pStr1[256]);

/// <summary>
/// <para>API编码:[78608175]</para>
/// 接口说明:变量文本-文件
/// <para>文档定位:数据-标准图元-编辑-文本类型-变量文本</para>
/// </summary>
/// <param name="idEnt">:变量文本ID</param>
/// <param name="index">:节点序号</param>
/// <param name="nFileType">:文件类型0记事本 1EXCEL</param>
/// <param name="bAutoReset">:完成后自动重置</param>
/// <param name="bReadAll">:全部读取</param>
/// <param name="nCurFileLineNo">:当前文件行数</param>
/// <param name="nCurFileInc">:行增量</param>
/// <param name="pStr1[256]">:文件名</param>
/// <param name="pStr2[256]">:EXCEL表名</param>
/// <param name="pStr3[256]">:EXCEL列名</param>
typedef E3_ERR (*e3_GetTextElementFile)(E3_ID idEnt,int index,int& nFileType,BOOL& bAutoReset,BOOL& bReadAll,int& nCurFileLineNo,int& nCurFileInc,TCHAR pStr1[256],TCHAR pStr2[256],TCHAR pStr3[256]);

/// <summary>
/// <para>API编码:[79083478]</para>
/// 接口说明:变量文本-键盘
/// <para>文档定位:数据-标准图元-编辑-文本类型-变量文本</para>
/// </summary>
/// <param name="idEnt">:变量文本ID</param>
/// <param name="index">:节点序号</param>
/// <param name="bEnableFixedLength">:是否固定长度</param>
/// <param name="bSetPenParam">:是否切换笔参数</param>
/// <param name="nCharLength">:固定长度值</param>
/// <param name="pStr1[256]">:请求字符命令</param>
/// <param name="pStr2[256]">:笔号+参数类型</param>
typedef E3_ERR (*e3_GetTextElementKB)(E3_ID idEnt,int index,BOOL& bEnableFixedLength,BOOL& bSetPenParam,int& nCharLength,TCHAR pStr1[256],TCHAR pStr2[256]);

/// <summary>
/// <para>API编码:[40272377]</para>
/// 接口说明:sql数据库变量文本.
/// <para>文档定位:数据-标准图元-编辑-文本类型-变量文本</para>
/// </summary>
/// <param name="idEnt">:变量文本ID</param>
/// <param name="index">:节点序号</param>
/// <param name="bAutoReset">:是否自动复位</param>
/// <param name="bReadAll">:是否读取全部</param>
/// <param name="nSqlLineNo">:SQL行号</param>
/// <param name="nSqlInc">:SQL行号增量</param>
/// <param name="pStr1[256]">:服务器信息</param>
/// <param name="pStr2[256]">:文件路径</param>
/// <param name="pStr3[256]">:用户名</param>
/// <param name="pStr4[256]">:密码</param>
/// <param name="pStr5[256]">:SQL查询命令</param>
typedef E3_ERR (*e3_GetTextElementSql)(E3_ID idEnt,int index,BOOL& bAutoReset,BOOL& bReadAll,int& nSqlLineNo,int& nSqlInc,TCHAR pStr1[256],TCHAR pStr2[256],TCHAR pStr3[256],TCHAR pStr4[256],TCHAR pStr5[256]);

/// <summary>
/// <para>API编码:[64254685]</para>
/// 接口说明:调整变量文本节点排序
/// <para>文档定位:数据-标准图元-编辑-文本类型-变量文本</para>
/// </summary>
/// <param name="idEM">:对象管理器ID</param>
/// <param name="idEnt">:变量文本ID</param>
/// <param name="indexElement">:节点序号</param>
/// <param name="nFun">:0删除 1上调 2下调</param>
/// <param name="bUndo">:默认参数 FALSE</param>
/// <param name="strUndo">:默认参数 ""</param>
typedef E3_ERR (*e3_ModifyTextElement)(E3_ID idEM,E3_ID idEnt,int indexElement,int nFun,BOOL bUndo,TCHAR* strUndo);

/// <summary>
/// <para>API编码:[51464256]</para>
/// 接口说明:变量文本内容更新.
/// <para>文档定位:数据-标准图元-编辑-文本类型-变量文本</para>
/// </summary>
/// <param name="idEM">:对象管理器ID</param>
/// <param name="idEnt">:变量文本ID</param>
/// <param name="nSubCmd">:-1递减 0复位 1递增</param>
typedef E3_ERR (*e3_SnTextEntRefresh)(E3_ID idEM,E3_ID idEnt,int nSubCmd);

/// <summary>
/// <para>API编码:[22293514]</para>
/// 接口说明:更新变量文本单元信息
/// <para>文档定位:数据-标准图元-编辑-文本类型-变量文本</para>
/// </summary>
/// <param name="idEM">:对象管理器ID</param>
/// <param name="idEnt">:变量文本ID</param>
/// <param name="indexElement">:变量文本单元序号</param>
/// <param name="nMaxParamN">:整形参数长度</param>
/// <param name="nParam">:整型参数列表</param>
/// <param name="nMaxParamD">:浮点参数长度</param>
/// <param name="dParam">:浮点参数列表</param>
/// <param name="nMaxParamS">:字符串参数长度</param>
/// <param name="sParam">:字符串数量</param>
/// <param name="bUndo">:是否支持撤销</param>
/// <param name="strUndo">:动作节点说明</param>
typedef E3_ERR (*e3_UpdateTextElement)(E3_ID idEM,E3_ID idEnt,int indexElement,int nMaxParamN,int* nParam,int nMaxParamD,double* dParam,int nMaxParamS,TCHAR** sParam,BOOL bUndo,TCHAR* strUndo);

/// <summary>
/// <para>API编码:[98510811]</para>
/// 接口说明:更新变量文本内容,也即得到新的值.
/// <para>文档定位:数据-标准图元-编辑-文本类型-变量文本</para>
/// </summary>
/// <param name="idEM">:对象管理器ID.</param>
/// <param name="idEnt">:变量文本对象ID.</param>
typedef E3_ERR (*e3_VariableEntRefresh)(E3_ID idEM,E3_ID idEnt);

/// <summary>
/// <para>API编码:[90171795]</para>
/// 接口说明:变量文本获取掩码元素参数.
/// <para>文档定位:数据-标准图元-编辑-文本类型-变量文本</para>
/// </summary>
/// <param name="idEnt">:对象ID</param>
/// <param name="index">:当前掩码元素所在变量列表索引号</param>
/// <param name="strMask[256]">:掩码</param>
/// <param name="strAlias[256]">:别名</param>
/// <param name="strText[256]">:文本</param>
typedef E3_ERR (*e3_GetTextElementMask)(E3_ID idEnt,int index,TCHAR strMask[256],TCHAR strAlias[256],TCHAR strText[256]);

/// <summary>
/// <para>API编码:[13352731]</para>
/// 接口说明:获取二维条码的删除中间块功能参数.
/// <para>文档定位:数据-对象操作-对象通用读写</para>
/// </summary>
/// <param name="idEnt">:对象ID</param>
/// <param name="bDeleteCenterBlock">:是否使能删除中间块</param>
/// <param name="nDeleteBlockNumX">:删除中间块的X数量</param>
/// <param name="nDeleteBlockNumY">:删除中间块的Y数量</param>
typedef E3_ERR (*e3_GetTextBarcodeInfo8)(E3_ID idEnt,BOOL& bDeleteCenterBlock,int& nDeleteBlockNumX,int& nDeleteBlockNumY);

/// <summary>
/// <para>API编码:[90198558]</para>
/// 接口说明:设置二维条码的删除中间块功能参数.
/// <para>文档定位:数据-对象操作-对象通用读写</para>
/// </summary>
/// <param name="idEnt">:对象ID</param>
/// <param name="bDeleteCenterBlock">:是否使能删除中间块</param>
/// <param name="nDeleteBlockNumX">:删除中间块的X数量</param>
/// <param name="nDeleteBlockNumY">:删除中间块的Y数量</param>
typedef E3_ERR (*e3_SetTextBarcodeInfo8)(E3_ID idEnt,BOOL bDeleteCenterBlock,int nDeleteBlockNumX,int nDeleteBlockNumY);

/// <summary>
/// <para>API编码:[80125201]</para>
/// 接口说明:设置对象隐藏状态.
/// <para>文档定位:数据-对象操作-对象通用读写</para>
/// </summary>
/// <param name="idEnt">:对象ID</param>
/// <param name="bHide">:是否设置隐藏</param>
typedef E3_ERR (*e3_SetEntHide)(E3_ID idEnt,BOOL bHide);

/// <summary>
/// <para>API编码:[39209787]</para>
/// 接口说明:解散群组,通过nOneGroupCount设置的数量进行分组解散
/// <para>文档定位:数据-对象操作-对象间操作</para>
/// </summary>
/// <param name="idEntGroup">:群组对象ID</param>
/// <param name="nFlag">:0x1，禁止通过笔号解散子对象</param>
/// <param name="nOneGroupCount">:设置打包对象数量,将按照此数量进行打包解散</param>
typedef E3_ERR (*e3_UnGroupEnt3)(E3_ID idEntGroup,int nFlag,int nOneGroupCount);

/// <summary>
/// <para>API编码:[60715303]</para>
/// 接口说明:linux平台下,在初始化之前设置系统主机与控制卡之间的通讯链路类型.
/// <para>文档定位:环境-初始化以及释放</para>
/// </summary>
/// <param name="Type">:控制卡通讯链路类型:Type=0x8,Linux SPI, Type=0x3,Linux Usb</param>
typedef E3_ERR (*e3_SetControllerInterfaceType)(BYTE Type);

/// <summary>
/// <para>API编码:[15240066]</para>
/// 接口说明:1.填充指定对象，最多八组填充参数； 2.当被填充的对象为非填充对象时，只能用此接口； 3.当被填充的对象时填充对象，可以用此接口，也可以用E3_SetHatchParam或者E3_SetHatchParam2修改填充参数
/// <para>文档定位:数据-填充相关</para>
/// </summary>
/// <param name="idEM">:管理器ID</param>
/// <param name="idEnt">:对象ID</param>
/// <param name="bEnableContour">:是否使能轮廓;true使能，false不使能</param>
/// <param name="bContourFirst">:是否使能轮廓优先;true使能，false不使能；</param>
/// <param name="nHatchParamCount">:填充参数数组paramList长度；范围1-8</param>
/// <param name="pParam">:填充参数数组</param>
/// <param name="idEntHatch">:填充之后的对象ID</param>
/// <param name="reserved1">:预留参数,默认False</param>
/// <param name="reserved2">:预留参数,默认""</param>
typedef E3_ERR (*e3_HatchEnt3)(E3_ID idEM,E3_ID idEnt,BOOL bEnableContour,BOOL bContourFirst,int nHatchParamCount,HatchParam* pParam,E3_ID& idEntHatch,BOOL reserved1,TCHAR* reserved2);

/// <summary>
/// <para>API编码:[27026726]</para>
/// 接口说明:获取qcw第二功率输出
/// <para>文档定位:数据-笔参数相关</para>
/// </summary>
/// <param name="idEM">:管理器ID</param>
/// <param name="nPenNo">:笔号</param>
/// <param name="dPowerRatio2">:返回的第二组功率输出</param>
typedef E3_ERR (*e3_GetPenParamPower2)(E3_ID idEM,int nPenNo,double& dPowerRatio2);

/// <summary>
/// <para>API编码:[05201969]</para>
/// 接口说明:设置qcw第二功率输出
/// <para>文档定位:数据-笔参数相关</para>
/// </summary>
/// <param name="idEM">:管理器ID</param>
/// <param name="nPenNo">:笔号</param>
/// <param name="dPowerRatio2">:设置第二组功率输出值</param>
typedef E3_ERR (*e3_SetPenParamPower2)(E3_ID idEM,int nPenNo,double dPowerRatio2);

/// <summary>
/// <para>API编码:[60832921]</para>
/// 接口说明:设置系统int类型参数.从sysparam.ini中读取.
/// <para>文档定位:环境-控制卡-配置</para>
/// </summary>
/// <param name="index">:系统参数中int类型参数的索引号</param>
/// <param name="value">:对应索引参数值</param>
typedef E3_ERR (*e3_SetSysParamInt)(int index,int value);

/// <summary>
/// <para>API编码:[90308215]</para>
/// 接口说明:获取系统int类型参数.从sysparam.ini中读取.
/// <para>文档定位:环境-控制卡-配置</para>
/// </summary>
/// <param name="index">:系统参数中int类型参数的索引号</param>
/// <param name="value">:对应索引参数值</param>
typedef E3_ERR (*e3_GetSysParamInt)(int index,int& value);

/// <summary>
/// <para>API编码:[57783273]</para>
/// 接口说明:变量文本刷新,但不对序列号刷新.
/// <para>文档定位:数据-标准图元-编辑-文本类型-变量文本</para>
/// </summary>
/// <param name="idEM">:管理器ID</param>
/// <param name="idEnt">:对象ID</param>
typedef E3_ERR (*e3_VariableEntRefresh_NoSN)(E3_ID idEM,E3_ID idEnt);

/// <summary>
/// <para>API编码:[88753679]</para>
/// 接口说明:变量文本更新,用于加工前后更新数据,加工后调用,会更新曲线.
/// <para>文档定位:数据-标准图元-编辑-文本类型-变量文本</para>
/// </summary>
/// <param name="idEM">:管理器ID</param>
/// <param name="idEnt">:对象ID</param>
/// <param name="bMark">:刷新标志,True:加工前刷新.False:加工后刷新</param>
typedef E3_ERR (*e3_VariableEntRefresh2)(E3_ID idEM,E3_ID idEnt,BOOL bMark);

/// <summary>
/// <para>API编码:[35905330]</para>
/// 接口说明:获取当前底层库的版本信息
/// <para>文档定位:环境-控制卡</para>
/// </summary>
/// <param name="szVersion[256]">:返回的版本信息字符串</param>
typedef E3_ERR (*e3_GetDllVersion)(TCHAR  szVersion[256]);

/// <summary>
/// <para>API编码:[85082386]</para>
/// 接口说明:添加螺旋线3.
/// <para>文档定位:数据-标准图元-创建</para>
/// </summary>
/// <param name="idEM">:管理器ID</param>
/// <param name="nPen">:笔号[0,255]</param>
/// <param name="pt1">:螺旋中心坐标</param>
/// <param name="pt2">:螺旋半径坐标 （X 坐标为中心坐标+半径长度，Y坐标为中心坐标）</param>
/// <param name="dSpiralPitchDistMin">:最小螺旋线间距</param>
/// <param name="dSpiralPitchDistMax">:最大螺旋线间距</param>
/// <param name="dSpiralPitchDistInc">:螺旋线间距增量</param>
/// <param name="bUpdateParentInfo">:是否更新列表信息，若不更新对象列表信息,最后更新,避免大量创建时由于更新对象列表导致的卡顿</param>
/// <param name="idNewEnt">:返回创建的对象ID</param>
typedef E3_ERR (*e3_CreateSpiral_3)(E3_ID idEM,int nPen,Pt2d pt1,Pt2d pt2,double dSpiralPitchDistMin,double dSpiralPitchDistMax,double dSpiralPitchDistInc,BOOL bUpdateParentInfo,E3_ID& idNewEnt);

/// <summary>
/// <para>API编码:[10485363]</para>
/// 接口说明:获取输入口状态,此接口支持读取锁存状态,通过[E3_SetInputPortWorkMode]接口设置模式为脉冲及高低电平,锁存功能才会被使能. 当板卡检测到边沿信号后,会将portLatchedStatus对应端口位置位1,此时需要调用[MarkerClearInputPort0State]或[MarkerClearInputPortState]来清除板卡缓存状态. 建议不要在portLatchedStatus为0的情况下,调用清锁存接口,因为会存在误清的情况.
/// <para>文档定位:硬件-资源-数字量IN-查询</para>
/// </summary>
/// <param name="idMarker">:控制卡ID</param>
/// <param name="portData">:端口当前的电平值,此值与[E3_MarkerReadPort]接口相同.(v4卡默认为1,一般情况读取为0x0fff).</param>
/// <param name="portLatchedStatus">:端口锁存状态,位指示脉冲锁存是否有效,通过[MarkerClearInputPortState]接口清除.</param>
typedef E3_ERR (*e3_MarkerGetInputPortStatus)(E3_ID idMarker,unsigned short& portData,unsigned short& portLatchedStatus);

/// <summary>
/// <para>API编码:[04580131]</para>
/// 接口说明:清除板卡输入口的锁存状态,配合[E3_MarkerGetInputPortStatus]接口使用.
/// <para>文档定位:硬件-资源-数字量IN-配置</para>
/// </summary>
/// <param name="idMarker">:控制卡ID</param>
/// <param name="portNo">:十进制端口索引编号,一般的为0-15</param>
typedef E3_ERR (*e3_MarkerClearInputPortState)(E3_ID idMarker,unsigned short portNo);

/// <summary>
/// <para>API编码:[95336489]</para>
/// 接口说明:清除板卡输入口的锁存状态,配合[E3_MarkerGetInputPortStatus]接口使用.与[MarkerClearInputPortState]功能相同,但是此接口适配老版本底层程序.
/// <para>文档定位:硬件-资源-数字量IN-配置</para>
/// </summary>
/// <param name="idMarker">:控制卡ID</param>
/// <param name="portNo">:十进制端口索引编号,一般的为0-15</param>
typedef E3_ERR (*e3_MarkerClearInputPort0State)(E3_ID idMarker,BYTE portNo);

/// <summary>
/// <para>API编码:[68546191]</para>
/// 接口说明:列表中发送空指令.
/// <para>文档定位:硬件-加工动作-列表命令-列表过程命令</para>
/// </summary>
/// <param name="idMarker">:控制卡ID</param>
typedef E3_ERR (*e3_MarkerListNop)(E3_ID idMarker);

/// <summary>
/// <para>API编码:[62931927]</para>
/// 接口说明:此接口设置停止标志,在填充过程中支持取消. 注意,需要在填充之前将标志设置为false,不然填充接口不执行. 设置标志后,填充接口停止会有一定延迟,与底层库的检测时机有关.
/// <para>文档定位:数据-填充相关</para>
/// </summary>
/// <param name="bStop">:是否填充中取消标志</param>
typedef E3_ERR (*e3_SetHatchStop)(BOOL bStop);


#ifdef _WIN32
  #define EXPORT_SYMBOL __declspec(dllexport)
#elif __linux__
  #define EXPORT_SYMBOL __attribute__((visibility("default")))
#else
  #define EXPORT_SYMBOL
#endif

//接口库主类.
class EXPORT_SYMBOL EzdKernel
{
public:
    EzdKernel(LogCallbackHandler logback);
    ~EzdKernel();
private:
#ifdef _WIN32
    HMODULE m_hEzdDLL;//DLL调用句柄
    HMODULE m_sysDLL;//DLL调用句柄
#else
    void* m_hEzdDLL;
#endif

    INIParser ini_parser;
    LogCallbackHandler logCallback = nullptr;
public:
getForegroundWindow GetForegroundWindow = nullptr;

        /// <summary> 
        /// 封装的初始化函数,用于支持网口卡. 
        /// </summary> 
        /// <param name="basePath">开发库根目录路径.</param> 
        /// <param name="mode">初始化模式.</param> 
        /// <param name="otherCfgPath">如果配置的目录不在开发库目录下,这个参数指定,如果在同一目录下,给null.</param> 
        /// <returns></returns> 
E3_ERR Initial(TCHAR* basePath, InitialMode mode, TCHAR* otherCfgPath);
string TCHAR2STRING(TCHAR* STR);

        /// <summary>
        /// 设置矢量图对象信息
        /// </summary>
        /// <param name="idEnt">对象ID</param>
        /// <param name="strFileName">文件名称</param>
        /// <param name="bOptimize">是否优化曲线顺序</param>
        /// <param name="bAutoConnect">是否自动连接相邻的曲线段</param>
        /// <param name="bDynFile">是否动态输入文件</param>
        /// <param name="bFixedX">是否固定X方向尺寸</param>
        /// <param name="bFixedY">是否固定Y方向尺寸</param>
        /// <param name="dSizeX">X方向尺寸</param>
        /// <param name="dSizeY">Y方向尺寸</param>
        /// <param name="bFixedCoor">是否固定输入点坐标</param>
        /// <param name="dFixedCoorX">固定输入点X坐标</param>
        /// <param name="dFixedCoorY">固定输入点X坐标</param>
        /// <param name="nFixedPos">固定位置</param>
        /// 6 5 4
        /// 7 8 3
        /// 0 1 2
        /// <returns>E3_ERR</returns>
    E3_ERR E3_SetEntVectorFileInfo(E3_ID idEM, E3_ID idEnt, TCHAR* strFileName, bool bOptimize, bool bAutoConnect, bool bDynFile, bool bFixedX, bool bFixedY, double dSizeX, double dSizeY, bool bFixedCoor, double dFixedCoorX, double dFixedCoorY, int nFixedPos);

        const int VECATTRIB_DYNFILE = 0x1000;//动态文件加工时重新载入
        const int VECATTRIB_IMPORTFIXED_WIDTH = 0x2000;//固定文件输入宽
        const int VECATTRIB_IMPORTFIXED_HEIGHT = 0x4000;//固定文件输入高
        const int VECATTRIB_AUTOCONNECTCURVE = 0x0100;//自动连接断开的曲线
        const int VECATTRIB_OPTIMIZEPATH = 0x0200;//自动曲线顺序
        /// <summary>
        /// 得到矢量图对象信息
        /// </summary>
        /// <param name="idEnt">对象ID</param>
        /// <param name="strFileName">文件名称</param>
        /// <param name="bOptimize">是否优化曲线顺序</param>
        /// <param name="bAutoConnect">是否自动连接相邻的曲线段</param>
        /// <param name="bDynFile">是否动态输入文件</param>
        /// <param name="bFixedX">是否固定X方向尺寸</param>
        /// <param name="bFixedY">是否固定Y方向尺寸</param>
        /// <param name="dSizeX">X方向尺寸</param>
        /// <param name="dSizeY">Y方向尺寸</param>
        /// <param name="bFixedCoor">是否固定输入点坐标</param>
        /// <param name="dFixedCoorX">固定输入点X坐标</param>
        /// <param name="dFixedCoorY">固定输入点X坐标</param>
        /// <param name="nFixedPos">固定位置</param>
        /// 6 5 4
        /// 7 8 3
        /// 0 1 2
        /// <returns>E3_ERR</returns>
    E3_ERR E3_GetEntVectorFileInfo(E3_ID idEnt, TCHAR* strFileName, bool& bOptimize, bool& bAutoConnect, bool& bDynFile, bool& bFixedX, bool& bFixedY, double& dSizeX, double& dSizeY, bool& bFixedCoor, double& dFixedCoorX, double& dFixedCoorY, int& nFixedPos);

        /// <summary>
        /// 设置输入口对象信息
        /// </summary>
        /// <param name="idEnt">对象ID</param>
        /// <param name="bEnablePrompt">是否使能提示消息</param>
        /// <param name="strPrompt">提示消息</param>
        /// <param name="wIoHigh">高电平端口值（比如只有2和3端口是高电平，这个值为12）</param>
        /// <param name="wIoLow">低电平端口值（比如只有端口1和3是低电平，这个值是10）</param>
        /// <returns></returns>
    E3_ERR E3_SetEntIoInputInfo(E3_ID idEM, E3_ID idEnt, bool bEnablePrompt, TCHAR* strPrompt, int wIoHigh, int wIoLow);

        /// <summary>
        /// 设置输出口对象信息
        /// </summary>
        /// <param name="idEnt">对象ID</param>
        /// <param name="bAllOutMode">是否全部输出</param>
        /// <param name="wOutValue">当使能全部输出口时，如要输出口3，此值为2的3次方即8，若要输出口0,1,2,都有输出此值为7</param>
        /// <param name="nOutPutBit">设置单独输出口，端口值，比如输出口2，此值为2</param>
        /// <param name="bHigh">是否高电平或者上升沿有效</param>
        /// <param name="bPulse">是否脉冲模式</param>
        /// <param name="dPulseTimeMs">脉冲持续时间（ms）</param>
        /// <returns>E3_ERR</returns>
    E3_ERR E3_SetEntIoOutputInfo(E3_ID idEM, E3_ID idEnt, bool bAllOutMode, int wOutValue, int nOutPutBit, bool bHigh, bool bPulse, double dPulseTimeMs);

        /// <summary>
        /// 得到输入口对象信息
        /// </summary>
        /// <param name="idEnt">对象ID</param>
        /// <param name="bEnablePrompt">是否使能提示消息</param>
        /// <param name="strPrompt">提示消息</param>
        /// <param name="wIoHigh">高电平端口值（比如只有2和3端口是高电平，这个值为12）</param>
        /// <param name="wIoLow">低电平端口值（比如只有端口1和3是低电平，这个值是10）</param>
        /// <returns></returns>
   E3_ERR E3_GetEntIoInputInfo(E3_ID idEnt, bool& bEnablePrompt, TCHAR* strPrompt, int& wIoHigh, int& wIoLow);

        /// <summary>
        /// 得到输出口对象信息
        /// </summary>
        /// <param name="idEnt">对象ID</param>
        /// <param name="bAllOutMode">是否全部输出</param>
        /// <param name="wOutValue">当使能全部输出口时，如要输出口3，此值为2的3次方即8，若要输出口0,1,2,都有输出此值为7</param>
        /// <param name="nOutPutBit">设置单独输出口，端口值，比如输出口2，此值为2</param>
        /// <param name="bHigh">是否高电平或者上升沿有效</param>
        /// <param name="bPulse">是否脉冲模式</param>
        /// <param name="dPulseTimeMs">脉冲持续时间（ms）</param>
        /// <returns>E3_ERR</returns>
   E3_ERR E3_GetEntIoOutputInfo(E3_ID idEnt, bool& bAllOutMode, int& wOutValue, int& nOutPutBit, bool& bHigh, bool& bPulse, double& dPulseTimeMs);

		/// <summary>
		/// 获取矩形对象参数;
		///  (此接口非库函数,基于Get/SetEntInfo封装实现)
		/// </summary>
		/// <param name="idEnt">对象ID;</param>
		/// <param name="nCornerLT">左上圆角(角度);</param>
		/// <param name="nCornerRT">右上圆角(角度);</param>
		/// <param name="nCornerLB">左下圆角(角度);</param>
		/// <param name="nCornerRB">右下圆角(角度);</param>
E3_ERR E3_GetEntRectInfo(E3_ID idEnt, double& nCornerLT, double& nCornerRT, double& nCornerLB, double& nCornerRB);

		/// <summary>
		/// 设置矩形对象参数;
		/// (此接口非库函数,基于Get/SetEntInfo封装实现)
		/// </summary>
		/// <param name="idEM">管理器ID;</param>
		/// <param name="idEnt">对象ID;</param>
		/// <param name="nCornerLT">左上圆角(角度);</param>
		/// <param name="nCornerRT">右上圆角(角度);</param>
		/// <param name="nCornerLB">左下圆角(角度);</param>
		/// <param name="nCornerRB">右下圆角(角度);</param>
E3_ERR E3_SetEntRectInfo(E3_ID idEM, E3_ID idEnt, double nCornerLT, double nCornerRT, double nCornerLB, double nCornerRB);

		/// <summary>
		/// 获取椭圆对象参数;
		/// (此接口非库函数,基于Get/SetEntInfo封装实现)
		/// </summary>
		/// <param name="idEnt">对象ID;</param>
		/// <param name="dStartAng">开始角度（弧度值）;</param>
		/// <param name="dEndAng">结束角度（弧度值）;</param>
		/// <param name="bDirCW">是否为开顺时针.True为顺时针;</param>
		/// <param name="bOC">是否为开曲线.True为开曲线;</param>
E3_ERR E3_GetEntEllipseInfo(E3_ID idEnt, double& dStartAng, double& dEndAng, bool& bDirCW, bool& bOC);

		/// <summary>
		/// 设置椭圆对象参数接口.
		/// (此接口非库函数, 基于Get/SetEntInfo封装实现)
		/// </summary>
		/// <param name="idEM">管理器ID;</param>
		/// <param name="idEnt">对象ID;</param>
		/// <param name="dStartAng">开始角度（弧度值）;</param>
		/// <param name="dEndAng">结束角度（弧度值）;</param>
		/// <param name="bDirCW">是否为开顺时针.True为顺时针;</param>
		/// <param name="bOC">是否为开曲线.True为开曲线;</param>
E3_ERR E3_SetEntEllipseInfo(E3_ID idEM, E3_ID idEnt, double dStartAng, double dEndAng, bool bDirCW, bool bOC);

		/// <summary>
		/// 获取多边形对象参数.
		/// (此接口非库函数, 基于Get/SetEntInfo封装实现)
		/// </summary>
		/// <param name="idEnt">对象ID;</param>
		/// <param name="nEdge">边数;</param>
		/// <param name="bStar">是否内轮廓（默认false外轮廓）;</param>
E3_ERR E3_GetEntPolygonInfo(E3_ID idEnt, int& nEdge, bool& bStar);

		/// <summary>
		/// 设置多边形对象参数.
		/// (此接口非库函数, 基于Get/SetEntInfo封装实现)
		/// </summary>
		/// <param name="idEnt">对象ID;</param>
		/// <param name="nEdge">边数;</param>
		/// <param name="bStar">是否内轮廓（默认false外轮廓）;</param>
E3_ERR E3_SetEntPolygonInfo(E3_ID idEM, E3_ID idEnt, int nEdge, bool bStar);

		/// <summary>
		/// 获取圆对象参数
		/// (此接口非库函数, 基于Get/SetEntInfo封装实现)
		/// </summary>
		/// <param name="idEnt">对象ID;</param>
		/// <param name="dDiameter">直径;</param>
		/// <param name="dStartAng">开始角度;</param>
		/// <param name="bDirCW">是否为逆时针(默认FALSE顺时针);</param>
E3_ERR E3_GetEntCircleInfo(E3_ID idEnt, double& dDiameter, double& dStartAng, bool& bDirCW);

		/// <summary>
		/// 设置圆对象参数;
		/// (此接口非库函数, 基于Get/SetEntInfo封装实现)
		/// </summary>
		/// <param name="idEM">管理器ID;</param>
		/// <param name="idEnt">对象ID;</param>
		/// <param name="dDiameter">直径;</param>
		/// <param name="dStartAng">开始角度;</param>
		/// <param name="bDirCW">是否为逆时针(默认FALSE顺时针);</param>
E3_ERR E3_SetEntCircleInfo(E3_ID idEM, E3_ID idEnt, double dDiameter, double dStartAng, bool bDirCW);

		/// <summary>
		/// 获取螺旋线对象信息
		/// </summary>
		/// <param name="idEnt">对象ID</param>
		/// <param name="nSpiralMode">填充属性 0等间距 1外疏内密 2外密内</param>
		/// <param name="bInsideToOutside">是否由里向外</param>
		/// <param name="nOutsideLoop">外环数</param>
		/// <param name="nInsideLoop">内环数</param>
		/// <param name="bDoubleSprialMode">是否是双曲线模式</param>
		/// <param name="bRectangleMode">是否是矩形模式</param>
		/// <param name="dSpiralPitchDistMin">最小螺旋线间距</param>
		/// <param name="dSpiralPitchDistMax">最大螺旋线间距</param>
		/// <param name="dSpiralPitchDistInc">螺旋线间距增量</param>
		/// <param name="dMinRadius">最小半径</param>
		/// <param name="dTolError">精度，默认0.005</param>
    E3_ERR E3_GetEntSpiralInfo(E3_ID idEnt, int& nSpiralMode, bool& bInsideToOutside, int& nOutsideLoop, int& nInsideLoop, bool& bDoubleSprialMode, bool& bRectangleMode, double& dSpiralPitchDistMin, double& dSpiralPitchDistMax, double& dSpiralPitchDistInc, double& dMinRadius, double& dTolError);

		/// <summary>
		/// 设置螺旋线对象信息
		/// </summary>
		/// <param name="idEnt">对象ID</param>
		/// <param name="nSpiralMode">填充属性 0等间距 1外疏内密 2外密内</param>
		/// <param name="bInsideToOutside">是否由里向外</param>
		/// <param name="nOutsideLoop">外环数</param>
		/// <param name="nInsideLoop">内环数</param>
		/// <param name="bDoubleSprialMode">是否是双曲线模式</param>
		/// <param name="bRectangleMode">是否是矩形模式</param>
		/// <param name="dSpiralPitchDistMin">最小螺旋线间距</param>
		/// <param name="dSpiralPitchDistMax">最大螺旋线间距</param>
		/// <param name="dSpiralPitchDistInc">螺旋线间距增量</param>
		/// <param name="dMinRadius">最小半径</param>
		/// <param name="dTolError">精度，默认0.005</param>
   E3_ERR E3_SetEntSpiralInfo(E3_ID idEM, E3_ID idEnt, int nSpiralMode, bool bInsideToOutside, int nOutsideLoop, int nInsideLoop, bool bDoubleSprialMode, bool bRectangleMode, double dSpiralPitchDistMin, double dSpiralPitchDistMax, double dSpiralPitchDistInc, double dMinRadius, double dTolError);

		/// <summary>
		/// 获取延时器对象参数;
		/// (此接口非库函数, 基于Get/SetEntInfo封装实现)
		/// </summary>
		/// <param name="idEnt">对象ID;</param>
		/// <param name="dTimeDelay">延时时间(单位:ms) [0,1000000];</param>
E3_ERR E3_GetEntTimerInfo(E3_ID idEnt, double& dTimeDelay);

		/// <summary>
		/// 设置延时器对象参数;
		/// </summary>
		/// <param name="idEM">管理器ID;</param>
		/// <param name="idEnt">对象ID;</param>
		/// <param name="dTimeDelay">延时时间(单位:ms) [0,1000000];</param>
E3_ERR E3_SetEntTimerInfo(E3_ID idEM, E3_ID idEnt, double dTimeDelay);

		/// <summary>
		/// 获取编码器对象参数;
		/// (此接口非库函数, 基于Get/SetEntInfo封装实现)
		/// </summary>
		/// <param name="idEnt">对象ID;</param>
		/// <param name="dFlyMoveDist">编码器移动距离单位（mm）;</param>
E3_ERR E3_GetEntFlyMoveDistInfo(E3_ID idEnt, double& dFlyMoveDist);

		/// <summary>
		/// 设置编码器对象参数;
		/// (此接口非库函数, 基于Get/SetEntInfo封装实现)
		/// </summary>
		/// <param name="idEM">管理器ID;</param>
		/// <param name="idEnt">对象ID;</param>
		/// <param name="dFlyMoveDist">编码器移动距离单位（mm）;</param>
E3_ERR E3_SetEntFlyMoveDistInfo(E3_ID idEM, E3_ID idEnt, double dFlyMoveDist);

		/// <summary>
		/// 设置轴对象参数(二次开发库中轴对象是free模式);
		/// (此接口非库函数, 基于Get/SetEntInfo封装实现)
		/// </summary>
		/// <param name="idEM">管理器ID;</param>
		/// <param name="idEnt">对象ID;</param>
		/// <param name="nUnit">每转运动距离;</param>
		/// <param name="nAxisId">轴索引:xyza对应0123;</param>
		/// <param name="nMoveFlag">移动标志位： 移动 零点 复位对应012;</param>
		/// <param name="bRelative">是否使能相对位置true 是绝对位置 ，false相对位置;</param>
		/// <param name="dPulsePerUnit">每转脉冲数;</param>
		/// <param name="dDist">移动距离(单位：mm);</param>
		/// <param name="dMinSpeed">最小速度(单位：mm/s);</param>
		/// <param name="dMaxSpeed">最大速度(单位：mm/s);</param>
		/// <param name="dAxisAccTime">加速度(单位：mm/s2);</param>
E3_ERR E3_SetEntAxisInfo(E3_ID idEM, E3_ID idEnt, int nUnit, int nAxisId, int nMoveFlag, bool bRelative, double dPulsePerUnit, double dDist, double dMinSpeed, double dMaxSpeed, double dAxisAccTime);

		/// <summary>
		/// 获取轴对象参数(二次开发库中轴对象是free模式).
		/// (此接口非库函数, 基于Get/SetEntInfo封装实现)
		/// </summary>
		/// <param name="idEnt">对象ID;</param>
		/// <param name="nUnit">每转运动距离;</param>
		/// <param name="nAxisId">轴索引:xyza对应0123;</param>
		/// <param name="nMoveFlag">移动标志位： 移动 零点 复位对应012;</param>
		/// <param name="bRelative">是否使能相对位置true 是绝对位置 ，false相对位置;</param>
		/// <param name="dPulsePerUnit">每转脉冲数;</param>
		/// <param name="dDist">移动距离(单位：mm);</param>
		/// <param name="dMinSpeed">最小速度(单位：mm/s);</param>
		/// <param name="dMaxSpeed">最大速度(单位：mm/s);</param>
		/// <param name="dAxisAccTime">加速度(单位：mm/s2);</param>
E3_ERR E3_GetEntAxisInfo(E3_ID idEnt, int& nUnit, int& nAxisId, int& nMoveFlag, bool& bRelative, double& dPulsePerUnit, double& dDist, double& dMinSpeed, double& dMaxSpeed, double& dAxisAccTime);

		/// <summary>
		/// 获取CCD对象参数;
		/// (此接口非库函数, 基于Get/SetEntInfo封装实现)
		/// </summary>
		/// <param name="idEnt">对象ID;</param>
		/// <param name="bReset">是否复位ccd true为复位 ccd;</param>
		/// <param name="bMoveToStartPos">移动到ccd开始位置;</param>
		/// <param name="bEnableCalibrate">使能ccd校正;</param>
		/// <param name="bEnableChangeModel">使能模板修改;</param>
		/// <param name="nModelIndex">模板号;</param>
		/// <param name="nFailMode">失败处理模式 0停止1继续2跳转;</param>
		/// <param name="bRepeatTry">是否重试;</param>
		/// <param name="nRepeatCount">重试次数;</param>
		/// <param name="nJumpToEntIndex">跳转后索引;</param>
E3_ERR E3_GetCCDInfo(E3_ID idEnt, bool& bReset, bool& bMoveToStartPos, bool& bEnableCalibrate, bool& bEnableChangeModel, int& nModelIndex, int& nFailMode, bool& bRepeatTry, int& nRepeatCount, int& nJumpToEntIndex);

		/// <summary>
		/// 设置CCD对象参数;
		/// (此接口非库函数, 基于Get/SetEntInfo封装实现)
		/// </summary>
		/// <param name="idEM">管理器ID;</param>
		/// <param name="idEnt">对象ID;</param>
		/// <param name="bReset">是否复位ccd true为复位 ccd;</param>
		/// <param name="bMoveToStartPos">移动到ccd开始位置;</param>
		/// <param name="bEnableCalibrate">使能ccd校正;</param>
		/// <param name="bEnableChangeModel">使能模板修改;</param>
		/// <param name="nModelIndex">模板号;</param>
		/// <param name="nFailMode">失败处理模式 0停止1继续2跳转;</param>
		/// <param name="bRepeatTry">是否重试;</param>
		/// <param name="nRepeatCount">重试次数;</param>
		/// <param name="nJumpToEntIndex">跳转后索引;</param>
E3_ERR E3_SetCCDInfo(E3_ID idEM, E3_ID idEnt, bool bReset, bool bMoveToStartPos, bool bEnableCalibrate, bool bEnableChangeModel, int nModelIndex, int nFailMode, bool bRepeatTry, int nRepeatCount, int nJumpToEntIndex);

		/// <summary>
		/// 获取对象的索引参数;
		/// (此接口非库函数, 基于Get/SetEntInfo封装实现)
		/// </summary>
		/// <param name="idEnt">对象ID;</param>
		/// <param name="index">索引;</param>
E3_ERR E3_GetEntIndex(E3_ID idEnt, int& index);

		/// <summary>
		/// 设置对象索引参数;
		/// (此接口非库函数, 基于Get/SetEntInfo封装实现)
		/// </summary>
		/// <param name="idEM">管理器ID;</param>
		/// <param name="idEnt">对象ID;</param>
		/// <param name="index">索引;</param>
E3_ERR E3_SetEntIndex(E3_ID idEM, E3_ID idEnt, int index);

/// <summary>
/// 获取bmp对象的参数信息;
/// (此接口非库函数, 基于Get/SetEntInfo封装实现)
/// </summary>
/// <param name="idEnt">对象ID;</param>
/// <param name="strFileName">位图对象文件全路径.(最大256字节);</param>
/// <param name="bBidir">双向扫描;</param>
/// <param name="dBiDirOffset">双向扫描错位补偿;</param>
/// <param name="bDrillmode">打点模式;</param>
/// <param name="dDrillTime">打点延时;[0,100000];</param>
/// <param name="bScanY">Y向扫描;</param>
/// <param name="mirrorX">镜像X;</param>
/// <param name="mirrorY">镜像Y;</param>
/// <param name="bPixelPower">调整点功率;</param>
/// <param name="bFixedDPI">使能固定DPI;</param>
/// <param name="nDpiX">固定X方向DPI;[10,10000];</param>
/// <param name="nDpiY">固定Y方向DPI;[10,10000];</param>
/// <param name="bDynFile">使能动态文件;</param>
/// <param name="bFixedX">使能固定X尺寸;</param>
/// <param name="bFixedY">使能固定Y尺寸;</param>
/// <param name="bTrueDPI">使能改变位图真实DPI;</param>
/// <param name="dSizeX">固定的X方向尺寸;</param>
/// <param name="dSizeY">固定的Y方向尺寸;</param>
/// <param name="nFixedPosition">动态文件的参考坐标:0~8,排布方式:左下角=0,逆时针旋转,中心为8;</param>
/// <param name="bGray">使能灰度处理;</param>
/// <param name="bInvert">使能反转处理;</param>
/// <param name="bDither">使能网点处理;</param>
/// <param name="bLight">使能发亮处理;</param>
/// <param name="bOptimize">使能优化模式;</param>
/// <param name="scanReverse">扫描反转;</param>
/// <param name="luminValue" >亮度;</ param >
/// <param name="contrast">对比度;</param>
/// <param name="bLineOffset">行错位;</param>
/// <param name="bLineIncrement">使能位图扫描行增量;</param>
/// <param name="nLineIncrement">扫描行数;[1,100];</param>
/// <param name="nMinLowGrayPt">低灰度值;[0,255];</param>
/// <param name="bDisableMarkLowGrayPt">使能不标刻低灰度值的点;</param>
/// <param name="dAccDist">加速距离</param>
/// <param name="dDecDist">减速距离</param>
/// <param name="dGlobalMigration">整体偏移</param>
/// <param name="nGrayCurvePt">灰度功率曲线节点数量（无效）</param>
/// <param name="ptGrayCurveBuf">灰度功率曲线列表(无效)</param>
/// <param name="bGrayScaleBuf">灰度功率表(256长度，POW[i] i=gray pow[i]=pow*2.56);</param>
E3_ERR E3_GetEntBmpFileInfo(E3_ID idEnt, TCHAR* strFileName, bool& bBidir, double& dBiDirOffset, bool& bDrillmode, double& dDrillTime, bool& bScanY, bool& mirrorX, bool& mirrorY, bool& bPixelPower, bool& bFixedDPI, int& nDpiX, int& nDpiY, bool& bDynFile, bool& bFixedX, bool& bFixedY, bool& bTrueDPI, double& dSizeX, double& dSizeY, int& nFixedPosition, bool& bGray, bool& bInvert, bool& bDither, bool& bLight, bool& bOptimize, bool& scanReverse, double& luminValue, double& contrast, bool& bLineOffset, bool& bLineIncrement, int& nLineIncrement, int& nMinLowGrayPt, bool& bDisableMarkLowGrayPt, double& dAccDist, double& dDecDist, double& dGlobalMigration, int& nGrayCurvePt, Pt2d ptGrayCurveBuf[20], BYTE bGrayScaleBuf[256]);

        /// <summary>
        /// 设置bmp对象的参数信息;
        /// (此接口非库函数, 基于Get/SetEntInfo封装实现)
        /// </summary>
        /// <param name="idEM">管理器ID;</param>
        /// <param name="idEnt">对象ID;</param>
        /// <param name="strFileName">位图对象文件全路径.(最大256字节);</param>
        /// <param name="bBidir">双向扫描;</param>
        /// <param name="dBiDirOffset">双向扫描错位补偿;</param>
        /// <param name="bDrillmode">打点模式;</param>
        /// <param name="dDrillTime">打点延时;[0,100000];</param>
        /// <param name="bScanY">Y向扫描;</param>
        /// <param name="mirrorX">镜像X;</param>
        /// <param name="mirrorY">镜像Y;</param>
        /// <param name="bPixelPower">调整点功率;</param>
        /// <param name="bFixedDPI">使能固定DPI;</param>
        /// <param name="nDpiX">固定X方向DPI;[10,10000];</param>
        /// <param name="nDpiY">固定Y方向DPI;[10,10000];</param>
        /// <param name="bDynFile">使能动态文件;</param>
        /// <param name="bFixedX">使能固定X尺寸;</param>
        /// <param name="bFixedY">使能固定Y尺寸;</param>
        /// <param name="bTrueDPI">使能改变位图真实DPI;</param>
        /// <param name="dSizeX">固定的X方向尺寸;</param>
        /// <param name="dSizeY">固定的Y方向尺寸;</param>
        /// <param name="nFixedPosition">动态文件的参考坐标:0~8,排布方式:左下角=0,逆时针旋转,中心为8;</param>
        /// <param name="bGray">使能灰度处理;</param>
        /// <param name="bInvert">使能反转处理;</param>
        /// <param name="bDither">使能网点处理;</param>
        /// <param name="bLight">使能发亮处理;</param>
        /// <param name="bOptimize">使能优化模式;</param>
        /// <param name="scanReverse">扫描反转;</param>
        /// <param name="luminValue" >亮度;</ param >
        /// <param name="contrast">对比度;</param>
        /// <param name="bLineOffset">行错位;</param>
        /// <param name="bLineIncrement">使能位图扫描行增量;</param>
        /// <param name="nLineIncrement">扫描行数;[1,100];</param>
        /// <param name="nMinLowGrayPt">低灰度值;[0,255];</param>
        /// <param name="bDisableMarkLowGrayPt">使能不标刻低灰度值的点;</param>
        /// <param name="dAccDist">加速距离</param>
        /// <param name="dDecDist">减速距离</param>
        /// <param name="dGlobalMigration">整体偏移</param>
        /// <param name="nGrayCurvePt">灰度功率曲线节点数量（无效）</param>
        /// <param name="ptGrayCurveBuf">灰度功率曲线列表(无效)</param>
        /// <param name="bGrayScaleBuf">灰度功率表(256长度，POW[i] i=gray pow[i]=pow*2.56);</param>
        /// <param name="bmpFilePath">位图文件路径</param>

    /// <summary>
    /// 获取位图对象真实数据
    /// </summary>
    /// <param name="idEnt">对象ID</param>
    /// <param name="W">图像宽度</param>
    /// <param name="H">图像高度</param>
    /// <param name="ScanW">图像数据宽度</param>
    /// <param name="Bitcount">位深度</param>
    /// <param name="byteCount">图像数据数组长度</param>
    /// <param name="bmpMinX">图像的最小X坐标</param>
    /// <param name="bmpMinY">图像的最小Y坐标</param>
    /// <param name="bmpAngleFromX">图像底边与X轴的夹角</param>
    /// <param name="bmpWidth">图像的宽度</param>
    /// <param name="bmpHeight">图像的高度</param>
    /// <returns>图像数据BUFF</returns>
    BYTE* E3_GetEntBmpFileData(E3_ID idEnt, int& W, int& H, int& ScanW, int& Bitcount, int& byteCount, double& bmpMinX, double& bmpMinY, double& bmpAngleFromX, double& bmpWidth, double& bmpHeight, E3_ERR& err);

/// <summary>
/// 释放由[E3_GetEntBmpFileData]得到的图像指针变量.
/// </summary>
void E3_FreeEntBmpFileData(BYTE* FileDataBuf);

/// <summary>
/// 接口说明:1.强制停止扩展轴运动； 2.当轴以速度模式（E3_MarkerSetStepperAxisVelocityMode）进行移动，用此接口停止； 3.当轴为非等待模式下运动，用此接口停止；
/// <para>API编码:[67236723]</para>
/// <para>文档定位:硬件-资源-运动轴-动作</para>
/// </summary>
/// <param name="idMarker">:板卡ID</param>
/// <param name="axis">:需要操作的扩展轴序号；取值范围0-5</param>
e3_AxisStopForce E3_AxisStopForce = nullptr;

/// <summary>
/// 接口说明:清除指定层ID中的子对象
/// <para>API编码:[12305230]</para>
/// <para>文档定位:数据-对象操作-对象间操作</para>
/// </summary>
/// <param name="idLayer">:指定层ID</param>
/// <param name="bUpdateParentInfo">:是否更新对象列表；true更新，false不更新</param>
e3_ClearLayerAllChild E3_ClearLayerAllChild = nullptr;

/// <summary>
/// 接口说明:得到模拟输入口(ADC1~ADC4)的模拟量；
/// <para>API编码:[35667791]</para>
/// <para>文档定位:硬件-资源-模拟量IO-读</para>
/// </summary>
/// <param name="idMarker">:板卡ID</param>
/// <param name="PortNum">:模拟量输入端口；取值范围1-4；</param>
/// <param name="AnalogValue">:得到模拟量对应的bit值;当卡是MCS时，电压-10V到10V对应410到3686</param>
e3_Get3DPrintAnalogOutput E3_Get3DPrintAnalogOutput = nullptr;

/// <summary>
/// 接口说明:得到指定对象ID的三组填充参数;
/// <para>API编码:[43922762]</para>
/// <para>文档定位:数据-填充相关</para>
/// </summary>
/// <param name="idEnt">:对象ID</param>
/// <param name="bEnableContour">:是否使能轮廓;true使能，false不使能</param>
/// <param name="bContourFirst">:是否使能轮廓优先;true使能，false不使能；</param>
/// <param name="param1">:填充参数1</param>
/// <param name="param2">:填充参数2</param>
/// <param name="param3">:填充参数3</param>
e3_GetEntHatchParam E3_GetEntHatchParam = nullptr;

/// <summary>
/// 接口说明:1.得到填充对象中的填充部分（填充线对象）,一个填充对象解散之后会有轮廓和填充线对象及若干轮廓对象，此接口得到的就是填充线对象,轮廓则利用[E3_GetEntParam1]接口来获取.
/// <para>API编码:[12099349]</para>
/// <para>文档定位:数据-对象操作-对象ID关系</para>
/// </summary>
/// <param name="idEnt">:对象ID</param>
/// <param name="idEntHatch">:填充属性的对象ID</param>
e3_GetEntParam3 E3_GetEntParam3 = nullptr;

/// <summary>
/// 接口说明:1.得到slc文件中的指定层序号对应的对象ID，Z值和slc文件总层数，最小Z值，层厚，外包盒的最小最大坐标； 2.得到的对象ID，需要用接口E3_AddEntityToChild添加到指定层；
/// <para>API编码:[68119134]</para>
/// <para>文档定位:数据-3D操作</para>
/// </summary>
/// <param name="idEM">:对象管理器ID</param>
/// <param name="strFile">:slc文件完整路径</param>
/// <param name="nLayerIndex">:slc文件层序号</param>
/// <param name="nTotalLayerCount">:slc文件总层数</param>
/// <param name="dMinZLevel">:slc文件最小Z值</param>
/// <param name="dLayerThickness">:slc文件层厚</param>
/// <param name="dZ">:层序号对应的Z值</param>
/// <param name="bHaveExtents">:文件是否包括外轮廓数据;true包含，false不包含</param>
/// <param name="ptExtentsMin">:外轮廓的最小值</param>
/// <param name="ptExtentsMax">:外轮廓的最大值</param>
/// <param name="idNewEnt">:层序号对应的对象ID</param>
e3_GetOneLayerFromSlcFile2 E3_GetOneLayerFromSlcFile2 = nullptr;

/// <summary>
/// 接口说明:1.标刻九点校正标准图形（田字格图形）； 2.使用默认参数标刻，不受是否使能校正加载校正文件，是否修改振镜镜像等影响；
/// <para>API编码:[54919416]</para>
/// <para>文档定位:硬件-资源-振镜-校正</para>
/// </summary>
/// <param name="idMarker">:板卡ID</param>
/// <param name="nRectSizeDa">:标准图形对应的DA值</param>
/// <param name="nPointSizeDa">:用于区别方向的标志位对应的DA值</param>
e3_MarkCorStdPoint E3_MarkCorStdPoint = nullptr;

/// <summary>
/// 接口说明:得到MCS板卡上输入口的值；
/// <para>API编码:[01874792]</para>
/// <para>文档定位:硬件-资源-数字量IN-查询</para>
/// </summary>
/// <param name="idMarker">:板卡ID</param>
/// <param name="wPortData">:1.输入口对应的bit值; 2.共16个输入口，端口从0到15； 3.假设端口nPort，端口对应的值为usPortValue=1nPort，参数usInputData&usPortValue==usPortValue， 表明端口nPort有输入；</param>
e3_MarkerGetExtInputPortStatus E3_MarkerGetExtInputPortStatus = nullptr;

/// <summary>
/// 接口说明:得到MCS板卡上输出口的值；
/// <para>API编码:[78477434]</para>
/// <para>文档定位:硬件-资源-数字量OUT-查询</para>
/// </summary>
/// <param name="idMarker">:板卡ID</param>
/// <param name="wPortData">:1.输出口对应的bit值; 2.共24个输出口，端口从0到23； 3.假设端口nPort，端口对应的值为unPortValue=1nPort，参数unOutputData&unPortValue==unPortValue， 表明端口nPort有输出；</param>
e3_MarkerGetExtOutputPort E3_MarkerGetExtOutputPort = nullptr;

/// <summary>
/// 接口说明:1.列表功能； 2.选择打标使用的校正表序号； 3.校正表序号需要用接口E3_MarkerSetCorFile2进行设置；
/// <para>API编码:[32825130]</para>
/// <para>文档定位:硬件-资源-振镜-校正</para>
/// </summary>
/// <param name="idMarker">:板卡ID</param>
/// <param name="indexTable">:校正表号;取值范围1-4</param>
/// <param name="bEnableCor">:是否使用校正； 默认true</param>
e3_MarkerSelectCorTableToList E3_MarkerSelectCorTableToList = nullptr;

/// <summary>
/// 接口说明:给指定板卡设置指定的校正文件，需要校正文件完整路径；
/// <para>API编码:[92816036]</para>
/// <para>文档定位:硬件-资源-振镜-校正</para>
/// </summary>
/// <param name="idMarker">:板卡ID</param>
/// <param name="szFileName[256]">:校正文件完整路径</param>
e3_MarkerSetCorFile E3_MarkerSetCorFile = nullptr;

/// <summary>
/// 接口说明:设置MCS板卡上的输出口；
/// <para>API编码:[94693559]</para>
/// <para>文档定位:硬件-资源-数字量OUT-动作</para>
/// </summary>
/// <param name="idMarker">:板卡ID</param>
/// <param name="wPortData">:1.输出口对应的bit值; 2.共24个输出口，端口从0到23； 3.假设端口nPort，端口对应的值为unPortValue=1nPort，参数unOutputData&unPortValue==unPortValue， 表明端口nPort有输出；</param>
e3_MarkerSetExtOutputPort E3_MarkerSetExtOutputPort = nullptr;

/// <summary>
/// 接口说明:1.轴速度模式； 2.轴根据设定的速度限制参数（最小速度、最大速度和加速度）运动到设定的目标速度，之后一直按照设定的速度无目的的运行
/// <para>API编码:[17999409]</para>
/// <para>文档定位:硬件-资源-运动轴-动作</para>
/// </summary>
/// <param name="idMarker">:板卡ID</param>
/// <param name="nAxisNo">:扩展轴序号;取值范围0-5</param>
/// <param name="dVelocity">:目标速度</param>
e3_MarkerSetStepperAxisVelocityMode E3_MarkerSetStepperAxisVelocityMode = nullptr;

/// <summary>
/// 接口说明:将对象里的子对象进行排序
/// <para>API编码:[49368220]</para>
/// <para>文档定位:数据-对象操作-对象间操作</para>
/// </summary>
/// <param name="idEnt">:对象ID</param>
/// <param name="bYFirst">:是否按Y优先排序;true是，false否</param>
/// <param name="bMinToMax">:坐标从小到大排序;true坐标从小到大排序，false坐标从大大小排序</param>
/// <param name="bEnChangeDir">:是否可以改变曲线的方向；true改变曲线方向，false不改变曲线方向</param>
/// <param name="nFlag">:默认为0</param>
e3_ResortEntChilds E3_ResortEntChilds = nullptr;

/// <summary>
/// 接口说明:将对象里的子对象的最短路径进行排序,从第一个对象出发，以每个子对象的中心点为判断依据排序
/// <para>API编码:[64761820]</para>
/// <para>文档定位:数据-对象操作-对象间操作</para>
/// </summary>
/// <param name="idEnt">:对象ID</param>
/// <param name="nFlag">:默认为0</param>
e3_ResortEntChilds2 E3_ResortEntChilds2 = nullptr;

/// <summary>
/// 接口说明:设置模拟输出口(DAC1~DAC4)的值；
/// <para>API编码:[34850423]</para>
/// <para>文档定位:硬件-资源-模拟量IO-写</para>
/// </summary>
/// <param name="idMarker">:板卡ID</param>
/// <param name="PortNum">:模拟量输出端口;取值范围1-4</param>
/// <param name="AnalogValue">:1.模拟量值对应的bit值 2.电压值0-10V对应0-65535；</param>
e3_Set3DPrintAnalogOutput E3_Set3DPrintAnalogOutput = nullptr;

/// <summary>
/// 接口说明:设置板卡上的PWM1和PWM2的值;
/// <para>API编码:[46931907]</para>
/// <para>文档定位:硬件-资源-模拟量IO-写</para>
/// </summary>
/// <param name="idMarker">:板卡ID</param>
/// <param name="PwmNo">:PWM端口;取值范围1-2</param>
/// <param name="Freq">:1.设置频率； 2.输出频率等于20Mhz/unFreq</param>
/// <param name="Width">:1设置脉冲宽度； 2.输出脉宽等于unPulseWidth*0.05（一个脉宽是50ns）</param>
e3_Set3DPrintPWMOutput E3_Set3DPrintPWMOutput = nullptr;

/// <summary>
/// 接口说明:生成并保存九点校正文件到指定路径下
/// <para>API编码:[03311905]</para>
/// <para>文档定位:硬件-资源-振镜-校正</para>
/// </summary>
/// <param name="idMarker">:板卡ID</param>
/// <param name="nDaSize">:标刻标准九点图形时的DA值；与接口E3_MarkCorStdPoint中参数nRectSizeDa一致</param>
/// <param name="nMode">:确定振镜的方向；取值范围0-7； 0：[X=振镜1][Y=振镜2]; 1：[X=振镜1,反向][Y=振镜2]; 2：[X=振镜1,反向][Y=振镜2,反向]; 3：[X=振镜1][Y=振镜2,反向]; 4：[X=振镜2,反向][Y=振镜1]; 5：[X=振镜2,反向][Y=振镜1,反向]; 6：[X=振镜2][Y=振镜1,反向]; 7：[X=振镜2][Y=振镜1]; 每个取值都代表一种标准九点图形，每个图形只是方向不同，此值需要与E3_MarkCorStdPoint标刻出来的图形一致；</param>
/// <param name="ptCoor[9][2]">:1.九点实际测量值； 2.每个点坐标是到中心十字线的距离； 3.点的顺序为左上角第一个点，从左到右，从上到下；</param>
e3_Set3x3PointCor E3_Set3x3PointCor = nullptr;

/// <summary>
/// 接口说明:生成并保存多点校正文件到指定路径下
/// <para>API编码:[44397002]</para>
/// <para>文档定位:硬件-资源-振镜-校正</para>
/// </summary>
/// <param name="idMarker">:板卡ID</param>
/// <param name="dFieldSize">:多点数据的理论区域；最外围两点中心点间距；</param>
/// <param name="row">:多点校正的列数,需要是奇数</param>
/// <param name="col">:多点校正的列数,需要是奇数</param>
/// <param name="ptCoor[][2]">:1.多点实际测量值； 2.每个点坐标到中心点的距离，数值带正负号； 3.点的顺序为左下角为第一个点，从左到右，从下到上；</param>
e3_SetMultiPointCor E3_SetMultiPointCor = nullptr;

/// <summary>
/// 接口说明:互换指定序号的两层对象顺序
/// <para>API编码:[72889431]</para>
/// <para>文档定位:数据-对象操作-对象间操作</para>
/// </summary>
/// <param name="idEM">:对象管理器ID</param>
/// <param name="nLayerIndex1">:要互换的第1个图层序号，取值范围从0开始</param>
/// <param name="nLayerIndex2">:要互换的第2个图层序号，取值范围从0开始</param>
/// <param name="bUndo">:预留参数,默认False</param>
/// <param name="strUndoName">:预留参数,默认 ""</param>
e3_ChangeOrderLayer E3_ChangeOrderLayer = nullptr;

/// <summary>
/// 接口说明:1.多张打标卡时，只能用此接口释放扩展轴； 2.单卡时，可以用此接口释放扩展轴；
/// <para>API编码:[51167952]</para>
/// <para>文档定位:硬件-资源-运动轴-动作</para>
/// </summary>
/// <param name="idMarker">:板卡ID</param>
e3_CloseMotionMgrOfMarker E3_CloseMotionMgrOfMarker = nullptr;

/// <summary>
/// 接口说明:导入stl文件
/// <para>API编码:[17932665]</para>
/// <para>文档定位:数据-3D操作</para>
/// </summary>
/// <param name="idEM">:对象管理器ID</param>
/// <param name="strStlFile">:stl文件完整路径</param>
/// <param name="bAddMode">:是否为追加模式;true为追加模式，false覆盖上次导入的stl文件</param>
/// <param name="bPick">:预留参数,默认false;</param>
e3_CreateAddStlFile E3_CreateAddStlFile = nullptr;

/// <summary>
/// 接口说明:创建三阶贝塞尔曲线
/// <para>API编码:[16838888]</para>
/// <para>文档定位:数据-标准图元-创建</para>
/// </summary>
/// <param name="idEM">:对象管理器ID</param>
/// <param name="nPen">:笔号，范围0-255</param>
/// <param name="ptLines">:1.曲线对应的点数组； 2.数组长度为4+3(n-1),n=1;</param>
/// <param name="nPointCount">:为数组ptLines的长度；</param>
/// <param name="reserved1">:预留接口.默认值:flase</param>
/// <param name="reserved2">:预留接口.默认值:flase</param>
/// <param name="reserved3">:预留接口.默认值""</param>
e3_CreateBeziers E3_CreateBeziers = nullptr;

/// <summary>
/// 接口说明:1.创建三阶贝塞尔曲线； 2.如果添加多条贝塞尔曲线，可以将参数bUpdateParentInfo设置为false，在最后一次添加的时候设置成true，这样可以避免大量创建时由于更新对象列表导致卡顿；
/// <para>API编码:[37103428]</para>
/// <para>文档定位:数据-标准图元-创建</para>
/// </summary>
/// <param name="idEM">:对象管理器ID</param>
/// <param name="nPen">:笔号，范围0-255</param>
/// <param name="ptLines">:1.曲线对应的点数组； 2.数组长度为4+3(n-1),n=1;</param>
/// <param name="nPointCount">:为数组ptLines的长度；</param>
/// <param name="bUpdateParentInfo">:是否更新列表信息；true为更新，false为不更新</param>
/// <param name="idNewEnt">:创建贝塞尔曲线对象ID</param>
e3_CreateBeziers_2 E3_CreateBeziers_2 = nullptr;

/// <summary>
/// 接口说明:删除填充对象的填充属性；
/// <para>API编码:[30342248]</para>
/// <para>文档定位:数据-填充相关</para>
/// </summary>
/// <param name="idEM">:对象管理器ID</param>
/// <param name="idEnt">:对象ID</param>
/// <param name="reserved1">:预留接口，默认值false</param>
/// <param name="reserved2">:预留接口，默认值为“”</param>
e3_DelEntHatchParam E3_DelEntHatchParam = nullptr;

/// <summary>
/// 接口说明:删除填充对象的填充属性；
/// <para>API编码:[25181608]</para>
/// <para>文档定位:数据-填充相关</para>
/// </summary>
/// <param name="idEM">:对象管理器ID</param>
/// <param name="idEnt">:对象ID</param>
e3_DelEntHatchParam_2 E3_DelEntHatchParam_2 = nullptr;

/// <summary>
/// 接口说明:删除指定对象的所有子对象，不删除它自己;比如删除层对象中的所有对象；
/// <para>API编码:[92495733]</para>
/// <para>文档定位:数据-对象操作-对象间操作</para>
/// </summary>
/// <param name="idEnt">:对象ID</param>
e3_DeleteAllChildOfEnt E3_DeleteAllChildOfEnt = nullptr;

/// <summary>
/// 接口说明:删除指定对象
/// <para>API编码:[04369686]</para>
/// <para>文档定位:数据-对象操作-对象通用读写</para>
/// </summary>
/// <param name="idEnt">:对象ID</param>
e3_DeleteEnt E3_DeleteEnt = nullptr;

/// <summary>
/// 接口说明:删除指定序号的层对象
/// <para>API编码:[11781849]</para>
/// <para>文档定位:数据-对象操作-对象通用读写</para>
/// </summary>
/// <param name="idEM">:对象管理器ID</param>
/// <param name="nLayerindex">:指定层序号；取值范围从0开始</param>
/// <param name="reserved1">:预留接口，默认值false</param>
/// <param name="reserved2">:预留接口，默认值为“”</param>
e3_DeleteLayer E3_DeleteLayer = nullptr;

/// <summary>
/// 接口说明:删除指定序号的层对象
/// <para>API编码:[16622624]</para>
/// <para>文档定位:数据-对象操作-对象通用读写</para>
/// </summary>
/// <param name="idEM">:对象管理器ID</param>
/// <param name="nLayerindex">:指定层序号；取值范围从0开始</param>
e3_DeleteLayer2 E3_DeleteLayer2 = nullptr;

/// <summary>
/// 接口说明:1.造型，包括焊接对象，修剪对象，交叉对象； 2.当修剪的时候，两个对象ID输入接口的顺序会影响结果；其它两种造型不会受对象顺序影响；
/// <para>API编码:[81875862]</para>
/// <para>文档定位:数据-对象操作-对象间操作</para>
/// </summary>
/// <param name="idEM">:对象管理器ID</param>
/// <param name="idEnt1">:对象ID1</param>
/// <param name="idEnt2">:对象ID2</param>
/// <param name="nMode">:造型模式； 1.nMode=0 焊接对象； 2.nMode=1 修剪对象； 3.nMode=2 交叉对象；</param>
/// <param name="nPen">:造型之后对象的笔号；取值范围0-255</param>
/// <param name="reserved1">:预留接口，默认值false</param>
/// <param name="reserved2">:预留接口，默认值为“”</param>
e3_DistortionEntity E3_DistortionEntity = nullptr;

/// <summary>
/// 接口说明:1.造型，包括焊接对象，修剪对象，交叉对象； 2.当修剪的时候，两个对象ID输入接口的顺序会影响结果；其它两种造型不会受对象顺序影响；
/// <para>API编码:[88335574]</para>
/// <para>文档定位:数据-对象操作-对象间操作</para>
/// </summary>
/// <param name="idEM">:对象管理器ID</param>
/// <param name="idEnt1">:对象ID1</param>
/// <param name="idEnt2">:对象ID2</param>
/// <param name="nMode">:造型模式； 1.nMode=0 焊接对象； 2.nMode=1 修剪对象； 3.nMode=2 交叉对象；</param>
/// <param name="nPen">:造型之后对象的笔号；取值范围0-255</param>
e3_DistortionEntity_2 E3_DistortionEntity_2 = nullptr;

/// <summary>
/// 接口说明:生成并保存多点校正文件
/// <para>API编码:[30210049]</para>
/// <para>文档定位:硬件-资源-振镜-校正</para>
/// </summary>
/// <param name="strOldCorFile">:旧校正文件完整路径；此校正文件为打标多点时使用的校正文件；</param>
/// <param name="strNewCorFile">:生成新的校正文件完整路径</param>
/// <param name="ptGridReal">:1.多点实际测量值； 2.每个点坐标到中心点的距离，数值带正负号； 3.点的顺序为左下角为第一个点，从左到右，从下到上；</param>
/// <param name="nCountX">:多点X方向个数</param>
/// <param name="nCountY">:多点Y方向个数</param>
/// <param name="dGridLBX">:点阵左下角X理论坐标</param>
/// <param name="dGridLBY">:点阵左下角Y理论坐标</param>
/// <param name="dGridDisX">:点阵X方向理论间距</param>
/// <param name="dGridDisY">:点阵X方向理论间距</param>
e3_FunCF E3_FunCF = nullptr;

/// <summary>
/// 接口说明:生成并保存九点校正文件
/// <para>API编码:[77011660]</para>
/// <para>文档定位:硬件-资源-振镜-校正</para>
/// </summary>
/// <param name="idMarker">:板卡ID</param>
/// <param name="strNewFile">:保存九点校正文件完整路径</param>
/// <param name="nPointMode">:确定振镜的方向；取值范围0-7； 0：[X=振镜1][Y=振镜2]; 1：[X=振镜1,反向][Y=振镜2]; 2：[X=振镜1,反向][Y=振镜2,反向]; 3：[X=振镜1][Y=振镜2,反向]; 4：[X=振镜2,反向][Y=振镜1]; 5：[X=振镜2,反向][Y=振镜1,反向]; 6：[X=振镜2][Y=振镜1,反向]; 7：[X=振镜2][Y=振镜1]; 每个取值都代表一种标准九点图形，每个图形只是方向不同，此值需要与E3_MarkCorStdPoint2标刻出来的图形一致；</param>
/// <param name="dPts">:1.九点实际测量值； 2.每个点坐标是到中心十字线的距离； 3.点的顺序为左上角第一个点，从左到右，从上到下；</param>
/// <param name="dFiledSize">:1.标刻幅面大小（一般就是指场镜的理论值，比如是110的场镜，这个值就是可以填写110）； 2.与接口E3_MarkCorStdPoint2中参数dFiledSize保持一致</param>
/// <param name="dBoxSize">:1.标刻矩形尺寸（标准九点图形的尺寸，要给多大的幅面做矫正）； 2.与接口E3_MarkCorStdPoint2中参数dBoxSize保持一致</param>
e3_FunCF9 E3_FunCF9 = nullptr;

/// <summary>
/// 接口说明:获取填充参数，可以得到三组填充参数
/// <para>API编码:[40863716]</para>
/// <para>文档定位:数据-填充相关</para>
/// </summary>
/// <param name="idEnt">:对象ID</param>
/// <param name="bEnableContour">:是否使能轮廓;true使能，false不使能</param>
/// <param name="bContourFirst">:是否使能轮廓优先;true使能，false不使能；</param>
/// <param name="param1">:填充参数1</param>
/// <param name="param2">:填充参数2</param>
/// <param name="param3">:填充参数3</param>
e3_GetHatchParam E3_GetHatchParam = nullptr;

/// <summary>
/// 接口说明:获取填充参数，最多可以得到八组填充参数
/// <para>API编码:[26453245]</para>
/// <para>文档定位:数据-填充相关</para>
/// </summary>
/// <param name="idEnt">:对象ID</param>
/// <param name="bEnableContour">:是否使能轮廓;true使能，false不使能</param>
/// <param name="bContourFirst">:是否使能轮廓优先;true使能，false不使能；</param>
/// <param name="nHatchParamCount">:得到填充参数的组数</param>
/// <param name="pParam">:填充参数；可以传入填充参数数组的第一个元素</param>
e3_GetHatchParam2 E3_GetHatchParam2 = nullptr;

/// <summary>
/// 接口说明:得到指定路径下stl模型的尺寸
/// <para>API编码:[04351611]</para>
/// <para>文档定位:数据-3D操作</para>
/// </summary>
/// <param name="idEM">:对象管理器ID</param>
/// <param name="strStlFile">:stl文件完整路径</param>
/// <param name="minx">:stl模型的最小X坐标;</param>
/// <param name="miny">:stl模型的最小Y坐标;</param>
/// <param name="maxx">:stl模型的最大X坐标;</param>
/// <param name="maxy">:stl模型的最大Y坐标;</param>
/// <param name="minz">:stl模型的最小Z坐标;</param>
/// <param name="maxz">:stl模型的最大Z坐标;</param>
e3_GetStlFileSize E3_GetStlFileSize = nullptr;

/// <summary>
/// 接口说明:1.填充指定对象; 2.当被填充的对象为非填充对象时，只能用此接口； 3.当被填充的对象时填充对象，可以用此接口，也可以用E3_SetHatchParam或者E3_SetHatchParam2修改填充参数 4.非填充对象填充之后，对象ID会发生变化
/// <para>API编码:[45830240]</para>
/// <para>文档定位:数据-填充相关</para>
/// </summary>
/// <param name="idEnt">:对象ID</param>
/// <param name="bEnableContour">:是否使能轮廓;true使能，false不使能</param>
/// <param name="bContourFirst">:是否使能轮廓优先;true使能，false不使能；</param>
/// <param name="param1">:填充参数1</param>
/// <param name="param2">:填充参数2</param>
/// <param name="param3">:得到填充参数3</param>
e3_HatchEnt E3_HatchEnt = nullptr;

/// <summary>
/// 接口说明:1.填充指定对象，最多八组填充参数； 2.当被填充的对象为非填充对象时，只能用此接口； 3.当被填充的对象时填充对象，可以用此接口，也可以用E3_SetHatchParam或者E3_SetHatchParam2修改填充参数
/// <para>API编码:[76283542]</para>
/// <para>文档定位:数据-填充相关</para>
/// </summary>
/// <param name="idEnt">:对象ID</param>
/// <param name="bEnableContour">:是否使能轮廓;true使能，false不使能</param>
/// <param name="bContourFirst">:是否使能轮廓优先;true使能，false不使能；</param>
/// <param name="nHatchParamCount">:填充参数数组paramList长度；范围1-8</param>
/// <param name="pParam">:填充参数数组</param>
/// <param name="idEntHatch">:填充之后的对象ID</param>
e3_HatchEnt2 E3_HatchEnt2 = nullptr;

/// <summary>
/// 接口说明:背景填充，用对象idEntBack当背景填充对象idEnt
/// <para>API编码:[48449352]</para>
/// <para>文档定位:数据-填充相关</para>
/// </summary>
/// <param name="idEnt">:对象ID</param>
/// <param name="idEntBack">:背景对象ID</param>
/// <param name="bEnableContour">:是否使能轮廓;true使能，false不使能</param>
/// <param name="bContourFirst">:是否使能轮廓优先;true使能，false不使能；</param>
/// <param name="bDeleteOldEnt">:是否删除</param>
/// <param name="idNewEnt">:填充后得到的填充对象的ID</param>
e3_HatchEntByBack E3_HatchEntByBack = nullptr;

/// <summary>
/// 接口说明:1.多张打标卡时，只能用此接口初始化扩展轴； 2.单卡时，可以用此接口初始化扩展轴；
/// <para>API编码:[45079026]</para>
/// <para>文档定位:硬件-资源-运动轴-动作</para>
/// </summary>
/// <param name="idMarker">:板卡ID</param>
/// <param name="nIndexOfParamFile">:配置文件对应的序号； 从0开始，nIndexOfParamFile=0使用参数文件Motors.ini; nIndexOfParamFile=1使用Motors1.ini; nIndexOfParamFile=2使用Motors2.ini；以此类推；</param>
e3_InitMotorMgrOfMarker E3_InitMotorMgrOfMarker = nullptr;

/// <summary>
/// 接口说明:判断指定序号的扩展轴是否有故障
/// <para>API编码:[43163621]</para>
/// <para>文档定位:硬件-资源-运动轴-查询</para>
/// </summary>
/// <param name="idMarker">:板卡ID</param>
/// <param name="axis">:扩展轴序号;取值范围0-5</param>
/// <param name="bIsFault">:序号对应的扩展轴是否有故障；true表示存在故障,false不存在故障</param>
e3_IsAxisHaveFault E3_IsAxisHaveFault = nullptr;

/// <summary>
/// 接口说明:判断指定序号的扩展轴是否使能零点，是否已经回过零
/// <para>API编码:[18270977]</para>
/// <para>文档定位:硬件-资源-运动轴-查询</para>
/// </summary>
/// <param name="idMarker">:板卡ID</param>
/// <param name="axis">:扩展轴序号;取值范围0-5</param>
/// <param name="bIsHaveHome">:扩展轴是否使能零点;true使能了零点，false未使能零点</param>
/// <param name="bIsAlreadyFindHome">:扩展轴是否已经回过零;true扩展轴已经回过零，false扩展轴未回过零；</param>
e3_IsAxisHaveHome E3_IsAxisHaveHome = nullptr;

/// <summary>
/// 接口说明:判断指定序号的扩展轴是否正在运动
/// <para>API编码:[75546172]</para>
/// <para>文档定位:硬件-资源-振镜-状态查询</para>
/// </summary>
/// <param name="idMarker">:板卡ID</param>
/// <param name="axis">:扩展轴序号;取值范围0-5</param>
/// <param name="bIsMoving">:扩展轴是否正在运动；true扩展轴正在运动，false扩展轴为静止</param>
e3_IsAxisMoving E3_IsAxisMoving = nullptr;

/// <summary>
/// 接口说明:1.标刻九点校正标准图形（田字格图形）； 2.使用默认参数标刻，不受是否使能校正加载校正文件，是否修改振镜镜像等影响；
/// <para>API编码:[84116983]</para>
/// <para>文档定位:硬件-资源-振镜-校正</para>
/// </summary>
/// <param name="idMarker">:板卡ID</param>
/// <param name="dFieldSize">:标刻幅面大小（标刻幅面大小一般就是指场镜的理论值，比如是110的场镜，这个值就是可以填写110）,单位毫米;</param>
/// <param name="dBoxSize">:标刻矩形尺寸（要给多大的幅面做矫正）,单位毫米;</param>
e3_MarkCorStdPoint2 E3_MarkCorStdPoint2 = nullptr;

/// <summary>
/// 接口说明:1.选择打标使用的校正表序号； 2.校正表序号需要用接口E3_MarkerSetCorFile2进行设置；
/// <para>API编码:[24343039]</para>
/// <para>文档定位:硬件-资源-振镜-校正</para>
/// </summary>
/// <param name="idMarker">:板卡ID</param>
/// <param name="indexTable">:校正表号;取值范围1-4</param>
/// <param name="bEnableCor">:是否使用校正； 默认true</param>
e3_MarkerSelectCorTable E3_MarkerSelectCorTable = nullptr;

/// <summary>
/// 接口说明:镜像指定对象
/// <para>API编码:[58887993]</para>
/// <para>文档定位:数据-对象操作-对象通用读写</para>
/// </summary>
/// <param name="idEnt">:对象ID</param>
/// <param name="dCenx">:镜像中心X坐标</param>
/// <param name="dCeny">:镜像中心Y坐标</param>
/// <param name="bMirrorX">:是否X方向镜像;true镜像，false不镜像</param>
/// <param name="bMirrorY">:是否Y方向镜像;true镜像，false不镜像；</param>
e3_MirrorEnt E3_MirrorEnt = nullptr;

/// <summary>
/// 接口说明:移动指定对象到指定序号，用于调整对象在对象列表中的顺序
/// <para>API编码:[18149409]</para>
/// <para>文档定位:数据-对象操作-对象间操作</para>
/// </summary>
/// <param name="idEM">:对象管理器ID</param>
/// <param name="idEnt">:对象ID</param>
/// <param name="nIndex">:对象列表中的序号;取值范围从0开始；</param>
e3_MoveEntToIndex E3_MoveEntToIndex = nullptr;

/// <summary>
/// 接口说明:指定对象Z方向移动指定距离
/// <para>API编码:[27419263]</para>
/// <para>文档定位:数据-对象操作-对象通用读写</para>
/// </summary>
/// <param name="idEnt">:对象ID</param>
/// <param name="dMoveZ">:Z方向移动的距离</param>
e3_MoveEntZ E3_MoveEntZ = nullptr;

/// <summary>
/// 接口说明:1.旋转和移动指定对象； 2.指定对象先绕指定中心旋转,然后移动指定距离
/// <para>API编码:[12175561]</para>
/// <para>文档定位:数据-对象操作-对象通用读写</para>
/// </summary>
/// <param name="idEnt">:对象ID</param>
/// <param name="dMoveX">:X方向移动距离</param>
/// <param name="dMoveY">:Y方向移动距离</param>
/// <param name="dCenterX">:旋转中心x坐标</param>
/// <param name="dCenterY">:旋转中心y坐标</param>
/// <param name="dRotateAng">:1.旋转角度（弧度值）; 2.正值为逆时针旋转，负值为顺时针;</param>
e3_MoveRotateEnt E3_MoveRotateEnt = nullptr;

/// <summary>
/// 接口说明:1.对指定对象进行投影，包裹等； 2.圆柱包裹，球面包裹不需要stl文件，其它动作需要先加载stl文件
/// <para>API编码:[31129690]</para>
/// <para>文档定位:数据-3D操作</para>
/// </summary>
/// <param name="idEM">:对象管理器ID</param>
/// <param name="idEnt">:对象ID</param>
/// <param name="nProjectMode">:投影模式:    0：投影模式;    1：包裹;    2：圆柱包裹;    3：球面包裹;    4：旋转体包裹;    5：包裹XY;</param>
/// <param name="bDownProject">:是否为下曲面投影</param>
/// <param name="dLimetZ">:Z极限值；小于Z极限值的部分将不进行投影</param>
/// <param name="dDefaultZ">:默认Z值</param>
/// <param name="bRemoveNoInter">:是否移除未相交线段；true移除，false保留</param>
/// <param name="bCylinderX">:当模式选0包裹时，true为X方向包裹，否则为Y方向包裹</param>
/// <param name="dCylinderDiameter">:圆柱包裹，球面包裹时的直径</param>
e3_ProjectEnt_2 E3_ProjectEnt_2 = nullptr;

/// <summary>
/// 接口说明:保存Ez3文件
/// <para>API编码:[51171353]</para>
/// <para>文档定位:数据-文件读写</para>
/// </summary>
/// <param name="pStrFileName">:ez3文件完整路径</param>
/// <param name="idEM">:对象管理器ID</param>
/// <param name="bSelect">:是否仅保存当前选中内容;true保存当前选中内容, false保存全部内容</param>
/// <param name="bPreImage">:是否保存预览图.true保存预览图,false不保存预览图</param>
/// <param name="strAuthor">:作者信息.默认为空("");</param>
/// <param name="strTime">:时间信息.默认为空("");</param>
/// <param name="strNotes">:备注信息.默认为空("");</param>
e3_SaveEntMgrToFile E3_SaveEntMgrToFile = nullptr;

/// <summary>
/// 接口说明:保存扩展轴参数到指定配置文件中;配置文件参考E3_InitMotorMgrOfMarker中的nIndexOfMotorFile
/// <para>API编码:[81432735]</para>
/// <para>文档定位:硬件-资源-运动轴-配置</para>
/// </summary>
/// <param name="idMarker">:板卡ID</param>
e3_SaveMotionMgrParamToFile E3_SaveMotionMgrParamToFile = nullptr;

/// <summary>
/// 接口说明:1.修改填充参数； 2.当对象为填充对象时，使用此接口修改填充参数；
/// <para>API编码:[20852974]</para>
/// <para>文档定位:数据-填充相关</para>
/// </summary>
/// <param name="idEM">:对象管理器ID</param>
/// <param name="idEnt">:对象ID</param>
/// <param name="bEnableContour">:是否使能轮廓;true使能，false不使能</param>
/// <param name="bContourFirst">:是否使能轮廓优先;true使能，false不使能；</param>
/// <param name="param1">:填充参数1</param>
/// <param name="param2">:填充参数2</param>
/// <param name="param3">:填充参数3</param>
e3_SetHatchParam E3_SetHatchParam = nullptr;

/// <summary>
/// 接口说明:1.修改填充参数，最多可以设置八组填充参数； 2.当对象为填充对象时，使用此接口修改填充参数；
/// <para>API编码:[23608755]</para>
/// <para>文档定位:数据-填充相关</para>
/// </summary>
/// <param name="idEM">:对象管理器ID</param>
/// <param name="idEnt">:对象ID</param>
/// <param name="bEnableContour">:是否使能轮廓;true使能，false不使能</param>
/// <param name="bContourFirst">:是否使能轮廓优先;true使能，false不使能；</param>
/// <param name="nHatchParamCount">:填充参数数组paramList长度；范围1-8</param>
/// <param name="pParam">:填充参数数组</param>
e3_SetHatchParam2 E3_SetHatchParam2 = nullptr;

/// <summary>
/// 接口说明:1.设置是否多头同步和同步使用的输入输出口； 2.需要有硬件支持；
/// <para>API编码:[70124665]</para>
/// <para>文档定位:环境-控制卡-配置</para>
/// </summary>
/// <param name="b">:是否使能同步功能;true使能同步功能，不使能同步功能</param>
/// <param name="nInportIndex">:输入口端口</param>
/// <param name="nOutportIndex">:输出口端口</param>
e3_SetMultiCardSyn E3_SetMultiCardSyn = nullptr;

/// <summary>
/// 接口说明:设置是否按照曲线同步
/// <para>API编码:[06519769]</para>
/// <para>文档定位:环境-控制卡-配置</para>
/// </summary>
/// <param name="b">:是否按照曲线同步；true 按曲线同步，false按照对象同步</param>
e3_SetMultiCardSynEveryCurve E3_SetMultiCardSynEveryCurve = nullptr;

/// <summary>
/// 接口说明:设置是否同步完成
/// <para>API编码:[21675899]</para>
/// <para>文档定位:环境-控制卡-配置</para>
/// </summary>
/// <param name="b">:是否同步完成；true同步完成，false不用同步完成</param>
e3_SetMultiCardSynWhenFinish E3_SetMultiCardSynWhenFinish = nullptr;

/// <summary>
/// 接口说明:将指定路径的stl文件进行切片到指定图层中
/// <para>API编码:[84332886]</para>
/// <para>文档定位:数据-3D操作</para>
/// </summary>
/// <param name="idLayer">:图层ID</param>
/// <param name="strStlFile">:stl文件完整路径</param>
/// <param name="strName">:切片后对象名称前缀</param>
/// <param name="bZUpToDown">:按照从上到下的顺序切片;true从上到下进行切片，false从下到上进行切片;影响切片之后对象顺序;</param>
/// <param name="dMinZ">:切片范围最小Z坐标</param>
/// <param name="dMaxZ">:切片范围最大Z坐标</param>
/// <param name="dThickness">:切片层厚</param>
e3_SliceStlFile E3_SliceStlFile = nullptr;

/// <summary>
/// 接口说明:将指定路径的stl文件进行切片到指定图层中，并将切片之后的对象进行移动
/// <para>API编码:[81150769]</para>
/// <para>文档定位:数据-3D操作</para>
/// </summary>
/// <param name="idLayer">:图层ID</param>
/// <param name="strStlFile">:stl文件完整路径</param>
/// <param name="strName">:切片后对象名称前缀</param>
/// <param name="bZUpToDown">:按照从上到下的顺序切片;true从上到下进行切片，false从下到上进行切片;影响切片之后对象顺序;</param>
/// <param name="dMinZ">:切片范围最小Z坐标</param>
/// <param name="dMaxZ">:切片范围最大Z坐标</param>
/// <param name="dThickness">:切片层厚</param>
/// <param name="dStlOffsetX">:X方向偏移量</param>
/// <param name="dStlOffsetY">:Y方向偏移量</param>
/// <param name="dStlOffsetZ">:Z方向偏移量</param>
/// <param name="nFlag">:默认0</param>
e3_SliceStlFile2 E3_SliceStlFile2 = nullptr;

/// <summary>
/// 接口说明:得到当前层中对象的个数和所有对象的总的最小最大坐标
/// <para>API编码:[35744039]</para>
/// <para>文档定位:数据-对象操作-对象通用读写</para>
/// </summary>
/// <param name="idEM">:对象管理器ID</param>
/// <param name="nEntCount">:当前层中对象的个数</param>
/// <param name="minx">:最小X坐标</param>
/// <param name="miny">:最小X坐标</param>
/// <param name="maxx">:最大X坐标</param>
/// <param name="maxy">:最大Y坐标</param>
e3_GetAllEntCount E3_GetAllEntCount = nullptr;

/// <summary>
/// 接口说明:将指定序号层设置为当前层
/// <para>API编码:[15349028]</para>
/// <para>文档定位:数据-对象操作-对象通用读写</para>
/// </summary>
/// <param name="idEM">:对象管理器ID</param>
/// <param name="nLayerIndex">:层序号</param>
e3_SetCurLayer E3_SetCurLayer = nullptr;

/// <summary>
/// 接口说明:设置文本信息，比如字体，对齐方式，坐标，字符高度间距等
/// <para>API编码:[08420886]</para>
/// <para>文档定位:数据-标准图元-编辑-文本类型-文本</para>
/// </summary>
/// <param name="idEM">:对象管理器ID</param>
/// <param name="idEnt">:文本对象ID</param>
/// <param name="nMaxParamN">:整型数组最大长度，默认24</param>
/// <param name="nParam">:整型数组，包括字体序号，字符间距类型等</param>
/// <param name="nMaxParamD">:浮点型数组最大长度，默认16</param>
/// <param name="dParam">:浮点型数组，包括XY坐标，字符高度宽度等；</param>
/// <param name="strText">:文本对象内容，长度为4098</param>
/// <param name="strExtFile">:文本内容打标之后保存到txt中，txt文件的完整路径，长度255</param>
/// <param name="reserved1">:预留接口</param>
/// <param name="reserved2">:预留接口</param>
e3_SetEntTextInfo E3_SetEntTextInfo = nullptr;

/// <summary>
/// 接口说明:设置文本信息，比如字体，对齐方式，坐标，字符高度间距等
/// <para>API编码:[67169458]</para>
/// <para>文档定位:数据-标准图元-编辑-文本类型-文本</para>
/// </summary>
/// <param name="idEM">:对象管理器ID</param>
/// <param name="idEnt">:文本对象ID</param>
/// <param name="nMaxParamN">:整型数组最大长度，默认24</param>
/// <param name="nParam">:整型数组，包括字体序号，字符间距类型等</param>
/// <param name="nMaxParamD">:浮点型数组最大长度，默认16</param>
/// <param name="dParam">:浮点型数组，包括XY坐标，字符高度宽度等；</param>
/// <param name="strText">:文本对象内容，长度为4098</param>
/// <param name="strExtFile">:文本内容打标之后保存到txt中，txt文件的完整路径，长度255</param>
e3_SetEntTextInfo_2 E3_SetEntTextInfo_2 = nullptr;

/// <summary>
/// 接口说明:设置对象笔号
/// <para>API编码:[98721922]</para>
/// <para>文档定位:数据-笔参数相关</para>
/// </summary>
/// <param name="idEnt">:对象ID</param>
/// <param name="nPen">:笔号，取值范围0-255</param>
e3_SetEntPen E3_SetEntPen = nullptr;

/// <summary>
/// 接口说明:设置对象以及子对象笔号
/// <para>API编码:[73288904]</para>
/// <para>文档定位:数据-笔参数相关</para>
/// </summary>
/// <param name="idEnt">:对象ID</param>
/// <param name="nPen">:笔号，取值范围0-255</param>
/// <param name="nFlag">:是否对子对象生效，0x01 对子对象生效</param>
e3_SetEntPen2 E3_SetEntPen2 = nullptr;

/// <summary>
/// 接口说明:设置对象Z值
/// <para>API编码:[79548685]</para>
/// <para>文档定位:数据-对象操作-对象通用读写</para>
/// </summary>
/// <param name="idEnt">:对象ID</param>
/// <param name="z">:对象设置的Z值</param>
/// <param name="bChangeAllChildZ">:是否对子对象的Z值属性进行修改；true为修改，false为不修改；</param>
e3_SetEntityZ E3_SetEntityZ = nullptr;

/// <summary>
/// 接口说明:设置对象A值
/// <para>API编码:[06024193]</para>
/// <para>文档定位:数据-对象操作-对象通用读写</para>
/// </summary>
/// <param name="idEnt">:对象ID</param>
/// <param name="a">:对象设置的A值</param>
/// <param name="bChangeAllChildA">:是否对子对象的A值属性进行修改；true为修改，false为不修改；</param>
e3_SetEntityA E3_SetEntityA = nullptr;

/// <summary>
/// 接口说明:设置对象名称,包括层名称
/// <para>API编码:[06055636]</para>
/// <para>文档定位:数据-对象操作-对象通用读写</para>
/// </summary>
/// <param name="idEnt">:对象ID</param>
/// <param name="szEntName">:对象名称，长度99</param>
e3_SetEntityName E3_SetEntityName = nullptr;

/// <summary>
/// 接口说明:得到板卡的当前状态
/// <para>API编码:[84855759]</para>
/// <para>文档定位:环境-控制卡-操作</para>
/// </summary>
/// <param name="idMarker">:板卡ID</param>
/// <param name="data">:板卡的状态,取值 0Ready， 1Run， 2Pause， 3Error</param>
e3_MarkerGetState E3_MarkerGetState = nullptr;

/// <summary>
/// 接口说明:获取校正文件校正范围，与F3参数中的区域尺寸一致
/// <para>API编码:[40200356]</para>
/// <para>文档定位:数据-对象操作-对象通用读写</para>
/// </summary>
/// <param name="idMarker">:板卡ID</param>
/// <param name="x">:X方向范围</param>
/// <param name="y">:Y方向范围</param>
e3_MarkerGetRange E3_MarkerGetRange = nullptr;

/// <summary>
/// 接口说明:得到控制卡加工数量寄存器数据，与接口E3_MarkerChangeMarkCountToList搭配使用
/// <para>API编码:[28744430]</para>
/// <para>文档定位:数据-对象操作-对象通用读写</para>
/// </summary>
/// <param name="idMarker">:板卡ID</param>
/// <param name="n">:计数数值</param>
e3_MarkerGetMarkCount E3_MarkerGetMarkCount = nullptr;

/// <summary>
/// 接口说明:得到板卡中硬件信息
/// <para>API编码:[45436009]</para>
/// <para>文档定位:环境-控制卡-操作</para>
/// </summary>
/// <param name="idMarker">:板卡ID</param>
/// <param name="szType[256]">:板卡类型</param>
/// <param name="szVersion[256]">:板卡版本号</param>
/// <param name="szFunInfo[256]">:功能代码</param>
/// <param name="szID[256]">:激光接口卡版本</param>
e3_MarkerGetHardInfo E3_MarkerGetHardInfo = nullptr;

/// <summary>
/// 接口说明:1.得到加工预估时间； 2.先将标刻类型选为计算模式0x01000000,调用E3_MarkerMarkEnt2
/// <para>API编码:[75890477]</para>
/// <para>文档定位:硬件-组合动作-动作指令</para>
/// </summary>
/// <param name="idMarker">:板卡ID</param>
/// <param name="nTimeMs">:得到的预估时间，单位ms</param>
e3_MarkerGetCalcMarkTime E3_MarkerGetCalcMarkTime = nullptr;

/// <summary>
/// 接口说明:得到文本信息，比如字体，对齐方式，坐标，字符高度间距等
/// <para>API编码:[33789418]</para>
/// <para>文档定位:数据-标准图元-编辑-文本类型-文本</para>
/// </summary>
/// <param name="idEnt">:对象ID</param>
/// <param name="nMaxParamN">:整型数组最大长度，默认24</param>
/// <param name="nParam">:整型数组，包括字体序号，字符间距类型等</param>
/// <param name="nMaxParamD">:浮点型数组最大长度，默认16</param>
/// <param name="dParam">:浮点型数组，包括XY坐标，字符高度宽度等；</param>
e3_GetTextInfo E3_GetTextInfo = nullptr;

/// <summary>
/// 接口说明:获取文本对象中的内容
/// <para>API编码:[29286958]</para>
/// <para>文档定位:数据-标准图元-编辑-文本类型-文本</para>
/// </summary>
/// <param name="idEnt">:对象ID</param>
/// <param name="index">:保留参数，默认0</param>
/// <param name="nMaxCharLen">:文本对象内容最大长度，默认4098</param>
/// <param name="pStr">:文本对象内容</param>
e3_GetTextStringInfo E3_GetTextStringInfo = nullptr;

/// <summary>
/// 接口说明:1.获取板卡SN； 2.SN是通过拨码或者程序写到板卡中的，从0开始
/// <para>API编码:[37711635]</para>
/// <para>文档定位:环境-控制卡-操作</para>
/// </summary>
/// <param name="idMarker">:板卡ID</param>
/// <param name="sn">:板卡SN</param>
e3_GetMarkerSN E3_GetMarkerSN = nullptr;

/// <summary>
/// 接口说明:得到指定对象外包盒的最小最大坐标和对象是否为空
/// <para>API编码:[00452547]</para>
/// <para>文档定位:数据-对象操作-对象通用读写</para>
/// </summary>
/// <param name="idEnt">:对象ID</param>
/// <param name="pageMinx">:外包盒的最小X坐标</param>
/// <param name="pageMiny">:外包盒的最小Y坐标</param>
/// <param name="pageMaxx">:外包盒的最大X坐标</param>
/// <param name="pageMaxy">:外包盒的最大Y坐标</param>
/// <param name="bIsEmpty">:内容是否为空;true内容为空,false内容不为空</param>
e3_GetEntityRange E3_GetEntityRange = nullptr;

/// <summary>
/// 接口说明:得到指定对象名称
/// <para>API编码:[27501726]</para>
/// <para>文档定位:数据-对象操作-对象通用读写</para>
/// </summary>
/// <param name="idEnt">:对象ID</param>
/// <param name="szEntName[256]">:对象名称</param>
e3_GetEntityName E3_GetEntityName = nullptr;

/// <summary>
/// 接口说明:得到指定层中对象个数
/// <para>API编码:[37497213]</para>
/// <para>文档定位:数据-对象操作-对象通用读写</para>
/// </summary>
/// <param name="idLayer">:图层ID</param>
/// <param name="nCount">:对象个数</param>
e3_GetEntCountInLayer E3_GetEntCountInLayer = nullptr;

/// <summary>
/// 接口说明:得到指定对象中子对象的个数，比如群组中子对象个数或者层对象中对象个数
/// <para>API编码:[67096585]</para>
/// <para>文档定位:数据-对象操作-对象通用读写</para>
/// </summary>
/// <param name="idEnt">:对象ID</param>
/// <param name="n">:子对象个数</param>
e3_GetEntChildCount E3_GetEntChildCount = nullptr;

/// <summary>
/// 接口说明:得到指定对象的基本信息，包括对象类型，对象笔号，对象名称，对象尺寸
/// <para>API编码:[72200004]</para>
/// <para>文档定位:数据-对象操作-对象通用读写</para>
/// </summary>
/// <param name="idEnt">:对象ID</param>
/// <param name="type">:对象类型</param>
/// <param name="nPen">:笔号；取值范围0-255</param>
/// <param name="strName[256]">:对象名称</param>
/// <param name="box">:外包盒尺寸</param>
/// <param name="z">:Z坐标</param>
/// <param name="a">:A坐标</param>
e3_GetEntBaseInfo E3_GetEntBaseInfo = nullptr;

/// <summary>
/// 接口说明:将指定对象中线段按照精度要求进行连接
/// <para>API编码:[00148051]</para>
/// <para>文档定位:数据-对象操作-对象通用读写</para>
/// </summary>
/// <param name="idEnt">:对象ID</param>
/// <param name="err">:当两条线首首或者首尾或者尾首或者尾尾距离小于等于设定值值，进行连接</param>
/// <param name="nConnectFlag">:连接方式；  0x01 首首相连  0x02首尾相连  0x04尾首相连  0x08尾尾相连</param>
e3_AutoConnectChildCurve E3_AutoConnectChildCurve = nullptr;

/// <summary>
/// 接口说明:将指定对象中相交的线段按照精度去交叉点
/// <para>API编码:[18601890]</para>
/// <para>文档定位:数据-对象操作-对象通用读写</para>
/// </summary>
/// <param name="idEnt">:对象ID</param>
/// <param name="dCrossLen">:相交线段去掉的线段长度</param>
/// <param name="idNewEntGroup">:去掉交叉点之后新的对象ID,需要用接口E3_AddEntityToChild添加到指定层中</param>
e3_AutoBreakCrossEntChilds E3_AutoBreakCrossEntChilds = nullptr;

/// <summary>
/// 接口说明:将指定对象添加到其它对象的前后
/// <para>API编码:[53160759]</para>
/// <para>文档定位:数据-对象操作-对象间操作</para>
/// </summary>
/// <param name="idEM">:对象管理器ID</param>
/// <param name="idEntNew">:新的对象ID，比如E3_CopyEntity得到的复制对象</param>
/// <param name="idEntOther">:另一个对象的ID,指已经存在的对象</param>
/// <param name="bBeforeOther">:是否添加到另一个对象在对象列表中的前面；true表示idEnt添加到idEntOther前,false表示idEnt添加到idEntOther后；</param>
e3_AddEntityToOther E3_AddEntityToOther = nullptr;

/// <summary>
/// 接口说明:将新对象添加到父对象中
/// <para>API编码:[61149045]</para>
/// <para>文档定位:数据-对象操作-对象间操作</para>
/// </summary>
/// <param name="idEM">:对象管理器ID</param>
/// <param name="idEntNew">:新的对象ID，比如E3_CopyEntity得到的复制对象</param>
/// <param name="idEntNewParent">:父对象ID,比如层对象</param>
/// <param name="bToHead">:是否添加到父对象的第一个；true添加到父对象第一个，false添加到父对象最后一个</param>
e3_AddEntityToChild E3_AddEntityToChild = nullptr;

/// <summary>
/// 接口说明:标刻多点十字线阵列或者圆阵列
/// <para>API编码:[46481962]</para>
/// <para>文档定位:硬件-资源-振镜-校正</para>
/// </summary>
/// <param name="idMarker">:板卡ID</param>
/// <param name="nPtnum">:多点数目,ptBuf的长度</param>
/// <param name="ptBuf">:多点中心坐标</param>
/// <param name="dLen">:十字线的长度或者圆直径</param>
/// <param name="bMarkCenter">:是否标刻中心标志符;true会标刻X,false不标刻；</param>
/// <param name="bCircleMode">:是否为圆模式；true标刻填充圆，false标刻十字线</param>
e3_MarkCrossLines E3_MarkCrossLines = nullptr;

/// <summary>
/// 接口说明:1.释放指定对象所占的内存； 2.比如E3_CopyEntity之后，并没有将拷贝的新对象添加到层里，这时候需要释放对象内存，否则软件所占内存会增加
/// <para>API编码:[36455892]</para>
/// <para>文档定位:数据-对象操作-对象ID关系</para>
/// </summary>
/// <param name="idEnt">:对象ID</param>
e3_FreeEntity E3_FreeEntity = nullptr;

/// <summary>
/// 接口说明:添加3D曲线对象
/// <para>API编码:[83289762]</para>
/// <para>文档定位:数据-标准图元-创建</para>
/// </summary>
/// <param name="idEM">:管理器ID</param>
/// <param name="nPen">:添加曲线所用笔号[0,255]</param>
/// <param name="ptLines">:添加的3D曲线点集数组</param>
/// <param name="nPointCount">:添加的3D曲线的实际点数量</param>
/// <param name="bUpdateParentInfo">:是否更新列表</param>
/// <param name="idEnt">:新创建对象的id</param>
e3_CreateLines3d_2 E3_CreateLines3d_2 = nullptr;

/// <summary>
/// 接口说明:添加3D曲线对象
/// <para>API编码:[31035919]</para>
/// <para>文档定位:数据-标准图元-创建</para>
/// </summary>
/// <param name="idEM">:管理器ID</param>
/// <param name="nPen">:添加曲线所用笔号[0,255]</param>
/// <param name="ptLines">:添加的3D曲线点集数组</param>
/// <param name="nPointCount">:添加的3D曲线的实际点数量</param>
e3_CreateLines3d E3_CreateLines3d = nullptr;

/// <summary>
/// 接口说明:添加SVG曲线对象
/// <para>API编码:[73283338]</para>
/// <para>文档定位:数据-标准图元-创建</para>
/// </summary>
/// <param name="idEM">:管理器ID</param>
/// <param name="nPen">:添加曲线所用笔号[0,255]</param>
/// <param name="pSvgStr">:svg path路径字符串</param>
/// <param name="bUpdateParentInfo">:是否更新列表</param>
/// <param name="idEnt">:新创建SVG对象的id</param>
e3_CreateSvgPath E3_CreateSvgPath = nullptr;

/// <summary>
/// 接口说明:添加SVG曲线对象
/// <para>API编码:[38005460]</para>
/// <para>文档定位:数据-标准图元-创建</para>
/// </summary>
/// <param name="idEM">:管理器ID</param>
/// <param name="nPen">:添加曲线所用笔号[0,255]</param>
/// <param name="pSvgStr">:svg path路径字符串</param>
/// <param name="bPick">:预留接口.默认值:flase</param>
/// <param name="bUndo">:预留接口.默认值:flase</param>
/// <param name="strUndoName">:预留接口.默认值:""</param>
e3_CreateSvgPath_2 E3_CreateSvgPath_2 = nullptr;

/// <summary>
/// 接口说明:字符串形式的IP地址转换为32位无符号整形数据
/// <para>API编码:[87918644]</para>
/// <para>文档定位:环境-控制卡-配置</para>
/// </summary>
/// <param name="IPString[16]">:需要转换的IP地址，按照点分十进制表示形式，16位字节数据，低位先发，包括结束符”\0”</param>
/// <param name="&IP">:转换完成的IP地址，32位无符号整形，按照Bit Endian Byte Order顺序排列</param>
e3_EthConvertStringToIP E3_EthConvertStringToIP = nullptr;

/// <summary>
/// 接口说明:根据将已知的DLC 板卡IP地址分配到注册表中
/// <para>API编码:[42714315]</para>
/// <para>文档定位:环境-控制卡-配置</para>
/// </summary>
/// <param name="IPAddr">:板卡IP地址</param>
e3_EthRegisterCardByIP E3_EthRegisterCardByIP = nullptr;

/// <summary>
/// 接口说明:得到指定投影对象参数（当前有投影获取设置正常，当前无投影调用此接口返回值2）
/// <para>API编码:[04904722]</para>
/// <para>文档定位:数据-3D操作</para>
/// </summary>
/// <param name="idEnt">:对象ID</param>
/// <param name="nProjectMode">:投影模式： 0投影 1包裹 2圆柱包裹3：球面包裹 4：旋转体包裹 5包裹xy</param>
/// <param name="dLimetZ">:z极限值</param>
/// <param name="dDefaultZ">:默认z</param>
/// <param name="bDownProject">:下投影</param>
/// <param name="bRemoveNoInter">:移除未相交点</param>
/// <param name="dBrokenZTol">:移除未相交点垂直线断开的阈值</param>
/// <param name="bCylinderX">:绕X轴</param>
/// <param name="dCylinderDiameter">:圆柱直径</param>
/// <param name="nAlignMode">:对齐模式</param>
/// <param name="dAlignOffset">:对齐偏移</param>
/// <param name="bCurveReducePt">:对曲线进行自动减点</param>
/// <param name="dCurveReducePtTol">:自动减点计算误差</param>
e3_GetProjectEntParam E3_GetProjectEntParam = nullptr;

/// <summary>
/// 接口说明:标刻一组点
/// <para>API编码:[37414844]</para>
/// <para>文档定位:硬件-加工动作-列表命令-对象级列表命令</para>
/// </summary>
/// <param name="idMarker">:板卡ID</param>
/// <param name="type">:默认为0</param>
/// <param name="pen">:笔号[0,255]</param>
/// <param name="ptNum">:标刻点数</param>
/// <param name="nFlag">:标刻标志位，</param>
/// <param name="ptBuf[][2]">:标刻点坐标数组</param>
e3_MarkerPointsToList E3_MarkerPointsToList = nullptr;

/// <summary>
/// 接口说明:设置错误复位信号
/// <para>API编码:[76501316]</para>
/// <para>文档定位:硬件-资源-激光-配置</para>
/// </summary>
/// <param name="idMarker">:板卡ID</param>
e3_MarkerResetLaserError E3_MarkerResetLaserError = nullptr;

/// <summary>
/// 接口说明:保存CFG文件
/// <para>API编码:[55026092]</para>
/// <para>文档定位:环境-控制卡-配置</para>
/// </summary>
/// <param name="idMarker">:板卡ID</param>
e3_MarkerSaveCfg E3_MarkerSaveCfg = nullptr;

/// <summary>
/// 接口说明:检测输入口在不同的列表索引对象之间跳转；（列表执行等待，检查输入口的状态满足条件之后，列表运行到相对应的列表索引对象处开始执行列表，列表索引对象之前指令不再执行，若不满足条件则一直等待）
/// <para>API编码:[20948937]</para>
/// <para>文档定位:硬件-组合动作-列表命令-列表过程命令</para>
/// </summary>
/// <param name="idMarker">:板卡ID</param>
/// <param name="wMask">:端口 端口 Bit0表示端口0， Bit1表示端口1...... （端口掩码：需检测的端口号，如要测试端口0和端口1的状态，此值为3）</param>
/// <param name="wLevel">:端口满足条件后的比较值 bit=1表示高电平，bit=0表示低电平，（若掩码为3，需检测端口1为高电平时，此值则为2，需检测端口0和端口1均为高电平时，此值则为3）</param>
/// <param name="nIndex">:跳转到的索引号[0-255]</param>
e3_MarkerSetInputJumpIndexToList E3_MarkerSetInputJumpIndexToList = nullptr;

/// <summary>
/// 接口说明:投影指定对象
/// <para>API编码:[07805088]</para>
/// <para>文档定位:数据-3D操作</para>
/// </summary>
/// <param name="idEM">:管理器ID</param>
/// <param name="idEnt">:对象ID</param>
/// <param name="nProjectMode">:模式</param>
/// <param name="bDownProject">:从下往上投影</param>
/// <param name="dLimetZ">:Z极限值</param>
/// <param name="dDefaultZ">:Z默认值</param>
/// <param name="bRemoveNoInter">:移除未相交点</param>
/// <param name="bCylinderX">:</param>
/// <param name="dCylinderDiameter">:</param>
/// <param name="bUndo">:预留参数默认false</param>
/// <param name="strUndo">:预留接口，默认空</param>
e3_ProjectEnt E3_ProjectEnt = nullptr;

/// <summary>
/// 接口说明:投影对象删除投影
/// <para>API编码:[74390126]</para>
/// <para>文档定位:数据-3D操作</para>
/// </summary>
/// <param name="idEnt">:对象ID</param>
e3_ProjectEntDelete E3_ProjectEntDelete = nullptr;

/// <summary>
/// 接口说明:设置指定投影对象参数（当前无投影调用此接口返回值2）
/// <para>API编码:[51831403]</para>
/// <para>文档定位:数据-3D操作</para>
/// </summary>
/// <param name="idEnt">:对象ID</param>
/// <param name="nProjectMode">:投影模式： 0投影 1包裹 2圆柱包裹3：球面包裹 4：旋转体包裹 5包裹xy</param>
/// <param name="dLimetZ">:z极限值</param>
/// <param name="dDefaultZ">:默认z</param>
/// <param name="bDownProject">:下投影</param>
/// <param name="bRemoveNoInter">:移除未相交点</param>
/// <param name="dBrokenZTol">:移除未相交点垂直线断开的阈值</param>
/// <param name="bCylinderX">:绕X轴</param>
/// <param name="dCylinderDiameter">:圆柱直径</param>
/// <param name="nAlignMode">:对齐模式</param>
/// <param name="dAlignOffset">:对齐偏移</param>
/// <param name="bCurveReducePt">:对曲线进行自动减点</param>
/// <param name="dCurveReducePtTol">:自动减点计算误差</param>
e3_SetProjectEntParam E3_SetProjectEntParam = nullptr;

/// <summary>
/// 接口说明:开启winsock接口库（一般程序开始时调用）
/// <para>API编码:[94857247]</para>
/// <para>文档定位:环境-控制卡-配置</para>
/// </summary>
e3_WSAStartUp E3_WSAStartUp = nullptr;

/// <summary>
/// 接口说明:添加图层（此接口需用得到层id接口得到层id）
/// <para>API编码:[97303186]</para>
/// <para>文档定位:数据-对象操作-对象通用读写</para>
/// </summary>
/// <param name="idEM">:管理器ID</param>
/// <param name="bUndo">:预留接口默认false</param>
/// <param name="strUndoName">:预留接口，默认""</param>
e3_AddLayer E3_AddLayer = nullptr;

/// <summary>
/// 接口说明:添加图层（此接口可返回添加的层id）
/// <para>API编码:[97753596]</para>
/// <para>文档定位:数据-对象操作-对象通用读写</para>
/// </summary>
/// <param name="idEM">:管理器ID</param>
/// <param name="idNewLayer">:返回的图层id</param>
e3_AddNewLayer E3_AddNewLayer = nullptr;

/// <summary>
/// 接口说明:对对象的曲线中的直线进行自动减点
/// <para>API编码:[26883381]</para>
/// <para>文档定位:数据-对象操作-对象间操作</para>
/// </summary>
/// <param name="idEnt">:对象ID</param>
/// <param name="dMinDistTol">:曲线离散误差（mm）</param>
e3_AutoReduceCurvePt E3_AutoReduceCurvePt = nullptr;

/// <summary>
/// 接口说明:关闭控制卡
/// <para>API编码:[71801712]</para>
/// <para>文档定位:环境-初始化以及释放</para>
/// </summary>
/// <param name="idMarker">:控制卡的ID;</param>
e3_CloseMarker E3_CloseMarker = nullptr;

/// <summary>
/// 接口说明:复制对象
/// <para>API编码:[05546620]</para>
/// <para>文档定位:数据-对象操作-对象间操作</para>
/// </summary>
/// <param name="idEnt">:被复制对象的ID</param>
e3_CopyEntity E3_CopyEntity = nullptr;

/// <summary>
/// 接口说明:添加圆（新添加对象id需使用得到对象id接口获取）
/// <para>API编码:[27363120]</para>
/// <para>文档定位:数据-标准图元-创建</para>
/// </summary>
/// <param name="idEM">:管理器ID</param>
/// <param name="nPen">:笔号[0,255]</param>
/// <param name="pt1">:圆中心坐标</param>
/// <param name="pt2">:圆半径,此坐标与圆心坐标距离即为半径.</param>
/// <param name="bPick">:预留接口.默认值:flase</param>
/// <param name="bUndo">:预留接口.默认值:flase</param>
/// <param name="strUndoName">:预留接口.默认值:""</param>
e3_CreateCircle E3_CreateCircle = nullptr;

/// <summary>
/// 接口说明:添加圆(新添加对象ID此接口直接返回)
/// <para>API编码:[88719874]</para>
/// <para>文档定位:数据-标准图元-创建</para>
/// </summary>
/// <param name="idEM">:管理器ID</param>
/// <param name="nPen">:笔号[0,255]</param>
/// <param name="pt1">:圆中心坐标</param>
/// <param name="pt2">:圆半径坐标,此坐标与圆心坐标距离即为半径.</param>
/// <param name="bUpdateParentInfo">:是否更新列表信息，若不更新对象列表信息,最后更新,避免大量创建时由于更新对象列表导致的卡顿</param>
/// <param name="idNewEnt">:返回添加对象ID</param>
e3_CreateCircle_2 E3_CreateCircle_2 = nullptr;

/// <summary>
/// 接口说明:创建控制器,将控制器添加到管理器中,类型与标准软件中相同
/// <para>API编码:[45813410]</para>
/// <para>文档定位:数据-标准图元-创建</para>
/// </summary>
/// <param name="idEM">:管理器ID</param>
/// <param name="nPen">:笔号[0,255]</param>
/// <param name="nControlType">:控制器类型1=延时器;2=输入端口; 3=输出端口; 4=Unkonw;(预留) 5=扩展轴; 6=输入口跳转; 7=索引; 8=CCD; 9=编码器移动距离</param>
/// <param name="bPick">:预留接口.默认值:flase</param>
/// <param name="bUndo">:预留接口.默认值:flase</param>
/// <param name="strUndoName">:预留接口.默认值:""</param>
e3_CreateControl E3_CreateControl = nullptr;

/// <summary>
/// 接口说明:创建控制器,将控制器添加到管理器中,类型与标准软件中相同
/// <para>API编码:[85456471]</para>
/// <para>文档定位:数据-标准图元-创建</para>
/// </summary>
/// <param name="idEM">:管理器ID</param>
/// <param name="nPen">:笔号[0,255]</param>
/// <param name="nControlType">:控制器类型1=延时器;2=输入端口; 3=输出端口; 4=Unkonw;(预留) 5=扩展轴; 6=输入口跳转; 7=索引; 8=CCD; 9=编码器移动距离</param>
/// <param name="bUpdateParentInfo">:是否更新列表信息，若不更新对象列表信息,最后更新,避免大量创建时由于更新对象列表导致的卡顿</param>
/// <param name="idNewEnt">:返回添加对象ID</param>
e3_CreateControl_2 E3_CreateControl_2 = nullptr;

/// <summary>
/// 接口说明:添加椭圆
/// <para>API编码:[91838111]</para>
/// <para>文档定位:数据-标准图元-创建</para>
/// </summary>
/// <param name="idEM">:管理器ID</param>
/// <param name="nPen">:笔号[0,255]</param>
/// <param name="pt1">:椭圆外包盒左下角坐标</param>
/// <param name="pt2">:椭圆外包盒右上角坐标</param>
/// <param name="bPick">:预留接口.默认值:flase</param>
/// <param name="bUndo">:预留接口.默认值:flase</param>
/// <param name="strUndoName">:预留接口.默认值:""</param>
e3_CreateEllipse E3_CreateEllipse = nullptr;

/// <summary>
/// 接口说明:添加椭圆
/// <para>API编码:[89444728]</para>
/// <para>文档定位:数据-标准图元-创建</para>
/// </summary>
/// <param name="idEM">:管理器ID</param>
/// <param name="nPen">:笔号[0,255]</param>
/// <param name="pt1">:椭圆外包盒左下角坐标</param>
/// <param name="pt2">:椭圆外包盒右上角坐标</param>
/// <param name="bUpdateParentInfo">:是否更新列表信息，若不更新对象列表信息,最后更新,避免大量创建时由于更新对象列表导致的卡顿</param>
/// <param name="idNewEnt">:返回添加对象ID</param>
e3_CreateEllipse_2 E3_CreateEllipse_2 = nullptr;

/// <summary>
/// 接口说明:添加线段
/// <para>API编码:[64805740]</para>
/// <para>文档定位:数据-标准图元-创建</para>
/// </summary>
/// <param name="idEM">:管理器ID</param>
/// <param name="nPen">:笔号[0,255]</param>
/// <param name="ptLines">:线段的点集数组</param>
/// <param name="nPointCount">:添加点的数量（实际添加的点数量）</param>
/// <param name="bPick">:预留接口.默认值:flase</param>
/// <param name="bUndo">:预留接口.默认值:flase</param>
/// <param name="strUndoName">:预留接口.默认值:""</param>
e3_CreateLines E3_CreateLines = nullptr;

/// <summary>
/// 接口说明:添加线段
/// <para>API编码:[96973526]</para>
/// <para>文档定位:数据-标准图元-创建</para>
/// </summary>
/// <param name="idEM">:管理器ID</param>
/// <param name="nPen">:笔号[0,255]</param>
/// <param name="ptLines">:线段的点集数组</param>
/// <param name="nPointCount">:添加点的数量（实际添加的点数量）</param>
/// <param name="bUpdateParentInfo">:是否更新列表信息，若不更新对象列表信息,最后更新,避免大量创建时由于更新对象列表导致的卡顿</param>
/// <param name="idEnt">:返回添加对象ID</param>
e3_CreateLines_2 E3_CreateLines_2 = nullptr;

/// <summary>
/// 接口说明:添加点对象
/// <para>API编码:[84889825]</para>
/// <para>文档定位:数据-标准图元-创建</para>
/// </summary>
/// <param name="idEM">:管理器ID</param>
/// <param name="nPen">:笔号[0,255]</param>
/// <param name="pts">:线段的点集数组</param>
/// <param name="nPointCount">:添加点的数量（实际添加的点数量）</param>
/// <param name="reserved1">:预留接口.默认值:flase</param>
/// <param name="reserved2">:预留接口.默认值:flase</param>
/// <param name="reserved3">:预留接口.默认值:""</param>
e3_CreatePoints E3_CreatePoints = nullptr;

/// <summary>
/// 接口说明:添加点对象
/// <para>API编码:[43447856]</para>
/// <para>文档定位:数据-标准图元-创建</para>
/// </summary>
/// <param name="idEM">:管理器ID</param>
/// <param name="nPen">:笔号[0,255]</param>
/// <param name="pts">:线段的点集数组</param>
/// <param name="nPointCount">:添加点的数量（实际添加的点数量）</param>
/// <param name="bUpdateParentInfo">:是否更新列表信息，若不更新对象列表信息,最后更新,避免大量创建时由于更新对象列表导致的卡顿</param>
/// <param name="idNewEnt">:返回添加对象ID</param>
e3_CreatePoints_2 E3_CreatePoints_2 = nullptr;

/// <summary>
/// 接口说明:添加六边形对象
/// <para>API编码:[67951084]</para>
/// <para>文档定位:数据-标准图元-创建</para>
/// </summary>
/// <param name="idEM">:管理器ID</param>
/// <param name="nPen">:笔号[0,255]</param>
/// <param name="pt1">:六边形外切圆的左下角坐标</param>
/// <param name="pt2">:六边形外切圆的右上角坐标</param>
/// <param name="bPick">:预留接口.默认值:flase</param>
/// <param name="bUndo">:预留接口.默认值:flase</param>
/// <param name="strUndoName">:预留接口.默认值:""</param>
e3_CreatePolygon E3_CreatePolygon = nullptr;

/// <summary>
/// 接口说明:添加六边形对象
/// <para>API编码:[96717837]</para>
/// <para>文档定位:数据-标准图元-创建</para>
/// </summary>
/// <param name="idEM">:管理器ID</param>
/// <param name="nPen">:笔号[0,255]</param>
/// <param name="pt1">:六边形外切圆的左下角坐标</param>
/// <param name="pt2">:六边形外切圆的右上角坐标</param>
/// <param name="bUpdateParentInfo">:是否更新列表信息，若不更新对象列表信息,最后更新,避免大量创建时由于更新对象列表导致的卡顿</param>
/// <param name="idNewEnt">:返回添加对象ID</param>
e3_CreatePolygon_2 E3_CreatePolygon_2 = nullptr;

/// <summary>
/// 接口说明:添加矩形
/// <para>API编码:[81677020]</para>
/// <para>文档定位:数据-标准图元-创建</para>
/// </summary>
/// <param name="idEM">:管理器ID</param>
/// <param name="nPen">:笔号[0,255]</param>
/// <param name="pt1">:矩形左下脚下x，y坐标</param>
/// <param name="pt2">:矩形外包盒右上角坐标</param>
/// <param name="bPick">:预留接口.默认值:flase</param>
/// <param name="bUndo">:预留接口.默认值:flase</param>
/// <param name="strUndoName">:预留接口.默认值:""</param>
e3_CreateRect E3_CreateRect = nullptr;

/// <summary>
/// 接口说明:添加矩形
/// <para>API编码:[71254326]</para>
/// <para>文档定位:数据-标准图元-创建</para>
/// </summary>
/// <param name="idEM">:管理器ID</param>
/// <param name="nPen">:笔号[0,255]</param>
/// <param name="pt1">:矩形左下脚下x，y坐标</param>
/// <param name="pt2">:矩形外包盒右上角坐标</param>
/// <param name="bUpdateParentInfo">:是否更新列表信息，若不更新对象列表信息,最后更新,避免大量创建时由于更新对象列表导致的卡顿</param>
/// <param name="idNewEnt">:返回添加对象ID</param>
e3_CreateRect_2 E3_CreateRect_2 = nullptr;

/// <summary>
/// 接口说明:添加螺旋线
/// <para>API编码:[69225644]</para>
/// <para>文档定位:数据-标准图元-创建</para>
/// </summary>
/// <param name="idEM">:管理器ID</param>
/// <param name="nPen">:笔号[0,255]</param>
/// <param name="pt1">:螺旋中心坐标</param>
/// <param name="pt2">:螺旋半径坐标 （X 坐标为中心坐标+半径长度，Y坐标为中心坐标）</param>
/// <param name="bPick">:预留接口.默认值:flase</param>
/// <param name="bUndo">:预留接口.默认值:flase</param>
/// <param name="strUndoName">:预留接口.默认值:""</param>
e3_CreateSpiral E3_CreateSpiral = nullptr;

/// <summary>
/// 接口说明:添加螺旋线
/// <para>API编码:[70475483]</para>
/// <para>文档定位:数据-标准图元-创建</para>
/// </summary>
/// <param name="idEM">:管理器ID</param>
/// <param name="nPen">:笔号[0,255]</param>
/// <param name="pt1">:螺旋中心坐标</param>
/// <param name="pt2">:螺旋半径坐标 （X 坐标为中心坐标+半径长度，Y坐标为中心坐标）</param>
/// <param name="bUpdateParentInfo">:是否更新列表信息，若不更新对象列表信息,最后更新,避免大量创建时由于更新对象列表导致的卡顿</param>
/// <param name="idNewEnt">:返回添加对象ID</param>
e3_CreateSpiral_2 E3_CreateSpiral_2 = nullptr;

/// <summary>
/// 接口说明:添加文本条码
/// <para>API编码:[87849520]</para>
/// <para>文档定位:数据-标准图元-创建</para>
/// </summary>
/// <param name="idEM">:管理器ID</param>
/// <param name="nPen">:笔号[0,255]</param>
/// <param name="ptBase">:工作空间中XY左下脚位置</param>
/// <param name="str">:添加的文本内容.0-4098个字符</param>
/// <param name="nFontId">:此字体在系统中所有字体的中的序号.调用E3_GetAllFontRecord得到此序号字体的名字及类型</param>
/// <param name="dTextHeight">:字符高度.默认10</param>
/// <param name="dTextWidthRatio">:字符宽度与字符高度比例.默认50</param>
/// <param name="nTextSpaceType">:文本间距模式:      0：自动模式;     1：边框间距;     2：中心间距;</param>
/// <param name="dTextSpace">:文本间距.默认2.5</param>
/// <param name="dTextAngle">:字体弧度（弧度值）</param>
/// <param name="nAlignType">:0:左对齐; 1:中心对齐; 2:右对齐;</param>
/// <param name="dNullCharWidthRatio">:空字符宽度比例.默认0.34</param>
/// <param name="dLineSpace">:行间距.默认0.21</param>
/// <param name="bVerText">:字体排列方向.True:为竖向排列</param>
/// <param name="bBold">:粗体</param>
/// <param name="bItalic">:斜体</param>
/// <param name="reserved1">:预留接口.默认值:flase</param>
/// <param name="reserved2">:预留接口.默认值:flase</param>
/// <param name="reserved3">:预留接口.默认值:""</param>
e3_CreateText E3_CreateText = nullptr;

/// <summary>
/// 接口说明:添加文本条码
/// <para>API编码:[83009595]</para>
/// <para>文档定位:数据-标准图元-创建</para>
/// </summary>
/// <param name="idEM">:管理器ID</param>
/// <param name="nPen">:笔号[0,255]</param>
/// <param name="ptBase">:工作空间中XY左下脚位置</param>
/// <param name="str">:添加的文本内容.0-4098个字符</param>
/// <param name="nFontId">:此字体在系统中所有字体的中的序号.调用E3_GetAllFontRecord得到此序号字体的名字及类型</param>
/// <param name="dTextHeight">:字符高度.默认10</param>
/// <param name="dTextWidthRatio">:字符宽度与字符高度比例.默认50</param>
/// <param name="nTextSpaceType">:文本间距模式:      0：自动模式;     1：边框间距;     2：中心间距;</param>
/// <param name="dTextSpace">:文本间距.默认2.5</param>
/// <param name="dTextAngle">:字体弧度（弧度值）</param>
/// <param name="nAlignType">:0:左对齐; 1:中心对齐;  2:右对齐;</param>
/// <param name="dNullCharWidthRatio">:空字符宽度比例.默认0.34</param>
/// <param name="dLineSpace">:行间距.默认0.21</param>
/// <param name="bVerText">:字体排列方向.True:为竖向排列</param>
/// <param name="bBold">:粗体</param>
/// <param name="bItalic">:斜体</param>
/// <param name="bUpdateParentInfo">:是否更新列表信息，若不更新对象列表信息,最后更新,避免大量创建时由于更新对象列表导致的卡顿</param>
/// <param name="idNewEnt">:返回添加对象ID</param>
e3_CreateText_2 E3_CreateText_2 = nullptr;

/// <summary>
/// 接口说明:得到当前层ID和层索引
/// <para>API编码:[65402300]</para>
/// <para>文档定位:数据-对象操作-对象ID关系</para>
/// </summary>
/// <param name="idEM">:管理器ID</param>
/// <param name="idLayer">:返回的层ID</param>
/// <param name="nLayerId">:返回的层索引</param>
e3_GetCurLayerId E3_GetCurLayerId = nullptr;

/// <summary>
/// 接口说明:得到指定管理器中的图层数和当前层索引
/// <para>API编码:[87172203]</para>
/// <para>文档定位:数据-对象操作-对象ID关系</para>
/// </summary>
/// <param name="idEM">:管理器ID</param>
/// <param name="nLayerCount">:返回的指定管理器中图层数目</param>
/// <param name="nCurLayer">:返回的层索引</param>
e3_GetLayerCount E3_GetLayerCount = nullptr;

/// <summary>
/// 接口说明:得到指定管理器中指定序号的图层ID
/// <para>API编码:[15276306]</para>
/// <para>文档定位:数据-对象操作-对象ID关系</para>
/// </summary>
/// <param name="idEM">:管理器ID</param>
/// <param name="nLayerIndex">:层索引</param>
/// <param name="idLayer">:返回的指定层的ID</param>
e3_GetLayerId E3_GetLayerId = nullptr;

/// <summary>
/// 接口说明:添加矢量文件
/// <para>API编码:[76258762]</para>
/// <para>文档定位:数据-标准图元-创建</para>
/// </summary>
/// <param name="pStrFileName">:矢量文件全路径</param>
/// <param name="idEM">:管理器ID</param>
/// <param name="bUndo">:预留参数 默认false</param>
/// <param name="strUndoName">:预留参数 默认为""</param>
e3_ImportFileToEntMgr E3_ImportFileToEntMgr = nullptr;

/// <summary>
/// 接口说明:添加矢量文件
/// <para>API编码:[70355257]</para>
/// <para>文档定位:数据-标准图元-创建</para>
/// </summary>
/// <param name="pStrFileName">:矢量文件全路径</param>
/// <param name="idEM">:管理器ID</param>
/// <param name="bUpdateParentInfo">:是否更新列表信息，若不更新对象列表信息,最后更新,避免大量创建时由于更新对象列表导致的卡顿</param>
/// <param name="idNewEnt">:返回添加对象ID</param>
e3_ImportFileToEntMgr_2 E3_ImportFileToEntMgr_2 = nullptr;

/// <summary>
/// 接口说明:标刻圆弧（起始点为当前振镜所在点，从当前点开始标刻一段指定角度的圆弧）
/// <para>API编码:[22276893]</para>
/// <para>文档定位:硬件-组合动作-列表命令-对象级列表命令</para>
/// </summary>
/// <param name="idMarker">:板卡ID</param>
/// <param name="ptCen">:圆心坐标</param>
/// <param name="dAng">:角度，单位为（度）</param>
/// <param name="bIsFirstPt">:圆弧是否是一段曲线的第一段</param>
/// <param name="bLaserFreqSyn">:如果是第一段是否要进行激光信号同步</param>
e3_MarkerArcMarkToPtList E3_MarkerArcMarkToPtList = nullptr;

/// <summary>
/// 接口说明:振镜跳转到指定点
/// <para>API编码:[49222656]</para>
/// <para>文档定位:硬件-组合动作-列表命令-对象级列表命令</para>
/// </summary>
/// <param name="idMarker">:板卡ID</param>
/// <param name="pt">:指定点坐标</param>
e3_MarkerBasicJumpToPtList E3_MarkerBasicJumpToPtList = nullptr;

/// <summary>
/// 接口说明:标刻到指定点
/// <para>API编码:[29732565]</para>
/// <para>文档定位:硬件-组合动作-列表命令-对象级列表命令</para>
/// </summary>
/// <param name="idMarker">:板卡ID</param>
/// <param name="pt">:指定点坐标</param>
/// <param name="bIsFirstPt">:是否是第一个点</param>
/// <param name="bLaserFreqSyn">:如果是第一段是否要进行激光信号同步</param>
e3_MarkerBasicMarkToPtList E3_MarkerBasicMarkToPtList = nullptr;

/// <summary>
/// 接口说明:设置指定笔号参数加工（如标刻到指定点等无指定笔号的的接口使用）
/// <para>API编码:[92398974]</para>
/// <para>文档定位:硬件-组合动作-列表命令-列表过程命令</para>
/// </summary>
/// <param name="idMarker">:板卡ID</param>
/// <param name="nPen">:笔号[0,255]</param>
e3_MarkerBasicSetPenList E3_MarkerBasicSetPenList = nullptr;

/// <summary>
/// 接口说明:检查激光器状态
/// <para>API编码:[31015533]</para>
/// <para>文档定位:硬件-资源-激光-状态查询</para>
/// </summary>
/// <param name="idMarker">:板卡ID</param>
/// <param name="isOk">:激光器状态是否正常</param>
e3_MarkerCheckLaserState E3_MarkerCheckLaserState = nullptr;

/// <summary>
/// 接口说明:增加缓存数据
/// <para>API编码:[42892184]</para>
/// <para>文档定位:硬件-组合动作-动作指令</para>
/// </summary>
/// <param name="idMarker">:板卡ID</param>
/// <param name="pStr1">:设置的对象名字pStr1对应的字符串</param>
/// <param name="pStr2">:设置的对象名字pStr2对应的字符串</param>
/// <param name="pStr3">:设置的对象名字pStr3对应的字符串</param>
/// <param name="pStr4">:设置的对象名字pStr4对应的字符串</param>
/// <param name="pStr5">:设置的对象名字pStr5对应的字符串</param>
/// <param name="pStr6">:设置的对象名字pStr6对应的字符串</param>
e3_MarkerContinueBufferAdd E3_MarkerContinueBufferAdd = nullptr;

/// <summary>
/// 接口说明:清除缓存区
/// <para>API编码:[03445085]</para>
/// <para>文档定位:硬件-组合动作-动作指令</para>
/// </summary>
/// <param name="idMarker">:板卡ID</param>
e3_MarkerContinueBufferClear E3_MarkerContinueBufferClear = nullptr;

/// <summary>
/// 接口说明:得到已加工数目和缓存区剩余个数
/// <para>API编码:[61383545]</para>
/// <para>文档定位:硬件-资源-激光-状态查询</para>
/// </summary>
/// <param name="idMarker">:板卡ID</param>
/// <param name="nTotalMarkCount">:返回的从开始加工到现在已经完整加工的次数</param>
/// <param name="nBufferLeftCount">:当前缓存区剩余中未开始处理的个数（有可能数据已经处理，当时还未开始加工）,缓存区数据数最大为8</param>
e3_MarkerContinueBufferGetParam E3_MarkerContinueBufferGetParam = nullptr;

/// <summary>
/// 接口说明:设置发送零件数已经结束的标志
/// <para>API编码:[39900765]</para>
/// <para>文档定位:硬件-组合动作-动作指令</para>
/// </summary>
/// <param name="idMarker">:板卡ID</param>
e3_MarkerContinueBufferPartFinish E3_MarkerContinueBufferPartFinish = nullptr;

/// <summary>
/// 接口说明:设置缓存区文本对象的名字
/// <para>API编码:[59480047]</para>
/// <para>文档定位:硬件-组合动作-动作指令</para>
/// </summary>
/// <param name="idMarker">:板卡ID</param>
/// <param name="nNum">:设置后面有几个字符串有效</param>
/// <param name="pStr1">:设置缓存区字符串的对象名</param>
/// <param name="pStr2">:设置缓存区字符串的对象名</param>
/// <param name="pStr3">:设置缓存区字符串的对象名</param>
/// <param name="pStr4">:设置缓存区字符串的对象名</param>
/// <param name="pStr5">:设置缓存区字符串的对象名</param>
/// <param name="pStr6">:设置缓存区字符串的对象名</param>
e3_MarkerContinueBufferSetTextName E3_MarkerContinueBufferSetTextName = nullptr;

/// <summary>
/// 接口说明:开始缓存区加工，如何缓存区没数据会一直等待数据
/// <para>API编码:[52588617]</para>
/// <para>文档定位:硬件-组合动作-动作指令</para>
/// </summary>
/// <param name="idMarker">:板卡ID</param>
/// <param name="idEM">:管理器ID</param>
/// <param name="idEntParent">:层ID</param>
e3_MarkerContinueBufferStart E3_MarkerContinueBufferStart = nullptr;

/// <summary>
/// 接口说明:开始循环
/// <para>API编码:[92504541]</para>
/// <para>文档定位:硬件-组合动作-列表命令-列表过程命令</para>
/// </summary>
/// <param name="idMarker">:板卡ID</param>
e3_MarkerDoLoopToList E3_MarkerDoLoopToList = nullptr;

/// <summary>
/// 接口说明:脱机使能
/// <para>API编码:[30764560]</para>
/// <para>文档定位:硬件-组合动作-列表命令-列表过程命令</para>
/// </summary>
/// <param name="idMarker">:板卡ID</param>
/// <param name="bOffline">:是否使能脱机 ,true为使能</param>
e3_MarkerEnableOffLineMode E3_MarkerEnableOffLineMode = nullptr;

/// <summary>
/// 接口说明:仅加工不发送数据
/// <para>API编码:[23560627]</para>
/// <para>文档定位:环境-控制卡-操作</para>
/// </summary>
/// <param name="idMarker">:板卡ID</param>
/// <param name="bWaitForFinish">:是否等到加工结束返回 true:是</param>
/// <param name="nFlag">:加工标志位 0:加工</param>
e3_MarkerExecuteAndWaitFinish E3_MarkerExecuteAndWaitFinish = nullptr;

/// <summary>
/// 接口说明:获取板卡运行状态
/// <para>API编码:[32545702]</para>
/// <para>文档定位:硬件-资源-振镜-状态查询</para>
/// </summary>
/// <param name="idMarker">:板卡ID</param>
/// <param name="nStatus">:板卡运行状态,一共32Bit,每Bit分别代表不同的状态,具体请查看状态表;BIT0:加工过程中振镜位置是否超出最大加工幅面; 0x1=振镜已超出最大加工幅面;0x0=振镜未超出最大加工幅面;</param>
e3_MarkerGetBoardRunningStatus E3_MarkerGetBoardRunningStatus = nullptr;

/// <summary>
/// 接口说明:得到激光器状态（F3是否检测激光器的启用/关闭不影响此接口的状态）
/// <para>API编码:[76468645]</para>
/// <para>文档定位:硬件-资源-激光-状态查询</para>
/// </summary>
/// <param name="idMarker">:板卡ID</param>
/// <param name="data">:激光器状态,                                                                                                                                                                                                                                                                                                            QCW:详情查看;BIT0 :激光器发射反馈: 1=正常;0=异常;BIT1 主电源启动反馈:1=正常;0=异常;BIT2 系统上电反馈:1=正常;0=异常;BIT3 激光器异常状态反馈:1=正常;0=异常;BIT4 ;BIT5 激光输出状态:1=打开;0=关闭;BIT6 红光输出状态:1=打开;0=关闭;BIT7 错误复位输出状态:1=打开;0=关闭; FIBER:BIT0-3 激光状态反馈，BIT4:MO, BIT5:AP       TYPE:E/G BIT0-BIT2激光状态反馈  BIT4:MO, BIT5:AP BIT6:红光输出                                                                                                                                SPI:BIT0-3 激光状态反馈 BIT5:激光输出, BIT6 红光输出 1表示输出                                                                                                                                                                                                       CO2/YAG:BIT0-BIT3 激光状态反馈 BIT5:激光输出, BIT6 红光输出， 1表示输出状态</param>
e3_MarkerGetLaserState E3_MarkerGetLaserState = nullptr;

/// <summary>
/// 接口说明:得到当前已发列表总数
/// <para>API编码:[81935943]</para>
/// <para>文档定位:环境-控制卡-操作</para>
/// </summary>
/// <param name="idMarker">:板卡ID</param>
/// <param name="nCount">:返回的当前已发列表总数</param>
e3_MarkerGetListTotalCount E3_MarkerGetListTotalCount = nullptr;

/// <summary>
/// 接口说明:获取实际加工时间
/// <para>API编码:[65544265]</para>
/// <para>文档定位:环境-控制卡-操作</para>
/// </summary>
/// <param name="idMarker">:板卡ID</param>
/// <param name="nTimeMs">:返回的加工时间（ms）</param>
e3_MarkerGetMakingTime E3_MarkerGetMakingTime = nullptr;

/// <summary>
/// 接口说明:得到振镜坐标
/// <para>API编码:[99472409]</para>
/// <para>文档定位:硬件-资源-振镜-状态查询</para>
/// </summary>
/// <param name="idMarker">:板卡ID</param>
/// <param name="x">:当前振镜x坐标</param>
/// <param name="y">:当前振镜y坐标</param>
/// <param name="z">:当前振镜z坐标</param>
e3_MarkerGetPos E3_MarkerGetPos = nullptr;

/// <summary>
/// 接口说明:脱机开始标志
/// <para>API编码:[36876632]</para>
/// <para>文档定位:环境-控制卡-操作</para>
/// </summary>
/// <param name="idMarker">:板卡ID</param>
/// <param name="nFileIndex">:层序号</param>
e3_MarkerOffLineModeStart E3_MarkerOffLineModeStart = nullptr;

/// <summary>
/// 接口说明:脱机结束标志
/// <para>API编码:[36890195]</para>
/// <para>文档定位:硬件-组合动作-列表命令-列表过程命令</para>
/// </summary>
/// <param name="idMarker">:板卡ID</param>
e3_MarkerOffLineModeStop E3_MarkerOffLineModeStop = nullptr;

/// <summary>
/// 接口说明:暂停继续（在列表外部需要继续暂停的指令时）
/// <para>API编码:[39894918]</para>
/// <para>文档定位:环境-控制卡-操作</para>
/// </summary>
/// <param name="idMarker">:板卡ID</param>
e3_MarkerRestartList E3_MarkerRestartList = nullptr;

/// <summary>
/// 接口说明:脱机下传
/// <para>API编码:[70824257]</para>
/// <para>文档定位:硬件-组合动作-列表命令-列表过程命令</para>
/// </summary>
/// <param name="idMarker">:板卡ID</param>
/// <param name="nFileCount">:图层个数</param>
e3_MarkerSendOfflineMainProgram E3_MarkerSendOfflineMainProgram = nullptr;

/// <summary>
/// 接口说明:确保当前数据缓存区的数据已经发送到卡里，并且卡里已经执行列表
/// <para>API编码:[82331401]</para>
/// <para>文档定位:硬件-组合动作-列表命令-列表过程命令</para>
/// </summary>
/// <param name="idMarker">:板卡ID</param>
e3_MarkerSentBufToCardAndRunList E3_MarkerSentBufToCardAndRunList = nullptr;

/// <summary>
/// 接口说明:暂停（在列表外部需要时调用）
/// <para>API编码:[32151152]</para>
/// <para>文档定位:环境-控制卡-操作</para>
/// </summary>
/// <param name="idMarker">:板卡ID</param>
e3_MarkerSetPause E3_MarkerSetPause = nullptr;

/// <summary>
/// 接口说明:停止加工
/// <para>API编码:[59798804]</para>
/// <para>文档定位:环境-控制卡-操作</para>
/// </summary>
/// <param name="idMarker">:板卡ID</param>
e3_MarkerStop E3_MarkerStop = nullptr;

/// <summary>
/// 接口说明:是否开启激光器内置红光
/// <para>API编码:[48871173]</para>
/// <para>文档定位:硬件-资源-数字量OUT-动作</para>
/// </summary>
/// <param name="idMarker">:板卡ID</param>
/// <param name="bOn">:开启/关闭激光内置红光 true：开启</param>
e3_MarkerSwitchRedLight E3_MarkerSwitchRedLight = nullptr;

/// <summary>
/// 接口说明:设置循环开始标志
/// <para>API编码:[46297679]</para>
/// <para>文档定位:硬件-组合动作-列表命令-列表过程命令</para>
/// </summary>
/// <param name="idMarker">:板卡ID</param>
e3_MarkertSetLoopStartToList E3_MarkertSetLoopStartToList = nullptr;

/// <summary>
/// 接口说明:等待列表命令实际执行结束
/// <para>API编码:[83858236]</para>
/// <para>文档定位:硬件-组合动作-列表命令-列表过程命令</para>
/// </summary>
/// <param name="idMarker">:板卡ID</param>
e3_MarkerWaitForFinish E3_MarkerWaitForFinish = nullptr;

/// <summary>
/// 接口说明:设置输入信号参数. 列表执行到此后会等待外触发信号，有相应信号才往下执行其他操作，若为脉冲模式，外触发脉宽30us,电平模式下200
/// <para>API编码:[42062835]</para>
/// <para>文档定位:硬件-加工动作-列表命令-对象级列表命令</para>
/// </summary>
/// <param name="idMarker">:板卡ID</param>
/// <param name="wMask">:设置的端口值.0-65535; 一般为位域设置,按照二进制位</param>
/// <param name="wLevel">:端口满足条件之后的比较值; 一般为0或1</param>
/// <param name="bIsFollowAvail">:等待IO中振镜是否跟随(在飞行中,等待IO会暂停列表,但是流水线在移动,振镜的位置可以选择是否等待或者跟随流水线移动)</param>
e3_MarkerWaitForInputToList E3_MarkerWaitForInputToList = nullptr;

/// <summary>
/// 接口说明:设置输出口.（控制命令） 可以用于标刻输出或者标刻结束输出等动作. Bit0是In0的状态,Bit0=1表示In0为高电平,Bit0=0表示In0为低电平. Bit1是In1的状态,Bit1=1表示In1为高电平,Bit1=0表示In1为低电平,依次类推. 如果设置值为5，表示OUT0,OUT2是高电平，其他端口都是低电平
/// <para>API编码:[63535317]</para>
/// <para>文档定位:硬件-资源-数字量OUT-动作</para>
/// </summary>
/// <param name="idMarker">:板卡ID</param>
/// <param name="data">:设置的输出的端口值.0-65535</param>
e3_MarkerWritePort E3_MarkerWritePort = nullptr;

/// <summary>
/// 接口说明:列表设置输出口.此接口为列表加工时输出口，接口指令是写入板卡， 在程序中调用此函数来输出数据到当前输出端口。Bit0是In0的状态,Bit0=1表示In0为高电平,Bit0= 0表示In0为低电平；Bit1是In1的状态,Bit1=1表示In1为高电平,Bit1=0表示In1为低电平；依次类推。如果获取值为2， 表示OUT1是高电平，其他端口都是低电平
/// <para>API编码:[92854590]</para>
/// <para>文档定位:硬件-资源-数字量OUT-动作</para>
/// </summary>
/// <param name="idMarker">:板卡ID</param>
/// <param name="data">:设置的输出的端口值.0-65535</param>
e3_MarkerWritePortToList E3_MarkerWritePortToList = nullptr;

/// <summary>
/// 接口说明:错切指定对象
/// <para>API编码:[83151043]</para>
/// <para>文档定位:数据-对象操作-对象间操作</para>
/// </summary>
/// <param name="idEnt">:对象ID</param>
/// <param name="nPos">:nPos为对象变换的9个基准点                                                                                                                                                                                                                                                                //6 5 4 //7 8 3 //0 1 2</param>
/// <param name="angx">:X方向倾斜角度，单位为度</param>
/// <param name="angy">:Y方向倾斜角度，单位为度</param>
e3_ShearEnt E3_ShearEnt = nullptr;

/// <summary>
/// 接口说明:分割对象
/// <para>API编码:[62839199]</para>
/// <para>文档定位:数据-对象操作-对象间操作</para>
/// </summary>
/// <param name="idEnt">:对象ID</param>
/// <param name="pBoxs">:分割盒列表 分割盒传值：矩形最小坐标/最大坐标</param>
/// <param name="nBoxCount">:分割盒数量, 因为不同开发语言的缘故，需用明确的长度参数，以便于结构体数组长度内存确定</param>
/// <param name="dSplitErr">:边界计算误差，一般为0.001就行</param>
/// <param name="dArcTol">:曲线离散误差，一般为0.01就行</param>
/// <param name="strNewEntNamePrefix">:分割后对象名标识前缀</param>
e3_SplitEntByBox E3_SplitEntByBox = nullptr;

/// <summary>
/// 接口说明:分割对象
/// <para>API编码:[65800117]</para>
/// <para>文档定位:数据-对象操作-对象ID关系</para>
/// </summary>
/// <param name="idEnt">:对象ID</param>
/// <param name="pBoxs">:分割盒列表 分割盒传值：矩形最小坐标/最大坐标</param>
/// <param name="nBoxCount">:分割盒数量, 因为不同开发语言的缘故，需用明确的长度参数，以便于结构体数组长度内存确定</param>
/// <param name="dSplitErr">:边界计算误差，一般为0.001就行</param>
/// <param name="dArcTol">:曲线离散误差，一般为0.01就行</param>
/// <param name="bNoCutEntity">:禁止切割对象,此功能使能后不会对对象进行切分,而是对分割区域中存在的很多小对象进行群组.</param>
/// <param name="bNotCutSmallEnt">:不对小于dSmallSize的对象进行分割,此功能为当分割区域内,存在整体曲线超出分割区域但是小于设定的最小分割尺寸,则不分割而是完整纳入当前分割区域,如果超出则按照分割区域边界切分.</param>
/// <param name="dSmallSize">:分割最小尺寸</param>
/// <param name="bEnableOverlap">:对填充对象进行错位分割,此功能使能后会对分割盒自动增加错位尺寸,之后对对象分割,在增加的错位尺寸内进行间隔对曲线端点进行增加减少,进行交错分割,用于错开开关光点.</param>
/// <param name="dOverlapSize">:错位分割尺寸</param>
/// <param name="strNewEntNamePrefix">:分割后对象名标识前缀</param>
e3_SplitEntByBox2 E3_SplitEntByBox2 = nullptr;

/// <summary>
/// 接口说明:对指定的对象,沿指定的0,0,0 到ptAxisX,y,z  构成的轴线旋转,然后按照MOVEXYZ移动.
/// <para>API编码:[82735176]</para>
/// <para>文档定位:数据-3D操作</para>
/// </summary>
/// <param name="idEnt">:对象ID</param>
/// <param name="dMoveX">:X方向移动相对距离</param>
/// <param name="dMoveY">:Y方向移动相对距离</param>
/// <param name="dMoveZ">:Z方向移动相对距离</param>
/// <param name="ptAxisX">:旋转轴线的x坐标</param>
/// <param name="ptAxisY">:轴线的Y坐标</param>
/// <param name="ptAxisZ">:轴线的Z坐标</param>
/// <param name="fRadAngle">:旋转角度</param>
/// <param name="dTol">:精度</param>
/// <param name="idNewEnt">:旋转移动操作后返回的新的对象ID</param>
e3_TransormEnt3dRotate E3_TransormEnt3dRotate = nullptr;

/// <summary>
/// 接口说明:对STL模型,沿指定的0,0,0 到ptAxisX,y,z  构成的轴线旋转,然后按照MOVEXYZ移动.（三个旋转轴向量ptAxisX，ptAxisY, ptAxisZ不可同时为0）.
/// <para>API编码:[98999986]</para>
/// <para>文档定位:数据-3D操作</para>
/// </summary>
/// <param name="idLayer">:图层ID</param>
/// <param name="dMoveX">:X方向移动相对距离</param>
/// <param name="dMoveY">:Y方向移动相对距离</param>
/// <param name="dMoveZ">:Z方向移动相对距离</param>
/// <param name="ptAxisX">:旋转轴线的x坐标</param>
/// <param name="ptAxisY">:旋转轴线的y坐标</param>
/// <param name="ptAxisZ">:旋转轴线的z坐标</param>
/// <param name="fRadAngle">:旋转角度</param>
e3_TransormStlRotate E3_TransormStlRotate = nullptr;

/// <summary>
/// 接口说明:获取QCW波形输出参数,此接口序号为2_2,与同名_2的接口声明无区别,但是底层是控制独立的硬件模块.也可以说这个是控制着第二路硬件模块.
/// <para>API编码:[50631982]</para>
/// <para>文档定位:数据-笔参数相关</para>
/// </summary>
/// <param name="idEM">:管理器ID</param>
/// <param name="nPenNo">:笔号[0,255]</param>
/// <param name="bLaserContMode">:是否使能连续模式，true为是</param>
/// <param name="bEnableWeldWave">:是否使能波形输出，true为是</param>
/// <param name="nMaxCount">:波形最大段数，此值最大为64段</param>
/// <param name="dWeldWavePower">:波形输出功率，功率范围[0,100]</param>
/// <param name="dWeldWaveWidthMs">:波形脉宽,64个脉宽值的和不可超过笔参数中设置的脉宽值</param>
e3_GetPenParamWeldWave2_2 E3_GetPenParamWeldWave2_2 = nullptr;

/// <summary>
/// 接口说明:设置QCW波形2输出参数,此接口序号为2_2,与同名_2的接口声明无区别,但是底层是控制独立的硬件模块.也可以说这个是控制着第二路硬件模块.
/// <para>API编码:[53590283]</para>
/// <para>文档定位:数据-笔参数相关</para>
/// </summary>
/// <param name="idEM">:管理器ID</param>
/// <param name="nPenNo">:笔号[0,255]</param>
/// <param name="bLaserContMode">:是否使能连续模式，true为是</param>
/// <param name="bEnableWeldWave">:是否使能波形输出，true为是</param>
/// <param name="nMaxCount">:波形最大段数，此值最大为64段</param>
/// <param name="dWeldWavePower">:波形输出功率，功率范围[0,100]</param>
/// <param name="dWeldWaveWidthMs">:波形脉宽,64个脉宽值的和不可超过笔参数中设置的脉宽值</param>
e3_SetPenParamWeldWave2_2 E3_SetPenParamWeldWave2_2 = nullptr;

/// <summary>
/// 接口说明:插值拟合非均匀B样条曲线
/// <para>API编码:[68430511]</para>
/// <para>文档定位:数据-标准图元-创建</para>
/// </summary>
/// <param name="nFlag">:内置标志，固定为0</param>
/// <param name="nPointNum">:曲线点集数量</param>
/// <param name="ptBuf[][2]">:曲线点集数据</param>
/// <param name="idNewCurveEnt">:添加到对象管理器中的曲线ID</param>
e3_BSplineInterFitCurve E3_BSplineInterFitCurve = nullptr;

/// <summary>
/// 接口说明:获取对象管理器指定笔号脉宽索引
/// <para>API编码:[09594498]</para>
/// <para>文档定位:数据-笔参数相关</para>
/// </summary>
/// <param name="idEM">:对象管理器ID</param>
/// <param name="nPenNo">:笔号</param>
/// <param name="nLaserParamIndex">:返回脉宽索引</param>
e3_GetPenParamLaserParamIndex E3_GetPenParamLaserParamIndex = nullptr;

/// <summary>
/// 接口说明:得到条码黑白信息
/// <para>API编码:[87778931]</para>
/// <para>文档定位:数据-对象操作-对象通用读写</para>
/// </summary>
/// <param name="idEnt">:对象ID</param>
/// <param name="nRow">:条码行数</param>
/// <param name="nCol">:条码列数</param>
/// <param name="pDataBuf">:条码二维黑白点信息</param>
e3_GetTextBarcodeInfo3 E3_GetTextBarcodeInfo3 = nullptr;

/// <summary>
/// 接口说明:跳转到列表指定索引位置
/// <para>API编码:[14771780]</para>
/// <para>文档定位:硬件-组合动作-列表命令-列表过程命令</para>
/// </summary>
/// <param name="idMarker">:控制卡ID</param>
/// <param name="index">:列表索引</param>
e3_MarkeDirectJumpToIndexToList E3_MarkeDirectJumpToIndexToList = nullptr;

/// <summary>
/// 接口说明:获取指定计数器计数值
/// <para>API编码:[24389001]</para>
/// <para>文档定位:硬件-资源-寄存器-读</para>
/// </summary>
/// <param name="idMarker">:控制卡ID</param>
/// <param name="index">:计数器索引</param>
/// <param name="nCount">:</param>
e3_MarkerGetMarkCount2 E3_MarkerGetMarkCount2 = nullptr;

/// <summary>
/// 接口说明:设置指定索引计数器值
/// <para>API编码:[51276588]</para>
/// <para>文档定位:硬件-资源-寄存器-写</para>
/// </summary>
/// <param name="idMarker">:控制卡ID</param>
/// <param name="index">:当前寄存器索引值.</param>
/// <param name="nCount">:当前寄存器的计数器值</param>
e3_MarkerSetMarkCount E3_MarkerSetMarkCount = nullptr;

/// <summary>
/// 接口说明:设置指定索引计数器值
/// <para>API编码:[97446379]</para>
/// <para>文档定位:硬件-资源-寄存器-写</para>
/// </summary>
/// <param name="idMarker">:控制卡ID</param>
/// <param name="index">:当前寄存器索引值</param>
/// <param name="nCount">:当前寄存器的计数器值</param>
e3_MarkerSetMarkCountToList E3_MarkerSetMarkCountToList = nullptr;

/// <summary>
/// 接口说明:开启USB通讯监控断线设置输出口状态
/// <para>API编码:[35469982]</para>
/// <para>文档定位:环境-控制卡-配置</para>
/// </summary>
/// <param name="idMarker">:控制卡ID</param>
/// <param name="TimeInterval">:时间间隔</param>
/// <param name="IsSetOutputPort">:USB断线输出口是否输出信号</param>
/// <param name="OutputPort">:输出端口</param>
/// <param name="OutputLevel">:端口电平状态</param>
e3_MarkerStartUSBMonitorProcess E3_MarkerStartUSBMonitorProcess = nullptr;

/// <summary>
/// 接口说明:列表循环，此循环可嵌套于Loop循环使用，但不可反向嵌套Loop循环
/// <para>API编码:[67703348]</para>
/// <para>文档定位:硬件-组合动作-列表命令-列表过程命令</para>
/// </summary>
/// <param name="idMarker">:控制卡ID</param>
e3_MarkertRepeatToList E3_MarkertRepeatToList = nullptr;

/// <summary>
/// 接口说明:列表循环结尾标志命令
/// <para>API编码:[90834687]</para>
/// <para>文档定位:硬件-组合动作-列表命令-列表过程命令</para>
/// </summary>
/// <param name="idMarker">:控制卡ID</param>
/// <param name="RepeatNumber">:循环次数==0xFFFFFFFF 无限循环 范围[1,0xffffffff]</param>
e3_MarkertUntilToList E3_MarkertUntilToList = nullptr;

/// <summary>
/// 接口说明:设置指定笔参数脉冲索引
/// <para>API编码:[37954707]</para>
/// <para>文档定位:数据-笔参数相关</para>
/// </summary>
/// <param name="idEM">:对象管理器ID</param>
/// <param name="nPenNo">:笔号</param>
/// <param name="nLaserParamIndex">:脉宽索引</param>
e3_SetPenParamLaserParamIndex E3_SetPenParamLaserParamIndex = nullptr;

/// <summary>
/// 接口说明:循环体中指定计数器自加
/// <para>API编码:[86632813]</para>
/// <para>文档定位:硬件-资源-寄存器-写</para>
/// </summary>
/// <param name="idMarker">:控制卡ID</param>
/// <param name="Index">:计数器索引</param>
/// <param name="IncCounter">:自加值</param>
e3_MarkerSetAutoIncCounterToList E3_MarkerSetAutoIncCounterToList = nullptr;

/// <summary>
/// 接口说明:获取对象所属管理器
/// <para>API编码:[57224956]</para>
/// <para>文档定位:数据-对象操作-对象通用读写</para>
/// </summary>
/// <param name="idEnt">:对象ID</param>
/// <param name="idEntMgr">:管理器ID</param>
e3_GetEntMgr E3_GetEntMgr = nullptr;

/// <summary>
/// 接口说明:获取对象属性
/// <para>API编码:[31515403]</para>
/// <para>文档定位:数据-对象操作-对象通用读写</para>
/// </summary>
/// <param name="idEnt">:对象ID</param>
/// <param name="minx">:最小X坐标</param>
/// <param name="miny">:最小Y坐标</param>
/// <param name="maxx">:最大X坐标</param>
/// <param name="maxy">:最大Y坐标</param>
/// <param name="minz">:最小Z坐标</param>
/// <param name="maxz">:最大Z坐标</param>
/// <param name="penNo">:笔号</param>
e3_GetEntParam E3_GetEntParam = nullptr;

/// <summary>
/// 接口说明:获取第一个序列子对象
/// <para>API编码:[80946951]</para>
/// <para>文档定位:数据-对象操作-对象通用读写</para>
/// </summary>
/// <param name="idEnt">:对象ID</param>
/// <param name="idEntChild">:子对象ID</param>
e3_GetEntParam1 E3_GetEntParam1 = nullptr;

/// <summary>
/// 接口说明:获取第一序列同级对象,也即[E3_GetEntParam1]接口得到子对象的下一个序号的对象,之后由此接口迭代获得所有排序的对象.
/// <para>API编码:[15487756]</para>
/// <para>文档定位:数据-对象操作-对象通用读写</para>
/// </summary>
/// <param name="idEnt">:对象ID</param>
/// <param name="idEntNext">:子对象ID</param>
e3_GetEntParam2 E3_GetEntParam2 = nullptr;

/// <summary>
/// 接口说明:获取指定对象的笔号，注意得到的是对象本身的笔号，并不代表其子对象的笔号。这个在群组和填充时需要注意.
/// <para>API编码:[75510903]</para>
/// <para>文档定位:数据-对象操作-对象通用读写</para>
/// </summary>
/// <param name="idEnt">:对象ID</param>
/// <param name="nPen">:笔号</param>
e3_GetEntPen E3_GetEntPen = nullptr;

/// <summary>
/// 接口说明:查询条码详细信息，使用E3_GetLayerId得到层id, E3_FindEntInLayerByIndex得到指定对象ID, E3_GetAllFontCount获得当前系统包含字体数量，E3_GetAllFontRecord获得字体类型及名称用于条码字体类型及明码名称的设置.
/// <para>API编码:[00041454]</para>
/// <para>文档定位:数据-对象操作-对象通用读写</para>
/// </summary>
/// <param name="idEnt">:对象ID</param>
/// <param name="nMaxParamN">:最大整形数据.默认23</param>
/// <param name="nParam">:条码属性数组,每一位代表一个属性,具体请查看附录;</param>
/// <param name="nMaxParamD">:最大浮点型数据.默认值28;</param>
/// <param name="dParam">:条码造型数组,每一位代表一个造型参数,具体请查看附录;</param>
/// <param name="strFontName[256]">:条码字体类型名称;</param>
/// <param name="strTextFontName[256]">:明码字体名称;</param>
/// <param name="param1">:第一组填充参数;</param>
/// <param name="param2">:第二组填充参数;</param>
/// <param name="param3">:第三组填充参数;</param>
e3_GetTextBarcodeInfo E3_GetTextBarcodeInfo = nullptr;

/// <summary>
/// 接口说明:查询条码类型及行列数.
/// <para>API编码:[08057877]</para>
/// <para>文档定位:数据-对象操作-对象通用读写</para>
/// </summary>
/// <param name="idEnt">:对象ID</param>
/// <param name="strText[256]">:条码数据内容</param>
/// <param name="nSizeMode">:条码版本号</param>
/// <param name="nRow">:行数;</param>
/// <param name="nCol">:列数</param>
e3_GetTextBarcodeInfo2 E3_GetTextBarcodeInfo2 = nullptr;

/// <summary>
/// 接口说明:得到二维码尺寸的接口
/// <para>API编码:[35931452]</para>
/// <para>文档定位:数据-对象操作-对象通用读写</para>
/// </summary>
/// <param name="idEnt">:对象ID</param>
/// <param name="nPointMode">:条码模式（4=螺旋 3=点 1=矩形 2=圆 0=标准模式）;</param>
/// <param name="dPointSize">:尺寸;</param>
/// <param name="bFixedSize">:是否使用固定尺寸;</param>
/// <param name="dFixedSizeX">:固定X尺寸;</param>
/// <param name="dFixedSizeY">:固定Y尺寸;</param>
e3_GetTextBarcodeInfo4 E3_GetTextBarcodeInfo4 = nullptr;

/// <summary>
/// 接口说明:获取条码螺旋线模式参数.
/// <para>API编码:[79555907]</para>
/// <para>文档定位:数据-对象操作-对象通用读写</para>
/// </summary>
/// <param name="idEnt">:对象ID</param>
/// <param name="nInsideLoop">:内边界环数;</param>
/// <param name="nOutsideLoop">:外边界环数;</param>
/// <param name="bSpiralInsideToOutside">:由内向外;</param>
/// <param name="dSpiralPitchDist">:螺旋线螺距mm;</param>
/// <param name="dSpiralMinRadius">:最小半径mm;</param>
e3_GetTextBarcodeInfo5 E3_GetTextBarcodeInfo5 = nullptr;

/// <summary>
/// 接口说明:获取条码编码模式.
/// <para>API编码:[92243035]</para>
/// <para>文档定位:数据-对象操作-对象通用读写</para>
/// </summary>
/// <param name="idEnt">:对象ID</param>
/// <param name="nEncodeMode">:编码模式 0：Auto 1:Numeric 2:Alpha Numeric 3:Byte 4:Kanji;</param>
/// <param name="nCheckLevel">:错误纠正级：0-3 对应LMQH;</param>
/// <param name="nMaskPattern">:掩码：0-8对应auto 0-7;</param>
e3_GetTextBarcodeInfo6 E3_GetTextBarcodeInfo6 = nullptr;

/// <summary>
/// 接口说明:用于获取指定ID对象的文本内容.
/// <para>API编码:[49755439]</para>
/// <para>文档定位:数据-对象操作-对象ID关系</para>
/// </summary>
/// <param name="idEnt">:对象ID</param>
/// <param name="pStr[256]">:指定ID的文本内容;</param>
e3_GetTextByID E3_GetTextByID = nullptr;

/// <summary>
/// 接口说明:验证条码内容是否有效，有效是指是否符合该条码类型的编码规则，编码规则可见标准软件条码信息说明.
/// <para>API编码:[06560219]</para>
/// <para>文档定位:数据-对象操作-对象通用读写</para>
/// </summary>
/// <param name="nMaxParamN">:最大整形数据.默认值23;</param>
/// <param name="nParam">:具体请查看字体类型附录;</param>
/// <param name="nMaxParamD">:最大浮点型数据.默认值28;</param>
/// <param name="dParam">:具体请查看字体造型参数附录;</param>
/// <param name="strFontName">:条码字体类型;</param>
/// <param name="strText">:条码文本内容;</param>
/// <param name="bIsValid">:是否为条码有效:True:有效;</param>
e3_IsBarcodeTextValid E3_IsBarcodeTextValid = nullptr;

/// <summary>
/// 接口说明:插入计数值. 计数值相当于在板卡中添加一个标志位，每次加1计录列表加工数目.
/// <para>API编码:[79735281]</para>
/// <para>文档定位:硬件-资源-寄存器-写</para>
/// </summary>
/// <param name="idMarker">:控制卡ID</param>
/// <param name="n">:每次计数的增量，每次加的个数.固定为1;</param>
e3_MarkerChangeMarkCountToList E3_MarkerChangeMarkCountToList = nullptr;

/// <summary>
/// 接口说明:设置条码详细信息. 使用E3_GetLayerId得到层id, E3_FindEntInLayerByIndex得到指定对象ID, E3_GetAllFontCount获得当前系统包含字体数量，E3_GetAllFontRecord获得字体类型及名称用于条码字体类型及明码名称的设置.
/// <para>API编码:[80865706]</para>
/// <para>文档定位:数据-对象操作-对象通用读写</para>
/// </summary>
/// <param name="idEM">:对象管理器ID</param>
/// <param name="idEnt">:对象ID</param>
/// <param name="nMaxParamN">:最大整形数据.默认23;</param>
/// <param name="nParam">:条码属性数组,每一位代表一个属性,具体请查看附录;</param>
/// <param name="nMaxParamD">:最大浮点型数据.默认值28;</param>
/// <param name="dParam">:条码造型数组,每一位代表一个造型参数,具体请查看附录;</param>
/// <param name="str1">:条码字体类型名称,0-255;</param>
/// <param name="str2">:明码字体名称,0-255;</param>
/// <param name="param1">:第一组填充参数;</param>
/// <param name="param2">:第二组填充参数;</param>
/// <param name="param3">:第三组填充参数;</param>
/// <param name="strText">:文本内容,0-4098;</param>
/// <param name="reserved1">:预留接口.默认值:flase;</param>
/// <param name="reserved2">:预留接口.默认值:"";</param>
e3_SetTextBarcodeInfo E3_SetTextBarcodeInfo = nullptr;

/// <summary>
/// 接口说明:设置二维码尺寸的接口，调用此接口后需调用E3_SetTextBarcodeInfo才可让设置尺寸接口设置成功
/// <para>API编码:[36748373]</para>
/// <para>文档定位:数据-对象操作-对象通用读写</para>
/// </summary>
/// <param name="idEnt">:对象ID</param>
/// <param name="nPointMode">:条码模式（4=螺旋 3=点 1=矩形 2=圆 0=标准模式）;</param>
/// <param name="dPointSize">:尺寸;</param>
/// <param name="bFixedSize">:是否使用固定尺寸;</param>
/// <param name="dFixedSizeX">:固定X尺寸;</param>
/// <param name="dFixedSizeY">:固定Y尺寸;</param>
e3_SetTextBarcodeInfo4 E3_SetTextBarcodeInfo4 = nullptr;

/// <summary>
/// 接口说明:设置条码螺旋线模式参数，调用此接口后需调用E3_SetTextBarcodeInfo才可让设置尺寸接口设置成功.
/// <para>API编码:[87689862]</para>
/// <para>文档定位:数据-对象操作-对象通用读写</para>
/// </summary>
/// <param name="idEnt">:对象ID</param>
/// <param name="nInsideLoop">:内边界环数;</param>
/// <param name="nOutsideLoop">:外边界环数;</param>
/// <param name="bSpiralInsideToOutside">:由内向外;</param>
/// <param name="dSpiralPitchDist">:螺旋线螺距mm;</param>
/// <param name="dSpiralMinRadius">:最小半径mm;</param>
e3_SetTextBarcodeInfo5 E3_SetTextBarcodeInfo5 = nullptr;

/// <summary>
/// 接口说明:设置条码编码模式.
/// <para>API编码:[55834520]</para>
/// <para>文档定位:数据-对象操作-对象通用读写</para>
/// </summary>
/// <param name="idEnt">:对象ID</param>
/// <param name="nEncodeMode">:编码模式 0：Auto 1:Numeric 2:Alpha Numeric 3:Byte 4:Kanji;</param>
/// <param name="nCheckLevel">:错误纠正级 0-3 对应 LMQH</param>
/// <param name="nMaskPattern">:掩码 0-8 对应 auto 0-7</param>
e3_SetTextBarcodeInfo6 E3_SetTextBarcodeInfo6 = nullptr;

/// <summary>
/// 接口说明:设置条码详细信息. 使用E3_GetLayerId得到层id, E3_FindEntInLayerByIndex得到指定对象ID, E3_GetAllFontCount获得当前系统包含字体数量，E3_GetAllFontRecord获得字体类型及名称用于条码字体类型及明码名称的设置.
/// <para>API编码:[44573425]</para>
/// <para>文档定位:数据-对象操作-对象通用读写</para>
/// </summary>
/// <param name="idEM">:对象管理器ID</param>
/// <param name="idEnt">:对象ID</param>
/// <param name="nMaxParamN">:最大整形数据.默认23;</param>
/// <param name="nParam">:条码属性数组,每一位代表一个属性,具体请查看附录;</param>
/// <param name="nMaxParamD">:最大浮点型数据.默认值28;</param>
/// <param name="dParam">:条码造型数组,每一位代表一个造型参数,具体请查看附录;</param>
/// <param name="str1">:条码字体类型名称,0-255;</param>
/// <param name="str2">:明码字体名称,0-255;</param>
/// <param name="param1">:第一组填充参数;</param>
/// <param name="param2">:第二组填充参数;</param>
/// <param name="param3">:第三组填充参数;</param>
/// <param name="strText">:文本内容,0-4098;</param>
e3_SetTextBarcodeInfo_2 E3_SetTextBarcodeInfo_2 = nullptr;

/// <summary>
/// 接口说明:得到对象基础信息2.
/// <para>API编码:[92336735]</para>
/// <para>文档定位:数据-对象操作-对象通用读写</para>
/// </summary>
/// <param name="idEnt">:对象ID</param>
/// <param name="type">:对象类型</param>
/// <param name="nPen">:对象笔号</param>
/// <param name="strName[256]">:对象名字</param>
/// <param name="box">:对象外包盒</param>
/// <param name="z">:对象z坐标</param>
/// <param name="a">:对象A坐标</param>
/// <param name="dSizeZ">:Z方向落差</param>
e3_GetEntBaseInfo2 E3_GetEntBaseInfo2 = nullptr;

/// <summary>
/// 接口说明:得到对象基础信息3.
/// <para>API编码:[35370579]</para>
/// <para>文档定位:数据-对象操作-对象通用读写</para>
/// </summary>
/// <param name="idEnt">:对象ID</param>
/// <param name="type">:对象类型</param>
/// <param name="nPen">:对象笔号</param>
/// <param name="strName[256]">:对象名字</param>
/// <param name="box">:对象外包盒</param>
/// <param name="z">:对象z坐标</param>
/// <param name="a">:对象A坐标</param>
/// <param name="nMarkCount">:重复加工次数</param>
e3_GetEntBaseInfo3 E3_GetEntBaseInfo3 = nullptr;

/// <summary>
/// 接口说明:得到卡配置参数中各个类型参数的总数
/// <para>API编码:[03288115]</para>
/// <para>文档定位:环境-控制卡-配置</para>
/// </summary>
/// <param name="idMarker">:控制卡ID</param>
/// <param name="nParamInt">:int类型参数总数</param>
/// <param name="nParamDouble">:double类型参数总数</param>
/// <param name="nParamStr">:string类型参数总数</param>
e3_GetParamCount E3_GetParamCount = nullptr;

/// <summary>
/// 接口说明:获取笔参数
/// <para>API编码:[31526290]</para>
/// <para>文档定位:数据-笔参数相关</para>
/// </summary>
/// <param name="idEM">:管理器ID</param>
/// <param name="nPenNo">:笔号</param>
/// <param name="pStrName[256]">:笔名称</param>
/// <param name="clr">:笔颜色</param>
/// <param name="bDisableMark">:使能</param>
/// <param name="bUseDefParam">:使用默认</param>
/// <param name="nMarkLoop">:加工次数</param>
/// <param name="dMarkSpeed">:标刻速度mm/s</param>
/// <param name="dPowerRatio">:功率%</param>
/// <param name="dCurrent">:电流A</param>
/// <param name="dFreq">:频率HZ</param>
/// <param name="dQPulseWidth">:脉冲宽度us|ns</param>
/// <param name="nStartTC">:开始延时us</param>
/// <param name="nLaserOffTC">:关闭延时us</param>
/// <param name="nEndTC">:结束延时us</param>
/// <param name="nPolyTC">:拐角延时us</param>
/// <param name="dJumpSpeed">:跳转速度mm/s</param>
/// <param name="nMinJumpDelayTCUs">:最小跳转延时us</param>
/// <param name="nMaxJumpDelayTCUs">:最大跳转延时us</param>
/// <param name="dJumpLengthLimit">:跳转长度极限mm</param>
/// <param name="dPointTimeMs">:打点时间ms</param>
/// <param name="nSpiSpiContinueMode">:SPI连续模式</param>
/// <param name="nSpiWave">:SPI波形选择</param>
/// <param name="nYagMarkMode">:YAG优化填充模式</param>
/// <param name="bPulsePointMode">:脉冲点模式</param>
/// <param name="nPulseNum">:脉冲点数</param>
/// <param name="bEnableACCMode">:使能加速模式</param>
/// <param name="dEndComp">:末点补偿</param>
/// <param name="dAccDist">:加速距离mm</param>
/// <param name="dBreakAngle">:中断角度(89)（弧度值）;已经被淘汰，暂时保留</param>
/// <param name="bWobbleMode">:抖动模式(false);已经升级，目前版本不再使用这个参数</param>
/// <param name="bWobbleDiameter">:抖动直径(1)mm;已经升级，目前版本不再使用这个参数</param>
/// <param name="bWobbleDist">:抖动距离(0.5)mm;已经升级，目前版本不再使用这个参数</param>
e3_GetPenParam E3_GetPenParam = nullptr;

/// <summary>
/// 接口说明:得到优化模式参数
/// <para>API编码:[88005718]</para>
/// <para>文档定位:数据-笔参数相关</para>
/// </summary>
/// <param name="idEM">:管理器ID</param>
/// <param name="nPenNo">:笔号</param>
/// <param name="bOpitmize">:使能优化模式</param>
/// <param name="dScanberBiDirOffset">:双向偏移</param>
/// <param name="dAccDist">:加速距离</param>
/// <param name="dEndDist">:结束距离</param>
e3_GetPenParamExt4 E3_GetPenParamExt4 = nullptr;

/// <summary>
/// 接口说明:获取焊接参数
/// <para>API编码:[26334623]</para>
/// <para>文档定位:数据-笔参数相关</para>
/// </summary>
/// <param name="idEM">:管理器ID</param>
/// <param name="nPenNo">:笔号</param>
/// <param name="nMarkLoop">:加工数目</param>
/// <param name="bAveragePtMode">:是否平均分布所有点</param>
/// <param name="dPointDist">:点间距</param>
/// <param name="nPulseNum">:每点脉冲数</param>
e3_GetPenParamExt5 E3_GetPenParamExt5 = nullptr;

/// <summary>
/// 接口说明:得到当前标刻状态信息
/// <para>API编码:[41430745]</para>
/// <para>文档定位:环境-控制卡-配置</para>
/// </summary>
/// <param name="idMarker">:控制卡ID</param>
/// <param name="bHaveMsg">:当前加工中是否存在消息</param>
/// <param name="strMsg[256]">:调用接口后返回的消息内容</param>
/// <param name="nPartCount">:返回当前加工的对象总数</param>
/// <param name="nPartTime">:返回对象加工次数</param>
e3_MarkerGetMsg E3_MarkerGetMsg = nullptr;

/// <summary>
/// 接口说明:读取控制卡的Double类型的参数集合.
/// <para>API编码:[55234352]</para>
/// <para>文档定位:环境-控制卡-配置</para>
/// </summary>
/// <param name="idMarker">:控制卡ID</param>
/// <param name="nMaxParamCount">:给定最大double参数个数</param>
/// <param name="pParamDouble">:读取到的double类型的参数值数组</param>
e3_MarkerGetParamDouble E3_MarkerGetParamDouble = nullptr;

/// <summary>
/// 接口说明:读取控制卡的Int类型的参数集合.
/// <para>API编码:[32962026]</para>
/// <para>文档定位:环境-控制卡-配置</para>
/// </summary>
/// <param name="idMarker">:控制卡ID</param>
/// <param name="nMaxParamCount">:给定最大int参数个数</param>
/// <param name="pParamInt">:读取到的int类型的参数值数组</param>
e3_MarkerGetParamInt E3_MarkerGetParamInt = nullptr;

/// <summary>
/// 接口说明:读取控制卡的string类型的参数集合.
/// <para>API编码:[08031012]</para>
/// <para>文档定位:环境-控制卡-配置</para>
/// </summary>
/// <param name="idMarker">:控制卡ID</param>
/// <param name="nParamId">:读取string类型参数的索引ID</param>
/// <param name="pParamInt[256]">:读取到的string类型得参数值</param>
e3_MarkerGetParamString E3_MarkerGetParamString = nullptr;

/// <summary>
/// 接口说明:USB连接侦测功能的初始化启动
/// <para>API编码:[83918892]</para>
/// <para>文档定位:环境-初始化以及释放</para>
/// </summary>
/// <param name="pWndMonitor">:侦测结果通过系统消息泵来传送,这里要给定接收消息的目标窗体句柄.</param>
e3_MarkerInitUsbMonitor E3_MarkerInitUsbMonitor = nullptr;

/// <summary>
/// 接口说明:列表系统的终结指令,板卡执行列表系统时执行到这一条指令后会退出列表系统.
/// <para>API编码:[87588443]</para>
/// <para>文档定位:硬件-组合动作-列表命令-列表过程命令</para>
/// </summary>
/// <param name="idMarker">:控制卡ID</param>
e3_MarkerListEndToList E3_MarkerListEndToList = nullptr;

/// <summary>
/// 接口说明:设置控制卡的Double类型参数
/// <para>API编码:[92701320]</para>
/// <para>文档定位:环境-控制卡-配置</para>
/// </summary>
/// <param name="idMarker">:控制卡ID</param>
/// <param name="nMaxParamCount">:给定设置最大double参数个数</param>
/// <param name="pParamDouble">:要设置的参数数组</param>
e3_MarkerSetParamDouble E3_MarkerSetParamDouble = nullptr;

/// <summary>
/// 接口说明:设置控制卡的Int类型参数
/// <para>API编码:[36329220]</para>
/// <para>文档定位:环境-控制卡-配置</para>
/// </summary>
/// <param name="idMarker">:控制卡ID</param>
/// <param name="nMaxParamCount">:给定设置最大int参数个数</param>
/// <param name="pParamInt">:要设置的参数数组</param>
e3_MarkerSetParamInt E3_MarkerSetParamInt = nullptr;

/// <summary>
/// 接口说明:流水线高低速偏差校正表
/// <para>API编码:[27230083]</para>
/// <para>文档定位:环境-控制卡-配置</para>
/// </summary>
/// <param name="idMarker">:控制卡ID</param>
/// <param name="Enable">:是否使能: 0x0=失能; 0x1=使能;</param>
/// <param name="TableSize">:指定校正表大小,最大32组;每组两个元素位置,最大也即64个数组元素.</param>
/// <param name="TableAddr">:校正表速度差值,示例: [0]速度值,单位mm/s; [1]补偿值,单位mm; [2]速度值,单位mm/s; [3]补偿值,单位mm; [...]速度值,单位mm/s; [...+1]补偿值,单位mm;</param>
e3_MarkerLoadFlyDistanceCorrectionTable E3_MarkerLoadFlyDistanceCorrectionTable = nullptr;

/// <summary>
/// 接口说明:通过对象ID修改对象的内容,仅限文本类型对象
/// <para>API编码:[77449635]</para>
/// <para>文档定位:数据-标准图元-编辑-文本类型-文本</para>
/// </summary>
/// <param name="idEnt">:对象ID</param>
/// <param name="strTextNew">:新的内容字符</param>
e3_ChangeTextById E3_ChangeTextById = nullptr;

/// <summary>
/// 接口说明:通过对象名称修改对象的内容,仅限文本类型对象
/// <para>API编码:[60245749]</para>
/// <para>文档定位:数据-标准图元-编辑-文本类型-文本</para>
/// </summary>
/// <param name="idLayer">:图层ID</param>
/// <param name="strEntName">:对象的名称</param>
/// <param name="strTextNew">:新的内容字符</param>
e3_ChangeTextByName E3_ChangeTextByName = nullptr;

/// <summary>
/// 接口说明:关闭函数库
/// <para>API编码:[85868531]</para>
/// <para>文档定位:环境-初始化以及释放</para>
/// </summary>
e3_Close E3_Close = nullptr;

/// <summary>
/// 接口说明:将位图文件添加到管理器中. 支持BMP,JPG,JPEG,GIF,TGA,PNG,TIF,TIFF. *上述支持类型在Windows版本系统上测试通过
/// <para>API编码:[39650013]</para>
/// <para>文档定位:数据-标准图元-创建</para>
/// </summary>
/// <param name="idEM">:管理器ID</param>
/// <param name="nPen">:笔号</param>
/// <param name="strBmpFile">:文件路径</param>
/// <param name="nBmpAttrib">:位图属性.详细请参见附录</param>
/// <param name="nScanAttrib">:扫描参数,详细请参见附录</param>
/// <param name="ptBase">:工作空间中XY左下脚位置</param>
/// <param name="reserved1">:预留接口.默认值:flase</param>
/// <param name="reserved2">:预留接口.默认值:flase</param>
/// <param name="reserved3">:预留接口.默认值:""</param>
e3_CreateBitmap E3_CreateBitmap = nullptr;

/// <summary>
/// 接口说明:将位图文件添加到管理器中. 支持BMP,JPG,JPEG,GIF,TGA,PNG,TIF,TIFF. *上述支持类型在Windows版本系统上测试通过
/// <para>API编码:[50941709]</para>
/// <para>文档定位:数据-标准图元-创建</para>
/// </summary>
/// <param name="idEM">:管理器ID</param>
/// <param name="nPen">:笔号</param>
/// <param name="strBmpFile">:文件路径</param>
/// <param name="nBmpAttrib">:位图属性.详细请参见附录</param>
/// <param name="nScanAttrib">:扫描参数,详细请参见附录</param>
/// <param name="ptBase">:工作空间中XY左下脚位置</param>
/// <param name="bUpdateParentInfo">:是否更新列表信息</param>
/// <param name="idNewEnt">:返回添加对象ID</param>
e3_CreateBitmap_2 E3_CreateBitmap_2 = nullptr;

/// <summary>
/// 接口说明:创建对象管理器,管理器为软件运行的容器，标准软件中设置对象为mm，若此接口设置为英寸，对象尺寸会由mm转化为英寸
/// <para>API编码:[23385706]</para>
/// <para>文档定位:环境-初始化以及释放</para>
/// </summary>
/// <param name="nUnitType">:创建对象管理器的单位=.0单位为毫米，=1单位为英寸</param>
e3_CreateEntMgr E3_CreateEntMgr = nullptr;

/// <summary>
/// 接口说明:在调用E3_Initial前有效.可以使用此函数设置是否弹出控制卡丢失的对话框,调用此函数即不显示弹框
/// <para>API编码:[21346364]</para>
/// <para>文档定位:环境-初始化以及释放</para>
/// </summary>
e3_DisableInitialPrompt E3_DisableInitialPrompt = nullptr;

/// <summary>
/// 接口说明:显示填充进度条
/// <para>API编码:[76596691]</para>
/// <para>文档定位:数据-填充相关</para>
/// </summary>
/// <param name="b">:是否使能</param>
e3_EnableShowHatchProcess E3_EnableShowHatchProcess = nullptr;

/// <summary>
/// 接口说明:得到指定图层指定索引的对象id
/// <para>API编码:[97609081]</para>
/// <para>文档定位:数据-对象操作-对象ID关系</para>
/// </summary>
/// <param name="idLayer">:图层ID</param>
/// <param name="nEntIndex">:要获取对象ID的对象索引号</param>
/// <param name="idEnt">:返回的对象ID</param>
e3_FindEntInLayerByIndex E3_FindEntInLayerByIndex = nullptr;

/// <summary>
/// 接口说明:得到指定图层指定对象名称的id
/// <para>API编码:[51828854]</para>
/// <para>文档定位:数据-对象操作-对象ID关系</para>
/// </summary>
/// <param name="idLayer">:图层ID</param>
/// <param name="strEntName">:对象的名称</param>
/// <param name="idEnt">:返回的对象ID</param>
e3_FindEntInLayerByName E3_FindEntInLayerByName = nullptr;

/// <summary>
/// 接口说明:释放对象管理器
/// <para>API编码:[13797725]</para>
/// <para>文档定位:环境-初始化以及释放</para>
/// </summary>
/// <param name="idEM">:管理器ID</param>
e3_FreeEntMgr E3_FreeEntMgr = nullptr;

/// <summary>
/// 接口说明:得到指定对象的预览图片
/// <para>API编码:[01389431]</para>
/// <para>文档定位:数据-对象操作-对象间操作</para>
/// </summary>
/// <param name="idEnt">:对象ID</param>
/// <param name="nParam">:为0即可</param>
/// <param name="bmpwidth">:窗口的像素宽</param>
/// <param name="bmpheight">:窗口的像素高</param>
/// <param name="dLogOriginX">:窗口的左下角对应点的x向逻辑坐标</param>
/// <param name="dLogOriginY">:窗口的左下角对应点的y向逻辑坐标</param>
/// <param name="dLogScale">:窗口对应的逻辑尺寸与窗口像素尺寸的比例</param>
e3_GetEntBitmap E3_GetEntBitmap = nullptr;

/// <summary>
/// 接口说明:获取加工参数库中的参数的数量
/// <para>API编码:[00290942]</para>
/// <para>文档定位:数据-笔参数相关</para>
/// </summary>
/// <param name="nCount">:返回参数的数量</param>
e3_GetParamLibCount E3_GetParamLibCount = nullptr;

/// <summary>
/// 接口说明:获取加工参数库中的指定位置的参数名
/// <para>API编码:[89145991]</para>
/// <para>文档定位:数据-笔参数相关</para>
/// </summary>
/// <param name="nIndex">:将要获取参数名的从0开始的下标</param>
/// <param name="strName[256]">:获取到对应下标参数的参数名</param>
e3_GetParamLibName E3_GetParamLibName = nullptr;

/// <summary>
/// 接口说明:得到激光扩展输出口索引
/// <para>API编码:[59069335]</para>
/// <para>文档定位:硬件-资源-激光-配置</para>
/// </summary>
/// <param name="idEM">:管理器ID</param>
/// <param name="nPenNo">:笔号</param>
/// <param name="_nLasetExtOutputIndex">:扩展输出口索引</param>
e3_GetPenParamExtOutputIndex E3_GetPenParamExtOutputIndex = nullptr;

/// <summary>
/// 接口说明:得到频率渐变参数
/// <para>API编码:[11534671]</para>
/// <para>文档定位:数据-笔参数相关</para>
/// </summary>
/// <param name="idEM">:管理器ID</param>
/// <param name="nPenNo">:笔号</param>
/// <param name="bAccSegEnable">:使能起始</param>
/// <param name="dAccSegStartRatio">:起始比例</param>
/// <param name="dAccSegLen">:起始长度;起始频率渐变的长度</param>
/// <param name="bDecSegEnable">:使能结束</param>
/// <param name="dDecSegStartRatio">:结束频率比例%;实际频率为当前加工参数频率乘此百分比</param>
/// <param name="dDecSegLen">:结束长度;结束频率渐变的长度</param>
e3_GetPenParamFreqRamp E3_GetPenParamFreqRamp = nullptr;

/// <summary>
/// 接口说明:得到指定笔号的激光滞后时间
/// <para>API编码:[56708316]</para>
/// <para>文档定位:数据-笔参数相关</para>
/// </summary>
/// <param name="idEM">:管理器ID</param>
/// <param name="nPenNo">:笔号</param>
/// <param name="bEnable">:是否使能激光滞后时间</param>
/// <param name="nTimeUs">:激光滞后时间us</param>
e3_GetPenParamLaserLagTime E3_GetPenParamLaserLagTime = nullptr;

/// <summary>
/// 接口说明:得到功率渐变参数
/// <para>API编码:[89121745]</para>
/// <para>文档定位:数据-笔参数相关</para>
/// </summary>
/// <param name="idEM">:管理器ID</param>
/// <param name="nPenNo">:笔号</param>
/// <param name="bAccSegEnable">:使能起始</param>
/// <param name="dAccSegStartRatio">:实际出光功率为当前加工参数功率乘此百分比</param>
/// <param name="dAccSegLen">:起始长度;起始功率渐变的长度</param>
/// <param name="bDecSegEnable">:使能结束</param>
/// <param name="dDecSegStartRatio">:结束功率比例%;实际出光功率为当前加工参数功率乘此百分比</param>
/// <param name="dDecSegLen">:结束长度;结束功率渐变的长度</param>
e3_GetPenParamPowerRamp E3_GetPenParamPowerRamp = nullptr;

/// <summary>
/// 接口说明:获取匀速笔标刻参数
/// <para>API编码:[50713168]</para>
/// <para>文档定位:数据-笔参数相关</para>
/// </summary>
/// <param name="idEM">:管理器ID</param>
/// <param name="nPenNo">:笔号</param>
/// <param name="bSkyWrite">:使能</param>
/// <param name="nSkyWriteMode">:匀速模式</param>
/// <param name="dSkyWriteLimitAngle">:极限角度</param>
/// <param name="nSkyWriteNprev">:导入周期.默认10us</param>
/// <param name="nSkyWriteNpost">:导出周期.默认10us</param>
/// <param name="dSkyWriteTimelag">:滞后时间us</param>
/// <param name="nSkyWriteLaserOnShift">:漂移时间us</param>
e3_GetPenParamSkyWriting E3_GetPenParamSkyWriting = nullptr;

/// <summary>
/// 接口说明:得到速度渐变参数
/// <para>API编码:[33388533]</para>
/// <para>文档定位:数据-笔参数相关</para>
/// </summary>
/// <param name="idEM">:管理器ID</param>
/// <param name="nPenNo">:笔号</param>
/// <param name="bAccSegEnable">:使能起始</param>
/// <param name="dAccSegStartRatio">:起始速度比例%;实际振镜摆动为当前加工参数速度乘此百分比</param>
/// <param name="dAccSegLen">:起始长度;起始速度渐变的长度</param>
/// <param name="bDecSegEnable">:使能结束</param>
/// <param name="dDecSegStartRatio">:结束比例%;实际振镜摆动速度为当前加工参数速度乘此百分比</param>
/// <param name="dDecSegLen">:结束长度;结束速度渐变的长度</param>
e3_GetPenParamSpeedRamp E3_GetPenParamSpeedRamp = nullptr;

/// <summary>
/// 接口说明:获取步距标刻参数
/// <para>API编码:[13651106]</para>
/// <para>文档定位:数据-笔参数相关</para>
/// </summary>
/// <param name="idEM">:管理器ID</param>
/// <param name="nPenNo">:笔号</param>
/// <param name="bEnableStepMode">:步距模式</param>
/// <param name="dMarkStep">:优化长度</param>
e3_GetPenParamStep E3_GetPenParamStep = nullptr;

/// <summary>
/// 接口说明:获取QCW波形输出
/// <para>API编码:[55255427]</para>
/// <para>文档定位:数据-笔参数相关</para>
/// </summary>
/// <param name="idEM">:管理器ID</param>
/// <param name="nPenNo">:笔号</param>
/// <param name="dWeldWavePower">:功率（每个功率[0,100]）</param>
/// <param name="dWeldWaveWidthMs">:脉宽（ms）(64个脉宽值的和不可超过笔参数中设置的总脉宽);[0,63]</param>
e3_GetPenParamWeldWave E3_GetPenParamWeldWave = nullptr;

/// <summary>
/// 接口说明:获取QCW波形输出（与不带2的相比多了是否使能连续模式及是否使能波形输出两个参数）.
/// <para>API编码:[72576032]</para>
/// <para>文档定位:数据-笔参数相关</para>
/// </summary>
/// <param name="idEM">:管理器ID</param>
/// <param name="nPenNo">:笔号</param>
/// <param name="bLaserContMode">:是否使能连续模式（true为使能）</param>
/// <param name="bEnableWeldWave">:是否使能波形输出(true为使能)</param>
/// <param name="nMaxCount">:波形输出最大组数;[0,63]</param>
/// <param name="dWeldWavePower">:功率（每个功率[0,100]）</param>
/// <param name="dWeldWaveWidthMs">:脉宽（ms）(64个脉宽值的和不可超过笔参数中设置的总脉宽);[0,63]</param>
e3_GetPenParamWeldWave2 E3_GetPenParamWeldWave2 = nullptr;

/// <summary>
/// 接口说明:获取抖动参数
/// <para>API编码:[19400799]</para>
/// <para>文档定位:数据-笔参数相关</para>
/// </summary>
/// <param name="idEM">:管理器ID</param>
/// <param name="nPenNo">:笔号</param>
/// <param name="bWobbleMode">:使能抖动</param>
/// <param name="nWobbleType">:抖动类型(5种：分别为螺旋线，正弦曲线，椭圆，垂直8字，水平8字)</param>
/// <param name="dWobbleDiameter">:直径mm</param>
/// <param name="dWobbleDiameterB">:抖动直径2 (mm)</param>
/// <param name="dWobbleDist">:抖动距离 mm</param>
e3_GetPenParamWobble E3_GetPenParamWobble = nullptr;

/// <summary>
/// 接口说明:获取抖动的相对速度
/// <para>API编码:[44967736]</para>
/// <para>文档定位:数据-笔参数相关</para>
/// </summary>
/// <param name="idEM">:管理器ID</param>
/// <param name="nPenNo">:笔号</param>
/// <param name="dWobbleIncSpeed">:抖动的相对速度</param>
e3_GetPenParamWobbleIncSpeed E3_GetPenParamWobbleIncSpeed = nullptr;

/// <summary>
/// 接口说明:初始化开发库
/// <para>API编码:[06231488]</para>
/// <para>文档定位:环境-初始化以及释放</para>
/// </summary>
/// <param name="strWorkPath">:Ezcad3.exe所处的目录的全路径名称，例如C:\WorkBook\20180528\EzCAD3\Debug</param>
/// <param name="nFlag">:否是测试模式,默认0</param>
e3_Initial E3_Initial = nullptr;

/// <summary>
/// 接口说明:监视USB-关闭设备检测
/// <para>API编码:[30913458]</para>
/// <para>文档定位:环境-初始化以及释放</para>
/// </summary>
e3_MarkerCloseUsbMonitor E3_MarkerCloseUsbMonitor = nullptr;

/// <summary>
/// 接口说明:设置等待延时
/// <para>API编码:[16692804]</para>
/// <para>文档定位:硬件-组合动作-列表命令-对象级列表命令</para>
/// </summary>
/// <param name="idMarker">:控制卡ID</param>
/// <param name="us">:延时时间（单位：us）</param>
e3_MarkerDelayUsToList E3_MarkerDelayUsToList = nullptr;

/// <summary>
/// 接口说明:打开设备参数窗体.会弹出库中集成的参数设置窗体.进行对系统的参数设置
/// <para>API编码:[13101121]</para>
/// <para>文档定位:环境-控制卡-配置</para>
/// </summary>
/// <param name="idMarker">:控制卡ID</param>
/// <param name="bReturnOk">:是否修改设备参数(若点击确认返回true)</param>
e3_MarkerDlgSetCfg E3_MarkerDlgSetCfg = nullptr;

/// <summary>
/// 接口说明:得到F3参数double型参数值
/// <para>API编码:[70751330]</para>
/// <para>文档定位:环境-控制卡-配置</para>
/// </summary>
/// <param name="idMarker">:控制卡ID</param>
/// <param name="nIndex">:索引值</param>
/// <param name="dParam">:当前索引的double的参数值</param>
e3_MarkerGetCfgParamDouble E3_MarkerGetCfgParamDouble = nullptr;

/// <summary>
/// 接口说明:得到F3参数Int型参数值
/// <para>API编码:[44416657]</para>
/// <para>文档定位:环境-控制卡-配置</para>
/// </summary>
/// <param name="idMarker">:控制卡ID</param>
/// <param name="nIndex">:索引值</param>
/// <param name="nParam">:当前索引的Int的参数值</param>
e3_MarkerGetCfgParamInt E3_MarkerGetCfgParamInt = nullptr;

/// <summary>
/// 接口说明:查看控制卡的关联对象管理器,此接口使用的前提为使用了[E3_MarkerSetEntMgr]接口
/// <para>API编码:[85205858]</para>
/// <para>文档定位:环境-控制卡-操作</para>
/// </summary>
/// <param name="idMarker">:控制卡ID</param>
/// <param name="idEM">:传出关联当前控制卡的管理器ID</param>
e3_MarkerGetEntMgr E3_MarkerGetEntMgr = nullptr;

/// <summary>
/// 接口说明:获取有效的控制卡的ID,单卡设备仅需执行一次，多卡设备需要多次执行，直到返回0，每台计算机最多支持8张卡，没有找到控制卡，会得到虚拟的卡ID
/// <para>API编码:[52307060]</para>
/// <para>文档定位:环境-控制卡-操作</para>
/// </summary>
e3_MarkerGetFirstValidId E3_MarkerGetFirstValidId = nullptr;

/// <summary>
/// 接口说明:监视USB-启动设备检测
/// <para>API编码:[89013925]</para>
/// <para>文档定位:环境-初始化以及释放</para>
/// </summary>
/// <param name="hWndMonitor">:当前窗体的句柄</param>
e3_MarkerInitUsbMonitor2 E3_MarkerInitUsbMonitor2 = nullptr;

/// <summary>
/// 接口说明:振镜以指定速度运动到指定位置（可见标准软件F3参数中振镜移动）
/// <para>API编码:[34048802]</para>
/// <para>文档定位:硬件-资源-振镜-动作</para>
/// </summary>
/// <param name="idMarker">:控制卡ID</param>
/// <param name="x">:X坐标</param>
/// <param name="y">:Y坐标</param>
/// <param name="z">:Z坐标</param>
/// <param name="spd">:指定速度</param>
e3_MarkerJumpTo E3_MarkerJumpTo = nullptr;

/// <summary>
/// 接口说明:单独控制激光开关
/// <para>API编码:[81185209]</para>
/// <para>文档定位:硬件-资源-激光-动作</para>
/// </summary>
/// <param name="idMarker">:控制卡ID</param>
/// <param name="nPenNo">:笔号</param>
/// <param name="bOn">:激光开关true开</param>
e3_MarkerLaserOn E3_MarkerLaserOn = nullptr;

/// <summary>
/// 接口说明:列表直接出激光接口
/// <para>API编码:[40056189]</para>
/// <para>文档定位:硬件-组合动作-列表命令-节点级列表命令</para>
/// </summary>
/// <param name="idMarker">:控制卡ID</param>
/// <param name="bOn">:是否可以开激光（true为开激光）</param>
e3_MarkerLaserOnToList E3_MarkerLaserOnToList = nullptr;

/// <summary>
/// 接口说明:待列表结束后执行清理与复位,列表流程必须. 放在[E3_MarkerWaitForFinish]接口之后,顺序不能错
/// <para>API编码:[54509179]</para>
/// <para>文档定位:硬件-组合动作-列表命令-列表过程命令</para>
/// </summary>
/// <param name="idMarker">:控制卡ID</param>
e3_MarkerListEnd E3_MarkerListEnd = nullptr;

/// <summary>
/// 接口说明:标刻准备. 开启列表，E3_MarkerStop接口会中断列表，若用列表需重新开启列表
/// <para>API编码:[27869676]</para>
/// <para>文档定位:硬件-加工动作-列表命令-列表过程命令</para>
/// </summary>
/// <param name="idMarker">:控制卡ID</param>
/// <param name="idEM">:管理器ID</param>
/// <param name="nFlag">:工作标识类型: 0x000000000 = 静态标刻; 0x000000002 = 红光指示; 0x000000400 =飞行标刻; 0x000002000 = 焊接模式; 0x000008000 =（只下发数据不加工）; 0x000200000 = 禁止飞行打标自动排序; 0x001000000 = 计算模式（用于预估加工时间）; 0x002000000 = 脱机模式;</param>
e3_MarkerListReady E3_MarkerListReady = nullptr;

/// <summary>
/// 接口说明:标刻或者红光预览指定对象. 标刻或者红光预览指定对象,与E3_MarkerGetFirstValidId获得板卡ID，E3_CreateEntMgr获得管理器ID，E3_FindEntInLayerByIndex获得指定对象ID配合使用，此接口红光指示时只是振镜摆动，若需出实际红光，可调用IO中设置输出口接口进行设置，红光是否显示轮廓可在程序同目录下的EZCAD3软件中进行设置，计算模式用于预估加工时间不会实际出光且记录标刻时间至板卡. 标刻接口是阻塞式,当标刻接口返回就代表加工完成,不过可能由于通讯等问题,状态变更会有一点点延时,但是并不明显.不过要考虑这一点,一般编写时会在标刻接口返回后在下一行加一个一毫秒的延时
/// <para>API编码:[36257416]</para>
/// <para>文档定位:硬件-资源-激光-动作</para>
/// </summary>
/// <param name="idMarker">:控制卡ID</param>
/// <param name="idEM">:管理器ID</param>
/// <param name="idEnt">:对象ID或层ID</param>
/// <param name="nMarkFlag">:工作标识类型:   0x0000       = 静态标刻;    0x0002       = 红光指示;   0x0400       = 飞行标刻;   0x000002000  = 焊接模式;   0x01000000   = 计算模式（用于预估加工时间）;   0x000008000  = 只下发数据不加工;</param>
/// <param name="nStartPartNum">:从第几个对象开始标刻</param>
/// <param name="nMaxPartCount">:标刻最大个数</param>
e3_MarkerMarkEnt2 E3_MarkerMarkEnt2 = nullptr;

/// <summary>
/// 接口说明:标刻指定对象，添加到列表，此接口需配合E3_MarkerListReady ,E3_MarkerListEnd, E3_MarkerWaitForFinish三个接口一起使用
/// <para>API编码:[01404368]</para>
/// <para>文档定位:硬件-组合动作-列表命令-对象级列表命令</para>
/// </summary>
/// <param name="idMarker">:控制卡ID</param>
/// <param name="idEnt">:对象ID或层ID</param>
e3_MarkerMarkEntToList2 E3_MarkerMarkEntToList2 = nullptr;

/// <summary>
/// 接口说明:按笔号标刻指定对象，添加到列表
/// <para>API编码:[16269043]</para>
/// <para>文档定位:硬件-组合动作-列表命令-对象级列表命令</para>
/// </summary>
/// <param name="idMarker">:控制卡ID</param>
/// <param name="idEnt">:对象ID或层ID</param>
/// <param name="nPenNo">:笔号</param>
e3_MarkerMarkEntToListByPen E3_MarkerMarkEntToListByPen = nullptr;

/// <summary>
/// 接口说明:标刻一条2D曲线. 标刻一条指定参数的2D曲线，此接口需配合E3_MarkerListReady ,E3_MarkerListEnd, E3_MarkerWaitForFinish三个接口一起使用
/// <para>API编码:[85883362]</para>
/// <para>文档定位:数据-标准图元-创建</para>
/// </summary>
/// <param name="idMarker">:控制卡ID</param>
/// <param name="type">:保留,默认0</param>
/// <param name="pen">:笔号</param>
/// <param name="ptNum">:曲线顶点数</param>
/// <param name="nFlag">:0x0002 红光指示  0x0000 静态标刻 =0x0400飞行标刻</param>
/// <param name="ptBuf">:曲线顶点数组;ptBuf点坐标组；ptBuf[n,0]表示第n个点的x坐标，ptBuf[n,1]表示第n个点的y坐标,ptBuf[n,2]表示第n个点的z坐标</param>
e3_MarkerOneCurveToList E3_MarkerOneCurveToList = nullptr;

/// <summary>
/// 接口说明:读输入口. 在程序中调用此函数来读入当前输入端口的数据. Bit0是In0的状态,Bit0=1表示In0为高电平,Bit0=0表示In0为低电平. Bit1是In1的状态,Bit1=1表示In1为高电平,Bit1=0表示In1为低电平,依次类推. 如果获取值为5，表示IN0,IN2是高电平，其他端口都是低电平
/// <para>API编码:[35178069]</para>
/// <para>文档定位:硬件-资源-数字量IN-查询</para>
/// </summary>
/// <param name="idMarker">:控制卡ID</param>
/// <param name="data">:读取到的端入口值</param>
e3_MarkerReadPort E3_MarkerReadPort = nullptr;

/// <summary>
/// 接口说明:计数复位,复位列表计数的数目
/// <para>API编码:[59779327]</para>
/// <para>文档定位:硬件-资源-寄存器-写</para>
/// </summary>
/// <param name="idMarker">:控制卡ID</param>
e3_MarkerResetMarkCount E3_MarkerResetMarkCount = nullptr;

/// <summary>
/// 接口说明:设置F3参数double型参数值
/// <para>API编码:[55511348]</para>
/// <para>文档定位:环境-控制卡-配置</para>
/// </summary>
/// <param name="idMarker">:控制卡ID</param>
/// <param name="nIndex">:索引值</param>
/// <param name="dParam">:当前索引的double的参数值</param>
e3_MarkerSetCfgParamDouble E3_MarkerSetCfgParamDouble = nullptr;

/// <summary>
/// 接口说明:设置F3参数Int型参数值
/// <para>API编码:[15491583]</para>
/// <para>文档定位:环境-控制卡-配置</para>
/// </summary>
/// <param name="idMarker">:控制卡ID</param>
/// <param name="nIndex">:索引值</param>
/// <param name="nParam">:当前索引的Int的参数值</param>
e3_MarkerSetCfgParamInt E3_MarkerSetCfgParamInt = nullptr;

/// <summary>
/// 接口说明:给控制卡发送校正表
/// <para>API编码:[81296136]</para>
/// <para>文档定位:环境-控制卡-配置</para>
/// </summary>
/// <param name="idMarker">:控制卡ID</param>
/// <param name="szFileName[256]">:校正文件路径</param>
/// <param name="indexTable">:内校正表序号,范围: 1-4</param>
e3_MarkerSetCorFile2 E3_MarkerSetCorFile2 = nullptr;

/// <summary>
/// 接口说明:关联控制卡与对象管理器,在不需要使用模板的情况下,直接控制激光器进行开关光,则需要使用此接口,一般在初始化成功之后调用即可
/// <para>API编码:[80607194]</para>
/// <para>文档定位:环境-控制卡-配置</para>
/// </summary>
/// <param name="idMarker">:控制卡ID</param>
/// <param name="idEM">:管理器ID</param>
e3_MarkerSetEntMgr E3_MarkerSetEntMgr = nullptr;

/// <summary>
/// 接口说明:设置F3参数string型参数值
/// <para>API编码:[83152820]</para>
/// <para>文档定位:环境-控制卡-配置</para>
/// </summary>
/// <param name="idMarker">:控制卡ID</param>
/// <param name="nParamId">:参数索引</param>
/// <param name="pParamStr">:该索引对应的字符串</param>
e3_MarkerSetParamString E3_MarkerSetParamString = nullptr;

/// <summary>
/// 接口说明:监视USB-关闭设备检测
/// <para>API编码:[65299578]</para>
/// <para>文档定位:环境-初始化以及释放</para>
/// </summary>
/// <param name="idMarker">:获取到新的控制卡ID</param>
e3_MarkerUsbMonitorGetNewDevice E3_MarkerUsbMonitorGetNewDevice = nullptr;

/// <summary>
/// 接口说明:删除参数库中对应名称的参数配置
/// <para>API编码:[82400246]</para>
/// <para>文档定位:数据-笔参数相关</para>
/// </summary>
/// <param name="strName">:参数配置的名称</param>
e3_ParamLibDeleteName E3_ParamLibDeleteName = nullptr;

/// <summary>
/// 接口说明:更新保存给定笔号到对应参数名称的参数配置
/// <para>API编码:[11044294]</para>
/// <para>文档定位:数据-笔参数相关</para>
/// </summary>
/// <param name="idEM">:管理器ID</param>
/// <param name="nPenNo">:笔号</param>
/// <param name="strName">:参数配置的名称</param>
e3_ParamLibSavePenToName E3_ParamLibSavePenToName = nullptr;

/// <summary>
/// 接口说明:从参数库读取给定名称参数配置设置到给定的笔号
/// <para>API编码:[60153944]</para>
/// <para>文档定位:数据-笔参数相关</para>
/// </summary>
/// <param name="idEM">:管理器ID</param>
/// <param name="nPenNo">:笔号</param>
/// <param name="strName">:参数配置的名称</param>
e3_ParamLibSetPenFromName E3_ParamLibSetPenFromName = nullptr;

/// <summary>
/// 接口说明:设置图像参数
/// <para>API编码:[82265331]</para>
/// <para>文档定位:数据-标准图元-编辑-位图类型</para>
/// </summary>
/// <param name="idEM">:管理器ID</param>
/// <param name="idEnt">:对象ID</param>
/// <param name="nParamBuf">:整形数据.这里的整形数组长度为50,其中每一位元都存储一个参数,通过设置这个数组来进行图像的修改</param>
/// <param name="dParamBuf">:这里的浮点型数组长度为8,其中每一位元都存储一个参数,通过设置这个数组来进行图像的修改</param>
/// <param name="bGrayScaleBuf">:灰度功率表.长度为256,默认数元值与下标一致,例如:     _grayTables[0] = (byte)0;     _grayTables[1] = (byte)1;     ......     _grayTables[255] = (byte)255;     如果想要呈现不同不同功率不同灰度效果,可以修改此数组,ezcad3中存在此功能,可在ezcad3中事先查看效果.之后用接口实现</param>
/// <param name="str1">:位图对象文件路径</param>
/// <param name="reserved1">:预留参数,默认false</param>
/// <param name="reserved2">:预留参数,默认""</param>
e3_SetBmpFileInfo E3_SetBmpFileInfo = nullptr;

/// <summary>
/// 接口说明:设置图像参数2
/// <para>API编码:[73078029]</para>
/// <para>文档定位:数据-标准图元-编辑-位图类型</para>
/// </summary>
/// <param name="idEM">:管理器ID</param>
/// <param name="idEnt">:对象ID</param>
/// <param name="nParamBuf">:整形数据.这里的整形数组长度为50,其中每一位元都存储一个参数,通过设置这个数组来进行图像的修改</param>
/// <param name="dParamBuf">:这里的浮点型数组长度为8,其中每一位元都存储一个参数,通过设置这个数组来进行图像的修改</param>
/// <param name="bGrayScaleBuf">:灰度功率表.长度为256,默认数元值与下标一致,例如:     _grayTables[0] = (byte)0;     _grayTables[1] = (byte)1;     ......     _grayTables[255] = (byte)255;     如果想要呈现不同不同功率不同灰度效果,可以修改此数组,ezcad3中存在此功能,可在ezcad3中事先查看效果.之后用接口实现</param>
/// <param name="str1">:位图对象文件路径</param>
e3_SetBmpFileInfo_2 E3_SetBmpFileInfo_2 = nullptr;

/// <summary>
/// 接口说明:设置软件读取语言文件.只对设备参数窗体语言生效，默认为英文
/// <para>API编码:[66351540]</para>
/// <para>文档定位:环境-初始化以及释放</para>
/// </summary>
/// <param name="strFile">:语言包路径</param>
e3_SetLanguageFile E3_SetLanguageFile = nullptr;

/// <summary>
/// 接口说明:设置笔参数
/// <para>API编码:[55082481]</para>
/// <para>文档定位:数据-笔参数相关</para>
/// </summary>
/// <param name="idEM">:管理器ID</param>
/// <param name="nPenNo">:笔号</param>
/// <param name="pStrName">:笔名称</param>
/// <param name="clr">:笔颜色</param>
/// <param name="bDisableMark">:使能</param>
/// <param name="bUseDefParam">:使用默认</param>
/// <param name="nMarkLoop">:加工次数</param>
/// <param name="dMarkSpeed">:标刻速度mm/s</param>
/// <param name="dPowerRatio">:功率%</param>
/// <param name="dCurrent">:电流A</param>
/// <param name="dFreq">:频率HZ</param>
/// <param name="dQPulseWidth">:脉冲宽度us|ns</param>
/// <param name="nStartTC">:开始延时us</param>
/// <param name="nLaserOffTC">:关闭延时us</param>
/// <param name="nEndTC">:结束延时us</param>
/// <param name="nPolyTC">:拐角延时us</param>
/// <param name="dJumpSpeed">:跳转速度mm/s</param>
/// <param name="nMinJumpDelayTCUs">:最小跳转延时us</param>
/// <param name="nMaxJumpDelayTCUs">:最大跳转延时us</param>
/// <param name="dJumpLengthLimit">:跳转长度极限mm</param>
/// <param name="dPointTimeMs">:打点时间ms</param>
/// <param name="nSpiSpiContinueMode">:SPI连续模式</param>
/// <param name="nSpiWave">:SPI波形选择</param>
/// <param name="nYagMarkMode">:YAG优化填充模式</param>
/// <param name="bPulsePointMode">:脉冲点模式</param>
/// <param name="nPulseNum">:脉冲点数</param>
/// <param name="bEnableACCMode">:使能加速模式</param>
/// <param name="dEndComp">:末点补偿</param>
/// <param name="dAccDist">:加速距离mm</param>
/// <param name="dBreakAngle">:中断角度(89)（弧度值）;已经被淘汰，暂时保留</param>
/// <param name="bWobbleMode">:抖动模式(false);已经升级，目前版本不再使用这个参数</param>
/// <param name="bWobbleDiameter">:抖动直径(1)mm;已经升级，目前版本不再使用这个参数</param>
/// <param name="bWobbleDist">:抖动距离(0.5)mm;已经升级，目前版本不再使用这个参数</param>
e3_SetPenParam E3_SetPenParam = nullptr;

/// <summary>
/// 接口说明:设置优化模式参数
/// <para>API编码:[91206111]</para>
/// <para>文档定位:数据-笔参数相关</para>
/// </summary>
/// <param name="idEM">:管理器ID</param>
/// <param name="nPenNo">:笔号</param>
/// <param name="bOpitmize">:使能优化模式</param>
/// <param name="dScanberBiDirOffset">:双向偏移</param>
/// <param name="dAccDist">:加速距离</param>
/// <param name="dEndDist">:末点补偿</param>
e3_SetPenParamExt4 E3_SetPenParamExt4 = nullptr;

/// <summary>
/// 接口说明:设置笔参数数模块的焊接参数
/// <para>API编码:[79888088]</para>
/// <para>文档定位:数据-笔参数相关</para>
/// </summary>
/// <param name="idEM">:管理器ID</param>
/// <param name="nPenNo">:笔号</param>
/// <param name="nMarkLoop">:加工数目</param>
/// <param name="bAveragePtMode">:是否平均分布所有点（true为是）</param>
/// <param name="dPointDist">:点间距</param>
/// <param name="nPulseNum">:每点脉冲数</param>
e3_SetPenParamExt5 E3_SetPenParamExt5 = nullptr;

/// <summary>
/// 接口说明:设置激光扩展输出口索引
/// <para>API编码:[14208434]</para>
/// <para>文档定位:数据-笔参数相关</para>
/// </summary>
/// <param name="idEM">:管理器ID</param>
/// <param name="nPenNo">:笔号</param>
/// <param name="nLasetExtOutputIndex">:扩展输出口索引</param>
e3_SetPenParamExtOutputIndex E3_SetPenParamExtOutputIndex = nullptr;

/// <summary>
/// 接口说明:设置频率渐变参数
/// <para>API编码:[18689610]</para>
/// <para>文档定位:数据-笔参数相关</para>
/// </summary>
/// <param name="idEM">:管理器ID</param>
/// <param name="nPenNo">:笔号</param>
/// <param name="bAccSegEnable">:使能起始</param>
/// <param name="dAccSegStartRatio">:起始比例</param>
/// <param name="dAccSegLen">:起始长度;起始频率渐变的长度</param>
/// <param name="bDecSegEnable">:使能结束</param>
/// <param name="dDecSegStartRatio">:结束频率比例%;实际频率为当前加工参数频率乘此百分比</param>
/// <param name="dDecSegLen">:结束长度;结束频率渐变的长度</param>
e3_SetPenParamFreqRamp E3_SetPenParamFreqRamp = nullptr;

/// <summary>
/// 接口说明:设置指定笔号的激光滞后时间
/// <para>API编码:[39409173]</para>
/// <para>文档定位:数据-笔参数相关</para>
/// </summary>
/// <param name="idEM">:管理器ID</param>
/// <param name="nPenNo">:笔号</param>
/// <param name="bEnable">:是否使能激光滞后时间</param>
/// <param name="nTimeUs">:激光滞后时间us</param>
e3_SetPenParamLaserLagTime E3_SetPenParamLaserLagTime = nullptr;

/// <summary>
/// 接口说明:设置功率渐变参数
/// <para>API编码:[69830454]</para>
/// <para>文档定位:数据-笔参数相关</para>
/// </summary>
/// <param name="idEM">:管理器ID</param>
/// <param name="nPenNo">:笔号</param>
/// <param name="bAccSegEnable">:使能起始</param>
/// <param name="dAccSegStartRatio">:实际出光功率为当前加工参数功率乘此百分比</param>
/// <param name="dAccSegLen">:起始长度;起始功率渐变的长度</param>
/// <param name="bDecSegEnable">:使能结束</param>
/// <param name="dDecSegStartRatio">:结束功率比例%;实际出光功率为当前加工参数功率乘此百分比</param>
/// <param name="dDecSegLen">:结束长度;结束功率渐变的长度</param>
e3_SetPenParamPowerRamp E3_SetPenParamPowerRamp = nullptr;

/// <summary>
/// 接口说明:设置匀速笔标刻参数
/// <para>API编码:[42859443]</para>
/// <para>文档定位:数据-笔参数相关</para>
/// </summary>
/// <param name="idEM">:管理器ID</param>
/// <param name="nPenNo">:笔号</param>
/// <param name="bSkyWrite">:使能</param>
/// <param name="nSkyWriteMode">:匀速模式</param>
/// <param name="dSkyWriteLimitAngle">:极限角度</param>
/// <param name="nSkyWriteNprev">:导入周期.默认10us</param>
/// <param name="nSkyWriteNpost">:导出周期.默认10us</param>
/// <param name="dSkyWriteTimelag">:滞后时间us</param>
/// <param name="nSkyWriteLaserOnShift">:漂移时间us</param>
e3_SetPenParamSkyWriting E3_SetPenParamSkyWriting = nullptr;

/// <summary>
/// 接口说明:设置速度渐变参数
/// <para>API编码:[48941785]</para>
/// <para>文档定位:数据-笔参数相关</para>
/// </summary>
/// <param name="idEM">:管理器ID</param>
/// <param name="nPenNo">:笔号</param>
/// <param name="bAccSegEnable">:使能起始</param>
/// <param name="dAccSegStartRatio">:起始速度比例%;实际振镜摆动为当前加工参数速度乘此百分比</param>
/// <param name="dAccSegLen">:起始长度;起始速度渐变的长度</param>
/// <param name="bDecSegEnable">:使能结束</param>
/// <param name="dDecSegStartRatio">:结束比例%;实际振镜摆动速度为当前加工参数速度乘此百分比</param>
/// <param name="dDecSegLen">:结束长度;结束速度渐变的长度</param>
e3_SetPenParamSpeedRamp E3_SetPenParamSpeedRamp = nullptr;

/// <summary>
/// 接口说明:设置步距标刻参数
/// <para>API编码:[15439842]</para>
/// <para>文档定位:数据-笔参数相关</para>
/// </summary>
/// <param name="idEM">:管理器ID</param>
/// <param name="nPenNo">:笔号</param>
/// <param name="bEnableStepMode">:步距模式</param>
/// <param name="dMarkStep">:优化长度</param>
e3_SetPenParamStep E3_SetPenParamStep = nullptr;

/// <summary>
/// 接口说明:设置QCW波形输出
/// <para>API编码:[93238538]</para>
/// <para>文档定位:数据-笔参数相关</para>
/// </summary>
/// <param name="idEM">:管理器ID</param>
/// <param name="nPenNo">:笔号</param>
/// <param name="dWeldWavePower">:功率（每个功率[0,100]）</param>
/// <param name="dWeldWaveWidthMs">:脉宽（ms）(64个脉宽值的和不可超过笔参数中设置的总脉宽);[0,63]</param>
e3_SetPenParamWeldWave E3_SetPenParamWeldWave = nullptr;

/// <summary>
/// 接口说明:设置QCW波形输出,E3_SetPenParamWeldWave的参数扩展.
/// <para>API编码:[54255338]</para>
/// <para>文档定位:数据-笔参数相关</para>
/// </summary>
/// <param name="idEM">:管理器ID</param>
/// <param name="nPenNo">:笔号</param>
/// <param name="bLaserContMode">:是否使能连续模式（true为使能）</param>
/// <param name="bEnableWeldWave">:是否使能波形输出(true为使能)</param>
/// <param name="nMaxCount">:波形输出最大组数;[0,63]</param>
/// <param name="dWeldWavePower">:功率（每个功率[0,100]）</param>
/// <param name="dWeldWaveWidthMs">:脉宽（ms）(64个脉宽值的和不可超过笔参数中设置的总脉宽);[0,63]</param>
e3_SetPenParamWeldWave2 E3_SetPenParamWeldWave2 = nullptr;

/// <summary>
/// 接口说明:设置抖动参数
/// <para>API编码:[99975243]</para>
/// <para>文档定位:数据-笔参数相关</para>
/// </summary>
/// <param name="idEM">:管理器ID</param>
/// <param name="nPenNo">:笔号</param>
/// <param name="bWobbleMode">:使能抖动</param>
/// <param name="nWobbleType">:抖动类型(5种：分别为螺旋线，正弦曲线，椭圆，垂直8字，水平8字)</param>
/// <param name="dWobbleDiameter">:直径mm</param>
/// <param name="dWobbleDiameterB">:抖动直径2 (mm)</param>
/// <param name="dWobbleDist">:抖动距离 mm</param>
e3_SetPenParamWobble E3_SetPenParamWobble = nullptr;

/// <summary>
/// 接口说明:设置抖动的相对速度
/// <para>API编码:[01564414]</para>
/// <para>文档定位:数据-笔参数相关</para>
/// </summary>
/// <param name="idEM">:管理器ID</param>
/// <param name="nPenNo">:笔号</param>
/// <param name="dWobbleIncSpeed">:抖动的相对速度</param>
e3_SetPenParamWobbleIncSpeed E3_SetPenParamWobbleIncSpeed = nullptr;

/// <summary>
/// 接口说明:获取所有的字体数
/// <para>API编码:[12265534]</para>
/// <para>文档定位:环境-字库管理</para>
/// </summary>
/// <param name="nFontCount">:字体总数（包括TTF,JSF，条码……）</param>
e3_GetAllFontCount E3_GetAllFontCount = nullptr;

/// <summary>
/// 接口说明:获取在所有字体中指定位置的字体记录
/// <para>API编码:[17802958]</para>
/// <para>文档定位:环境-字库管理</para>
/// </summary>
/// <param name="id">:在字体总数中的字体位置</param>
/// <param name="strName">:字体名</param>
/// <param name="attrib">:字体属性，JSF(attrib&0x1001)!=0  TTF(attrib&0x02)!=0 点阵DMF(attrib&0x04)!=0  条码BCF(attrib&0x08)!=0 SHX(attrib&0x10)!=0</param>
e3_GetAllFontRecord E3_GetAllFontRecord = nullptr;

/// <summary>
/// 接口说明:根据层ID得到当前层的stl模型尺寸
/// <para>API编码:[71980031]</para>
/// <para>文档定位:数据-显示-3D显示</para>
/// </summary>
/// <param name="idLayer">:图层ID</param>
/// <param name="minx">:Stl模型的左下角X坐标</param>
/// <param name="miny">:Stl模型的左下角Y坐标</param>
/// <param name="maxx">:Stl模型的右上角X坐标</param>
/// <param name="maxy">:Stl模型的右上角Y坐标</param>
/// <param name="minz">:Stl模型的最小Z坐标</param>
/// <param name="maxz">:Stl模型的最大Z坐标</param>
e3_GetMeshSize E3_GetMeshSize = nullptr;

/// <summary>
/// 接口说明:是否开启振镜补偿，关闭时，振镜标刻和流水线移动无关
/// <para>API编码:[04546726]</para>
/// <para>文档定位:硬件-加工动作-列表命令-列表过程命令</para>
/// </summary>
/// <param name="idMarker">:板卡ID</param>
/// <param name="bEnableFlyX">:使能x</param>
/// <param name="bEnableFlyY">:使能y</param>
e3_MarkerEnableFlyCorrectionToList E3_MarkerEnableFlyCorrectionToList = nullptr;

/// <summary>
/// 接口说明:设置飞行模拟速度，无编码器时必须执行这个，F3中的是设置不能直接执行
/// <para>API编码:[40029126]</para>
/// <para>文档定位:硬件-组合动作-动作指令</para>
/// </summary>
/// <param name="idMarker">:板卡ID</param>
/// <param name="bEnableSimuFly">:是否使能模拟，直接修改了cfg参数</param>
/// <param name="dSpeedX">:模拟速度</param>
e3_MarkerSetFlySimuSpeed E3_MarkerSetFlySimuSpeed = nullptr;

/// <summary>
/// 接口说明:清除在标刻过程中接到的IO信号，在等待IO信号前设置，可避免误触发
/// <para>API编码:[73417617]</para>
/// <para>文档定位:硬件-组合动作-动作指令</para>
/// </summary>
/// <param name="idMarker">:板卡ID</param>
/// <param name="nPort">:端口值</param>
e3_MarkerClearWaitForInputLock E3_MarkerClearWaitForInputLock = nullptr;

/// <summary>
/// 接口说明:使能飞行，如果飞行标刻，需F3参数使能飞行，E3_MarkerListReady里设置飞行状态，并使能飞行
/// <para>API编码:[42475852]</para>
/// <para>文档定位:硬件-加工动作-列表命令-列表过程命令</para>
/// </summary>
/// <param name="idMarker">:板卡ID</param>
/// <param name="b">:使能</param>
e3_MarkerFlyEnableToList E3_MarkerFlyEnableToList = nullptr;

/// <summary>
/// 接口说明:清除流水线（飞行）补偿，清除前必须用E3_MarkerFlyEnableToList关闭飞行，不然有可能清除失败
/// <para>API编码:[07723568]</para>
/// <para>文档定位:硬件-组合动作-列表命令-列表过程命令</para>
/// </summary>
/// <param name="idMarker">:板卡ID</param>
e3_MarkerFlyResetDistanceToList E3_MarkerFlyResetDistanceToList = nullptr;

/// <summary>
/// 接口说明:飞行等待距离
/// <para>API编码:[17984852]</para>
/// <para>文档定位:硬件-组合动作-列表命令-列表过程命令</para>
/// </summary>
/// <param name="idMarker">:板卡ID</param>
/// <param name="dFlyDist">:等距的距离，与飞行补偿对应</param>
/// <param name="bIsFollowAvail">:在等待过程中振镜是否跟随流水线移动</param>
e3_MarkerFlyWaitForDistToList E3_MarkerFlyWaitForDistToList = nullptr;

/// <summary>
/// 接口说明:获取编码器脉冲数
/// <para>API编码:[51684669]</para>
/// <para>文档定位:硬件-组合动作-动作指令</para>
/// </summary>
/// <param name="idMarker">:板卡ID</param>
/// <param name="index">:编码器，1为X,2为Y</param>
/// <param name="nCount">:返回的编码器脉冲数</param>
e3_MarkerGetFlyEncoder E3_MarkerGetFlyEncoder = nullptr;

/// <summary>
/// 接口说明:获取流水线速度
/// <para>API编码:[88602152]</para>
/// <para>文档定位:硬件-组合动作-动作指令</para>
/// </summary>
/// <param name="idMarker">:板卡ID</param>
/// <param name="index">:编码器，1为X,2为Y</param>
/// <param name="dSpeed">:速度</param>
e3_MarkerGetSpeedOfFly E3_MarkerGetSpeedOfFly = nullptr;

/// <summary>
/// 接口说明:获取当前输出口的状态值
/// <para>API编码:[08667501]</para>
/// <para>文档定位:硬件-资源-数字量OUT-查询</para>
/// </summary>
/// <param name="idMarker">:板卡ID</param>
/// <param name="data">:输出口的值</param>
e3_MarkerGetWritePort E3_MarkerGetWritePort = nullptr;

/// <summary>
/// 接口说明:清除振镜补偿，在清除前需要用E3_MarkerEnableFlyCorrectionToList关闭使能
/// <para>API编码:[69969995]</para>
/// <para>文档定位:硬件-资源-数字量OUT-查询</para>
/// </summary>
/// <param name="idMarker">:板卡ID</param>
/// <param name="bResetX">:使能x方向清除</param>
/// <param name="bResetY">:使能y方向清除</param>
e3_MarkerResetDistanceToList E3_MarkerResetDistanceToList = nullptr;

/// <summary>
/// 接口说明:设置输出口，掩码模式. 当mask参数的bit为1时,则设置这个bit的端口被打开,默认是低电平输出. 当data参数的bit为1时,则设置对应的端口以高电平模式输出,其余不为1的bit,则默认低电平输出.
/// <para>API编码:[90771974]</para>
/// <para>文档定位:硬件-资源-数字量OUT-动作</para>
/// </summary>
/// <param name="idMarker">:板卡ID</param>
/// <param name="wPortMask">:输出口掩码</param>
/// <param name="wPortLevel">:设置的输出口值</param>
e3_MarkerSetOutputPortWithMask E3_MarkerSetOutputPortWithMask = nullptr;

/// <summary>
/// 接口说明:设置输出口，只有掩码上的设置有效，list命令
/// <para>API编码:[05422563]</para>
/// <para>文档定位:硬件-资源-数字量OUT-动作</para>
/// </summary>
/// <param name="idMarker">:板卡ID</param>
/// <param name="wPortMask">:端口掩码:1有效,0无效;</param>
/// <param name="wPortLevel">:目标值:1高,0低;</param>
e3_MarkerSetOutputPortWithMaskToList E3_MarkerSetOutputPortWithMaskToList = nullptr;

/// <summary>
/// 接口说明:设置系统对于输入口的处理模式,是否是脉冲模式,是否是高低电平有效,通过此接口设定.支持动态设置,但不支持运行中设置(运行中代表开启了列表或调用了Markent2)
/// <para>API编码:[55675362]</para>
/// <para>文档定位:硬件-资源-数字量IN-配置</para>
/// </summary>
/// <param name="idMarker">:板卡ID</param>
/// <param name="bPulseMode">:是否是脉冲信号</param>
/// <param name="bLowVaild">:脉冲模式，true下降沿，false上升沿。电平模式，true低电平，false高电平</param>
e3_SetInputPortWorkMode E3_SetInputPortWorkMode = nullptr;

/// <summary>
/// 接口说明:把文本对象分离成字符对象,添加到idEntParent容器对象的尾部. 一般的idEntParent为图层ID,但是也可以传入对象ID,但对象ID必须为群组对象,如果是群组对象会将分离后的文本对象添加到群组对象子对象的尾部.
/// <para>API编码:[97652297]</para>
/// <para>文档定位:数据-标准图元-编辑-文本类型-文本</para>
/// </summary>
/// <param name="idEnt">:对象ID</param>
/// <param name="idEntParent">:分离对象添加到的父对象ID</param>
/// <param name="bTextLeftToRight">:分离字符的方式，false从右到左，true从左到右</param>
/// <param name="dArcTol">:曲线离散成直线的误差</param>
e3_SplitTextToChars E3_SplitTextToChars = nullptr;

/// <summary>
/// 接口说明:读取license信息
/// <para>API编码:[49432465]</para>
/// <para>文档定位:环境-激活码</para>
/// </summary>
/// <param name="BYTEInfo[10240]">:</param>
e3_BitGetInfo E3_BitGetInfo = nullptr;

/// <summary>
/// 接口说明:将对象转为曲线
/// <para>API编码:[94893641]</para>
/// <para>文档定位:数据-对象操作-对象间操作</para>
/// </summary>
/// <param name="idEnt">:对象ID</param>
/// <param name="nParamFlag">:默认0</param>
/// <param name="bDeleteOldEnt">:是否删除旧曲线</param>
/// <param name="idNewCurveEnt">:转换后的曲线组</param>
e3_ChangeEntToCurve E3_ChangeEntToCurve = nullptr;

/// <summary>
/// 接口说明:获取指定文本对象的字体类型，以及是否是条码
/// <para>API编码:[30609132]</para>
/// <para>文档定位:数据-标准图元-编辑-文本类型-条码</para>
/// </summary>
/// <param name="idEnt">:对象ID</param>
/// <param name="strFontName[256]">:字体名</param>
/// <param name="bIsbarcode">:是否有效</param>
e3_GetTextFontName E3_GetTextFontName = nullptr;

/// <summary>
/// 接口说明:群组对象
/// <para>API编码:[40121504]</para>
/// <para>文档定位:数据-对象操作-对象间操作</para>
/// </summary>
/// <param name="idEnts">:被群组的对象ID</param>
/// <param name="nEntCount">:群组的数目</param>
/// <param name="idEntGroup">:群组对象ID</param>
e3_GroupEnt E3_GroupEnt = nullptr;

/// <summary>
/// 接口说明:解散群组
/// <para>API编码:[63259186]</para>
/// <para>文档定位:数据-对象操作-对象间操作</para>
/// </summary>
/// <param name="idEntGroup">:群组对象ID</param>
e3_UnGroupEnt E3_UnGroupEnt = nullptr;

/// <summary>
/// 接口说明:解散群组
/// <para>API编码:[67084108]</para>
/// <para>文档定位:数据-对象操作-对象间操作</para>
/// </summary>
/// <param name="idEntGroup">:群组对象ID</param>
/// <param name="nFlag">:0x1，禁止通过笔号解散子对象</param>
e3_UnGroupEnt2 E3_UnGroupEnt2 = nullptr;

/// <summary>
/// 接口说明:在指定窗口绘制数据库中对象的预览图
/// <para>API编码:[03226969]</para>
/// <para>文档定位:数据-显示-2D显示</para>
/// </summary>
/// <param name="hDC">:绘图相关联的句柄</param>
/// <param name="idEnt">:要显示的层ID或对象ID</param>
/// <param name="nParam">:默认为0</param>
/// <param name="bmpwidth">:窗口的像素宽</param>
/// <param name="bmpheight">:窗口的像素高</param>
/// <param name="dLogOriginX">:窗口的左下角对应点的x向逻辑坐标</param>
/// <param name="dLogOriginY">:窗口的左下角对应点的y向逻辑坐标</param>
/// <param name="dLogScale">:窗口对应的逻辑尺寸与窗口像素尺寸的比例</param>
e3_DrawEnt2 E3_DrawEnt2 = nullptr;

/// <summary>
/// 接口说明:在指定窗口绘制数据库中对象的预览图，并添加背景图
/// <para>API编码:[11767624]</para>
/// <para>文档定位:数据-显示-2D显示</para>
/// </summary>
/// <param name="hDC">:绘图相关联的句柄</param>
/// <param name="idEnt">:要显示的层ID或对象ID</param>
/// <param name="nParam">:默认为0</param>
/// <param name="bmpwidth">:窗口的像素宽</param>
/// <param name="bmpheight">:窗口的像素高</param>
/// <param name="dLogOriginX">:窗口的左下角对应点的x向逻辑坐标</param>
/// <param name="dLogOriginY">:窗口的左下角对应点的y向逻辑坐标</param>
/// <param name="dLogScale">:窗口对应的逻辑尺寸与窗口像素尺寸的比例</param>
/// <param name="pBackBmpParam">:背景图的图像参数</param>
e3_DrawEnt3 E3_DrawEnt3 = nullptr;

/// <summary>
/// 接口说明:获取数据库中对象的预览图的HBITMAP
/// <para>API编码:[52841796]</para>
/// <para>文档定位:数据-显示-2D显示</para>
/// </summary>
/// <param name="strEzdFileName">:预览文档的路径</param>
e3_GetEzdFilePrevBitmap E3_GetEzdFilePrevBitmap = nullptr;

/// <summary>
/// 接口说明:比对序号为nCounterIndex的计数器的当前值与nCompareValue的大小，当nCounterIndex对应的计数器（0-255）的值大于nCompareValue则跳转到索引序号为nListIndex所在行，否则按顺序执行下一条命令。
/// <para>API编码:[44348519]</para>
/// <para>文档定位:硬件-加工动作-列表命令-列表过程命令</para>
/// </summary>
/// <param name="idMarker">:接口使用的板卡ID</param>
/// <param name="nCounterIndex">:计数器的序号</param>
/// <param name="nCompareValue">:比对的数值</param>
/// <param name="nListIndex">:跳转到的索引序号</param>
/// <param name="CompareCond">:</param>
e3_MarkerConditionJumpToIndexToList E3_MarkerConditionJumpToIndexToList = nullptr;

/// <summary>
/// 接口说明:查询飞行视觉应用中相机触发拍照定位的次数和加工次数
/// <para>API编码:[89133678]</para>
/// <para>文档定位:硬件-资源-寄存器-读</para>
/// </summary>
/// <param name="idMarker">:接口使用的板卡ID</param>
/// <param name="CameraObjectCount">:相机触发拍照定位次数</param>
/// <param name="MarkObjectCount">:加工次数</param>
e3_MarkerGetFlyCameraObjectCount E3_MarkerGetFlyCameraObjectCount = nullptr;

/// <summary>
/// 接口说明:在列表中插入一个索引序号，跳转指令通过索引序号引导跳转到当前行。
/// <para>API编码:[81708651]</para>
/// <para>文档定位:硬件-资源-寄存器-写</para>
/// </summary>
/// <param name="idMarker">:接口使用的板卡ID</param>
/// <param name="nIndex">:索引序号值</param>
e3_MarkerSetIndexToList E3_MarkerSetIndexToList = nullptr;

/// <summary>
/// 接口说明:设置文档加工时的矩阵，通过3x3矩阵支持设置平移，旋转，缩放，错切。
/// <para>API编码:[80557629]</para>
/// <para>文档定位:硬件-加工动作-列表命令-变换</para>
/// </summary>
/// <param name="idMarker">:接口使用的板卡ID</param>
/// <param name="dMatrix">:3x3变换矩阵</param>
e3_MarkerSetTransformMatrix E3_MarkerSetTransformMatrix = nullptr;

/// <summary>
/// 接口说明:设置文档加工时的移动旋转量，不对文档进行修改，先以（dCenterX,?dCenterY）为旋转中心，旋转dRotateAng（弧度），再分别沿X向和Y向平移dMoveX，?dMoveY。
/// <para>API编码:[86915055]</para>
/// <para>文档定位:硬件-组合动作-列表命令-变换</para>
/// </summary>
/// <param name="idMarker">:接口使用的板卡ID</param>
/// <param name="dMoveX">:沿X方向的平移距离</param>
/// <param name="dMoveY">:沿Y方向的平移距离</param>
/// <param name="dCenterX">:旋转中心的X坐标值</param>
/// <param name="dCenterY">:旋转中心的Y坐标值</param>
/// <param name="dRotateAng">:旋转弧度值</param>
e3_MarkerSetTransformMatrix2 E3_MarkerSetTransformMatrix2 = nullptr;

/// <summary>
/// 接口说明:将3x3矩阵按序号写入板卡相应的寄存器中，以备后续使用，最多支持32个寄存器。
/// <para>API编码:[10908885]</para>
/// <para>文档定位:硬件-加工动作-列表命令-变换</para>
/// </summary>
/// <param name="idMarker">:接口使用的板卡ID</param>
/// <param name="n">:写入寄存器的序号（0-31）</param>
/// <param name="mtx">:3x3变换矩阵</param>
e3_MarkerSetTransformMatrixByIndex E3_MarkerSetTransformMatrixByIndex = nullptr;

/// <summary>
/// 接口说明:加载ez3文件到数据库中
/// <para>API编码:[94646535]</para>
/// <para>文档定位:数据-文件读写</para>
/// </summary>
/// <param name="pStrFileName">:ez3文件的路径</param>
/// <param name="idEM">:要放在的资源管理器ID</param>
/// <param name="bAddMode">:是否为增加模式（不清空当前数据库）</param>
/// <param name="bUndo">:当前操作是否加入到撤销，重做功能</param>
e3_OpenFileToEntMgr E3_OpenFileToEntMgr = nullptr;

/// <summary>
/// 接口说明:加载ez3文件到数据库中
/// <para>API编码:[02376573]</para>
/// <para>文档定位:数据-文件读写</para>
/// </summary>
/// <param name="pStrFileName">:ez3文件的路径</param>
/// <param name="idEM">:要放在的资源管理器ID</param>
/// <param name="bAddMode">:是否为增加模式（不清空当前数据库）</param>
/// <param name="bUndo">:当前操作是否加入到撤销，重做功能</param>
/// <param name="bShowProgressDlg">:是否显示加载文件进度条窗口</param>
e3_OpenFileToEntMgr2 E3_OpenFileToEntMgr2 = nullptr;

/// <summary>
/// 接口说明:设置扩展轴的参数
/// <para>API编码:[47824490]</para>
/// <para>文档定位:硬件-资源-运动轴-配置</para>
/// </summary>
/// <param name="idMarker">:控制卡ID</param>
/// <param name="axis">:操作的轴序号</param>
/// <param name="bEnable">:是否使能扩展轴</param>
/// <param name="bInvert">:是否反转</param>
/// <param name="bOutNeg">:是否共阴极输出</param>
/// <param name="bRotaryAxis">:是否为旋转轴</param>
/// <param name="dDistPerRound">:转一圈的距离</param>
/// <param name="dPulsePerRound">:每转脉冲数</param>
/// <param name="dMinVel">:最小速度</param>
/// <param name="dMaxVel">:最大速度</param>
/// <param name="dAcceleration">:加速度</param>
/// <param name="dDeceleration">:减速度</param>
/// <param name="dBacklash">:反向间隙</param>
/// <param name="bEnFeedback">:是否使能编码器</param>
/// <param name="dPosErrFollow">:跟随误差</param>
/// <param name="bSAcc">:使能s曲线</param>
/// <param name="dJerk">:加速程度</param>
/// <param name="bEnableSoftLimit">:是否使能软限位</param>
/// <param name="dMinSoftLimit">:软限位最小坐标</param>
/// <param name="dMaxSoftLimit">:软限位最大坐标</param>
/// <param name="bEnableHome">:是否使能零点</param>
/// <param name="bHomeLowValid">:零点是否低电平有效</param>
/// <param name="bHomeDirPos">:是否正向回零</param>
/// <param name="bHomeFindIndex">:回零时是否寻找索引</param>
/// <param name="dHomePos">:零点的坐标</param>
/// <param name="dHomingFindVel">:找零点速度</param>
/// <param name="dHomingLeaveVel">:离开零点速度</param>
/// <param name="bHomeFinishGotoPos">:是否使能回零结束去指定位置</param>
/// <param name="dHomeFinishGotoPos">:回零结束的指定位置</param>
/// <param name="bEnableLimit">:是否使能限位</param>
/// <param name="bLimitLowValid">:限位是否低电平有效</param>
/// <param name="bMarkFinishGotoStartPoint">:加工完是否回到起始位置</param>
/// <param name="bEnableAccurateHome">:是否使能精确回零</param>
e3_SetAxisParam2 E3_SetAxisParam2 = nullptr;

/// <summary>
/// 接口说明:设置扩展轴的参数
/// <para>API编码:[22425743]</para>
/// <para>文档定位:硬件-资源-运动轴-配置</para>
/// </summary>
/// <param name="idMarker">:控制卡ID</param>
/// <param name="axis">:操作的轴序号</param>
/// <param name="bEnable">:是否使能扩展轴</param>
/// <param name="bInvert">:是否反转</param>
/// <param name="bOutNeg">:是否共阴极输出</param>
/// <param name="bRotaryAxis">:是否为旋转轴</param>
/// <param name="dDistPerRound">:转一圈的距离</param>
/// <param name="dPulsePerRound">:每转脉冲数</param>
/// <param name="dMinVel">:最小速度</param>
/// <param name="dMaxVel">:最大速度</param>
/// <param name="dAcceleration">:加速度</param>
/// <param name="dDeceleration">:减速度</param>
/// <param name="dBacklash">:反向间隙</param>
/// <param name="bEnFeedback">:是否使能编码器</param>
/// <param name="dPosErrFollow">:跟随误差</param>
/// <param name="bSAcc">:使能s曲线</param>
/// <param name="dJerk">:加速程度</param>
/// <param name="bEnableSoftLimit">:是否使能软限位</param>
/// <param name="dMinSoftLimit">:软限位最小坐标</param>
/// <param name="dMaxSoftLimit">:软限位最大坐标</param>
/// <param name="bEnableHome">:是否使能零点</param>
/// <param name="bHomeLowValid">:零点是否低电平有效</param>
/// <param name="bHomeDirPos">:是否正向回零</param>
/// <param name="bHomeFindIndex">:回零时是否寻找索引</param>
/// <param name="dHomePos">:零点的坐标</param>
/// <param name="dHomingFindVel">:找零点速度</param>
/// <param name="dHomingLeaveVel">:离开零点速度</param>
/// <param name="bHomeFinishGotoPos">:是否使能回零结束去指定位置</param>
/// <param name="dHomeFinishGotoPos">:回零结束的指定位置</param>
/// <param name="bEnableLimit">:是否使能限位</param>
/// <param name="bLimitLowValid">:限位是否低电平有效</param>
/// <param name="bMarkFinishGotoStartPoint">:加工完是否回到起始位置</param>
e3_SetAxisParam E3_SetAxisParam = nullptr;

/// <summary>
/// 接口说明:设置轴点位运动参数
/// <para>API编码:[04827805]</para>
/// <para>文档定位:硬件-资源-运动轴-配置</para>
/// </summary>
/// <param name="idMarker">:接口使用的板卡ID</param>
/// <param name="axis">:操作的轴序号</param>
/// <param name="dStartSpeed">:起始速度</param>
/// <param name="dMaxSpeed">:最大速度</param>
/// <param name="dAccSpeed">:加速度</param>
e3_SetAxisSpeedParam E3_SetAxisSpeedParam = nullptr;

/// <summary>
/// 接口说明:当前轴回零
/// <para>API编码:[93293524]</para>
/// <para>文档定位:硬件-资源-运动轴-动作</para>
/// </summary>
/// <param name="idMarker">:接口使用的板卡ID</param>
/// <param name="axis">:操作的轴序号</param>
/// <param name="bWaitForMoveFinish">:是否等待动作完成</param>
e3_AxisHome E3_AxisHome = nullptr;

/// <summary>
/// 接口说明:当前轴回零
/// <para>API编码:[67106153]</para>
/// <para>文档定位:硬件-资源-运动轴-动作</para>
/// </summary>
/// <param name="idMarker">:接口使用的板卡ID</param>
/// <param name="axis">:操作的轴序号</param>
/// <param name="bWaitForMoveFinish">:是否等待动作完成</param>
/// <param name="bSHowWnd">:是否显示回零窗口</param>
e3_AxisHome2 E3_AxisHome2 = nullptr;

/// <summary>
/// 接口说明:轴移动到指定坐标位置
/// <para>API编码:[47882942]</para>
/// <para>文档定位:硬件-资源-运动轴-动作</para>
/// </summary>
/// <param name="idMarker">:接口使用的板卡ID</param>
/// <param name="axis">:操作的轴序号</param>
/// <param name="dGoalCoor">:目标坐标位置</param>
/// <param name="bWaitForMoveFinish">:是否等待动作完成</param>
e3_AxisMoveTo E3_AxisMoveTo = nullptr;

/// <summary>
/// 接口说明:设置是否回零正常
/// <para>API编码:[10495038]</para>
/// <para>文档定位:硬件-资源-运动轴-配置</para>
/// </summary>
/// <param name="idMarker">:接口使用的板卡ID</param>
/// <param name="axis">:操作的轴序号</param>
/// <param name="bIsAlreadyFindHome">:是否已经正常回零</param>
e3_AxisSetFlag E3_AxisSetFlag = nullptr;

/// <summary>
/// 接口说明:中断当前轴运动
/// <para>API编码:[95469915]</para>
/// <para>文档定位:硬件-资源-运动轴-动作</para>
/// </summary>
/// <param name="idMarker">:接口使用的板卡ID</param>
/// <param name="axis">:操作的轴序号</param>
e3_AxisStopMoving E3_AxisStopMoving = nullptr;

/// <summary>
/// 接口说明:获取轴的当前坐标
/// <para>API编码:[76937869]</para>
/// <para>文档定位:硬件-资源-运动轴-查询</para>
/// </summary>
/// <param name="idMarker">:接口使用的板卡ID</param>
/// <param name="axis">:操作的轴序号</param>
/// <param name="dCoor">:轴坐标值</param>
e3_GetAxisCoor E3_GetAxisCoor = nullptr;

/// <summary>
/// 接口说明:获取轴的当前编码器坐标
/// <para>API编码:[83820310]</para>
/// <para>文档定位:硬件-资源-编码器-查询</para>
/// </summary>
/// <param name="idMarker">:接口使用的板卡ID</param>
/// <param name="axis">:操作的轴序号</param>
/// <param name="dCoor">:编码器坐标值</param>
e3_GetAxisFBCoor E3_GetAxisFBCoor = nullptr;

/// <summary>
/// 接口说明:获取轴的运动参数
/// <para>API编码:[41492024]</para>
/// <para>文档定位:硬件-资源-运动轴-查询</para>
/// </summary>
/// <param name="idMarker">:控制卡ID</param>
/// <param name="axis">:操作的轴序号</param>
/// <param name="bEnable">:是否使能扩展轴</param>
/// <param name="bInvert">:是否反转</param>
/// <param name="bOutNeg">:是否共阴极输出</param>
/// <param name="bRotaryAxis">:是否为旋转轴</param>
/// <param name="dDistPerRound">:转一圈的距离</param>
/// <param name="dPulsePerRound">:每转脉冲数</param>
/// <param name="dMinVel">:最小速度</param>
/// <param name="dMaxVel">:最大速度</param>
/// <param name="dAcceleration">:加速度</param>
/// <param name="dDeceleration">:减速度</param>
/// <param name="dBacklash">:反向间隙</param>
/// <param name="bEnFeedback">:是否使能编码器</param>
/// <param name="dPosErrFollow">:跟随误差</param>
/// <param name="bSAcc">:使能s曲线</param>
/// <param name="dJerk">:加速程度</param>
/// <param name="bEnableSoftLimit">:是否使能软限位</param>
/// <param name="dMinSoftLimit">:软限位最小坐标</param>
/// <param name="dMaxSoftLimit">:软限位最大坐标</param>
/// <param name="bEnableHome">:是否使能零点</param>
/// <param name="&bHomeLowValid">:零点是否低电平有效</param>
/// <param name="bHomeDirPos">:是否正向回零</param>
/// <param name="bHomeFindIndex">:回零时是否寻找索引</param>
/// <param name="dHomePos">:零点的坐标</param>
/// <param name="dHomingFindVel">:找零点速度</param>
/// <param name="dHomingLeaveVel">:离开零点速度</param>
/// <param name="bHomeFinishGotoPos">:是否使能回零结束去指定位置</param>
/// <param name="&dHomeFinishGotoPos">:回零结束的指定位置</param>
/// <param name="&bEnableLimit">:是否使能限位</param>
/// <param name="bLimitLowValid">:限位是否低电平有效</param>
/// <param name="bMarkFinishGotoStartPoint">:加工完是否回到起始位置</param>
e3_GetAxisParam E3_GetAxisParam = nullptr;

/// <summary>
/// 接口说明:获取轴当前状态
/// <para>API编码:[29335272]</para>
/// <para>文档定位:硬件-资源-运动轴-查询</para>
/// </summary>
/// <param name="idMarker">:接口使用的板卡ID</param>
/// <param name="axis">:操作的轴序号</param>
/// <param name="wStatus">:bit状态值: Bit0:  = 1 轴运动;  = 0 轴停止; Bit1:  = 1 左限位高电平;  = 0 左限位低电平; Bit2:  = 1 右限位高电平;  = 0 右限位低电平; Bit3:  = 1 原点高电平;  = 0 原点低电平;</param>
e3_GetAxisStatus E3_GetAxisStatus = nullptr;

/// <summary>
/// 接口说明:初始化所有轴
/// <para>API编码:[65751693]</para>
/// <para>文档定位:硬件-资源-运动轴-配置</para>
/// </summary>
/// <param name="idMarker">:接口使用的板卡ID</param>
e3_InitAllAxis E3_InitAllAxis = nullptr;

/// <summary>
/// 接口说明:设置cfg文件的参数
/// <para>API编码:[34345432]</para>
/// <para>文档定位:环境-控制卡-配置</para>
/// </summary>
/// <param name="idMarker">:接口使用的板卡ID</param>
/// <param name="strFile">:cfg文件的位置</param>
/// <param name="nIntParamCount">:int类型参数的数量</param>
/// <param name="nParamBuf">:int类型参数的数组</param>
/// <param name="nDoubleParamCount">:double类型参数的数量</param>
/// <param name="dParamBuf">:double类型参数的数组</param>
e3_SetCfgFileParam E3_SetCfgFileParam = nullptr;

/// <summary>
/// 接口说明:设置对象的填充参数
/// <para>API编码:[74736044]</para>
/// <para>文档定位:数据-填充相关</para>
/// </summary>
/// <param name="idEM">:目标所在的资源管理器ID</param>
/// <param name="idEnt">:填充的对象ID</param>
/// <param name="bEnableContour">:是否使能轮廓</param>
/// <param name="bContourFirst">:是否使能轮廓优先</param>
/// <param name="param1">:填充参数1</param>
/// <param name="param2">:填充参数2</param>
/// <param name="param3">:填充参数3</param>
/// <param name="bUndo">:是否加入到撤销，重做</param>
/// <param name="strUndo">:撤销，重做字符串</param>
e3_SetEntHatchParam E3_SetEntHatchParam = nullptr;

/// <summary>
/// 接口说明:飞行等待相机位置到位
/// <para>API编码:[32057454]</para>
/// <para>文档定位:硬件-组合动作-列表命令-列表过程命令</para>
/// </summary>
/// <param name="idMarker">:接口使用的板卡ID</param>
/// <param name="dFlyDistance">:相机与振镜之间的固定间距</param>
/// <param name="bIsFollowAvail">:在飞行等待的过程中振镜位置是否随流水线一起保持运动</param>
e3_FlyWaitCameraPositioningToList E3_FlyWaitCameraPositioningToList = nullptr;

/// <summary>
/// 接口说明:按照序号递增规则，加工时自动选择矩阵变换（0-31进行循环）
/// <para>API编码:[89202892]</para>
/// <para>文档定位:硬件-组合动作-列表命令-变换</para>
/// </summary>
/// <param name="idMarker">:接口使用的板卡ID</param>
/// <param name="ExceptionFlag">:0x1 当前变换无效时，对象直接加工，不进行旋转   0x2 当前变换无效时，对象不加工，振镜正常摆，不出光</param>
e3_MarkerAutoSelectListMatirxToList2 E3_MarkerAutoSelectListMatirxToList2 = nullptr;

/// <summary>
/// 接口说明:按序号选择矩阵变换并设置使能
/// <para>API编码:[99119811]</para>
/// <para>文档定位:硬件-组合动作-列表命令-变换</para>
/// </summary>
/// <param name="idMarker">:接口使用的板卡ID</param>
/// <param name="n">:变换矩阵的序号</param>
/// <param name="bEnable">:是否使能变换</param>
e3_MarkerSelectTransMatirxToList E3_MarkerSelectTransMatirxToList = nullptr;

/// <summary>
/// 接口说明:按序号选择矩阵变换并设置使能
/// <para>API编码:[76891828]</para>
/// <para>文档定位:硬件-组合动作-列表命令-变换</para>
/// </summary>
/// <param name="idMarker">:接口使用的板卡ID</param>
/// <param name="n">:变换矩阵的序号</param>
/// <param name="bEnable">:是否使能变换</param>
/// <param name="ExceptionFlag">:0x1 当前变换无效时，对象直接加工，不进行旋转   0x2 当前变换无效时，对象不加工，振镜正常摆，不出光</param>
e3_MarkerSelectTransMatirxToList2 E3_MarkerSelectTransMatirxToList2 = nullptr;

/// <summary>
/// 接口说明:设置加工时所有对象的先绕旋转中心旋转指定角度，然后平移指定距离。不改变原文档。
/// <para>API编码:[52189106]</para>
/// <para>文档定位:环境-控制卡-配置</para>
/// </summary>
/// <param name="idMarker">:接口使用的板卡ID</param>
/// <param name="dMoveX">:沿X方向的平移距离</param>
/// <param name="dMoveY">:沿Y方向的平移距离</param>
/// <param name="dCenterX">:旋转中心的X坐标值</param>
/// <param name="dCenterY">:旋转中心的Y坐标值</param>
/// <param name="dRotateAng">:旋转弧度值</param>
e3_MarkerSetRotateMoveParam E3_MarkerSetRotateMoveParam = nullptr;

/// <summary>
/// 接口说明:将移动，旋转变换按序号写入板卡相应的寄存器中，以备后续使用，最多支持32个寄存器。
/// <para>API编码:[07127413]</para>
/// <para>文档定位:硬件-组合动作-列表命令-变换</para>
/// </summary>
/// <param name="idMarker">:接口使用的板卡ID</param>
/// <param name="n">:写入寄存器的序号（0-31）</param>
/// <param name="dMoveX">:沿X方向的平移距离</param>
/// <param name="dMoveY">:沿Y方向的平移距离</param>
/// <param name="dCenterX">:旋转中心的X坐标值</param>
/// <param name="dCenterY">:旋转中心的Y坐标值</param>
/// <param name="dRotateAng">:旋转弧度值</param>
e3_MarkerSetTransformMatrixByIndex2 E3_MarkerSetTransformMatrixByIndex2 = nullptr;

/// <summary>
/// 接口说明:将移动，旋转变换按序号写入板卡相应的寄存器中，以备后续使用，最多支持32个寄存器。
/// <para>API编码:[44335471]</para>
/// <para>文档定位:硬件-组合动作-列表命令-变换</para>
/// </summary>
/// <param name="idMarker">:接口使用的板卡ID</param>
/// <param name="n">:写入寄存器的序号（0-31）</param>
/// <param name="dMoveX">:沿X方向的平移距离</param>
/// <param name="dMoveY">:沿Y方向的平移距离</param>
/// <param name="dCenterX">:旋转中心的X坐标值</param>
/// <param name="dCenterY">:旋转中心的Y坐标值</param>
/// <param name="dRotateAng">:旋转弧度值</param>
/// <param name="Avail">:0x1当前变换有效  0x0当前变换无效</param>
e3_MarkerSetTransformMatrixByIndex3 E3_MarkerSetTransformMatrixByIndex3 = nullptr;

/// <summary>
/// 接口说明:拉伸对象
/// <para>API编码:[67014622]</para>
/// <para>文档定位:数据-对象操作-对象通用读写</para>
/// </summary>
/// <param name="idEnt">:拉伸对象ID</param>
/// <param name="dCenx">:拉伸中心X坐标</param>
/// <param name="dCeny">:拉伸中心Y坐标</param>
/// <param name="dScaleX">:X方向拉伸比例</param>
/// <param name="dScaleY">:Y方向拉伸比例</param>
e3_ScaleEnt E3_ScaleEnt = nullptr;

/// <summary>
/// 接口说明:设置板卡主循环IO检测流程
/// <para>API编码:[41055991]</para>
/// <para>文档定位:硬件-加工动作-动作指令</para>
/// </summary>
/// <param name="idMarker">:控制卡ID</param>
/// <param name="PortMask">:要检查端口的端口掩膜</param>
/// <param name="PortValue">:满足条件的端口比较值</param>
/// <param name="bEnable">:0x1 启动主循环IO检测流程 0x0  关闭主循环IO检测流程</param>
/// <param name="dIOAvailTime">:输入口电平有效时间(ms)</param>
e3_StartMainLoopIOCheckProcess E3_StartMainLoopIOCheckProcess = nullptr;

/// <summary>
/// 接口说明:使用设置F3参数接口后，更新F3参数.
/// <para>API编码:[14090013]</para>
/// <para>文档定位:硬件-资源-激光-配置</para>
/// </summary>
/// <param name="idMarker">:板卡ID; </param>
/// <param name="bSaveCfg">:是否保存文件至cfg文件. True=是;</param>
e3_MarkerUpdateParam E3_MarkerUpdateParam = nullptr;

/// <summary>
/// 接口说明:得到对象信息
/// <para>API编码:[25432468]</para>
/// <para>文档定位:数据-对象操作-对象通用读写</para>
/// </summary>
/// <param name="idEnt">:对象ID</param>
/// <param name="nFlag">:属性页,对象属性超过本接口所能承载的数量后,可以输入分页参数</param>
/// <param name="np1">:int类型属性信息1</param>
/// <param name="np2">:int类型属性信息2</param>
/// <param name="np3">:int类型属性信息3</param>
/// <param name="np4">:int类型属性信息4</param>
/// <param name="np5">:int类型属性信息5</param>
/// <param name="np6">:int类型属性信息6</param>
/// <param name="dp1">:double类型属性信息1</param>
/// <param name="dp2">:double类型属性信息2</param>
/// <param name="dp3">:double类型属性信息3</param>
/// <param name="dp4">:double类型属性信息4</param>
/// <param name="dp5">:double类型属性信息5</param>
/// <param name="dp6">:double类型属性信息6</param>
/// <param name="str1[256]">:字符型信息</param>
/// <param name="pParam1">:Byte形数组</param>
e3_GetEntInfo E3_GetEntInfo = nullptr;

/// <summary>
/// 接口说明:设置对象信息
/// <para>API编码:[81821961]</para>
/// <para>文档定位:数据-对象操作-对象通用读写</para>
/// </summary>
/// <param name="idEM">:管理器ID</param>
/// <param name="idEnt">:对象ID</param>
/// <param name="nFlag">:属性页,对象属性超过本接口所能承载的数量后,可以输入分页参数</param>
/// <param name="np1">:int类型属性信息1</param>
/// <param name="np2">:int类型属性信息2</param>
/// <param name="np3">:int类型属性信息3</param>
/// <param name="np4">:int类型属性信息4</param>
/// <param name="np5">:int类型属性信息5</param>
/// <param name="np6">:int类型属性信息6</param>
/// <param name="dp1">:double类型属性信息1</param>
/// <param name="dp2">:double类型属性信息2</param>
/// <param name="dp3">:double类型属性信息3</param>
/// <param name="dp4">:double类型属性信息4</param>
/// <param name="dp5">:double类型属性信息5</param>
/// <param name="dp6">:double类型属性信息6</param>
/// <param name="str1">:字符型信息</param>
/// <param name="bUndo">:预留,默认False</param>
/// <param name="strUndo">:预留,默认""</param>
e3_SetEntInfo E3_SetEntInfo = nullptr;

/// <summary>
/// 接口说明:设置对象信息接口2
/// <para>API编码:[74334088]</para>
/// <para>文档定位:数据-对象操作-对象通用读写</para>
/// </summary>
/// <param name="idEM">:管理器ID</param>
/// <param name="idEnt">:对象ID</param>
/// <param name="nFlag">:属性页,对象属性超过本接口所能承载的数量后,可以输入分页参数</param>
/// <param name="np1">:int类型属性信息1</param>
/// <param name="np2">:int类型属性信息2</param>
/// <param name="np3">:int类型属性信息3</param>
/// <param name="np4">:int类型属性信息4</param>
/// <param name="np5">:int类型属性信息5</param>
/// <param name="np6">:int类型属性信息6</param>
/// <param name="dp1">:double类型属性信息1</param>
/// <param name="dp2">:double类型属性信息2</param>
/// <param name="dp3">:double类型属性信息3</param>
/// <param name="dp4">:double类型属性信息4</param>
/// <param name="dp5">:double类型属性信息5</param>
/// <param name="dp6">:double类型属性信息6</param>
/// <param name="str1">:字符型信息</param>
e3_SetEntInfo_2 E3_SetEntInfo_2 = nullptr;

/// <summary>
/// 接口说明:读取输出口状态,与[E3_MarkerGetWritePort]不同,[E3_MarkerGetWritePort]接口是读取的库内部缓存值,而此接口读取的是板卡真实值.
/// <para>API编码:[35784011]</para>
/// <para>文档定位:硬件-资源-数字量OUT-查询</para>
/// </summary>
/// <param name="idMarker">:控制卡ID.</param>
/// <param name="wCurOutPort">:返回的状态值.</param>
e3_MarkerGetOutputPortStatus E3_MarkerGetOutputPortStatus = nullptr;

/// <summary>
/// 接口说明:将对象转化为点对象,可以是文本，也可以是矩形等
/// <para>API编码:[56613766]</para>
/// <para>文档定位:数据-对象操作-对象间操作</para>
/// </summary>
/// <param name="idEnt">:对象ID</param>
/// <param name="nParamFlag">:默认为0</param>
/// <param name="bAveragePt">:nPointNum的点数是否平均分布 true的时候平均分布</param>
/// <param name="nPointNum">:平均分布的点数</param>
/// <param name="dPointDist">:非平均分布的时候，点间距</param>
/// <param name="dArcTol">:精度，默认0.01</param>
/// <param name="bDeleteOldEnt">:是否删除旧对象，true删除旧对象</param>
/// <param name="idNewEnt">:点组对象ID</param>
e3_ChangeEntToPoints E3_ChangeEntToPoints = nullptr;

/// <summary>
/// 接口说明:标刻一条3D线段，列表命令
/// <para>API编码:[23803992]</para>
/// <para>文档定位:硬件-加工动作-列表命令-节点级列表命令</para>
/// </summary>
/// <param name="idMarker">:控制卡ID</param>
/// <param name="type">:默认0</param>
/// <param name="pen">:笔号</param>
/// <param name="ptNum">:ptBuf的长度</param>
/// <param name="nFlag">:与E3_MarkerMarkEnt2中的nMarkFlag一致</param>
/// <param name="ptBuf">:线段顶点数组[,3]</param>
e3_MarkerOneCurveToList2 E3_MarkerOneCurveToList2 = nullptr;

/// <summary>
/// 接口说明:得到激光接口板卡类型 0X0001STD 0X0002SPI 0X0003QCW 0X0004FIBER 0X0005PolyScan 0X1001JCZ_LASER
/// <para>API编码:[79218581]</para>
/// <para>文档定位:环境-控制卡-操作</para>
/// </summary>
/// <param name="idMarker">:控制卡ID</param>
/// <param name="id">:扩展卡类型对应的类型</param>
e3_MarkerGetLaserBoardTypeID E3_MarkerGetLaserBoardTypeID = nullptr;

/// <summary>
/// 接口说明:获取变量文本信息
/// <para>API编码:[36382979]</para>
/// <para>文档定位:数据-标准图元-编辑-文本类型-变量文本</para>
/// </summary>
/// <param name="idEnt">:对象ID</param>
/// <param name="nMaxCount">:节点长度</param>
/// <param name="wTypes">:节点类型</param>
/// <param name="wFlags">:节点参数</param>
e3_GetTextElementInfo E3_GetTextElementInfo = nullptr;

/// <summary>
/// 接口说明:获取变量文本_固定文本
/// <para>API编码:[76139045]</para>
/// <para>文档定位:数据-标准图元-编辑-文本类型-变量文本</para>
/// </summary>
/// <param name="idEnt">:对象ID</param>
/// <param name="index">:节点序号</param>
/// <param name="pStr[256]">:固定文本内容</param>
e3_GetTextElementStr E3_GetTextElementStr = nullptr;

/// <summary>
/// 接口说明:获取变量文本_序列号信息
/// <para>API编码:[67467089]</para>
/// <para>文档定位:数据-标准图元-编辑-文本类型-变量文本</para>
/// </summary>
/// <param name="idEnt">:文本对象ID</param>
/// <param name="index">:节点序号</param>
/// <param name="nSnIncrement">:序列号增量</param>
/// <param name="nSnMarksPer">:每个加工数</param>
/// <param name="nSnCurMarksNum">:当前加工数</param>
/// <param name="nSerialCharType">:序列号类型（SC_TYPE_DEC）</param>
/// <param name="nSerialChar">:序列号进制字符数</param>
/// <param name="bEnableFilter">:是否启用过滤</param>
/// <param name="timeReset1">:重置时间</param>
/// <param name="bEnReset1">:是否重置</param>
/// <param name="pStr1[256]">:启示序号</param>
/// <param name="pStr2[256]">:当前序号</param>
/// <param name="pStr3[256]">:最大序号</param>
/// <param name="pFilter1[256]">:过滤内容1</param>
/// <param name="pFilter2[256]">:过滤内容2</param>
/// <param name="pFilter3[256]">:过滤内容3</param>
/// <param name="pFilter4[256]">:过滤内容4</param>
/// <param name="pFilter5[256]">:过滤内容5</param>
e3_GetTextElementSerialNo E3_GetTextElementSerialNo = nullptr;

/// <summary>
/// 接口说明:获取变量文本序列号扩展信息
/// <para>API编码:[93622729]</para>
/// <para>文档定位:数据-标准图元-编辑-文本类型-变量文本</para>
/// </summary>
/// <param name="idEnt">:变量文本ID</param>
/// <param name="index">:节点序号</param>
/// <param name="indexChar">:自定义序列号字符序号</param>
/// <param name="pStr[256]">:自定义序列号指定序号字符串</param>
e3_GetTextElementSerialNo2 E3_GetTextElementSerialNo2 = nullptr;

/// <summary>
/// 接口说明:获取变量文本日期信息
/// <para>API编码:[49677502]</para>
/// <para>文档定位:数据-标准图元-编辑-文本类型-变量文本</para>
/// </summary>
/// <param name="idEnt">:变量文本ID</param>
/// <param name="index">:节点序号</param>
/// <param name="nDateType">:日期类型</param>
/// <param name="nDateOffsetType">:日期偏移类型</param>
/// <param name="nDateOffset">:日期偏移量</param>
/// <param name="bEnableDefYear">:周类型默认按1月1日开始计算</param>
e3_GetTextElementDate E3_GetTextElementDate = nullptr;

/// <summary>
/// 接口说明:变量文本日期具体信息
/// <para>API编码:[07344239]</para>
/// <para>文档定位:数据-标准图元-编辑-文本类型-变量文本</para>
/// </summary>
/// <param name="idEnt">:变量文本ID</param>
/// <param name="index">:节点序号</param>
/// <param name="indexChar">:字符序号</param>
/// <param name="pStr[256]">:字符</param>
e3_GetTextElementDate2 E3_GetTextElementDate2 = nullptr;

/// <summary>
/// 接口说明:变量文本时刻信息
/// <para>API编码:[48032134]</para>
/// <para>文档定位:数据-标准图元-编辑-文本类型-变量文本</para>
/// </summary>
/// <param name="idEnt">:变量文本ID</param>
/// <param name="index">:节点序号</param>
/// <param name="nTimeType">:时刻类型0,24小时 1,12小时 2,分钟 3,秒钟 4时间段</param>
/// <param name="nStartTime[24]">:时间段开始时间列表</param>
/// <param name="nEndTime[24]">:时间段结束时间列表</param>
e3_GetTextElementTime E3_GetTextElementTime = nullptr;

/// <summary>
/// 接口说明:时间段自定义文本
/// <para>API编码:[37884216]</para>
/// <para>文档定位:数据-标准图元-编辑-文本类型-变量文本</para>
/// </summary>
/// <param name="idEnt">:变量文本ID</param>
/// <param name="index">:节点序号</param>
/// <param name="indexChar">:时间段序号</param>
/// <param name="pStr[256]">:时间段对应文本内容</param>
e3_GetTextElementTime2 E3_GetTextElementTime2 = nullptr;

/// <summary>
/// 接口说明:TCPIP通讯文本
/// <para>API编码:[37152633]</para>
/// <para>文档定位:数据-标准图元-编辑-文本类型-变量文本</para>
/// </summary>
/// <param name="idEnt">:变量文本ID</param>
/// <param name="index">:节点序号</param>
/// <param name="nPort">:服务器端口</param>
/// <param name="bUnicode">:是否UNICODE编码</param>
/// <param name="pStr1[256]">:服务器IP地址</param>
/// <param name="pStr2[256]">:请求字段命令</param>
e3_GetTextElementTcpip E3_GetTextElementTcpip = nullptr;

/// <summary>
/// 接口说明:串口通讯文本
/// <para>API编码:[20032220]</para>
/// <para>文档定位:数据-标准图元-编辑-文本类型-变量文本</para>
/// </summary>
/// <param name="idEnt">:变量文本ID</param>
/// <param name="index">:节点序号</param>
/// <param name="nPort">:上位机端口</param>
/// <param name="bUnicode">:是否UNICODE编码</param>
/// <param name="nBaudRate">:波特率</param>
/// <param name="nDataBits">:数据位</param>
/// <param name="nStopBits">:停止位</param>
/// <param name="nParity">:是否效验</param>
/// <param name="pStr1[256]">:请求字段命令</param>
e3_GetTextElementCom E3_GetTextElementCom = nullptr;

/// <summary>
/// 接口说明:变量文本-文件
/// <para>API编码:[78608175]</para>
/// <para>文档定位:数据-标准图元-编辑-文本类型-变量文本</para>
/// </summary>
/// <param name="idEnt">:变量文本ID</param>
/// <param name="index">:节点序号</param>
/// <param name="nFileType">:文件类型0记事本 1EXCEL</param>
/// <param name="bAutoReset">:完成后自动重置</param>
/// <param name="bReadAll">:全部读取</param>
/// <param name="nCurFileLineNo">:当前文件行数</param>
/// <param name="nCurFileInc">:行增量</param>
/// <param name="pStr1[256]">:文件名</param>
/// <param name="pStr2[256]">:EXCEL表名</param>
/// <param name="pStr3[256]">:EXCEL列名</param>
e3_GetTextElementFile E3_GetTextElementFile = nullptr;

/// <summary>
/// 接口说明:变量文本-键盘
/// <para>API编码:[79083478]</para>
/// <para>文档定位:数据-标准图元-编辑-文本类型-变量文本</para>
/// </summary>
/// <param name="idEnt">:变量文本ID</param>
/// <param name="index">:节点序号</param>
/// <param name="bEnableFixedLength">:是否固定长度</param>
/// <param name="bSetPenParam">:是否切换笔参数</param>
/// <param name="nCharLength">:固定长度值</param>
/// <param name="pStr1[256]">:请求字符命令</param>
/// <param name="pStr2[256]">:笔号+参数类型</param>
e3_GetTextElementKB E3_GetTextElementKB = nullptr;

/// <summary>
/// 接口说明:sql数据库变量文本.
/// <para>API编码:[40272377]</para>
/// <para>文档定位:数据-标准图元-编辑-文本类型-变量文本</para>
/// </summary>
/// <param name="idEnt">:变量文本ID</param>
/// <param name="index">:节点序号</param>
/// <param name="bAutoReset">:是否自动复位</param>
/// <param name="bReadAll">:是否读取全部</param>
/// <param name="nSqlLineNo">:SQL行号</param>
/// <param name="nSqlInc">:SQL行号增量</param>
/// <param name="pStr1[256]">:服务器信息</param>
/// <param name="pStr2[256]">:文件路径</param>
/// <param name="pStr3[256]">:用户名</param>
/// <param name="pStr4[256]">:密码</param>
/// <param name="pStr5[256]">:SQL查询命令</param>
e3_GetTextElementSql E3_GetTextElementSql = nullptr;

/// <summary>
/// 接口说明:调整变量文本节点排序
/// <para>API编码:[64254685]</para>
/// <para>文档定位:数据-标准图元-编辑-文本类型-变量文本</para>
/// </summary>
/// <param name="idEM">:对象管理器ID</param>
/// <param name="idEnt">:变量文本ID</param>
/// <param name="indexElement">:节点序号</param>
/// <param name="nFun">:0删除 1上调 2下调</param>
/// <param name="bUndo">:默认参数 FALSE</param>
/// <param name="strUndo">:默认参数 ""</param>
e3_ModifyTextElement E3_ModifyTextElement = nullptr;

/// <summary>
/// 接口说明:变量文本内容更新.
/// <para>API编码:[51464256]</para>
/// <para>文档定位:数据-标准图元-编辑-文本类型-变量文本</para>
/// </summary>
/// <param name="idEM">:对象管理器ID</param>
/// <param name="idEnt">:变量文本ID</param>
/// <param name="nSubCmd">:-1递减 0复位 1递增</param>
e3_SnTextEntRefresh E3_SnTextEntRefresh = nullptr;

/// <summary>
/// 接口说明:更新变量文本单元信息
/// <para>API编码:[22293514]</para>
/// <para>文档定位:数据-标准图元-编辑-文本类型-变量文本</para>
/// </summary>
/// <param name="idEM">:对象管理器ID</param>
/// <param name="idEnt">:变量文本ID</param>
/// <param name="indexElement">:变量文本单元序号</param>
/// <param name="nMaxParamN">:整形参数长度</param>
/// <param name="nParam">:整型参数列表</param>
/// <param name="nMaxParamD">:浮点参数长度</param>
/// <param name="dParam">:浮点参数列表</param>
/// <param name="nMaxParamS">:字符串参数长度</param>
/// <param name="sParam">:字符串数量</param>
/// <param name="bUndo">:是否支持撤销</param>
/// <param name="strUndo">:动作节点说明</param>
e3_UpdateTextElement E3_UpdateTextElement = nullptr;

/// <summary>
/// 接口说明:更新变量文本内容,也即得到新的值.
/// <para>API编码:[98510811]</para>
/// <para>文档定位:数据-标准图元-编辑-文本类型-变量文本</para>
/// </summary>
/// <param name="idEM">:对象管理器ID.</param>
/// <param name="idEnt">:变量文本对象ID.</param>
e3_VariableEntRefresh E3_VariableEntRefresh = nullptr;

/// <summary>
/// 接口说明:变量文本获取掩码元素参数.
/// <para>API编码:[90171795]</para>
/// <para>文档定位:数据-标准图元-编辑-文本类型-变量文本</para>
/// </summary>
/// <param name="idEnt">:对象ID</param>
/// <param name="index">:当前掩码元素所在变量列表索引号</param>
/// <param name="strMask[256]">:掩码</param>
/// <param name="strAlias[256]">:别名</param>
/// <param name="strText[256]">:文本</param>
e3_GetTextElementMask E3_GetTextElementMask = nullptr;

/// <summary>
/// 接口说明:获取二维条码的删除中间块功能参数.
/// <para>API编码:[13352731]</para>
/// <para>文档定位:数据-对象操作-对象通用读写</para>
/// </summary>
/// <param name="idEnt">:对象ID</param>
/// <param name="bDeleteCenterBlock">:是否使能删除中间块</param>
/// <param name="nDeleteBlockNumX">:删除中间块的X数量</param>
/// <param name="nDeleteBlockNumY">:删除中间块的Y数量</param>
e3_GetTextBarcodeInfo8 E3_GetTextBarcodeInfo8 = nullptr;

/// <summary>
/// 接口说明:设置二维条码的删除中间块功能参数.
/// <para>API编码:[90198558]</para>
/// <para>文档定位:数据-对象操作-对象通用读写</para>
/// </summary>
/// <param name="idEnt">:对象ID</param>
/// <param name="bDeleteCenterBlock">:是否使能删除中间块</param>
/// <param name="nDeleteBlockNumX">:删除中间块的X数量</param>
/// <param name="nDeleteBlockNumY">:删除中间块的Y数量</param>
e3_SetTextBarcodeInfo8 E3_SetTextBarcodeInfo8 = nullptr;

/// <summary>
/// 接口说明:设置对象隐藏状态.
/// <para>API编码:[80125201]</para>
/// <para>文档定位:数据-对象操作-对象通用读写</para>
/// </summary>
/// <param name="idEnt">:对象ID</param>
/// <param name="bHide">:是否设置隐藏</param>
e3_SetEntHide E3_SetEntHide = nullptr;

/// <summary>
/// 接口说明:解散群组,通过nOneGroupCount设置的数量进行分组解散
/// <para>API编码:[39209787]</para>
/// <para>文档定位:数据-对象操作-对象间操作</para>
/// </summary>
/// <param name="idEntGroup">:群组对象ID</param>
/// <param name="nFlag">:0x1，禁止通过笔号解散子对象</param>
/// <param name="nOneGroupCount">:设置打包对象数量,将按照此数量进行打包解散</param>
e3_UnGroupEnt3 E3_UnGroupEnt3 = nullptr;

/// <summary>
/// 接口说明:linux平台下,在初始化之前设置系统主机与控制卡之间的通讯链路类型.
/// <para>API编码:[60715303]</para>
/// <para>文档定位:环境-初始化以及释放</para>
/// </summary>
/// <param name="Type">:控制卡通讯链路类型:Type=0x8,Linux SPI, Type=0x3,Linux Usb</param>
e3_SetControllerInterfaceType E3_SetControllerInterfaceType = nullptr;

/// <summary>
/// 接口说明:1.填充指定对象，最多八组填充参数； 2.当被填充的对象为非填充对象时，只能用此接口； 3.当被填充的对象时填充对象，可以用此接口，也可以用E3_SetHatchParam或者E3_SetHatchParam2修改填充参数
/// <para>API编码:[15240066]</para>
/// <para>文档定位:数据-填充相关</para>
/// </summary>
/// <param name="idEM">:管理器ID</param>
/// <param name="idEnt">:对象ID</param>
/// <param name="bEnableContour">:是否使能轮廓;true使能，false不使能</param>
/// <param name="bContourFirst">:是否使能轮廓优先;true使能，false不使能；</param>
/// <param name="nHatchParamCount">:填充参数数组paramList长度；范围1-8</param>
/// <param name="pParam">:填充参数数组</param>
/// <param name="idEntHatch">:填充之后的对象ID</param>
/// <param name="reserved1">:预留参数,默认False</param>
/// <param name="reserved2">:预留参数,默认""</param>
e3_HatchEnt3 E3_HatchEnt3 = nullptr;

/// <summary>
/// 接口说明:获取qcw第二功率输出
/// <para>API编码:[27026726]</para>
/// <para>文档定位:数据-笔参数相关</para>
/// </summary>
/// <param name="idEM">:管理器ID</param>
/// <param name="nPenNo">:笔号</param>
/// <param name="dPowerRatio2">:返回的第二组功率输出</param>
e3_GetPenParamPower2 E3_GetPenParamPower2 = nullptr;

/// <summary>
/// 接口说明:设置qcw第二功率输出
/// <para>API编码:[05201969]</para>
/// <para>文档定位:数据-笔参数相关</para>
/// </summary>
/// <param name="idEM">:管理器ID</param>
/// <param name="nPenNo">:笔号</param>
/// <param name="dPowerRatio2">:设置第二组功率输出值</param>
e3_SetPenParamPower2 E3_SetPenParamPower2 = nullptr;

/// <summary>
/// 接口说明:设置系统int类型参数.从sysparam.ini中读取.
/// <para>API编码:[60832921]</para>
/// <para>文档定位:环境-控制卡-配置</para>
/// </summary>
/// <param name="index">:系统参数中int类型参数的索引号</param>
/// <param name="value">:对应索引参数值</param>
e3_SetSysParamInt E3_SetSysParamInt = nullptr;

/// <summary>
/// 接口说明:获取系统int类型参数.从sysparam.ini中读取.
/// <para>API编码:[90308215]</para>
/// <para>文档定位:环境-控制卡-配置</para>
/// </summary>
/// <param name="index">:系统参数中int类型参数的索引号</param>
/// <param name="value">:对应索引参数值</param>
e3_GetSysParamInt E3_GetSysParamInt = nullptr;

/// <summary>
/// 接口说明:变量文本刷新,但不对序列号刷新.
/// <para>API编码:[57783273]</para>
/// <para>文档定位:数据-标准图元-编辑-文本类型-变量文本</para>
/// </summary>
/// <param name="idEM">:管理器ID</param>
/// <param name="idEnt">:对象ID</param>
e3_VariableEntRefresh_NoSN E3_VariableEntRefresh_NoSN = nullptr;

/// <summary>
/// 接口说明:变量文本更新,用于加工前后更新数据,加工后调用,会更新曲线.
/// <para>API编码:[88753679]</para>
/// <para>文档定位:数据-标准图元-编辑-文本类型-变量文本</para>
/// </summary>
/// <param name="idEM">:管理器ID</param>
/// <param name="idEnt">:对象ID</param>
/// <param name="bMark">:刷新标志,True:加工前刷新.False:加工后刷新</param>
e3_VariableEntRefresh2 E3_VariableEntRefresh2 = nullptr;

/// <summary>
/// 接口说明:获取当前底层库的版本信息
/// <para>API编码:[35905330]</para>
/// <para>文档定位:环境-控制卡</para>
/// </summary>
/// <param name="szVersion[256]">:返回的版本信息字符串</param>
e3_GetDllVersion E3_GetDllVersion = nullptr;

/// <summary>
/// 接口说明:添加螺旋线3.
/// <para>API编码:[85082386]</para>
/// <para>文档定位:数据-标准图元-创建</para>
/// </summary>
/// <param name="idEM">:管理器ID</param>
/// <param name="nPen">:笔号[0,255]</param>
/// <param name="pt1">:螺旋中心坐标</param>
/// <param name="pt2">:螺旋半径坐标 （X 坐标为中心坐标+半径长度，Y坐标为中心坐标）</param>
/// <param name="dSpiralPitchDistMin">:最小螺旋线间距</param>
/// <param name="dSpiralPitchDistMax">:最大螺旋线间距</param>
/// <param name="dSpiralPitchDistInc">:螺旋线间距增量</param>
/// <param name="bUpdateParentInfo">:是否更新列表信息，若不更新对象列表信息,最后更新,避免大量创建时由于更新对象列表导致的卡顿</param>
/// <param name="idNewEnt">:返回创建的对象ID</param>
e3_CreateSpiral_3 E3_CreateSpiral_3 = nullptr;

/// <summary>
/// 接口说明:获取输入口状态,此接口支持读取锁存状态,通过[E3_SetInputPortWorkMode]接口设置模式为脉冲及高低电平,锁存功能才会被使能. 当板卡检测到边沿信号后,会将portLatchedStatus对应端口位置位1,此时需要调用[MarkerClearInputPort0State]或[MarkerClearInputPortState]来清除板卡缓存状态. 建议不要在portLatchedStatus为0的情况下,调用清锁存接口,因为会存在误清的情况.
/// <para>API编码:[10485363]</para>
/// <para>文档定位:硬件-资源-数字量IN-查询</para>
/// </summary>
/// <param name="idMarker">:控制卡ID</param>
/// <param name="portData">:端口当前的电平值,此值与[E3_MarkerReadPort]接口相同.(v4卡默认为1,一般情况读取为0x0fff).</param>
/// <param name="portLatchedStatus">:端口锁存状态,位指示脉冲锁存是否有效,通过[MarkerClearInputPortState]接口清除.</param>
e3_MarkerGetInputPortStatus E3_MarkerGetInputPortStatus = nullptr;

/// <summary>
/// 接口说明:清除板卡输入口的锁存状态,配合[E3_MarkerGetInputPortStatus]接口使用.
/// <para>API编码:[04580131]</para>
/// <para>文档定位:硬件-资源-数字量IN-配置</para>
/// </summary>
/// <param name="idMarker">:控制卡ID</param>
/// <param name="portNo">:十进制端口索引编号,一般的为0-15</param>
e3_MarkerClearInputPortState E3_MarkerClearInputPortState = nullptr;

/// <summary>
/// 接口说明:清除板卡输入口的锁存状态,配合[E3_MarkerGetInputPortStatus]接口使用.与[MarkerClearInputPortState]功能相同,但是此接口适配老版本底层程序.
/// <para>API编码:[95336489]</para>
/// <para>文档定位:硬件-资源-数字量IN-配置</para>
/// </summary>
/// <param name="idMarker">:控制卡ID</param>
/// <param name="portNo">:十进制端口索引编号,一般的为0-15</param>
e3_MarkerClearInputPort0State E3_MarkerClearInputPort0State = nullptr;

/// <summary>
/// 接口说明:列表中发送空指令.
/// <para>API编码:[68546191]</para>
/// <para>文档定位:硬件-加工动作-列表命令-列表过程命令</para>
/// </summary>
/// <param name="idMarker">:控制卡ID</param>
e3_MarkerListNop E3_MarkerListNop = nullptr;

/// <summary>
/// 接口说明:此接口设置停止标志,在填充过程中支持取消. 注意,需要在填充之前将标志设置为false,不然填充接口不执行. 设置标志后,填充接口停止会有一定延迟,与底层库的检测时机有关.
/// <para>API编码:[62931927]</para>
/// <para>文档定位:数据-填充相关</para>
/// </summary>
/// <param name="bStop">:是否填充中取消标志</param>
e3_SetHatchStop E3_SetHatchStop = nullptr;

};

#endif // EZDKERNEL_H

