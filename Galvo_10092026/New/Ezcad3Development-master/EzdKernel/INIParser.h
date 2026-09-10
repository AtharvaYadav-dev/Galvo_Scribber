#ifndef INI_PARSER_H
#define INI_PARSER_H

#include <iostream>
#include <fstream>
#include <sstream>
#include <deque>
#include <cstdlib>
#include <map>
#include <string>
using namespace std;
std::string WStringToString(const std::wstring& wstr);

class ININode {
public:
    ININode(const string& root, const string& key, const string& value)
        : root(root), key(key), value(value) {}

    string root;
    string key;
    string value;
};

class SubNode {
public:
    void InsertElement(const string& key, const string& value);
    map<string, string> sub_node;
};

class INIParser {
public:
    int ReadINI(const wstring& path);
    string GetValue(const string& root, const string& key);
    size_t GetSize() const { return map_ini.size(); }
    size_t SetValue(const string& root, const string& key, const string& value);
    int WriteINI();
    void Clear() { map_ini.clear(); }

private:
    map<string, SubNode> map_ini;
    wstring filePath;
};

#endif // INI_PARSER_H
