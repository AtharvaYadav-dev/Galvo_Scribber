import sys
import os
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLineEdit, QRadioButton, QPushButton, QLabel, 
                             QMessageBox, QButtonGroup)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
import qrcode
import ezdxf

try:
    import barcode
    from barcode.writer import ImageWriter
except ImportError:
    barcode = None

class QRBarcodeWidget(QWidget):
    def __init__(self):
        super().__init__()
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
        self.setWindowTitle("QR & Barcode to DXF Generator")
        self.resize(500, 550)
        layout = QVBoxLayout()
        
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
        
        self.btn_group = QButtonGroup()
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
        
        # 5. DXF File Name
        self.filename_input = QLineEdit()
        self.filename_input.setPlaceholderText("File ka naam dalein (e.g. My_QR_Code)")
        layout.addWidget(QLabel("DXF File Name:"))
        layout.addWidget(self.filename_input)
        
        # 6. Save Button
        self.btn_save = QPushButton("Save DXF")
        self.btn_save.setStyleSheet("background-color: #008CBA; color: white; padding: 5px;")
        self.btn_save.clicked.connect(self.save_dxf)
        layout.addWidget(self.btn_save)
        
        self.setLayout(layout)

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
            filepath = code_obj.save(img_temp)
            
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

    def save_dxf(self):
        if self.current_matrix is None:
            QMessageBox.warning(self, "Error", "Pehle 'Generate Preview' par click karein!")
            return
            
        filename = self.filename_input.text().strip()
        if not filename:
            filename = f"Generated_{self.current_type}"
            
        if not filename.lower().endswith(".dxf"):
            filename += ".dxf"
            
        filepath = os.path.join(self.save_dir, filename)
        
        try:
            doc = ezdxf.new('R2010')
            msp = doc.modelspace()
            
            if self.current_type == "QR":
                rows = len(self.current_matrix)
                cols = len(self.current_matrix[0])
                
                # DXF Y-axis goes upwards, so we invert Y
                for y in range(rows):
                    for x in range(cols):
                        if self.current_matrix[y][x]: # If black module
                            draw_y = rows - y
                            # Add SOLID (2D filled polygon) for the block
                            # SOLID points need to be in a specific order: p1, p2, p4, p3 (ezdxf handles list order)
                            p1 = (x, draw_y)
                            p2 = (x+1, draw_y)
                            p3 = (x+1, draw_y-1)
                            p4 = (x, draw_y-1)
                            msp.add_solid([p1, p2, p3, p4])
                            
            elif self.current_type == "BARCODE":
                # Barcode matrix is a list of strings (e.g., ['1010011...', '1010011...'])
                # We usually just need the first row, as barcode is 1D
                row_data = self.current_matrix[0]
                height = 40 # Default barcode height
                x = 0
                
                for char in row_data:
                    if char == '1': # If black bar
                        p1 = (x, height)
                        p2 = (x+1, height)
                        p3 = (x+1, 0)
                        p4 = (x, 0)
                        msp.add_solid([p1, p2, p3, p4])
                    x += 1
            
            doc.saveas(filepath)
            QMessageBox.information(self, "Success", f"DXF Successfully save ho gaya hai:\n{filepath}\n\nFile ka size KBs me hoga.")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"DXF save karne me error aaya:\n{str(e)}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = QRBarcodeWidget()
    window.show()
    sys.exit(app.exec_())
