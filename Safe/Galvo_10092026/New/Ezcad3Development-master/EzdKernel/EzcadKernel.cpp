
/*********************************
导出日期:2026/4/8 14:35:06
文档版本:Ver:1.2.9.6 Date:2026.04.08 L0 
*********************************/

#include "EzcadKernel.h" 
#include <cstring>
using namespace std;

#define M_PI 3.14159265358979323846

MarkEntMode operator|(MarkEntMode a, MarkEntMode b)
{
    return (MarkEntMode)((uint32_t)a | (uint32_t)b);
}
MarkEntMode& operator|=(MarkEntMode& a, MarkEntMode b)
{
    a = (MarkEntMode)((uint32_t)a | (uint32_t)b);
    return a;
}
MarkEntMode& operator&=(MarkEntMode& a, MarkEntMode b)
{
    a = (MarkEntMode)((uint32_t)a & (uint32_t)b);
    return a;
}
MarkEntMode operator~(MarkEntMode a)
{
    return (MarkEntMode)(~(uint32_t)a);
}
ListReadyMode operator|(ListReadyMode a, ListReadyMode b)
{
    return (ListReadyMode)((uint32_t)a | (uint32_t)b);
}
ListReadyMode& operator|=(ListReadyMode& a, ListReadyMode b)
{
    a = (ListReadyMode)((uint32_t)a | (uint32_t)b);
    return a;
}
ListReadyMode& operator&=(ListReadyMode& a, ListReadyMode b)
{
    a = (ListReadyMode)((uint32_t)a & (uint32_t)b);
    return a;
}
ListReadyMode operator~(ListReadyMode a)
{
    return (ListReadyMode)(~(uint32_t)a);
}
//接口库主类.
EzdKernel::EzdKernel(LogCallbackHandler logback)
{
    setlocale(LC_ALL, "");

    logCallback = logback;	
#ifdef _WIN32
    m_sysDLL = LoadLibrary(_T("user32.dll"));
    if (!m_sysDLL)
    {
        if (logback)
        {
            (logback)(_T("Can not find user32.dll!"), 0, LogLevel::Normal, LogType::Warning);
        }
    }
    else
    {
        GetForegroundWindow = (getForegroundWindow)GetProcAddress(m_sysDLL, "GetForegroundWindow");
        if (GetForegroundWindow == nullptr)
        {
            if (logback)
            {
                (logback)(_T("Can not find funtion GetForegroundWindow in user32.dll!"), 0, LogLevel::Normal, LogType::Warning);
            }
        }
    }
    m_hEzdDLL = LoadLibrary(_T("Ezcad3Kernel.dll"));
#else
    m_hEzdDLL = dlopen("libEzcad3Kernel.so", RTLD_LAZY);
#endif
    if (!m_hEzdDLL)
    {
        if (logback)
        {
#ifdef __linux_
            wstring tmp = L"Can not find Ezcad3Kernel.dll->";
            char* tmpData = dlerror();
            size_t len = std::strlen(tmpData) + 1;
            std::unique_ptr<wchar_t[]> wstr(new wchar_t[len]);
            std::mbstowcs(wstr.get(), tmpData, len);
            tmp += std::wstring(wstr.get());
            (logback)((TCHAR*)tmp.data(), 0, LogLevel::Normal, LogType::Error);
#else
            (logback)(_T("Can not find Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Error);

#endif // __linux_
        }

    }
    else
    {
#ifdef _WIN32
        E3_AxisStopForce = (e3_AxisStopForce)GetProcAddress(m_hEzdDLL, "E3_AxisStopForce");
#else
        E3_AxisStopForce = (e3_AxisStopForce)dlsym(m_hEzdDLL, "E3_AxisStopForce");
#endif
        if (E3_AxisStopForce == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_AxisStopForce in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_ClearLayerAllChild = (e3_ClearLayerAllChild)GetProcAddress(m_hEzdDLL, "E3_ClearLayerAllChild");
#else
        E3_ClearLayerAllChild = (e3_ClearLayerAllChild)dlsym(m_hEzdDLL, "E3_ClearLayerAllChild");
#endif
        if (E3_ClearLayerAllChild == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_ClearLayerAllChild in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_Get3DPrintAnalogOutput = (e3_Get3DPrintAnalogOutput)GetProcAddress(m_hEzdDLL, "E3_Get3DPrintAnalogOutput");
#else
        E3_Get3DPrintAnalogOutput = (e3_Get3DPrintAnalogOutput)dlsym(m_hEzdDLL, "E3_Get3DPrintAnalogOutput");
#endif
        if (E3_Get3DPrintAnalogOutput == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_Get3DPrintAnalogOutput in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_GetEntHatchParam = (e3_GetEntHatchParam)GetProcAddress(m_hEzdDLL, "E3_GetEntHatchParam");
#else
        E3_GetEntHatchParam = (e3_GetEntHatchParam)dlsym(m_hEzdDLL, "E3_GetEntHatchParam");
#endif
        if (E3_GetEntHatchParam == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_GetEntHatchParam in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_GetEntParam3 = (e3_GetEntParam3)GetProcAddress(m_hEzdDLL, "E3_GetEntParam3");
#else
        E3_GetEntParam3 = (e3_GetEntParam3)dlsym(m_hEzdDLL, "E3_GetEntParam3");
#endif
        if (E3_GetEntParam3 == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_GetEntParam3 in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_GetOneLayerFromSlcFile2 = (e3_GetOneLayerFromSlcFile2)GetProcAddress(m_hEzdDLL, "E3_GetOneLayerFromSlcFile2");
#else
        E3_GetOneLayerFromSlcFile2 = (e3_GetOneLayerFromSlcFile2)dlsym(m_hEzdDLL, "E3_GetOneLayerFromSlcFile2");
#endif
        if (E3_GetOneLayerFromSlcFile2 == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_GetOneLayerFromSlcFile2 in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_MarkCorStdPoint = (e3_MarkCorStdPoint)GetProcAddress(m_hEzdDLL, "E3_MarkCorStdPoint");
#else
        E3_MarkCorStdPoint = (e3_MarkCorStdPoint)dlsym(m_hEzdDLL, "E3_MarkCorStdPoint");
#endif
        if (E3_MarkCorStdPoint == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_MarkCorStdPoint in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_MarkerGetExtInputPortStatus = (e3_MarkerGetExtInputPortStatus)GetProcAddress(m_hEzdDLL, "E3_MarkerGetExtInputPortStatus");
#else
        E3_MarkerGetExtInputPortStatus = (e3_MarkerGetExtInputPortStatus)dlsym(m_hEzdDLL, "E3_MarkerGetExtInputPortStatus");
#endif
        if (E3_MarkerGetExtInputPortStatus == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_MarkerGetExtInputPortStatus in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_MarkerGetExtOutputPort = (e3_MarkerGetExtOutputPort)GetProcAddress(m_hEzdDLL, "E3_MarkerGetExtOutputPort");
#else
        E3_MarkerGetExtOutputPort = (e3_MarkerGetExtOutputPort)dlsym(m_hEzdDLL, "E3_MarkerGetExtOutputPort");
#endif
        if (E3_MarkerGetExtOutputPort == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_MarkerGetExtOutputPort in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_MarkerSelectCorTableToList = (e3_MarkerSelectCorTableToList)GetProcAddress(m_hEzdDLL, "E3_MarkerSelectCorTableToList");
#else
        E3_MarkerSelectCorTableToList = (e3_MarkerSelectCorTableToList)dlsym(m_hEzdDLL, "E3_MarkerSelectCorTableToList");
#endif
        if (E3_MarkerSelectCorTableToList == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_MarkerSelectCorTableToList in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_MarkerSetCorFile = (e3_MarkerSetCorFile)GetProcAddress(m_hEzdDLL, "E3_MarkerSetCorFile");
#else
        E3_MarkerSetCorFile = (e3_MarkerSetCorFile)dlsym(m_hEzdDLL, "E3_MarkerSetCorFile");
#endif
        if (E3_MarkerSetCorFile == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_MarkerSetCorFile in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_MarkerSetExtOutputPort = (e3_MarkerSetExtOutputPort)GetProcAddress(m_hEzdDLL, "E3_MarkerSetExtOutputPort");
#else
        E3_MarkerSetExtOutputPort = (e3_MarkerSetExtOutputPort)dlsym(m_hEzdDLL, "E3_MarkerSetExtOutputPort");
#endif
        if (E3_MarkerSetExtOutputPort == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_MarkerSetExtOutputPort in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_MarkerSetStepperAxisVelocityMode = (e3_MarkerSetStepperAxisVelocityMode)GetProcAddress(m_hEzdDLL, "E3_MarkerSetStepperAxisVelocityMode");
#else
        E3_MarkerSetStepperAxisVelocityMode = (e3_MarkerSetStepperAxisVelocityMode)dlsym(m_hEzdDLL, "E3_MarkerSetStepperAxisVelocityMode");
#endif
        if (E3_MarkerSetStepperAxisVelocityMode == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_MarkerSetStepperAxisVelocityMode in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_ResortEntChilds = (e3_ResortEntChilds)GetProcAddress(m_hEzdDLL, "E3_ResortEntChilds");
#else
        E3_ResortEntChilds = (e3_ResortEntChilds)dlsym(m_hEzdDLL, "E3_ResortEntChilds");
#endif
        if (E3_ResortEntChilds == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_ResortEntChilds in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_ResortEntChilds2 = (e3_ResortEntChilds2)GetProcAddress(m_hEzdDLL, "E3_ResortEntChilds2");
#else
        E3_ResortEntChilds2 = (e3_ResortEntChilds2)dlsym(m_hEzdDLL, "E3_ResortEntChilds2");
#endif
        if (E3_ResortEntChilds2 == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_ResortEntChilds2 in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_Set3DPrintAnalogOutput = (e3_Set3DPrintAnalogOutput)GetProcAddress(m_hEzdDLL, "E3_Set3DPrintAnalogOutput");
#else
        E3_Set3DPrintAnalogOutput = (e3_Set3DPrintAnalogOutput)dlsym(m_hEzdDLL, "E3_Set3DPrintAnalogOutput");
#endif
        if (E3_Set3DPrintAnalogOutput == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_Set3DPrintAnalogOutput in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_Set3DPrintPWMOutput = (e3_Set3DPrintPWMOutput)GetProcAddress(m_hEzdDLL, "E3_Set3DPrintPWMOutput");
#else
        E3_Set3DPrintPWMOutput = (e3_Set3DPrintPWMOutput)dlsym(m_hEzdDLL, "E3_Set3DPrintPWMOutput");
#endif
        if (E3_Set3DPrintPWMOutput == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_Set3DPrintPWMOutput in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_Set3x3PointCor = (e3_Set3x3PointCor)GetProcAddress(m_hEzdDLL, "E3_Set3x3PointCor");
#else
        E3_Set3x3PointCor = (e3_Set3x3PointCor)dlsym(m_hEzdDLL, "E3_Set3x3PointCor");
#endif
        if (E3_Set3x3PointCor == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_Set3x3PointCor in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_SetMultiPointCor = (e3_SetMultiPointCor)GetProcAddress(m_hEzdDLL, "E3_SetMultiPointCor");
#else
        E3_SetMultiPointCor = (e3_SetMultiPointCor)dlsym(m_hEzdDLL, "E3_SetMultiPointCor");
#endif
        if (E3_SetMultiPointCor == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_SetMultiPointCor in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_ChangeOrderLayer = (e3_ChangeOrderLayer)GetProcAddress(m_hEzdDLL, "E3_ChangeOrderLayer");
#else
        E3_ChangeOrderLayer = (e3_ChangeOrderLayer)dlsym(m_hEzdDLL, "E3_ChangeOrderLayer");
#endif
        if (E3_ChangeOrderLayer == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_ChangeOrderLayer in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_CloseMotionMgrOfMarker = (e3_CloseMotionMgrOfMarker)GetProcAddress(m_hEzdDLL, "E3_CloseMotionMgrOfMarker");
#else
        E3_CloseMotionMgrOfMarker = (e3_CloseMotionMgrOfMarker)dlsym(m_hEzdDLL, "E3_CloseMotionMgrOfMarker");
#endif
        if (E3_CloseMotionMgrOfMarker == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_CloseMotionMgrOfMarker in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_CreateAddStlFile = (e3_CreateAddStlFile)GetProcAddress(m_hEzdDLL, "E3_CreateAddStlFile");
#else
        E3_CreateAddStlFile = (e3_CreateAddStlFile)dlsym(m_hEzdDLL, "E3_CreateAddStlFile");
#endif
        if (E3_CreateAddStlFile == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_CreateAddStlFile in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_CreateBeziers = (e3_CreateBeziers)GetProcAddress(m_hEzdDLL, "E3_CreateBeziers");
#else
        E3_CreateBeziers = (e3_CreateBeziers)dlsym(m_hEzdDLL, "E3_CreateBeziers");
#endif
        if (E3_CreateBeziers == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_CreateBeziers in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_CreateBeziers_2 = (e3_CreateBeziers_2)GetProcAddress(m_hEzdDLL, "E3_CreateBeziers_2");
#else
        E3_CreateBeziers_2 = (e3_CreateBeziers_2)dlsym(m_hEzdDLL, "E3_CreateBeziers_2");
#endif
        if (E3_CreateBeziers_2 == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_CreateBeziers_2 in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_DelEntHatchParam = (e3_DelEntHatchParam)GetProcAddress(m_hEzdDLL, "E3_DelEntHatchParam");
#else
        E3_DelEntHatchParam = (e3_DelEntHatchParam)dlsym(m_hEzdDLL, "E3_DelEntHatchParam");
#endif
        if (E3_DelEntHatchParam == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_DelEntHatchParam in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_DelEntHatchParam_2 = (e3_DelEntHatchParam_2)GetProcAddress(m_hEzdDLL, "E3_DelEntHatchParam_2");
#else
        E3_DelEntHatchParam_2 = (e3_DelEntHatchParam_2)dlsym(m_hEzdDLL, "E3_DelEntHatchParam_2");
#endif
        if (E3_DelEntHatchParam_2 == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_DelEntHatchParam_2 in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_DeleteAllChildOfEnt = (e3_DeleteAllChildOfEnt)GetProcAddress(m_hEzdDLL, "E3_DeleteAllChildOfEnt");
#else
        E3_DeleteAllChildOfEnt = (e3_DeleteAllChildOfEnt)dlsym(m_hEzdDLL, "E3_DeleteAllChildOfEnt");
#endif
        if (E3_DeleteAllChildOfEnt == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_DeleteAllChildOfEnt in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_DeleteEnt = (e3_DeleteEnt)GetProcAddress(m_hEzdDLL, "E3_DeleteEnt");
#else
        E3_DeleteEnt = (e3_DeleteEnt)dlsym(m_hEzdDLL, "E3_DeleteEnt");
#endif
        if (E3_DeleteEnt == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_DeleteEnt in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_DeleteLayer = (e3_DeleteLayer)GetProcAddress(m_hEzdDLL, "E3_DeleteLayer");
#else
        E3_DeleteLayer = (e3_DeleteLayer)dlsym(m_hEzdDLL, "E3_DeleteLayer");
#endif
        if (E3_DeleteLayer == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_DeleteLayer in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_DeleteLayer2 = (e3_DeleteLayer2)GetProcAddress(m_hEzdDLL, "E3_DeleteLayer2");
#else
        E3_DeleteLayer2 = (e3_DeleteLayer2)dlsym(m_hEzdDLL, "E3_DeleteLayer2");
#endif
        if (E3_DeleteLayer2 == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_DeleteLayer2 in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_DistortionEntity = (e3_DistortionEntity)GetProcAddress(m_hEzdDLL, "E3_DistortionEntity");
#else
        E3_DistortionEntity = (e3_DistortionEntity)dlsym(m_hEzdDLL, "E3_DistortionEntity");
#endif
        if (E3_DistortionEntity == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_DistortionEntity in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_DistortionEntity_2 = (e3_DistortionEntity_2)GetProcAddress(m_hEzdDLL, "E3_DistortionEntity_2");
#else
        E3_DistortionEntity_2 = (e3_DistortionEntity_2)dlsym(m_hEzdDLL, "E3_DistortionEntity_2");
#endif
        if (E3_DistortionEntity_2 == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_DistortionEntity_2 in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_FunCF = (e3_FunCF)GetProcAddress(m_hEzdDLL, "E3_FunCF");
#else
        E3_FunCF = (e3_FunCF)dlsym(m_hEzdDLL, "E3_FunCF");
#endif
        if (E3_FunCF == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_FunCF in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_FunCF9 = (e3_FunCF9)GetProcAddress(m_hEzdDLL, "E3_FunCF9");
#else
        E3_FunCF9 = (e3_FunCF9)dlsym(m_hEzdDLL, "E3_FunCF9");
#endif
        if (E3_FunCF9 == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_FunCF9 in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_GetHatchParam = (e3_GetHatchParam)GetProcAddress(m_hEzdDLL, "E3_GetHatchParam");
#else
        E3_GetHatchParam = (e3_GetHatchParam)dlsym(m_hEzdDLL, "E3_GetHatchParam");
#endif
        if (E3_GetHatchParam == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_GetHatchParam in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_GetHatchParam2 = (e3_GetHatchParam2)GetProcAddress(m_hEzdDLL, "E3_GetHatchParam2");
#else
        E3_GetHatchParam2 = (e3_GetHatchParam2)dlsym(m_hEzdDLL, "E3_GetHatchParam2");
#endif
        if (E3_GetHatchParam2 == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_GetHatchParam2 in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_GetStlFileSize = (e3_GetStlFileSize)GetProcAddress(m_hEzdDLL, "E3_GetStlFileSize");
#else
        E3_GetStlFileSize = (e3_GetStlFileSize)dlsym(m_hEzdDLL, "E3_GetStlFileSize");
#endif
        if (E3_GetStlFileSize == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_GetStlFileSize in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_HatchEnt = (e3_HatchEnt)GetProcAddress(m_hEzdDLL, "E3_HatchEnt");
#else
        E3_HatchEnt = (e3_HatchEnt)dlsym(m_hEzdDLL, "E3_HatchEnt");
#endif
        if (E3_HatchEnt == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_HatchEnt in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_HatchEnt2 = (e3_HatchEnt2)GetProcAddress(m_hEzdDLL, "E3_HatchEnt2");
#else
        E3_HatchEnt2 = (e3_HatchEnt2)dlsym(m_hEzdDLL, "E3_HatchEnt2");
#endif
        if (E3_HatchEnt2 == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_HatchEnt2 in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_HatchEntByBack = (e3_HatchEntByBack)GetProcAddress(m_hEzdDLL, "E3_HatchEntByBack");
#else
        E3_HatchEntByBack = (e3_HatchEntByBack)dlsym(m_hEzdDLL, "E3_HatchEntByBack");
#endif
        if (E3_HatchEntByBack == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_HatchEntByBack in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_InitMotorMgrOfMarker = (e3_InitMotorMgrOfMarker)GetProcAddress(m_hEzdDLL, "E3_InitMotorMgrOfMarker");
#else
        E3_InitMotorMgrOfMarker = (e3_InitMotorMgrOfMarker)dlsym(m_hEzdDLL, "E3_InitMotorMgrOfMarker");
#endif
        if (E3_InitMotorMgrOfMarker == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_InitMotorMgrOfMarker in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_IsAxisHaveFault = (e3_IsAxisHaveFault)GetProcAddress(m_hEzdDLL, "E3_IsAxisHaveFault");
#else
        E3_IsAxisHaveFault = (e3_IsAxisHaveFault)dlsym(m_hEzdDLL, "E3_IsAxisHaveFault");
#endif
        if (E3_IsAxisHaveFault == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_IsAxisHaveFault in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_IsAxisHaveHome = (e3_IsAxisHaveHome)GetProcAddress(m_hEzdDLL, "E3_IsAxisHaveHome");
#else
        E3_IsAxisHaveHome = (e3_IsAxisHaveHome)dlsym(m_hEzdDLL, "E3_IsAxisHaveHome");
#endif
        if (E3_IsAxisHaveHome == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_IsAxisHaveHome in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_IsAxisMoving = (e3_IsAxisMoving)GetProcAddress(m_hEzdDLL, "E3_IsAxisMoving");
#else
        E3_IsAxisMoving = (e3_IsAxisMoving)dlsym(m_hEzdDLL, "E3_IsAxisMoving");
#endif
        if (E3_IsAxisMoving == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_IsAxisMoving in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_MarkCorStdPoint2 = (e3_MarkCorStdPoint2)GetProcAddress(m_hEzdDLL, "E3_MarkCorStdPoint2");
#else
        E3_MarkCorStdPoint2 = (e3_MarkCorStdPoint2)dlsym(m_hEzdDLL, "E3_MarkCorStdPoint2");
#endif
        if (E3_MarkCorStdPoint2 == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_MarkCorStdPoint2 in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_MarkerSelectCorTable = (e3_MarkerSelectCorTable)GetProcAddress(m_hEzdDLL, "E3_MarkerSelectCorTable");
#else
        E3_MarkerSelectCorTable = (e3_MarkerSelectCorTable)dlsym(m_hEzdDLL, "E3_MarkerSelectCorTable");
#endif
        if (E3_MarkerSelectCorTable == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_MarkerSelectCorTable in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_MirrorEnt = (e3_MirrorEnt)GetProcAddress(m_hEzdDLL, "E3_MirrorEnt");
#else
        E3_MirrorEnt = (e3_MirrorEnt)dlsym(m_hEzdDLL, "E3_MirrorEnt");
#endif
        if (E3_MirrorEnt == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_MirrorEnt in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_MoveEntToIndex = (e3_MoveEntToIndex)GetProcAddress(m_hEzdDLL, "E3_MoveEntToIndex");
#else
        E3_MoveEntToIndex = (e3_MoveEntToIndex)dlsym(m_hEzdDLL, "E3_MoveEntToIndex");
#endif
        if (E3_MoveEntToIndex == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_MoveEntToIndex in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_MoveEntZ = (e3_MoveEntZ)GetProcAddress(m_hEzdDLL, "E3_MoveEntZ");
#else
        E3_MoveEntZ = (e3_MoveEntZ)dlsym(m_hEzdDLL, "E3_MoveEntZ");
#endif
        if (E3_MoveEntZ == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_MoveEntZ in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_MoveRotateEnt = (e3_MoveRotateEnt)GetProcAddress(m_hEzdDLL, "E3_MoveRotateEnt");
#else
        E3_MoveRotateEnt = (e3_MoveRotateEnt)dlsym(m_hEzdDLL, "E3_MoveRotateEnt");
#endif
        if (E3_MoveRotateEnt == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_MoveRotateEnt in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_ProjectEnt_2 = (e3_ProjectEnt_2)GetProcAddress(m_hEzdDLL, "E3_ProjectEnt_2");
#else
        E3_ProjectEnt_2 = (e3_ProjectEnt_2)dlsym(m_hEzdDLL, "E3_ProjectEnt_2");
#endif
        if (E3_ProjectEnt_2 == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_ProjectEnt_2 in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_SaveEntMgrToFile = (e3_SaveEntMgrToFile)GetProcAddress(m_hEzdDLL, "E3_SaveEntMgrToFile");
#else
        E3_SaveEntMgrToFile = (e3_SaveEntMgrToFile)dlsym(m_hEzdDLL, "E3_SaveEntMgrToFile");
#endif
        if (E3_SaveEntMgrToFile == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_SaveEntMgrToFile in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_SaveMotionMgrParamToFile = (e3_SaveMotionMgrParamToFile)GetProcAddress(m_hEzdDLL, "E3_SaveMotionMgrParamToFile");
#else
        E3_SaveMotionMgrParamToFile = (e3_SaveMotionMgrParamToFile)dlsym(m_hEzdDLL, "E3_SaveMotionMgrParamToFile");
#endif
        if (E3_SaveMotionMgrParamToFile == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_SaveMotionMgrParamToFile in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_SetHatchParam = (e3_SetHatchParam)GetProcAddress(m_hEzdDLL, "E3_SetHatchParam");
#else
        E3_SetHatchParam = (e3_SetHatchParam)dlsym(m_hEzdDLL, "E3_SetHatchParam");
#endif
        if (E3_SetHatchParam == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_SetHatchParam in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_SetHatchParam2 = (e3_SetHatchParam2)GetProcAddress(m_hEzdDLL, "E3_SetHatchParam2");
#else
        E3_SetHatchParam2 = (e3_SetHatchParam2)dlsym(m_hEzdDLL, "E3_SetHatchParam2");
#endif
        if (E3_SetHatchParam2 == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_SetHatchParam2 in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_SetMultiCardSyn = (e3_SetMultiCardSyn)GetProcAddress(m_hEzdDLL, "E3_SetMultiCardSyn");
#else
        E3_SetMultiCardSyn = (e3_SetMultiCardSyn)dlsym(m_hEzdDLL, "E3_SetMultiCardSyn");
#endif
        if (E3_SetMultiCardSyn == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_SetMultiCardSyn in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_SetMultiCardSynEveryCurve = (e3_SetMultiCardSynEveryCurve)GetProcAddress(m_hEzdDLL, "E3_SetMultiCardSynEveryCurve");
#else
        E3_SetMultiCardSynEveryCurve = (e3_SetMultiCardSynEveryCurve)dlsym(m_hEzdDLL, "E3_SetMultiCardSynEveryCurve");
#endif
        if (E3_SetMultiCardSynEveryCurve == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_SetMultiCardSynEveryCurve in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_SetMultiCardSynWhenFinish = (e3_SetMultiCardSynWhenFinish)GetProcAddress(m_hEzdDLL, "E3_SetMultiCardSynWhenFinish");
#else
        E3_SetMultiCardSynWhenFinish = (e3_SetMultiCardSynWhenFinish)dlsym(m_hEzdDLL, "E3_SetMultiCardSynWhenFinish");
#endif
        if (E3_SetMultiCardSynWhenFinish == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_SetMultiCardSynWhenFinish in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_SliceStlFile = (e3_SliceStlFile)GetProcAddress(m_hEzdDLL, "E3_SliceStlFile");
#else
        E3_SliceStlFile = (e3_SliceStlFile)dlsym(m_hEzdDLL, "E3_SliceStlFile");
#endif
        if (E3_SliceStlFile == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_SliceStlFile in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_SliceStlFile2 = (e3_SliceStlFile2)GetProcAddress(m_hEzdDLL, "E3_SliceStlFile2");
#else
        E3_SliceStlFile2 = (e3_SliceStlFile2)dlsym(m_hEzdDLL, "E3_SliceStlFile2");
#endif
        if (E3_SliceStlFile2 == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_SliceStlFile2 in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_GetAllEntCount = (e3_GetAllEntCount)GetProcAddress(m_hEzdDLL, "E3_GetAllEntCount");
#else
        E3_GetAllEntCount = (e3_GetAllEntCount)dlsym(m_hEzdDLL, "E3_GetAllEntCount");
#endif
        if (E3_GetAllEntCount == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_GetAllEntCount in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_SetCurLayer = (e3_SetCurLayer)GetProcAddress(m_hEzdDLL, "E3_SetCurLayer");
#else
        E3_SetCurLayer = (e3_SetCurLayer)dlsym(m_hEzdDLL, "E3_SetCurLayer");
#endif
        if (E3_SetCurLayer == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_SetCurLayer in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_SetEntTextInfo = (e3_SetEntTextInfo)GetProcAddress(m_hEzdDLL, "E3_SetEntTextInfo");
#else
        E3_SetEntTextInfo = (e3_SetEntTextInfo)dlsym(m_hEzdDLL, "E3_SetEntTextInfo");
#endif
        if (E3_SetEntTextInfo == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_SetEntTextInfo in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_SetEntTextInfo_2 = (e3_SetEntTextInfo_2)GetProcAddress(m_hEzdDLL, "E3_SetEntTextInfo_2");
#else
        E3_SetEntTextInfo_2 = (e3_SetEntTextInfo_2)dlsym(m_hEzdDLL, "E3_SetEntTextInfo_2");
#endif
        if (E3_SetEntTextInfo_2 == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_SetEntTextInfo_2 in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_SetEntPen = (e3_SetEntPen)GetProcAddress(m_hEzdDLL, "E3_SetEntPen");
#else
        E3_SetEntPen = (e3_SetEntPen)dlsym(m_hEzdDLL, "E3_SetEntPen");
#endif
        if (E3_SetEntPen == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_SetEntPen in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_SetEntPen2 = (e3_SetEntPen2)GetProcAddress(m_hEzdDLL, "E3_SetEntPen2");
#else
        E3_SetEntPen2 = (e3_SetEntPen2)dlsym(m_hEzdDLL, "E3_SetEntPen2");
#endif
        if (E3_SetEntPen2 == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_SetEntPen2 in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_SetEntityZ = (e3_SetEntityZ)GetProcAddress(m_hEzdDLL, "E3_SetEntityZ");
#else
        E3_SetEntityZ = (e3_SetEntityZ)dlsym(m_hEzdDLL, "E3_SetEntityZ");
#endif
        if (E3_SetEntityZ == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_SetEntityZ in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_SetEntityA = (e3_SetEntityA)GetProcAddress(m_hEzdDLL, "E3_SetEntityA");
#else
        E3_SetEntityA = (e3_SetEntityA)dlsym(m_hEzdDLL, "E3_SetEntityA");
#endif
        if (E3_SetEntityA == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_SetEntityA in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_SetEntityName = (e3_SetEntityName)GetProcAddress(m_hEzdDLL, "E3_SetEntityName");
#else
        E3_SetEntityName = (e3_SetEntityName)dlsym(m_hEzdDLL, "E3_SetEntityName");
#endif
        if (E3_SetEntityName == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_SetEntityName in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_MarkerGetState = (e3_MarkerGetState)GetProcAddress(m_hEzdDLL, "E3_MarkerGetState");
#else
        E3_MarkerGetState = (e3_MarkerGetState)dlsym(m_hEzdDLL, "E3_MarkerGetState");
#endif
        if (E3_MarkerGetState == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_MarkerGetState in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_MarkerGetRange = (e3_MarkerGetRange)GetProcAddress(m_hEzdDLL, "E3_MarkerGetRange");
#else
        E3_MarkerGetRange = (e3_MarkerGetRange)dlsym(m_hEzdDLL, "E3_MarkerGetRange");
#endif
        if (E3_MarkerGetRange == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_MarkerGetRange in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_MarkerGetMarkCount = (e3_MarkerGetMarkCount)GetProcAddress(m_hEzdDLL, "E3_MarkerGetMarkCount");
#else
        E3_MarkerGetMarkCount = (e3_MarkerGetMarkCount)dlsym(m_hEzdDLL, "E3_MarkerGetMarkCount");
#endif
        if (E3_MarkerGetMarkCount == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_MarkerGetMarkCount in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_MarkerGetHardInfo = (e3_MarkerGetHardInfo)GetProcAddress(m_hEzdDLL, "E3_MarkerGetHardInfo");
#else
        E3_MarkerGetHardInfo = (e3_MarkerGetHardInfo)dlsym(m_hEzdDLL, "E3_MarkerGetHardInfo");
#endif
        if (E3_MarkerGetHardInfo == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_MarkerGetHardInfo in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_MarkerGetCalcMarkTime = (e3_MarkerGetCalcMarkTime)GetProcAddress(m_hEzdDLL, "E3_MarkerGetCalcMarkTime");
#else
        E3_MarkerGetCalcMarkTime = (e3_MarkerGetCalcMarkTime)dlsym(m_hEzdDLL, "E3_MarkerGetCalcMarkTime");
#endif
        if (E3_MarkerGetCalcMarkTime == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_MarkerGetCalcMarkTime in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_GetTextInfo = (e3_GetTextInfo)GetProcAddress(m_hEzdDLL, "E3_GetTextInfo");
#else
        E3_GetTextInfo = (e3_GetTextInfo)dlsym(m_hEzdDLL, "E3_GetTextInfo");
#endif
        if (E3_GetTextInfo == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_GetTextInfo in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_GetTextStringInfo = (e3_GetTextStringInfo)GetProcAddress(m_hEzdDLL, "E3_GetTextStringInfo");
#else
        E3_GetTextStringInfo = (e3_GetTextStringInfo)dlsym(m_hEzdDLL, "E3_GetTextStringInfo");
#endif
        if (E3_GetTextStringInfo == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_GetTextStringInfo in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_GetMarkerSN = (e3_GetMarkerSN)GetProcAddress(m_hEzdDLL, "E3_GetMarkerSN");
#else
        E3_GetMarkerSN = (e3_GetMarkerSN)dlsym(m_hEzdDLL, "E3_GetMarkerSN");
#endif
        if (E3_GetMarkerSN == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_GetMarkerSN in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_GetEntityRange = (e3_GetEntityRange)GetProcAddress(m_hEzdDLL, "E3_GetEntityRange");
#else
        E3_GetEntityRange = (e3_GetEntityRange)dlsym(m_hEzdDLL, "E3_GetEntityRange");
#endif
        if (E3_GetEntityRange == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_GetEntityRange in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_GetEntityName = (e3_GetEntityName)GetProcAddress(m_hEzdDLL, "E3_GetEntityName");
#else
        E3_GetEntityName = (e3_GetEntityName)dlsym(m_hEzdDLL, "E3_GetEntityName");
#endif
        if (E3_GetEntityName == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_GetEntityName in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_GetEntCountInLayer = (e3_GetEntCountInLayer)GetProcAddress(m_hEzdDLL, "E3_GetEntCountInLayer");
#else
        E3_GetEntCountInLayer = (e3_GetEntCountInLayer)dlsym(m_hEzdDLL, "E3_GetEntCountInLayer");
#endif
        if (E3_GetEntCountInLayer == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_GetEntCountInLayer in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_GetEntChildCount = (e3_GetEntChildCount)GetProcAddress(m_hEzdDLL, "E3_GetEntChildCount");
#else
        E3_GetEntChildCount = (e3_GetEntChildCount)dlsym(m_hEzdDLL, "E3_GetEntChildCount");
#endif
        if (E3_GetEntChildCount == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_GetEntChildCount in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_GetEntBaseInfo = (e3_GetEntBaseInfo)GetProcAddress(m_hEzdDLL, "E3_GetEntBaseInfo");
#else
        E3_GetEntBaseInfo = (e3_GetEntBaseInfo)dlsym(m_hEzdDLL, "E3_GetEntBaseInfo");
#endif
        if (E3_GetEntBaseInfo == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_GetEntBaseInfo in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_AutoConnectChildCurve = (e3_AutoConnectChildCurve)GetProcAddress(m_hEzdDLL, "E3_AutoConnectChildCurve");
#else
        E3_AutoConnectChildCurve = (e3_AutoConnectChildCurve)dlsym(m_hEzdDLL, "E3_AutoConnectChildCurve");
#endif
        if (E3_AutoConnectChildCurve == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_AutoConnectChildCurve in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_AutoBreakCrossEntChilds = (e3_AutoBreakCrossEntChilds)GetProcAddress(m_hEzdDLL, "E3_AutoBreakCrossEntChilds");
#else
        E3_AutoBreakCrossEntChilds = (e3_AutoBreakCrossEntChilds)dlsym(m_hEzdDLL, "E3_AutoBreakCrossEntChilds");
#endif
        if (E3_AutoBreakCrossEntChilds == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_AutoBreakCrossEntChilds in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_AddEntityToOther = (e3_AddEntityToOther)GetProcAddress(m_hEzdDLL, "E3_AddEntityToOther");
#else
        E3_AddEntityToOther = (e3_AddEntityToOther)dlsym(m_hEzdDLL, "E3_AddEntityToOther");
#endif
        if (E3_AddEntityToOther == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_AddEntityToOther in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_AddEntityToChild = (e3_AddEntityToChild)GetProcAddress(m_hEzdDLL, "E3_AddEntityToChild");
#else
        E3_AddEntityToChild = (e3_AddEntityToChild)dlsym(m_hEzdDLL, "E3_AddEntityToChild");
#endif
        if (E3_AddEntityToChild == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_AddEntityToChild in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_MarkCrossLines = (e3_MarkCrossLines)GetProcAddress(m_hEzdDLL, "E3_MarkCrossLines");
#else
        E3_MarkCrossLines = (e3_MarkCrossLines)dlsym(m_hEzdDLL, "E3_MarkCrossLines");
#endif
        if (E3_MarkCrossLines == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_MarkCrossLines in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_FreeEntity = (e3_FreeEntity)GetProcAddress(m_hEzdDLL, "E3_FreeEntity");
#else
        E3_FreeEntity = (e3_FreeEntity)dlsym(m_hEzdDLL, "E3_FreeEntity");
#endif
        if (E3_FreeEntity == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_FreeEntity in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_CreateLines3d_2 = (e3_CreateLines3d_2)GetProcAddress(m_hEzdDLL, "E3_CreateLines3d_2");
#else
        E3_CreateLines3d_2 = (e3_CreateLines3d_2)dlsym(m_hEzdDLL, "E3_CreateLines3d_2");
#endif
        if (E3_CreateLines3d_2 == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_CreateLines3d_2 in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_CreateLines3d = (e3_CreateLines3d)GetProcAddress(m_hEzdDLL, "E3_CreateLines3d");
#else
        E3_CreateLines3d = (e3_CreateLines3d)dlsym(m_hEzdDLL, "E3_CreateLines3d");
#endif
        if (E3_CreateLines3d == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_CreateLines3d in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_CreateSvgPath = (e3_CreateSvgPath)GetProcAddress(m_hEzdDLL, "E3_CreateSvgPath");
#else
        E3_CreateSvgPath = (e3_CreateSvgPath)dlsym(m_hEzdDLL, "E3_CreateSvgPath");
#endif
        if (E3_CreateSvgPath == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_CreateSvgPath in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_CreateSvgPath_2 = (e3_CreateSvgPath_2)GetProcAddress(m_hEzdDLL, "E3_CreateSvgPath_2");
#else
        E3_CreateSvgPath_2 = (e3_CreateSvgPath_2)dlsym(m_hEzdDLL, "E3_CreateSvgPath_2");
#endif
        if (E3_CreateSvgPath_2 == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_CreateSvgPath_2 in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_EthConvertStringToIP = (e3_EthConvertStringToIP)GetProcAddress(m_hEzdDLL, "E3_EthConvertStringToIP");
#else
        E3_EthConvertStringToIP = (e3_EthConvertStringToIP)dlsym(m_hEzdDLL, "E3_EthConvertStringToIP");
#endif
        if (E3_EthConvertStringToIP == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_EthConvertStringToIP in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_EthRegisterCardByIP = (e3_EthRegisterCardByIP)GetProcAddress(m_hEzdDLL, "E3_EthRegisterCardByIP");
#else
        E3_EthRegisterCardByIP = (e3_EthRegisterCardByIP)dlsym(m_hEzdDLL, "E3_EthRegisterCardByIP");
#endif
        if (E3_EthRegisterCardByIP == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_EthRegisterCardByIP in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_GetProjectEntParam = (e3_GetProjectEntParam)GetProcAddress(m_hEzdDLL, "E3_GetProjectEntParam");
#else
        E3_GetProjectEntParam = (e3_GetProjectEntParam)dlsym(m_hEzdDLL, "E3_GetProjectEntParam");
#endif
        if (E3_GetProjectEntParam == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_GetProjectEntParam in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_MarkerPointsToList = (e3_MarkerPointsToList)GetProcAddress(m_hEzdDLL, "E3_MarkerPointsToList");
#else
        E3_MarkerPointsToList = (e3_MarkerPointsToList)dlsym(m_hEzdDLL, "E3_MarkerPointsToList");
#endif
        if (E3_MarkerPointsToList == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_MarkerPointsToList in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_MarkerResetLaserError = (e3_MarkerResetLaserError)GetProcAddress(m_hEzdDLL, "E3_MarkerResetLaserError");
#else
        E3_MarkerResetLaserError = (e3_MarkerResetLaserError)dlsym(m_hEzdDLL, "E3_MarkerResetLaserError");
#endif
        if (E3_MarkerResetLaserError == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_MarkerResetLaserError in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_MarkerSaveCfg = (e3_MarkerSaveCfg)GetProcAddress(m_hEzdDLL, "E3_MarkerSaveCfg");
#else
        E3_MarkerSaveCfg = (e3_MarkerSaveCfg)dlsym(m_hEzdDLL, "E3_MarkerSaveCfg");
#endif
        if (E3_MarkerSaveCfg == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_MarkerSaveCfg in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_MarkerSetInputJumpIndexToList = (e3_MarkerSetInputJumpIndexToList)GetProcAddress(m_hEzdDLL, "E3_MarkerSetInputJumpIndexToList");
#else
        E3_MarkerSetInputJumpIndexToList = (e3_MarkerSetInputJumpIndexToList)dlsym(m_hEzdDLL, "E3_MarkerSetInputJumpIndexToList");
#endif
        if (E3_MarkerSetInputJumpIndexToList == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_MarkerSetInputJumpIndexToList in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_ProjectEnt = (e3_ProjectEnt)GetProcAddress(m_hEzdDLL, "E3_ProjectEnt");
#else
        E3_ProjectEnt = (e3_ProjectEnt)dlsym(m_hEzdDLL, "E3_ProjectEnt");
#endif
        if (E3_ProjectEnt == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_ProjectEnt in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_ProjectEntDelete = (e3_ProjectEntDelete)GetProcAddress(m_hEzdDLL, "E3_ProjectEntDelete");
#else
        E3_ProjectEntDelete = (e3_ProjectEntDelete)dlsym(m_hEzdDLL, "E3_ProjectEntDelete");
#endif
        if (E3_ProjectEntDelete == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_ProjectEntDelete in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_SetProjectEntParam = (e3_SetProjectEntParam)GetProcAddress(m_hEzdDLL, "E3_SetProjectEntParam");
#else
        E3_SetProjectEntParam = (e3_SetProjectEntParam)dlsym(m_hEzdDLL, "E3_SetProjectEntParam");
#endif
        if (E3_SetProjectEntParam == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_SetProjectEntParam in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_WSAStartUp = (e3_WSAStartUp)GetProcAddress(m_hEzdDLL, "E3_WSAStartUp");
#else
        E3_WSAStartUp = (e3_WSAStartUp)dlsym(m_hEzdDLL, "E3_WSAStartUp");
#endif
        if (E3_WSAStartUp == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_WSAStartUp in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_AddLayer = (e3_AddLayer)GetProcAddress(m_hEzdDLL, "E3_AddLayer");
#else
        E3_AddLayer = (e3_AddLayer)dlsym(m_hEzdDLL, "E3_AddLayer");
#endif
        if (E3_AddLayer == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_AddLayer in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_AddNewLayer = (e3_AddNewLayer)GetProcAddress(m_hEzdDLL, "E3_AddNewLayer");
#else
        E3_AddNewLayer = (e3_AddNewLayer)dlsym(m_hEzdDLL, "E3_AddNewLayer");
#endif
        if (E3_AddNewLayer == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_AddNewLayer in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_AutoReduceCurvePt = (e3_AutoReduceCurvePt)GetProcAddress(m_hEzdDLL, "E3_AutoReduceCurvePt");
#else
        E3_AutoReduceCurvePt = (e3_AutoReduceCurvePt)dlsym(m_hEzdDLL, "E3_AutoReduceCurvePt");
#endif
        if (E3_AutoReduceCurvePt == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_AutoReduceCurvePt in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_CloseMarker = (e3_CloseMarker)GetProcAddress(m_hEzdDLL, "E3_CloseMarker");
#else
        E3_CloseMarker = (e3_CloseMarker)dlsym(m_hEzdDLL, "E3_CloseMarker");
#endif
        if (E3_CloseMarker == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_CloseMarker in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_CopyEntity = (e3_CopyEntity)GetProcAddress(m_hEzdDLL, "E3_CopyEntity");
#else
        E3_CopyEntity = (e3_CopyEntity)dlsym(m_hEzdDLL, "E3_CopyEntity");
#endif
        if (E3_CopyEntity == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_CopyEntity in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_CreateCircle = (e3_CreateCircle)GetProcAddress(m_hEzdDLL, "E3_CreateCircle");
#else
        E3_CreateCircle = (e3_CreateCircle)dlsym(m_hEzdDLL, "E3_CreateCircle");
#endif
        if (E3_CreateCircle == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_CreateCircle in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_CreateCircle_2 = (e3_CreateCircle_2)GetProcAddress(m_hEzdDLL, "E3_CreateCircle_2");
#else
        E3_CreateCircle_2 = (e3_CreateCircle_2)dlsym(m_hEzdDLL, "E3_CreateCircle_2");
#endif
        if (E3_CreateCircle_2 == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_CreateCircle_2 in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_CreateControl = (e3_CreateControl)GetProcAddress(m_hEzdDLL, "E3_CreateControl");
#else
        E3_CreateControl = (e3_CreateControl)dlsym(m_hEzdDLL, "E3_CreateControl");
#endif
        if (E3_CreateControl == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_CreateControl in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_CreateControl_2 = (e3_CreateControl_2)GetProcAddress(m_hEzdDLL, "E3_CreateControl_2");
#else
        E3_CreateControl_2 = (e3_CreateControl_2)dlsym(m_hEzdDLL, "E3_CreateControl_2");
#endif
        if (E3_CreateControl_2 == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_CreateControl_2 in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_CreateEllipse = (e3_CreateEllipse)GetProcAddress(m_hEzdDLL, "E3_CreateEllipse");
#else
        E3_CreateEllipse = (e3_CreateEllipse)dlsym(m_hEzdDLL, "E3_CreateEllipse");
#endif
        if (E3_CreateEllipse == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_CreateEllipse in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_CreateEllipse_2 = (e3_CreateEllipse_2)GetProcAddress(m_hEzdDLL, "E3_CreateEllipse_2");
#else
        E3_CreateEllipse_2 = (e3_CreateEllipse_2)dlsym(m_hEzdDLL, "E3_CreateEllipse_2");
#endif
        if (E3_CreateEllipse_2 == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_CreateEllipse_2 in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_CreateLines = (e3_CreateLines)GetProcAddress(m_hEzdDLL, "E3_CreateLines");
#else
        E3_CreateLines = (e3_CreateLines)dlsym(m_hEzdDLL, "E3_CreateLines");
#endif
        if (E3_CreateLines == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_CreateLines in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_CreateLines_2 = (e3_CreateLines_2)GetProcAddress(m_hEzdDLL, "E3_CreateLines_2");
#else
        E3_CreateLines_2 = (e3_CreateLines_2)dlsym(m_hEzdDLL, "E3_CreateLines_2");
#endif
        if (E3_CreateLines_2 == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_CreateLines_2 in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_CreatePoints = (e3_CreatePoints)GetProcAddress(m_hEzdDLL, "E3_CreatePoints");
#else
        E3_CreatePoints = (e3_CreatePoints)dlsym(m_hEzdDLL, "E3_CreatePoints");
#endif
        if (E3_CreatePoints == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_CreatePoints in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_CreatePoints_2 = (e3_CreatePoints_2)GetProcAddress(m_hEzdDLL, "E3_CreatePoints_2");
#else
        E3_CreatePoints_2 = (e3_CreatePoints_2)dlsym(m_hEzdDLL, "E3_CreatePoints_2");
#endif
        if (E3_CreatePoints_2 == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_CreatePoints_2 in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_CreatePolygon = (e3_CreatePolygon)GetProcAddress(m_hEzdDLL, "E3_CreatePolygon");
#else
        E3_CreatePolygon = (e3_CreatePolygon)dlsym(m_hEzdDLL, "E3_CreatePolygon");
#endif
        if (E3_CreatePolygon == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_CreatePolygon in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_CreatePolygon_2 = (e3_CreatePolygon_2)GetProcAddress(m_hEzdDLL, "E3_CreatePolygon_2");
#else
        E3_CreatePolygon_2 = (e3_CreatePolygon_2)dlsym(m_hEzdDLL, "E3_CreatePolygon_2");
#endif
        if (E3_CreatePolygon_2 == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_CreatePolygon_2 in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_CreateRect = (e3_CreateRect)GetProcAddress(m_hEzdDLL, "E3_CreateRect");
#else
        E3_CreateRect = (e3_CreateRect)dlsym(m_hEzdDLL, "E3_CreateRect");
#endif
        if (E3_CreateRect == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_CreateRect in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_CreateRect_2 = (e3_CreateRect_2)GetProcAddress(m_hEzdDLL, "E3_CreateRect_2");
#else
        E3_CreateRect_2 = (e3_CreateRect_2)dlsym(m_hEzdDLL, "E3_CreateRect_2");
#endif
        if (E3_CreateRect_2 == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_CreateRect_2 in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_CreateSpiral = (e3_CreateSpiral)GetProcAddress(m_hEzdDLL, "E3_CreateSpiral");
#else
        E3_CreateSpiral = (e3_CreateSpiral)dlsym(m_hEzdDLL, "E3_CreateSpiral");
#endif
        if (E3_CreateSpiral == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_CreateSpiral in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_CreateSpiral_2 = (e3_CreateSpiral_2)GetProcAddress(m_hEzdDLL, "E3_CreateSpiral_2");
#else
        E3_CreateSpiral_2 = (e3_CreateSpiral_2)dlsym(m_hEzdDLL, "E3_CreateSpiral_2");
#endif
        if (E3_CreateSpiral_2 == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_CreateSpiral_2 in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_CreateText = (e3_CreateText)GetProcAddress(m_hEzdDLL, "E3_CreateText");
#else
        E3_CreateText = (e3_CreateText)dlsym(m_hEzdDLL, "E3_CreateText");
#endif
        if (E3_CreateText == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_CreateText in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_CreateText_2 = (e3_CreateText_2)GetProcAddress(m_hEzdDLL, "E3_CreateText_2");
#else
        E3_CreateText_2 = (e3_CreateText_2)dlsym(m_hEzdDLL, "E3_CreateText_2");
#endif
        if (E3_CreateText_2 == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_CreateText_2 in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_GetCurLayerId = (e3_GetCurLayerId)GetProcAddress(m_hEzdDLL, "E3_GetCurLayerId");
#else
        E3_GetCurLayerId = (e3_GetCurLayerId)dlsym(m_hEzdDLL, "E3_GetCurLayerId");
#endif
        if (E3_GetCurLayerId == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_GetCurLayerId in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_GetLayerCount = (e3_GetLayerCount)GetProcAddress(m_hEzdDLL, "E3_GetLayerCount");
#else
        E3_GetLayerCount = (e3_GetLayerCount)dlsym(m_hEzdDLL, "E3_GetLayerCount");
#endif
        if (E3_GetLayerCount == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_GetLayerCount in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_GetLayerId = (e3_GetLayerId)GetProcAddress(m_hEzdDLL, "E3_GetLayerId");
#else
        E3_GetLayerId = (e3_GetLayerId)dlsym(m_hEzdDLL, "E3_GetLayerId");
#endif
        if (E3_GetLayerId == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_GetLayerId in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_ImportFileToEntMgr = (e3_ImportFileToEntMgr)GetProcAddress(m_hEzdDLL, "E3_ImportFileToEntMgr");
#else
        E3_ImportFileToEntMgr = (e3_ImportFileToEntMgr)dlsym(m_hEzdDLL, "E3_ImportFileToEntMgr");
#endif
        if (E3_ImportFileToEntMgr == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_ImportFileToEntMgr in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_ImportFileToEntMgr_2 = (e3_ImportFileToEntMgr_2)GetProcAddress(m_hEzdDLL, "E3_ImportFileToEntMgr_2");
#else
        E3_ImportFileToEntMgr_2 = (e3_ImportFileToEntMgr_2)dlsym(m_hEzdDLL, "E3_ImportFileToEntMgr_2");
#endif
        if (E3_ImportFileToEntMgr_2 == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_ImportFileToEntMgr_2 in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_MarkerArcMarkToPtList = (e3_MarkerArcMarkToPtList)GetProcAddress(m_hEzdDLL, "E3_MarkerArcMarkToPtList");
#else
        E3_MarkerArcMarkToPtList = (e3_MarkerArcMarkToPtList)dlsym(m_hEzdDLL, "E3_MarkerArcMarkToPtList");
#endif
        if (E3_MarkerArcMarkToPtList == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_MarkerArcMarkToPtList in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_MarkerBasicJumpToPtList = (e3_MarkerBasicJumpToPtList)GetProcAddress(m_hEzdDLL, "E3_MarkerBasicJumpToPtList");
#else
        E3_MarkerBasicJumpToPtList = (e3_MarkerBasicJumpToPtList)dlsym(m_hEzdDLL, "E3_MarkerBasicJumpToPtList");
#endif
        if (E3_MarkerBasicJumpToPtList == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_MarkerBasicJumpToPtList in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_MarkerBasicMarkToPtList = (e3_MarkerBasicMarkToPtList)GetProcAddress(m_hEzdDLL, "E3_MarkerBasicMarkToPtList");
#else
        E3_MarkerBasicMarkToPtList = (e3_MarkerBasicMarkToPtList)dlsym(m_hEzdDLL, "E3_MarkerBasicMarkToPtList");
#endif
        if (E3_MarkerBasicMarkToPtList == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_MarkerBasicMarkToPtList in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_MarkerBasicSetPenList = (e3_MarkerBasicSetPenList)GetProcAddress(m_hEzdDLL, "E3_MarkerBasicSetPenList");
#else
        E3_MarkerBasicSetPenList = (e3_MarkerBasicSetPenList)dlsym(m_hEzdDLL, "E3_MarkerBasicSetPenList");
#endif
        if (E3_MarkerBasicSetPenList == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_MarkerBasicSetPenList in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_MarkerCheckLaserState = (e3_MarkerCheckLaserState)GetProcAddress(m_hEzdDLL, "E3_MarkerCheckLaserState");
#else
        E3_MarkerCheckLaserState = (e3_MarkerCheckLaserState)dlsym(m_hEzdDLL, "E3_MarkerCheckLaserState");
#endif
        if (E3_MarkerCheckLaserState == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_MarkerCheckLaserState in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_MarkerContinueBufferAdd = (e3_MarkerContinueBufferAdd)GetProcAddress(m_hEzdDLL, "E3_MarkerContinueBufferAdd");
#else
        E3_MarkerContinueBufferAdd = (e3_MarkerContinueBufferAdd)dlsym(m_hEzdDLL, "E3_MarkerContinueBufferAdd");
#endif
        if (E3_MarkerContinueBufferAdd == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_MarkerContinueBufferAdd in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_MarkerContinueBufferClear = (e3_MarkerContinueBufferClear)GetProcAddress(m_hEzdDLL, "E3_MarkerContinueBufferClear");
#else
        E3_MarkerContinueBufferClear = (e3_MarkerContinueBufferClear)dlsym(m_hEzdDLL, "E3_MarkerContinueBufferClear");
#endif
        if (E3_MarkerContinueBufferClear == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_MarkerContinueBufferClear in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_MarkerContinueBufferGetParam = (e3_MarkerContinueBufferGetParam)GetProcAddress(m_hEzdDLL, "E3_MarkerContinueBufferGetParam");
#else
        E3_MarkerContinueBufferGetParam = (e3_MarkerContinueBufferGetParam)dlsym(m_hEzdDLL, "E3_MarkerContinueBufferGetParam");
#endif
        if (E3_MarkerContinueBufferGetParam == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_MarkerContinueBufferGetParam in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_MarkerContinueBufferPartFinish = (e3_MarkerContinueBufferPartFinish)GetProcAddress(m_hEzdDLL, "E3_MarkerContinueBufferPartFinish");
#else
        E3_MarkerContinueBufferPartFinish = (e3_MarkerContinueBufferPartFinish)dlsym(m_hEzdDLL, "E3_MarkerContinueBufferPartFinish");
#endif
        if (E3_MarkerContinueBufferPartFinish == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_MarkerContinueBufferPartFinish in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_MarkerContinueBufferSetTextName = (e3_MarkerContinueBufferSetTextName)GetProcAddress(m_hEzdDLL, "E3_MarkerContinueBufferSetTextName");
#else
        E3_MarkerContinueBufferSetTextName = (e3_MarkerContinueBufferSetTextName)dlsym(m_hEzdDLL, "E3_MarkerContinueBufferSetTextName");
#endif
        if (E3_MarkerContinueBufferSetTextName == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_MarkerContinueBufferSetTextName in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_MarkerContinueBufferStart = (e3_MarkerContinueBufferStart)GetProcAddress(m_hEzdDLL, "E3_MarkerContinueBufferStart");
#else
        E3_MarkerContinueBufferStart = (e3_MarkerContinueBufferStart)dlsym(m_hEzdDLL, "E3_MarkerContinueBufferStart");
#endif
        if (E3_MarkerContinueBufferStart == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_MarkerContinueBufferStart in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_MarkerDoLoopToList = (e3_MarkerDoLoopToList)GetProcAddress(m_hEzdDLL, "E3_MarkerDoLoopToList");
#else
        E3_MarkerDoLoopToList = (e3_MarkerDoLoopToList)dlsym(m_hEzdDLL, "E3_MarkerDoLoopToList");
#endif
        if (E3_MarkerDoLoopToList == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_MarkerDoLoopToList in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_MarkerEnableOffLineMode = (e3_MarkerEnableOffLineMode)GetProcAddress(m_hEzdDLL, "E3_MarkerEnableOffLineMode");
#else
        E3_MarkerEnableOffLineMode = (e3_MarkerEnableOffLineMode)dlsym(m_hEzdDLL, "E3_MarkerEnableOffLineMode");
#endif
        if (E3_MarkerEnableOffLineMode == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_MarkerEnableOffLineMode in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_MarkerExecuteAndWaitFinish = (e3_MarkerExecuteAndWaitFinish)GetProcAddress(m_hEzdDLL, "E3_MarkerExecuteAndWaitFinish");
#else
        E3_MarkerExecuteAndWaitFinish = (e3_MarkerExecuteAndWaitFinish)dlsym(m_hEzdDLL, "E3_MarkerExecuteAndWaitFinish");
#endif
        if (E3_MarkerExecuteAndWaitFinish == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_MarkerExecuteAndWaitFinish in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_MarkerGetBoardRunningStatus = (e3_MarkerGetBoardRunningStatus)GetProcAddress(m_hEzdDLL, "E3_MarkerGetBoardRunningStatus");
#else
        E3_MarkerGetBoardRunningStatus = (e3_MarkerGetBoardRunningStatus)dlsym(m_hEzdDLL, "E3_MarkerGetBoardRunningStatus");
#endif
        if (E3_MarkerGetBoardRunningStatus == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_MarkerGetBoardRunningStatus in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_MarkerGetLaserState = (e3_MarkerGetLaserState)GetProcAddress(m_hEzdDLL, "E3_MarkerGetLaserState");
#else
        E3_MarkerGetLaserState = (e3_MarkerGetLaserState)dlsym(m_hEzdDLL, "E3_MarkerGetLaserState");
#endif
        if (E3_MarkerGetLaserState == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_MarkerGetLaserState in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_MarkerGetListTotalCount = (e3_MarkerGetListTotalCount)GetProcAddress(m_hEzdDLL, "E3_MarkerGetListTotalCount");
#else
        E3_MarkerGetListTotalCount = (e3_MarkerGetListTotalCount)dlsym(m_hEzdDLL, "E3_MarkerGetListTotalCount");
#endif
        if (E3_MarkerGetListTotalCount == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_MarkerGetListTotalCount in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_MarkerGetMakingTime = (e3_MarkerGetMakingTime)GetProcAddress(m_hEzdDLL, "E3_MarkerGetMakingTime");
#else
        E3_MarkerGetMakingTime = (e3_MarkerGetMakingTime)dlsym(m_hEzdDLL, "E3_MarkerGetMakingTime");
#endif
        if (E3_MarkerGetMakingTime == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_MarkerGetMakingTime in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_MarkerGetPos = (e3_MarkerGetPos)GetProcAddress(m_hEzdDLL, "E3_MarkerGetPos");
#else
        E3_MarkerGetPos = (e3_MarkerGetPos)dlsym(m_hEzdDLL, "E3_MarkerGetPos");
#endif
        if (E3_MarkerGetPos == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_MarkerGetPos in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_MarkerOffLineModeStart = (e3_MarkerOffLineModeStart)GetProcAddress(m_hEzdDLL, "E3_MarkerOffLineModeStart");
#else
        E3_MarkerOffLineModeStart = (e3_MarkerOffLineModeStart)dlsym(m_hEzdDLL, "E3_MarkerOffLineModeStart");
#endif
        if (E3_MarkerOffLineModeStart == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_MarkerOffLineModeStart in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_MarkerOffLineModeStop = (e3_MarkerOffLineModeStop)GetProcAddress(m_hEzdDLL, "E3_MarkerOffLineModeStop");
#else
        E3_MarkerOffLineModeStop = (e3_MarkerOffLineModeStop)dlsym(m_hEzdDLL, "E3_MarkerOffLineModeStop");
#endif
        if (E3_MarkerOffLineModeStop == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_MarkerOffLineModeStop in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_MarkerRestartList = (e3_MarkerRestartList)GetProcAddress(m_hEzdDLL, "E3_MarkerRestartList");
#else
        E3_MarkerRestartList = (e3_MarkerRestartList)dlsym(m_hEzdDLL, "E3_MarkerRestartList");
#endif
        if (E3_MarkerRestartList == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_MarkerRestartList in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_MarkerSendOfflineMainProgram = (e3_MarkerSendOfflineMainProgram)GetProcAddress(m_hEzdDLL, "E3_MarkerSendOfflineMainProgram");
#else
        E3_MarkerSendOfflineMainProgram = (e3_MarkerSendOfflineMainProgram)dlsym(m_hEzdDLL, "E3_MarkerSendOfflineMainProgram");
#endif
        if (E3_MarkerSendOfflineMainProgram == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_MarkerSendOfflineMainProgram in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_MarkerSentBufToCardAndRunList = (e3_MarkerSentBufToCardAndRunList)GetProcAddress(m_hEzdDLL, "E3_MarkerSentBufToCardAndRunList");
#else
        E3_MarkerSentBufToCardAndRunList = (e3_MarkerSentBufToCardAndRunList)dlsym(m_hEzdDLL, "E3_MarkerSentBufToCardAndRunList");
#endif
        if (E3_MarkerSentBufToCardAndRunList == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_MarkerSentBufToCardAndRunList in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_MarkerSetPause = (e3_MarkerSetPause)GetProcAddress(m_hEzdDLL, "E3_MarkerSetPause");
#else
        E3_MarkerSetPause = (e3_MarkerSetPause)dlsym(m_hEzdDLL, "E3_MarkerSetPause");
#endif
        if (E3_MarkerSetPause == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_MarkerSetPause in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_MarkerStop = (e3_MarkerStop)GetProcAddress(m_hEzdDLL, "E3_MarkerStop");
#else
        E3_MarkerStop = (e3_MarkerStop)dlsym(m_hEzdDLL, "E3_MarkerStop");
#endif
        if (E3_MarkerStop == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_MarkerStop in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_MarkerSwitchRedLight = (e3_MarkerSwitchRedLight)GetProcAddress(m_hEzdDLL, "E3_MarkerSwitchRedLight");
#else
        E3_MarkerSwitchRedLight = (e3_MarkerSwitchRedLight)dlsym(m_hEzdDLL, "E3_MarkerSwitchRedLight");
#endif
        if (E3_MarkerSwitchRedLight == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_MarkerSwitchRedLight in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_MarkertSetLoopStartToList = (e3_MarkertSetLoopStartToList)GetProcAddress(m_hEzdDLL, "E3_MarkertSetLoopStartToList");
#else
        E3_MarkertSetLoopStartToList = (e3_MarkertSetLoopStartToList)dlsym(m_hEzdDLL, "E3_MarkertSetLoopStartToList");
#endif
        if (E3_MarkertSetLoopStartToList == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_MarkertSetLoopStartToList in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_MarkerWaitForFinish = (e3_MarkerWaitForFinish)GetProcAddress(m_hEzdDLL, "E3_MarkerWaitForFinish");
#else
        E3_MarkerWaitForFinish = (e3_MarkerWaitForFinish)dlsym(m_hEzdDLL, "E3_MarkerWaitForFinish");
#endif
        if (E3_MarkerWaitForFinish == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_MarkerWaitForFinish in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_MarkerWaitForInputToList = (e3_MarkerWaitForInputToList)GetProcAddress(m_hEzdDLL, "E3_MarkerWaitForInputToList");
#else
        E3_MarkerWaitForInputToList = (e3_MarkerWaitForInputToList)dlsym(m_hEzdDLL, "E3_MarkerWaitForInputToList");
#endif
        if (E3_MarkerWaitForInputToList == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_MarkerWaitForInputToList in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_MarkerWritePort = (e3_MarkerWritePort)GetProcAddress(m_hEzdDLL, "E3_MarkerWritePort");
#else
        E3_MarkerWritePort = (e3_MarkerWritePort)dlsym(m_hEzdDLL, "E3_MarkerWritePort");
#endif
        if (E3_MarkerWritePort == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_MarkerWritePort in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_MarkerWritePortToList = (e3_MarkerWritePortToList)GetProcAddress(m_hEzdDLL, "E3_MarkerWritePortToList");
#else
        E3_MarkerWritePortToList = (e3_MarkerWritePortToList)dlsym(m_hEzdDLL, "E3_MarkerWritePortToList");
#endif
        if (E3_MarkerWritePortToList == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_MarkerWritePortToList in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_ShearEnt = (e3_ShearEnt)GetProcAddress(m_hEzdDLL, "E3_ShearEnt");
#else
        E3_ShearEnt = (e3_ShearEnt)dlsym(m_hEzdDLL, "E3_ShearEnt");
#endif
        if (E3_ShearEnt == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_ShearEnt in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_SplitEntByBox = (e3_SplitEntByBox)GetProcAddress(m_hEzdDLL, "E3_SplitEntByBox");
#else
        E3_SplitEntByBox = (e3_SplitEntByBox)dlsym(m_hEzdDLL, "E3_SplitEntByBox");
#endif
        if (E3_SplitEntByBox == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_SplitEntByBox in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_SplitEntByBox2 = (e3_SplitEntByBox2)GetProcAddress(m_hEzdDLL, "E3_SplitEntByBox2");
#else
        E3_SplitEntByBox2 = (e3_SplitEntByBox2)dlsym(m_hEzdDLL, "E3_SplitEntByBox2");
#endif
        if (E3_SplitEntByBox2 == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_SplitEntByBox2 in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_TransormEnt3dRotate = (e3_TransormEnt3dRotate)GetProcAddress(m_hEzdDLL, "E3_TransormEnt3dRotate");
#else
        E3_TransormEnt3dRotate = (e3_TransormEnt3dRotate)dlsym(m_hEzdDLL, "E3_TransormEnt3dRotate");
#endif
        if (E3_TransormEnt3dRotate == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_TransormEnt3dRotate in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_TransormStlRotate = (e3_TransormStlRotate)GetProcAddress(m_hEzdDLL, "E3_TransormStlRotate");
#else
        E3_TransormStlRotate = (e3_TransormStlRotate)dlsym(m_hEzdDLL, "E3_TransormStlRotate");
#endif
        if (E3_TransormStlRotate == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_TransormStlRotate in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_GetPenParamWeldWave2_2 = (e3_GetPenParamWeldWave2_2)GetProcAddress(m_hEzdDLL, "E3_GetPenParamWeldWave2_2");
#else
        E3_GetPenParamWeldWave2_2 = (e3_GetPenParamWeldWave2_2)dlsym(m_hEzdDLL, "E3_GetPenParamWeldWave2_2");
#endif
        if (E3_GetPenParamWeldWave2_2 == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_GetPenParamWeldWave2_2 in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_SetPenParamWeldWave2_2 = (e3_SetPenParamWeldWave2_2)GetProcAddress(m_hEzdDLL, "E3_SetPenParamWeldWave2_2");
#else
        E3_SetPenParamWeldWave2_2 = (e3_SetPenParamWeldWave2_2)dlsym(m_hEzdDLL, "E3_SetPenParamWeldWave2_2");
#endif
        if (E3_SetPenParamWeldWave2_2 == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_SetPenParamWeldWave2_2 in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_BSplineInterFitCurve = (e3_BSplineInterFitCurve)GetProcAddress(m_hEzdDLL, "E3_BSplineInterFitCurve");
#else
        E3_BSplineInterFitCurve = (e3_BSplineInterFitCurve)dlsym(m_hEzdDLL, "E3_BSplineInterFitCurve");
#endif
        if (E3_BSplineInterFitCurve == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_BSplineInterFitCurve in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_GetPenParamLaserParamIndex = (e3_GetPenParamLaserParamIndex)GetProcAddress(m_hEzdDLL, "E3_GetPenParamLaserParamIndex");
#else
        E3_GetPenParamLaserParamIndex = (e3_GetPenParamLaserParamIndex)dlsym(m_hEzdDLL, "E3_GetPenParamLaserParamIndex");
#endif
        if (E3_GetPenParamLaserParamIndex == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_GetPenParamLaserParamIndex in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_GetTextBarcodeInfo3 = (e3_GetTextBarcodeInfo3)GetProcAddress(m_hEzdDLL, "E3_GetTextBarcodeInfo3");
#else
        E3_GetTextBarcodeInfo3 = (e3_GetTextBarcodeInfo3)dlsym(m_hEzdDLL, "E3_GetTextBarcodeInfo3");
#endif
        if (E3_GetTextBarcodeInfo3 == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_GetTextBarcodeInfo3 in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_MarkeDirectJumpToIndexToList = (e3_MarkeDirectJumpToIndexToList)GetProcAddress(m_hEzdDLL, "E3_MarkeDirectJumpToIndexToList");
#else
        E3_MarkeDirectJumpToIndexToList = (e3_MarkeDirectJumpToIndexToList)dlsym(m_hEzdDLL, "E3_MarkeDirectJumpToIndexToList");
#endif
        if (E3_MarkeDirectJumpToIndexToList == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_MarkeDirectJumpToIndexToList in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_MarkerGetMarkCount2 = (e3_MarkerGetMarkCount2)GetProcAddress(m_hEzdDLL, "E3_MarkerGetMarkCount2");
#else
        E3_MarkerGetMarkCount2 = (e3_MarkerGetMarkCount2)dlsym(m_hEzdDLL, "E3_MarkerGetMarkCount2");
#endif
        if (E3_MarkerGetMarkCount2 == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_MarkerGetMarkCount2 in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_MarkerSetMarkCount = (e3_MarkerSetMarkCount)GetProcAddress(m_hEzdDLL, "E3_MarkerSetMarkCount");
#else
        E3_MarkerSetMarkCount = (e3_MarkerSetMarkCount)dlsym(m_hEzdDLL, "E3_MarkerSetMarkCount");
#endif
        if (E3_MarkerSetMarkCount == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_MarkerSetMarkCount in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_MarkerSetMarkCountToList = (e3_MarkerSetMarkCountToList)GetProcAddress(m_hEzdDLL, "E3_MarkerSetMarkCountToList");
#else
        E3_MarkerSetMarkCountToList = (e3_MarkerSetMarkCountToList)dlsym(m_hEzdDLL, "E3_MarkerSetMarkCountToList");
#endif
        if (E3_MarkerSetMarkCountToList == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_MarkerSetMarkCountToList in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_MarkerStartUSBMonitorProcess = (e3_MarkerStartUSBMonitorProcess)GetProcAddress(m_hEzdDLL, "E3_MarkerStartUSBMonitorProcess");
#else
        E3_MarkerStartUSBMonitorProcess = (e3_MarkerStartUSBMonitorProcess)dlsym(m_hEzdDLL, "E3_MarkerStartUSBMonitorProcess");
#endif
        if (E3_MarkerStartUSBMonitorProcess == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_MarkerStartUSBMonitorProcess in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_MarkertRepeatToList = (e3_MarkertRepeatToList)GetProcAddress(m_hEzdDLL, "E3_MarkertRepeatToList");
#else
        E3_MarkertRepeatToList = (e3_MarkertRepeatToList)dlsym(m_hEzdDLL, "E3_MarkertRepeatToList");
#endif
        if (E3_MarkertRepeatToList == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_MarkertRepeatToList in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_MarkertUntilToList = (e3_MarkertUntilToList)GetProcAddress(m_hEzdDLL, "E3_MarkertUntilToList");
#else
        E3_MarkertUntilToList = (e3_MarkertUntilToList)dlsym(m_hEzdDLL, "E3_MarkertUntilToList");
#endif
        if (E3_MarkertUntilToList == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_MarkertUntilToList in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_SetPenParamLaserParamIndex = (e3_SetPenParamLaserParamIndex)GetProcAddress(m_hEzdDLL, "E3_SetPenParamLaserParamIndex");
#else
        E3_SetPenParamLaserParamIndex = (e3_SetPenParamLaserParamIndex)dlsym(m_hEzdDLL, "E3_SetPenParamLaserParamIndex");
#endif
        if (E3_SetPenParamLaserParamIndex == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_SetPenParamLaserParamIndex in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_MarkerSetAutoIncCounterToList = (e3_MarkerSetAutoIncCounterToList)GetProcAddress(m_hEzdDLL, "E3_MarkerSetAutoIncCounterToList");
#else
        E3_MarkerSetAutoIncCounterToList = (e3_MarkerSetAutoIncCounterToList)dlsym(m_hEzdDLL, "E3_MarkerSetAutoIncCounterToList");
#endif
        if (E3_MarkerSetAutoIncCounterToList == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_MarkerSetAutoIncCounterToList in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_GetEntMgr = (e3_GetEntMgr)GetProcAddress(m_hEzdDLL, "E3_GetEntMgr");
#else
        E3_GetEntMgr = (e3_GetEntMgr)dlsym(m_hEzdDLL, "E3_GetEntMgr");
#endif
        if (E3_GetEntMgr == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_GetEntMgr in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_GetEntParam = (e3_GetEntParam)GetProcAddress(m_hEzdDLL, "E3_GetEntParam");
#else
        E3_GetEntParam = (e3_GetEntParam)dlsym(m_hEzdDLL, "E3_GetEntParam");
#endif
        if (E3_GetEntParam == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_GetEntParam in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_GetEntParam1 = (e3_GetEntParam1)GetProcAddress(m_hEzdDLL, "E3_GetEntParam1");
#else
        E3_GetEntParam1 = (e3_GetEntParam1)dlsym(m_hEzdDLL, "E3_GetEntParam1");
#endif
        if (E3_GetEntParam1 == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_GetEntParam1 in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_GetEntParam2 = (e3_GetEntParam2)GetProcAddress(m_hEzdDLL, "E3_GetEntParam2");
#else
        E3_GetEntParam2 = (e3_GetEntParam2)dlsym(m_hEzdDLL, "E3_GetEntParam2");
#endif
        if (E3_GetEntParam2 == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_GetEntParam2 in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_GetEntPen = (e3_GetEntPen)GetProcAddress(m_hEzdDLL, "E3_GetEntPen");
#else
        E3_GetEntPen = (e3_GetEntPen)dlsym(m_hEzdDLL, "E3_GetEntPen");
#endif
        if (E3_GetEntPen == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_GetEntPen in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_GetTextBarcodeInfo = (e3_GetTextBarcodeInfo)GetProcAddress(m_hEzdDLL, "E3_GetTextBarcodeInfo");
#else
        E3_GetTextBarcodeInfo = (e3_GetTextBarcodeInfo)dlsym(m_hEzdDLL, "E3_GetTextBarcodeInfo");
#endif
        if (E3_GetTextBarcodeInfo == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_GetTextBarcodeInfo in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_GetTextBarcodeInfo2 = (e3_GetTextBarcodeInfo2)GetProcAddress(m_hEzdDLL, "E3_GetTextBarcodeInfo2");
#else
        E3_GetTextBarcodeInfo2 = (e3_GetTextBarcodeInfo2)dlsym(m_hEzdDLL, "E3_GetTextBarcodeInfo2");
#endif
        if (E3_GetTextBarcodeInfo2 == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_GetTextBarcodeInfo2 in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_GetTextBarcodeInfo4 = (e3_GetTextBarcodeInfo4)GetProcAddress(m_hEzdDLL, "E3_GetTextBarcodeInfo4");
#else
        E3_GetTextBarcodeInfo4 = (e3_GetTextBarcodeInfo4)dlsym(m_hEzdDLL, "E3_GetTextBarcodeInfo4");
#endif
        if (E3_GetTextBarcodeInfo4 == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_GetTextBarcodeInfo4 in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_GetTextBarcodeInfo5 = (e3_GetTextBarcodeInfo5)GetProcAddress(m_hEzdDLL, "E3_GetTextBarcodeInfo5");
#else
        E3_GetTextBarcodeInfo5 = (e3_GetTextBarcodeInfo5)dlsym(m_hEzdDLL, "E3_GetTextBarcodeInfo5");
#endif
        if (E3_GetTextBarcodeInfo5 == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_GetTextBarcodeInfo5 in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_GetTextBarcodeInfo6 = (e3_GetTextBarcodeInfo6)GetProcAddress(m_hEzdDLL, "E3_GetTextBarcodeInfo6");
#else
        E3_GetTextBarcodeInfo6 = (e3_GetTextBarcodeInfo6)dlsym(m_hEzdDLL, "E3_GetTextBarcodeInfo6");
#endif
        if (E3_GetTextBarcodeInfo6 == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_GetTextBarcodeInfo6 in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_GetTextByID = (e3_GetTextByID)GetProcAddress(m_hEzdDLL, "E3_GetTextByID");
#else
        E3_GetTextByID = (e3_GetTextByID)dlsym(m_hEzdDLL, "E3_GetTextByID");
#endif
        if (E3_GetTextByID == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_GetTextByID in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_IsBarcodeTextValid = (e3_IsBarcodeTextValid)GetProcAddress(m_hEzdDLL, "E3_IsBarcodeTextValid");
#else
        E3_IsBarcodeTextValid = (e3_IsBarcodeTextValid)dlsym(m_hEzdDLL, "E3_IsBarcodeTextValid");
#endif
        if (E3_IsBarcodeTextValid == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_IsBarcodeTextValid in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_MarkerChangeMarkCountToList = (e3_MarkerChangeMarkCountToList)GetProcAddress(m_hEzdDLL, "E3_MarkerChangeMarkCountToList");
#else
        E3_MarkerChangeMarkCountToList = (e3_MarkerChangeMarkCountToList)dlsym(m_hEzdDLL, "E3_MarkerChangeMarkCountToList");
#endif
        if (E3_MarkerChangeMarkCountToList == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_MarkerChangeMarkCountToList in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_SetTextBarcodeInfo = (e3_SetTextBarcodeInfo)GetProcAddress(m_hEzdDLL, "E3_SetTextBarcodeInfo");
#else
        E3_SetTextBarcodeInfo = (e3_SetTextBarcodeInfo)dlsym(m_hEzdDLL, "E3_SetTextBarcodeInfo");
#endif
        if (E3_SetTextBarcodeInfo == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_SetTextBarcodeInfo in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_SetTextBarcodeInfo4 = (e3_SetTextBarcodeInfo4)GetProcAddress(m_hEzdDLL, "E3_SetTextBarcodeInfo4");
#else
        E3_SetTextBarcodeInfo4 = (e3_SetTextBarcodeInfo4)dlsym(m_hEzdDLL, "E3_SetTextBarcodeInfo4");
#endif
        if (E3_SetTextBarcodeInfo4 == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_SetTextBarcodeInfo4 in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_SetTextBarcodeInfo5 = (e3_SetTextBarcodeInfo5)GetProcAddress(m_hEzdDLL, "E3_SetTextBarcodeInfo5");
#else
        E3_SetTextBarcodeInfo5 = (e3_SetTextBarcodeInfo5)dlsym(m_hEzdDLL, "E3_SetTextBarcodeInfo5");
#endif
        if (E3_SetTextBarcodeInfo5 == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_SetTextBarcodeInfo5 in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_SetTextBarcodeInfo6 = (e3_SetTextBarcodeInfo6)GetProcAddress(m_hEzdDLL, "E3_SetTextBarcodeInfo6");
#else
        E3_SetTextBarcodeInfo6 = (e3_SetTextBarcodeInfo6)dlsym(m_hEzdDLL, "E3_SetTextBarcodeInfo6");
#endif
        if (E3_SetTextBarcodeInfo6 == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_SetTextBarcodeInfo6 in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_SetTextBarcodeInfo_2 = (e3_SetTextBarcodeInfo_2)GetProcAddress(m_hEzdDLL, "E3_SetTextBarcodeInfo_2");
#else
        E3_SetTextBarcodeInfo_2 = (e3_SetTextBarcodeInfo_2)dlsym(m_hEzdDLL, "E3_SetTextBarcodeInfo_2");
#endif
        if (E3_SetTextBarcodeInfo_2 == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_SetTextBarcodeInfo_2 in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_GetEntBaseInfo2 = (e3_GetEntBaseInfo2)GetProcAddress(m_hEzdDLL, "E3_GetEntBaseInfo2");
#else
        E3_GetEntBaseInfo2 = (e3_GetEntBaseInfo2)dlsym(m_hEzdDLL, "E3_GetEntBaseInfo2");
#endif
        if (E3_GetEntBaseInfo2 == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_GetEntBaseInfo2 in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_GetEntBaseInfo3 = (e3_GetEntBaseInfo3)GetProcAddress(m_hEzdDLL, "E3_GetEntBaseInfo3");
#else
        E3_GetEntBaseInfo3 = (e3_GetEntBaseInfo3)dlsym(m_hEzdDLL, "E3_GetEntBaseInfo3");
#endif
        if (E3_GetEntBaseInfo3 == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_GetEntBaseInfo3 in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_GetParamCount = (e3_GetParamCount)GetProcAddress(m_hEzdDLL, "E3_GetParamCount");
#else
        E3_GetParamCount = (e3_GetParamCount)dlsym(m_hEzdDLL, "E3_GetParamCount");
#endif
        if (E3_GetParamCount == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_GetParamCount in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_GetPenParam = (e3_GetPenParam)GetProcAddress(m_hEzdDLL, "E3_GetPenParam");
#else
        E3_GetPenParam = (e3_GetPenParam)dlsym(m_hEzdDLL, "E3_GetPenParam");
#endif
        if (E3_GetPenParam == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_GetPenParam in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_GetPenParamExt4 = (e3_GetPenParamExt4)GetProcAddress(m_hEzdDLL, "E3_GetPenParamExt4");
#else
        E3_GetPenParamExt4 = (e3_GetPenParamExt4)dlsym(m_hEzdDLL, "E3_GetPenParamExt4");
#endif
        if (E3_GetPenParamExt4 == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_GetPenParamExt4 in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_GetPenParamExt5 = (e3_GetPenParamExt5)GetProcAddress(m_hEzdDLL, "E3_GetPenParamExt5");
#else
        E3_GetPenParamExt5 = (e3_GetPenParamExt5)dlsym(m_hEzdDLL, "E3_GetPenParamExt5");
#endif
        if (E3_GetPenParamExt5 == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_GetPenParamExt5 in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_MarkerGetMsg = (e3_MarkerGetMsg)GetProcAddress(m_hEzdDLL, "E3_MarkerGetMsg");
#else
        E3_MarkerGetMsg = (e3_MarkerGetMsg)dlsym(m_hEzdDLL, "E3_MarkerGetMsg");
#endif
        if (E3_MarkerGetMsg == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_MarkerGetMsg in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_MarkerGetParamDouble = (e3_MarkerGetParamDouble)GetProcAddress(m_hEzdDLL, "E3_MarkerGetParamDouble");
#else
        E3_MarkerGetParamDouble = (e3_MarkerGetParamDouble)dlsym(m_hEzdDLL, "E3_MarkerGetParamDouble");
#endif
        if (E3_MarkerGetParamDouble == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_MarkerGetParamDouble in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_MarkerGetParamInt = (e3_MarkerGetParamInt)GetProcAddress(m_hEzdDLL, "E3_MarkerGetParamInt");
#else
        E3_MarkerGetParamInt = (e3_MarkerGetParamInt)dlsym(m_hEzdDLL, "E3_MarkerGetParamInt");
#endif
        if (E3_MarkerGetParamInt == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_MarkerGetParamInt in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_MarkerGetParamString = (e3_MarkerGetParamString)GetProcAddress(m_hEzdDLL, "E3_MarkerGetParamString");
#else
        E3_MarkerGetParamString = (e3_MarkerGetParamString)dlsym(m_hEzdDLL, "E3_MarkerGetParamString");
#endif
        if (E3_MarkerGetParamString == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_MarkerGetParamString in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_MarkerInitUsbMonitor = (e3_MarkerInitUsbMonitor)GetProcAddress(m_hEzdDLL, "E3_MarkerInitUsbMonitor");
#else
        E3_MarkerInitUsbMonitor = (e3_MarkerInitUsbMonitor)dlsym(m_hEzdDLL, "E3_MarkerInitUsbMonitor");
#endif
        if (E3_MarkerInitUsbMonitor == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_MarkerInitUsbMonitor in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_MarkerListEndToList = (e3_MarkerListEndToList)GetProcAddress(m_hEzdDLL, "E3_MarkerListEndToList");
#else
        E3_MarkerListEndToList = (e3_MarkerListEndToList)dlsym(m_hEzdDLL, "E3_MarkerListEndToList");
#endif
        if (E3_MarkerListEndToList == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_MarkerListEndToList in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_MarkerSetParamDouble = (e3_MarkerSetParamDouble)GetProcAddress(m_hEzdDLL, "E3_MarkerSetParamDouble");
#else
        E3_MarkerSetParamDouble = (e3_MarkerSetParamDouble)dlsym(m_hEzdDLL, "E3_MarkerSetParamDouble");
#endif
        if (E3_MarkerSetParamDouble == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_MarkerSetParamDouble in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_MarkerSetParamInt = (e3_MarkerSetParamInt)GetProcAddress(m_hEzdDLL, "E3_MarkerSetParamInt");
#else
        E3_MarkerSetParamInt = (e3_MarkerSetParamInt)dlsym(m_hEzdDLL, "E3_MarkerSetParamInt");
#endif
        if (E3_MarkerSetParamInt == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_MarkerSetParamInt in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_MarkerLoadFlyDistanceCorrectionTable = (e3_MarkerLoadFlyDistanceCorrectionTable)GetProcAddress(m_hEzdDLL, "E3_MarkerLoadFlyDistanceCorrectionTable");
#else
        E3_MarkerLoadFlyDistanceCorrectionTable = (e3_MarkerLoadFlyDistanceCorrectionTable)dlsym(m_hEzdDLL, "E3_MarkerLoadFlyDistanceCorrectionTable");
#endif
        if (E3_MarkerLoadFlyDistanceCorrectionTable == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_MarkerLoadFlyDistanceCorrectionTable in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_ChangeTextById = (e3_ChangeTextById)GetProcAddress(m_hEzdDLL, "E3_ChangeTextById");
#else
        E3_ChangeTextById = (e3_ChangeTextById)dlsym(m_hEzdDLL, "E3_ChangeTextById");
#endif
        if (E3_ChangeTextById == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_ChangeTextById in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_ChangeTextByName = (e3_ChangeTextByName)GetProcAddress(m_hEzdDLL, "E3_ChangeTextByName");
#else
        E3_ChangeTextByName = (e3_ChangeTextByName)dlsym(m_hEzdDLL, "E3_ChangeTextByName");
#endif
        if (E3_ChangeTextByName == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_ChangeTextByName in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_Close = (e3_Close)GetProcAddress(m_hEzdDLL, "E3_Close");
#else
        E3_Close = (e3_Close)dlsym(m_hEzdDLL, "E3_Close");
#endif
        if (E3_Close == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_Close in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_CreateBitmap = (e3_CreateBitmap)GetProcAddress(m_hEzdDLL, "E3_CreateBitmap");
#else
        E3_CreateBitmap = (e3_CreateBitmap)dlsym(m_hEzdDLL, "E3_CreateBitmap");
#endif
        if (E3_CreateBitmap == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_CreateBitmap in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_CreateBitmap_2 = (e3_CreateBitmap_2)GetProcAddress(m_hEzdDLL, "E3_CreateBitmap_2");
#else
        E3_CreateBitmap_2 = (e3_CreateBitmap_2)dlsym(m_hEzdDLL, "E3_CreateBitmap_2");
#endif
        if (E3_CreateBitmap_2 == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_CreateBitmap_2 in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_CreateEntMgr = (e3_CreateEntMgr)GetProcAddress(m_hEzdDLL, "E3_CreateEntMgr");
#else
        E3_CreateEntMgr = (e3_CreateEntMgr)dlsym(m_hEzdDLL, "E3_CreateEntMgr");
#endif
        if (E3_CreateEntMgr == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_CreateEntMgr in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_DisableInitialPrompt = (e3_DisableInitialPrompt)GetProcAddress(m_hEzdDLL, "E3_DisableInitialPrompt");
#else
        E3_DisableInitialPrompt = (e3_DisableInitialPrompt)dlsym(m_hEzdDLL, "E3_DisableInitialPrompt");
#endif
        if (E3_DisableInitialPrompt == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_DisableInitialPrompt in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_EnableShowHatchProcess = (e3_EnableShowHatchProcess)GetProcAddress(m_hEzdDLL, "E3_EnableShowHatchProcess");
#else
        E3_EnableShowHatchProcess = (e3_EnableShowHatchProcess)dlsym(m_hEzdDLL, "E3_EnableShowHatchProcess");
#endif
        if (E3_EnableShowHatchProcess == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_EnableShowHatchProcess in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_FindEntInLayerByIndex = (e3_FindEntInLayerByIndex)GetProcAddress(m_hEzdDLL, "E3_FindEntInLayerByIndex");
#else
        E3_FindEntInLayerByIndex = (e3_FindEntInLayerByIndex)dlsym(m_hEzdDLL, "E3_FindEntInLayerByIndex");
#endif
        if (E3_FindEntInLayerByIndex == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_FindEntInLayerByIndex in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_FindEntInLayerByName = (e3_FindEntInLayerByName)GetProcAddress(m_hEzdDLL, "E3_FindEntInLayerByName");
#else
        E3_FindEntInLayerByName = (e3_FindEntInLayerByName)dlsym(m_hEzdDLL, "E3_FindEntInLayerByName");
#endif
        if (E3_FindEntInLayerByName == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_FindEntInLayerByName in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_FreeEntMgr = (e3_FreeEntMgr)GetProcAddress(m_hEzdDLL, "E3_FreeEntMgr");
#else
        E3_FreeEntMgr = (e3_FreeEntMgr)dlsym(m_hEzdDLL, "E3_FreeEntMgr");
#endif
        if (E3_FreeEntMgr == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_FreeEntMgr in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_GetEntBitmap = (e3_GetEntBitmap)GetProcAddress(m_hEzdDLL, "E3_GetEntBitmap");
#else
        E3_GetEntBitmap = (e3_GetEntBitmap)dlsym(m_hEzdDLL, "E3_GetEntBitmap");
#endif
        if (E3_GetEntBitmap == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_GetEntBitmap in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_GetParamLibCount = (e3_GetParamLibCount)GetProcAddress(m_hEzdDLL, "E3_GetParamLibCount");
#else
        E3_GetParamLibCount = (e3_GetParamLibCount)dlsym(m_hEzdDLL, "E3_GetParamLibCount");
#endif
        if (E3_GetParamLibCount == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_GetParamLibCount in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_GetParamLibName = (e3_GetParamLibName)GetProcAddress(m_hEzdDLL, "E3_GetParamLibName");
#else
        E3_GetParamLibName = (e3_GetParamLibName)dlsym(m_hEzdDLL, "E3_GetParamLibName");
#endif
        if (E3_GetParamLibName == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_GetParamLibName in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_GetPenParamExtOutputIndex = (e3_GetPenParamExtOutputIndex)GetProcAddress(m_hEzdDLL, "E3_GetPenParamExtOutputIndex");
#else
        E3_GetPenParamExtOutputIndex = (e3_GetPenParamExtOutputIndex)dlsym(m_hEzdDLL, "E3_GetPenParamExtOutputIndex");
#endif
        if (E3_GetPenParamExtOutputIndex == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_GetPenParamExtOutputIndex in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_GetPenParamFreqRamp = (e3_GetPenParamFreqRamp)GetProcAddress(m_hEzdDLL, "E3_GetPenParamFreqRamp");
#else
        E3_GetPenParamFreqRamp = (e3_GetPenParamFreqRamp)dlsym(m_hEzdDLL, "E3_GetPenParamFreqRamp");
#endif
        if (E3_GetPenParamFreqRamp == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_GetPenParamFreqRamp in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_GetPenParamLaserLagTime = (e3_GetPenParamLaserLagTime)GetProcAddress(m_hEzdDLL, "E3_GetPenParamLaserLagTime");
#else
        E3_GetPenParamLaserLagTime = (e3_GetPenParamLaserLagTime)dlsym(m_hEzdDLL, "E3_GetPenParamLaserLagTime");
#endif
        if (E3_GetPenParamLaserLagTime == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_GetPenParamLaserLagTime in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_GetPenParamPowerRamp = (e3_GetPenParamPowerRamp)GetProcAddress(m_hEzdDLL, "E3_GetPenParamPowerRamp");
#else
        E3_GetPenParamPowerRamp = (e3_GetPenParamPowerRamp)dlsym(m_hEzdDLL, "E3_GetPenParamPowerRamp");
#endif
        if (E3_GetPenParamPowerRamp == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_GetPenParamPowerRamp in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_GetPenParamSkyWriting = (e3_GetPenParamSkyWriting)GetProcAddress(m_hEzdDLL, "E3_GetPenParamSkyWriting");
#else
        E3_GetPenParamSkyWriting = (e3_GetPenParamSkyWriting)dlsym(m_hEzdDLL, "E3_GetPenParamSkyWriting");
#endif
        if (E3_GetPenParamSkyWriting == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_GetPenParamSkyWriting in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_GetPenParamSpeedRamp = (e3_GetPenParamSpeedRamp)GetProcAddress(m_hEzdDLL, "E3_GetPenParamSpeedRamp");
#else
        E3_GetPenParamSpeedRamp = (e3_GetPenParamSpeedRamp)dlsym(m_hEzdDLL, "E3_GetPenParamSpeedRamp");
#endif
        if (E3_GetPenParamSpeedRamp == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_GetPenParamSpeedRamp in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_GetPenParamStep = (e3_GetPenParamStep)GetProcAddress(m_hEzdDLL, "E3_GetPenParamStep");
#else
        E3_GetPenParamStep = (e3_GetPenParamStep)dlsym(m_hEzdDLL, "E3_GetPenParamStep");
#endif
        if (E3_GetPenParamStep == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_GetPenParamStep in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_GetPenParamWeldWave = (e3_GetPenParamWeldWave)GetProcAddress(m_hEzdDLL, "E3_GetPenParamWeldWave");
#else
        E3_GetPenParamWeldWave = (e3_GetPenParamWeldWave)dlsym(m_hEzdDLL, "E3_GetPenParamWeldWave");
#endif
        if (E3_GetPenParamWeldWave == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_GetPenParamWeldWave in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_GetPenParamWeldWave2 = (e3_GetPenParamWeldWave2)GetProcAddress(m_hEzdDLL, "E3_GetPenParamWeldWave2");
#else
        E3_GetPenParamWeldWave2 = (e3_GetPenParamWeldWave2)dlsym(m_hEzdDLL, "E3_GetPenParamWeldWave2");
#endif
        if (E3_GetPenParamWeldWave2 == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_GetPenParamWeldWave2 in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_GetPenParamWobble = (e3_GetPenParamWobble)GetProcAddress(m_hEzdDLL, "E3_GetPenParamWobble");
#else
        E3_GetPenParamWobble = (e3_GetPenParamWobble)dlsym(m_hEzdDLL, "E3_GetPenParamWobble");
#endif
        if (E3_GetPenParamWobble == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_GetPenParamWobble in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_GetPenParamWobbleIncSpeed = (e3_GetPenParamWobbleIncSpeed)GetProcAddress(m_hEzdDLL, "E3_GetPenParamWobbleIncSpeed");
#else
        E3_GetPenParamWobbleIncSpeed = (e3_GetPenParamWobbleIncSpeed)dlsym(m_hEzdDLL, "E3_GetPenParamWobbleIncSpeed");
#endif
        if (E3_GetPenParamWobbleIncSpeed == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_GetPenParamWobbleIncSpeed in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_Initial = (e3_Initial)GetProcAddress(m_hEzdDLL, "E3_Initial");
#else
        E3_Initial = (e3_Initial)dlsym(m_hEzdDLL, "E3_Initial");
#endif
        if (E3_Initial == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_Initial in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_MarkerCloseUsbMonitor = (e3_MarkerCloseUsbMonitor)GetProcAddress(m_hEzdDLL, "E3_MarkerCloseUsbMonitor");
#else
        E3_MarkerCloseUsbMonitor = (e3_MarkerCloseUsbMonitor)dlsym(m_hEzdDLL, "E3_MarkerCloseUsbMonitor");
#endif
        if (E3_MarkerCloseUsbMonitor == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_MarkerCloseUsbMonitor in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_MarkerDelayUsToList = (e3_MarkerDelayUsToList)GetProcAddress(m_hEzdDLL, "E3_MarkerDelayUsToList");
#else
        E3_MarkerDelayUsToList = (e3_MarkerDelayUsToList)dlsym(m_hEzdDLL, "E3_MarkerDelayUsToList");
#endif
        if (E3_MarkerDelayUsToList == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_MarkerDelayUsToList in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_MarkerDlgSetCfg = (e3_MarkerDlgSetCfg)GetProcAddress(m_hEzdDLL, "E3_MarkerDlgSetCfg");
#else
        E3_MarkerDlgSetCfg = (e3_MarkerDlgSetCfg)dlsym(m_hEzdDLL, "E3_MarkerDlgSetCfg");
#endif
        if (E3_MarkerDlgSetCfg == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_MarkerDlgSetCfg in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_MarkerGetCfgParamDouble = (e3_MarkerGetCfgParamDouble)GetProcAddress(m_hEzdDLL, "E3_MarkerGetCfgParamDouble");
#else
        E3_MarkerGetCfgParamDouble = (e3_MarkerGetCfgParamDouble)dlsym(m_hEzdDLL, "E3_MarkerGetCfgParamDouble");
#endif
        if (E3_MarkerGetCfgParamDouble == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_MarkerGetCfgParamDouble in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_MarkerGetCfgParamInt = (e3_MarkerGetCfgParamInt)GetProcAddress(m_hEzdDLL, "E3_MarkerGetCfgParamInt");
#else
        E3_MarkerGetCfgParamInt = (e3_MarkerGetCfgParamInt)dlsym(m_hEzdDLL, "E3_MarkerGetCfgParamInt");
#endif
        if (E3_MarkerGetCfgParamInt == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_MarkerGetCfgParamInt in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_MarkerGetEntMgr = (e3_MarkerGetEntMgr)GetProcAddress(m_hEzdDLL, "E3_MarkerGetEntMgr");
#else
        E3_MarkerGetEntMgr = (e3_MarkerGetEntMgr)dlsym(m_hEzdDLL, "E3_MarkerGetEntMgr");
#endif
        if (E3_MarkerGetEntMgr == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_MarkerGetEntMgr in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_MarkerGetFirstValidId = (e3_MarkerGetFirstValidId)GetProcAddress(m_hEzdDLL, "E3_MarkerGetFirstValidId");
#else
        E3_MarkerGetFirstValidId = (e3_MarkerGetFirstValidId)dlsym(m_hEzdDLL, "E3_MarkerGetFirstValidId");
#endif
        if (E3_MarkerGetFirstValidId == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_MarkerGetFirstValidId in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_MarkerInitUsbMonitor2 = (e3_MarkerInitUsbMonitor2)GetProcAddress(m_hEzdDLL, "E3_MarkerInitUsbMonitor2");
#else
        E3_MarkerInitUsbMonitor2 = (e3_MarkerInitUsbMonitor2)dlsym(m_hEzdDLL, "E3_MarkerInitUsbMonitor2");
#endif
        if (E3_MarkerInitUsbMonitor2 == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_MarkerInitUsbMonitor2 in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_MarkerJumpTo = (e3_MarkerJumpTo)GetProcAddress(m_hEzdDLL, "E3_MarkerJumpTo");
#else
        E3_MarkerJumpTo = (e3_MarkerJumpTo)dlsym(m_hEzdDLL, "E3_MarkerJumpTo");
#endif
        if (E3_MarkerJumpTo == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_MarkerJumpTo in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_MarkerLaserOn = (e3_MarkerLaserOn)GetProcAddress(m_hEzdDLL, "E3_MarkerLaserOn");
#else
        E3_MarkerLaserOn = (e3_MarkerLaserOn)dlsym(m_hEzdDLL, "E3_MarkerLaserOn");
#endif
        if (E3_MarkerLaserOn == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_MarkerLaserOn in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_MarkerLaserOnToList = (e3_MarkerLaserOnToList)GetProcAddress(m_hEzdDLL, "E3_MarkerLaserOnToList");
#else
        E3_MarkerLaserOnToList = (e3_MarkerLaserOnToList)dlsym(m_hEzdDLL, "E3_MarkerLaserOnToList");
#endif
        if (E3_MarkerLaserOnToList == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_MarkerLaserOnToList in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_MarkerListEnd = (e3_MarkerListEnd)GetProcAddress(m_hEzdDLL, "E3_MarkerListEnd");
#else
        E3_MarkerListEnd = (e3_MarkerListEnd)dlsym(m_hEzdDLL, "E3_MarkerListEnd");
#endif
        if (E3_MarkerListEnd == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_MarkerListEnd in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_MarkerListReady = (e3_MarkerListReady)GetProcAddress(m_hEzdDLL, "E3_MarkerListReady");
#else
        E3_MarkerListReady = (e3_MarkerListReady)dlsym(m_hEzdDLL, "E3_MarkerListReady");
#endif
        if (E3_MarkerListReady == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_MarkerListReady in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_MarkerMarkEnt2 = (e3_MarkerMarkEnt2)GetProcAddress(m_hEzdDLL, "E3_MarkerMarkEnt2");
#else
        E3_MarkerMarkEnt2 = (e3_MarkerMarkEnt2)dlsym(m_hEzdDLL, "E3_MarkerMarkEnt2");
#endif
        if (E3_MarkerMarkEnt2 == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_MarkerMarkEnt2 in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_MarkerMarkEntToList2 = (e3_MarkerMarkEntToList2)GetProcAddress(m_hEzdDLL, "E3_MarkerMarkEntToList2");
#else
        E3_MarkerMarkEntToList2 = (e3_MarkerMarkEntToList2)dlsym(m_hEzdDLL, "E3_MarkerMarkEntToList2");
#endif
        if (E3_MarkerMarkEntToList2 == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_MarkerMarkEntToList2 in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_MarkerMarkEntToListByPen = (e3_MarkerMarkEntToListByPen)GetProcAddress(m_hEzdDLL, "E3_MarkerMarkEntToListByPen");
#else
        E3_MarkerMarkEntToListByPen = (e3_MarkerMarkEntToListByPen)dlsym(m_hEzdDLL, "E3_MarkerMarkEntToListByPen");
#endif
        if (E3_MarkerMarkEntToListByPen == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_MarkerMarkEntToListByPen in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_MarkerOneCurveToList = (e3_MarkerOneCurveToList)GetProcAddress(m_hEzdDLL, "E3_MarkerOneCurveToList");
#else
        E3_MarkerOneCurveToList = (e3_MarkerOneCurveToList)dlsym(m_hEzdDLL, "E3_MarkerOneCurveToList");
#endif
        if (E3_MarkerOneCurveToList == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_MarkerOneCurveToList in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_MarkerReadPort = (e3_MarkerReadPort)GetProcAddress(m_hEzdDLL, "E3_MarkerReadPort");
#else
        E3_MarkerReadPort = (e3_MarkerReadPort)dlsym(m_hEzdDLL, "E3_MarkerReadPort");
#endif
        if (E3_MarkerReadPort == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_MarkerReadPort in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_MarkerResetMarkCount = (e3_MarkerResetMarkCount)GetProcAddress(m_hEzdDLL, "E3_MarkerResetMarkCount");
#else
        E3_MarkerResetMarkCount = (e3_MarkerResetMarkCount)dlsym(m_hEzdDLL, "E3_MarkerResetMarkCount");
#endif
        if (E3_MarkerResetMarkCount == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_MarkerResetMarkCount in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_MarkerSetCfgParamDouble = (e3_MarkerSetCfgParamDouble)GetProcAddress(m_hEzdDLL, "E3_MarkerSetCfgParamDouble");
#else
        E3_MarkerSetCfgParamDouble = (e3_MarkerSetCfgParamDouble)dlsym(m_hEzdDLL, "E3_MarkerSetCfgParamDouble");
#endif
        if (E3_MarkerSetCfgParamDouble == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_MarkerSetCfgParamDouble in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_MarkerSetCfgParamInt = (e3_MarkerSetCfgParamInt)GetProcAddress(m_hEzdDLL, "E3_MarkerSetCfgParamInt");
#else
        E3_MarkerSetCfgParamInt = (e3_MarkerSetCfgParamInt)dlsym(m_hEzdDLL, "E3_MarkerSetCfgParamInt");
#endif
        if (E3_MarkerSetCfgParamInt == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_MarkerSetCfgParamInt in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_MarkerSetCorFile2 = (e3_MarkerSetCorFile2)GetProcAddress(m_hEzdDLL, "E3_MarkerSetCorFile2");
#else
        E3_MarkerSetCorFile2 = (e3_MarkerSetCorFile2)dlsym(m_hEzdDLL, "E3_MarkerSetCorFile2");
#endif
        if (E3_MarkerSetCorFile2 == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_MarkerSetCorFile2 in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_MarkerSetEntMgr = (e3_MarkerSetEntMgr)GetProcAddress(m_hEzdDLL, "E3_MarkerSetEntMgr");
#else
        E3_MarkerSetEntMgr = (e3_MarkerSetEntMgr)dlsym(m_hEzdDLL, "E3_MarkerSetEntMgr");
#endif
        if (E3_MarkerSetEntMgr == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_MarkerSetEntMgr in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_MarkerSetParamString = (e3_MarkerSetParamString)GetProcAddress(m_hEzdDLL, "E3_MarkerSetParamString");
#else
        E3_MarkerSetParamString = (e3_MarkerSetParamString)dlsym(m_hEzdDLL, "E3_MarkerSetParamString");
#endif
        if (E3_MarkerSetParamString == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_MarkerSetParamString in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_MarkerUsbMonitorGetNewDevice = (e3_MarkerUsbMonitorGetNewDevice)GetProcAddress(m_hEzdDLL, "E3_MarkerUsbMonitorGetNewDevice");
#else
        E3_MarkerUsbMonitorGetNewDevice = (e3_MarkerUsbMonitorGetNewDevice)dlsym(m_hEzdDLL, "E3_MarkerUsbMonitorGetNewDevice");
#endif
        if (E3_MarkerUsbMonitorGetNewDevice == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_MarkerUsbMonitorGetNewDevice in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_ParamLibDeleteName = (e3_ParamLibDeleteName)GetProcAddress(m_hEzdDLL, "E3_ParamLibDeleteName");
#else
        E3_ParamLibDeleteName = (e3_ParamLibDeleteName)dlsym(m_hEzdDLL, "E3_ParamLibDeleteName");
#endif
        if (E3_ParamLibDeleteName == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_ParamLibDeleteName in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_ParamLibSavePenToName = (e3_ParamLibSavePenToName)GetProcAddress(m_hEzdDLL, "E3_ParamLibSavePenToName");
#else
        E3_ParamLibSavePenToName = (e3_ParamLibSavePenToName)dlsym(m_hEzdDLL, "E3_ParamLibSavePenToName");
#endif
        if (E3_ParamLibSavePenToName == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_ParamLibSavePenToName in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_ParamLibSetPenFromName = (e3_ParamLibSetPenFromName)GetProcAddress(m_hEzdDLL, "E3_ParamLibSetPenFromName");
#else
        E3_ParamLibSetPenFromName = (e3_ParamLibSetPenFromName)dlsym(m_hEzdDLL, "E3_ParamLibSetPenFromName");
#endif
        if (E3_ParamLibSetPenFromName == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_ParamLibSetPenFromName in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_SetBmpFileInfo = (e3_SetBmpFileInfo)GetProcAddress(m_hEzdDLL, "E3_SetBmpFileInfo");
#else
        E3_SetBmpFileInfo = (e3_SetBmpFileInfo)dlsym(m_hEzdDLL, "E3_SetBmpFileInfo");
#endif
        if (E3_SetBmpFileInfo == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_SetBmpFileInfo in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_SetBmpFileInfo_2 = (e3_SetBmpFileInfo_2)GetProcAddress(m_hEzdDLL, "E3_SetBmpFileInfo_2");
#else
        E3_SetBmpFileInfo_2 = (e3_SetBmpFileInfo_2)dlsym(m_hEzdDLL, "E3_SetBmpFileInfo_2");
#endif
        if (E3_SetBmpFileInfo_2 == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_SetBmpFileInfo_2 in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_SetLanguageFile = (e3_SetLanguageFile)GetProcAddress(m_hEzdDLL, "E3_SetLanguageFile");
#else
        E3_SetLanguageFile = (e3_SetLanguageFile)dlsym(m_hEzdDLL, "E3_SetLanguageFile");
#endif
        if (E3_SetLanguageFile == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_SetLanguageFile in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_SetPenParam = (e3_SetPenParam)GetProcAddress(m_hEzdDLL, "E3_SetPenParam");
#else
        E3_SetPenParam = (e3_SetPenParam)dlsym(m_hEzdDLL, "E3_SetPenParam");
#endif
        if (E3_SetPenParam == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_SetPenParam in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_SetPenParamExt4 = (e3_SetPenParamExt4)GetProcAddress(m_hEzdDLL, "E3_SetPenParamExt4");
#else
        E3_SetPenParamExt4 = (e3_SetPenParamExt4)dlsym(m_hEzdDLL, "E3_SetPenParamExt4");
#endif
        if (E3_SetPenParamExt4 == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_SetPenParamExt4 in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_SetPenParamExt5 = (e3_SetPenParamExt5)GetProcAddress(m_hEzdDLL, "E3_SetPenParamExt5");
#else
        E3_SetPenParamExt5 = (e3_SetPenParamExt5)dlsym(m_hEzdDLL, "E3_SetPenParamExt5");
#endif
        if (E3_SetPenParamExt5 == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_SetPenParamExt5 in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_SetPenParamExtOutputIndex = (e3_SetPenParamExtOutputIndex)GetProcAddress(m_hEzdDLL, "E3_SetPenParamExtOutputIndex");
#else
        E3_SetPenParamExtOutputIndex = (e3_SetPenParamExtOutputIndex)dlsym(m_hEzdDLL, "E3_SetPenParamExtOutputIndex");
#endif
        if (E3_SetPenParamExtOutputIndex == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_SetPenParamExtOutputIndex in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_SetPenParamFreqRamp = (e3_SetPenParamFreqRamp)GetProcAddress(m_hEzdDLL, "E3_SetPenParamFreqRamp");
#else
        E3_SetPenParamFreqRamp = (e3_SetPenParamFreqRamp)dlsym(m_hEzdDLL, "E3_SetPenParamFreqRamp");
#endif
        if (E3_SetPenParamFreqRamp == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_SetPenParamFreqRamp in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_SetPenParamLaserLagTime = (e3_SetPenParamLaserLagTime)GetProcAddress(m_hEzdDLL, "E3_SetPenParamLaserLagTime");
#else
        E3_SetPenParamLaserLagTime = (e3_SetPenParamLaserLagTime)dlsym(m_hEzdDLL, "E3_SetPenParamLaserLagTime");
#endif
        if (E3_SetPenParamLaserLagTime == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_SetPenParamLaserLagTime in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_SetPenParamPowerRamp = (e3_SetPenParamPowerRamp)GetProcAddress(m_hEzdDLL, "E3_SetPenParamPowerRamp");
#else
        E3_SetPenParamPowerRamp = (e3_SetPenParamPowerRamp)dlsym(m_hEzdDLL, "E3_SetPenParamPowerRamp");
#endif
        if (E3_SetPenParamPowerRamp == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_SetPenParamPowerRamp in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_SetPenParamSkyWriting = (e3_SetPenParamSkyWriting)GetProcAddress(m_hEzdDLL, "E3_SetPenParamSkyWriting");
#else
        E3_SetPenParamSkyWriting = (e3_SetPenParamSkyWriting)dlsym(m_hEzdDLL, "E3_SetPenParamSkyWriting");
#endif
        if (E3_SetPenParamSkyWriting == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_SetPenParamSkyWriting in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_SetPenParamSpeedRamp = (e3_SetPenParamSpeedRamp)GetProcAddress(m_hEzdDLL, "E3_SetPenParamSpeedRamp");
#else
        E3_SetPenParamSpeedRamp = (e3_SetPenParamSpeedRamp)dlsym(m_hEzdDLL, "E3_SetPenParamSpeedRamp");
#endif
        if (E3_SetPenParamSpeedRamp == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_SetPenParamSpeedRamp in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_SetPenParamStep = (e3_SetPenParamStep)GetProcAddress(m_hEzdDLL, "E3_SetPenParamStep");
#else
        E3_SetPenParamStep = (e3_SetPenParamStep)dlsym(m_hEzdDLL, "E3_SetPenParamStep");
#endif
        if (E3_SetPenParamStep == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_SetPenParamStep in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_SetPenParamWeldWave = (e3_SetPenParamWeldWave)GetProcAddress(m_hEzdDLL, "E3_SetPenParamWeldWave");
#else
        E3_SetPenParamWeldWave = (e3_SetPenParamWeldWave)dlsym(m_hEzdDLL, "E3_SetPenParamWeldWave");
#endif
        if (E3_SetPenParamWeldWave == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_SetPenParamWeldWave in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_SetPenParamWeldWave2 = (e3_SetPenParamWeldWave2)GetProcAddress(m_hEzdDLL, "E3_SetPenParamWeldWave2");
#else
        E3_SetPenParamWeldWave2 = (e3_SetPenParamWeldWave2)dlsym(m_hEzdDLL, "E3_SetPenParamWeldWave2");
#endif
        if (E3_SetPenParamWeldWave2 == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_SetPenParamWeldWave2 in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_SetPenParamWobble = (e3_SetPenParamWobble)GetProcAddress(m_hEzdDLL, "E3_SetPenParamWobble");
#else
        E3_SetPenParamWobble = (e3_SetPenParamWobble)dlsym(m_hEzdDLL, "E3_SetPenParamWobble");
#endif
        if (E3_SetPenParamWobble == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_SetPenParamWobble in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_SetPenParamWobbleIncSpeed = (e3_SetPenParamWobbleIncSpeed)GetProcAddress(m_hEzdDLL, "E3_SetPenParamWobbleIncSpeed");
#else
        E3_SetPenParamWobbleIncSpeed = (e3_SetPenParamWobbleIncSpeed)dlsym(m_hEzdDLL, "E3_SetPenParamWobbleIncSpeed");
#endif
        if (E3_SetPenParamWobbleIncSpeed == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_SetPenParamWobbleIncSpeed in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_GetAllFontCount = (e3_GetAllFontCount)GetProcAddress(m_hEzdDLL, "E3_GetAllFontCount");
#else
        E3_GetAllFontCount = (e3_GetAllFontCount)dlsym(m_hEzdDLL, "E3_GetAllFontCount");
#endif
        if (E3_GetAllFontCount == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_GetAllFontCount in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_GetAllFontRecord = (e3_GetAllFontRecord)GetProcAddress(m_hEzdDLL, "E3_GetAllFontRecord");
#else
        E3_GetAllFontRecord = (e3_GetAllFontRecord)dlsym(m_hEzdDLL, "E3_GetAllFontRecord");
#endif
        if (E3_GetAllFontRecord == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_GetAllFontRecord in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_GetMeshSize = (e3_GetMeshSize)GetProcAddress(m_hEzdDLL, "E3_GetMeshSize");
#else
        E3_GetMeshSize = (e3_GetMeshSize)dlsym(m_hEzdDLL, "E3_GetMeshSize");
#endif
        if (E3_GetMeshSize == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_GetMeshSize in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_MarkerEnableFlyCorrectionToList = (e3_MarkerEnableFlyCorrectionToList)GetProcAddress(m_hEzdDLL, "E3_MarkerEnableFlyCorrectionToList");
#else
        E3_MarkerEnableFlyCorrectionToList = (e3_MarkerEnableFlyCorrectionToList)dlsym(m_hEzdDLL, "E3_MarkerEnableFlyCorrectionToList");
#endif
        if (E3_MarkerEnableFlyCorrectionToList == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_MarkerEnableFlyCorrectionToList in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_MarkerSetFlySimuSpeed = (e3_MarkerSetFlySimuSpeed)GetProcAddress(m_hEzdDLL, "E3_MarkerSetFlySimuSpeed");
#else
        E3_MarkerSetFlySimuSpeed = (e3_MarkerSetFlySimuSpeed)dlsym(m_hEzdDLL, "E3_MarkerSetFlySimuSpeed");
#endif
        if (E3_MarkerSetFlySimuSpeed == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_MarkerSetFlySimuSpeed in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_MarkerClearWaitForInputLock = (e3_MarkerClearWaitForInputLock)GetProcAddress(m_hEzdDLL, "E3_MarkerClearWaitForInputLock");
#else
        E3_MarkerClearWaitForInputLock = (e3_MarkerClearWaitForInputLock)dlsym(m_hEzdDLL, "E3_MarkerClearWaitForInputLock");
#endif
        if (E3_MarkerClearWaitForInputLock == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_MarkerClearWaitForInputLock in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_MarkerFlyEnableToList = (e3_MarkerFlyEnableToList)GetProcAddress(m_hEzdDLL, "E3_MarkerFlyEnableToList");
#else
        E3_MarkerFlyEnableToList = (e3_MarkerFlyEnableToList)dlsym(m_hEzdDLL, "E3_MarkerFlyEnableToList");
#endif
        if (E3_MarkerFlyEnableToList == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_MarkerFlyEnableToList in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_MarkerFlyResetDistanceToList = (e3_MarkerFlyResetDistanceToList)GetProcAddress(m_hEzdDLL, "E3_MarkerFlyResetDistanceToList");
#else
        E3_MarkerFlyResetDistanceToList = (e3_MarkerFlyResetDistanceToList)dlsym(m_hEzdDLL, "E3_MarkerFlyResetDistanceToList");
#endif
        if (E3_MarkerFlyResetDistanceToList == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_MarkerFlyResetDistanceToList in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_MarkerFlyWaitForDistToList = (e3_MarkerFlyWaitForDistToList)GetProcAddress(m_hEzdDLL, "E3_MarkerFlyWaitForDistToList");
#else
        E3_MarkerFlyWaitForDistToList = (e3_MarkerFlyWaitForDistToList)dlsym(m_hEzdDLL, "E3_MarkerFlyWaitForDistToList");
#endif
        if (E3_MarkerFlyWaitForDistToList == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_MarkerFlyWaitForDistToList in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_MarkerGetFlyEncoder = (e3_MarkerGetFlyEncoder)GetProcAddress(m_hEzdDLL, "E3_MarkerGetFlyEncoder");
#else
        E3_MarkerGetFlyEncoder = (e3_MarkerGetFlyEncoder)dlsym(m_hEzdDLL, "E3_MarkerGetFlyEncoder");
#endif
        if (E3_MarkerGetFlyEncoder == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_MarkerGetFlyEncoder in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_MarkerGetSpeedOfFly = (e3_MarkerGetSpeedOfFly)GetProcAddress(m_hEzdDLL, "E3_MarkerGetSpeedOfFly");
#else
        E3_MarkerGetSpeedOfFly = (e3_MarkerGetSpeedOfFly)dlsym(m_hEzdDLL, "E3_MarkerGetSpeedOfFly");
#endif
        if (E3_MarkerGetSpeedOfFly == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_MarkerGetSpeedOfFly in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_MarkerGetWritePort = (e3_MarkerGetWritePort)GetProcAddress(m_hEzdDLL, "E3_MarkerGetWritePort");
#else
        E3_MarkerGetWritePort = (e3_MarkerGetWritePort)dlsym(m_hEzdDLL, "E3_MarkerGetWritePort");
#endif
        if (E3_MarkerGetWritePort == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_MarkerGetWritePort in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_MarkerResetDistanceToList = (e3_MarkerResetDistanceToList)GetProcAddress(m_hEzdDLL, "E3_MarkerResetDistanceToList");
#else
        E3_MarkerResetDistanceToList = (e3_MarkerResetDistanceToList)dlsym(m_hEzdDLL, "E3_MarkerResetDistanceToList");
#endif
        if (E3_MarkerResetDistanceToList == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_MarkerResetDistanceToList in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_MarkerSetOutputPortWithMask = (e3_MarkerSetOutputPortWithMask)GetProcAddress(m_hEzdDLL, "E3_MarkerSetOutputPortWithMask");
#else
        E3_MarkerSetOutputPortWithMask = (e3_MarkerSetOutputPortWithMask)dlsym(m_hEzdDLL, "E3_MarkerSetOutputPortWithMask");
#endif
        if (E3_MarkerSetOutputPortWithMask == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_MarkerSetOutputPortWithMask in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_MarkerSetOutputPortWithMaskToList = (e3_MarkerSetOutputPortWithMaskToList)GetProcAddress(m_hEzdDLL, "E3_MarkerSetOutputPortWithMaskToList");
#else
        E3_MarkerSetOutputPortWithMaskToList = (e3_MarkerSetOutputPortWithMaskToList)dlsym(m_hEzdDLL, "E3_MarkerSetOutputPortWithMaskToList");
#endif
        if (E3_MarkerSetOutputPortWithMaskToList == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_MarkerSetOutputPortWithMaskToList in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_SetInputPortWorkMode = (e3_SetInputPortWorkMode)GetProcAddress(m_hEzdDLL, "E3_SetInputPortWorkMode");
#else
        E3_SetInputPortWorkMode = (e3_SetInputPortWorkMode)dlsym(m_hEzdDLL, "E3_SetInputPortWorkMode");
#endif
        if (E3_SetInputPortWorkMode == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_SetInputPortWorkMode in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_SplitTextToChars = (e3_SplitTextToChars)GetProcAddress(m_hEzdDLL, "E3_SplitTextToChars");
#else
        E3_SplitTextToChars = (e3_SplitTextToChars)dlsym(m_hEzdDLL, "E3_SplitTextToChars");
#endif
        if (E3_SplitTextToChars == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_SplitTextToChars in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_BitGetInfo = (e3_BitGetInfo)GetProcAddress(m_hEzdDLL, "E3_BitGetInfo");
#else
        E3_BitGetInfo = (e3_BitGetInfo)dlsym(m_hEzdDLL, "E3_BitGetInfo");
#endif
        if (E3_BitGetInfo == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_BitGetInfo in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_ChangeEntToCurve = (e3_ChangeEntToCurve)GetProcAddress(m_hEzdDLL, "E3_ChangeEntToCurve");
#else
        E3_ChangeEntToCurve = (e3_ChangeEntToCurve)dlsym(m_hEzdDLL, "E3_ChangeEntToCurve");
#endif
        if (E3_ChangeEntToCurve == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_ChangeEntToCurve in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_GetTextFontName = (e3_GetTextFontName)GetProcAddress(m_hEzdDLL, "E3_GetTextFontName");
#else
        E3_GetTextFontName = (e3_GetTextFontName)dlsym(m_hEzdDLL, "E3_GetTextFontName");
#endif
        if (E3_GetTextFontName == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_GetTextFontName in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_GroupEnt = (e3_GroupEnt)GetProcAddress(m_hEzdDLL, "E3_GroupEnt");
#else
        E3_GroupEnt = (e3_GroupEnt)dlsym(m_hEzdDLL, "E3_GroupEnt");
#endif
        if (E3_GroupEnt == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_GroupEnt in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_UnGroupEnt = (e3_UnGroupEnt)GetProcAddress(m_hEzdDLL, "E3_UnGroupEnt");
#else
        E3_UnGroupEnt = (e3_UnGroupEnt)dlsym(m_hEzdDLL, "E3_UnGroupEnt");
#endif
        if (E3_UnGroupEnt == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_UnGroupEnt in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_UnGroupEnt2 = (e3_UnGroupEnt2)GetProcAddress(m_hEzdDLL, "E3_UnGroupEnt2");
#else
        E3_UnGroupEnt2 = (e3_UnGroupEnt2)dlsym(m_hEzdDLL, "E3_UnGroupEnt2");
#endif
        if (E3_UnGroupEnt2 == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_UnGroupEnt2 in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_DrawEnt2 = (e3_DrawEnt2)GetProcAddress(m_hEzdDLL, "E3_DrawEnt2");
#else
        E3_DrawEnt2 = (e3_DrawEnt2)dlsym(m_hEzdDLL, "E3_DrawEnt2");
#endif
        if (E3_DrawEnt2 == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_DrawEnt2 in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_DrawEnt3 = (e3_DrawEnt3)GetProcAddress(m_hEzdDLL, "E3_DrawEnt3");
#else
        E3_DrawEnt3 = (e3_DrawEnt3)dlsym(m_hEzdDLL, "E3_DrawEnt3");
#endif
        if (E3_DrawEnt3 == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_DrawEnt3 in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_GetEzdFilePrevBitmap = (e3_GetEzdFilePrevBitmap)GetProcAddress(m_hEzdDLL, "E3_GetEzdFilePrevBitmap");
#else
        E3_GetEzdFilePrevBitmap = (e3_GetEzdFilePrevBitmap)dlsym(m_hEzdDLL, "E3_GetEzdFilePrevBitmap");
#endif
        if (E3_GetEzdFilePrevBitmap == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_GetEzdFilePrevBitmap in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_MarkerConditionJumpToIndexToList = (e3_MarkerConditionJumpToIndexToList)GetProcAddress(m_hEzdDLL, "E3_MarkerConditionJumpToIndexToList");
#else
        E3_MarkerConditionJumpToIndexToList = (e3_MarkerConditionJumpToIndexToList)dlsym(m_hEzdDLL, "E3_MarkerConditionJumpToIndexToList");
#endif
        if (E3_MarkerConditionJumpToIndexToList == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_MarkerConditionJumpToIndexToList in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_MarkerGetFlyCameraObjectCount = (e3_MarkerGetFlyCameraObjectCount)GetProcAddress(m_hEzdDLL, "E3_MarkerGetFlyCameraObjectCount");
#else
        E3_MarkerGetFlyCameraObjectCount = (e3_MarkerGetFlyCameraObjectCount)dlsym(m_hEzdDLL, "E3_MarkerGetFlyCameraObjectCount");
#endif
        if (E3_MarkerGetFlyCameraObjectCount == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_MarkerGetFlyCameraObjectCount in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_MarkerSetIndexToList = (e3_MarkerSetIndexToList)GetProcAddress(m_hEzdDLL, "E3_MarkerSetIndexToList");
#else
        E3_MarkerSetIndexToList = (e3_MarkerSetIndexToList)dlsym(m_hEzdDLL, "E3_MarkerSetIndexToList");
#endif
        if (E3_MarkerSetIndexToList == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_MarkerSetIndexToList in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_MarkerSetTransformMatrix = (e3_MarkerSetTransformMatrix)GetProcAddress(m_hEzdDLL, "E3_MarkerSetTransformMatrix");
#else
        E3_MarkerSetTransformMatrix = (e3_MarkerSetTransformMatrix)dlsym(m_hEzdDLL, "E3_MarkerSetTransformMatrix");
#endif
        if (E3_MarkerSetTransformMatrix == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_MarkerSetTransformMatrix in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_MarkerSetTransformMatrix2 = (e3_MarkerSetTransformMatrix2)GetProcAddress(m_hEzdDLL, "E3_MarkerSetTransformMatrix2");
#else
        E3_MarkerSetTransformMatrix2 = (e3_MarkerSetTransformMatrix2)dlsym(m_hEzdDLL, "E3_MarkerSetTransformMatrix2");
#endif
        if (E3_MarkerSetTransformMatrix2 == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_MarkerSetTransformMatrix2 in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_MarkerSetTransformMatrixByIndex = (e3_MarkerSetTransformMatrixByIndex)GetProcAddress(m_hEzdDLL, "E3_MarkerSetTransformMatrixByIndex");
#else
        E3_MarkerSetTransformMatrixByIndex = (e3_MarkerSetTransformMatrixByIndex)dlsym(m_hEzdDLL, "E3_MarkerSetTransformMatrixByIndex");
#endif
        if (E3_MarkerSetTransformMatrixByIndex == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_MarkerSetTransformMatrixByIndex in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_OpenFileToEntMgr = (e3_OpenFileToEntMgr)GetProcAddress(m_hEzdDLL, "E3_OpenFileToEntMgr");
#else
        E3_OpenFileToEntMgr = (e3_OpenFileToEntMgr)dlsym(m_hEzdDLL, "E3_OpenFileToEntMgr");
#endif
        if (E3_OpenFileToEntMgr == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_OpenFileToEntMgr in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_OpenFileToEntMgr2 = (e3_OpenFileToEntMgr2)GetProcAddress(m_hEzdDLL, "E3_OpenFileToEntMgr2");
#else
        E3_OpenFileToEntMgr2 = (e3_OpenFileToEntMgr2)dlsym(m_hEzdDLL, "E3_OpenFileToEntMgr2");
#endif
        if (E3_OpenFileToEntMgr2 == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_OpenFileToEntMgr2 in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_SetAxisParam2 = (e3_SetAxisParam2)GetProcAddress(m_hEzdDLL, "E3_SetAxisParam2");
#else
        E3_SetAxisParam2 = (e3_SetAxisParam2)dlsym(m_hEzdDLL, "E3_SetAxisParam2");
#endif
        if (E3_SetAxisParam2 == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_SetAxisParam2 in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_SetAxisParam = (e3_SetAxisParam)GetProcAddress(m_hEzdDLL, "E3_SetAxisParam");
#else
        E3_SetAxisParam = (e3_SetAxisParam)dlsym(m_hEzdDLL, "E3_SetAxisParam");
#endif
        if (E3_SetAxisParam == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_SetAxisParam in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_SetAxisSpeedParam = (e3_SetAxisSpeedParam)GetProcAddress(m_hEzdDLL, "E3_SetAxisSpeedParam");
#else
        E3_SetAxisSpeedParam = (e3_SetAxisSpeedParam)dlsym(m_hEzdDLL, "E3_SetAxisSpeedParam");
#endif
        if (E3_SetAxisSpeedParam == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_SetAxisSpeedParam in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_AxisHome = (e3_AxisHome)GetProcAddress(m_hEzdDLL, "E3_AxisHome");
#else
        E3_AxisHome = (e3_AxisHome)dlsym(m_hEzdDLL, "E3_AxisHome");
#endif
        if (E3_AxisHome == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_AxisHome in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_AxisHome2 = (e3_AxisHome2)GetProcAddress(m_hEzdDLL, "E3_AxisHome2");
#else
        E3_AxisHome2 = (e3_AxisHome2)dlsym(m_hEzdDLL, "E3_AxisHome2");
#endif
        if (E3_AxisHome2 == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_AxisHome2 in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_AxisMoveTo = (e3_AxisMoveTo)GetProcAddress(m_hEzdDLL, "E3_AxisMoveTo");
#else
        E3_AxisMoveTo = (e3_AxisMoveTo)dlsym(m_hEzdDLL, "E3_AxisMoveTo");
#endif
        if (E3_AxisMoveTo == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_AxisMoveTo in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_AxisSetFlag = (e3_AxisSetFlag)GetProcAddress(m_hEzdDLL, "E3_AxisSetFlag");
#else
        E3_AxisSetFlag = (e3_AxisSetFlag)dlsym(m_hEzdDLL, "E3_AxisSetFlag");
#endif
        if (E3_AxisSetFlag == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_AxisSetFlag in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_AxisStopMoving = (e3_AxisStopMoving)GetProcAddress(m_hEzdDLL, "E3_AxisStopMoving");
#else
        E3_AxisStopMoving = (e3_AxisStopMoving)dlsym(m_hEzdDLL, "E3_AxisStopMoving");
#endif
        if (E3_AxisStopMoving == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_AxisStopMoving in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_GetAxisCoor = (e3_GetAxisCoor)GetProcAddress(m_hEzdDLL, "E3_GetAxisCoor");
#else
        E3_GetAxisCoor = (e3_GetAxisCoor)dlsym(m_hEzdDLL, "E3_GetAxisCoor");
#endif
        if (E3_GetAxisCoor == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_GetAxisCoor in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_GetAxisFBCoor = (e3_GetAxisFBCoor)GetProcAddress(m_hEzdDLL, "E3_GetAxisFBCoor");
#else
        E3_GetAxisFBCoor = (e3_GetAxisFBCoor)dlsym(m_hEzdDLL, "E3_GetAxisFBCoor");
#endif
        if (E3_GetAxisFBCoor == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_GetAxisFBCoor in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_GetAxisParam = (e3_GetAxisParam)GetProcAddress(m_hEzdDLL, "E3_GetAxisParam");
#else
        E3_GetAxisParam = (e3_GetAxisParam)dlsym(m_hEzdDLL, "E3_GetAxisParam");
#endif
        if (E3_GetAxisParam == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_GetAxisParam in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_GetAxisStatus = (e3_GetAxisStatus)GetProcAddress(m_hEzdDLL, "E3_GetAxisStatus");
#else
        E3_GetAxisStatus = (e3_GetAxisStatus)dlsym(m_hEzdDLL, "E3_GetAxisStatus");
#endif
        if (E3_GetAxisStatus == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_GetAxisStatus in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_InitAllAxis = (e3_InitAllAxis)GetProcAddress(m_hEzdDLL, "E3_InitAllAxis");
#else
        E3_InitAllAxis = (e3_InitAllAxis)dlsym(m_hEzdDLL, "E3_InitAllAxis");
#endif
        if (E3_InitAllAxis == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_InitAllAxis in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_SetCfgFileParam = (e3_SetCfgFileParam)GetProcAddress(m_hEzdDLL, "E3_SetCfgFileParam");
#else
        E3_SetCfgFileParam = (e3_SetCfgFileParam)dlsym(m_hEzdDLL, "E3_SetCfgFileParam");
#endif
        if (E3_SetCfgFileParam == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_SetCfgFileParam in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_SetEntHatchParam = (e3_SetEntHatchParam)GetProcAddress(m_hEzdDLL, "E3_SetEntHatchParam");
#else
        E3_SetEntHatchParam = (e3_SetEntHatchParam)dlsym(m_hEzdDLL, "E3_SetEntHatchParam");
#endif
        if (E3_SetEntHatchParam == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_SetEntHatchParam in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_FlyWaitCameraPositioningToList = (e3_FlyWaitCameraPositioningToList)GetProcAddress(m_hEzdDLL, "E3_FlyWaitCameraPositioningToList");
#else
        E3_FlyWaitCameraPositioningToList = (e3_FlyWaitCameraPositioningToList)dlsym(m_hEzdDLL, "E3_FlyWaitCameraPositioningToList");
#endif
        if (E3_FlyWaitCameraPositioningToList == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_FlyWaitCameraPositioningToList in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_MarkerAutoSelectListMatirxToList2 = (e3_MarkerAutoSelectListMatirxToList2)GetProcAddress(m_hEzdDLL, "E3_MarkerAutoSelectListMatirxToList2");
#else
        E3_MarkerAutoSelectListMatirxToList2 = (e3_MarkerAutoSelectListMatirxToList2)dlsym(m_hEzdDLL, "E3_MarkerAutoSelectListMatirxToList2");
#endif
        if (E3_MarkerAutoSelectListMatirxToList2 == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_MarkerAutoSelectListMatirxToList2 in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_MarkerSelectTransMatirxToList = (e3_MarkerSelectTransMatirxToList)GetProcAddress(m_hEzdDLL, "E3_MarkerSelectTransMatirxToList");
#else
        E3_MarkerSelectTransMatirxToList = (e3_MarkerSelectTransMatirxToList)dlsym(m_hEzdDLL, "E3_MarkerSelectTransMatirxToList");
#endif
        if (E3_MarkerSelectTransMatirxToList == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_MarkerSelectTransMatirxToList in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_MarkerSelectTransMatirxToList2 = (e3_MarkerSelectTransMatirxToList2)GetProcAddress(m_hEzdDLL, "E3_MarkerSelectTransMatirxToList2");
#else
        E3_MarkerSelectTransMatirxToList2 = (e3_MarkerSelectTransMatirxToList2)dlsym(m_hEzdDLL, "E3_MarkerSelectTransMatirxToList2");
#endif
        if (E3_MarkerSelectTransMatirxToList2 == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_MarkerSelectTransMatirxToList2 in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_MarkerSetRotateMoveParam = (e3_MarkerSetRotateMoveParam)GetProcAddress(m_hEzdDLL, "E3_MarkerSetRotateMoveParam");
#else
        E3_MarkerSetRotateMoveParam = (e3_MarkerSetRotateMoveParam)dlsym(m_hEzdDLL, "E3_MarkerSetRotateMoveParam");
#endif
        if (E3_MarkerSetRotateMoveParam == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_MarkerSetRotateMoveParam in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_MarkerSetTransformMatrixByIndex2 = (e3_MarkerSetTransformMatrixByIndex2)GetProcAddress(m_hEzdDLL, "E3_MarkerSetTransformMatrixByIndex2");
#else
        E3_MarkerSetTransformMatrixByIndex2 = (e3_MarkerSetTransformMatrixByIndex2)dlsym(m_hEzdDLL, "E3_MarkerSetTransformMatrixByIndex2");
#endif
        if (E3_MarkerSetTransformMatrixByIndex2 == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_MarkerSetTransformMatrixByIndex2 in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_MarkerSetTransformMatrixByIndex3 = (e3_MarkerSetTransformMatrixByIndex3)GetProcAddress(m_hEzdDLL, "E3_MarkerSetTransformMatrixByIndex3");
#else
        E3_MarkerSetTransformMatrixByIndex3 = (e3_MarkerSetTransformMatrixByIndex3)dlsym(m_hEzdDLL, "E3_MarkerSetTransformMatrixByIndex3");
#endif
        if (E3_MarkerSetTransformMatrixByIndex3 == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_MarkerSetTransformMatrixByIndex3 in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_ScaleEnt = (e3_ScaleEnt)GetProcAddress(m_hEzdDLL, "E3_ScaleEnt");
#else
        E3_ScaleEnt = (e3_ScaleEnt)dlsym(m_hEzdDLL, "E3_ScaleEnt");
#endif
        if (E3_ScaleEnt == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_ScaleEnt in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_StartMainLoopIOCheckProcess = (e3_StartMainLoopIOCheckProcess)GetProcAddress(m_hEzdDLL, "E3_StartMainLoopIOCheckProcess");
#else
        E3_StartMainLoopIOCheckProcess = (e3_StartMainLoopIOCheckProcess)dlsym(m_hEzdDLL, "E3_StartMainLoopIOCheckProcess");
#endif
        if (E3_StartMainLoopIOCheckProcess == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_StartMainLoopIOCheckProcess in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_MarkerUpdateParam = (e3_MarkerUpdateParam)GetProcAddress(m_hEzdDLL, "E3_MarkerUpdateParam");
#else
        E3_MarkerUpdateParam = (e3_MarkerUpdateParam)dlsym(m_hEzdDLL, "E3_MarkerUpdateParam");
#endif
        if (E3_MarkerUpdateParam == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_MarkerUpdateParam in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_GetEntInfo = (e3_GetEntInfo)GetProcAddress(m_hEzdDLL, "E3_GetEntInfo");
#else
        E3_GetEntInfo = (e3_GetEntInfo)dlsym(m_hEzdDLL, "E3_GetEntInfo");
#endif
        if (E3_GetEntInfo == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_GetEntInfo in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_SetEntInfo = (e3_SetEntInfo)GetProcAddress(m_hEzdDLL, "E3_SetEntInfo");
#else
        E3_SetEntInfo = (e3_SetEntInfo)dlsym(m_hEzdDLL, "E3_SetEntInfo");
#endif
        if (E3_SetEntInfo == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_SetEntInfo in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_SetEntInfo_2 = (e3_SetEntInfo_2)GetProcAddress(m_hEzdDLL, "E3_SetEntInfo_2");
#else
        E3_SetEntInfo_2 = (e3_SetEntInfo_2)dlsym(m_hEzdDLL, "E3_SetEntInfo_2");
#endif
        if (E3_SetEntInfo_2 == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_SetEntInfo_2 in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_MarkerGetOutputPortStatus = (e3_MarkerGetOutputPortStatus)GetProcAddress(m_hEzdDLL, "E3_MarkerGetOutputPortStatus");
#else
        E3_MarkerGetOutputPortStatus = (e3_MarkerGetOutputPortStatus)dlsym(m_hEzdDLL, "E3_MarkerGetOutputPortStatus");
#endif
        if (E3_MarkerGetOutputPortStatus == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_MarkerGetOutputPortStatus in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_ChangeEntToPoints = (e3_ChangeEntToPoints)GetProcAddress(m_hEzdDLL, "E3_ChangeEntToPoints");
#else
        E3_ChangeEntToPoints = (e3_ChangeEntToPoints)dlsym(m_hEzdDLL, "E3_ChangeEntToPoints");
#endif
        if (E3_ChangeEntToPoints == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_ChangeEntToPoints in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_MarkerOneCurveToList2 = (e3_MarkerOneCurveToList2)GetProcAddress(m_hEzdDLL, "E3_MarkerOneCurveToList2");
#else
        E3_MarkerOneCurveToList2 = (e3_MarkerOneCurveToList2)dlsym(m_hEzdDLL, "E3_MarkerOneCurveToList2");
#endif
        if (E3_MarkerOneCurveToList2 == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_MarkerOneCurveToList2 in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_MarkerGetLaserBoardTypeID = (e3_MarkerGetLaserBoardTypeID)GetProcAddress(m_hEzdDLL, "E3_MarkerGetLaserBoardTypeID");
#else
        E3_MarkerGetLaserBoardTypeID = (e3_MarkerGetLaserBoardTypeID)dlsym(m_hEzdDLL, "E3_MarkerGetLaserBoardTypeID");
#endif
        if (E3_MarkerGetLaserBoardTypeID == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_MarkerGetLaserBoardTypeID in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_GetTextElementInfo = (e3_GetTextElementInfo)GetProcAddress(m_hEzdDLL, "E3_GetTextElementInfo");
#else
        E3_GetTextElementInfo = (e3_GetTextElementInfo)dlsym(m_hEzdDLL, "E3_GetTextElementInfo");
#endif
        if (E3_GetTextElementInfo == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_GetTextElementInfo in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_GetTextElementStr = (e3_GetTextElementStr)GetProcAddress(m_hEzdDLL, "E3_GetTextElementStr");
#else
        E3_GetTextElementStr = (e3_GetTextElementStr)dlsym(m_hEzdDLL, "E3_GetTextElementStr");
#endif
        if (E3_GetTextElementStr == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_GetTextElementStr in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_GetTextElementSerialNo = (e3_GetTextElementSerialNo)GetProcAddress(m_hEzdDLL, "E3_GetTextElementSerialNo");
#else
        E3_GetTextElementSerialNo = (e3_GetTextElementSerialNo)dlsym(m_hEzdDLL, "E3_GetTextElementSerialNo");
#endif
        if (E3_GetTextElementSerialNo == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_GetTextElementSerialNo in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_GetTextElementSerialNo2 = (e3_GetTextElementSerialNo2)GetProcAddress(m_hEzdDLL, "E3_GetTextElementSerialNo2");
#else
        E3_GetTextElementSerialNo2 = (e3_GetTextElementSerialNo2)dlsym(m_hEzdDLL, "E3_GetTextElementSerialNo2");
#endif
        if (E3_GetTextElementSerialNo2 == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_GetTextElementSerialNo2 in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_GetTextElementDate = (e3_GetTextElementDate)GetProcAddress(m_hEzdDLL, "E3_GetTextElementDate");
#else
        E3_GetTextElementDate = (e3_GetTextElementDate)dlsym(m_hEzdDLL, "E3_GetTextElementDate");
#endif
        if (E3_GetTextElementDate == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_GetTextElementDate in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_GetTextElementDate2 = (e3_GetTextElementDate2)GetProcAddress(m_hEzdDLL, "E3_GetTextElementDate2");
#else
        E3_GetTextElementDate2 = (e3_GetTextElementDate2)dlsym(m_hEzdDLL, "E3_GetTextElementDate2");
#endif
        if (E3_GetTextElementDate2 == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_GetTextElementDate2 in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_GetTextElementTime = (e3_GetTextElementTime)GetProcAddress(m_hEzdDLL, "E3_GetTextElementTime");
#else
        E3_GetTextElementTime = (e3_GetTextElementTime)dlsym(m_hEzdDLL, "E3_GetTextElementTime");
#endif
        if (E3_GetTextElementTime == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_GetTextElementTime in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_GetTextElementTime2 = (e3_GetTextElementTime2)GetProcAddress(m_hEzdDLL, "E3_GetTextElementTime2");
#else
        E3_GetTextElementTime2 = (e3_GetTextElementTime2)dlsym(m_hEzdDLL, "E3_GetTextElementTime2");
#endif
        if (E3_GetTextElementTime2 == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_GetTextElementTime2 in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_GetTextElementTcpip = (e3_GetTextElementTcpip)GetProcAddress(m_hEzdDLL, "E3_GetTextElementTcpip");
#else
        E3_GetTextElementTcpip = (e3_GetTextElementTcpip)dlsym(m_hEzdDLL, "E3_GetTextElementTcpip");
#endif
        if (E3_GetTextElementTcpip == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_GetTextElementTcpip in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_GetTextElementCom = (e3_GetTextElementCom)GetProcAddress(m_hEzdDLL, "E3_GetTextElementCom");
#else
        E3_GetTextElementCom = (e3_GetTextElementCom)dlsym(m_hEzdDLL, "E3_GetTextElementCom");
#endif
        if (E3_GetTextElementCom == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_GetTextElementCom in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_GetTextElementFile = (e3_GetTextElementFile)GetProcAddress(m_hEzdDLL, "E3_GetTextElementFile");
#else
        E3_GetTextElementFile = (e3_GetTextElementFile)dlsym(m_hEzdDLL, "E3_GetTextElementFile");
#endif
        if (E3_GetTextElementFile == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_GetTextElementFile in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_GetTextElementKB = (e3_GetTextElementKB)GetProcAddress(m_hEzdDLL, "E3_GetTextElementKB");
#else
        E3_GetTextElementKB = (e3_GetTextElementKB)dlsym(m_hEzdDLL, "E3_GetTextElementKB");
#endif
        if (E3_GetTextElementKB == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_GetTextElementKB in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_GetTextElementSql = (e3_GetTextElementSql)GetProcAddress(m_hEzdDLL, "E3_GetTextElementSql");
#else
        E3_GetTextElementSql = (e3_GetTextElementSql)dlsym(m_hEzdDLL, "E3_GetTextElementSql");
#endif
        if (E3_GetTextElementSql == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_GetTextElementSql in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_ModifyTextElement = (e3_ModifyTextElement)GetProcAddress(m_hEzdDLL, "E3_ModifyTextElement");
#else
        E3_ModifyTextElement = (e3_ModifyTextElement)dlsym(m_hEzdDLL, "E3_ModifyTextElement");
#endif
        if (E3_ModifyTextElement == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_ModifyTextElement in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_SnTextEntRefresh = (e3_SnTextEntRefresh)GetProcAddress(m_hEzdDLL, "E3_SnTextEntRefresh");
#else
        E3_SnTextEntRefresh = (e3_SnTextEntRefresh)dlsym(m_hEzdDLL, "E3_SnTextEntRefresh");
#endif
        if (E3_SnTextEntRefresh == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_SnTextEntRefresh in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_UpdateTextElement = (e3_UpdateTextElement)GetProcAddress(m_hEzdDLL, "E3_UpdateTextElement");
#else
        E3_UpdateTextElement = (e3_UpdateTextElement)dlsym(m_hEzdDLL, "E3_UpdateTextElement");
#endif
        if (E3_UpdateTextElement == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_UpdateTextElement in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_VariableEntRefresh = (e3_VariableEntRefresh)GetProcAddress(m_hEzdDLL, "E3_VariableEntRefresh");
#else
        E3_VariableEntRefresh = (e3_VariableEntRefresh)dlsym(m_hEzdDLL, "E3_VariableEntRefresh");
#endif
        if (E3_VariableEntRefresh == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_VariableEntRefresh in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_GetTextElementMask = (e3_GetTextElementMask)GetProcAddress(m_hEzdDLL, "E3_GetTextElementMask");
#else
        E3_GetTextElementMask = (e3_GetTextElementMask)dlsym(m_hEzdDLL, "E3_GetTextElementMask");
#endif
        if (E3_GetTextElementMask == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_GetTextElementMask in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_GetTextBarcodeInfo8 = (e3_GetTextBarcodeInfo8)GetProcAddress(m_hEzdDLL, "E3_GetTextBarcodeInfo8");
#else
        E3_GetTextBarcodeInfo8 = (e3_GetTextBarcodeInfo8)dlsym(m_hEzdDLL, "E3_GetTextBarcodeInfo8");
#endif
        if (E3_GetTextBarcodeInfo8 == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_GetTextBarcodeInfo8 in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_SetTextBarcodeInfo8 = (e3_SetTextBarcodeInfo8)GetProcAddress(m_hEzdDLL, "E3_SetTextBarcodeInfo8");
#else
        E3_SetTextBarcodeInfo8 = (e3_SetTextBarcodeInfo8)dlsym(m_hEzdDLL, "E3_SetTextBarcodeInfo8");
#endif
        if (E3_SetTextBarcodeInfo8 == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_SetTextBarcodeInfo8 in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_SetEntHide = (e3_SetEntHide)GetProcAddress(m_hEzdDLL, "E3_SetEntHide");
#else
        E3_SetEntHide = (e3_SetEntHide)dlsym(m_hEzdDLL, "E3_SetEntHide");
#endif
        if (E3_SetEntHide == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_SetEntHide in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_UnGroupEnt3 = (e3_UnGroupEnt3)GetProcAddress(m_hEzdDLL, "E3_UnGroupEnt3");
#else
        E3_UnGroupEnt3 = (e3_UnGroupEnt3)dlsym(m_hEzdDLL, "E3_UnGroupEnt3");
#endif
        if (E3_UnGroupEnt3 == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_UnGroupEnt3 in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_SetControllerInterfaceType = (e3_SetControllerInterfaceType)GetProcAddress(m_hEzdDLL, "E3_SetControllerInterfaceType");
#else
        E3_SetControllerInterfaceType = (e3_SetControllerInterfaceType)dlsym(m_hEzdDLL, "E3_SetControllerInterfaceType");
#endif
        if (E3_SetControllerInterfaceType == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_SetControllerInterfaceType in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_HatchEnt3 = (e3_HatchEnt3)GetProcAddress(m_hEzdDLL, "E3_HatchEnt3");
#else
        E3_HatchEnt3 = (e3_HatchEnt3)dlsym(m_hEzdDLL, "E3_HatchEnt3");
#endif
        if (E3_HatchEnt3 == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_HatchEnt3 in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_GetPenParamPower2 = (e3_GetPenParamPower2)GetProcAddress(m_hEzdDLL, "E3_GetPenParamPower2");
#else
        E3_GetPenParamPower2 = (e3_GetPenParamPower2)dlsym(m_hEzdDLL, "E3_GetPenParamPower2");
#endif
        if (E3_GetPenParamPower2 == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_GetPenParamPower2 in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_SetPenParamPower2 = (e3_SetPenParamPower2)GetProcAddress(m_hEzdDLL, "E3_SetPenParamPower2");
#else
        E3_SetPenParamPower2 = (e3_SetPenParamPower2)dlsym(m_hEzdDLL, "E3_SetPenParamPower2");
#endif
        if (E3_SetPenParamPower2 == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_SetPenParamPower2 in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_SetSysParamInt = (e3_SetSysParamInt)GetProcAddress(m_hEzdDLL, "E3_SetSysParamInt");
#else
        E3_SetSysParamInt = (e3_SetSysParamInt)dlsym(m_hEzdDLL, "E3_SetSysParamInt");
#endif
        if (E3_SetSysParamInt == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_SetSysParamInt in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_GetSysParamInt = (e3_GetSysParamInt)GetProcAddress(m_hEzdDLL, "E3_GetSysParamInt");
#else
        E3_GetSysParamInt = (e3_GetSysParamInt)dlsym(m_hEzdDLL, "E3_GetSysParamInt");
#endif
        if (E3_GetSysParamInt == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_GetSysParamInt in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_VariableEntRefresh_NoSN = (e3_VariableEntRefresh_NoSN)GetProcAddress(m_hEzdDLL, "E3_VariableEntRefresh_NoSN");
#else
        E3_VariableEntRefresh_NoSN = (e3_VariableEntRefresh_NoSN)dlsym(m_hEzdDLL, "E3_VariableEntRefresh_NoSN");
#endif
        if (E3_VariableEntRefresh_NoSN == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_VariableEntRefresh_NoSN in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_VariableEntRefresh2 = (e3_VariableEntRefresh2)GetProcAddress(m_hEzdDLL, "E3_VariableEntRefresh2");
#else
        E3_VariableEntRefresh2 = (e3_VariableEntRefresh2)dlsym(m_hEzdDLL, "E3_VariableEntRefresh2");
#endif
        if (E3_VariableEntRefresh2 == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_VariableEntRefresh2 in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_GetDllVersion = (e3_GetDllVersion)GetProcAddress(m_hEzdDLL, "E3_GetDllVersion");
#else
        E3_GetDllVersion = (e3_GetDllVersion)dlsym(m_hEzdDLL, "E3_GetDllVersion");
#endif
        if (E3_GetDllVersion == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_GetDllVersion in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_CreateSpiral_3 = (e3_CreateSpiral_3)GetProcAddress(m_hEzdDLL, "E3_CreateSpiral_3");
#else
        E3_CreateSpiral_3 = (e3_CreateSpiral_3)dlsym(m_hEzdDLL, "E3_CreateSpiral_3");
#endif
        if (E3_CreateSpiral_3 == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_CreateSpiral_3 in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_MarkerGetInputPortStatus = (e3_MarkerGetInputPortStatus)GetProcAddress(m_hEzdDLL, "E3_MarkerGetInputPortStatus");
#else
        E3_MarkerGetInputPortStatus = (e3_MarkerGetInputPortStatus)dlsym(m_hEzdDLL, "E3_MarkerGetInputPortStatus");
#endif
        if (E3_MarkerGetInputPortStatus == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_MarkerGetInputPortStatus in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_MarkerClearInputPortState = (e3_MarkerClearInputPortState)GetProcAddress(m_hEzdDLL, "E3_MarkerClearInputPortState");
#else
        E3_MarkerClearInputPortState = (e3_MarkerClearInputPortState)dlsym(m_hEzdDLL, "E3_MarkerClearInputPortState");
#endif
        if (E3_MarkerClearInputPortState == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_MarkerClearInputPortState in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_MarkerClearInputPort0State = (e3_MarkerClearInputPort0State)GetProcAddress(m_hEzdDLL, "E3_MarkerClearInputPort0State");
#else
        E3_MarkerClearInputPort0State = (e3_MarkerClearInputPort0State)dlsym(m_hEzdDLL, "E3_MarkerClearInputPort0State");
#endif
        if (E3_MarkerClearInputPort0State == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_MarkerClearInputPort0State in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_MarkerListNop = (e3_MarkerListNop)GetProcAddress(m_hEzdDLL, "E3_MarkerListNop");
#else
        E3_MarkerListNop = (e3_MarkerListNop)dlsym(m_hEzdDLL, "E3_MarkerListNop");
#endif
        if (E3_MarkerListNop == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_MarkerListNop in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

#ifdef _WIN32
        E3_SetHatchStop = (e3_SetHatchStop)GetProcAddress(m_hEzdDLL, "E3_SetHatchStop");
#else
        E3_SetHatchStop = (e3_SetHatchStop)dlsym(m_hEzdDLL, "E3_SetHatchStop");
#endif
        if (E3_SetHatchStop == nullptr)
        {
        if (logback)
        	{
        		(logback)(_T("Can not find funtion E3_SetHatchStop in Ezcad3Kernel.dll!"), 0, LogLevel::Normal, LogType::Warning);
        	}
        }

    }
}

        /// <summary> 
        /// 封装的初始化函数,用于支持网口卡. 
        /// </summary> 
        /// <param name="basePath">开发库根目录路径.</param> 
        /// <param name="mode">初始化模式.</param> 
        /// <param name="otherCfgPath">如果配置的目录不在开发库目录下,这个参数指定,如果在同一目录下,给null.</param> 
        /// <returns></returns> 
E3_ERR EzdKernel::Initial(TCHAR* basePath, InitialMode mode, TCHAR* otherCfgPath)
{
    wstring basePathStr(basePath);
    if (otherCfgPath != nullptr)
    {
        basePathStr = wstring(otherCfgPath);
    }
#ifdef WIN32
    size_t start_pos = 0;
    while ((start_pos = basePathStr.find(L"/", start_pos)) != std::string::npos) {
        basePathStr = basePathStr.replace(start_pos, 1, L"\\");
        start_pos += 1; // 移动到替换后的部分后面
    }
    wstring conttrollerFile = basePathStr + L"\\PARAM\\Controller.ini";
#else
    wstring conttrollerFile = basePathStr + L"/PARAM/Controller.ini";
#endif
    INIParser ctrlIni;
    if (!ctrlIni.ReadINI(conttrollerFile))
    {
        return E3_ERR::ERR_OPENFILE;
    }
    //0=USB,1=Eth,2=SPI;
    int initType = 0;
    if (mode == InitialMode::ByCfg)
    {
        string str = ctrlIni.GetValue("PARAM", "TYPE");
        if (str == "USB")
        {
            cout << "cfg mode->USB!" << endl;
#ifdef _WIN32
            initType = 0;
#else
            initType = 2;
#endif
        }
        else
        {
            cout << "cfg mode->Ethernet!" << endl;
            initType = 1;
        }
    }
    if (initType == 1 || mode == InitialMode::Ethernet_ChangeCfg || mode == InitialMode::Ethernet2_ChangeCfg)
    {
        cout << "initial mode->Ethernet!" << endl;
        if (mode == InitialMode::Ethernet_ChangeCfg)
            ctrlIni.SetValue("PARAM", "TYPE", "ETHERNET");
        if (mode == InitialMode::Ethernet2_ChangeCfg)
            ctrlIni.SetValue("PARAM", "TYPE", "ETHERNET2");
#ifdef _WIN32
        wstring	qstrFile = basePathStr + L"\\PARAM\\EtherNetcfg.ini";
#else
        wstring	qstrFile = basePathStr + L"/PARAM/EtherNetcfg.ini";
#endif
        if (!ini_parser.ReadINI(qstrFile))
        {
            return E3_ERR::ERR_OPENFILE;
        }
        //
        string cardIP[32];
        for (int i = 0; i < 32; i++)
        {
            string val = ini_parser.GetValue(to_string(i), "IP");
            if (val != "")
            {
                cout << "read card config ip->idx->" << i << "->ip->" << val << endl;
                cardIP[i] = val;
            }
        }
#ifdef _WIN32
        //EthLink
        E3_WSAStartUp();
#else
        E3_SetControllerInterfaceType(0x7);//ethernet
#endif
        for (int i = 0; i < 32; i++)
        {
            if (cardIP[i] == "")
            {
                continue;
            }
            unsigned int curIP = 0;
            char* a = new char[cardIP[i].length() + 1];
            strcpy(a, cardIP[i].data());
            E3_EthConvertStringToIP(a, curIP);
            delete[] a;
            if (curIP)
            {
                E3_ERR err = E3_EthRegisterCardByIP(curIP);
                cout << "register card ip ->" << cardIP[i] << "->err->" << err << endl;
            }
        }
    }
    else if (initType == 2 || mode == InitialMode::SPI || mode == InitialMode::SPI_ChangeCfg)
    {
        cout << "initial mode->SPI!" << endl;
        if (mode == InitialMode::SPI_ChangeCfg)
            ctrlIni.SetValue("PARAM", "TYPE", "USB");
        //Type = 0x3, Linux Usb
        //Type = 0x8, Linux SPI
#ifdef __linux__
        E3_SetControllerInterfaceType(0x8);
#endif // __linux__
    }
    else if (initType == 0 || mode == InitialMode::USB_ChangeCfg)
    {
        cout << "initial mode->USB!" << endl;
        if (mode == InitialMode::USB_ChangeCfg)
            ctrlIni.SetValue("PARAM", "TYPE", "USB");
        //Type = 0x3, Linux Usb
        //Type = 0x8, Linux SPI
#ifdef __linux__
        E3_SetControllerInterfaceType(0x3);
#endif // __linux__
    }
    if (mode != InitialMode::ByCfg)
    ctrlIni.WriteINI();
    return E3_Initial(basePath, 0);
}


std::string EzdKernel::TCHAR2STRING(TCHAR* STR)
{
#if _WIN32
	string result;
	wstring wstr(STR);
	int len = WideCharToMultiByte(CP_ACP, 0, wstr.c_str(), wstr.size(), NULL, 0, NULL, NULL);
	if (len <= 0)return result;
	char* buffer = new char[len + 1];
	if (buffer == NULL)return result;
	WideCharToMultiByte(CP_ACP, 0, wstr.c_str(), wstr.size(), buffer, len, NULL, NULL);
	buffer[len] = '\0';
	result.append(buffer);
	delete[] buffer;
	return result;
#else
	std::wstring_convert<std::codecvt_utf8<wchar_t>> converter;
	wstring temp(STR);
	std::string str = converter.to_bytes(temp);
	return str;
#endif // _WIN32
}


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
E3_ERR EzdKernel::E3_SetEntVectorFileInfo(E3_ID idEM, E3_ID idEnt, TCHAR* strFileName, bool bOptimize, bool bAutoConnect, bool bDynFile, bool bFixedX, bool bFixedY, double dSizeX, double dSizeY, bool bFixedCoor, double dFixedCoorX, double dFixedCoorY, int nFixedPos)
{
    int np1 = 0;
    int np2 = nFixedPos;
    int np3 = bFixedCoor ? 1 : 0;
    int np4 = 0;
    int np5 = 0;
    int np6 = 0;
    double dp1 = dSizeX;
    double dp2 = dSizeY;
    double dp3 = dFixedCoorX;
    double dp4 = dFixedCoorY;
    double dp5 = 0;
    double dp6 = 0;
    //
    if (bOptimize)
    {
        np1 |= VECATTRIB_OPTIMIZEPATH;
    }
    if (bAutoConnect)
    {
        np1 |= VECATTRIB_AUTOCONNECTCURVE;
    }
    if (bFixedX)
    {
        np1 |= VECATTRIB_IMPORTFIXED_WIDTH;
    }
    if (bFixedY)
    {
        np1 |= VECATTRIB_IMPORTFIXED_HEIGHT;
    }
    if (bDynFile)
    {
        np1 |= VECATTRIB_DYNFILE;
    }
    //
    E3_ERR err = E3_SetEntInfo(idEM, idEnt, 0, np1, np2, np3, np4, np5, np6, dp1, dp2, dp3, dp4, dp5, dp6, strFileName, false, nullptr);
    return err;
}

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
E3_ERR EzdKernel::E3_GetEntVectorFileInfo(E3_ID idEnt, TCHAR* strFileName, bool& bOptimize, bool& bAutoConnect, bool& bDynFile, bool& bFixedX, bool& bFixedY, double& dSizeX, double& dSizeY, bool& bFixedCoor, double& dFixedCoorX, double& dFixedCoorY, int& nFixedPos)
{
    int np1 = 0;
    int np2 = 0;
    int np3 = 0;
    int np4 = 0;
    int np5 = 0;
    int np6 = 0;
    double dp1 = 0;
    double dp2 = 0;
    double dp3 = 0;
    double dp4 = 0;
    double dp5 = 0;
    double dp6 = 0;
    E3_ERR err = E3_GetEntInfo(idEnt, 0, np1, np2, np3, np4, np5, np6, dp1, dp2, dp3, dp4, dp5, dp6, strFileName, nullptr);
    bOptimize = (np1 & VECATTRIB_OPTIMIZEPATH) != 0 ? true : false;
    bAutoConnect = (np1 & VECATTRIB_AUTOCONNECTCURVE) != 0 ? true : false;
    bFixedX = (np1 & VECATTRIB_IMPORTFIXED_WIDTH) != 0 ? true : false;
    bFixedY = (np1 & VECATTRIB_IMPORTFIXED_HEIGHT) != 0 ? true : false;
    bDynFile = (np1 & VECATTRIB_DYNFILE) != 0 ? true : false;
    nFixedPos = np2;
    bFixedCoor = np3 == 0 ? false : true;
    dSizeX = dp1;
    dSizeY = dp2;
    dFixedCoorX = dp3;
    dFixedCoorY = dp4;
    return err;
}

        /// <summary>
        /// 设置输入口对象信息
        /// </summary>
        /// <param name="idEnt">对象ID</param>
        /// <param name="bEnablePrompt">是否使能提示消息</param>
        /// <param name="strPrompt">提示消息</param>
        /// <param name="wIoHigh">高电平端口值（比如只有2和3端口是高电平，这个值为12）</param>
        /// <param name="wIoLow">低电平端口值（比如只有端口1和3是低电平，这个值是10）</param>
        /// <returns></returns>
E3_ERR EzdKernel::E3_SetEntIoInputInfo(E3_ID idEM, E3_ID idEnt, bool bEnablePrompt, TCHAR* strPrompt, int wIoHigh, int wIoLow)
{
    int np1 = bEnablePrompt ? 1 : 0;
    int np2 = wIoHigh;
    int np3 = wIoLow;
    int np4 = 0;
    int np5 = 0;
    int np6 = 0;
    double dp1 = 0;
    double dp2 = 0;
    double dp3 = 0;
    double dp4 = 0;
    double dp5 = 0;
    double dp6 = 0;
    E3_ERR err = E3_SetEntInfo(idEM, idEnt, 0, np1, np2, np3, np4, np5, np6, dp1, dp2, dp3, dp4, dp5, dp6, strPrompt, false, nullptr);
    return err;
}

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
E3_ERR EzdKernel::E3_SetEntIoOutputInfo(E3_ID idEM, E3_ID idEnt, bool bAllOutMode, int wOutValue, int nOutPutBit, bool bHigh, bool bPulse, double dPulseTimeMs)
{
    int np1 = bPulse ? 1 : 0;
    int np2 = bHigh ? 1 : 0;
    int np3 = nOutPutBit;
    int np4 = bAllOutMode ? 1 : 0;
    int np5 = wOutValue;
    int np6 = 0;
    double dp1 = dPulseTimeMs;
    double dp2 = 0;
    double dp3 = 0;
    double dp4 = 0;
    double dp5 = 0;
    double dp6 = 0;
    E3_ERR err = E3_SetEntInfo(idEM, idEnt, 0, np1, np2, np3, np4, np5, np6, dp1, dp2, dp3, dp4, dp5, dp6, nullptr, false, nullptr);
    return err;
}

        /// <summary>
        /// 得到输入口对象信息
        /// </summary>
        /// <param name="idEnt">对象ID</param>
        /// <param name="bEnablePrompt">是否使能提示消息</param>
        /// <param name="strPrompt">提示消息</param>
        /// <param name="wIoHigh">高电平端口值（比如只有2和3端口是高电平，这个值为12）</param>
        /// <param name="wIoLow">低电平端口值（比如只有端口1和3是低电平，这个值是10）</param>
        /// <returns></returns>
E3_ERR EzdKernel::E3_GetEntIoInputInfo(E3_ID idEnt, bool& bEnablePrompt, TCHAR* strPrompt, int& wIoHigh, int& wIoLow)
{
    int np1 = 0;
    int np2 = 0;
    int np3 = 0;
    int np4 = 0;
    int np5 = 0;
    int np6 = 0;
    double dp1 = 0;
    double dp2 = 0;
    double dp3 = 0;
    double dp4 = 0;
    double dp5 = 0;
    double dp6 = 0;
    E3_ERR err = E3_GetEntInfo(idEnt, 0, np1, np2, np3, np4, np5, np6, dp1, dp2, dp3, dp4, dp5, dp6, strPrompt, nullptr);
    bEnablePrompt = np1 != 0 ? true : false;
    wIoHigh = np2;
    wIoLow = np3;
    return err;
}

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
E3_ERR EzdKernel::E3_GetEntIoOutputInfo(E3_ID idEnt, bool& bAllOutMode, int& wOutValue, int& nOutPutBit, bool& bHigh, bool& bPulse, double& dPulseTimeMs)
{
    int np1 = 0;
    int np2 = 0;
    int np3 = 0;
    int np4 = 0;
    int np5 = 0;
    int np6 = 0;
    double dp1 = 0;
    double dp2 = 0;
    double dp3 = 0;
    double dp4 = 0;
    double dp5 = 0;
    double dp6 = 0;
    E3_ERR err = E3_GetEntInfo(idEnt, 0, np1, np2, np3, np4, np5, np6, dp1, dp2, dp3, dp4, dp5, dp6, nullptr, nullptr);
    bPulse = np1 != 0 ? true : false;
    bHigh = np2 != 0 ? true : false;
    nOutPutBit = np3;
    bAllOutMode = np4 != 0 ? true : false;
    wOutValue = np5;
    dPulseTimeMs = dp1;
    return err;
}

		/// <summary>
		/// 获取矩形对象参数;
		///  (此接口非库函数,基于Get/SetEntInfo封装实现)
		/// </summary>
		/// <param name="idEnt">对象ID;</param>
		/// <param name="nCornerLT">左上圆角(角度);</param>
		/// <param name="nCornerRT">右上圆角(角度);</param>
		/// <param name="nCornerLB">左下圆角(角度);</param>
		/// <param name="nCornerRB">右下圆角(角度);</param>
E3_ERR EzdKernel::E3_GetEntRectInfo(E3_ID idEnt, double& nCornerLT, double& nCornerRT, double& nCornerLB, double& nCornerRB)
{
	int np1 = 0;
	int np2 = 0;
	int np3 = 0;
	int np4 = 0;
	int np5 = 0;
	int np6 = 0;
	double dp1 = 0;
	double dp2 = 0;
	double dp3 = 0;
	double dp4 = 0;
	double dp5 = 0;
	double dp6 = 0;
	E3_ERR err = E3_GetEntInfo(idEnt, 0, np1,  np2,  np3, np4, np5, np6, dp1, dp2, dp3, dp4, dp5, dp6, NULL, NULL);
	nCornerLB = dp1;
	nCornerRB = dp2;
	nCornerRT = dp3;
	nCornerLT = dp4;
	return err;
}

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
E3_ERR EzdKernel::E3_SetEntRectInfo(E3_ID idEM, E3_ID idEnt, double nCornerLT, double nCornerRT, double nCornerLB, double nCornerRB)
{
	int np1 = 0;
	int np2 = 0;
	int np3 = 0;
	int np4 = 0;
	int np5 = 0;
	int np6 = 0;
	double dp1 = nCornerLB;
	double dp2 = nCornerRB;
	double dp3 = nCornerRT;
	double dp4 = nCornerLT;
	double dp5 = 0;
	double dp6 = 0;
	E3_ERR err = E3_SetEntInfo_2(idEM, idEnt, 0, np1, np2, np3, np4, np5, np6, dp1, dp2, dp3, dp4, dp5, dp6, nullptr);
	return err;
}

		/// <summary>
		/// 获取椭圆对象参数;
		/// (此接口非库函数,基于Get/SetEntInfo封装实现)
		/// </summary>
		/// <param name="idEnt">对象ID;</param>
		/// <param name="dStartAng">开始角度（弧度值）;</param>
		/// <param name="dEndAng">结束角度（弧度值）;</param>
		/// <param name="bDirCW">是否为开顺时针.True为顺时针;</param>
		/// <param name="bOC">是否为开曲线.True为开曲线;</param>
E3_ERR EzdKernel::E3_GetEntEllipseInfo(E3_ID idEnt, double& dStartAng, double& dEndAng, bool& bDirCW, bool& bOC)
{
	int np1 = 0;
	int np2 = 0;
	int np3 = 0;
	int np4 = 0;
	int np5 = 0;
	int np6 = 0;
	double dp1 = 0;
	double dp2 = 0;
	double dp3 = 0;
	double dp4 = 0;
	double dp5 = 0;
	double dp6 = 0;
	E3_ERR err = E3_GetEntInfo(idEnt, 0, np1, np2, np3, np4, np5, np6, dp1, dp2, dp3, dp4, dp5, dp6, NULL, NULL);
	dStartAng = (180 / M_PI) * dp1;
	dEndAng = (180 / M_PI) * dp2;
	bDirCW = np1 == 0 ? false : true;
	bOC = np2 == 0 ? false : true;
	return err;
}

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
E3_ERR EzdKernel::E3_SetEntEllipseInfo(E3_ID idEM, E3_ID idEnt, double dStartAng, double dEndAng, bool bDirCW, bool bOC)
{
	 int np1 = bDirCW ? 1 : 0;
	 int np2 = bOC ? 1 : 0;
	 int np3 = 0;
	 int np4 = 0;
	 int np5 = 0;
	 int np6 = 0;
	 double dp1 = dStartAng;
	 double dp2 = dEndAng;
	 double dp3 = 0;
	 double dp4 = 0;
	 double dp5 = 0;
	 double dp6 = 0;
	 E3_ERR err = E3_SetEntInfo_2(idEM, idEnt, 0, np1, np2, np3, np4, np5, np6, dp1, dp2, dp3, dp4, dp5, dp6, nullptr);
	 return err;
}

		/// <summary>
		/// 获取多边形对象参数.
		/// (此接口非库函数, 基于Get/SetEntInfo封装实现)
		/// </summary>
		/// <param name="idEnt">对象ID;</param>
		/// <param name="nEdge">边数;</param>
		/// <param name="bStar">是否内轮廓（默认false外轮廓）;</param>
E3_ERR EzdKernel::E3_GetEntPolygonInfo(E3_ID idEnt, int& nEdge, bool& bStar)
{
	 int np1 = 0;
	 int np2 = 0;
	 int np3 = 0;
	 int np4 = 0;
	 int np5 = 0;
	 int np6 = 0;
	 double dp1 = 0;
	 double dp2 = 0;
	 double dp3 = 0;
	 double dp4 = 0;
	 double dp5 = 0;
	 double dp6 = 0;
	 E3_ERR err = E3_GetEntInfo(idEnt, 0, np1, np2, np3, np4, np5, np6, dp1, dp2, dp3, dp4, dp5, dp6, NULL, NULL);
	 nEdge = np2;
	 bStar = np1 == 0 ? false : true;
	 return err;
}

		/// <summary>
		/// 设置多边形对象参数.
		/// (此接口非库函数, 基于Get/SetEntInfo封装实现)
		/// </summary>
		/// <param name="idEnt">对象ID;</param>
		/// <param name="nEdge">边数;</param>
		/// <param name="bStar">是否内轮廓（默认false外轮廓）;</param>
E3_ERR EzdKernel::E3_SetEntPolygonInfo(E3_ID idEM, E3_ID idEnt, int nEdge, bool bStar)
{
	 int np1 = bStar ? 1 : 0;
	 int np2 = nEdge;
	 int np3 = 0;
	 int np4 = 0;
	 int np5 = 0;
	 int np6 = 0;
	 double dp1 = 0;
	 double dp2 = 0;
	 double dp3 = 0;
	 double dp4 = 0;
	 double dp5 = 0;
	 double dp6 = 0;
	 E3_ERR err = E3_SetEntInfo_2(idEM, idEnt, 0, np1, np2, np3, np4, np5, np6, dp1, dp2, dp3, dp4, dp5, dp6, nullptr);
	 return err;
}

		/// <summary>
		/// 获取圆对象参数
		/// (此接口非库函数, 基于Get/SetEntInfo封装实现)
		/// </summary>
		/// <param name="idEnt">对象ID;</param>
		/// <param name="dDiameter">直径;</param>
		/// <param name="dStartAng">开始角度;</param>
		/// <param name="bDirCW">是否为逆时针(默认FALSE顺时针);</param>
E3_ERR EzdKernel::E3_GetEntCircleInfo(E3_ID idEnt, double& dDiameter, double& dStartAng, bool& bDirCW)
{
	int np1 = 0;
	int np2 = 0;
	int np3 = 0;
	int np4 = 0;
	int np5 = 0;
	int np6 = 0;
	double dp1 = 0;
	double dp2 = 0;
	double dp3 = 0;
	double dp4 = 0;
	double dp5 = 0;
	double dp6 = 0;
	E3_ERR err = E3_GetEntInfo(idEnt, 0, np1, np2, np3, np4, np5, np6, dp1, dp2, dp3, dp4, dp5, dp6, NULL, NULL);
	bDirCW = np1 == 0 ? false : true;
	dDiameter = dp1;
	dStartAng = dp2;
	return err;
}

		/// <summary>
		/// 设置圆对象参数;
		/// (此接口非库函数, 基于Get/SetEntInfo封装实现)
		/// </summary>
		/// <param name="idEM">管理器ID;</param>
		/// <param name="idEnt">对象ID;</param>
		/// <param name="dDiameter">直径;</param>
		/// <param name="dStartAng">开始角度;</param>
		/// <param name="bDirCW">是否为逆时针(默认FALSE顺时针);</param>
E3_ERR EzdKernel::E3_SetEntCircleInfo(E3_ID idEM, E3_ID idEnt, double dDiameter, double dStartAng, bool bDirCW)
{
	int np1 = bDirCW ? 1 : 0;
	int np2 = 0;
	int np3 = 0;
	int np4 = 0;
	int np5 = 0;
	int np6 = 0;
	double dp1 = dDiameter;
	double dp2 = dStartAng;
	double dp3 = 0;
	double dp4 = 0;
	double dp5 = 0;
	double dp6 = 0;
	E3_ERR err = E3_SetEntInfo_2(idEM, idEnt, 0, np1, np2, np3, np4, np5, np6, dp1, dp2, dp3, dp4, dp5, dp6, nullptr);
	return err;
}

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
E3_ERR EzdKernel::E3_GetEntSpiralInfo(E3_ID idEnt, int& nSpiralMode, bool& bInsideToOutside, int& nOutsideLoop, int& nInsideLoop, bool& bDoubleSprialMode, bool& bRectangleMode, double& dSpiralPitchDistMin, double& dSpiralPitchDistMax, double& dSpiralPitchDistInc, double& dMinRadius, double& dTolError)
{
    int np1 = 0;
    int np2 = 0;
    int np3 = 0;
    int np4 = 0;
    int np5 = 0;
    int np6 = 0;
    double dp1 = 0;
    double dp2 = 0;
    double dp3 = 0;
    double dp4 = 0;
    double dp5 = 0;
    double dp6 = 0;
    E3_ERR err = E3_GetEntInfo(idEnt, 0, np1, np2, np3, np4, np5, np6, dp1, dp2, dp3, dp4, dp5, dp6, NULL, NULL);
    nSpiralMode = np1;//填充属性 0=等间距  1=外疏内密  2=外密内疏
    bInsideToOutside = np2;
    nOutsideLoop = np3;//内环数
    nInsideLoop = np4;//外环数
    bDoubleSprialMode = np5;
    bRectangleMode = np6;
    dSpiralPitchDistMin = dp1;//最小螺旋线间距
    dSpiralPitchDistMax = dp2;//最大螺旋线间距
    dSpiralPitchDistInc = dp3;//螺旋线间距增量
    dMinRadius = dp4;
    dTolError = dp5;
    return err;
}

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
E3_ERR EzdKernel::E3_SetEntSpiralInfo(E3_ID idEM, E3_ID idEnt, int nSpiralMode, bool bInsideToOutside, int nOutsideLoop, int nInsideLoop, bool bDoubleSprialMode, bool bRectangleMode, double dSpiralPitchDistMin, double dSpiralPitchDistMax, double dSpiralPitchDistInc, double dMinRadius, double dTolError)
{
    int np1 = nSpiralMode;
    int np2 = bInsideToOutside;
    int np3 = nOutsideLoop;
    int np4 = nInsideLoop;
    int np5 = bDoubleSprialMode;
    int np6 = bRectangleMode;
    double dp1 = dSpiralPitchDistMin;
    double dp2 = dSpiralPitchDistMax;
    double dp3 = dSpiralPitchDistInc;
    double dp4 = dMinRadius;
    double dp5 = dTolError;
    double dp6 = 0;
    E3_ERR err = E3_SetEntInfo_2(idEM, idEnt, 0, np1, np2, np3, np4, np5, np6, dp1, dp2, dp3, dp4, dp5, dp6, nullptr);
    return err;
}

		/// <summary>
		/// 获取延时器对象参数;
		/// (此接口非库函数, 基于Get/SetEntInfo封装实现)
		/// </summary>
		/// <param name="idEnt">对象ID;</param>
		/// <param name="dTimeDelay">延时时间(单位:ms) [0,1000000];</param>
E3_ERR EzdKernel::E3_GetEntTimerInfo(E3_ID idEnt, double& dTimeDelay)
{
	int np1 = 0;
	int np2 = 0;
	int np3 = 0;
	int np4 = 0;
	int np5 = 0;
	int np6 = 0;
	double dp1 = 0;
	double dp2 = 0;
	double dp3 = 0;
	double dp4 = 0;
	double dp5 = 0;
	double dp6 = 0;
	E3_ERR err = E3_GetEntInfo(idEnt, 0, np1, np2, np3, np4, np5, np6, dp1, dp2, dp3, dp4, dp5, dp6, NULL, NULL);
	dTimeDelay = dp1;
	return err;
}

		/// <summary>
		/// 设置延时器对象参数;
		/// </summary>
		/// <param name="idEM">管理器ID;</param>
		/// <param name="idEnt">对象ID;</param>
		/// <param name="dTimeDelay">延时时间(单位:ms) [0,1000000];</param>
E3_ERR EzdKernel::E3_SetEntTimerInfo(E3_ID idEM, E3_ID idEnt, double dTimeDelay)
{
	int np1 = 0;
	int np2 = 0;
	int np3 = 0;
	int np4 = 0;
	int np5 = 0;
	int np6 = 0;
	double dp1 = dTimeDelay;
	double dp2 = 0;
	double dp3 = 0;
	double dp4 = 0;
	double dp5 = 0;
	double dp6 = 0;
	E3_ERR err = E3_SetEntInfo_2(idEM, idEnt, 0, np1, np2, np3, np4, np5, np6, dp1, dp2, dp3, dp4, dp5, dp6, nullptr);
	return err;
}

		/// <summary>
		/// 获取编码器对象参数;
		/// (此接口非库函数, 基于Get/SetEntInfo封装实现)
		/// </summary>
		/// <param name="idEnt">对象ID;</param>
		/// <param name="dFlyMoveDist">编码器移动距离单位（mm）;</param>
E3_ERR EzdKernel::E3_GetEntFlyMoveDistInfo(E3_ID idEnt, double& dFlyMoveDist)
{
	int np1 = 0;
	int np2 = 0;
	int np3 = 0;
	int np4 = 0;
	int np5 = 0;
	int np6 = 0;
	double dp1 = 0;
	double dp2 = 0;
	double dp3 = 0;
	double dp4 = 0;
	double dp5 = 0;
	double dp6 = 0;
	E3_ERR err = E3_GetEntInfo(idEnt, 0, np1, np2, np3, np4, np5, np6, dp1, dp2, dp3, dp4, dp5, dp6, NULL, NULL);
	dFlyMoveDist = dp1;
	return err;
}

		/// <summary>
		/// 设置编码器对象参数;
		/// (此接口非库函数, 基于Get/SetEntInfo封装实现)
		/// </summary>
		/// <param name="idEM">管理器ID;</param>
		/// <param name="idEnt">对象ID;</param>
		/// <param name="dFlyMoveDist">编码器移动距离单位（mm）;</param>
E3_ERR EzdKernel::E3_SetEntFlyMoveDistInfo(E3_ID idEM, E3_ID idEnt, double dFlyMoveDist)
{
	int np1 = 0;
	int np2 = 0;
	int np3 = 0;
	int np4 = 0;
	int np5 = 0;
	int np6 = 0;
	double dp1 = dFlyMoveDist;
	double dp2 = 0;
	double dp3 = 0;
	double dp4 = 0;
	double dp5 = 0;
	double dp6 = 0;
	E3_ERR err = E3_SetEntInfo_2(idEM, idEnt, 0, np1, np2, np3, np4, np5, np6, dp1, dp2, dp3, dp4, dp5, dp6, nullptr);
	return err;
}

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
E3_ERR EzdKernel::E3_SetEntAxisInfo(E3_ID idEM, E3_ID idEnt, int nUnit, int nAxisId, int nMoveFlag, bool bRelative, double dPulsePerUnit, double dDist, double dMinSpeed, double dMaxSpeed, double dAxisAccTime)
{
	int np1 = nUnit;
	int np2 = nAxisId;
	int np3 = nMoveFlag;
	int np4 = bRelative ? 0 : 1;
	int np5 = 0;
	int np6 = 0;
	double dp1 = dPulsePerUnit;
	double dp2 = dDist;
	double dp3 = dMinSpeed;
	double dp4 = dMaxSpeed;
	double dp5 = dAxisAccTime;
	double dp6 = 0;
	E3_ERR err = E3_SetEntInfo_2(idEM, idEnt, 0, np1, np2, np3, np4, np5, np6, dp1, dp2, dp3, dp4, dp5, dp6, nullptr);
	return err;
}

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
E3_ERR EzdKernel::E3_GetEntAxisInfo(E3_ID idEnt, int& nUnit, int& nAxisId, int& nMoveFlag, bool& bRelative, double& dPulsePerUnit, double& dDist, double& dMinSpeed, double& dMaxSpeed, double& dAxisAccTime)
{
	int np1 = 0;
	int np2 = 0;
	int np3 = 0;
	int np4 = 0;
	int np5 = 0;
	int np6 = 0;
	double dp1 = 0;
	double dp2 = 0;
	double dp3 = 0;
	double dp4 = 0;
	double dp5 = 0;
	double dp6 = 0;
	E3_ERR err = E3_GetEntInfo(idEnt, 0, np1, np2, np3, np4, np5, np6, dp1, dp2, dp3, dp4, dp5, dp6, NULL, NULL);
	nUnit = np1;
	nAxisId = np2;
	nMoveFlag = np3;
	bRelative = np4 == 0;
	dPulsePerUnit = dp1;
	dDist = dp2;
	dMinSpeed = dp3;
	dMaxSpeed = dp4;
	dAxisAccTime = dp5;
	return err;
}

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
E3_ERR EzdKernel::E3_GetCCDInfo(E3_ID idEnt, bool& bReset, bool& bMoveToStartPos, bool& bEnableCalibrate, bool& bEnableChangeModel, int& nModelIndex, int& nFailMode, bool& bRepeatTry, int& nRepeatCount, int& nJumpToEntIndex)
{
	int np1 = 0;
	int np2 = 0;
	int np3 = 0;
	int np4 = 0;
	int np5 = 0;
	int np6 = 0;
	double dp1 = 0;
	double dp2 = 0;
	double dp3 = 0;
	double dp4 = 0;
	double dp5 = 0;
	double dp6 = 0;
	E3_ERR err = E3_GetEntInfo(idEnt, 0, np1, np2, np3, np4, np5, np6, dp1, dp2, dp3, dp4, dp5, dp6, NULL, NULL);
	bReset = ((np1 & 0x01) == 0x01);
	bMoveToStartPos = ((np1 & 0x02) == 0x02);
	bEnableCalibrate = ((np1 & 0x04) == 0x04);
	bEnableChangeModel = ((np1 & 0x08) == 0x08);
	nModelIndex = np2;
	nFailMode = np3;
	bRepeatTry = np4 == 0 ? true : false;
	nRepeatCount = np5;
	nJumpToEntIndex = np6;
	return err;
}

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
E3_ERR EzdKernel::E3_SetCCDInfo(E3_ID idEM, E3_ID idEnt, bool bReset, bool bMoveToStartPos, bool bEnableCalibrate, bool bEnableChangeModel, int nModelIndex, int nFailMode, bool bRepeatTry, int nRepeatCount, int nJumpToEntIndex)
{
	int np1 = 0;
	int np2 = 0;
	int np3 = 0;
	int np4 = 0;
	int np5 = 0;
	int np6 = 0;
	double dp1 = 0;
	double dp2 = 0;
	double dp3 = 0;
	double dp4 = 0;
	double dp5 = 0;
	double dp6 = 0;
	//
	if (bReset)
	{
	  np1 |= 0x01;
	}
	if (bMoveToStartPos)
	{
	  np1 |= 0x02;
	}
	if (bEnableCalibrate)
	{
	  np1 |= 0x04;
	}
	if (bEnableChangeModel)
	{
	  np1 |= 0x08;
	}
	np2 = nModelIndex;
	np3 = nFailMode;//失败处理模式 0停止 1继续 2跳转
	np4 = bRepeatTry == true ? 0 : 1;//是否重试
	np5 = nRepeatCount;//重试次数
	np6 = nJumpToEntIndex;//跳转后索引  

	E3_ERR err = E3_SetEntInfo_2(idEM, idEnt, 0, np1, np2, np3, np4, np5, np6, dp1, dp2, dp3, dp4, dp5, dp6, nullptr);
	return err;
}

		/// <summary>
		/// 获取对象的索引参数;
		/// (此接口非库函数, 基于Get/SetEntInfo封装实现)
		/// </summary>
		/// <param name="idEnt">对象ID;</param>
		/// <param name="index">索引;</param>
E3_ERR EzdKernel::E3_GetEntIndex(E3_ID idEnt, int& index)
{
	int np1 = 0;
	int np2 = 0;
	int np3 = 0;
	int np4 = 0;
	int np5 = 0;
	int np6 = 0;
	double dp1 = 0;
	double dp2 = 0;
	double dp3 = 0;
	double dp4 = 0;
	double dp5 = 0;
	double dp6 = 0;
	E3_ERR err = E3_GetEntInfo(idEnt, 0, np1, np2, np3, np4, np5, np6, dp1, dp2, dp3, dp4, dp5, dp6, NULL, NULL);
	index = np1;
	return err;
}

		/// <summary>
		/// 设置对象索引参数;
		/// (此接口非库函数, 基于Get/SetEntInfo封装实现)
		/// </summary>
		/// <param name="idEM">管理器ID;</param>
		/// <param name="idEnt">对象ID;</param>
		/// <param name="index">索引;</param>
E3_ERR EzdKernel::E3_SetEntIndex(E3_ID idEM, E3_ID idEnt, int index)
{
	int np1 = index;
	int np2 = 0;
	int np3 = 0;
	int np4 = 0;
	int np5 = 0;
	int np6 = 0;
	double dp1 = 0;
	double dp2 = 0;
	double dp3 = 0;
	double dp4 = 0;
	double dp5 = 0;
	double dp6 = 0;
	E3_ERR err = E3_SetEntInfo_2(idEM, idEnt, 0, np1, np2, np3, np4, np5, np6, dp1, dp2, dp3, dp4, dp5, dp6, nullptr);
	index = np1;
	return err;
}

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
E3_ERR EzdKernel::E3_GetEntBmpFileInfo(E3_ID idEnt, TCHAR* strFileName, bool& bBidir, double& dBiDirOffset, bool& bDrillmode, double& dDrillTime, bool& bScanY, bool& mirrorX, bool& mirrorY, bool& bPixelPower, bool& bFixedDPI, int& nDpiX, int& nDpiY, bool& bDynFile, bool& bFixedX, bool& bFixedY, bool& bTrueDPI, double& dSizeX, double& dSizeY, int& nFixedPosition, bool& bGray, bool& bInvert, bool& bDither, bool& bLight, bool& bOptimize, bool& scanReverse, double& luminValue, double& contrast, bool& bLineOffset, bool& bLineIncrement, int& nLineIncrement, int& nMinLowGrayPt, bool& bDisableMarkLowGrayPt, double& dAccDist, double& dDecDist, double& dGlobalMigration, int& nGrayCurvePt, Pt2d ptGrayCurveBuf[20], BYTE bGrayScaleBuf[256])
{
    int np1 = 0;
    int np2 = 0;
    int np3 = 0;
    int np4 = 0;
    int np5 = 0;
    int np6 = 0;
    double dp1 = 0;
    double dp2 = 0;
    double dp3 = 0;
    double dp4 = 0;
    double dp5 = 0;
    double dp6 = 0;

    E3_ERR err = E3_GetEntInfo(idEnt, 0, np1, np2, np3, np4, np5, np6, dp1, dp2, dp3, dp4, dp5, dp6, strFileName, bGrayScaleBuf);
    bDynFile = (np1 & (int)BmpAttributeBitKey::DYNFILE) != 0 ? true : false;
    bFixedX = (np1 & (int)BmpAttributeBitKey::WIDTH) != 0 ? true : false;
    bFixedY = (np1 & (int)BmpAttributeBitKey::HEIGHT) != 0 ? true : false;
    bFixedDPI = (np1 & (int)BmpAttributeBitKey::DPI) != 0 ? true : false;
    bTrueDPI = (np1 & (int)BmpAttributeBitKey::DPITRUE) != 0 ? true : false;
    bInvert = (np3 & (int)BmpScanBitKey::INVERT) != 0 ? true : false;
    bGray = (np3 & (int)BmpScanBitKey::GRAY) != 0 ? true : false;
    bDither = (np3 & (int)BmpScanBitKey::DITHER) != 0 ? true : false;
    bBidir = (np3 & (int)BmpScanBitKey::BIDIR) != 0 ? true : false;
    bDrillmode = (np3 & (int)BmpScanBitKey::DRILL) != 0 ? true : false;
    bPixelPower = (np3 & (int)BmpScanBitKey::POWER) != 0 ? true : false;
    bLight = (np3 & (int)BmpScanBitKey::LIGHT) != 0 ? true : false;
    bOptimize = (np3 & (int)BmpScanBitKey::OPTIMIZE) != 0 ? true : false;
    scanReverse = (np3 & (int)BmpScanBitKey::SCANREVERSE) != 0 ? true : false;
    bScanY = (np3 & (int)BmpScanBitKey::YDIR) != 0 ? true : false;
    bLineOffset = (np3 & (int)BmpScanBitKey::OFFSETPT) != 0 ? true : false;
    mirrorX = (np3 & (int)BmpScanBitKey::MIRRORX) != 0 ? true : false;
    mirrorY = (np3 & (int)BmpScanBitKey::MIRRORY) != 0 ? true : false;
    nFixedPosition = np2;
    nDpiX = np4;
    nDpiY = np5;
    dSizeX = dp1;
    dSizeY = dp2;
    luminValue = dp3;
    dDrillTime = dp4;
    contrast = dp5;
    if ((int)err != 0)
    {
        return err;
    }
    BYTE byteGrayCurveBuf[160];
    err = E3_GetEntInfo(idEnt, 1, np1, np2, np3, np4, np5, np6, dp1, dp2, dp3, dp4, dp5, dp6, strFileName, byteGrayCurveBuf);
    bLineIncrement = np1 != 0;
    nLineIncrement = np2;
    bDisableMarkLowGrayPt = np3 != 0 ? true : false;
    nMinLowGrayPt = np4;
    nGrayCurvePt = np5;
    dBiDirOffset = dp1;
    dAccDist = dp2;
    dDecDist = dp3;
    dGlobalMigration = dp5;
    //
    for (int i = 0; i < 20; i++)
    {
        int x = 0;
        try
        {
            int x1 = (int)byteGrayCurveBuf[(i * 4) * 2];
            int x2 = (int)byteGrayCurveBuf[(i * 4) * 2 + 1];
            int x3 = (int)byteGrayCurveBuf[(i * 4) * 2 + 2];
            int x4 = (int)byteGrayCurveBuf[(i * 4) * 2 + 3];
            x = x1 | (x2 << 8) | (x3 << 16) | (x4 << 24);
        }
        catch (...)
        {
            x = 0;
        }
        ptGrayCurveBuf[i].X = x;
        //
        int y = 0;
        try
        {
            int y1 = (int)byteGrayCurveBuf[(i * 4) * 2 + 4];
            int y2 = (int)byteGrayCurveBuf[(i * 4) * 2 + 4 + 1];
            int y3 = (int)byteGrayCurveBuf[(i * 4) * 2 + 4 + 2];
            int y4 = (int)byteGrayCurveBuf[(i * 4) * 2 + 4 + 3];
            y = y1 | (y2 << 8) | (y3 << 16) | (y4 << 24);
        }
        catch (...)
        {
            y = 0;
        }
        ptGrayCurveBuf[i].Y = y;
    }
    return err;
}


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
BYTE* EzdKernel::E3_GetEntBmpFileData(E3_ID idEnt, int& W, int& H, int& ScanW, int& Bitcount, int& byteCount, double& bmpMinX, double& bmpMinY, double& bmpAngleFromX, double& bmpWidth, double& bmpHeight, E3_ERR& err)
{
    int np1 = 0;
    int np2 = 0;
    int np3 = 0;
    int np4 = 0;
    int np5 = 0;
    int np6 = 0;
    double dp1 = 0;
    double dp2 = 0;
    double dp3 = 0;
    double dp4 = 0;
    double dp5 = 0;
    double dp6 = 0;
    //获取位图数据部分，nFlag=101，是原数据的数据字节，100是原数据的属性信息
    //获取位图数据部分，nFlag=201，是处理后的数据字节，200是处理后的属性信息
    //先读取200是否返回正常,如果返回失败,则代表图片并未修改过.读取100.
    //读取修改前
    err = E3_GetEntInfo(idEnt, 100, np1, np2, np3, np4, np5, np6, dp1, dp2, dp3, dp4, dp5, dp6, NULL, nullptr);
    W = np1;
    H = np2;
    Bitcount = np3;
    ScanW = np4;
    byteCount = np5;
    bmpMinX = dp1;
    bmpMinY = dp2;
    bmpAngleFromX = dp3;
    bmpWidth = dp4;
    bmpHeight = dp5;
    // 
    //获取图片内容信息
    err = E3_GetEntInfo(idEnt, 200, np1, np2, np3, np4, np5, np6, dp1, dp2, dp3, dp4, dp5, dp6, NULL, nullptr);
    if ((int)err == 0)
    {
        byteCount = np5;
        BYTE* FileDataBuf = new BYTE[byteCount]{0};
        err = E3_GetEntInfo(idEnt, 201, np1, np2, np3, np4, np5, np6, dp1, dp2, dp3, dp4, dp5, dp6, NULL, FileDataBuf);
        return FileDataBuf;
    }
    else
    {
        //读取修改前
        err = E3_GetEntInfo(idEnt, 100, np1, np2, np3, np4, np5, np6, dp1, dp2, dp3, dp4, dp5, dp6, NULL, nullptr);
        BYTE* FileDataBuf = new BYTE[byteCount]{ 0 };
        err = E3_GetEntInfo(idEnt, 101, np1, np2, np3, np4, np5, np6, dp1, dp2, dp3, dp4, dp5, dp6, NULL, FileDataBuf);
        return FileDataBuf;
    }
}


/// <summary>
/// 释放由[E3_GetEntBmpFileData]得到的图像指针变量.
/// </summary>
void EzdKernel::E3_FreeEntBmpFileData(BYTE* FileDataBuf)
{
	if (FileDataBuf != nullptr)
	{
		delete[] FileDataBuf;
	}
}

EzdKernel::~EzdKernel()
{
#ifdef _WIN32
    if (m_sysDLL)
    {
        FreeLibrary(m_sysDLL);
    }
    if (m_hEzdDLL)
    {
        FreeLibrary(m_hEzdDLL);
    }
#else
    if (m_hEzdDLL)
    {
        dlclose(m_hEzdDLL);
    }
#endif
}

