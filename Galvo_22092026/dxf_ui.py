import sys
import os
import ezdxf
from ezdxf import bbox
from PySide6.QtWidgets import (QApplication, QMainWindow, QPushButton, QVBoxLayout, 
                             QWidget, QFileDialog, QLabel, QTextEdit)
from PySide6.QtCore import Qt

class DXFInfoUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DXF Position Analyzer")
        self.setMinimumSize(400, 300)

        # Main Layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        # File selection
        self.btn_open = QPushButton("Select DXF File")
        self.btn_open.setFixedHeight(40)
        self.btn_open.clicked.connect(self.open_file)
        self.layout.addWidget(self.btn_open)

        self.lbl_file = QLabel("No file selected")
        self.lbl_file.setWordWrap(True)
        self.lbl_file.setStyleSheet("color: #666; font-style: italic;")
        self.layout.addWidget(self.lbl_file)

        # Results Display
        self.results_box = QTextEdit()
        self.results_box.setReadOnly(True)
        self.results_box.setPlaceholderText("Results will appear here...")
        self.layout.addWidget(self.results_box)

        # Styling
        self.setStyleSheet("""
            QMainWindow { background-color: #f5f5f5; }
            QPushButton { 
                background-color: #102a83; 
                color: white; 
                border-radius: 5px; 
                font-weight: bold; 
            }
            QPushButton:hover { background-color: #2846a0; }
            QTextEdit { 
                background-color: white; 
                border: 1px solid #ccc; 
                border-radius: 5px; 
                padding: 10px;
                font-family: 'Consolas', monospace;
                font-size: 13px;
            }
        """)

    def open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open DXF", "", "DXF Files (*.dxf)"
        )
        
        if file_path:
            self.lbl_file.setText(f"File: {os.path.basename(file_path)}")
            self.analyze_dxf(file_path)

    def analyze_dxf(self, filepath):
        try:
            doc = ezdxf.readfile(filepath)
            msp = doc.modelspace()
            
            entities = list(msp)
            if not entities:
                self.results_box.setText("Error: The DXF file is empty.")
                return

            cache = bbox.Cache()
            box = bbox.extents(entities, cache=cache)

            if box.has_data:
                xmin, ymin, _ = box.extmin
                xmax, ymax, _ = box.extmax
                width = xmax - xmin
                height = ymax - ymin

                results = (
                    f"ANALYSIS RESULTS\n"
                    f"{'='*30}\n"
                    f"Filename:   {os.path.basename(filepath)}\n\n"
                    f"START POSITION (Min X, Min Y):\n"
                    f"X: {xmin:>10.4f}\n"
                    f"Y: {ymin:>10.4f}\n\n"
                    f"END POSITION (Max X, Max Y):\n"
                    f"X: {xmax:>10.4f}\n"
                    f"Y: {ymax:>10.4f}\n\n"
                    f"DIMENSIONS:\n"
                    f"Width:  {width:>10.4f} mm\n"
                    f"Height: {height:>10.4f} mm\n"
                    f"{'='*30}"
                )
                self.results_box.setText(results)
            else:
                self.results_box.setText("Error: Could not determine bounding box.")

        except Exception as e:
            self.results_box.setText(f"Critical Error:\n{str(e)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DXFInfoUI()
    window.show()
    sys.exit(app.exec())
