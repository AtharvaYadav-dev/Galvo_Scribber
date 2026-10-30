import os
import sys
import time

# Headless offscreen platform for Qt
os.environ["QT_QPA_PLATFORM"] = "offscreen"
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt, QPointF, QRectF
from PySide6.QtGui import QPainterPath

from cad_canvas import CadCanvasWidget
from cad_items import CadRectItem, CadTextItem, CadHatchItem

def run_test():
    app = QApplication.instance() or QApplication(sys.argv)
    from PySide6.QtGui import QFont
    app.setFont(QFont("Segoe UI", 9))
    
    # Mock main window
    class MockMainWindow:
        def __init__(self):
            self.galvo_config = None
            from core.motion_planner import MotionPlanner
            self.planner = MotionPlanner()
            self.galvo_controller = None

    mw = MockMainWindow()
    widget = CadCanvasWidget(main_window=mw)
    widget.resize(1100, 750)
    widget.show()

    # 1. Test Power On Timer
    widget._update_power_on_timer()
    print(f"Power on timer text: {widget.lbl_power_timer.text()}")
    assert ":" in widget.lbl_power_timer.text()

    # 2. Add shapes: a rectangle and a text item
    rect = CadRectItem(QRectF(-20, -20, 40, 40))
    rect.name = "Box_1"
    widget.scene.addItem(rect)

    text = CadTextItem("Laser", QPointF(-10, 10))
    text.name = "Text_1"
    widget.scene.addItem(text)

    # Add hatch to rect
    hatch = CadHatchItem(target_item=rect, line_pitch=1.0, angle_deg=45.0)
    rect.hatch_items.append(hatch)

    # Select text
    text.setSelected(True)
    widget.scene.selectionChangedCustom.emit()
    print(f"Selection status: {widget.lbl_status_selection.text()}")
    assert "Text_1" in widget.lbl_status_selection.text()

    # 3. Test Red light guide framing
    widget._toggle_red_light()
    assert widget.is_framing is True
    assert widget.btn_red_light.text() == "STOP (F1)"
    assert widget.framing_rect_item is not None
    print("Red light guide started successfully.")

    # Stop Red light guide
    widget._toggle_red_light()
    assert widget.is_framing is False
    assert widget.btn_red_light.text() == "Red(F1)"
    print("Red light guide stopped successfully.")

    # 4. Test Part Counter & Reset Button
    widget.edit_part_no.setText("15")
    assert widget.part_counter == 15
    widget._reset_counter()
    assert widget.part_counter == 0
    assert widget.edit_part_no.text() == "0"
    print("Part counter reset verified.")

    # 5. Test Mark (F2) Execution
    widget.cb_mark_select.setChecked(False) # mark all shapes
    widget._execute_mark()
    assert len(mw.planner.send_queue) > 0
    print(f"Mark generated {len(mw.planner.send_queue)} planner commands (contours + hatches).")

    # Simulate mark finished
    widget._on_mark_finished(True)
    assert widget.part_counter == 1
    assert widget.total_counter == 1
    assert widget.edit_part_no.text() == "1"
    assert widget.edit_total_no.text() == "1"
    print("Mark finished successfully, counter updated to 1.")

    # 6. Grab screenshot of bottom execution bar
    container = widget.findChild(type(widget.btn_red_light.parentWidget()))
    bottom_bar = widget.btn_red_light.parentWidget()
    pix = bottom_bar.grab()
    out_path = os.path.join(r"C:\Users\EXPRESS\.gemini\antigravity-ide\brain\c1319201-ddb2-4088-9d96-6c9d27f2627a\scratch", "bottom_bar_preview.png")
    pix.save(out_path)
    print(f"Saved bottom bar preview to {out_path}")

    # Also grab entire widget screenshot
    full_pix = widget.grab()
    full_out = os.path.join(r"C:\Users\EXPRESS\.gemini\antigravity-ide\brain\c1319201-ddb2-4088-9d96-6c9d27f2627a\scratch", "cad_canvas_full_preview.png")
    full_pix.save(full_out)
    print(f"Saved full canvas preview to {full_out}", flush=True)

    print("ALL TESTS PASSED SUCCESSFULLY!", flush=True)
    os._exit(0)

if __name__ == "__main__":
    run_test()
