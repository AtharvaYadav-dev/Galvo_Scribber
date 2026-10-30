import json

with open('config/pens.json', 'r', encoding='utf-8') as f:
    pens = json.load(f)

for p in pens:
    if p.get('id') == 0:
        p['color'] = '#00E5FF'
        p['name'] = 'Pen 0 (Default)'

with open('config/pens.json', 'w', encoding='utf-8') as f:
    json.dump(pens, f, indent=2)

print("Updated Pen 0 in config/pens.json to #00E5FF")

