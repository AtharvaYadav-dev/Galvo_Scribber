#include "Widget/EzcadDevelopment.h"
#include <QtWidgets/QApplication>

int main(int argc, char *argv[])
{
    QApplication app(argc, argv);
    EzcadDevelopment window;
    window.show();
    return app.exec();
}
