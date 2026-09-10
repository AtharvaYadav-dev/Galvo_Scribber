#include "CWndOpenGL.h"

int CWndOpenGL::m_WorkSpace_Width = 100;
int CWndOpenGL::m_WorkSpace_Height = 100;
double CWndOpenGL::m_WorkSpace_LeftBottomX = -50;
double CWndOpenGL::m_WorkSpace_LeftBottomY = -50;
double CWndOpenGL::m_Scale = 1.0;
E3_ID CWndOpenGL::m_idShowEnt;
QRect CWndOpenGL::m_WndOpenGL_Rect;
BOOL CWndOpenGL::m_bShowByName = FALSE;
TCHAR* CWndOpenGL::m_sShowName;
HBITMAP CWndOpenGL::m_sShowBIT;
ULONG_PTR CWndOpenGL::m_gdiplusToken = 0;
bool CWndOpenGL::m_gdiplusInitialized = false;
CWndOpenGL::CWndOpenGL(QWidget* parent) :QOpenGLWidget(parent) 
{
    m_pEzcad3 = new EzdKernel(nullptr);
    QSurfaceFormat fmt = format();
    fmt.setSamples(18);
    setFormat(fmt);
    setAttribute(Qt::WA_PaintOnScreen, true);
    if (!m_gdiplusInitialized) {
        Gdiplus::GdiplusStartupInput gdiplusStartupInput;
        Gdiplus::GdiplusStartup(&m_gdiplusToken, &gdiplusStartupInput, NULL);
        m_gdiplusInitialized = true;
    }
}
CWndOpenGL::~CWndOpenGL()
{

}

void CWndOpenGL::ZoomWorkSpace()
{
    ZoomAll(-m_WorkSpace_Width / 2, -m_WorkSpace_Height / 2, m_WorkSpace_Width / 2, m_WorkSpace_Height / 2);
}
void CWndOpenGL::ZoomAll(double xMin, double yMin, double xMax, double yMax)
{
    double dCenx = (xMin + xMax) / 2;
    double dCeny = (yMin + yMax) / 2;
    double fScale1 = (xMax - xMin) / m_WndOpenGL_Rect.width();
    double fScale2 = (yMax - yMin) / m_WndOpenGL_Rect.height();
    if (fScale1 < fScale2)
    {
        m_Scale = fScale2;
    }
    else
    {
        m_Scale = fScale1;
    }
    m_WorkSpace_LeftBottomX = dCenx - m_Scale * m_WndOpenGL_Rect.width() / 2;
    m_WorkSpace_LeftBottomY = dCeny - m_Scale * m_WndOpenGL_Rect.height() / 2;
}

void CWndOpenGL::ZoomOffset(double x, double y)
{
    m_WorkSpace_LeftBottomX += x;
    m_WorkSpace_LeftBottomY += y;
}
double  CWndOpenGL::GetLogWndWidth()
{
    return (double)m_WndOpenGL_Rect.width() * m_Scale;
}
double  CWndOpenGL::GetLogWndHeight()
{
    return (double)m_WndOpenGL_Rect.height() * m_Scale;
}

void CWndOpenGL::GetLogWndCenter(double& x, double& y)
{
    x = m_WorkSpace_LeftBottomX + GetLogWndWidth() / 2;
    y = m_WorkSpace_LeftBottomY + GetLogWndHeight() / 2;
}

void CWndOpenGL::SetLogWndCenter(double  x, double  y)
{
    m_WorkSpace_LeftBottomX = x - GetLogWndWidth() / 2;
    m_WorkSpace_LeftBottomY = y - GetLogWndHeight() / 2;
}

void CWndOpenGL::ZoomIn()
{
    ZoomScale(m_Scale * 0.5);
}
void CWndOpenGL::ZoomOut()
{
    ZoomScale(m_Scale * 2);
}
void CWndOpenGL::ZoomScale(double dScale)
{
    double x, y;
    GetLogWndCenter(x, y);
    m_Scale = dScale;
    SetLogWndCenter(x, y);
}

void CWndOpenGL::initializeGL()
{
    initializeOpenGLFunctions();
    glClearColor(255, 255, 255, 1.0);
}


void CWndOpenGL::paintGL()
{
    GDIDraw();
}

void CWndOpenGL::showEvent(QShowEvent* event)
{
    m_WndOpenGL_Rect = this->rect();
    ZoomWorkSpace();
    GDIDraw();
}

QPaintEngine* CWndOpenGL::paintEngine()
{
    GDIDraw();
    return nullptr;
}

void CWndOpenGL::GDIDraw()
{
    HWND hwnd;
    hwnd = (HWND)this->winId();
    HDC labelDC = GetDC(hwnd);
    HBITMAP hbm = CreateCompatibleBitmap(labelDC, m_WndOpenGL_Rect.width(), m_WndOpenGL_Rect.height());
    if (m_bShowByName == TRUE)
    {
        hbm = m_sShowBIT;
        //  hbm= m_pEzcad3->E3_GetEzdFilePrevBitmap(m_sShowName);

    }

    HDC  hdcsource = CreateCompatibleDC(labelDC);
    SelectObject(hdcsource, hbm);


    if (m_bShowByName == FALSE)
    {
        Gdiplus::Graphics* g = Gdiplus::Graphics::FromHDC(hdcsource);
        auto WhiteBrush = new Gdiplus::SolidBrush(Gdiplus::Color::White);
        g->FillRectangle(WhiteBrush, m_WndOpenGL_Rect.left(), m_WndOpenGL_Rect.top(),
            m_WndOpenGL_Rect.right() - m_WndOpenGL_Rect.left(),
            m_WndOpenGL_Rect.bottom() - m_WndOpenGL_Rect.top());
        delete WhiteBrush;
        WhiteBrush = nullptr;
        delete g;
        g = nullptr;
        m_pEzcad3->E3_DrawEnt2(hdcsource, m_idShowEnt, 0, m_WndOpenGL_Rect.width(),
            m_WndOpenGL_Rect.height(), m_WorkSpace_LeftBottomX, m_WorkSpace_LeftBottomY, m_Scale);
        BitBlt(labelDC, 0, 0, m_WndOpenGL_Rect.width(), m_WndOpenGL_Rect.height(), hdcsource, 0, 0, SRCCOPY);
    }
    else
    {

        BitBlt(labelDC, 0, 0, m_WndOpenGL_Rect.width(), m_WndOpenGL_Rect.height(), hdcsource, 0, 0, SRCCOPY);
    }


    ReleaseDC(hwnd, labelDC);
    DeleteObject(hbm);
    DeleteObject(hdcsource);


}


