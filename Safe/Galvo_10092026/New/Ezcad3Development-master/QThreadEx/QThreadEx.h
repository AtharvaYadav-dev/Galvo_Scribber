#ifndef QTHREADEX_H
#define QTHREADEX_H
#include <QThread>
#include <QString>

typedef void(*ThreadStart_Object)(const void* callObject, const void* param);
typedef void(*ThreadStart_Int)(const void* callObject, int param);
class QThreadEx :public QThread
{
    Q_OBJECT
private:
    ThreadStart_Object thread_Object;
    ThreadStart_Int thread_Int;
    //0=参数为对象指针;1=参数为int类型;
    int m_Model = 0;
    const void* m_tParam_object = nullptr;
    int m_tParam_int = 0;
    const void* dParent = nullptr;
    QString qState = nullptr;
    void run() override;
public:
    QThreadEx();
    ~QThreadEx();
    void DoWork(ThreadStart_Object tMethod, const void* parent, const void* param);
    void DoWork(ThreadStart_Int tMethod, const void* parent, int param);
signals:
    void RunWorkerCompleted(const QString* state);
};

#endif // QTHREADEX_H
