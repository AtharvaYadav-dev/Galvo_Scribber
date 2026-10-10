import os
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                             QLineEdit, QRadioButton, QPushButton, QLabel, 
                             QMessageBox, QButtonGroup, QApplication, QComboBox)
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt
import qrcode
import ezdxf

try:
    import barcode
    from barcode.writer import ImageWriter
except ImportError:
    barcode = None

class QRBarcodeWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        # Target Save Directory
        self.save_dir = r"d:\Atharva\Galvo_Scribber\Galvo_UI_2\QR\Barcode DXF"
        if not os.path.exists(self.save_dir):
            try:
                os.makedirs(self.save_dir)
            except Exception as e:
                print(f"Could not create directory {self.save_dir}: {e}")
                self.save_dir = os.getcwd()
        
        self.current_matrix = None
        self.current_type = None
        self.initUI()
        
    def initUI(self):
        layout = QVBoxLayout(self)
        
        # 1. Input Text
        self.input_text = QLineEdit()
        self.input_text.setPlaceholderText("Yahan apna text, number ya link dalein...")
        layout.addWidget(QLabel("Data Input:"))
        layout.addWidget(self.input_text)
        
        # 2. Selection
        type_layout = QHBoxLayout()
        self.radio_qr = QRadioButton("QR Code")
        self.radio_barcode = QRadioButton("Barcode (Code128)")
        self.radio_qr.setChecked(True)
        type_layout.addWidget(self.radio_qr)
        type_layout.addWidget(self.radio_barcode)
        
        self.btn_group = QButtonGroup(self)
        self.btn_group.addButton(self.radio_qr)
        self.btn_group.addButton(self.radio_barcode)
        layout.addLayout(type_layout)
        
        # 3. Generate Button
        self.btn_generate = QPushButton("Generate Preview")
        self.btn_generate.setStyleSheet("background-color: #4CAF50; color: white; padding: 5px;")
        self.btn_generate.clicked.connect(self.generate_preview)
        layout.addWidget(self.btn_generate)
        
        # 4. Preview Area
        self.preview_label = QLabel("Preview yahan dikhega")
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setMinimumHeight(250)
        self.preview_label.setStyleSheet("border: 1px solid gray; background-color: white;")
        layout.addWidget(self.preview_label)
        
        # 5. File Format and Name
        file_layout = QHBoxLayout()
        
        self.format_dropdown = QComboBox()
        self.format_dropdown.addItems(["DXF", "SVG"])
        file_layout.addWidget(QLabel("Format:"))
        file_layout.addWidget(self.format_dropdown)
        
        self.filename_input = QLineEdit()
        self.filename_input.setPlaceholderText("File ka naam dalein (e.g. My_QR_Code)")
        file_layout.addWidget(QLabel("File Name:"))
        file_layout.addWidget(self.filename_input)
        
        layout.addLayout(file_layout)
        
        # 6. Save Button
        self.btn_save = QPushButton("Save File")
        self.btn_save.setStyleSheet("background-color: #008CBA; color: white; padding: 5px;")
        self.btn_save.clicked.connect(self.save_file)
        layout.addWidget(self.btn_save)

    def generate_preview(self):
        text = self.input_text.text().strip()
        if not text:
            QMessageBox.warning(self, "Error", "Please input data enter karein!")
            return
            
        if self.radio_qr.isChecked():
            self.generate_qr(text)
        else:
            self.generate_barcode(text)
            
    def generate_qr(self, text):
        qr = qrcode.QRCode(version=1, box_size=10, border=4)
        qr.add_data(text)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Save boolean matrix for DXF generation
        self.current_matrix = qr.get_matrix()
        self.current_type = "QR"
        
        # Display preview
        img_temp = "temp_qr.png"
        img.save(img_temp)
        pixmap = QPixmap(img_temp)
        self.preview_label.setPixmap(pixmap.scaled(self.preview_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
        if os.path.exists(img_temp):
            os.remove(img_temp)
        
    def generate_barcode(self, text):
        if barcode is None:
            QMessageBox.warning(self, "Error", "python-barcode module installed nahi hai.\nTerminal me run karein: pip install python-barcode")
            return
            
        try:
            Code128 = barcode.get_barcode_class('code128')
            # SVGWriter gives us an easy way to get binary data, but we can also use ImageWriter for preview
            code_obj = Code128(text, writer=ImageWriter())
            
            # Save preview image
            img_temp = "temp_barcode"
            options = {"write_text": False}
            filepath = code_obj.save(img_temp, options=options)
            
            pixmap = QPixmap(filepath)
            self.preview_label.setPixmap(pixmap.scaled(self.preview_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
            if os.path.exists(filepath):
                os.remove(filepath)
                
            # Get binary string (1s and 0s) for DXF
            # 'build()' returns a list of binary strings
            self.current_matrix = code_obj.build() 
            self.current_type = "BARCODE"
            
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Barcode generate karne me error:\n{str(e)}")

    def save_file(self):
        if self.current_matrix is None:
            QMessageBox.warning(self, "Error", "Pehle 'Generate Preview' par click karein!")
            return
            
        filename = self.filename_input.text().strip()
        if not filename:
            filename = f"Generated_{self.current_type}"
            
        file_format = self.format_dropdown.currentText()
        ext = f".{file_format.lower()}"
        
        if not filename.lower().endswith(ext):
            filename += ext
            
        filepath = os.path.join(self.save_dir, filename)
        
        try:
            with open(filepath, 'w') as f:
                if file_format == "DXF":
                    # Minimal DXF header just to start the entities section
                    f.write("  0\nSECTION\n  2\nENTITIES\n")
                    
                    def write_polyline(x1, y1, x2, y2, x3, y3, x4, y4):
                        f.write("  0\nPOLYLINE\n  8\n0\n 66\n1\n 70\n1\n")
                        f.write(f"  0\nVERTEX\n  8\n0\n 10\n{x1}\n 20\n{y1}\n 30\n0.0\n")
                        f.write(f"  0\nVERTEX\n  8\n0\n 10\n{x2}\n 20\n{y2}\n 30\n0.0\n")
                        f.write(f"  0\nVERTEX\n  8\n0\n 10\n{x3}\n 20\n{y3}\n 30\n0.0\n")
                        f.write(f"  0\nVERTEX\n  8\n0\n 10\n{x4}\n 20\n{y4}\n 30\n0.0\n")
                        f.write("  0\nSEQEND\n  8\n0\n")

                    if self.current_type == "QR":
                        rows = len(self.current_matrix)
                        cols = len(self.current_matrix[0])
                        for y in range(rows):
                            x = 0
                            while x < cols:
                                if self.current_matrix[y][x]:
                                    start_x = x
                                    while x < cols and self.current_matrix[y][x]:
                                        x += 1
                                    width = x - start_x
                                    y_top = rows - y
                                    y_bottom = rows - y - 1
                                    pad = 0.002
                                    write_polyline(start_x + pad, y_bottom + pad, 
                                                start_x + width - pad, y_bottom + pad, 
                                                start_x + width - pad, y_top - pad, 
                                                start_x + pad, y_top - pad)
                                else:
                                    x += 1
                    elif self.current_type == "BARCODE":
                        row_data = self.current_matrix[0]
                        height = 40
                        x = 0
                        while x < len(row_data):
                            if row_data[x] == '1':
                                start_x = x
                                while x < len(row_data) and row_data[x] == '1':
                                    x += 1
                                width = x - start_x
                                pad = 0.002
                                write_polyline(start_x + pad, pad, 
                                            start_x + width - pad, pad, 
                                            start_x + width - pad, height - pad, 
                                            start_x + pad, height - pad)
                            else:
                                x += 1
                    f.write("  0\nENDSEC\n  0\nEOF\n")
                    
                elif file_format == "SVG":
                    scale = 10 # Scaling factor to make the SVG larger
                    
                    if self.current_type == "QR":
                        w_val = len(self.current_matrix[0]) * scale
                        h_val = len(self.current_matrix) * scale
                    else:
                        w_val = len(self.current_matrix[0]) * scale
                        h_val = 40 * scale
                        
                    f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
                    f.write(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w_val} {h_val}" width="{w_val}" height="{h_val}">\n')
                    f.write('  <g fill="black">\n')
                    
                    if self.current_type == "QR":
                        rows = len(self.current_matrix)
                        cols = len(self.current_matrix[0])
                        for y in range(rows):
                            x = 0
                            while x < cols:
                                if self.current_matrix[y][x]:
                                    start_x = x
                                    while x < cols and self.current_matrix[y][x]:
                                        x += 1
                                    width = x - start_x
                                    f.write(f'    <rect x="{start_x * scale}" y="{y * scale}" width="{width * scale}" height="{scale}" />\n')
                                else:
                                    x += 1
                    elif self.current_type == "BARCODE":
                        row_data = self.current_matrix[0]
                        x = 0
                        while x < len(row_data):
                            if row_data[x] == '1':
                                start_x = x
                                while x < len(row_data) and row_data[x] == '1':
                                    x += 1
                                width = x - start_x
                                f.write(f'    <rect x="{start_x * scale}" y="0" width="{width * scale}" height="{h_val}" />\n')
                            else:
                                x += 1
                    f.write('  </g>\n</svg>\n')
            
            QMessageBox.information(self, "Success", f"File successfully save ho gayi hai:\n{filepath}")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"File save karne me error aaya:\n{str(e)}")
