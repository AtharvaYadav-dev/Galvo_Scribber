#ifndef CWNDOPENGL_H
#define CWNDOPENGL_H

#include "CWndOpenGL_global.h"
#include "../EzdKernel/EzcadKernel.h"
#include "QOpenGLWidget"
#include <QOpenGLFunctions>
//#include "QtWin"

namespace Gdiplus
{
    using std::max;
    using std::min;
};
#include<Gdiplus.h>
#pragma comment(lib,"gdiplus.lib")

class CWNDOPENGL_EXPORT CWndOpenGL :public QOpenGLWidget, protected QOpenGLFunctions
{
public:
    CWndOpenGL(QWidget* parent);
    ~CWndOpenGL();
public:
    EzdKernel* m_pEzcad3;
    CWndOpenGL()
    {
        m_pEzcad3 = NULL;
    }
public:
    static int m_WorkSpace_Width;
    static int m_WorkSpace_Height;
    static double m_WorkSpace_LeftBottomX;
    static double m_WorkSpace_LeftBottomY;
    static double m_Scale;
    static E3_ID m_idShowEnt;

    static QRect m_WndOpenGL_Rect;
    static BOOL m_bShowByName;
    static TCHAR* m_sShowName;
    static HBITMAP m_sShowBIT;
public:
    double GetLogWndWidth();
    double GetLogWndHeight();
    void GetLogWndCenter(double& x, double& y);
    void SetLogWndCenter(double x, double y);
    void ZoomAll();
    void ZoomWorkSpace();
    void ZoomAll(double xMin, double yMin, double xMax, double yMax);
    void ZoomOffset(double x, double y);
    void ZoomIn();
    void ZoomOut();
    void ZoomScale(double dScale);
    void GDIDraw();

protected:
    virtual void paintGL() Q_DECL_OVERRIDE;
    virtual void initializeGL() override;
    virtual void showEvent(QShowEvent* event)override;
    virtual QPaintEngine* paintEngine();

    static ULONG_PTR m_gdiplusToken;
    static bool m_gdiplusInitialized;
};

#endif // CWNDOPENGL_H
