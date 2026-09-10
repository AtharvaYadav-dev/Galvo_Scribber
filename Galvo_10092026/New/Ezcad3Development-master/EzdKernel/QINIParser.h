#ifndef INI_PARSERQT_H
#define INI_PARSERQT_H

#include <iostream>
#include <fstream>
#include <sstream>
#include <deque>
#include <cstdlib>
#include <map>
#include <string>
#include <QString>
#include <QVector>

using namespace std;

class QININode {
public:
    QININode(const QString& root, const QString& key, const QString& value)
        : root(root), key(key), value(value) {}

    QString root;
    QString key;
    QString value;
};

class QSubNode {
public:
    void InsertElement(const QString& key, const QString& value) {
        sub_node.emplace(key, value);
    }

    map<QString, QString> sub_node;
};

class QINIParser {
public:
    QString FormatEscapedString(const QString& input);
    int ReadINI(const QString& path);
    QString GetValue(const QString& root, const QString& key, const QString& defTxt);
    size_t GetSize() const { return map_ini.size(); }
    size_t SetValue(const QString& root, const QString& key, const QString& value);
    bool WriteINI();
    bool AppendINI(const QString& root, const QString& key, const QString& value);
    void Clear() { map_ini.clear(); }
    QVector<QString> Sections;
private:
    map<QString, QSubNode> map_ini;
    QString fileName;
};

#endif // INI_PARSERQT_H
