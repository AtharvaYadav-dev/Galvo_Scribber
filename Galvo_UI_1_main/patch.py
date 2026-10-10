import json
with open('style.json', 'r', encoding='utf-8') as f:
    style = json.load(f)

for stacked in style.get('QStackedWidget', []):
    for nav in stacked.get('navigation', []):
        for btn_group in nav.get('navigationButtons', []):
            keys_to_delete = [k for k, v in btn_group.items() if v in ["jogPage", "programPage", "printPage", "terminalPage", "laserconfPage", "cameraPage"]]
            for k in keys_to_delete:
                del btn_group[k]

with open('style.json', 'w', encoding='utf-8') as f:
    json.dump(style, f, indent=4)
