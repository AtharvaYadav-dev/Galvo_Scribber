#ifndef QTHREADEX_GLOBAL_H
#define QTHREADEX_GLOBAL_H

#include <QtCore/qglobal.h>

#if defined(QTHREADEX_LIBRARY)
#  define QTHREADEX_EXPORT Q_DECL_EXPORT
#else
#  define QTHREADEX_EXPORT Q_DECL_IMPORT
#endif

#endif // QTHREADEX_GLOBAL_H
