import json
with open('style.json', 'r', encoding='utf-8') as f:
    style = json.load(f)

for section in ['QMainWindow', 'QCustomSlideMenu', 'QStackedWidget']:
    for item in style.get(section, []):
        for nav in item.get('navigation', []):
            for btn_group in nav.get('navigationButtons', []):
                keys_to_delete = [k for k, v in btn_group.items() if v in ["jogPage", "programPage", "printPage", "terminalPage", "laserconfPage", "cameraPage", "ezcadPage", "parametermatrixPage"]]
                for k in keys_to_delete:
                    del btn_group[k]

with open('style.json', 'w', encoding='utf-8') as f:
    json.dump(style, f, indent=4)
