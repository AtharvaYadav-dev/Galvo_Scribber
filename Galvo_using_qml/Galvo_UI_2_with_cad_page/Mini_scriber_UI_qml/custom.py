
from PySide6.QtWidgets import QButtonGroup, QMessageBox

class CustomMessageBox(QMessageBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        # Set default properties
        self.setWindowTitle("Message")
        self.setStyleSheet("background-color: rgb(167, 198, 229);color: rgb(16, 42, 83);")
        self.setStandardButtons(QMessageBox.Ok)
        self.setDefaultButton(QMessageBox.Ok)
        
    def info(self, title, message):
        self.setWindowTitle(title)
        self.setText(message)
        self.setIcon(QMessageBox.Information)
        self.setStandardButtons(QMessageBox.Ok)
        return self.exec()
        
    def warning(self, title, message):
        self.setWindowTitle(title)
        self.setText(message)
        self.setIcon(QMessageBox.Warning)
        self.setStandardButtons(QMessageBox.Ok)
        return self.exec()
        
    def error(self, title, message):
        self.setWindowTitle(title)
        self.setText(message)
        self.setIcon(QMessageBox.Critical)
        self.setStandardButtons(QMessageBox.Ok)
        return self.exec()
        
    def question(self, title, message):
        self.setWindowTitle(title)
        self.setText(message)
        self.setIcon(QMessageBox.Question)
        self.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        self.setDefaultButton(QMessageBox.Yes)
        return self.exec()
        
    def confirmation(self, title, message):
        self.setWindowTitle(title)
        self.setText(message)
        self.setIcon(QMessageBox.Question)
        self.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        self.setDefaultButton(QMessageBox.Ok)
        return self.exec()
    
    def getButton(self, btnName):
        btn_name_dict = {"Ok" : QMessageBox.Ok,
                         "Yes" : QMessageBox.Yes,
                         "No" : QMessageBox.No,
                         "Cancel" : QMessageBox.Cancel}
        
        btn = btn_name_dict.get(btnName)
        return btn


class CustomRadioGroup(QButtonGroup):
    def __init__(self, parent=None):
        super(CustomRadioGroup, self).__init__(parent)
        self.setExclusive(False)