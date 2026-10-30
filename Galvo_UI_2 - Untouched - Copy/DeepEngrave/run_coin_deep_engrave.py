import os
import sys
import time
import argparse

# Ensure project root is in sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from core.coin_3d_engraver import Coin3DReliefEngraver
from core.heightmap_slicer import Heightmap3DSlicer
from machine.galvo_controller import GalvoController

def run_redlight_framing(controller, diameter_mm=27.0, loops=30, field_size=100.0):
    print("\n" + "="*55, flush=True)
    print("STARTING RED LIGHT ALIGNMENT (27.0mm COIN CIRCLE)", flush=True)
    print("Place your 1.0mm brass blank directly under the red circle.", flush=True)
    print("Press Ctrl+C to stop framing.", flush=True)
    print("="*55, flush=True)
    
    galvo_units_per_mm = 65535.0 / field_size
    center_bits = 32767.5
    r = diameter_mm / 2.0
    num_pts = 64
    speed_gu = int(1200 * galvo_units_per_mm)
    
    pts = []
    for i in range(num_pts):
        ang = i * 2.0 * 3.1415926535 / float(num_pts)
        gx = center_bits + (r * 3.1415926535 * 0 + r * 1.0 * (math_cos := (lambda a: __import__('math').cos(a))(ang)) * galvo_units_per_mm)
        gy = center_bits + (r * (math_sin := (lambda a: __import__('math').sin(a))(ang)) * galvo_units_per_mm)
        pts.append((int(round(gx)), int(round(gy))))
    pts.append(pts[0])
    
    red_queue = [{'type': 'jump', 'x': pts[0][0], 'y': pts[0][1], 'speed': speed_gu}]
    for pt in pts[1:]:
        red_queue.append({'type': 'mark', 'x': pt[0], 'y': pt[1], 'speed': speed_gu})
        
    if hasattr(controller.connection, 'reddot_on'):
        controller.connection.reddot_on()
        
    try:
        controller.execute_queue(red_queue, loop_count=loops)
    except KeyboardInterrupt:
        print("\nFraming stopped by user.", flush=True)
    finally:
        if hasattr(controller.connection, 'reddot_off'):
            controller.connection.reddot_off()
        if hasattr(controller, 'galvo_home'):
            controller.galvo_home()
        print("Framing complete. Galvo returned to park position.", flush=True)

def run_3d_preview(gcode_path):
    print(f"\nLaunching 3D OpenGL Bas-Relief Preview for: {gcode_path}", flush=True)
    from PySide6.QtWidgets import QApplication, QMainWindow
    from preview3d import GCode3DPreview
    
    app = QApplication.instance() or QApplication(sys.argv)
    win = QMainWindow()
    win.setWindowTitle("3D Coin Bas-Relief Preview - Galvo Studio")
    win.resize(1000, 800)
    
    preview_widget = GCode3DPreview(win)
    win.setCentralWidget(preview_widget)
    win.show()
    
    with open(gcode_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
        
    preview_widget.sigLoadGcode.emit(lines)
    print("Preview window opened. Inspect layers using the layer slider.", flush=True)
    sys.exit(app.exec())

def execute_queue_with_telemetry(controller, queue, title="3D Laser Engraving"):
    print("\n" + "="*60, flush=True)
    print(f"EXECUTING: {title}", flush=True)
    print("="*60, flush=True)
    total_cmds = len(queue)
    print(f"Total Galvo Commands: {total_cmds}", flush=True)
    start_time = time.time()
    
    def on_progress(idx, total, x, y, ctype):
        if ctype and str(ctype).startswith("pass_change"):
            return
        if idx % 2000 == 0 or idx == total - 1:
            pct = (idx + 1) / float(total) * 100.0
            elapsed = time.time() - start_time
            print(f" -> Progress: {pct:5.1f}% | Cmd {idx+1}/{total} | Elapsed: {elapsed:5.1f}s", flush=True)
            
    try:
        success = controller.execute_queue(queue, loop_count=1, progress_callback=on_progress)
        elapsed = time.time() - start_time
        if success:
            print("\n" + "*"*60, flush=True)
            print(f"ENGRAVING COMPLETED SUCCESSFULLY in {elapsed:.1f}s!", flush=True)
            print("*"*60, flush=True)
        else:
            print("\nJob interrupted or aborted.", flush=True)
    finally:
        if hasattr(controller.connection, 'laser_off'):
            controller.connection.laser_off()
        controller.disconnect()

def main():
    parser = argparse.ArgumentParser(description="3D Laser Relief Engraving for 27mm Coin on 1.7-1.9mm Brass")
    parser.add_argument("--frame", action="store_true", help="Run Red-pointer framing circle for workpiece positioning")
    parser.add_argument("--preview", action="store_true", help="Open 3D OpenGL preview of the bas-relief toolpaths")
    parser.add_argument("--engrave", action="store_true", help="Execute the 3D relief engraving job on the laser")
    parser.add_argument("--mode", choices=["perfect", "vector", "stl"], default="perfect", help="Relief mode: 'perfect' (50-layer compact heightmap), 'stl' (3D mesh), or 'vector'")
    parser.add_argument("--file", type=str, default=None, help="Custom file path (.stl, .png, .dxf)")
    parser.add_argument("--mock", action="store_true", help="Force mock simulator mode (safe dry run)")
    args = parser.parse_args()

    controller = GalvoController()
    deep_dir = os.path.join(BASE_DIR, "DeepEngrave")
    
    # Select target files (Optimized for 27.0mm diameter, 1.7-1.9mm thickness brass)
    if args.mode == "stl" or (args.file and args.file.lower().endswith(('.stl', '.obj'))):
        from core.stl_3d_engraver import STL3DEngraver
        stl_path = args.file or os.path.join(deep_dir, "test_sample_coin.stl")
        engraver = STL3DEngraver(stl_path=stl_path, diameter_mm=27.0, max_depth_mm=0.75, num_layers=50)
        queue_builder = lambda: engraver.compile_job_queue()
        gcode_path = os.path.join(deep_dir, "rupee_10_coin_27mm_sliced.gcode")
        job_title = f"STL 3D Relief ({os.path.basename(stl_path)}, 50 Layers)"
    elif args.mode == "perfect":
        # Check for 16-bit or 8-bit compact PNG
        hmap_path = args.file or os.path.join(deep_dir, "rupee_10_coin_27mm_relief_16bit.png")
        if not os.path.exists(hmap_path):
            hmap_path = os.path.join(deep_dir, "rupee_10_coin_27mm_relief_8bit.png")
        slicer = Heightmap3DSlicer(hmap_path, diameter_mm=27.0, max_depth_mm=0.75, num_layers=50)
        gcode_path = os.path.join(deep_dir, "rupee_10_coin_27mm_sliced.gcode")
        queue_builder = lambda: slicer.compile_sliced_3d_queue()
        job_title = "Compact 27mm Coin 3D Relief (50-Layer Slicing, 0.75mm Depth)"
    else:
        dxf_path = args.file or os.path.join(deep_dir, "rupee_10_coin_27mm_relief.dxf")
        if not os.path.exists(dxf_path):
            dxf_path = os.path.join(deep_dir, "rupee_10_relief_27mm_master.dxf")
        engraver = Coin3DReliefEngraver(dxf_path=dxf_path)
        gcode_path = os.path.join(deep_dir, "rupee_10_coin_27mm_sliced.gcode")
        queue_builder = lambda: engraver.compile_job_queue()
        job_title = "Step-Relief Vector 27mm Coin (Layers 00 to 05)"

    if not (args.frame or args.preview or args.engrave):
        print("\n=================================================================", flush=True)
        print("   3D COIN RELIEF ENGRAVER - 27.0mm RBI SPEC (~1.8mm BRASS)     ", flush=True)
        print("=================================================================", flush=True)
        print("1. [RECOMMENDED] 27mm Coin 3D Relief (50 Sliced Layers, 0.75mm Depth)", flush=True)
        print("2. Red-Light Alignment Framing (Project 27.0mm Circle on Brass)", flush=True)
        print("3. 3D OpenGL Bas-Relief Preview (Inspect Toolpath in 3D)", flush=True)
        print("4. Safe Simulator Dry Run (No Laser Fired)", flush=True)
        print("5. Step-Relief Vector Coin Mode (EZCad/LightBurn 6-Layer)", flush=True)
        print("6. STL 3D Mesh Mode (Direct .stl File Ingestion & Slicing)", flush=True)
        print("7. Exit", flush=True)
        choice = input("\nSelect an option (1-6): ").strip()
        
        if choice == '1':
            controller.connect(force_mock=args.mock)
            q = queue_builder()
            execute_queue_with_telemetry(controller, q, job_title)
        elif choice == '2':
            controller.connect(force_mock=args.mock)
            run_redlight_framing(controller, diameter_mm=27.0, loops=40)
        elif choice == '3':
            run_3d_preview(gcode_path)
        elif choice == '4':
            controller.connect(force_mock=True)
            q = queue_builder()
            execute_queue_with_telemetry(controller, q, job_title + " [SIMULATOR]")
        elif choice == '5':
            dxf_path = os.path.join(deep_dir, "rupee_10_coin_27mm_relief.dxf")
            if not os.path.exists(dxf_path):
                dxf_path = os.path.join(deep_dir, "rupee_10_relief_27mm_master.dxf")
            engraver = Coin3DReliefEngraver(dxf_path=dxf_path)
            controller.connect(force_mock=args.mock)
            q = engraver.compile_job_queue()
            execute_queue_with_telemetry(controller, q, "Step-Relief Vector Coin")
        elif choice == '6':
            from core.stl_3d_engraver import STL3DEngraver
            stl_path = os.path.join(deep_dir, "test_sample_coin.stl")
            engraver = STL3DEngraver(stl_path=stl_path, diameter_mm=27.0, max_depth_mm=0.75, num_layers=50)
            controller.connect(force_mock=args.mock)
            q = engraver.compile_job_queue()
            execute_queue_with_telemetry(controller, q, "STL 3D Mesh Relief (50 Layers)")
        else:
            print("Exiting.", flush=True)
            return

    if args.frame:
        controller.connect(force_mock=args.mock)
        run_redlight_framing(controller, diameter_mm=27.0, loops=40)
    elif args.preview:
        run_3d_preview(gcode_path)
    elif args.engrave:
        controller.connect(force_mock=args.mock)
        q = queue_builder()
        execute_queue_with_telemetry(controller, q, job_title)

if __name__ == "__main__":
    main()
