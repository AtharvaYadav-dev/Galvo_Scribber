#include "INIParser.h"
#include <algorithm> // 需要包含这个头文件
#include <string>
#include <locale>
#include <codecvt>

std::string WStringToString(const std::wstring& wstr)
{
    try
    {
        // 使用std::wstring_convert和std::codecvt_utf8_utf16进行转换
        std::wstring_convert<std::codecvt_utf8_utf16<wchar_t>> converter;
        return converter.to_bytes(wstr);
    }
    catch (const std::exception& e)
    {
        // 如果转换失败，抛出异常
        throw std::runtime_error("Failed to convert wstring to string: " + std::string(e.what()));
    }
}

void SubNode::InsertElement(const string& key, const string& value)
{
    auto it = std::find_if(sub_node.begin(), sub_node.end(),
        [&key](const std::pair<const std::string, std::string>& element)
        {
            return element.first == key;
        });
    if (it == sub_node.end())
    {
        sub_node.emplace(key, value);
    }
    else
    {
        sub_node[key] = value;
    }
}
// 移除所有空白字符
string& TrimString(string& str)
{
    str.erase(remove_if(str.begin(), str.end(), ::isspace), str.end());
    return str;
}
// 读取 INI 文件并解析
int INIParser::ReadINI(const wstring& path)
{
#ifdef _WIN32
    wifstream in_conf_file(path);
#else
    // 将wstring转换为UTF-8编码的string
    string utf8_path = WStringToString(path);
    ifstream in_conf_file(utf8_path);
#endif
    if (!in_conf_file)
        return 0;
    filePath = path;
    map_ini.clear();
#ifdef _WIN32
    wstring str_line;
#else
    string str_line;
#endif
    string str_root;
    deque<ININode> vec_ini;
    while (getline(in_conf_file, str_line))
    {
        string::size_type left_pos, right_pos, equal_div_pos;
        string str_key, str_value;
        if (str_line.empty())
        {
            continue;
        }
        if (str_line[0] == L'/')
        {
            continue;
        }
#ifdef _WIN32
        if ((left_pos = str_line.find(L"[")) != wstring::npos &&
            (right_pos = str_line.find(L"]")) != wstring::npos)
        {
            str_root = WStringToString(str_line.substr(left_pos + 1, right_pos - left_pos - 1));
        }

        if ((equal_div_pos = str_line.find(L"=")) != wstring::npos)
        {
            str_key = WStringToString(str_line.substr(0, equal_div_pos));
            str_value = WStringToString(str_line.substr(equal_div_pos + 1));
            str_key = TrimString(str_key);
            str_value = TrimString(str_value);
        }
#else
        if ((left_pos = str_line.find("[")) != string::npos &&
            (right_pos = str_line.find("]")) != string::npos)
        {
            str_root = str_line.substr(left_pos + 1, right_pos - left_pos - 1);
        }

        if ((equal_div_pos = str_line.find("=")) != string::npos)
        {
            str_key = str_line.substr(0, equal_div_pos);
            str_value = str_line.substr(equal_div_pos + 1);
            str_key = TrimString(str_key);
            str_value = TrimString(str_value);
        }
#endif

        if (!str_root.empty() && !str_key.empty() && !str_value.empty())
        {
            vec_ini.emplace_back(str_root, str_key, str_value);
        }
    }

    for (const auto& node : vec_ini)
    {
        map_ini[node.root].InsertElement(node.key, node.value);
    }

    return 1;
}

// 根据 root 和 key 获取值
string INIParser::GetValue(const string& root, const string& key)
{
    auto itr = map_ini.find(root);
    if (itr != map_ini.end())
    {
        auto sub_itr = itr->second.sub_node.find(key);
        if (sub_itr != itr->second.sub_node.end())
        {
            return sub_itr->second;
        }
    }
    return "";
}

// 写入 INI 文件
int INIParser::WriteINI()
{
    if (filePath.empty())
    {
        return -1;
    }
    string path = WStringToString(filePath);
    ofstream out_conf_file(path);
    if (!out_conf_file)
        return -1;

    for (const auto& pair : map_ini)
    {
        out_conf_file << "[" << pair.first << "]" << endl;
        for (const auto& sub_pair : pair.second.sub_node)
        {
            out_conf_file << sub_pair.first << "=" << sub_pair.second << endl;
        }
    }
    out_conf_file.flush();
    return 1;
}

// 设置值
size_t INIParser::SetValue(const string& root, const string& key, const string& value)
{
    map_ini[root].InsertElement(key, value);
    return map_ini.size();
}
