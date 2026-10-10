import os
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QLabel, 
                               QPushButton, QFileDialog, QMessageBox, QFrame)
from core.calibration import GalvoCalibration
from core.calibration_generator_ui import CalibrationGeneratorDialog

class CalibrationDialog(QDialog):
    def __init__(self, galvo_calibration: GalvoCalibration, parent=None, galvo_controller=None):
        super().__init__(parent)
        self.setWindowTitle("Galvo Binary Calibration (.cor)")
        self.setMinimumWidth(400)
        self.calibration = galvo_calibration
        self.galvo_controller = galvo_controller
        
        self.layout = QVBoxLayout(self)
        
        self.info_label = QLabel("JCZ EZCAD .cor File Calibration")
        font = self.info_label.font()
        font.setBold(True)
        self.info_label.setFont(font)
        self.layout.addWidget(self.info_label)
        
        self.status_label = QLabel()
        self.layout.addWidget(self.status_label)
        
        self.path_label = QLabel()
        self.path_label.setWordWrap(True)
        self.layout.addWidget(self.path_label)
        
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        self.layout.addWidget(line)
        
        self.btn_load = QPushButton("Load Binary .cor File")
        self.btn_load.clicked.connect(self.load_file)
        self.layout.addWidget(self.btn_load)
        
        self.btn_create = QPushButton("Create New .cor File")
        self.btn_create.clicked.connect(self.create_new_cor)
        self.layout.addWidget(self.btn_create)
        
        self.update_ui()
        
    def create_new_cor(self):
        dlg = CalibrationGeneratorDialog(self.galvo_controller, self)
        dlg.exec()
        
    def update_ui(self):
        if self.calibration.is_valid:
            self.status_label.setText("Status: ✅ Active (65x65 Grid Loaded)")
            self.status_label.setStyleSheet("color: green;")
        else:
            self.status_label.setText("Status: ❌ No valid .cor file loaded")
            self.status_label.setStyleSheet("color: red;")
            
        self.path_label.setText(f"File: {self.calibration.config_path}")

    def load_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Calibration File", "", "EZCAD Cor Files (*.cor);;All Files (*)")
        if file_path:
            self.calibration.load_calibration(file_path)
            self.update_ui()
            if self.calibration.is_valid:
                QMessageBox.information(self, "Success", "Binary .cor file loaded successfully!\nThe 65x65 correction map is now active.")
            else:
                QMessageBox.warning(self, "Error", "Failed to load the selected file. Ensure it is a valid EZCAD .cor file.")
