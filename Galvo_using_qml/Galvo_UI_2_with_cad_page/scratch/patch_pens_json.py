import json

with open('config/pens.json', 'r', encoding='utf-8') as f:
    pens = json.load(f)

for p in pens:
    if p['id'] == 1 and p.get('color') == '#FFFFFF':
        p['color'] = '#2563EB'

with open('config/pens.json', 'w', encoding='utf-8') as f:
    json.dump(pens, f, indent=2)

print("config/pens.json updated successfully!")

