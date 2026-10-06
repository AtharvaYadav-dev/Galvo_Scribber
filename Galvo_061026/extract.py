import re
import os

ui_file = r'd:\TeamDev\DLL_Galvo\GalvoUI_1\ui_interface.py'

with open(ui_file, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Track which page a widget is added to.
# A widget is added to a layout, which is added to a frame, etc.
# Actually, since the pages are created sequentially in setupUi, we can track the current "page" block.

current_page = None
page_widgets = {
    'joggalvoPage': [],
    'laserconfgalvoPage': [],
    'programgalvoPage': [],
    'printgalvoPage': [],
    'configgalvoPage': []
}

pattern_page = re.compile(r'self\.(.*?Page) = QWidget')
pattern_widget = re.compile(r'self\.(\w+) = (QPushButton|QLineEdit|QComboBox|QCheckBox|QRadioButton)\(')

for line in lines:
    m_page = pattern_page.search(line)
    if m_page:
        page_name = m_page.group(1)
        if page_name in page_widgets:
            current_page = page_name
        else:
            current_page = None
    
    m_widget = pattern_widget.search(line)
    if m_widget and current_page:
        widget_name = m_widget.group(1)
        widget_type = m_widget.group(2)
        page_widgets[current_page].append((widget_name, widget_type))

# Also, some widgets might be added to frames outside the main page definition? In Qt generated code, they are sequential.
# Let's generate the setup methods.

actions = {
    'joggalvoPage': 'jogGalvoAction',
    'laserconfgalvoPage': 'laserConfGalvoAction',
    'programgalvoPage': 'programsGalvoAction',
    'printgalvoPage': 'printGalvoAction',
    'configgalvoPage': 'configGalvoAction'
}

methods = {
    'joggalvoPage': 'setupJogGalvo',
    'laserconfgalvoPage': 'setupLaserConfGalvo',
    'programgalvoPage': 'setupProgramsGalvo',
    'printgalvoPage': 'setupPrintGalvo',
    'configgalvoPage': 'setupConfigGalvo'
}

with open(r'd:\TeamDev\DLL_Galvo\GalvoUI_1\scratch_snippets.txt', 'w', encoding='utf-8') as out:
    for page, widgets in page_widgets.items():
        out.write(f"    def {methods[page]}(self):\n")
        out.write(f"        widget_list = []\n")
        for w_name, w_type in widgets:
            # role is usually name without 'PushButton', 'LineEdit', etc.
            role = w_name
            for suffix in ['PushButton', 'LineEdit', 'ComboBox', 'CheckBox', 'RadioButton', '_RadioButton']:
                if role.endswith(suffix):
                    role = role[:-len(suffix)]
            
            # Determine signal based on type
            signal = "clicked"
            if w_type == "QLineEdit": signal = "textChanged"  # or returnPressed
            elif w_type == "QComboBox": signal = "currentTextChanged"
            elif w_type in ["QCheckBox", "QRadioButton"]: signal = "clicked"
            
            out.write(f"        widget_list.append(self.wh.configWidget(self, {w_type}, \"{w_name}\", \"{signal}\", self.{actions[page]}, role=\"{role}\"))\n")
        
        out.write(f"        self.util.dedupeList(widget_list)\n")
        out.write(f"        self.{page.replace('Page', '_widgets')} = self.wh.createMap(*widget_list)\n\n")

print("Done generating snippets.")
