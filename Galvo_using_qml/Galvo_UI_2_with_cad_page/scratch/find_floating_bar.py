with open('qml/components/cad/CadCanvas.qml', 'r', encoding='utf-8') as f:
    text = f.read()

import re
matches = [m.start() for m in re.finditer(r'floating|quickAction|contextBar|toolbar|trash|delete', text, re.IGNORECASE)]
for idx in matches[:15]:
    start = max(0, text.rfind('\n', 0, idx))
    end = text.find('\n', idx)
    print(text[start:end].strip())

