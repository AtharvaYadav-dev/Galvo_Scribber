#include "QINIParser.h"
#include <algorithm>
#include <QRegExp>
#include <QTextStream>
#include <QFile>
#include <QStringList>
#include <QRegularExpression>
#include <QDebug>
#include <QFile>
#include <chrono>
#include <QDebug>
// 移除所有空白字符
QString& TrimString(QString& str) {
    str.remove(QRegExp("\\r"));
    str = str.trimmed();
    return str;
}
QString QINIParser::FormatEscapedString(const QString& input)
{
    QString formatted = input;
    //formatted = formatted.replace("\\", "\\\\"); // 替换反斜杠
    if (formatted.indexOf("\\\\n") != -1)
    {
        formatted = formatted.replace("\\\\n", "\\n");  // 替换换行符
    }
    formatted = formatted.replace("\t", "\\t");  // 替换制表符
    return formatted;
}
// 读取 INI 文件并解析
int QINIParser::ReadINI(const QString& path)
{
    auto start = chrono::steady_clock::now();

    QFile in_conf_file(path);
    if (!in_conf_file.open(QIODevice::ReadOnly))
    {
        return 0;
    }
    bool isFindRepetKey = false;
    fileName = path;
    QTextStream qts(&in_conf_file);
    qts.setCodec("UTF-8");
    map_ini.clear();
    Sections.clear();
    QString str_root;
    QString str_line;
    deque<QININode> vec_ini;
    QRegularExpression qre("[\\[\\]]+");
    while (!qts.atEnd())
    {
        QString str_key, str_value;
        str_line = qts.readLine().trimmed();
        if (str_line.isEmpty())
        {
            continue;
        }
        //
        if (str_line[0] == ';' || str_line[0] == '#')
        {
            continue;
        }
        //
        if (str_line[0] == '[')
        {
            int idx = str_line.indexOf(']', 0);
            if (idx)
            {
                str_root = str_line.mid(1, idx - 1);
                Sections.push_back(str_root);
            }
            //QStringList list = str_line.split(qre, QString::SplitBehavior::SkipEmptyParts);
            //if (list.size() > 0)
            //{
            //    str_root = list.first();
            //    Sections.push_back(str_root);
            //}
            continue;
        }
        //
        int equalIdx = (str_line.indexOf("="));
        if (equalIdx) {
            str_key = str_line.mid(0, equalIdx);
            str_value = str_line.mid(equalIdx + 1, str_line.length() - equalIdx);

            str_key = TrimString(str_key);
            str_value = TrimString(str_value);
        }

        if (!str_root.isEmpty() && !str_key.isEmpty()) {
            if (find_if(vec_ini.begin(), vec_ini.end(), [=](const QININode& qi) {return str_root == qi.root && str_key == qi.key; }) == vec_ini.end())
            {
                vec_ini.emplace_back(str_root, str_key, str_value);
            }
            else
            {
                isFindRepetKey = true;
                continue;
            }
        }
        else
        {
            str_value = TrimString(str_value);
        }
    }
    for (const auto& node : vec_ini) {
        map_ini[node.root].InsertElement(node.key, node.value);
    }
    in_conf_file.close();
    if (isFindRepetKey)
    {
        WriteINI();
    }
    auto stop = chrono::steady_clock::now();
    chrono::duration<double> diff = stop - start;
    qDebug() << "qini run time:" << diff.count() << "s";
    return 1;
}

// 根据 root 和 key 获取值
QString QINIParser::GetValue(const QString& root, const QString& key, const QString& defTxt) {
    auto itr = map_ini.find(root);
    if (itr != map_ini.end()) {
        auto sub_itr = itr->second.sub_node.find(key);
        if (sub_itr != itr->second.sub_node.end()) {
            return sub_itr->second;
        }
        else
        {
            AppendINI(root, key, defTxt);
        }
    }
    else
    {
        map_ini.emplace(root, QSubNode());
    }
    return defTxt;
}
bool QINIParser::AppendINI(const QString& root, const QString& key, const QString& value)
{
    if (!map_ini.size())
    {
        return false;
    }
    if (fileName.isEmpty())
    {
        return false;
    }
    auto itr = map_ini.find(root);
    if (itr != map_ini.end()) {
        auto sub_itr = itr->second.sub_node.find(key);
        if (sub_itr != itr->second.sub_node.end()) {
            return false;
        }
    }
    else
    {
        map_ini.emplace(root, QSubNode());
    }
    itr->second.sub_node.emplace(key, value);
    //
    QFile file(fileName);
    if (file.open(QIODevice::WriteOnly | QIODevice::Append)) {
        QTextStream out(&file);
        out.setCodec("UTF-8");
#ifdef __linux__
        QString newLine = "\n";
#else
        QString newLine = "\r\n";
#endif
        // 追加内容到文件末尾
        QString newText = newLine + FormatEscapedString(key + "=" + value);
        out << newText;
        file.close();
        return true;
    }
    else {
        qDebug() << "Failed to open file in append mode." << file.errorString();
        return false;
    }
}
// 写入 INI 文件
bool QINIParser::WriteINI() {
    if (fileName.isEmpty())
    {
        return false;
    }
    if (!map_ini.size())
    {
        return false;
    }
    QFile file(fileName);
    if (file.open(QIODevice::WriteOnly)) {
#ifdef __linux__
        QString newLine = "\n";
#else
        QString newLine = "\r\n";
#endif
        for (const auto& pair : map_ini) {
            QString writeStr = newLine + "[" + pair.first + "]" + newLine;
            for (const auto& sub_pair : pair.second.sub_node) {
                writeStr += FormatEscapedString(sub_pair.first + "=" + sub_pair.second) + newLine;
            }
            file.write(writeStr.toUtf8());
        }
        file.close();
}
    else {
        qDebug() << "Failed to open file for writing.";
    }
    return true;
}

// 设置值
size_t QINIParser::SetValue(const QString& root, const QString& key, const QString& value) {
    map_ini[root].InsertElement(key, value);
    return map_ini.size();
}
