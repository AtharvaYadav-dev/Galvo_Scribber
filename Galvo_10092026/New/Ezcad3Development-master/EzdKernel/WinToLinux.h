#ifndef WINTOLINUX1_H
#define WINTOLINUX1_H
#ifdef  __linux__

#define INVALID_HANDLE_VALUE   -1
#define _MAX_PATH           260
#define MAX_PATH            260
#define TRUE                true
#define FALSE               false

#define __T(x)      L ## x
#define _T(x)       __T(x)

typedef int                 BOOL;
typedef unsigned char       byte;
typedef byte                BYTE;
typedef byte                boolean;
typedef char                CHAR;
typedef unsigned char       UCHAR;
typedef short               Int16;
typedef long                Int32;
typedef unsigned short      UInt16;
typedef unsigned long       UInt32;
typedef long long           Int64;
typedef unsigned long long  UInt64;

typedef wchar_t             TCHAR;
//
typedef UInt16              WORD;
typedef unsigned long       INT_PTR;
typedef unsigned long       DWORD;
//
#define DECLARE_HANDLE(name) struct name##__{int unused;}; typedef struct name##__ *name
DECLARE_HANDLE(HWND);
DECLARE_HANDLE(HDC);
DECLARE_HANDLE(HINSTANCE);
typedef HINSTANCE HMODULE;
DECLARE_HANDLE(HBITMAP);
#endif //  Linux

#endif //WINTOLINUX1_H
