with open('bridges/cad_bridge.py', 'r', encoding='utf-8') as f:
    content = f.read()

pens_methods = """
    def _default_pens(self):
        return [
            {"id": 0, "name": "Pen 0 (Default)", "color": "#00E5FF", "speed": 1200, "power": 50, "freq": 35, "passes": 1},
            {"id": 1, "name": "Pen 1 (Blue)",    "color": "#2563EB", "speed": 1800, "power": 40, "freq": 45, "passes": 1},
            {"id": 2, "name": "Pen 2 (Red)",     "color": "#EF4444", "speed": 800,  "power": 75, "freq": 30, "passes": 2},
            {"id": 3, "name": "Pen 3 (Green)",   "color": "#10B981", "speed": 2000, "power": 30, "freq": 60, "passes": 1},
            {"id": 4, "name": "Pen 4 (Amber)",   "color": "#F59E0B", "speed": 1500, "power": 60, "freq": 40, "passes": 1},
            {"id": 5, "name": "Pen 5 (Purple)",  "color": "#A855F7", "speed": 1000, "power": 70, "freq": 35, "passes": 1},
            {"id": 6, "name": "Pen 6 (Cyan)",    "color": "#06B6D4", "speed": 2200, "power": 25, "freq": 70, "passes": 1},
            {"id": 7, "name": "Pen 7 (Brown)",   "color": "#854D0E", "speed": 600,  "power": 85, "freq": 25, "passes": 3}
        ]

    def _load_pens(self):
        if os.path.exists(self.PENS_CONFIG_FILE):
            try:
                with open(self.PENS_CONFIG_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, list) and len(data) > 0:
                        print(f"[CadBridge] Loaded {len(data)} Pens from {self.PENS_CONFIG_FILE}")
                        return data
            except Exception as e:
                print(f"[CadBridge] Error loading pens.json: {e}")
        return self._default_pens()

    @Slot(result=list)
    def getPens(self):
        return self._pens

    @Slot(list)
    def savePens(self, pens_list):
        try:
            self._pens = list(pens_list)
            os.makedirs(os.path.dirname(self.PENS_CONFIG_FILE), exist_ok=True)
            with open(self.PENS_CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(self._pens, f, indent=2)
            print(f"[CadBridge] Saved {len(self._pens)} Pens to {self.PENS_CONFIG_FILE}")
            self.pensChanged.emit(self._pens)
        except Exception as e:
            print(f"[CadBridge] Error saving pens: {e}")

    @Slot(str, str, result=int)
    def addPen(self, name="", color=""):
        next_id = 0
        for p in self._pens:
            if p.get("id", 0) >= next_id:
                next_id = p.get("id", 0) + 1
        distinct_colors = ["#EC4899", "#14B8A6", "#EAB308", "#6366F1", "#F97316", "#84CC16", "#06B6D4", "#A855F7", "#F43F5E", "#3B82F6"]
        col = color if color else distinct_colors[(next_id - 8) % len(distinct_colors)]
        p_name = name if name else f"Pen {next_id}"
        new_pen = {
            "id": next_id,
            "name": p_name,
            "color": col,
            "speed": 1500,
            "power": 50,
            "freq": 35,
            "passes": 1
        }
        self._pens.append(new_pen)
        self.savePens(self._pens)
        print(f"[CadBridge] Added Pen {next_id} ({p_name}, {col})")
        return next_id

    @Slot(int, str)
    def updatePenColor(self, pen_id, color):
        for p in self._pens:
            if p.get("id") == pen_id:
                p["color"] = color
                break
        self.savePens(self._pens)
        print(f"[CadBridge] Updated Pen {pen_id} color to {color}")

    @Slot(int, str, result=bool)
    def updatePenName(self, pen_id, name):
        for p in self._pens:
            if p.get("id") == pen_id:
                p["name"] = name
                self.savePens(self._pens)
                return True
        return False

    @Slot(int)
    def deletePen(self, pen_id):
        if pen_id == 0:
            return
        self._pens = [p for p in self._pens if p.get("id") != pen_id]
        self.savePens(self._pens)
        print(f"[CadBridge] Deleted Pen {pen_id}")
"""

target = "    @Slot(float)\n    def setFieldSize(self, size: float):"
if target in content:
    content = content.replace(target, pens_methods + "\n" + target, 1)
    print("Inserted pens methods before setFieldSize")
else:
    print("WARNING: target not found!")

with open('bridges/cad_bridge.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("Saved bridges/cad_bridge.py")
