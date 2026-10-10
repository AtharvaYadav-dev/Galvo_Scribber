import xml.etree.ElementTree as ET
try:
    for node in ET.parse('interface.ui').iter('widget'):
        if node.get('class') == 'QPushButton':
            print(node.get('name'))
    for node in ET.parse('interface.ui').iter('widget'):
        if node.get('class') == 'QRadioButton':
            print(node.get('name'))
except Exception as e:
    print(e)
