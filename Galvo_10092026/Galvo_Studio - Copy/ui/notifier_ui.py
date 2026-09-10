from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QLabel, QTextEdit, QMessageBox
from PySide6.QtCore import Qt, QEventLoop, QTimer

class NotifierUI:
    @staticmethod
    def setup(main_window):
        # Increase size limits to accommodate buttons
        if hasattr(main_window, 'notify_menu_widgets') and main_window.notify_menu_widgets.notify:
            main_window.notify_menu_widgets.notify.setMaximumHeight(180)
        
        # Manually find sub-container because it wasn't mapped in setupNotifyMenu
        notifySubContainer = main_window.findChild(QWidget, "notifySubContainer")
        
        if notifySubContainer:
            notifySubContainer.setMaximumHeight(180)
            notifySubContainer.layout().setContentsMargins(0, 0, 0, 0)
            notifySubContainer.setStyleSheet("""
                QWidget#notifySubContainer {
                    background-color: rgb(167, 198, 229);
                    color: rgb(16, 42, 83);
                    border-radius: 15px;
                    border: 2px solid rgb(16, 42, 131);
                }
            """)

        notifyLabel = main_window.findChild(QLabel, "notifyLabel")
        if notifyLabel:
            main_window.notifyLabel = notifyLabel
            notifyLabel.setMinimumHeight(35)
            notifyLabel.setStyleSheet("""
                QLabel {
                    background-color: rgb(16, 42, 131);
                    color: white;
                    font-weight: bold;
                    font-size: 14px;
                    padding-left: 15px;
                    border-top-left-radius: 13px;
                    border-top-right-radius: 13px;
                    border-bottom-left-radius: 0px;
                    border-bottom-right-radius: 0px;
                }
            """)

        notifyTextEdit = main_window.findChild(QTextEdit, "notifyTextEdit")
        if notifyTextEdit:
            main_window.notifyTextEdit = notifyTextEdit
            notifyTextEdit.setReadOnly(True)
            notifyTextEdit.setStyleSheet("""
                QTextEdit {
                    background-color: transparent;
                    color: rgb(16, 42, 83);
                    border: none;
                    font-size: 13px;
                    padding: 10px 15px;
                }
            """)

        # Style the close button
        closeNotifyBtn = main_window.findChild(QPushButton, "closeNotifyPushButton")
        if closeNotifyBtn:
            closeNotifyBtn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    border: none;
                    padding: 5px;
                    margin-right: 5px;
                }
                QPushButton:hover {
                    background-color: rgba(16, 42, 131, 50);
                    border-radius: 15px;
                }
            """)
            closeNotifyBtn.clicked.connect(lambda: main_window.onPopupBtnClicked(QMessageBox.Cancel))

        if notifySubContainer:
            # Container for buttons.
            main_window.notifyBtnContainer = QWidget(notifySubContainer)
            main_window.notifyBtnContainer.setStyleSheet("background-color: transparent;")
            main_window.notifyBtnLayout = QHBoxLayout(main_window.notifyBtnContainer)
            main_window.notifyBtnLayout.setContentsMargins(0, 0, 0, 5)
            main_window.notifyBtnLayout.setSpacing(10)
            main_window.notifyBtnLayout.setAlignment(Qt.AlignCenter)
            
            notifySubContainer.layout().addWidget(main_window.notifyBtnContainer)
            
            main_window.btnOk = QPushButton("OK")
            main_window.btnYes = QPushButton("Yes")
            main_window.btnNo = QPushButton("No")
            main_window.btnCancel = QPushButton("Cancel")
            
            btn_style = """
                QPushButton {
                    background-color: rgb(16, 42, 131);
                    color: white;
                    border: 1px solid rgb(16, 42, 131);
                    border-radius: 8px;
                    padding: 6px 20px;
                    font-weight: bold;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background-color: rgb(40, 70, 160);
                    color: white;
                }
                QPushButton:pressed {
                    background-color: rgb(10, 30, 100);
                }
            """
            
            for btn in [main_window.btnOk, main_window.btnYes, main_window.btnNo, main_window.btnCancel]:
                btn.setStyleSheet(btn_style)
                btn.hide()
                main_window.notifyBtnLayout.addWidget(btn)
                
            main_window.btnOk.clicked.connect(lambda: main_window.onPopupBtnClicked(QMessageBox.Ok))
            main_window.btnYes.clicked.connect(lambda: main_window.onPopupBtnClicked(QMessageBox.Yes))
            main_window.btnNo.clicked.connect(lambda: main_window.onPopupBtnClicked(QMessageBox.No))
            main_window.btnCancel.clicked.connect(lambda: main_window.onPopupBtnClicked(QMessageBox.Cancel))

        # --- Notification System Setup ---
        main_window.popupLoop = QEventLoop(main_window)
        main_window.popupResult = QMessageBox.Ok

    @staticmethod
    def onPopupBtnClicked(main_window, result):
        main_window.popupResult = result
        if main_window.popupLoop.isRunning():
            main_window.popupLoop.quit()
        main_window.notify_menu_widgets.notify.collapseMenu()
        
    @staticmethod
    def showCustomPopup(main_window, title, message, buttons=QMessageBox.Ok):
        """Show notification in the slide-in panel and block until user responds."""
        if hasattr(main_window, "notifyLabel"):
            main_window.notifyLabel.setText(title)
        if hasattr(main_window, "notifyTextEdit"):
            main_window.notifyTextEdit.setText(message)

        # Reset all buttons
        main_window.btnOk.hide()
        main_window.btnYes.hide()
        main_window.btnNo.hide()
        main_window.btnCancel.hide()

        if buttons & QMessageBox.Ok:     main_window.btnOk.show()
        if buttons & QMessageBox.Yes:    main_window.btnYes.show()
        if buttons & QMessageBox.No:     main_window.btnNo.show()
        if buttons & QMessageBox.Cancel: main_window.btnCancel.show()

        main_window.notify_menu_widgets.notify.expandMenu()
        main_window.popupLoop.exec()
        return main_window.popupResult

    @staticmethod
    def showAutoCloseMessage(main_window, title, message, timeout_ms=5000):
        """Show notification that auto-collapses after timeout_ms ms."""
        if hasattr(main_window, "notifyLabel"):
            main_window.notifyLabel.setText(title)
        if hasattr(main_window, "notifyTextEdit"):
            main_window.notifyTextEdit.setText(message)

        main_window.btnOk.hide()
        main_window.btnYes.hide()
        main_window.btnNo.hide()
        main_window.btnCancel.hide()

        main_window.notify_menu_widgets.notify.expandMenu()
        
        # Keep a persistent reference to the timer to prevent garbage collection
        if hasattr(main_window, '_auto_close_timer'):
            main_window._auto_close_timer.stop()
            main_window._auto_close_timer.deleteLater()
            
        main_window._auto_close_timer = QTimer(main_window)
        main_window._auto_close_timer.setSingleShot(True)
        main_window._auto_close_timer.timeout.connect(main_window.notify_menu_widgets.notify.collapseMenu)
        main_window._auto_close_timer.start(timeout_ms)
