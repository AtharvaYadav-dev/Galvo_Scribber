import re

with open("bridges/cad_bridge.py", "r", encoding="utf-8") as f:
    text = f.read()

# 1. Add FileImportWorker class before CadBridge
worker_code = '''
class FileImportWorker(QThread):
    finished = Signal(dict)
    error = Signal(str)

    def __init__(self, local_path, ext, field_size, parent=None):
        super().__init__(parent)
        self.local_path = local_path
        self.ext = ext
        self.field_size = field_size

    def run(self):
        try:
            polygons = []
            if self.ext == ".dxf":
                parser = DXFParser(self.local_path)
                polygons = parser.parse_to_polygons(field_size=self.field_size)
            elif self.ext == ".svg":
                parser = SVGParser(field_size=self.field_size)
                polygons = parser.parse_to_polygons(self.local_path)
            elif self.ext in ('.gbr', '.gtl', '.gbl', '.gto', '.gbo', '.gts', '.gbs', '.gml', '.gtp', '.gbp', '.drl', '.txt'):
                parser = GerberParser(self.local_path)
                polygons = parser.parse_to_polygons(field_size=self.field_size)
            elif self.ext in ('.bmp', '.jpg', '.jpeg', '.png'):
                parser = ImageParser(field_size=self.field_size)
                polygons = parser.parse_to_polygons(self.local_path)
            else:
                parser = SVGParser(field_size=self.field_size)
                polygons = parser.parse_to_polygons(self.local_path)

            if not polygons:
                self.error.emit(f"No vector curves or polylines found in {os.path.basename(self.local_path)}.")
                return

            min_x, max_x = float('inf'), float('-inf')
            min_y, max_y = float('inf'), float('-inf')
            for poly in polygons:
                for pt in poly:
                    min_x = min(min_x, pt[0])
                    max_x = max(max_x, pt[0])
                    min_y = min(min_y, pt[1])
                    max_y = max(max_y, pt[1])

            if min_x == float('inf'):
                self.error.emit("Invalid geometry found.")
                return

            bw = float(max_x - min_x) if max_x > min_x else 10.0
            bh = float(max_y - min_y) if max_y > min_y else 10.0
            cx = float((min_x + max_x) / 2.0)
            cy = float((min_y + max_y) / 2.0)

            try:
                from shapely.geometry import LineString
                has_shapely = True
            except ImportError:
                has_shapely = False

            rel_paths = []
            for poly in polygons:
                if len(poly) < 2:
                    continue
                rel_poly = [(pt[0] - cx, pt[1] - cy) for pt in poly]
                if has_shapely and len(rel_poly) > 4:
                    try:
                        ls = LineString(rel_poly)
                        sim = ls.simplify(0.012, preserve_topology=True)
                        rel_poly = list(sim.coords)
                    except Exception:
                        pass
                rel_paths.append([[round(p[0], 3), round(p[1], 3)] for p in rel_poly])

            file_name = os.path.basename(self.local_path)
            shape_name = os.path.splitext(file_name)[0]

            result = {
                "shape_name": shape_name,
                "file_name": file_name,
                "cx": cx,
                "cy": cy,
                "bw": bw,
                "bh": bh,
                "rel_paths": rel_paths,
                "raw_polygons": polygons,
                "poly_count": len(polygons)
            }
            self.finished.emit(result)

        except Exception as e:
            self.error.emit(str(e))
'''

bridge_marker = "class CadBridge(QObject):"
assert bridge_marker in text, "CadBridge class not found"
text = text.replace(bridge_marker, worker_code + "\n\n" + bridge_marker, 1)

# 2. Update importFile implementation
old_import = """    @Slot(str)
    def importFile(self, file_path: str):
        \"\"\"
        Parses a CAD vector or raster file (.dxf, .svg, .gbr/.gtl/... Gerber, .png/.jpg/.bmp)
        and converts entities into native QML shapes that display immediately on the QML Canvas.
        \"\"\"
        if not file_path:
            return

        # Correctly decode Qt URL or raw Windows filesystem path (spaces, %20, etc.)
        u = QUrl(file_path)
        if u.isLocalFile():
            local_path = u.toLocalFile()
        else:
            local_path = file_path
            if local_path.startswith("file:///"):
                local_path = local_path[8:]
            local_path = unquote(local_path)

        local_path = os.path.normpath(local_path)
        self._last_imported_path = local_path

        if not os.path.exists(local_path):
            self._set_status(f"File not found: {local_path}")
            return

        file_name = os.path.basename(local_path)
        ext = os.path.splitext(local_path)[1].lower()
        self._set_status(f"Importing CAD file: {file_name}...")
        imported_shapes = []

        try:
            polygons = []
            if ext == ".dxf":
                parser = DXFParser(local_path)
                polygons = parser.parse_to_polygons(field_size=self.galvo_config.field_size)
            elif ext == ".svg":
                parser = SVGParser(field_size=self.galvo_config.field_size)
                polygons = parser.parse_to_polygons(local_path)
            elif ext in ('.gbr', '.gtl', '.gbl', '.gto', '.gbo', '.gts', '.gbs', '.gml', '.gtp', '.gbp', '.drl', '.txt'):
                parser = GerberParser(local_path)
                polygons = parser.parse_to_polygons(field_size=self.galvo_config.field_size)
            elif ext in ('.bmp', '.jpg', '.jpeg', '.png'):
                parser = ImageParser(field_size=self.galvo_config.field_size)
                polygons = parser.parse_to_polygons(local_path)
            else:
                # Default fallback attempt as SVG
                parser = SVGParser(field_size=self.galvo_config.field_size)
                polygons = parser.parse_to_polygons(local_path)

            if not polygons:
                self._set_status(f"No vector curves or polylines found in {file_name}.")
                return

            # Compute overall bounding box
            min_x, max_x = float('inf'), float('-inf')
            min_y, max_y = float('inf'), float('-inf')
            for poly in polygons:
                for pt in poly:
                    min_x = min(min_x, pt[0])
                    max_x = max(max_x, pt[0])
                    min_y = min(min_y, pt[1])
                    max_y = max(max_y, pt[1])

            if min_x == float('inf'):
                self._set_status(f"Invalid geometry in {file_name}.")
                return

            bw = float(max_x - min_x) if max_x > min_x else 10.0
            bh = float(max_y - min_y) if max_y > min_y else 10.0
            cx = float((min_x + max_x) / 2.0)
            cy = float((min_y + max_y) / 2.0)

            # Normalize polylines relative to (cx, cy)
            rel_paths = []
            for poly in polygons:
                rel_poly = [[float(round(pt[0] - cx, 3)), float(round(pt[1] - cy, 3))] for pt in poly]
                rel_paths.append(rel_poly)

            # Package as a unified QML Vector CAD Shape
            shape_name = os.path.splitext(file_name)[0]
            qml_shape = {
                "id": int(len(self._shapes) + 1),
                "name": str(shape_name),
                "type": "polygon",
                "xMm": float(round(cx, 2)),
                "yMm": float(round(cy, 2)),
                "wMm": float(round(bw, 2)),
                "hMm": float(round(bh, 2)),
                "rotation": 0.0,
                "penId": 0,
                "hatched": False,
                "visible": True,
                "locked": False,
                "paths": rel_paths
            }
            imported_shapes.append(qml_shape)

            # Emit to QML Canvas
            self.shapesImported.emit(imported_shapes)
            self._set_status(f"Imported '{shape_name}' ({len(polygons)} curves, {bw:.1f}x{bh:.1f}mm)")

        except Exception as e:
            err_msg = f"Import error: {e}"
            print(f"[CadBridge] {err_msg}")
            self._set_status(err_msg)"""

new_import = """    @Slot(str)
    def importFile(self, file_path: str):
        \"\"\"
        Parses a CAD vector or raster file (.dxf, .svg, .gbr/.gtl/... Gerber, .png/.jpg/.bmp)
        in a background QThread to ensure the UI NEVER hangs, freezes, or closes on heavy files.
        \"\"\"
        if not file_path:
            return

        # Correctly decode Qt URL or raw Windows filesystem path (spaces, %20, etc.)
        u = QUrl(file_path)
        if u.isLocalFile():
            local_path = u.toLocalFile()
        else:
            local_path = file_path
            if local_path.startswith("file:///"):
                local_path = local_path[8:]
            local_path = unquote(local_path)

        local_path = os.path.normpath(local_path)
        self._last_imported_path = local_path

        if not os.path.exists(local_path):
            self._set_status(f"File not found: {local_path}")
            return

        file_name = os.path.basename(local_path)
        ext = os.path.splitext(local_path)[1].lower()
        self._set_status(f"Importing {file_name}... Parsing vector entities in background.")

        # Launch background worker
        self._import_worker = FileImportWorker(local_path, ext, self.galvo_config.field_size, self)
        self._import_worker.finished.connect(self._on_import_finished)
        self._import_worker.error.connect(lambda err: self._set_status(f"Import error: {err}"))
        self._import_worker.start()

    def _on_import_finished(self, res: dict):
        new_id = int(len(self._shapes) + 1)
        qml_shape = {
            "id": new_id,
            "name": str(res["shape_name"]),
            "type": "polygon",
            "xMm": float(round(res["cx"], 2)),
            "yMm": float(round(res["cy"], 2)),
            "wMm": float(round(res["bw"], 2)),
            "hMm": float(round(res["bh"], 2)),
            "rotation": 0.0,
            "penId": 0,
            "hatched": False,
            "visible": True,
            "locked": False,
            "paths": res["rel_paths"]
        }

        # Cache full-precision raw polygons in backend for laser marking
        if not hasattr(self, "_raw_imported_shapes"):
            self._raw_imported_shapes = {}
        self._raw_imported_shapes[new_id] = res["raw_polygons"]

        self.shapesImported.emit([qml_shape])
        self._set_status(f"Imported '{res['shape_name']}' ({res['poly_count']} curves, {res['bw']:.1f}x{res['bh']:.1f}mm)")"""

assert old_import in text, "old_import not found"
text = text.replace(old_import, new_import, 1)

# 3. In _shape_to_polygons, check _raw_imported_shapes for high-precision marking
old_dxf_case = """            elif stype in ["dxf", "svg"]:
                raw_paths = shp.get("paths", [])
                if raw_paths:
                    return [[rotate_and_shift(p[0], p[1]) for p in subpath] for subpath in raw_paths if len(subpath) >= 2]"""

new_dxf_case = """            elif stype in ["dxf", "svg"] or (shp.get("id") and hasattr(self, "_raw_imported_shapes") and shp.get("id") in self._raw_imported_shapes):
                shp_id = shp.get("id")
                if hasattr(self, "_raw_imported_shapes") and shp_id in self._raw_imported_shapes:
                    raw_polys = self._raw_imported_shapes[shp_id]
                    return [[rotate_and_shift(p[0] - cx, p[1] - cy) for p in subpath] for subpath in raw_polys if len(subpath) >= 2]
                raw_paths = shp.get("paths", [])
                if raw_paths:
                    return [[rotate_and_shift(p[0], p[1]) for p in subpath] for subpath in raw_paths if len(subpath) >= 2]"""

assert old_dxf_case in text, "old_dxf_case not found"
text = text.replace(old_dxf_case, new_dxf_case, 1)

with open("bridges/cad_bridge.py", "w", encoding="utf-8") as f:
    f.write(text)

print("cad_bridge.py updated with FileImportWorker and async background import!")

