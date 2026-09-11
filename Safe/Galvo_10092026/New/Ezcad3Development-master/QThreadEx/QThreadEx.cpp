#include "QThreadEx.h"
QThreadEx::QThreadEx()
{

}
void QThreadEx::run()
{
    try {
        switch (m_Model)
        {
        case 0:
            thread_Object(dParent, m_tParam_object);
            break;
        case 1:
            thread_Int(dParent, m_tParam_int);
            break;
        case 2:
            break;
        }
    }
    catch (int& err) {
        qState = QString("出现异常,异常代码:").arg(err);
    }
    emit RunWorkerCompleted(&qState);
}

void QThreadEx::DoWork(ThreadStart_Object tMethod, const void* parent, const void* params)
{
    m_Model = 0;
    thread_Object = tMethod;
    m_tParam_object = params;
    dParent = parent;
    this->start();
}
void QThreadEx::DoWork(ThreadStart_Int tMethod, const void* parent, int params)
{
    m_Model = 1;
    thread_Int = tMethod;
    m_tParam_int = params;
    dParent = parent;
    this->start();
}
QThreadEx::~QThreadEx()
{

}
