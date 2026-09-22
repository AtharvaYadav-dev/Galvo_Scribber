import os
import sys
import re


from ui_interface import *
from Custom_Widgets.Widgets import *
from PySide6.QtCore import QTimer, QRegularExpression, Signal, Slot, Qt, QThread, QEvent, QEventLoop, QSize
from PySide6.QtGui import QIcon, QCloseEvent, QIntValidator, QDoubleValidator, QRegularExpressionValidator
from PySide6.QtWidgets import QFileDialog
from PySide6.QtWidgets import QMessageBox

from com import SerialCom, SerialConfigError
from util import CallbackHandler, FileHandler, ConfigHandler, AppLogger, Utils, CyclicBuffer
from gcode import GcodeHandler
from custom import CustomMessageBox
from dxf import DXFParser
from preview3d import GCode3DPreview
from uihandler import AxisHandler, LaserHandler, WidgetHandler, WidgetManger, KeyFilter, DictAsClass, EventHandler

from preview_galvo import GalvoPreviewWidget
from galvo_threads import ExecutionThread, PreviewThread
from core.motion_planner import MotionPlanner
from core.coordinate_mapper import CoordinateConfig
from machine.galvo_controller import GalvoController
from machine.stepper_controller import StepperController
from core.svg_parser import SVGParser
from core.text_parser import TextParser

from pygrabber.dshow_graph import FilterGraph
from camera_thread import CameraThread
from PySide6.QtGui import QPixmap, QImage

from notifier_ui import NotifierUI


class MainWindow(QMainWindow):
    sigPrintProgress = Signal(float)
    exceptionOccurred = Signal(str)
    sigUpdateData = Signal(str)
    
    def __init__(self, parent=None):
        # basic UI working starts here
        QMainWindow.__init__(self)
        self.ui = Ui_MainWindow()       # calls the mainwindow from compiled ui file 
        self.ui.setupUi(self)           # setup the ui mainwindow class
        loadJsonStyle(self, self.ui)    # loads the style from style.json required if using QT-PyQt-PySide-Custom-Widgets
        
        # Allow multiple hatch types to be selected simultaneously
        self.ui.pgmhatch1_RadioButton.setAutoExclusive(False)
        self.ui.pgmhatch2_RadioButton.setAutoExclusive(False)
        self.ui.pgmhatch3_RadioButton.setAutoExclusive(False)
        
        # basic UI working ends here
        
        
        # create instance of other python class or modules starts here
        self.maincom = SerialCom()
        self.ah = AxisHandler()
        self.fh = FileHandler()
        self.ch = ConfigHandler()
        self.cb = CallbackHandler()
        self.eh = EventHandler()
        self.gh = GcodeHandler()
        self.wh = WidgetHandler()
        self.util = Utils()
        self.msgbox = CustomMessageBox(self)
        self.logger = AppLogger(logger_name="UILogger", log_file="app.log", log_level="DEBUG")
        self.wm = WidgetManger()

        # Galvo Core components
        self.planner = MotionPlanner()
        self.text_parser = TextParser()
        self.galvo_config = CoordinateConfig()
        self.galvo_controller = GalvoController()
        self.galvo_controller.connect()
        self.galvo_controller.galvo_home()
        self.stepper_controller = StepperController(self.galvo_controller.connection)
        self.galvo_preview_thread = None
        self.galvo_has_disconnected = False
        if not self.galvo_controller.is_connected:
            self.ui.titleLabel.setText("Patterning Machine (Demo Mode)")


        self.util.debugFlag = True
        
        self.temp_report_hide_flag = False 
        self.com_errorFlag = False
        # self.exceptionOccurred.connect(self.showExceptionPopup)
        
        self.lh = LaserHandler()
        
        # variables
        self.jogfeed = 1000
        self.xcenter = 75
        self.ycenter = 75
        self.zcenter = 50
        self.travel = 10
        self.jogcmd = None
        
        self.pgm_file = None
        self.pgm_height = None
        self.pgm_laser = None
        self.pgm_glist = []
        self.pgm_mlist = []
        self.pgm_index = 0
        self.seg_index = 0
        self.mark_flag = False
        self.gcode_ack = None
        self.pause_flag = False
        self.pgm_run_flag = False
        self.pgm_pause_flag = False
        self.pgm_abort_flag = False
        self.progress = 0
        self.prev_segment = 0
        self.laser_name = None
        self.zero_laser = None
        self.offset_laser = None
        self.offset_laser_name = None
        self.focus = 0
        self.xindex = 0
        self.yindex = 0
        self.offset = 0
        self.zero_flag = False
        self.xtemp = 0
        self.ytemp = 0
        self.travel_index = 0
        self.cam_offset_travel = 10.0
        self.Z_MAX_LIMIT = 28.0
        self.is_inspection_running = False
        self.cam_thread = None
        self.master_glist = []

        self.notification_timer = QTimer(self)
        self.notification_timer.setSingleShot(True)
        self.notification_timer.timeout.connect(lambda: self.notify_menu_widgets.notify.collapseMenu())

        self.preview = GCode3DPreview()
        self.preview.sigGlError.connect(lambda msg: print("⚠️", msg))
        # Match the actual machine bed: 300x300mm, 50mm Z travel
        self.preview.setBedSize(300, 300, 50)

        
        # create instance of other python class or modules ends here
        # initialization of ini file        
        self.initConfig()
        
        # initialization of serial communication
        self.initSerial()
        
        # widget setup calls starts here
        self.setupCom()
        self.setupLeftMenu()
        self.setupCenterMenu()
        self.setupNotifyMenu()
        self.setupProfile()
        self.setupMainPages()
        self.setupInfoPages()
        self.setupSettings()
        self.setupJog()
        self.setupFocus()
        self.setupOffset()
        self.setupProgram()
        self.setupPrint()
        self.setupCamera()
        self.setupTerminal()
        self.setupJogGalvo()
        self.setupLaserConfGalvo()
        self.setupProgramsGalvo()
        self.setupPrintGalvo()
        self.setupConfigGalvo()
        self.setupAdvancedCalibration()
        self.setupHeader()
        
        # widget setup calls ends here
        
        # widget init calls starts here
        
        self.initCom()
        self.initLeftMenu()
        self.initCenterMenu()
        self.initNotifyMenu()
        self.initProfile()
        self.initMainPages()
        self.initInfoPages()
        self.initLaser()
        self.initSettings()
        self.initJog()
        self.initFocus()
        self.initOffset()
        self.initProgram()
        self.initPrint()
        self.initCamera()
        self.initTerminal()
        self.initJogGalvo()
        self.initLaserConfGalvo()
        self.initProgramsGalvo()
        self.initPrintGalvo()
        self.initConfigGalvo()
        
        # widget init calls starts here
        
        # callbacks used in the UI initialization starts here
        self.gh.attachCallback(self.cb)
        self.cb.register(self.gh.gcode_dict.get("home"), self.goHome)
        self.cb.register(self.gh.gcode_dict.get("get-pos"), self.updateAxisPos)
        self.cb.register(self.gh.gcode_dict.get("finish-move"), self.moveFinish)
        
        # callbacks used in the UI initialization ends here            
        self.sigPrintProgress.connect(self._updatePrintProgress)
        
        # UI init starts here
        if hasattr(self.ui, 'xposgalvoLCDNumber'):
            self.ui.xposgalvoLCDNumber.setDigitCount(6)
        if hasattr(self.ui, 'yposgalvoLCDNumber'):
            self.ui.yposgalvoLCDNumber.setDigitCount(6)
        if hasattr(self.ui, 'zposgalvoLCDNumber'):
            self.ui.zposgalvoLCDNumber.setDigitCount(6)
        if hasattr(self.ui, 'focusgalvoLCDNumber'):
            self.ui.focusgalvoLCDNumber.setDigitCount(6)
            
        if hasattr(self.ui, 'xposLCDNumber'):
            self.ui.xposLCDNumber.setDigitCount(6)
        if hasattr(self.ui, 'yposLCDNumber'):
            self.ui.yposLCDNumber.setDigitCount(6)
        if hasattr(self.ui, 'zposLCDNumber'):
            self.ui.zposLCDNumber.setDigitCount(6)
        if hasattr(self.ui, 'focusLCDNumber'):
            self.ui.focusLCDNumber.setDigitCount(6)
            
        # schedule UI loaded notification
        QTimer.singleShot(200, self.onLoad)
        self.logger.info("UI load successful")
        
        self.applyGalvoMode()
        if str(self.galvo_mode).upper() == "ON":
            self.showMainPages("joggalvo")
            QTimer.singleShot(1000, self.checkGalvoConnection)
        else:
            self.showMainPages("jog")
        
        self.setup_di_polling()
        
        # UI init ends here
        
    def initConfig(self, config_dir="config", config_file="config.ini"):
        self.config_dir_path = self.fh.getPath(dir=config_dir)
        self.config_file_path = self.fh.getPath(dir=self.config_dir_path, file=config_file)

        self.fh.checkDir(self.config_dir_path)
        self.ch.ini_parser.read(self.config_file_path)
        
        self.galvo_mode = self.ch.getValues("machine", "galvo")
        if not self.galvo_mode:
            self.galvo_mode = "OFF"

    def checkGalvoConnection(self):
        if self.galvo_controller.is_connected:
            self.showAutoCloseMessage("Hardware Connected", "Connected with machine, card is active.", timeout_ms=5000)
        else:
            self.showAutoCloseMessage("Hardware Disconnected", "Connect the card and try to connect again.", timeout_ms=5000)

    def setup_di_polling(self):
        self.di1_last_state = 0
        self.di2_last_state = 0
        self.di_timer = QTimer(self)
        self.di_timer.setInterval(100)
        self.di_timer.timeout.connect(self.poll_di_inputs)
        self.di_timer.start()

    def poll_di_inputs(self):
        if not hasattr(self, 'galvo_controller') or not self.galvo_controller.is_connected:
            return
            
        try:
            di1_state = self.galvo_controller.get_di_bit(11)
            di2_state = self.galvo_controller.get_di_bit(12)
            
            # Rising edge DI1 (Start)
            if di1_state == 1 and self.di1_last_state == 0:
                self.logger.info("DI1 (Pin 11) Triggered - Starting Print")
                if str(self.galvo_mode).upper() == "ON":
                    # Check if on print page and design is loaded
                    if self.main_stack.currentIndex() == self.main_page_dict.get("printgalvo"):
                        if getattr(self, 'pgm_file', None) or getattr(self, 'current_test_shape', None):
                            if hasattr(self.ui, 'printrungalvoPushButton') and self.ui.printrungalvoPushButton.isEnabled():
                                self.printGalvoAction(self.printgalvo_widgets.printrungalvo)
                else:
                    if self.main_stack.currentIndex() == self.main_page_dict.get("print"):
                        if getattr(self, 'pgm_file', None):
                            if hasattr(self.ui, 'printrunPushButton') and self.ui.printrunPushButton.isEnabled():
                                self.printAction(self.print_widgets.printrun)
                        
            # Rising edge DI2 (Abort)
            if di2_state == 1 and self.di2_last_state == 0:
                self.logger.info("DI2 (Pin 12) Triggered - Aborting Print")
                if str(self.galvo_mode).upper() == "ON":
                    if hasattr(self.ui, 'printabortgalvoPushButton') and self.ui.printabortgalvoPushButton.isEnabled():
                        self.printGalvoAction(self.printgalvo_widgets.printabortgalvo)
                else:
                    if hasattr(self.ui, 'printabortPushButton') and self.ui.printabortPushButton.isEnabled():
                        self.printAction(self.print_widgets.printabort)
                        
            self.di1_last_state = di1_state
            self.di2_last_state = di2_state
        except Exception as e:
            self.logger.error(f"Error polling DI inputs: {e}")

    def applyGalvoMode(self):
        is_on = (str(self.galvo_mode).upper() == "ON")
        
        self.wh.invokeMethod(self.left_menu_widgets.home, "hide" if is_on else "show")
        self.wh.invokeMethod(self.left_menu_widgets.programs, "hide" if is_on else "show")
        self.wh.invokeMethod(self.left_menu_widgets.print, "hide" if is_on else "show")
        self.wh.invokeMethod(self.left_menu_widgets.camera, "hide" if is_on else "show")
        self.wh.invokeMethod(self.left_menu_widgets.camerajog, "hide" if is_on else "show")
        
        self.wh.invokeMethod(self.left_menu_widgets.joggalvo, "show" if is_on else "hide")
        self.wh.invokeMethod(self.left_menu_widgets.programsgalvo, "show" if is_on else "hide")
        self.wh.invokeMethod(self.left_menu_widgets.printgalvo, "show" if is_on else "hide")
        
        if is_on:
            self.wh.invokeMethod(self.left_menu_widgets.laser, "hide")
        else:
            self.wh.invokeMethod(self.left_menu_widgets.laserconfgalvo, "hide")
            
        self.ui.indexFrame.setVisible(not is_on)
        self.ui.machinesetFrame.setVisible(not is_on)
        self.ui.setconfigPushButton.setVisible(is_on)
        
        self.ui.portFrame.setVisible(not is_on)
        self.ui.baudFrame.setVisible(not is_on)
        self.ui.mainconnectPushButton.setVisible(not is_on)
        self.ui.mainrefreshPushButton.setVisible(not is_on)
        
        self.ui.mainconnectgalvoPushButton.setVisible(is_on)
        self.ui.maindisconnectgalvoPushButton.setVisible(is_on)
        
        if is_on:
            if self.galvo_controller.is_connected and not self.galvo_has_disconnected:
                self.ui.mainconnectgalvoPushButton.setEnabled(False)
                self.ui.maindisconnectgalvoPushButton.setEnabled(True)
            else:
                self.ui.mainconnectgalvoPushButton.setEnabled(True)
                self.ui.maindisconnectgalvoPushButton.setEnabled(False)
        
    def initSerial(self):
        self.sercom_dict = {}
        self.serial_error_dict = {
                                  SerialConfigError.PORT_AND_BAUD_INVALID : ("Invalid Input", "Kindly select both COM port and baud rate."),
                                  SerialConfigError.PORT_INVALID : ("Invalid Input", "Kindly select a COM port."),
                                  SerialConfigError.BAUD_INVALID: ("Invalid Input", "Kindly select a baud rate.")
                                  }
        
        self.serial_connect_state = "Connect"
        self.serial_disconnect_state = "Disconnect"
                        
    def configSerial(self, obj_name, widgets, response_callback=None, exception_callback=None):
        obj = getattr(self, obj_name)
        print(f"ser obj : {obj} | name : {obj_name}")
        ch = obj_name.replace("com", "")
        
        port = getattr(widgets, f"{ch}port")
        baud = getattr(widgets, f"{ch}baud")
        connect_btn = getattr(widgets, f"{ch}connect")
        refresh_btn = getattr(widgets, f"{ch}refresh")
        
        self.sercom_dict[obj_name] = {}
        self.sercom_dict[obj_name]["obj"] = obj
        self.sercom_dict[obj_name]["ch"] = ch
        self.sercom_dict[obj_name]["port"] = port
        self.sercom_dict[obj_name]["baud"] = baud
        self.sercom_dict[obj_name]["connect"] = connect_btn
        self.sercom_dict[obj_name]["refresh"] = refresh_btn
        
        self.util.debugPrint(f"sercom_dict : {self.sercom_dict}")
                        
        # initialize callbacks used in the UI
        obj.configCallbacks(responseCallback = response_callback, exceptionCallback = exception_callback)
        
    def beginSerial(self, obj_name, refresh=False):
        if obj_name in self.sercom_dict:
            obj_dict = self.sercom_dict.get(obj_name)
            
            obj = obj_dict.get("obj")
            port_widget = obj_dict.get("port")
            baud_widget = obj_dict.get("baud")
            
            port_list = obj.getPorts()
            baud_list = obj.getBaudrates()

            ch = obj_name.replace("com", "")
            msg = f"Com : {obj_name.replace(ch, '')}, Port : {port_list}, Baud : {baud_list}"
            self.util.debugPrint(msg)
            self.logger.info(msg)

            # Filter out ports already used by other active connections
            used_ports = []
            for name, data in self.sercom_dict.items():
                if name != obj_name:
                    other_obj = data.get("obj")
                    if other_obj and other_obj.is_connected and other_obj.port:
                        used_ports.append(other_obj.port)
            
            port_list = [p for p in port_list if p not in used_ports]
            
            self.wh.invokeMethod(port_widget, "clear")
            self.wh.invokeMethod(baud_widget, "clear")

            self.wh.invokeMethod(port_widget, "add", port_list)
            self.wh.invokeMethod(baud_widget, "add", baud_list)

            if refresh:
                port_widget.setPlaceholderText("Select Port")
                baud_widget.setPlaceholderText("Select Baud")
                port_widget.setCurrentIndex(-1)
                baud_widget.setCurrentIndex(-1)
            
    def validateSerial(self, obj, port, baud):
        error_code = obj.validateConfig(port, baud)
        
        if error_code == SerialConfigError.NONE:
            return True
        
        else:
            error_title, error_text = self.serial_error_dict.get(error_code)
            msg = f"Error : {error_title} > {error_text}"
            self.util.debugPrint(msg)
            self.logger.error(msg)
            self.showAutoCloseMessage(error_title, error_text)
            
            return False
            
    def activateSerial(self, obj_name, action):
        if obj_name in self.sercom_dict:
            obj_dict = self.sercom_dict.get(obj_name)
            
            obj = obj_dict.get("obj")
            ch = obj_name.replace("com", "")
            port_widget = obj_dict.get("port")
            baud_widget = obj_dict.get("baud")
            connect_btn = obj_dict.get("connect")
            refresh_btn = obj_dict.get("refresh")
            
            mode = action.replace(ch, "")
            print(f"action : {mode.capitalize()}")
            
            if mode in ["auto", "connect"]:
                port = self.wh.invokeMethod(port_widget, "get") if mode == "connect" else self.ch.getValues(ch, "port")
                baud = self.wh.invokeMethod(baud_widget, "get") if mode == "connect" else self.ch.getValues(ch, "baudrate")

                validate = self.validateSerial(obj, port, baud)
                print(f"status : {validate}")
                
                if mode == "auto":
                    # Map simplified names to display names
                    display_names = {
                        "main": "Main Controller"
                    }
                    display_name = display_names.get(ch, f"{ch.upper()} Controller")

                    msg_dict = {}
                    msg_dict[True] = ("COM Port Connection",f"Do you want to auto connect to {port} @ {baud}")
                    msg_dict[False] = ("COM Port Auto-Connection failed","Kindly peform manual COM port configuration!!!")
                
                    msg_title, msg_text = msg_dict.get(validate)

                    if validate:
                        retval = self.showCustomPopup(msg_title, msg_text, buttons=QMessageBox.Ok | QMessageBox.Cancel)
                        self.logger.info(msg_text)

                        if retval == QMessageBox.Ok:
                            self.util.debugPrint('OK clicked')
                            msg = "Serial COM : Auto"
                            self.util.debugPrint(msg)
                            self.logger.info("Auto Connect dialog button : Ok")
                            self.logger.info(msg)
                            
                            # Update UI to show what we are connecting to
                            self.wh.invokeMethod(port_widget, "set", port)
                            self.wh.invokeMethod(baud_widget, "set", baud)

                        if retval == QMessageBox.Cancel:
                            self.util.debugPrint('Cancel clicked')
                            self.logger.info("Auto Connect dialog button : Cancel")
                            self.wh.invokeMethod(port_widget, "clear")
                            self.wh.invokeMethod(baud_widget, "clear")
                            return
                
                if mode == "connect":
                    state = self.wh.invokeMethod(connect_btn, "get")
                    
                    if state == self.serial_connect_state:
                        
                        if validate:
                            self.ch.addParameter(ch, "port", port)
                            self.ch.addParameter(ch, "baudrate", baud)
                            self.ch.updateFile(self.config_file_path)
                            
                            msg = "Serial COM : Manual"
                            self.util.debugPrint(msg)
                    
                    if state == self.serial_disconnect_state:
                        mode = "disconnect"
                        
                if mode in ["auto", "connect"] and validate:
                    obj.port = port
                    obj.baudrate = baud
                    obj.connect()

                    self.wh.invokeMethod(connect_btn, "set", self.serial_disconnect_state)
                    self.wh.invokeMethod(refresh_btn, "disable")
                
            if mode == "refresh":
                self.beginSerial(obj_name, refresh=True)
                
            if mode == "disconnect":
                obj.disconnect()
                self.wh.invokeMethod(connect_btn, "set", self.serial_connect_state)
                self.wh.invokeMethod(refresh_btn, "enable")
                
    def sendSerial(self, obj_name, data):
        if obj_name in self.sercom_dict:
            obj_dict = self.sercom_dict.get(obj_name)
            
            obj = obj_dict.get("obj")
            obj.send(data)                
        
    def setupCom(self):        
        com_widget_list = []
        com_widget_list.append(self.wh.configWidget(self, QComboBox, "mainportComboBox", role="mainport"))
        com_widget_list.append(self.wh.configWidget(self, QComboBox, "mainbaudComboBox", role="mainbaud"))
        com_widget_list.append(self.wh.configWidget(self, QPushButton, "mainconnectPushButton", "clicked", self.comAction, role="mainconnect"))
        com_widget_list.append(self.wh.configWidget(self, QPushButton, "mainrefreshPushButton", "clicked", self.comAction, role="mainrefresh"))
        com_widget_list.append(self.wh.configWidget(self, QPushButton, "mainconnectgalvoPushButton", "clicked", self.comAction, role="mainconnectgalvo"))
        com_widget_list.append(self.wh.configWidget(self, QPushButton, "maindisconnectgalvoPushButton", "clicked", self.comAction, role="maindisconnectgalvo"))
        
        self.util.dedupeList(com_widget_list)
        self.com_widgets = self.wh.createMap(*com_widget_list)
    
    def setupLeftMenu(self):
        left_menu_widget_list = []
        left_menu_widget_list.append(self.wh.configWidget(self, QPushButton, "homePushButton", role="home", toolTip="Jog"))
        left_menu_widget_list.append(self.wh.configWidget(self, QPushButton, "laserPushButton", role="laser", toolTip="Laser"))
        left_menu_widget_list.append(self.wh.configWidget(self, QPushButton, "programsPushButton", role="programs", toolTip="Program"))
        left_menu_widget_list.append(self.wh.configWidget(self, QPushButton, "printPushButton", role="print", toolTip="Print"))
        left_menu_widget_list.append(self.wh.configWidget(self, QPushButton, "cameraPushButton", role="camera", toolTip="Camera"))
        left_menu_widget_list.append(self.wh.configWidget(self, QPushButton, "cameraonoffoffsetPushButton", "clicked", self.leftMenuAction, role="camerajog", toolTip="Camera Jog"))
        left_menu_widget_list.append(self.wh.configWidget(self, QPushButton, "terminalPushButton", role="terminal", toolTip="Terminal"))
        
        left_menu_widget_list.append(self.wh.configWidget(self, QPushButton, "joggalvoPushButton", role="joggalvo", toolTip="Jog Galvo"))
        left_menu_widget_list.append(self.wh.configWidget(self, QPushButton, "laserconfgalvoPushButton", role="laserconfgalvo", toolTip="Laser Galvo"))
        left_menu_widget_list.append(self.wh.configWidget(self, QPushButton, "programsgalvoPushButton", role="programsgalvo", toolTip="Program Galvo"))
        left_menu_widget_list.append(self.wh.configWidget(self, QPushButton, "printgalvoPushButton", role="printgalvo", toolTip="Print Galvo"))

        
        self.util.dedupeList(left_menu_widget_list)
        self.left_menu_widgets = self.wh.createMap(*left_menu_widget_list)
    
    def setupCenterMenu(self):
        center_menu_widget_list = []
        center_menu_widget_list.append(self.wh.configWidget(self, QCustomSlideMenu, "centerSlideMenu", role="center"))
        center_menu_widget_list.append(self.wh.configWidget(self, QPushButton, "comPushButton", "clicked", self.centerMenuAction, role="com", toolTip="Com"))
        center_menu_widget_list.append(self.wh.configWidget(self, QPushButton, "settingsPushButton", "clicked", self.centerMenuAction, role="settings", toolTip="Setting"))
        center_menu_widget_list.append(self.wh.configWidget(self, QPushButton, "infoPushButton", "clicked", self.centerMenuAction, role="info", toolTip="Info"))
        center_menu_widget_list.append(self.wh.configWidget(self, QPushButton, "closeCenterMenuPushButton", "clicked", self.centerMenuAction, role="closeCenterMenu"))
        center_menu_widget_list.append(self.wh.configWidget(self, QPushButton, "profilePushButton", "clicked", self.centerMenuAction, role="profile", toolTip="Profile"))

        self.util.dedupeList(center_menu_widget_list)
        self.center_menu_widgets = self.wh.createMap(*center_menu_widget_list)
        print(f"center menu : {self.center_menu_widgets}")
    
    def setupNotifyMenu(self):
        notify_menu_widget_list = []
        notify_menu_widget_list.append(self.wh.configWidget(self, QCustomSlideMenu, "notifySlideMenu", role="notify"))
        notify_menu_widget_list.append(self.wh.configWidget(self, QPushButton, "closeNotifyPushButton", "clicked", self.notifyMenuAction, role="closeNotify"))
    
        self.util.dedupeList(notify_menu_widget_list)
        self.notify_menu_widgets = self.wh.createMap(*notify_menu_widget_list)
    
    def setupProfile(self):
        profile_widget_list = []
        profile_widget_list.append(self.wh.configWidget(self, QComboBox, "userComboBox", role="user"))
        profile_widget_list.append(self.wh.configWidget(self, QLineEdit, "passwordLineEdit", role="password"))
        profile_widget_list.append(self.wh.configWidget(self, QPushButton, "profilesetPushButton", "clicked", self.profileAction, role="profileset"))

        self.util.dedupeList(profile_widget_list)
        self.profile_widgets = self.wh.createMap(*profile_widget_list)
    
    def setupMainPages(self):
        self.main_stack = self.findChild(QCustomStackedWidget, "mainPages")
    
    def setupInfoPages(self):
        self.info_stack = self.findChild(QStackedWidget, "infoSubPages")
        
    def setupSettings(self):
        settings_widget_list = []
        settings_widget_list.append(self.wh.configWidget(self, QLineEdit, "indexLineEdit", "returnPressed", self.settingAction, role="index"))
        # settings_widget_list.append(self.wh.configWidget(self, QLineEdit, "feedLineEdit", "returnPressed", self.settingAction, role="feed"))
        settings_widget_list.append(self.wh.configWidget(self, QPushButton, "cameraoffsetPushButton", "clicked", self.settingAction, role="cameraoffset"))
        settings_widget_list.append(self.wh.configWidget(self, QPushButton, "setconfigPushButton", "clicked", self.settingAction, role="setconfig"))
        settings_widget_list.append(self.wh.configWidget(self, QPushButton, "setadvancalPushButton", "clicked", self.settingAction, role="setadvancal")) 
        
        self.util.dedupeList(settings_widget_list)
        self.settings_widgets = self.wh.createMap(*settings_widget_list)
    
    def setupJog(self):
        jog_widget_list = []
        jog_widget_list.append(self.wh.configWidget(self, QLCDNumber, "xposLCDNumber", role="xpos"))
        jog_widget_list.append(self.wh.configWidget(self, QLCDNumber, "yposLCDNumber", role="ypos"))
        jog_widget_list.append(self.wh.configWidget(self, QLCDNumber, "zposLCDNumber", role="zpos"))
        jog_widget_list.append(self.wh.configWidget(self, QPushButton, "xhomePushButton", "clicked", self.jogAction, role="xhome"))
        jog_widget_list.append(self.wh.configWidget(self, QPushButton, "yhomePushButton", "clicked", self.jogAction, role="yhome"))
        jog_widget_list.append(self.wh.configWidget(self, QPushButton, "zhomePushButton", "clicked", self.jogAction, role="zhome"))
        jog_widget_list.append(self.wh.configWidget(self, QPushButton, "allhomePushButton", "clicked", self.jogAction, role="allhome"))
        jog_widget_list.append(self.wh.configWidget(self, QPushButton, "xminusPushButton", "clicked", self.jogAction, role="xminus"))
        jog_widget_list.append(self.wh.configWidget(self, QPushButton, "xplusPushButton", "clicked", self.jogAction, role="xplus"))
        jog_widget_list.append(self.wh.configWidget(self, QPushButton, "yminusPushButton", "clicked", self.jogAction, role="yminus"))
        jog_widget_list.append(self.wh.configWidget(self, QPushButton, "yplusPushButton", "clicked", self.jogAction, role="yplus"))
        jog_widget_list.append(self.wh.configWidget(self, QPushButton, "zminusPushButton", "clicked", self.jogAction, role="zminus"))
        jog_widget_list.append(self.wh.configWidget(self, QPushButton, "zplusPushButton", "clicked", self.jogAction, role="zplus"))
        jog_widget_list.append(self.wh.configWidget(self, QPushButton, "xycenterPushButton", "clicked", self.jogAction, role="xycenter"))
        jog_widget_list.append(self.wh.configWidget(self, QPushButton, "zcenterPushButton", "clicked", self.jogAction, role="zcenter"))
        jog_widget_list.append(self.wh.configWidget(self, QRadioButton, "travel100_RadioButton", "clicked", self.jogAction, role="travel100"))
        jog_widget_list.append(self.wh.configWidget(self, QRadioButton, "travel50_RadioButton", "clicked", self.jogAction, role="travel50"))
        jog_widget_list.append(self.wh.configWidget(self, QRadioButton, "travel10_RadioButton", "clicked", self.jogAction, role="travel10"))
        jog_widget_list.append(self.wh.configWidget(self, QRadioButton, "travel1_RadioButton", "clicked", self.jogAction, role="travel1"))

        self.util.dedupeList(jog_widget_list)
        self.jog_widgets = self.wh.createMap(*jog_widget_list)
        
    def setupFocus(self):
        focus_widget_list = []
        focus_widget_list.append(self.wh.configWidget(self, QLCDNumber, "focusLCDNumber", role="focus"))
        focus_widget_list.append(self.wh.configWidget(self, QPushButton, "flaserPushButton", "clicked", self.focusAction, role="flaserset"))
        focus_widget_list.append(self.wh.configWidget(self, QPushButton, "fplusPushButton", "clicked", self.focusAction, role="fplus"))
        focus_widget_list.append(self.wh.configWidget(self, QPushButton, "fminusPushButton", "clicked", self.focusAction, role="fminus"))
        focus_widget_list.append(self.wh.configWidget(self, QPushButton, "ftravelPushButton", "clicked", self.focusAction, role="ftravel"))
        focus_widget_list.append(self.wh.configWidget(self, QPushButton, "fsetPushButton", "clicked", self.focusAction, role="fset"))
        focus_widget_list.append(self.wh.configWidget(self, QComboBox, "flaserComboBox", "currentTextChanged", self.focusAction, role="flaser"))
        focus_widget_list.append(self.wh.configWidget(self, QLineEdit, "objheightLineEdit", "returnPressed", self.focusAction, role="objheight"))
        
        self.util.dedupeList(focus_widget_list)
        self.focus_widgets = self.wh.createMap(*focus_widget_list)
    
    def setupOffset(self):
        offset_widget_list = []
        offset_widget_list.append(self.wh.configWidget(self, QLCDNumber, "xoffsetLCDNumber", role="xoffset"))
        offset_widget_list.append(self.wh.configWidget(self, QLCDNumber, "yoffsetLCDNumber", role="yoffset"))
        offset_widget_list.append(self.wh.configWidget(self, QPushButton, "offyplusPushButton", "clicked", self.offsetAction, role="offyplus"))
        offset_widget_list.append(self.wh.configWidget(self, QPushButton, "offyminusPushButton", "clicked", self.offsetAction, role="offyminus"))
        offset_widget_list.append(self.wh.configWidget(self, QPushButton, "offxplusPushButton", "clicked", self.offsetAction, role="offxplus"))
        offset_widget_list.append(self.wh.configWidget(self, QPushButton, "offxminusPushButton", "clicked", self.offsetAction, role="offxminus"))
        offset_widget_list.append(self.wh.configWidget(self, QPushButton, "offsetPushButton", "clicked", self.offsetAction, role="offset"))
        offset_widget_list.append(self.wh.configWidget(self, QPushButton, "travelPushButton", "clicked", self.offsetAction, role="travel"))
        offset_widget_list.append(self.wh.configWidget(self, QComboBox, "offlaserComboBox", "currentTextChanged", self.offsetAction, role="offlaser"))
        offset_widget_list.append(self.wh.configWidget(self, QPushButton, "offlaserPushButton", "clicked", self.offsetAction, role="offlaserset"))
        offset_widget_list.append(self.wh.configWidget(self, QPushButton, "offzeroPushButton", "clicked", self.offsetAction, role="offzero"))
        
        self.util.dedupeList(offset_widget_list)
        self.offset_widgets = self.wh.createMap(*offset_widget_list)
    
    def setupProgram(self):
        program_widget_list = []
        program_widget_list.append(self.wh.configWidget(self, QTextEdit, "pgmfileTextEdit", role="pgmfile", toolTip="Select Dxf or Gcode File"))
        program_widget_list.append(self.wh.configWidget(self, QLineEdit, "pgmheightLineEdit", "textChanged", self.onPgmDataChanged, role="pgmheight", arg="height", toolTip="Enter Sample Height"))
        program_widget_list.append(self.wh.configWidget(self, QLineEdit, "pgmfeedLineEdit", "textChanged", self.onPgmDataChanged, role="pgmfeed", arg="feed", toolTip="Enter Scribing Feed"))
        program_widget_list.append(self.wh.configWidget(self, QComboBox, "pgmlaserComboBox", "currentTextChanged", self.onPgmDataChanged, role="pgmlaser", arg="laser", toolTip="Select Laser"))
        program_widget_list.append(self.wh.configWidget(self, QPushButton, "pgmfilePushButton", "clicked", self.programAction, role="pgmfileset", toolTip="Browse File"))
        program_widget_list.append(self.wh.configWidget(self, QPushButton, "pgmsavePushButton", "clicked", self.programAction, role="pgmsaveset", toolTip="Save G-code"))
        # program_widget_list.append(self.wh.configWidget(self, QPushButton, "pgmstepsPushButton", "clicked", self.programAction))
        
        self.util.dedupeList(program_widget_list)
        self.program_widgets = self.wh.createMap(*program_widget_list)

        # Restrict inputs to numbers and a single decimal point
        regex_validator = QRegularExpressionValidator(QRegularExpression(r"^\d*\.?\d*$"), self)
        self.program_widgets.pgmheight.setValidator(regex_validator)
        self.program_widgets.pgmfeed.setValidator(regex_validator)

    
    def setupPrint(self):
        print_widget_list = []
        print_widget_list.append(self.wh.configWidget(self, QLabel, "progressLabel", role="progress"))        
        print_widget_list.append(self.wh.configWidget(self, QProgressBar, "printProgressBar", role="print"))
        print_widget_list.append(self.wh.configWidget(self, QFrame, "printplotFrame", role="printplot"))
        print_widget_list.append(self.wh.configWidget(self, QPushButton, "printrunPushButton", "clicked", self.printAction, role="printrun", toolTip="Run"))
        print_widget_list.append(self.wh.configWidget(self, QPushButton, "printpausePushButton", "clicked", self.printAction, role="printpause", toolTip="Pause/Resume"))
        print_widget_list.append(self.wh.configWidget(self, QPushButton, "printabortPushButton", "clicked", self.printAction, role="printabort", toolTip="Abort"))
        print_widget_list.append(self.wh.configWidget(self, QPushButton, "inspectionPushButton", "clicked", self.printAction, role="printinspect", toolTip="Camera Inspection"))


        self.util.dedupeList(print_widget_list)
        self.print_widgets = self.wh.createMap(*print_widget_list)
        
        plot = QVBoxLayout()
        self.print_widgets.printplot.setLayout(plot)
        plot.addWidget(self.preview)

        
    def setupCamera(self):
        camera_widget_list = []
        camera_widget_list.append(self.wh.configWidget(self, QFrame, "camvdoFrame", role="camvdo"))
        camera_widget_list.append(self.wh.configWidget(self, QPushButton, "camstartPushButton", "clicked", self.cameraAction, role="camstart"))
        camera_widget_list.append(self.wh.configWidget(self, QPushButton, "camstopPushButton", "clicked", self.cameraAction, role="camstop"))
        camera_widget_list.append(self.wh.configWidget(self, QPushButton, "campausePushButton", "clicked", self.cameraAction, role="campause"))
        
        # Offset Buttons
        camera_widget_list.append(self.wh.configWidget(self, QPushButton, "camoffxplusPushButton", "clicked", self.cameraAction, role="camoffxplus"))
        camera_widget_list.append(self.wh.configWidget(self, QPushButton, "camoffxminusPushButton", "clicked", self.cameraAction, role="camoffxminus"))
        camera_widget_list.append(self.wh.configWidget(self, QPushButton, "camoffyplusPushButton", "clicked", self.cameraAction, role="camoffyplus"))
        camera_widget_list.append(self.wh.configWidget(self, QPushButton, "camoffyminusPushButton", "clicked", self.cameraAction, role="camoffyminus"))
        camera_widget_list.append(self.wh.configWidget(self, QPushButton, "camoffzplusPushButton", "clicked", self.cameraAction, role="camoffzplus"))
        camera_widget_list.append(self.wh.configWidget(self, QPushButton, "camoffzminusPushButton", "clicked", self.cameraAction, role="camoffzminus"))
        
        # Radio Buttons
        camera_widget_list.append(self.wh.configWidget(self, QRadioButton, "camstep10_RadioButton", "clicked", self.cameraAction, role="camstep10"))
        camera_widget_list.append(self.wh.configWidget(self, QRadioButton, "camstep5_RadioButton", "clicked", self.cameraAction, role="camstep5"))
        camera_widget_list.append(self.wh.configWidget(self, QRadioButton, "camstep1_RadioButton", "clicked", self.cameraAction, role="camstep1"))
        camera_widget_list.append(self.wh.configWidget(self, QRadioButton, "camstep01_RadioButton", "clicked", self.cameraAction, role="camstep01"))

        self.util.dedupeList(camera_widget_list)
        self.camera_widgets = self.wh.createMap(*camera_widget_list)
        
        # Init visibility
        btn_opt = getattr(self.ui, "cameraoffsetPushButton", None)
        btn_jog = getattr(self.ui, "cameraonoffoffsetPushButton", None)
        if btn_opt:
            btn_opt.setText("ON")
        # if btn_jog:
        #     # KEEP LABEL AS IS: "Camera Jog"
        #     btn_jog.setText("Camera Jog")
        if hasattr(self.ui, 'cameraxyoffFrame'):
            self.ui.cameraxyoffFrame.setVisible(False)
    
    def setupTerminal(self):
        key_filter = KeyFilter(self, trigger_events=(QEvent.KeyPress, QEvent.KeyRelease))
        self.eh.attachCallback(Qt.Key_Return, self.onKeyEnter)
        self.eh.attachCallback(Qt.Key_Enter, self.onKeyEnter)
        self.eh.attachCallback(Qt.Key_Up, self.onKeyUp)
        self.eh.attachCallback(Qt.Key_Down, self.onKeyDown)
        
        terminal_widget_list = []        
        terminal_widget_list.append(self.wh.configWidget(self, QTextEdit, "termresponseTextEdit", role="termresponse"))
        # terminal_widget_list.append(self.wh.configWidget(self, QLineEdit, "termdataLineEdit", "returnPressed", self.terminalAction))
        terminal_widget_list.append(self.wh.configWidget(self, QLineEdit, "termdataLineEdit", "event", self.terminalAction, key_filter, role="termdata"))
        terminal_widget_list.append(self.wh.configWidget(self, QPushButton, "termsendPushButton", "clicked", self.terminalAction, role="termsend"))
        
        self.util.dedupeList(terminal_widget_list)
        self.terminal_widgets = self.wh.createMap(*terminal_widget_list)

    def setupJogGalvo(self):
        widget_list = []
        widget_list.append(self.wh.configWidget(self, QPushButton, "galvohomePushButton", "clicked", self.jogGalvoAction, role="galvohome"))
        widget_list.append(self.wh.configWidget(self, QPushButton, "galvozhomePushButton", "clicked", self.jogGalvoAction, role="galvozhome"))
        widget_list.append(self.wh.configWidget(self, QPushButton, "galvoallhomePushButton", "clicked", self.jogGalvoAction, role="galvoallhome"))
        widget_list.append(self.wh.configWidget(self, QPushButton, "circlePushButton", "clicked", self.jogGalvoAction, role="circle"))
        widget_list.append(self.wh.configWidget(self, QPushButton, "trianglePushButton", "clicked", self.jogGalvoAction, role="triangle"))
        widget_list.append(self.wh.configWidget(self, QPushButton, "squarePushButton", "clicked", self.jogGalvoAction, role="square"))
        widget_list.append(self.wh.configWidget(self, QPushButton, "zplusgalvoPushButton", "clicked", self.jogGalvoAction, role="zplusgalvo"))
        widget_list.append(self.wh.configWidget(self, QPushButton, "ztravelPushButton", "clicked", self.jogGalvoAction, role="ztravel"))
        widget_list.append(self.wh.configWidget(self, QPushButton, "zminusgalvoPushButton", "clicked", self.jogGalvoAction, role="zminusgalvo"))
        self.util.dedupeList(widget_list)
        self.joggalvo_widgets = self.wh.createMap(*widget_list)

    def setupLaserConfGalvo(self):
        widget_list = []
        widget_list.append(self.wh.configWidget(self, QLineEdit, "galvoobjheightLineEdit", "textChanged", self.laserConfGalvoAction, role="galvoobjheight"))
        widget_list.append(self.wh.configWidget(self, QComboBox, "flasergalvoComboBox", "currentTextChanged", self.laserConfGalvoAction, role="flasergalvo"))
        widget_list.append(self.wh.configWidget(self, QPushButton, "flasergalvoPushButton", "clicked", self.laserConfGalvoAction, role="flasergalvoset"))
        widget_list.append(self.wh.configWidget(self, QPushButton, "freddotlasergalvoPushButton", "clicked", self.laserConfGalvoAction, role="freddotlasergalvoset"))
        widget_list.append(self.wh.configWidget(self, QPushButton, "fplusgalvoPushButton", "clicked", self.laserConfGalvoAction, role="fplusgalvo"))
        widget_list.append(self.wh.configWidget(self, QPushButton, "ftravelgalvoPushButton", "clicked", self.laserConfGalvoAction, role="ftravelgalvo"))
        widget_list.append(self.wh.configWidget(self, QPushButton, "fminusgalvoPushButton", "clicked", self.laserConfGalvoAction, role="fminusgalvo"))
        widget_list.append(self.wh.configWidget(self, QPushButton, "fsetgalvoPushButton", "clicked", self.laserConfGalvoAction, role="fsetgalvo"))
        
        widget_list.append(self.wh.configWidget(self, QSlider, "galvolaserpowerHorizontalSlider_2", "valueChanged", self.laserConfGalvoAction, role="galvolaserpower"))
        widget_list.append(self.wh.configWidget(self, QLineEdit, "laserpowerLineEdit", "returnPressed", self.laserConfGalvoAction, role="laserpower"))
        widget_list.append(self.wh.configWidget(self, QSlider, "galvolaserfreqHorizontalSlider", "valueChanged", self.laserConfGalvoAction, role="galvolaserfreq"))
        widget_list.append(self.wh.configWidget(self, QLineEdit, "laserfreqLineEdit", "returnPressed", self.laserConfGalvoAction, role="laserfreq"))
        widget_list.append(self.wh.configWidget(self, QPushButton, "powersetgalvoPushButton", "clicked", self.printGalvoAction, role="powersetgalvo"))
        widget_list.append(self.wh.configWidget(self, QPushButton, "freqsetgalvoPushButton", "clicked", self.printGalvoAction, role="freqsetgalvo"))
        
        self.util.dedupeList(widget_list)
        self.laserconfgalvo_widgets = self.wh.createMap(*widget_list)
        
        # Ensure the laser button is enabled
        if hasattr(self.ui, 'flasergalvoPushButton'):
            self.ui.flasergalvoPushButton.setEnabled(True)
            
        if hasattr(self.ui, 'freddotlasergalvoPushButton'):
            self.ui.freddotlasergalvoPushButton.setEnabled(True)
            
        if hasattr(self.ui, 'galvoobjheightLineEdit'):
            self.ui.galvoobjheightLineEdit.returnPressed.connect(self.save_galvoobjheight_to_config)

    def save_galvoobjheight_to_config(self):
        try:
            val = float(self.ui.galvoobjheightLineEdit.text() or 0.0)
        except ValueError:
            val = 0.0
        self.ch.addParameter("focus", "galvoobjheight", f"{val:.2f}")
        if hasattr(self, 'config_file_path'):
            self.ch.updateFile(self.config_file_path)
            self.showAutoCloseMessage("Saved", f"Object height saved as {val:.2f} mm.")

    def setupProgramsGalvo(self):
        self.current_hatch_idx = 1
        self._loading_hatch = True
        self.hatch_profiles = {
            1: self._default_hatch_profile(),
            2: self._default_hatch_profile(),
            3: self._default_hatch_profile()
        }
        widget_list = []
        widget_list.append(self.wh.configWidget(self, QTextEdit, "pgmfilegalvoTextEdit", role="pgmfilegalvotext"))
        widget_list.append(self.wh.configWidget(self, QPushButton, "pgmfilegalvoPushButton", "clicked", self.programsGalvoAction, role="pgmfilegalvo"))
        widget_list.append(self.wh.configWidget(self, QLineEdit, "pgmheightgalvoLineEdit", "textChanged", self.programsGalvoAction, role="pgmheightgalvo"))
        widget_list.append(self.wh.configWidget(self, QLineEdit, "pgmmarkspeedgalvoLineEdit", "textChanged", self.programsGalvoAction, role="pgmmarkspeedgalvo"))
        widget_list.append(self.wh.configWidget(self, QLineEdit, "pgmjumpspeedLineEdit", "textChanged", self.programsGalvoAction, role="pgmjumpspeed"))
        widget_list.append(self.wh.configWidget(self, QLineEdit, "pgmloopcountLineEdit", "textChanged", self.programsGalvoAction, role="pgmloopcount"))
        widget_list.append(self.wh.configWidget(self, QLineEdit, "pgmstartposxLineEdit", "textChanged", self.programsGalvoAction, role="pgmstartposx"))
        widget_list.append(self.wh.configWidget(self, QLineEdit, "pgmstartposyLineEdit", "textChanged", self.programsGalvoAction, role="pgmstartposy"))
        widget_list.append(self.wh.configWidget(self, QCheckBox, "pgmenablehatchCheckBox", "clicked", self.programsGalvoAction, role="pgmenablehatch"))
        widget_list.append(self.wh.configWidget(self, QCheckBox, "pgmmarkcontourCheckBox", "clicked", self.programsGalvoAction, role="pgmmarkcontour"))
        widget_list.append(self.wh.configWidget(self, QRadioButton, "pgmhatch1_RadioButton", "clicked", self.programsGalvoAction, role="pgmhatch1"))
        widget_list.append(self.wh.configWidget(self, QRadioButton, "pgmhatch2_RadioButton", "clicked", self.programsGalvoAction, role="pgmhatch2"))
        widget_list.append(self.wh.configWidget(self, QRadioButton, "pgmhatch3_RadioButton", "clicked", self.programsGalvoAction, role="pgmhatch3"))
        widget_list.append(self.wh.configWidget(self, QCheckBox, "pgmallcalcCheckBox", "clicked", self.programsGalvoAction, role="pgmallcalc"))
        widget_list.append(self.wh.configWidget(self, QCheckBox, "pgmfolloedgCheckBox", "clicked", self.programsGalvoAction, role="pgmfolloedg"))
        widget_list.append(self.wh.configWidget(self, QCheckBox, "pgmcrosshatchCheckBox", "clicked", self.programsGalvoAction, role="pgmcrosshatch"))
        widget_list.append(self.wh.configWidget(self, QComboBox, "pgmtypeComboBox", "currentTextChanged", self.programsGalvoAction, role="pgmtype"))
        widget_list.append(self.wh.configWidget(self, QLineEdit, "pgmangleLineEdit", "textChanged", self.programsGalvoAction, role="pgmangle"))
        widget_list.append(self.wh.configWidget(self, QLineEdit, "pgmcountLineEdit", "textChanged", self.programsGalvoAction, role="pgmcount"))
        widget_list.append(self.wh.configWidget(self, QLineEdit, "pgmlinespaceLineEdit", "textChanged", self.programsGalvoAction, role="pgmlinespace"))
        widget_list.append(self.wh.configWidget(self, QCheckBox, "pgmavgdistCheckBox", "clicked", self.programsGalvoAction, role="pgmavgdist"))
        widget_list.append(self.wh.configWidget(self, QLineEdit, "pgmedgeoffLineEdit", "textChanged", self.programsGalvoAction, role="pgmedgeoff"))
        widget_list.append(self.wh.configWidget(self, QLineEdit, "pgmstartoffLineEdit", "textChanged", self.programsGalvoAction, role="pgmstartoff"))
        widget_list.append(self.wh.configWidget(self, QLineEdit, "pgmendoffLineEdit", "textChanged", self.programsGalvoAction, role="pgmendoff"))
        widget_list.append(self.wh.configWidget(self, QLineEdit, "pgmlineredLineEdit", "textChanged", self.programsGalvoAction, role="pgmlinered"))
        widget_list.append(self.wh.configWidget(self, QLineEdit, "pgmnumloopsLineEdit", "textChanged", self.programsGalvoAction, role="pgmnumloops"))
        widget_list.append(self.wh.configWidget(self, QLineEdit, "pgmloopdistLineEdit", "textChanged", self.programsGalvoAction, role="pgmloopdist"))
        widget_list.append(self.wh.configWidget(self, QCheckBox, "pgmautorotangleCheckBox", "clicked", self.programsGalvoAction, role="pgmautorotangle"))
        widget_list.append(self.wh.configWidget(self, QLineEdit, "pgmautorotanglLineEdit", "textChanged", self.programsGalvoAction, role="pgmautorotangl"))
        widget_list.append(self.wh.configWidget(self, QPushButton, "pgmgalvosavePushButton", "clicked", self.programsGalvoAction, role="pgmgalvosave"))
        widget_list.append(self.wh.configWidget(self, QCheckBox, "pgmenableCheckBox", "clicked", self.programsGalvoAction, role="pgmenable"))
        
        # Add default hatch settings
        self.ui.pgmtypeComboBox.clear()
        self.ui.pgmtypeComboBox.addItems(["Bidirectional", "Unidirectional", "Ring-like", "Optimized / Bow-tie", "Auto-Sorting / Block Hatch"])
        if not self.ui.pgmangleLineEdit.text(): self.ui.pgmangleLineEdit.setText("0.0")
        if not self.ui.pgmcountLineEdit.text(): self.ui.pgmcountLineEdit.setText("1")
        if not self.ui.pgmlinespaceLineEdit.text(): self.ui.pgmlinespaceLineEdit.setText("0.05")
        if not self.ui.pgmedgeoffLineEdit.text(): self.ui.pgmedgeoffLineEdit.setText("0.0")
        if not self.ui.pgmstartoffLineEdit.text(): self.ui.pgmstartoffLineEdit.setText("0.0")
        if not self.ui.pgmendoffLineEdit.text(): self.ui.pgmendoffLineEdit.setText("0.0")
        if not self.ui.pgmlineredLineEdit.text(): self.ui.pgmlineredLineEdit.setText("0.0")
        if not self.ui.pgmnumloopsLineEdit.text(): self.ui.pgmnumloopsLineEdit.setText("0")
        if not self.ui.pgmloopdistLineEdit.text(): self.ui.pgmloopdistLineEdit.setText("0.05")
        if not self.ui.pgmautorotanglLineEdit.text(): self.ui.pgmautorotanglLineEdit.setText("10.0")
        
        self.util.dedupeList(widget_list)
        self.programgalvo_widgets = self.wh.createMap(*widget_list)
        
        # Initialize hatch UI visibility state
        self.programsGalvoAction(self.ui.pgmenablehatchCheckBox)
        self._load_hatch_profiles_from_config()
        self.load_hatch_profile(1)

    def setupPrintGalvo(self):
        widget_list = []
        widget_list.append(self.wh.configWidget(self, QPushButton, "printrungalvoPushButton", "clicked", self.printGalvoAction, role="printrungalvo"))
        widget_list.append(self.wh.configWidget(self, QPushButton, "printabortgalvoPushButton", "clicked", self.printGalvoAction, role="printabortgalvo"))
        widget_list.append(self.wh.configWidget(self, QPushButton, "redlightprePushButton", "clicked", self.printGalvoAction, role="redlightpre"))
        self.util.dedupeList(widget_list)
        self.printgalvo_widgets = self.wh.createMap(*widget_list)
        self.ui.redlightprePushButton.setText("START")
        
        from PySide6.QtGui import QShortcut, QKeySequence
        self.f1_shortcut = QShortcut(QKeySequence("F1"), self)
        self.f1_shortcut.activated.connect(self.handle_f1_shortcut)
        
        self.f2_shortcut = QShortcut(QKeySequence("F2"), self)
        self.f2_shortcut.activated.connect(self.handle_f2_shortcut)

    def handle_f1_shortcut(self):
        if hasattr(self.ui, 'redlightprePushButton') and self.ui.redlightprePushButton.isVisible():
            if self.ui.redlightprePushButton.isEnabled():
                self.printGalvoAction(self.ui.redlightprePushButton)

    def handle_f2_shortcut(self):
        if hasattr(self.ui, 'printrungalvoPushButton') and self.ui.printrungalvoPushButton.isVisible():
            if self.ui.printrungalvoPushButton.isEnabled():
                self.printGalvoAction(self.ui.printrungalvoPushButton)
            elif hasattr(self.ui, 'printabortgalvoPushButton') and self.ui.printabortgalvoPushButton.isEnabled():
                self.printGalvoAction(self.ui.printabortgalvoPushButton)

    def setupConfigGalvo(self):
        from PySide6.QtWidgets import QButtonGroup
        
        # Create Button Groups for Radio Buttons/CheckBoxes to ensure mutual exclusivity
        self.galvo_assignment_group = QButtonGroup(self)
        if hasattr(self.ui, 'galvo1confRadioButton'): self.galvo_assignment_group.addButton(self.ui.galvo1confRadioButton)
        elif hasattr(self.ui, 'galvo1confCheckBox'): self.galvo_assignment_group.addButton(self.ui.galvo1confCheckBox)
        
        if hasattr(self.ui, 'galvo2confRadioButton'): self.galvo_assignment_group.addButton(self.ui.galvo2confRadioButton)
        elif hasattr(self.ui, 'galvo2confCheckBox'): self.galvo_assignment_group.addButton(self.ui.galvo2confCheckBox)

        self.pos_after_mark_group = QButtonGroup(self)
        for name in ['confnomov', 'confgalvocent', 'conftopleft', 'conftopright', 'confbotright', 'confbotleft', 'confspecpos']:
            if hasattr(self.ui, f"{name}RadioButton"): self.pos_after_mark_group.addButton(getattr(self.ui, f"{name}RadioButton"))
            elif hasattr(self.ui, f"{name}CheckBox"): self.pos_after_mark_group.addButton(getattr(self.ui, f"{name}CheckBox"))

        widget_list = []
        
        # Aspect
        widget_list.append(self.wh.configWidget(self, QLineEdit, "fieldsizeconfLineEdit", "textChanged", self.configGalvoAction, role="fieldsizeconf"))
        widget_list.append(self.wh.configWidget(self, QLineEdit, "offxconfLineEdit", "textChanged", self.configGalvoAction, role="offxconf"))
        widget_list.append(self.wh.configWidget(self, QLineEdit, "offyconfLineEdit", "textChanged", self.configGalvoAction, role="offyconf"))
        widget_list.append(self.wh.configWidget(self, QLineEdit, "angleconfLineEdit", "textChanged", self.configGalvoAction, role="angleconf"))
        
        if hasattr(self.ui, 'galvo1confRadioButton'): widget_list.append(self.wh.configWidget(self, QRadioButton, "galvo1confRadioButton", "clicked", self.configGalvoAction, role="galvo1conf"))
        elif hasattr(self.ui, 'galvo1confCheckBox'): widget_list.append(self.wh.configWidget(self, QCheckBox, "galvo1confCheckBox", "clicked", self.configGalvoAction, role="galvo1conf"))
        
        if hasattr(self.ui, 'galvo2confRadioButton'): widget_list.append(self.wh.configWidget(self, QRadioButton, "galvo2confRadioButton", "clicked", self.configGalvoAction, role="galvo2conf"))
        elif hasattr(self.ui, 'galvo2confCheckBox'): widget_list.append(self.wh.configWidget(self, QCheckBox, "galvo2confCheckBox", "clicked", self.configGalvoAction, role="galvo2conf"))

        # Galvo 1
        widget_list.append(self.wh.configWidget(self, QCheckBox, "neggalvo1confCheckBox", "clicked", self.configGalvoAction, role="neggalvo1conf"))
        widget_list.append(self.wh.configWidget(self, QLineEdit, "confscalegalvo1LineEdit", "textChanged", self.configGalvoAction, role="confscalegalvo1"))
        widget_list.append(self.wh.configWidget(self, QPushButton, "confscalegalvo1PushButton", "clicked", self.configGalvoAction, role="confscalegalvo1btn"))
        widget_list.append(self.wh.configWidget(self, QLineEdit, "confbargalvo1LineEdit", "textChanged", self.configGalvoAction, role="confbargalvo1"))
        widget_list.append(self.wh.configWidget(self, QLineEdit, "confpargalvo1LineEdit", "textChanged", self.configGalvoAction, role="confpargalvo1"))
        widget_list.append(self.wh.configWidget(self, QLineEdit, "conftrapgalvo1LineEdit", "textChanged", self.configGalvoAction, role="conftrapgalvo1"))

        # Galvo 2
        widget_list.append(self.wh.configWidget(self, QCheckBox, "neggalvo2confCheckBox", "clicked", self.configGalvoAction, role="neggalvo2conf"))
        widget_list.append(self.wh.configWidget(self, QLineEdit, "confscalegalvo2LineEdit", "textChanged", self.configGalvoAction, role="confscalegalvo2"))
        widget_list.append(self.wh.configWidget(self, QPushButton, "confscalegalvo2PushButton", "clicked", self.configGalvoAction, role="confscalegalvo2btn"))
        widget_list.append(self.wh.configWidget(self, QLineEdit, "confbargalvo2LineEdit", "textChanged", self.configGalvoAction, role="confbargalvo2"))
        widget_list.append(self.wh.configWidget(self, QLineEdit, "confpargalvo2LineEdit", "textChanged", self.configGalvoAction, role="confpargalvo2"))
        widget_list.append(self.wh.configWidget(self, QLineEdit, "conftrapgalvo2LineEdit", "textChanged", self.configGalvoAction, role="conftrapgalvo2"))

        # Go to Pos After Mark
        for name in ['confnomov', 'confgalvocent', 'conftopleft', 'conftopright', 'confbotright', 'confbotleft', 'confspecpos']:
            if hasattr(self.ui, f"{name}RadioButton"):
                widget_list.append(self.wh.configWidget(self, QRadioButton, f"{name}RadioButton", "clicked", self.configGalvoAction, role=name))
            elif hasattr(self.ui, f"{name}CheckBox"):
                widget_list.append(self.wh.configWidget(self, QCheckBox, f"{name}CheckBox", "clicked", self.configGalvoAction, role=name))
                
        widget_list.append(self.wh.configWidget(self, QLineEdit, "confxmarkLineEdit", "textChanged", self.configGalvoAction, role="confxmark"))
        widget_list.append(self.wh.configWidget(self, QLineEdit, "confymarkLineEdit", "textChanged", self.configGalvoAction, role="confymark"))

        # Buttons
        widget_list.append(self.wh.configWidget(self, QPushButton, "confokPushButton", "clicked", self.configGalvoAction, role="confok"))
        widget_list.append(self.wh.configWidget(self, QPushButton, "confcancelPushButton", "clicked", self.configGalvoAction, role="confcancel"))
        widget_list.append(self.wh.configWidget(self, QPushButton, "confapplyPushButton", "clicked", self.configGalvoAction, role="confapply"))

        self.util.dedupeList(widget_list)
        self.configgalvo_widgets = self.wh.createMap(*widget_list)

    def setupHeader(self): 
        self.wh.configWidget(self, QPushButton, "menuPushButton", role="menu", toolTip="Menu")
        self.wh.configWidget(self, QPushButton, "notifyPushButton", role="notify", toolTip="Notification")
        self.wh.configWidget(self, QPushButton, "minimizePushButton", role="minimize", toolTip="Minimize")
        self.wh.configWidget(self, QPushButton, "restorePushButton", role="restore", toolTip="Maximize")
        self.wh.configWidget(self, QPushButton, "closePushButton", role="close", toolTip="Close")

    # def minimizeWindow(self, widget, *args):
    #     self.showMinimized()

    # def restoreWindow(self, widget, *args):
    #     if self.isMaximized():
    #         self.showNormal()
    #         icon = QIcon()
    #         icon.addFile(u":/icons/icons/square.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
    #         widget.setIcon(icon)
    #     else:
    #         self.showMaximized()
    #         icon = QIcon()
    #         icon.addFile(u":/icons/icons/copy.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
    #         widget.setIcon(icon)

    # def closeWindow(self, widget, *args):
    #     self.close()
      
    def initCom(self):
        self.sigUpdateData.connect(self.updateData, Qt.QueuedConnection)
        self.exceptionOccurred.connect(self.showExceptionPopup)
        self.configSerial("maincom", self.com_widgets, response_callback=self.sigUpdateData.emit, exception_callback=self.updateException)
        # self.beginSerial("maincom") # Handled by onLoad
    
    def initLeftMenu(self):
        pass
    
    def initCenterMenu(self):
        self.center_menu_btn = None
    
    def initNotifyMenu(self):
        NotifierUI.setup(self)

    
    def initProfile(self):
        self.profile_list = ["Operator", "Supervisor", "Technician"]
        self.wh.invokeMethod(self.profile_widgets.user, "add", self.profile_list)
        
        # Set initial state to Operator profile
        self.wh.invokeMethod(self.left_menu_widgets.terminal, "hide")
        self.wh.invokeMethod(self.left_menu_widgets.laser, "hide")
        self.wh.invokeMethod(self.left_menu_widgets.laserconfgalvo, "hide")
        self.wh.invokeMethod(self.center_menu_widgets.settings, "hide")
        if hasattr(self.ui, 'testpatterngalvoFrame'):
            self.wh.invokeMethod(self.ui.testpatterngalvoFrame, "hide")
        
    def initMainPages(self):
        self.main_page_dict = {}
        self.main_page_dict["jog"] = 0
        self.main_page_dict["laser"] = 1
        self.main_page_dict["program"] = 2
        self.main_page_dict["print"] = 3
        self.main_page_dict["camera"] = 4
        self.main_page_dict["joggalvo"] = 5
        self.main_page_dict["laserconfgalvo"] = 6
        self.main_page_dict["programsgalvo"] = 7
        self.main_page_dict["printgalvo"] = 8
        self.main_page_dict["configgalvo"] = 9
        self.main_page_dict["terminal"] = 10
        self.main_page_dict["ezcad"] = 11

    
    def initInfoPages(self):
        pass
    
    def initSettings(self):
        conf_name = "index"
        self.xindex = float(self.ch.getValues(conf_name, "xindex"))
        self.yindex = float(self.ch.getValues(conf_name, "yindex"))

        conf_name = "focus"
        focus_dict = self.ch.getSection(conf_name)

        if focus_dict:
            if 'objheight' in focus_dict:
                objheight_val = focus_dict['objheight']
                if hasattr(self, 'focus_widgets') and hasattr(self.focus_widgets, 'objheight'):
                    self.wh.invokeMethod(self.focus_widgets.objheight, "set", objheight_val)

            for key, value in focus_dict.items():
                if key == 'objheight':
                    continue
                data = value.replace('{', '').replace('}', '')
                try:
                    parts = data.split(':')
                    if len(parts) >= 2:
                        laser = parts[0].strip("'")
                        focus = float(parts[1])
                        self.lh.focus(laser, focus)
                except ValueError:
                    pass

        conf_name = "zero"
        self.zero_laser = self.ch.getValues(conf_name, "laser")

        conf_name = "offset"
        self.offset_laser = self.ch.getValues(conf_name, "laser")
        xoffset_val = self.ch.getValues(conf_name, "xoffset")
        yoffset_val = self.ch.getValues(conf_name, "yoffset")

        if xoffset_val and yoffset_val:
            self.lh.xpos(self.offset_laser, float(xoffset_val))
            self.lh.ypos(self.offset_laser, float(yoffset_val))

        conf_name = "feed"
        self.jog_feed_val = int(self.ch.getValues(conf_name, "jog") or 1000)
        self.laser_feed_val = int(self.ch.getValues(conf_name, "laser") or 500)
        self.jogfeed = self.jog_feed_val # Sync legacy variable

        conf_name = "camera"
        self.camera_inspection_feed = int(self.ch.getValues(conf_name, "inspection_feed") or 300)
        self.camera_jog_feed = int(self.ch.getValues(conf_name, "jog_feed") or 500)

        laser_handler_dict = self.lh.getHandlerData()
        self.util.debugPrint(f"xindex : {self.xindex}")
        self.util.debugPrint(f"yindex : {self.yindex}")
        self.util.debugPrint(f"feed : {self.jog_feed_val}")
        self.util.debugPrint(f"camera inspection feed : {self.camera_inspection_feed}")
        self.util.debugPrint(f"camera jog feed : {self.camera_jog_feed}")
        self.util.debugPrint(f"laser handler : {laser_handler_dict}")

    
    def initJog(self):
        
        self.travel = 10.0
        self.jog_travel = 10.0
        self.xcenter = 150   # midpoint of 300mm X bed
        self.ycenter = 150   # midpoint of 300mm Y bed
        self.zcenter = 25    # midpoint of 50mm Z travel
        self.ecenter = 0

        
        ghome = self.gh.gcode_dict.get("home")
        glinear = self.gh.gcode_dict.get("linear")
        
        self.ah.addAxis("X", 0, 0, 300, self.xcenter, self.jog_feed_val, 800, glinear, glinear, ghome)
        self.ah.addAxis("Y", 0, 0, 300, self.ycenter, self.jog_feed_val, 800, glinear, glinear, ghome)
        self.ah.addAxis("Z", 0, 0, 50,  self.zcenter, self.jog_feed_val, 800, glinear, glinear, ghome)
        self.ah.addAxis("E", 0, 0, 100, self.ecenter, self.jog_feed_val, 800, glinear, glinear, "")
    
    def initFocus(self):
        self.focus_feed = 100
        self.focus_travel = 0.1
    
    def initOffset(self):
        self.offset_feed = 200
        self.offset_travel_index = 0
        self.offset_travel = 10.0
    
    def initProgram(self):
        self.pgm_feed = 600
        self.pgm_steps_index = 1
  
    def initPrint(self):
        self.wh.invokeMethod(self.print_widgets.print, "min", 0)
        self.wh.invokeMethod(self.print_widgets.print, "max", 100)
        self.wh.invokeMethod(self.print_widgets.print, "clear")
        
    def initCamera(self):
        # Camera Display Label
        self.video_label = QLabel("Camera OFF")
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setStyleSheet("background-color: black; color: white; font-size: 20px;")
        
        # Add label to camFrame
        cam_layout = QVBoxLayout(self.camera_widgets.camvdo)
        cam_layout.addWidget(self.video_label)
        cam_layout.setContentsMargins(0, 0, 0, 0)
        cam_layout.setSpacing(0)
        
        self.video_label.setScaledContents(True)

        btn = getattr(self.ui, "cameraoffsetPushButton", None)
        if btn and "OFF" in btn.text().upper():
            if hasattr(self, 'camera_widgets'):
                self.camera_widgets.camstart.setVisible(False)
                self.camera_widgets.campause.setVisible(False)
                self.camera_widgets.camstop.setVisible(False)
                QTimer.singleShot(500, lambda: self.cameraAction(self.camera_widgets.camstart))

    
    def initJogGalvo(self):
        pass

    def initLaserConfGalvo(self):
        pass

    def initProgramsGalvo(self):
        if hasattr(self.ui, 'pgmenablehatchCheckBox'):
            is_checked = self.ui.pgmenablehatchCheckBox.isChecked()
            for w_name in ['widget_27', 'widget_28', 'widget_29', 'frame_19', 'frame_22', 'widget_17']:
                w = getattr(self.ui, w_name, None)
                if w:
                    w.setVisible(is_checked)
        self.validateGalvoProgramFields()

    def initPrintGalvo(self):
        self.galvo_preview = GalvoPreviewWidget(config=self.galvo_config)
        galvo_plot_layout = QVBoxLayout()
        if hasattr(self.ui, 'printplotgalvoFrame'):
            self.ui.printplotgalvoFrame.setLayout(galvo_plot_layout)
            galvo_plot_layout.addWidget(self.galvo_preview)
        
        self.debounce_timer = QTimer()
        self.debounce_timer.setSingleShot(True)
        self.debounce_timer.timeout.connect(self._apply_galvo_settings)

    def initConfigGalvo(self):
        self._loading_config_galvo = True
        try:
            def _get(key, default):
                try:
                    val = self.ch.getValues("GalvoField", key)
                    if val is not None and str(val).strip() != "":
                        return str(val)
                except Exception:
                    pass
                return default
            
            # Aspect
            self.wh.invokeMethod(self.configgalvo_widgets.fieldsizeconf, "set", _get("field_size", "100.0"))
            self.wh.invokeMethod(self.configgalvo_widgets.offxconf, "set", _get("offset_x", "0.0"))
            self.wh.invokeMethod(self.configgalvo_widgets.offyconf, "set", _get("offset_y", "0.0"))
            self.wh.invokeMethod(self.configgalvo_widgets.angleconf, "set", _get("angle", "0"))
            
            is_g1 = _get("galvo1_x", "False") == "True"
            if hasattr(self.ui, 'galvo1confRadioButton'): self.ui.galvo1confRadioButton.setChecked(is_g1)
            elif hasattr(self.ui, 'galvo1confCheckBox'): self.ui.galvo1confCheckBox.setChecked(is_g1)
            
            if hasattr(self.ui, 'galvo2confRadioButton'): self.ui.galvo2confRadioButton.setChecked(not is_g1)
            elif hasattr(self.ui, 'galvo2confCheckBox'): self.ui.galvo2confCheckBox.setChecked(not is_g1)
            
            # Galvo 1
            if hasattr(self.ui, 'neggalvo1confCheckBox'): self.ui.neggalvo1confCheckBox.setChecked(_get("g1_negate", "False") == "True")
            self.wh.invokeMethod(self.configgalvo_widgets.confscalegalvo1, "set", _get("g1_scale", "100.0"))
            self.wh.invokeMethod(self.configgalvo_widgets.confbargalvo1, "set", _get("g1_barrel", "1.0"))
            self.wh.invokeMethod(self.configgalvo_widgets.confpargalvo1, "set", _get("g1_par", "1.0"))
            self.wh.invokeMethod(self.configgalvo_widgets.conftrapgalvo1, "set", _get("g1_trapezoid", "1.0"))
            
            # Galvo 2
            if hasattr(self.ui, 'neggalvo2confCheckBox'): self.ui.neggalvo2confCheckBox.setChecked(_get("g2_negate", "False") == "True")
            self.wh.invokeMethod(self.configgalvo_widgets.confscalegalvo2, "set", _get("g2_scale", "100.0"))
            self.wh.invokeMethod(self.configgalvo_widgets.confbargalvo2, "set", _get("g2_barrel", "1.0"))
            self.wh.invokeMethod(self.configgalvo_widgets.confpargalvo2, "set", _get("g2_par", "1.0"))
            self.wh.invokeMethod(self.configgalvo_widgets.conftrapgalvo2, "set", _get("g2_trapezoid", "1.0"))
            
            # Go to Pos After Mark
            pos_after = _get("pos_after_mark", "confnomovRadioButton")
            radios = ["confnomov", "confgalvocent", "conftopleft", "conftopright", "confbotright", "confbotleft", "confspecpos"]
            for r in radios:
                if hasattr(self.ui, f"{r}RadioButton") and (pos_after == f"{r}RadioButton" or pos_after == f"{r}CheckBox" or pos_after == r):
                    getattr(self.ui, f"{r}RadioButton").setChecked(True)
                elif hasattr(self.ui, f"{r}CheckBox") and (pos_after == f"{r}RadioButton" or pos_after == f"{r}CheckBox" or pos_after == r):
                    getattr(self.ui, f"{r}CheckBox").setChecked(True)
                    
            self.wh.invokeMethod(self.configgalvo_widgets.confxmark, "set", _get("sp_x", "0.0"))
            self.wh.invokeMethod(self.configgalvo_widgets.confymark, "set", _get("sp_y", "0.0"))
            
            # UI States
            is_special = False
            if hasattr(self.ui, 'confspecposRadioButton'): is_special = self.ui.confspecposRadioButton.isChecked()
            elif hasattr(self.ui, 'confspecposCheckBox'): is_special = self.ui.confspecposCheckBox.isChecked()
            
            if hasattr(self.ui, 'confxmarkLineEdit'): self.ui.confxmarkLineEdit.setEnabled(is_special)
            if hasattr(self.ui, 'confymarkLineEdit'): self.ui.confymarkLineEdit.setEnabled(is_special)
            
            if hasattr(self.ui, 'confapplyPushButton'): self.ui.confapplyPushButton.setEnabled(False)
            
            # Synchronize loaded config to core engine
            self._apply_galvo_config_to_core()
            
        finally:
            self._loading_config_galvo = False

    def initTerminal(self):
        self.terminal_buffer = CyclicBuffer(200)
    
    def comAction(self, widget, *args):
        self.wh.getInfo(widget)
        action = self.wh.getRole(widget)
        
        if action == "mainconnectgalvo":
            if self.galvo_has_disconnected or not self.galvo_controller.is_connected:
                self.showAutoCloseMessage("Restart Required", "Please close the UI and restart it to connect with card.\nAlso make sure machine usb is connected properly.", timeout_ms=5000)
                return
                
            success = self.galvo_controller.connect()
            if success:
                self.galvo_controller.galvo_home()
            self.stepper_controller.connection = self.galvo_controller.connection
            if success:
                self.ui.titleLabel.setText("Patterning Machine")

                self.ui.mainconnectgalvoPushButton.setEnabled(False)
                self.ui.maindisconnectgalvoPushButton.setEnabled(True)
                self.showAutoCloseMessage("Connected", "Galvo controller connected successfully.", timeout_ms=3000)
            else:
                self.showAutoCloseMessage("Simulator Mode", "Could not find Galvo hardware. Falling back to Simulator Mode.", timeout_ms=5000)
            return
            
        elif action == "maindisconnectgalvo":
            self.galvo_controller.disconnect()
            self.ui.titleLabel.setText("Patterning Machine (Demo Mode)")

            self.galvo_has_disconnected = True
            self.ui.mainconnectgalvoPushButton.setEnabled(True)
            self.ui.maindisconnectgalvoPushButton.setEnabled(False)
            self.showAutoCloseMessage("Disconnected", "Galvo controller disconnected.", timeout_ms=3000)
            return

        self.activateSerial("maincom", action)
    
    def leftMenuAction(self, widget, *args):
        self.wh.getInfo(widget) 
        action = self.wh.getRole(widget)
        print(f"action : {action}")

        if action == "camerajog":
            self.toggleCameraJog()
    
    def centerMenuAction(self, widget, *args):
        # self.wh.getInfo(widget)
        
        center_menu = self.center_menu_widgets.center
        if widget == self.center_menu_btn or self.wh.checkRole(widget, name="close"):
            center_menu.collapseMenu()
            self.center_menu_btn.setStyleSheet("background-color: rgb(16, 42, 131);")
            self.center_menu_btn = None
            
        else:
            if self.wh.checkRole(widget, name="profile") and self.center_menu_btn is not None:
                self.center_menu_btn.setStyleSheet("background-color: rgb(16, 42, 131);")
            
            self.center_menu_btn = widget
            center_menu.expandMenu() 

    def notifyMenuAction(self, widget):
        self.wh.getInfo(widget) 
        action = self.wh.getRole(widget)
        print(f"action : {action}")

    def onPopupBtnClicked(self, result):
        NotifierUI.onPopupBtnClicked(self, result)

    def showCustomPopup(self, title, message, buttons=QMessageBox.Ok):
        """Show notification in the slide-in panel and block until user responds."""
        return NotifierUI.showCustomPopup(self, title, message, buttons)

    def showAutoCloseMessage(self, title, message, timeout_ms=5000):
        """Show notification that auto-collapses after timeout_ms ms."""
        NotifierUI.showAutoCloseMessage(self, title, message, timeout_ms)

    def closeEvent(self, event):
        reply = self.showCustomPopup(
            "Confirm Exit",
            "Are you sure you want to quit?",
            buttons=QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.util.debugPrint("Application is closing")
            
            if hasattr(self, 'galvo_controller') and self.galvo_controller.is_connected:
                try:
                    self.galvo_controller.connection.laser_off()
                    self.logger.info("Galvo Laser Shutdown")
                except Exception as e:
                    self.util.debugPrint(f"Galvo laser shutdown failed: {e}")
                    
            self.shutdownLaser()
            self.logger.info("Stepper Lasers Shutdown")

            for obj_name in list(self.sercom_dict.keys()):
                obj = self.sercom_dict[obj_name]["obj"]
                try:
                    obj.disconnect()
                except Exception:
                    pass

            self.logger.info("COM connection close successfully")
            self.logger.info("Main window close successfully")

            if hasattr(self.logger, "sessionSeparator"):
                self.logger.sessionSeparator("close")

            event.accept()

        else:
            self.util.debugPrint("Close event ignored.")
            self.logger.info("Close event ignored.")
            event.ignore()

    def showExceptionPopup(self, args: str):
        if getattr(self, "_exception_popup_shown", False):
            return
        self._exception_popup_shown = True

        if "Access is denied" in args:
            title = "Port Busy"
            msg = (
                f"Could not open the selected port.\n\n"
                f"Reason: {args}\n\n"
                f"The port is likely open in another application (e.g. Cura, Arduino).\n"
                f"Please close other programs and try again."
            )
        else:
            title = "Machine Disconnected"
            msg = (
                f"USB/COM connection to the machine was lost.\n\n"
                f"Reason:\n{args}\n\n"
                f"Reconnect the COM port to continue."
            )

        self.showAutoCloseMessage(title, msg, timeout_ms=8000)
        self._exception_popup_shown = False


    def profileAction(self, widget, *args):
        wobj = widget.objectName()
        
        if self.util.checkSubString(wobj, "set"):
            
            user = self.wh.invokeMethod(self.profile_widgets.user, "get")
            password = self.wh.invokeMethod(self.profile_widgets.password, "get")
            self.wh.invokeMethod(self.profile_widgets.password, "clear")
            
            self.util.debugPrint(f"user : {user} | password : {password}")
            
            if user == "Operator" and password == "012345":
                self.logger.info("Profile : Operator")
                self.wh.invokeMethod(self.left_menu_widgets.terminal, "hide")
                self.wh.invokeMethod(self.left_menu_widgets.laser, "hide")
                self.wh.invokeMethod(self.left_menu_widgets.laserconfgalvo, "hide")
                self.wh.invokeMethod(self.center_menu_widgets.settings, "hide")
                if hasattr(self.ui, 'testpatterngalvoFrame'):
                    self.wh.invokeMethod(self.ui.testpatterngalvoFrame, "hide")
            
            elif user == "Supervisor" and password == "452301":
                self.logger.info("Profile : Supervisor")
                self.wh.invokeMethod(self.left_menu_widgets.terminal, "show")
                self.wh.invokeMethod(self.left_menu_widgets.laser, "hide" if str(self.galvo_mode).upper() == "ON" else "show")
                self.wh.invokeMethod(self.left_menu_widgets.laserconfgalvo, "show" if str(self.galvo_mode).upper() == "ON" else "hide")
                self.wh.invokeMethod(self.center_menu_widgets.settings, "show")
                if hasattr(self.ui, 'testpatterngalvoFrame'):
                    self.wh.invokeMethod(self.ui.testpatterngalvoFrame, "show")

                QTimer.singleShot(600000, self.resetProfile)
            
            elif user == "Technician" and password == "543210":
                self.logger.info("Profile : Technician")
                self.wh.invokeMethod(self.left_menu_widgets.terminal, "show")
                self.wh.invokeMethod(self.left_menu_widgets.laser, "hide" if str(self.galvo_mode).upper() == "ON" else "show")
                self.wh.invokeMethod(self.left_menu_widgets.laserconfgalvo, "show" if str(self.galvo_mode).upper() == "ON" else "hide")
                self.wh.invokeMethod(self.center_menu_widgets.settings, "show")
                if hasattr(self.ui, 'testpatterngalvoFrame'):
                    self.wh.invokeMethod(self.ui.testpatterngalvoFrame, "show")
            
            else:
                self.logger.warning(f"Failed login attempt for user: {user}")
                self.showAutoCloseMessage("Login Failed", "Invalid password entered.", timeout_ms=3000)
        
    def mainPagesAction(self, widget, *args):
        self.wh.getInfo(widget) 
        action = self.wh.getRole(widget)
        print(f"action : {action}")
        
    def infoPagesAction(self, widget, *args):
        self.wh.getInfo(widget) 
        action = self.wh.getRole(widget)
        print(f"action : {action}")
        
    def settingAction(self, widget, *args):
        self.wh.getInfo(widget)
        action = self.wh.getRole(widget)
        self.util.debugPrint(f"settingAction : {action}")

        # --- Index field (X,Y format e.g. "10,7") ---
        if action == "index":
            raw = self.wh.invokeMethod(self.settings_widgets.index, "get")
            parts = str(raw).split(",")
            if len(parts) == 2:
                try:
                    self.xindex = float(parts[0].strip())
                    self.yindex = float(parts[1].strip())
                    self.util.debugPrint(f"Index updated: X={self.xindex} Y={self.yindex}")

                    # --- Persist to config.ini ---
                    self.ch.addParameter("index", "xindex", str(self.xindex))
                    self.ch.addParameter("index", "yindex", str(self.yindex))
                    self.ch.updateFile(self.config_file_path)

                    self.logger.info(f"Settings saved: xindex={self.xindex}, yindex={self.yindex}")
                    self.showAutoCloseMessage("Settings Saved", f"Index: X={self.xindex}, Y={self.yindex}", timeout_ms=3000)
                except ValueError:
                    self.showAutoCloseMessage("Invalid Index", "Enter index as X,Y (e.g. 10,7)")
            else:
                self.showAutoCloseMessage("Invalid Index", "Index must be in X,Y format (e.g. 10,7).")
            return

        # --- Feed field ---
        # if action == "feed":
        #     raw = self.wh.invokeMethod(self.settings_widgets.feed, "get")
        #     try:
        #         self.jog_feed = int(raw)
        #         self.util.debugPrint(f"Feed updated: {self.jog_feed}")

        #         # --- Persist to config.ini ---
        #         self.ch.addParameter("feed", "feed", str(self.jog_feed))
        #         self.ch.updateFile(self.config_file_path)

        #         self.logger.info(f"Settings saved: feed={self.jog_feed}")
        #         self.showAutoCloseMessage("Settings Saved", f"Feed: {self.jog_feed} mm/min", timeout_ms=3000)
        #     except ValueError:
        #         self.showAutoCloseMessage("Invalid Feed", "Enter a valid integer feed rate.")
        #     return

        if action == "cameraoffset":
            self.toggleCameraJog()
            return
            
        if action == "setconfig":
            self.showMainPages("configgalvo")
            return
            
        if action == "setadvancal":
            from notifier_ui import NotifierUI
            from PySide6.QtWidgets import QFileDialog, QMessageBox
            res = NotifierUI.showActionPopup(self, "Advanced Calibration", "Choose an action:", ["Load cor file", "Create a cor file"])
            if res == "Load cor file":
                file_path, _ = QFileDialog.getOpenFileName(self, "Open Calibration File", "", "EZCAD Cor Files (*.cor);;All Files (*)")
                if file_path:
                    if hasattr(self.galvo_controller, 'connection') and hasattr(self.galvo_controller.connection, 'calibration'):
                        self.galvo_controller.connection.calibration.load_calibration(file_path)
                        if self.galvo_controller.connection.calibration.is_valid:
                            QMessageBox.information(self, "Success", "Binary .cor file loaded successfully!")
                        else:
                            QMessageBox.warning(self, "Error", "Failed to load the selected file. Ensure it is a valid EZCAD .cor file.")
                    else:
                        QMessageBox.warning(self, "Error", "Calibration module not found.")
            elif res == "Create a cor file":
                self.showMainPages("ezcad")
                if hasattr(self, 'center_menu_widgets') and hasattr(self.center_menu_widgets, 'center'):
                    self.center_menu_widgets.center.collapseMenu()
                if hasattr(self, 'center_menu_btn') and self.center_menu_btn:
                    self.center_menu_btn.setStyleSheet("background-color: rgb(16, 42, 131);")
                    self.center_menu_btn = None
            return
        
    def toggleCameraJog(self):
        # State depends on "cameraoffsetPushButton" (ON/OFF toggle)
        # OR current visibility of the offset frame.
        btn_opt = getattr(self.ui, "cameraoffsetPushButton", None)
        
        # Determine current state from btn_opt text (Action Labeling: "ON" means currently OFF)
        if btn_opt:
            current_action = btn_opt.text().upper()
            is_active = "OFF" in current_action # It says "OFF" because it IS currently ON
        else:
            # Fallback to frame visibility if button is missing
            is_active = self.ui.cameraxyoffFrame.isVisible() if hasattr(self.ui, 'cameraxyoffFrame') else False

        if not is_active:
            # ACTIVATE JOG
            new_action = "OFF" # Label for setting button (click to turn OFF)
            visible = True
        else:
            # DEACTIVATE JOG
            new_action = "ON" # Label for setting button (click to turn ON)
            visible = False

        # 1. Update Settings Button Label
        if btn_opt:
            btn_opt.setText(new_action)
        
        # 2. Main Menu Button (cameraonoffoffsetPushButton) stays "Camera Jog"
        # Optional: could update style/color to show active state if desired, 
        # but user wants label unchanged.
        
        if self.is_inspection_running:
            return

        # 3. Handle Visibility and Camera Start/Stop
        if not visible:
            if hasattr(self.ui, 'cameraxyoffFrame'):
                self.ui.cameraxyoffFrame.setVisible(False)
            if hasattr(self, 'camera_widgets'):
                # Reveal standard camera controls
                self.camera_widgets.camstart.setVisible(True)
                self.camera_widgets.campause.setVisible(True)
                self.camera_widgets.camstop.setVisible(True)
        else:
            if hasattr(self.ui, 'cameraxyoffFrame'):
                self.ui.cameraxyoffFrame.setVisible(True)
            if hasattr(self, 'camera_widgets'):
                # Hide standard camera controls while in offset/jog mode
                self.camera_widgets.camstart.setVisible(False)
                self.camera_widgets.campause.setVisible(False)
                self.camera_widgets.camstop.setVisible(False)
                # Auto-start camera stream for jogging
                QTimer.singleShot(500, lambda: self.cameraAction(self.camera_widgets.camstart, skip_restart=True))

        
    def jogGalvoAction(self, widget, *args):
        action = self.wh.getRole(widget)
        self.util.debugPrint(f"jogGalvoAction : {action}")
        
        if action in ["galvohome", "galvozhome", "galvoallhome", "zplusgalvo", "zminusgalvo"]:
            if not self.galvo_controller.is_connected:
                self.showAutoCloseMessage("Hardware Disconnected", "Ensure hardware is connected before moving axis.")
                return
            if not self.verify_hardware_connection():
                return
        
        if action == "galvohome":
            success = self.galvo_controller.galvo_home()
            if success:
                self.showAutoCloseMessage("Homed", "Galvo successfully sent to home position.")
            else:
                self.showAutoCloseMessage("Error", "Failed to home Galvo. Ensure hardware is connected.")
        elif action == "galvozhome":
            self.wh.invokeMethod(widget, "disable")
            from PySide6.QtWidgets import QApplication
            success = self.stepper_controller.home_z(app_instance=QApplication.instance())
            self.wh.invokeMethod(widget, "enable")
            if success:
                self.showAutoCloseMessage("Homing Complete", "Z-Axis successfully homed.")
            else:
                self.showAutoCloseMessage("Homing Failed", "Failed to reach the limit switch.")
                
            self.ah.pos("Z", self.stepper_controller.z_position)
            self.jogPosDisplay()
            self.focusPosDisplay()
        elif action == "galvoallhome":
            self.wh.invokeMethod(widget, "disable")
            from PySide6.QtWidgets import QApplication
            
            galvo_success = self.galvo_controller.galvo_home()
            z_success = self.stepper_controller.home_z(app_instance=QApplication.instance())
            
            self.wh.invokeMethod(widget, "enable")
            
            if galvo_success and z_success:
                self.showAutoCloseMessage("All Homed", "Galvo and Z-Axis successfully homed.")
            else:
                self.showAutoCloseMessage("Homing Failed", "Failed to home Galvo or Z-Axis.")
                
            self.ah.pos("Z", self.stepper_controller.z_position)
            self.jogPosDisplay()
            self.focusPosDisplay()
        elif action == "ztravel":
            travel_list = [10.0, 5.0, 1.0, 0.1]
            if not hasattr(self, "galvo_z_travel_index"):
                self.galvo_z_travel_index = 0
            self.galvo_z_travel_index = (self.galvo_z_travel_index + 1) % len(travel_list)
            val = travel_list[self.galvo_z_travel_index]
            self.wh.invokeMethod(widget, "set", str(val))
            self.galvo_z_travel = val
        elif action == "zplusgalvo":
            travel = getattr(self, "galvo_z_travel", 10.0)
            if self.stepper_controller.z_position + travel > 120.0:
                travel = 120.0 - self.stepper_controller.z_position
                if travel <= 0.0:
                    self.showAutoCloseMessage("Limit Reached", "Z-Axis max limit (120 mm) reached.")
                    return
            self.stepper_controller.move_z_relative(travel)
            self.ah.pos("Z", self.stepper_controller.z_position)
            self.jogPosDisplay()
            self.focusPosDisplay()
        elif action == "zminusgalvo":
            travel = getattr(self, "galvo_z_travel", 10.0)
            if self.stepper_controller.z_position - travel < 0.0:
                travel = self.stepper_controller.z_position
                if travel <= 0.0:
                    self.showAutoCloseMessage("Limit Reached", "Z-Axis min limit (0 mm) reached.")
                    return
            self.stepper_controller.move_z_relative(-travel)
            self.ah.pos("Z", self.stepper_controller.z_position)
            self.jogPosDisplay()
            self.focusPosDisplay()
        elif action in ["circle", "triangle", "square"]:
            self.load_galvo_test_pattern(action)

    def load_galvo_test_pattern(self, shape):
        self.planner.clear()
        self.current_test_shape = shape
        if hasattr(self, 'pgm_file'):
            self.pgm_file = None
            
        try:
            jump_speed = int(self.wh.invokeMethod(self.programgalvo_widgets.pgmjumpspeed, "get") or 2000000)
            mark_speed = int(self.wh.invokeMethod(self.programgalvo_widgets.pgmmarkspeedgalvo, "get") or 1000000)
        except:
            jump_speed = 2000000
            mark_speed = 1000000
            
        import math
        
        size_mm = min(100.0, self.galvo_config.field_size if self.galvo_config else 100.0)
        half_size = size_mm / 2.0

        def _add_jump(x, y):
            if self.galvo_config:
                gx, gy = self.galvo_config.apply_transform(x, y)
            else:
                gx, gy = 32767 + int(x * 65535 / 100), 32767 + int(y * 65535 / 100)
            self.planner.add_jump(gx, gy, speed=jump_speed)

        def _add_mark(x, y):
            if self.galvo_config:
                gx, gy = self.galvo_config.apply_transform(x, y)
            else:
                gx, gy = 32767 + int(x * 65535 / 100), 32767 + int(y * 65535 / 100)
            self.planner.add_mark(gx, gy, speed=mark_speed)

        if shape == "square":
            _add_jump(-half_size, -half_size)
            _add_mark(half_size, -half_size)
            _add_mark(half_size, half_size)
            _add_mark(-half_size, half_size)
            _add_mark(-half_size, -half_size)
        elif shape == "circle":
            radius = half_size
            for i in range(37):
                angle = math.radians(i * 10)
                px = radius * math.cos(angle)
                py = radius * math.sin(angle)
                if i == 0:
                    _add_jump(px, py)
                else:
                    _add_mark(px, py)
        elif shape == "triangle":
            _add_jump(0, half_size)
            _add_mark(half_size, -half_size)
            _add_mark(-half_size, -half_size)
            _add_mark(0, half_size)
            
        _add_jump(0, 0)
        
        self.planner.commit_to_send_queue()
        if hasattr(self, "galvo_preview"):
            self.galvo_preview.draw_queue(self.planner.preview_queue)
        self.update_galvo_preview_bounds()
        self.showMainPages("printgalvo")

    def update_galvo_preview_bounds(self):
        if not self.galvo_preview_thread: return
        min_x, max_x = float('inf'), float('-inf')
        min_y, max_y = float('inf'), float('-inf')
        for cmd in self.planner.send_queue:
            if 'x' in cmd and 'y' in cmd:
                min_x = min(min_x, cmd['x'])
                max_x = max(max_x, cmd['x'])
                min_y = min(min_y, cmd['y'])
                max_y = max(max_y, cmd['y'])
        if min_x != float('inf'):
            self.galvo_preview_thread.update_bounds(min_x, max_x, min_y, max_y)

    def laserConfGalvoAction(self, widget, *args):
        action = self.wh.getRole(widget)
        self.util.debugPrint(f"laserConfGalvoAction : {action}")
        
        if action in ["fplusgalvo", "fminusgalvo"]:
            if not self.galvo_controller.is_connected:
                self.showAutoCloseMessage("Hardware Disconnected", "Ensure hardware is connected before moving focus axis.")
                return
        if action == "ftravelgalvo":
            travel_list = [10.0, 5.0, 1.0, 0.1]
            if not hasattr(self, "galvo_f_travel_index"):
                self.galvo_f_travel_index = 0
            self.galvo_f_travel_index = (self.galvo_f_travel_index + 1) % len(travel_list)
            val = travel_list[self.galvo_f_travel_index]
            self.wh.invokeMethod(widget, "set", str(val))
            self.galvo_f_travel = val
        elif action == "fplusgalvo":
            travel = getattr(self, "galvo_f_travel", 10.0)
            if self.stepper_controller.z_position + travel > 120.0:
                travel = 120.0 - self.stepper_controller.z_position
                if travel <= 0.0:
                    self.showAutoCloseMessage("Limit Reached", "Z-Axis max limit (120 mm) reached.")
                    return
            self.stepper_controller.move_z_relative(travel)
            self.ah.pos("Z", self.stepper_controller.z_position)
            self.jogPosDisplay()
            self.focusPosDisplay()
        elif action == "fminusgalvo":
            travel = getattr(self, "galvo_f_travel", 10.0)
            if self.stepper_controller.z_position - travel < 0.0:
                travel = self.stepper_controller.z_position
                if travel <= 0.0:
                    self.showAutoCloseMessage("Limit Reached", "Z-Axis min limit (0 mm) reached.")
                    return
            self.stepper_controller.move_z_relative(-travel)
            self.ah.pos("Z", self.stepper_controller.z_position)
            self.jogPosDisplay()
            self.focusPosDisplay()
        elif action == "fsetgalvo":
            focus_pos = self.stepper_controller.z_position
            self.ch.addParameter("focus", "galvo_z_focus", str(focus_pos))
            if hasattr(self, 'config_file_path'): self.ch.updateFile(self.config_file_path)
            self.showAutoCloseMessage("Focus Set", f"Z Focus position saved at {focus_pos:.2f} mm.")
        elif action == "flasergalvoset":
            focus_pos = self.stepper_controller.z_position
            self.ch.addParameter("focus", "galvo_z_focus", str(focus_pos))
            if hasattr(self, 'config_file_path'): self.ch.updateFile(self.config_file_path)
            
            if not self.galvo_controller.is_connected:
                self.showAutoCloseMessage("Hardware Disconnected", "Ensure hardware is connected before operating laser.")
                return
                
            current_text = widget.text().upper()
            if current_text == "ON":
                print("UI COMMAND: Turning Laser ON (DO1 = HIGH)")
                self.galvo_controller.connection.laser_on()
                widget.setText("OFF")
                widget.setStyleSheet("QPushButton { color: rgb(255, 255, 255); background-color: rgb(200, 0, 0); border-color: transparent; border-style: outset; border-radius: 20px; border-width: 2px; padding: 6px; }")
            else:
                print("UI COMMAND: Turning Laser OFF (DO1 = LOW)")
                self.galvo_controller.connection.laser_off()
                widget.setText("ON")
                widget.setStyleSheet("QPushButton { color: rgb(255, 255, 255); background-color: rgb(16, 42, 131); border-color: transparent; border-style: outset; border-radius: 20px; border-width: 2px; padding: 6px; }")
        elif action == "freddotlasergalvoset":
            if not self.galvo_controller.is_connected:
                self.showAutoCloseMessage("Hardware Disconnected", "Ensure hardware is connected before operating reddot laser.")
                return
                
            current_text = widget.text().upper()
            if current_text == "ON":
                print("UI COMMAND: Turning Reddot Laser ON")
                if hasattr(self.galvo_controller.connection, 'reddot_on'):
                    self.galvo_controller.connection.reddot_on()
                else:
                    print("WARNING: reddot_on() method not found in connection")
                widget.setText("OFF")
                widget.setStyleSheet("QPushButton { color: rgb(255, 255, 255); background-color: rgb(200, 0, 0); border-color: transparent; border-style: outset; border-radius: 20px; border-width: 2px; padding: 6px; }")
            else:
                print("UI COMMAND: Turning Reddot Laser OFF")
                if hasattr(self.galvo_controller.connection, 'reddot_off'):
                    self.galvo_controller.connection.reddot_off()
                else:
                    print("WARNING: reddot_off() method not found in connection")
                widget.setText("ON")
                widget.setStyleSheet("QPushButton { color: rgb(255, 255, 255); background-color: rgb(16, 42, 131); border-color: transparent; border-style: outset; border-radius: 20px; border-width: 2px; padding: 6px; }")

        elif action == "galvolaserpower":
            val = self.ui.galvolaserpowerHorizontalSlider_2.value()
            self.ui.laserpowerLineEdit.setText(str(val))
        elif action == "laserpower":
            try:
                val = int(self.ui.laserpowerLineEdit.text())
                self.ui.galvolaserpowerHorizontalSlider_2.setValue(val)
            except ValueError:
                pass
        elif action == "galvolaserfreq":
            val = self.ui.galvolaserfreqHorizontalSlider.value()
            self.ui.laserfreqLineEdit.setText(str(val))
        elif action == "laserfreq":
            try:
                val = int(self.ui.laserfreqLineEdit.text())
                self.ui.galvolaserfreqHorizontalSlider.setValue(val)
            except ValueError:
                pass

    def programsGalvoAction(self, widget, *args):
        action = self.wh.getRole(widget)
        self.util.debugPrint(f"programsGalvoAction : {action}")
        
        if action == "pgmfilegalvo":
            self.pgm_file, _ = QFileDialog.getOpenFileName(self, "Select File", "", "Supported Files (*.svg *.dxf);;SVG Files (*.svg);;DXF Files (*.dxf)")
            if self.pgm_file:
                self.wh.invokeMethod(self.programgalvo_widgets.pgmfilegalvotext, "set", os.path.basename(self.pgm_file))
                self.logger.info(f"File selected : {self.pgm_file}")

                # --- CLEANUP ORPHANED JSON FILES ---
                dxf_dir = os.path.dirname(self.pgm_file)
                self.fh.cleanupOrphanedParams(dxf_dir)

                # --- AUTO FETCH PARAMETERS ---
                params = self.fh.loadDxfParams(self.pgm_file)
                if params:
                    self.util.debugPrint(f"Fetched parameters for file: {params}")
                    
                    nested_params = params.get("Galvo program page parameters", params)
                    
                    param_map = {
                        "pgmheightgalvo": "Sample Height",
                        "pgmmarkspeedgalvo": "Mark Speed",
                        "pgmjumpspeed": "Jump Speed",
                        "pgmloopcount": "Loop Count",
                        "pgmstartposx": "Start Pos X",
                        "pgmstartposy": "Start Pos Y"
                    }
                    
                    for role, key in param_map.items():
                        val = nested_params.get(key)
                        if val is not None:
                            widget_ui = getattr(self.programgalvo_widgets, role, None)
                            if widget_ui:
                                self.wh.invokeMethod(widget_ui, "set", str(val))
                                
                    enable_hatch = nested_params.get("Enable Hatch")
                    if enable_hatch is not None:
                        self.ui.pgmenablehatchCheckBox.setChecked(enable_hatch)
                        self.programsGalvoAction(self.ui.pgmenablehatchCheckBox)

                    mode = nested_params.get("Mode")
                    if mode is not None:
                        cross = getattr(self.ui, 'pgmmodeCheckBox', None)
                        if cross: cross.setChecked(mode)

                    self.showAutoCloseMessage("Parameters Fetched", "Previous parameters for this file have been loaded.", timeout_ms=3000)

        elif action == "pgmenablehatch":
            is_checked = self.ui.pgmenablehatchCheckBox.isChecked()
            for w_name in ['widget_32', 'frame_26', 'frame_36', 'widget_33', 'widget_34', 'widget_35', 'frame_22', 'frame_28', 'frame_35', 'frame_39', 'frame_19', 'frame_20', 'frame_21']:
                w = getattr(self.ui, w_name, None)
                if w:
                    w.setVisible(is_checked)
        elif action in ["pgmhatch1", "pgmhatch2", "pgmhatch3"]:
            self.save_current_hatch_profile()
            idx = int(action[-1])
            self.load_hatch_profile(idx)
        elif action == "pgmenable":
            self.save_current_hatch_profile()
        elif action in ["pgmtype", "pgmangle", "pgmcount", "pgmlinespace", "pgmavgdist", "pgmedgeoff", "pgmstartoff", "pgmendoff", "pgmlinered", "pgmnumloops", "pgmloopdist", "pgmautorotangle", "pgmautorotangl", "pgmmarkcontour", "pgmallcalc", "pgmfolloedg", "pgmcrosshatch"]:
            self.save_current_hatch_profile()
        elif action in ["pgmheightgalvo", "pgmmarkspeedgalvo", "pgmjumpspeed", "pgmloopcount", "pgmstartposx", "pgmstartposy"]:
            pass
        elif action == "pgmgalvosave":
            if not getattr(self, 'pgm_file', None):
                self.showAutoCloseMessage("Error", "Please select a file first.")
                return
                
            if self.ui.pgmenablehatchCheckBox.isChecked():
                hatch_type = self.ui.pgmtypeComboBox.currentText()
                valid_types = ["Bidirectional", "Unidirectional", "Ring-like", "Optimized / Bow-tie", "Auto-Sorting / Block Hatch"]
                if not hatch_type or hatch_type not in valid_types:
                    self.showAutoCloseMessage("Error", "Please select a valid Hatch Type before saving.")
                    return
                    
            try:
                galvosampleheight = float(self.ui.pgmheightgalvoLineEdit.text() or 0.0)
            except ValueError:
                galvosampleheight = 0.0
            self.ch.addParameter("focus", "galvosampleheight", f"{galvosampleheight:.2f}")
            if hasattr(self, 'config_file_path'):
                self.ch.updateFile(self.config_file_path)
                
            try:
                params = {
                    "Galvo program page parameters": {
                        "Sample Height": self.wh.invokeMethod(self.programgalvo_widgets.pgmheightgalvo, "get"),
                        "Mark Speed": self.wh.invokeMethod(self.programgalvo_widgets.pgmmarkspeedgalvo, "get"),
                        "Jump Speed": self.wh.invokeMethod(self.programgalvo_widgets.pgmjumpspeed, "get"),
                        "Loop Count": self.wh.invokeMethod(self.programgalvo_widgets.pgmloopcount, "get"),
                        "Start Pos X": getattr(self.programgalvo_widgets, "pgmstartposx", None) and self.wh.invokeMethod(self.programgalvo_widgets.pgmstartposx, "get"),
                        "Start Pos Y": getattr(self.programgalvo_widgets, "pgmstartposy", None) and self.wh.invokeMethod(self.programgalvo_widgets.pgmstartposy, "get"),
                        "Enable Hatch": self.ui.pgmenablehatchCheckBox.isChecked(),
                        "Mode": getattr(self.ui, 'pgmmodeCheckBox', None) and self.ui.pgmmodeCheckBox.isChecked()
                    }
                }
                if self.fh.saveDxfParams(self.pgm_file, params):
                    self.util.debugPrint(f"Saved parameters for Galvo file: {params}")
                    self.logger.info(f"Parameters saved for {self.pgm_file}")
            except Exception as e:
                self.logger.error(f"Failed to save parameters: {e}")
                
            if self.process_galvo_file():
                self.showMainPages("printgalvo")

        self.validateGalvoProgramFields()

    def validateGalvoProgramFields(self):
        is_valid = True
        
        if not getattr(self, 'pgm_file', None):
            is_valid = False
            
        if is_valid:
            required_basic = [
                "pgmheightgalvo", "pgmmarkspeedgalvo", "pgmjumpspeed", 
                "pgmloopcount", "pgmstartposx", "pgmstartposy"
            ]
            for role in required_basic:
                val = self.wh.invokeMethod(getattr(self.programgalvo_widgets, role), "get")
                if val is None or str(val).strip() == "":
                    is_valid = False
                    break
                    

                    
        if hasattr(self, 'pgmgalvosavePushButton'):
            self.pgmgalvosavePushButton.setEnabled(is_valid)
        elif hasattr(self.ui, 'pgmgalvosavePushButton'):
            self.ui.pgmgalvosavePushButton.setEnabled(is_valid)

    def _apply_galvo_config_to_core(self):
        try:
            def _get(key, default):
                try:
                    val = self.ch.getValues("GalvoField", key)
                    if val is not None and str(val).strip() != "":
                        return str(val)
                except Exception: pass
                return default

            if not hasattr(self, 'galvo_config'):
                return

            override_field_size = None
            if hasattr(self, 'galvo_controller') and hasattr(self.galvo_controller, 'connection'):
                if hasattr(self.galvo_controller.connection, 'calibration'):
                    calib = self.galvo_controller.connection.calibration
                    if calib.is_valid and calib.scale is not None:
                        override_field_size = 65535.0 / calib.scale

            if override_field_size:
                self.galvo_config.field_size = override_field_size
            else:
                self.galvo_config.field_size = float(_get("field_size", "100.0"))
            self.galvo_config.offset_x = float(_get("offset_x", "0.0"))
            self.galvo_config.offset_y = float(_get("offset_y", "0.0"))
            self.galvo_config.angle = float(_get("angle", "0.0"))
            
            is_g1_x = _get("galvo1_x", "False") == "True"
            self.galvo_config.galvo_1_is_x = is_g1_x
            
            self.galvo_config.g1_negate = _get("g1_negate", "False") == "True"
            self.galvo_config.g1_scale = float(_get("g1_scale", "100.0"))
            self.galvo_config.g1_bulge = float(_get("g1_barrel", "1.0"))
            self.galvo_config.g1_skew = float(_get("g1_par", "1.0"))
            self.galvo_config.g1_trapezoid = float(_get("g1_trapezoid", "1.0"))
            
            self.galvo_config.g2_negate = _get("g2_negate", "False") == "True"
            self.galvo_config.g2_scale = float(_get("g2_scale", "100.0"))
            self.galvo_config.g2_bulge = float(_get("g2_barrel", "1.0"))
            self.galvo_config.g2_skew = float(_get("g2_par", "1.0"))
            self.galvo_config.g2_trapezoid = float(_get("g2_trapezoid", "1.0"))

        except Exception as e:
            self.util.debugPrint(f"Error applying Galvo config to core: {e}")

    def _apply_galvo_settings(self):
        if hasattr(self, 'current_test_shape') and self.current_test_shape:
            self.load_galvo_test_pattern(self.current_test_shape)
        elif hasattr(self, 'pgm_file') and self.pgm_file:
            self.process_galvo_file()
            
    def _default_hatch_profile(self):
        return {
            "enable": False,
            "mark_contour": False,
            "all_calc": False,
            "follow_edge": False,
            "cross_hatch": False,
            "type": "Bidirectional",
            "angle": "0.0",
            "count": "1",
            "line_space": "0.05",
            "avg_dist": False,
            "edge_off": "0.0",
            "start_off": "0.0",
            "end_off": "0.0",
            "line_red": "0.0",
            "num_loops": "0",
            "loop_dist": "0.05",
            "auto_rot": False,
            "rot_angle": "10.0"
        }

    def _load_hatch_profiles_from_config(self):
        for idx in [1, 2, 3]:
            section = f"hatch_profile_{idx}"
            p = self.hatch_profiles[idx]
            for key in p.keys():
                val = self.ch.getValues(section, key)
                if val is not None and str(val).strip() != "":
                    if isinstance(p[key], bool):
                        p[key] = str(val).lower() == 'true'
                    else:
                        p[key] = str(val)

    def save_current_hatch_profile(self):
        if self._loading_hatch: return
        p = self.hatch_profiles[self.current_hatch_idx]
        p["enable"] = self.ui.pgmenableCheckBox.isChecked()
        p["mark_contour"] = getattr(self.ui, 'pgmmarkcontourCheckBox', None) and self.ui.pgmmarkcontourCheckBox.isChecked()
        p["all_calc"] = getattr(self.ui, 'pgmallcalcCheckBox', None) and self.ui.pgmallcalcCheckBox.isChecked()
        p["follow_edge"] = getattr(self.ui, 'pgmfolloedgCheckBox', None) and self.ui.pgmfolloedgCheckBox.isChecked()
        p["cross_hatch"] = getattr(self.ui, 'pgmcrosshatchCheckBox', None) and self.ui.pgmcrosshatchCheckBox.isChecked()
        p["type"] = self.ui.pgmtypeComboBox.currentText()
        p["angle"] = self.ui.pgmangleLineEdit.text()
        p["count"] = self.ui.pgmcountLineEdit.text()
        p["line_space"] = self.ui.pgmlinespaceLineEdit.text()
        p["avg_dist"] = getattr(self.ui, 'pgmavgdistCheckBox', None) and self.ui.pgmavgdistCheckBox.isChecked()
        p["edge_off"] = self.ui.pgmedgeoffLineEdit.text()
        p["start_off"] = self.ui.pgmstartoffLineEdit.text()
        p["end_off"] = self.ui.pgmendoffLineEdit.text()
        p["line_red"] = self.ui.pgmlineredLineEdit.text()
        p["num_loops"] = self.ui.pgmnumloopsLineEdit.text()
        p["loop_dist"] = self.ui.pgmloopdistLineEdit.text()
        p["auto_rot"] = getattr(self.ui, 'pgmautorotangleCheckBox', None) and self.ui.pgmautorotangleCheckBox.isChecked()
        p["rot_angle"] = self.ui.pgmautorotanglLineEdit.text()
        
        section = f"hatch_profile_{self.current_hatch_idx}"
        for k, v in p.items():
            self.ch.addParameter(section, k, str(v))
        self.ch.updateFile(self.config_file_path)

    def load_hatch_profile(self, idx):
        self._loading_hatch = True
        self.current_hatch_idx = idx
        p = self.hatch_profiles[idx]
        
        self.ui.pgmenableCheckBox.setChecked(p["enable"])
        if getattr(self.ui, 'pgmmarkcontourCheckBox', None): self.ui.pgmmarkcontourCheckBox.setChecked(p["mark_contour"])
        if getattr(self.ui, 'pgmallcalcCheckBox', None): self.ui.pgmallcalcCheckBox.setChecked(p["all_calc"])
        if getattr(self.ui, 'pgmfolloedgCheckBox', None): self.ui.pgmfolloedgCheckBox.setChecked(p["follow_edge"])
        if getattr(self.ui, 'pgmcrosshatchCheckBox', None): self.ui.pgmcrosshatchCheckBox.setChecked(p["cross_hatch"])
        self.ui.pgmtypeComboBox.setCurrentText(p["type"])
        self.ui.pgmangleLineEdit.setText(p["angle"])
        self.ui.pgmcountLineEdit.setText(p["count"])
        self.ui.pgmlinespaceLineEdit.setText(p["line_space"])
        if getattr(self.ui, 'pgmavgdistCheckBox', None): self.ui.pgmavgdistCheckBox.setChecked(p["avg_dist"])
        self.ui.pgmedgeoffLineEdit.setText(p["edge_off"])
        self.ui.pgmstartoffLineEdit.setText(p["start_off"])
        self.ui.pgmendoffLineEdit.setText(p["end_off"])
        self.ui.pgmlineredLineEdit.setText(p["line_red"])
        self.ui.pgmnumloopsLineEdit.setText(p["num_loops"])
        self.ui.pgmloopdistLineEdit.setText(p["loop_dist"])
        if getattr(self.ui, 'pgmautorotangleCheckBox', None): self.ui.pgmautorotangleCheckBox.setChecked(p["auto_rot"])
        self.ui.pgmautorotanglLineEdit.setText(p["rot_angle"])
            
        self._loading_hatch = False



    def updatePreviewGalvo(self, filepath):
        self.util.debugPrint(f"updatePreviewGalvo({filepath})")
        self.pgm_file = filepath
        self.current_test_shape = None
        
        try:
            self.process_galvo_file()
        except Exception as e:
            self.util.debugPrint(f"Preview update error: {e}")

    def process_galvo_file(self):
        if hasattr(self, "_current_printing_pass"):
            del self._current_printing_pass
            
        filepath = getattr(self, 'pgm_file', None)
        if not filepath: return False
        
        try:
            jump_speed = int(self.wh.invokeMethod(self.programgalvo_widgets.pgmjumpspeed, "get") or 2000000)
            mark_speed = int(self.wh.invokeMethod(self.programgalvo_widgets.pgmmarkspeedgalvo, "get") or 1000000)
            
            try:
                start_x_str = self.wh.invokeMethod(self.programgalvo_widgets.pgmstartposx, "get")
                start_x = float(start_x_str.strip() if start_x_str and start_x_str.strip() else 0.0)
                start_y_str = self.wh.invokeMethod(self.programgalvo_widgets.pgmstartposy, "get")
                start_y = float(start_y_str.strip() if start_y_str and start_y_str.strip() else 0.0)
            except ValueError:
                start_x, start_y = 0.0, 0.0
        except Exception:
            return False
            
        if filepath.lower().endswith('.dxf'):
            from dxf import DXFParser
            parser = DXFParser(filepath)
            polygons = parser.parse_to_polygons(field_size=self.galvo_config.field_size)
        else:
            parser = SVGParser(field_size=self.galvo_config.field_size)
            polygons = parser.parse_to_polygons(filepath)
        
        if not polygons: return False
        
        # Calculate design dimensions in mm
        min_x, max_x = float('inf'), float('-inf')
        min_y, max_y = float('inf'), float('-inf')
        for poly in polygons:
            for pt in poly:
                min_x = min(min_x, pt[0])
                max_x = max(max_x, pt[0])
                min_y = min(min_y, pt[1])
                max_y = max(max_y, pt[1])
                
        if min_x == float('inf'):
            return False
            
        w = max_x - min_x
        h = max_y - min_y
        lens_size = self.galvo_config.field_size
        
        if w > lens_size or h > lens_size:
            self.showCustomPopup("Design Too Large", f"Design size ({w:.1f}x{h:.1f}mm) is larger than lens area ({lens_size}x{lens_size}mm).", buttons=QMessageBox.Ok)
            return False
            
        max_start_x = lens_size - w
        max_start_y = lens_size - h
        
        if start_x < 0 or start_x > max_start_x or start_y < 0 or start_y > max_start_y:
            self.showCustomPopup("Invalid Start Position", f"Design size is {w:.1f}x{h:.1f}mm.\nFor a {lens_size}x{lens_size}mm lens:\nValid Start Pos X: 0 to {max_start_x:.1f}\nValid Start Pos Y: 0 to {max_start_y:.1f}\n\nPlease adjust the Start Pos.", buttons=QMessageBox.Ok)
            return False
            
        target_min_x = start_x - (lens_size / 2.0)
        target_min_y = start_y - (lens_size / 2.0)
        shift_x = target_min_x - min_x
        shift_y = target_min_y - min_y

        self.planner.clear()
        # Check if a .cor file is loaded and provides a native scale
        calib_scale = None
        if hasattr(self, 'galvo_controller') and hasattr(self.galvo_controller, 'connection'):
            if hasattr(self.galvo_controller.connection, 'calibration'):
                calib = self.galvo_controller.connection.calibration
                if calib.is_valid and calib.scale is not None:
                    calib_scale = calib.scale
        
        if calib_scale:
            galvo_units_per_mm = calib_scale
            # Update lens_size for preview/bounds math to match the physical lens
            lens_size = 65535 / calib_scale
            self.galvo_config.field_size = lens_size
        else:
            galvo_units_per_mm = 65535 / self.galvo_config.field_size
        
        is_hatch = self.ui.pgmenablehatchCheckBox.isChecked()
        mark_contour = getattr(self.ui, 'pgmmarkcontourCheckBox', None) and self.ui.pgmmarkcontourCheckBox.isChecked()
        
        # If hatching is not enabled, we must draw the contour so something is printed
        if not is_hatch:
            mark_contour = True
        
        hatch_configs = []
        if is_hatch:
            self.save_current_hatch_profile()
            for k, p in self.hatch_profiles.items():
                if not p.get("enable", False):
                    continue
                try:
                    cfg = {
                        'enable': True,
                        'follow_edge': p.get("follow_edge", False),
                        'all_calc': p.get("all_calc", False),
                        'cross_hatch': p.get("cross_hatch", False),
                        'type': p.get("type", "Bidirectional"),
                        'angle': float(p.get("angle", "0.0") or 0.0),
                        'pen_no': 0,
                        'count': int(p.get("count", "1") or 1),
                        'line_space': float(p.get("line_space", "0.05") or 0.05),
                        'avg_distribute': p.get("avg_dist", False),
                        'edge_offset': float(p.get("edge_off", "0.0") or 0.0),
                        'start_offset': float(p.get("start_off", "0.0") or 0.0),
                        'end_offset': float(p.get("end_off", "0.0") or 0.0),
                        'line_reduction': float(p.get("line_red", "0.0") or 0.0),
                        'num_loops': int(p.get("num_loops", "0") or 0),
                        'loop_distance': float(p.get("loop_dist", "0.05") or 0.05),
                        'auto_rotate': p.get("auto_rot", False),
                        'rotate_angle': float(p.get("rot_angle", "10.0") or 10.0),
                        'hatch_idx': k
                    }
                    hatch_configs.append(cfg)
                except Exception as e:
                    self.util.debugPrint(f"Hatch config {k} error: {e}")
                    pass
                
        all_polys_galvo = []
        seen_polys = set()
        
        for poly in polygons:
            if not poly: continue
            poly_galvo = []
            for pt in poly:
                gx, gy = self.galvo_config.apply_transform(pt[0] + shift_x, pt[1] + shift_y)
                poly_galvo.append((gx, gy))
                
            # Deduplicate identical overlapping paths (e.g. SVG Fill + Stroke exports)
            # Round to nearest integer (galvo units) for robust hashing
            poly_key = tuple((int(round(pt[0])), int(round(pt[1]))) for pt in poly_galvo)
            poly_key_rev = tuple(reversed(poly_key))
            
            if poly_key not in seen_polys and poly_key_rev not in seen_polys:
                seen_polys.add(poly_key)
                all_polys_galvo.append(poly_galvo)
            
        for poly_galvo in all_polys_galvo:
            if mark_contour:
                self.planner.add_jump(poly_galvo[0][0], poly_galvo[0][1], speed=jump_speed)
                for pt in poly_galvo[1:]:
                    self.planner.add_mark(pt[0], pt[1], speed=mark_speed)
                
        if is_hatch and hatch_configs:
            self.planner.generate_hatch(
                all_polys_galvo, 
                hatch_configs,
                mark_speed=mark_speed, 
                jump_speed=jump_speed,
                galvo_units_per_mm=galvo_units_per_mm
            )
            
        if not is_hatch or not hatch_configs:
            self.planner.optimize_path()
            
        self.planner.commit_to_send_queue()
        
        # Dump the galvo commands to a text file for user inspection
        try:
            import os
            dump_path = os.path.join(os.path.dirname(__file__), "config", "galvo_output.txt")
            with open(dump_path, "w") as f:
                f.write("; Galvo Command Execution Queue\n")
                f.write(f"; Total Commands: {len(self.planner.send_queue)}\n")
                f.write(f"; Field Size: {self.galvo_config.field_size}mm\n\n")
                for cmd in self.planner.send_queue:
                    ctype = cmd.get('type')
                    if ctype == 'jump':
                        f.write(f"JUMP X:{cmd.get('x')} Y:{cmd.get('y')} SPEED:{cmd.get('speed')}\n")
                    elif ctype == 'mark':
                        f.write(f"MARK X:{cmd.get('x')} Y:{cmd.get('y')} SPEED:{cmd.get('speed')}\n")
                    elif ctype == 'delay':
                        f.write(f"DELAY {cmd.get('ms')}ms\n")
                    elif ctype == 'laser_on':
                        f.write("LASER ON\n")
                    elif ctype == 'laser_off':
                        f.write("LASER OFF\n")
                    elif ctype == 'pass_change':
                        f.write(f"\n; --- STARTING HATCH/PASS {cmd.get('idx')} ---\n")
                    else:
                        f.write(f"{ctype.upper()} {cmd}\n")
        except Exception as e:
            self.util.debugPrint(f"Failed to write galvo_output.txt: {e}")

        if hasattr(self, "galvo_preview"):
            self.galvo_preview.draw_queue(self.planner.preview_queue)
        self.update_galvo_preview_bounds()
        return True

    def printGalvoAction(self, widget, *args):
        action = self.wh.getRole(widget)
        self.util.debugPrint(f"printGalvoAction : {action}")
        if action == "redlightpre":
            if not getattr(self, "galvo_preview_active", False):
                if not self.galvo_controller.is_connected:
                    self.showAutoCloseMessage("Hardware Disconnected", "Ensure hardware is connected before starting.")
                    return
                if not self.verify_hardware_connection():
                    return
                    
                # Regenerate queue with current UI settings (start pos, scale, etc.) before previewing
                self._apply_galvo_settings()
                
                if not self.planner.send_queue:
                    self.showAutoCloseMessage("Empty Queue", "Load a pattern first.")
                    return
                min_x, max_x, min_y, max_y = float('inf'), float('-inf'), float('inf'), float('-inf')
                for cmd in self.planner.send_queue:
                    if 'x' in cmd and 'y' in cmd:
                        min_x = min(min_x, cmd['x'])
                        max_x = max(max_x, cmd['x'])
                        min_y = min(min_y, cmd['y'])
                        max_y = max(max_y, cmd['y'])
                if min_x == float('inf'): return
                
                self.wh.invokeMethod(self.printgalvo_widgets.printrungalvo, "disable")
                self.galvo_preview_thread = PreviewThread(self.galvo_controller, min_x, max_x, min_y, max_y)
                self.galvo_preview_thread.finished_signal.connect(self.on_galvo_preview_finished)
                self.galvo_preview_thread.start()
                self.galvo_preview_active = True
                self.ui.redlightprePushButton.setText("STOP")
            else:
                if self.galvo_preview_thread:
                    self.galvo_preview_thread.running = False
                    self.galvo_preview_thread.wait()
                    self.galvo_preview_thread = None
                if self.galvo_controller.connection:
                    if hasattr(self.galvo_controller.connection, 'reddot_off'):
                        self.galvo_controller.connection.reddot_off()
                    if hasattr(self.galvo_controller.connection, 'laser_off'):
                        self.galvo_controller.connection.laser_off()
                    if hasattr(self.galvo_controller.connection, 'stop'):
                        self.galvo_controller.connection.stop()
                self.wh.invokeMethod(self.printgalvo_widgets.printrungalvo, "enable")
                self.galvo_preview_active = False
                self.ui.redlightprePushButton.setText("START")

        elif action in ["powersetgalvo", "freqsetgalvo"]:
            if not self.galvo_controller.is_connected:
                self.showAutoCloseMessage("Hardware Disconnected", "Ensure hardware is connected before setting power or frequency.")
                return
            
            try:
                # Read slider values
                slider_percentage = float(self.ui.galvolaserpowerHorizontalSlider_2.value())
                # Use direct power value
                slider_value = slider_percentage
                
                freq_val = float(self.ui.galvolaserfreqHorizontalSlider.value())
                
                # Default settings for Analog/PWM out
                max_val = 100.0
                bit = 0 # Default bit mapping
                
                # Check if hardware connection supports setting the bit directly
                if hasattr(self.galvo_controller, "connection") and hasattr(self.galvo_controller.connection, "set_analog_do_bit"):
                    # The PWM pin responds to bit=0. We'll test bits 0, 1, and 2 to see which controls the Analog pin.
                    for test_bit in [0, 1, 2]:
                        self.galvo_controller.connection.set_analog_do_bit(max_val, slider_value, freq_val, test_bit)
                    
                    if action == "powersetgalvo":
                        self.showAutoCloseMessage("Power Set", f"Laser power set to {slider_percentage}%")
                    elif action == "freqsetgalvo":
                        self.showAutoCloseMessage("Frequency Set", f"Frequency set to {freq_val}kHz")
                else:
                    self.showAutoCloseMessage("Error", "Hardware connection does not support setting analog power.")
            except Exception as e:
                self.showAutoCloseMessage("Error", f"Failed to set power/frequency: {e}")

        elif action == "printrungalvo":
            if not self.galvo_controller.is_connected:
                self.showAutoCloseMessage("Hardware Disconnected", "Ensure hardware is connected before starting.")
                return
            if not self.verify_hardware_connection():
                return
            if not self.planner.send_queue:
                self.showAutoCloseMessage("Empty Queue", "Load a pattern first.")
                return
                
            try:
                focus_z_str = self.ch.getValues("focus", "galvo_z_focus")
                if focus_z_str:
                    from PySide6.QtWidgets import QApplication
                    focus_z = float(focus_z_str)
                    
                    try:
                        galvoobjheight = float(self.ui.galvoobjheightLineEdit.text() or 0.0)
                    except ValueError:
                        galvoobjheight = 0.0
                        
                    finalobjectfocus = focus_z + galvoobjheight
                    
                    try:
                        galvosampleheight = float(self.ui.pgmheightgalvoLineEdit.text() or 0.0)
                    except ValueError:
                        galvosampleheight = 0.0
                        
                    finalgalvofocus = finalobjectfocus - galvosampleheight
                    
                    self.ch.addParameter("focus", "galvoobjheight", f"{galvoobjheight:.2f}")
                    self.ch.addParameter("focus", "finalobjectfocus", f"{finalobjectfocus:.2f}")
                    self.ch.addParameter("focus", "galvosampleheight", f"{galvosampleheight:.2f}")
                    self.ch.addParameter("focus", "finalgalvofocus", f"{finalgalvofocus:.2f}")
                    if hasattr(self, 'config_file_path'):
                        self.ch.updateFile(self.config_file_path)

                    print(f"Moving Z axis to focus position: {finalgalvofocus:.2f} mm (Base: {focus_z}, ObjHeight: {galvoobjheight}, SampleHeight: {galvosampleheight})")
                    self.stepper_controller.move_z_absolute(finalgalvofocus)
                    self.ah.pos("Z", self.stepper_controller.z_position)
                    self.jogPosDisplay()
                    self.focusPosDisplay()
                    import time
                    while time.time() < getattr(self.stepper_controller, 'next_ready_time', time.time()):
                        QApplication.instance().processEvents()
                        time.sleep(0.05)
            except Exception as e:
                print(f"Failed to move Z axis to focus position: {e}")

            try:
                loop_count = int(self.wh.invokeMethod(self.programgalvo_widgets.pgmloopcount, "get") or 1)
            except:
                loop_count = 1
                
            self.wh.invokeMethod(widget, "disable")
            self.wh.invokeMethod(self.printgalvo_widgets.printabortgalvo, "enable")
            self.wh.invokeMethod(self.printgalvo_widgets.redlightpre, "disable")
            
            self.galvo_exec_thread = ExecutionThread(self.galvo_controller, self.planner.send_queue, loop_count)
            self.galvo_exec_thread.finished_signal.connect(self.on_galvo_execution_finished)
            self.galvo_exec_thread.progress_signal.connect(self.on_galvo_execution_progress)
            
            if hasattr(self, "galvo_preview"):
                self.galvo_preview.reset_progress()
                
            if hasattr(self.ui, 'printgalvoProgressBar'):
                self.ui.printgalvoProgressBar.setValue(0)
            if hasattr(self.ui, 'progressLabel_2'):
                self.ui.progressLabel_2.setText("0%")
                
            self.galvo_exec_thread.start()

        elif action == "printabortgalvo":
            if hasattr(self, "galvo_exec_thread") and self.galvo_exec_thread.isRunning():
                self.wh.invokeMethod(widget, "disable")
                self.galvo_exec_thread.abort()
                
            self.showMainPages("programsgalvo")
            
            if hasattr(self.ui, 'printgalvoProgressBar'):
                self.ui.printgalvoProgressBar.setValue(0)
            if hasattr(self.ui, 'progressLabel_2'):
                self.ui.progressLabel_2.setText("0%")
                
            self.planner.clear()
            if hasattr(self, "galvo_preview"):
                self.galvo_preview.draw_queue([])

    def on_galvo_execution_progress(self, idx, total, x, y, ctype):
        if ctype and str(ctype).startswith("pass_change:"):
            try:
                self._current_printing_pass = int(ctype.split(":")[1])
            except:
                pass
            return
            
        pct = int(((idx + 1) / total) * 100) if total > 0 else 0
        if hasattr(self.ui, 'printgalvoProgressBar'):
            self.ui.printgalvoProgressBar.setValue(pct)
            
        if hasattr(self.ui, 'progressLabel_2'):
            pass_str = ""
            if hasattr(self, "_current_printing_pass"):
                active_hatches = 0
                if hasattr(self, 'hatch_profiles'):
                    active_hatches = sum(1 for p in self.hatch_profiles.values() if p.get('enable', False))
                
                if active_hatches > 1:
                    pass_str = f"Hatch {self._current_printing_pass} | "
            self.ui.progressLabel_2.setText(f"{pass_str}{pct}%")
            
        if hasattr(self, "galvo_preview"):
            self.galvo_preview.update_progress(idx, x, y, ctype)

    def on_galvo_execution_finished(self, success):
        self.wh.invokeMethod(self.printgalvo_widgets.printrungalvo, "enable")
        self.wh.invokeMethod(self.printgalvo_widgets.printabortgalvo, "disable")
        self.wh.invokeMethod(self.printgalvo_widgets.redlightpre, "enable")
        
        is_disconnected = False
        if self.galvo_controller.connection and hasattr(self.galvo_controller.connection, 'is_physically_connected'):
            if not self.galvo_controller.connection.is_physically_connected():
                is_disconnected = True
                
        if success:
            self.showAutoCloseMessage("Success", "Galvo execution complete.")
        else:
            if is_disconnected:
                self.showAutoCloseMessage("Hardware Disconnected", "USB removed. Aborting and disconnecting. Please restart the UI when card is connected again.")
                self.galvo_has_disconnected = True
                
                # Auto disconnect
                self.galvo_controller.disconnect()
                self.ui.titleLabel.setText("Patterning Machine (Demo Mode)")

                self.ui.mainconnectgalvoPushButton.setEnabled(True)
                self.ui.maindisconnectgalvoPushButton.setEnabled(False)
                
                # Open the center menu for COM settings
                if hasattr(self, 'center_menu_widgets') and hasattr(self.center_menu_widgets, 'com'):
                    self.centerMenuAction(self.center_menu_widgets.com)
            else:
                self.showAutoCloseMessage("Status", "Galvo execution failed or aborted.")
                
            if hasattr(self.ui, 'printgalvoProgressBar'):
                self.ui.printgalvoProgressBar.setValue(0)
            if hasattr(self.ui, 'progressLabel_2'):
                self.ui.progressLabel_2.setText("0%")

    def on_galvo_preview_finished(self, success):
        if not success:
            self.galvo_preview_active = False
            self.ui.redlightprePushButton.setText("START")
            self.on_galvo_execution_finished(False)

    def verify_hardware_connection(self):
        """Checks if hardware is physically connected, and triggers disconnect if not."""
        if not self.galvo_controller.is_connected:
            return False
            
        if self.galvo_controller.connection and hasattr(self.galvo_controller.connection, 'is_physically_connected'):
            if not self.galvo_controller.connection.is_physically_connected():
                self.showAutoCloseMessage("Hardware Disconnected", "USB removed. Aborting and disconnecting. Please restart the UI when card is connected again.")
                self.galvo_has_disconnected = True
                
                # Auto disconnect
                self.galvo_controller.disconnect()
                self.ui.titleLabel.setText("Patterning Machine (Demo Mode)")

                self.ui.mainconnectgalvoPushButton.setEnabled(True)
                self.ui.maindisconnectgalvoPushButton.setEnabled(False)
                
                # Open the center menu for COM settings
                if hasattr(self, 'center_menu_widgets') and hasattr(self.center_menu_widgets, 'com'):
                    self.centerMenuAction(self.center_menu_widgets.com)
                return False
        return True

    def configGalvoAction(self, widget, *args):
        action = self.wh.getRole(widget)
        self.util.debugPrint(f"configGalvoAction : {action}")
        
        if getattr(self, "_loading_config_galvo", False):
            return
            
        if action in ["confscalegalvo1btn", "confscalegalvo2btn"]:
            from notifier_ui import NotifierUI
            
            # Use the native slide-in UI for inputs
            results = NotifierUI.showInputPopup(self, "Calculate Scale", ["Desired Marking Size:", "Actual Mark Size:"])
            
            if results and len(results) == 2:
                try:
                    desired = float(results[0])
                    actual = float(results[1])
                    if actual != 0:
                        scale_widget = self.configgalvo_widgets.confscalegalvo1 if action == "confscalegalvo1btn" else self.configgalvo_widgets.confscalegalvo2
                        current_scale = float(self.wh.invokeMethod(scale_widget, "get") or "100.0")
                        new_scale = current_scale * (desired / actual)
                        self.wh.invokeMethod(scale_widget, "set", f"{new_scale:.4f}")
                        
                        if hasattr(self.ui, 'confapplyPushButton'): self.ui.confapplyPushButton.setEnabled(True)
                except ValueError:
                    pass
            return
            
        if action in ["confapply", "confok", "confcancel"]:
            if action in ["confapply", "confok"]:
                # Save all to config
                def _save(key, val): self.ch.addParameter("GalvoField", key, str(val))
                
                _save("field_size", self.wh.invokeMethod(self.configgalvo_widgets.fieldsizeconf, "get"))
                _save("offset_x", self.wh.invokeMethod(self.configgalvo_widgets.offxconf, "get"))
                _save("offset_y", self.wh.invokeMethod(self.configgalvo_widgets.offyconf, "get"))
                _save("angle", self.wh.invokeMethod(self.configgalvo_widgets.angleconf, "get"))
                
                if hasattr(self.ui, 'galvo1confRadioButton'): _save("galvo1_x", self.ui.galvo1confRadioButton.isChecked())
                elif hasattr(self.ui, 'galvo1confCheckBox'): _save("galvo1_x", self.ui.galvo1confCheckBox.isChecked())
                
                _save("g1_negate", getattr(self.ui, 'neggalvo1confCheckBox').isChecked() if hasattr(self.ui, 'neggalvo1confCheckBox') else False)
                _save("g1_scale", self.wh.invokeMethod(self.configgalvo_widgets.confscalegalvo1, "get"))
                _save("g1_barrel", self.wh.invokeMethod(self.configgalvo_widgets.confbargalvo1, "get"))
                _save("g1_par", self.wh.invokeMethod(self.configgalvo_widgets.confpargalvo1, "get"))
                _save("g1_trapezoid", self.wh.invokeMethod(self.configgalvo_widgets.conftrapgalvo1, "get"))
                
                _save("g2_negate", getattr(self.ui, 'neggalvo2confCheckBox').isChecked() if hasattr(self.ui, 'neggalvo2confCheckBox') else False)
                _save("g2_scale", self.wh.invokeMethod(self.configgalvo_widgets.confscalegalvo2, "get"))
                _save("g2_barrel", self.wh.invokeMethod(self.configgalvo_widgets.confbargalvo2, "get"))
                _save("g2_par", self.wh.invokeMethod(self.configgalvo_widgets.confpargalvo2, "get"))
                _save("g2_trapezoid", self.wh.invokeMethod(self.configgalvo_widgets.conftrapgalvo2, "get"))
                
                # Find checked radio/checkbox
                radios = ["confnomov", "confgalvocent", "conftopleft", "conftopright", "confbotright", "confbotleft", "confspecpos"]
                for r in radios:
                    if hasattr(self.ui, f"{r}RadioButton") and getattr(self.ui, f"{r}RadioButton").isChecked():
                        _save("pos_after_mark", f"{r}RadioButton")
                        break
                    elif hasattr(self.ui, f"{r}CheckBox") and getattr(self.ui, f"{r}CheckBox").isChecked():
                        _save("pos_after_mark", f"{r}CheckBox")
                        break
                        
                _save("sp_x", self.wh.invokeMethod(self.configgalvo_widgets.confxmark, "get"))
                _save("sp_y", self.wh.invokeMethod(self.configgalvo_widgets.confymark, "get"))
                
                if hasattr(self, 'config_file_path'): self.ch.updateFile(self.config_file_path)
                
                # Dynamically sync to the galvo_config engine and update preview
                self._apply_galvo_config_to_core()
                self._apply_galvo_settings()
                
                # Show success popup
                self.showAutoCloseMessage("Settings Saved", "Galvo configurations have been applied successfully.", timeout_ms=2000)
                
            if action in ["confapply", "confok", "confcancel"]:
                self.showMainPages("printgalvo")
                if hasattr(self.ui, 'confapplyPushButton'): self.ui.confapplyPushButton.setEnabled(False)
        else:
            if hasattr(self.ui, 'confapplyPushButton'): self.ui.confapplyPushButton.setEnabled(True)
            is_special = False
            if hasattr(self.ui, 'confspecposRadioButton'): is_special = self.ui.confspecposRadioButton.isChecked()
            elif hasattr(self.ui, 'confspecposCheckBox'): is_special = self.ui.confspecposCheckBox.isChecked()
            
            if hasattr(self.ui, 'confxmarkLineEdit'): self.ui.confxmarkLineEdit.setEnabled(is_special)
            if hasattr(self.ui, 'confymarkLineEdit'): self.ui.confymarkLineEdit.setEnabled(is_special)

    def jogAction(self, widget, *args):
        action = self.wh.getRole(widget)
        
        # Handle Travel Radio Buttons
        if "travel" in action:
            # Parse value from role e.g. "travel100" -> 100, "travel1" -> 1
            try:
                val = float(action.replace("travel", ""))
                # Special cases if naming is weird, but main.py has roles: 
                # travel100 (100?), travel50, travel10, travel1
                # m.py mapping: travel100 -> 10, travel50 -> 5, travel10 -> 1, travel1 -> 0.1
                # Parsing logic in main.py axisTravel used /10. 
                # Let's align with m.py behavior:
                if val == 100: self.travel = 10.0
                elif val == 50: self.travel = 5.0
                elif val == 10: self.travel = 1.0
                elif val == 1: self.travel = 0.1
                else: self.travel = val
            except:
                pass
            
            self.util.debugPrint(f"Travel set to: {self.travel}")

        # Handle Moves
        result = self.util.checkSubString(action, "home", "center", "plus", "minus")
        if result.found:
            # Z+ Safety
            if action == "zplus" and not self.canMoveZPlus(self.travel):
                return
            self.axisMotion(action, mode="jog")
 
        
    def focusAction(self, widget, *args):
        action = self.wh.getRole(widget)
        
        if action == "flaser":
             # Read selection first, then decide what to enable
             laser_name = self.wh.invokeMethod(self.focus_widgets.flaser, "get")
             self.laser_name = laser_name.strip() if laser_name else None

             if self.laser_name:
                  # Valid laser selected — enable controls
                  self.wh.invokeMethod(self.focus_widgets.fplus, "enable")
                  self.wh.invokeMethod(self.focus_widgets.fminus, "enable")
                  self.wh.invokeMethod(self.focus_widgets.flaserset, "enable")
                  self.wh.invokeMethod(self.focus_widgets.ftravel, "enable")
                  self.wh.invokeMethod(self.focus_widgets.flaserset, "set", "ON") # Button says ON (ready to turn ON)
                  self.wh.invokeMethod(self.focus_widgets.fset, "disable") # Lock Set Focus until turned ON
                  # Ensure laser is OFF when switching
                  laser = self.lh.getLaser(self.laser_name)
                  if laser:
                       self.sendGcode(laser.cmd.get("OFF"))
             else:
                  # Blank / invalid — disable all controls
                  self.wh.invokeMethod(self.focus_widgets.fplus, "disable")
                  self.wh.invokeMethod(self.focus_widgets.fminus, "disable")
                  self.wh.invokeMethod(self.focus_widgets.flaserset, "disable")
                  self.wh.invokeMethod(self.focus_widgets.ftravel, "disable")
                  self.wh.invokeMethod(self.focus_widgets.fset, "disable")

        if action == "objheight":
             height = self.wh.invokeMethod(self.focus_widgets.objheight, "get")
             if height:
                 try:
                     height_val = float(height)
                     # Save objheight under focus section
                     self.ch.addParameter("focus", "objheight", str(height_val))
                     self.ch.updateFile(self.config_file_path)
                     self.util.debugPrint(f"Saved Object Height: {height_val}")
                     self.showAutoCloseMessage("Settings Saved", f"Object Height: {height_val} mm", timeout_ms=3000)
                 except ValueError:
                     self.showAutoCloseMessage("Invalid Input", "Enter a valid number for Object Height.", timeout_ms=3000)

        if action == "flaserset": # Button to toggle ON/OFF
             current_text = self.wh.invokeMethod(widget, "get")
             new_text = "OFF" if current_text == "ON" else "ON"
             self.wh.invokeMethod(widget, "set", new_text)
             
             laser = self.lh.getLaser(self.laser_name)
             if laser:
                  # If button was "ON", user clicked to turn laser ON
                  cmd_key = "ON" if current_text == "ON" else "OFF"
                  cmd = laser.cmd.get(cmd_key)
                  self.sendGcode(cmd)
                  
                  if new_text == "OFF": # Laser is now ON
                       self.wh.invokeMethod(self.focus_widgets.fset, "enable")
                  else: # Laser is now OFF
                       self.wh.invokeMethod(self.focus_widgets.fset, "disable")

        if action == "fset":
             self.shutdownLaser(name=self.laser_name)

             zpos = self.ah.getAxis("Z").pos
             
             # Read objheight
             height_str = self.wh.invokeMethod(self.focus_widgets.objheight, "get")
             try:
                 objheight = float(height_str) if height_str else 0.0
             except ValueError:
                 objheight = 0.0

             final_focus = round(float(zpos) + objheight, 3)

             self.lh.focus(self.laser_name, final_focus)

             # Config Save
             self.ch.addParameter("focus", self.laser_name, f"{{'{self.laser_name}': {final_focus}}}") # Format matching m.py
             self.ch.updateFile(self.config_file_path)

             # Reset and lock all focus controls — user must re-select laser to continue
             self.wh.invokeMethod(self.focus_widgets.flaserset, "set", "ON")
             self.wh.invokeMethod(self.focus_widgets.flaserset, "disable")
             self.wh.invokeMethod(self.focus_widgets.fplus, "disable")
             self.wh.invokeMethod(self.focus_widgets.fminus, "disable")
             self.wh.invokeMethod(self.focus_widgets.ftravel, "disable")
             self.wh.invokeMethod(self.focus_widgets.fset, "disable")

        if action == "ftravel":
             current_text = self.wh.invokeMethod(widget, "get")
             if current_text == "1":
                 new_text = "0.1"
             elif current_text == "0.1":
                 new_text = "0.01"
             else:
                 new_text = "1"
             self.wh.invokeMethod(widget, "set", new_text)

        if action in ["fplus", "fminus"]:
             # Map fplus/fminus to zplus/zminus but logic is axisMotion
             # m.py checks "plus", "minus" substring.
             
             # Read current focus travel
             travel_text = self.wh.invokeMethod(self.focus_widgets.ftravel, "get")
             try:
                 f_travel = float(travel_text)
             except (ValueError, TypeError):
                 f_travel = 1.0
             
             orig_travel = self.travel
             self.travel = f_travel
             
             dir_map = {"fplus": "zplus", "fminus": "zminus"}
             cmd = dir_map.get(action)
             
             if cmd == "zplus" and not self.canMoveZPlus(f_travel):
                 self.travel = orig_travel
                 return
                 
             self.axisMotion(cmd, mode="laser")
             
             self.travel = orig_travel

        
    def offsetAction(self, widget, *args):
        self.wh.getInfo(widget)     
        action = self.wh.getRole(widget)
        
             
        if action == "offlaser":
             # ComboBox role
             laser_name = self.wh.invokeMethod(self.offset_widgets.offlaser, "get")
             self.offset_laser_name = laser_name
             self.wh.invokeMethod(self.offset_widgets.offlaserset, "enable")

        if action == "offlaserset": # The ON/OFF button
             current_text = self.wh.invokeMethod(widget, "get")
             new_text = "OFF" if current_text == "ON" else "ON"
             self.wh.invokeMethod(widget, "set", new_text)
             
             laser = self.lh.getLaser(self.offset_laser_name)
             if laser:
                  cmd_key = "ON" if current_text == "ON" else "OFF"

                  if cmd_key == "ON":
                       # Move Z to this laser's calibrated focus height
                       focus = laser.focus
                       if focus is not None:
                           self.sendGcode("G90")  # absolute mode before Z move
                           gstr = f"G1 F{self.jogfeed} Z{focus}"
                           self.sendGcode(gstr)

                       # Button visibility:
                       # - ZERO only enabled before first zero (zero_flag=False)
                       # - OFFSET only enabled after zero has been set (zero_flag=True)
                       if not self.zero_flag:
                           self.wh.invokeMethod(self.offset_widgets.offzero, "enable")
                           self.wh.invokeMethod(self.offset_widgets.offset, "disable")
                       else:
                           self.wh.invokeMethod(self.offset_widgets.offzero, "disable")
                           self.wh.invokeMethod(self.offset_widgets.offset, "enable")

                  cmd = laser.cmd.get(cmd_key)
                  self.sendGcode(cmd)

        if action == "offzero":
             self.zero_laser = self.wh.invokeMethod(self.offset_widgets.offlaser, "get")
             self.shutdownLaser(name=self.zero_laser)
             self.wh.invokeMethod(self.offset_widgets.offlaserset, "set", "ON")

             self.wh.invokeMethod(self.offset_widgets.offzero, "disable")
             self.wh.invokeMethod(self.offset_widgets.offset, "enable")

             self.xtemp = self.ah.getAxis("X").pos
             self.ytemp = self.ah.getAxis("Y").pos
             
             self.zero_flag = True

             self.lh.xpos(self.zero_laser, float(self.xtemp))
             self.lh.ypos(self.zero_laser, float(self.ytemp))
             self.logger.critical(f"{self.zero_laser} : Set as Zero reference")

             # Save zero laser to config so it persists after restart
             self.ch.addParameter("zero", "laser", self.zero_laser)
             self.ch.updateFile(self.config_file_path)

             # Auto-switch dropdown to the other laser (ready for offset step)
             next_list = [l for l in self.laser_data_list if l.strip() and l.strip() != self.zero_laser]
             if next_list:
                  next_laser = next_list[0]
                  self.wh.invokeMethod(self.offset_widgets.offlaser, "set", next_laser)
                  self.offset_laser_name = next_laser

        if action == "travel":
            travel_list = [10, 5, 1, 0.1]
            # Assumes self.travel_index exists or creates it
            if not hasattr(self, "travel_index"):
                 self.travel_index = 0
            
            if self.travel_index < len(travel_list) - 1:
                self.travel_index += 1
            else:
                self.travel_index = 0
                
            val = travel_list[self.travel_index]
            self.wh.invokeMethod(self.offset_widgets.travel, "set", str(val))
            self.travel = val

        if action in ["offxplus", "offxminus", "offyplus", "offyminus"]:
             cmd_map = {
                 "offxplus": "xplus", "offxminus": "xminus",
                 "offyplus": "yplus", "offyminus": "yminus"
             }
             axis_cmd = cmd_map.get(action)

             # Read travel from the offset travel button (its own independent travel)
             # NOT from self.travel which is shared with the jog page
             travel_str = self.wh.invokeMethod(self.offset_widgets.travel, "get")
             try:
                 self.travel = float(travel_str)
             except (ValueError, TypeError):
                 self.travel = 10.0  # fallback to offset default

             self.axisMotion(axis_cmd, mode="laser")

        if action == "offset": # Set Offset
             self.offset_laser = self.wh.invokeMethod(self.offset_widgets.offlaser, "get")
             self.shutdownLaser(name=self.offset_laser)
             self.wh.invokeMethod(self.offset_widgets.offlaserset, "set", "ON") # Reset ON/OFF btn
             
             self.wh.invokeMethod(self.offset_widgets.offset, "disable")

             if not hasattr(self, "xtemp"): self.xtemp = 0
             if not hasattr(self, "ytemp"): self.ytemp = 0

             xoffset = self.ah.getAxis("X").pos - self.xtemp
             yoffset = self.ah.getAxis("Y").pos - self.ytemp
             
             self.lh.xpos(self.offset_laser, float(xoffset))
             self.lh.ypos(self.offset_laser, float(yoffset))
             
             self.ch.addParameter("offset", "laser", self.offset_laser)
             self.ch.addParameter("offset", "xoffset", str(float(xoffset)))
             self.ch.addParameter("offset", "yoffset", str(float(yoffset)))
             self.ch.updateFile(self.config_file_path)
             
             self.zero_flag = False
             

        
    def programAction(self, widget, *args):
        self.wh.getInfo(widget) 
        action = self.wh.getRole(widget)
        
        # ---------------------------------------------------------
        # 1. FILE SELECTION
        # ---------------------------------------------------------
        if action == "pgmfileset":
            self.pgm_file, _ = QFileDialog.getOpenFileName(self, "Select DXF File", "", "DXF Files (*.dxf)")
            
            if self.pgm_file:                
                self.wh.invokeMethod(self.program_widgets.pgmfile, "set", os.path.basename(self.pgm_file))
                self.logger.info(f"DXF file selected : {self.pgm_file}")

                # --- CLEANUP ORPHANED JSON FILES ---
                dxf_dir = os.path.dirname(self.pgm_file)
                self.fh.cleanupOrphanedParams(dxf_dir)

                # --- AUTO FETCH PARAMETERS ---
                params = self.fh.loadDxfParams(self.pgm_file)
                if params:
                    self.util.debugPrint(f"Fetched parameters for DXF: {params}")
                    
                    # Check for nested structure "Program page parameters"
                    nested_params = params.get("Program page parameters")
                    if isinstance(nested_params, dict):
                        data = nested_params
                    else:
                        data = params # fallback to flat structure
                    
                    # Use both old and new keys for backward compatibility
                    height = data.get("Sample Height") or data.get("height")
                    if height is not None:
                        self.wh.invokeMethod(self.program_widgets.pgmheight, "set", str(height))
                        self.pgm_height = float(height)
                        
                    feed = data.get("Feed") or data.get("feed")
                    if feed is not None:
                        self.wh.invokeMethod(self.program_widgets.pgmfeed, "set", str(feed))
                        self.pgm_feed = float(feed)
                        
                    laser = data.get("Selected Laser") or data.get("laser")
                    if laser is not None:
                        self.wh.invokeMethod(self.program_widgets.pgmlaser, "set", laser)
                        self.pgm_laser = laser
                    
                    self.showAutoCloseMessage("Parameters Fetched", "Previous parameters for this DXF have been loaded.", timeout_ms=3000)

                self.onPgmDataChanged()

        # ---------------------------------------------------------
        # 5. SAVE / PROCESS
        # ---------------------------------------------------------
        if action == "pgmsaveset":
            # --- VALIDATION START ---
            ui_height = self.wh.invokeMethod(self.program_widgets.pgmheight, "get")
            ui_feed = self.wh.invokeMethod(self.program_widgets.pgmfeed, "get")
            ui_laser = self.wh.invokeMethod(self.program_widgets.pgmlaser, "get")

            try:
                self.pgm_height = float(ui_height)
                self.pgm_feed = float(ui_feed)
            except ValueError:
                 self.showAutoCloseMessage("Input Error", "Please enter valid numeric values for Height and Feed.")
                 return

            if not ui_laser or ui_laser.strip() == "" or ui_laser == "Select Laser":
                self.showAutoCloseMessage("Input Error", "Please select a valid Laser.")
                return

            self.pgm_laser = ui_laser
            # --- VALIDATION END ---

            laser = self.lh.getLaser(self.pgm_laser)
            self.focus = laser.focus
            zpos = self.focus - self.pgm_height

            s_file = f"DXF File : {self.pgm_file}"
            s_height = f"Sample Height : {self.pgm_height} mm"
            s_focus = f"Laser Focus : {self.focus} mm"
            s_zpos = f"Z Travel : {zpos} mm"
            s_laser = f"Selected LASER : {self.pgm_laser}"

            for s in [s_file, s_height, s_focus, s_zpos, s_laser]:
                self.util.debugPrint(s)
                self.logger.info(s)

            # DXF parser
            dxfparser = DXFParser(self.pgm_file)
            # Use new bed definition (P1–P4) as per user request
            dxfparser.setBedCorners((0, 0), (300, 0), (300, 300), (0, 300))
            dxfparser.setZvalue(zpos)
            if self.pgm_feed:
                dxfparser.setFeedRate(self.pgm_feed)

            # Apply offsets
            if self.pgm_laser == self.offset_laser:
                laser = self.lh.getLaser(self.offset_laser)
                self.logger.info(f"{self.offset_laser} : has offset, Xoffset : {laser.xpos} mm Yoffset : {laser.ypos} mm")
                dxfparser.setIndex(self.xindex + laser.xpos, self.yindex + laser.ypos)

            if self.pgm_laser == self.zero_laser:
                self.logger.info(f"{self.zero_laser} : is set as reference")
                dxfparser.setIndex(self.xindex, self.yindex)

            # Generate and archive G-code
            self.pgm_glist = dxfparser.generateGcode()
            self.master_glist = list(self.pgm_glist)

            try:
                output_path = self.config_dir_path / "final_output.gcode"
                with open(output_path, 'w') as f:
                    for line in self.pgm_glist:
                        f.write(line + "\n")
                self.logger.info(f"G-code saved to: {output_path}")
                self.util.debugPrint(f"G-code saved to: {output_path}")
            except Exception as e:
                self.logger.error(f"Failed to save G-code: {e}")

            self.pgm_mlist = [gcode for gcode in self.pgm_glist if self.gh.isMotion(gcode)]
            
            # Added debug prints as per user request
            self.util.debugPrint(f"segment dict : {self.preview.segment_dict}")
            self.util.debugPrint(f"motion gcode : {self.pgm_mlist}")
            self.util.debugPrint(f"motion gcode len : {len(self.pgm_mlist)}")
            self.util.debugPrint(f"gcode : {self.pgm_glist}")
            self.util.debugPrint(f"gcode : {self.pgm_glist}")
            
            self.preview.loadGcode(self.pgm_glist)
            
            # --- AUTO SAVE PARAMETERS ---
            params = {
                "Program page parameters": {
                    "Sample Height": self.pgm_height,
                    "Feed": self.pgm_feed,
                    "Selected Laser": self.pgm_laser
                }
            }
            if self.fh.saveDxfParams(self.pgm_file, params):
                self.util.debugPrint(f"Saved parameters for DXF: {params}")
                self.logger.info(f"Parameters saved for {self.pgm_file}")

            # Disable Inspect until printing is done
            self.wh.invokeMethod(self.print_widgets.printinspect, "disable")
            self.showMainPages("print")

    def onPgmDataChanged(self, *args):
        self.wh.invokeMethod(self.program_widgets.pgmsaveset, "disable")
        
        if not getattr(self, "pgm_file", None):
            return
            
        ui_height = self.wh.invokeMethod(self.program_widgets.pgmheight, "get")
        ui_feed = self.wh.invokeMethod(self.program_widgets.pgmfeed, "get")
        ui_laser = self.wh.invokeMethod(self.program_widgets.pgmlaser, "get")
        
        try:
            float(ui_height)
            float(ui_feed)
        except (ValueError, TypeError):
            return
            
        if not ui_laser or str(ui_laser).strip() == "" or str(ui_laser) == "Select Laser":
            return
            
        # If we pass all validation checks, enable the Save button
        self.wh.invokeMethod(self.program_widgets.pgmsaveset, "enable")

                
    def printAction(self, widget, *args):
        self.wh.getInfo(widget) 
        action = self.wh.getRole(widget)
        
        if action == "printrun":
            if self.pgm_file:
                # Restore full G-code
                if hasattr(self, 'master_glist') and self.master_glist:
                    self.pgm_glist = list(self.master_glist)
                
                # Turn OFF Camera Jog before starting print
                btn_opt = getattr(self.ui, "cameraoffsetPushButton", None)
                if btn_opt and "OFF" in btn_opt.text().upper():
                    self.toggleCameraJog()
                    
                self.runProgram("run")

                self.wh.invokeMethod(self.print_widgets.printrun, "disable")
                self.wh.invokeMethod(self.print_widgets.printpause, "enable")
                self.wh.invokeMethod(self.print_widgets.printabort, "enable")
                self.wh.invokeMethod(self.print_widgets.printinspect, "disable")

            else:
                reply = self.showCustomPopup("DXF File Error", "DXF file is not selected, Kindly select the dxf file first before run operation", buttons=QMessageBox.Ok)
                if reply == QMessageBox.Ok:
                    self.showMainPages("program")
                    
        if action == "printpause":
            arg = "pause" if not self.pause_flag else "resume"
            self.pause_flag = not self.pause_flag
            self.pauseWidget(widget, arg)
            self.runProgram(arg)
        
        if action == "printabort":
            self.runProgram("abort")
            self.wh.invokeMethod(self.print_widgets.printrun, "enable")

        if action == "printinspect":
            self.runInspection()

        
    def terminalAction(self, widget, event=None):
        # widget = self.sender()
        # self.wh.getInfo(widget)
        if widget:
            self.terminalData(widget)                
        
        if event:
            self.eh.handle(widget, event)
    
    def onKeyEnter(self, widget, event):
        wname = self.wh.getName(widget)
        print(wname, " ENTER pressed")
        
        if self.util.checkSubString(wname, "term"):
            self.terminalData(widget, event.key())
    
    def onKeyUp(self, widget, event):
        wname = self.wh.getName(widget)
        print(wname, " UP pressed")
        
        if self.util.checkSubString(wname, "term"):
            self.terminalData(widget, event.key())
    
    def onKeyDown(self, widget, event):
        wname = self.wh.getName(widget)
        print(wname, " DOWN pressed")
        
        if self.util.checkSubString(wname, "term"):
            self.terminalData(widget, event.key())
        
    def onLoad(self):
        if str(self.galvo_mode).upper() == "ON":
            return
            
        for key in self.sercom_dict:
            self.beginSerial(key, refresh=True)
            self.activateSerial(key, "auto")
            print(f"key : {key}")

        
    def showMainPages(self, page):
        arg = self.main_page_dict.get(page)
        
        # Click the corresponding left menu button to update styles
        button_map = {
            "jog": "home",
            "laser": "laser",
            "program": "programs",
            "print": "print",
            "camera": "camera",
            "terminal": "terminal",
            "joggalvo": "joggalvo",
            "laserconfgalvo": "laserconfgalvo",
            "programsgalvo": "programsgalvo",
            "printgalvo": "printgalvo"
        }
        
        role = button_map.get(page)
        btn = self.left_menu_widgets.get(role) if role else None
        
        if btn:
            btn.click()
        
        else:
            self.wh.invokeMethod(self.main_stack, "set", arg)
            
        self.util.debugPrint(f"index : {arg}")
        self.util.debugPrint(f"arg : {arg}")
        
    def axisTravel(self, arg, mode=None):
        if arg is not None and mode is not None:
            key = arg.replace("_", "")
            value = key.replace("travel", "")
            
            try:
                if mode == "jog":
                    self.travel = float(value) / 10
                
                else:
                    self.travel = float(value)
            
            except ValueError:
                self.travel = 0
                
            setattr(self, f"{mode}_travel", self.travel)

    def axisMotion(self, arg, mode=None):
        if arg is not None:
            # 🔒 Any HOME cancels active program
            if "home" in arg and self.pgm_run_flag:
                self.resetPrintState(reason="home")

            glist = []
            
            if mode == "jog":
                feed = self.jog_feed_val
            elif mode == "camera":
                feed = self.camera_jog_feed
            else:
                feed = self.laser_feed_val
            
            cmd_dict = {"home" : "G28",
                        "linear" : f"G1 F{feed}",
                        "relative" : "G91",
                        "absolute" : "G90",
                        "pos" : "M114"
                        }
            
            dir_dict = {'plus' : '', 'minus' : '-'}
            
            # center_dict logic simplified as main.py uses constants
            # In m.py it uses self.xcenter etc.
             
            # Determine command type
            # arg can be "xhome", "xminus", "xycenter"
            
            # Simple parsing logic based on substrings
            result = self.util.checkSubString(arg, "home", "minus", "plus", "center")
            
            if result.found:
                sub = result.matches[0]
                # Extract axis from role, e.g. "xhome" -> "x"
                axis_part = arg.replace(sub, "")
                
                # HOME Logic
                if sub == "home":
                    base_cmd = cmd_dict.get("home")
                    if "all" in axis_part: # allhome
                        glist.append(base_cmd)
                    else:
                        for char in axis_part: # x, y, z
                            base_cmd += f" {char.upper()}"
                        glist.append(base_cmd)
                
                # MOVE Logic
                if sub in ["minus", "plus"]:
                    glist.append(cmd_dict.get("relative"))
                    
                    linear_cmd = cmd_dict.get("linear")
                    move_cmd = ""
                    # axis_part usually 'x', 'y'
                    # Use self.travel (global travel var)
                    for char in axis_part:
                         val = f"{dir_dict.get(sub)}{self.travel}"
                         move_cmd += f" {char.upper()}{val}"
                    
                    # Combine G1 F... with X...
                    glist.append(f"{linear_cmd}{move_cmd}")

                
                # CENTER Logic
                if sub == "center":
                    glist.append(cmd_dict.get("absolute"))
                    
                    linear_cmd = cmd_dict.get("linear")
                    move_cmd = ""
                    if "xy" in axis_part:
                        move_cmd += f" X{self.xcenter} Y{self.ycenter}"
                    if "z" in axis_part:
                        move_cmd += f" Z{self.zcenter}"
                        
                    glist.append(f"{linear_cmd}{move_cmd}")


            glist.append("M114")
            
            for g in glist:
                self.sendGcode(g)

                    
    def terminalData(self, widget, response=None):
        action = self.wh.getRole(widget)
        
        if action == "termdata" and response in (Qt.Key_Up, Qt.Key_Down):
            
            cmd = None
            
            if response == Qt.Key_Up:
                cmd = self.terminal_buffer.decrement()
            
            if response == Qt.Key_Down:
                cmd = self.terminal_buffer.increment()                
                
            if cmd:
                print(f"cmd : {cmd}")
                self.wh.invokeMethod(self.terminal_widgets.termdata, "set", cmd)
        
        if action == "termsend" or response in (Qt.Key_Return, Qt.Key_Enter):
            gcode = self.wh.invokeMethod(self.terminal_widgets.termdata, "get")
            
            if gcode:
                self.terminal_buffer.push(gcode)
                print(f"buff : {self.terminal_buffer.get()}")
                self.wh.invokeMethod(self.terminal_widgets.termdata, "clear")
                self.sendGcode(gcode)
                self.sendGcode("M114")
                    
    def valueSelector(self, widget, index, *args):
        arg_list = [arg for arg in args]
        idx = (index + 1) % len(arg_list)
        value = arg_list[idx]
        
        self.wh.invokeMethod(widget, "set", str(value))
        return idx, value
    
    def goHome(self):
        self.updateAxisPos()

    
    def updateAxisPos(self):
        # self.util.debugPrint(f"pos : {self.gh.pos_list}")
        
        # gh.pos_list is populated by GcodeHandler when it parses M114 response
        for item in self.gh.pos_list:
            if ":" in item:
                axis, value = item.split(':')            
                self.ah.pos(axis, float(value))
            
        self.jogPosDisplay()
        self.focusPosDisplay()
        self.offsetPosDisplay()
        
        self.indexProgram()

    
    def moveFinish(self):
        pass
    
    @Slot(float)
    def _updatePrintProgress(self, value: float):
        self.wh.invokeMethod(self.print_widgets.print, "set", value)

    def setProgress(self, value: float):        
        self.sigPrintProgress.emit(value)

    
    def updateProgress(self, signal: Signal, value: float):
        signal.emit(value)
    
    def setWidgetPara(self, widget, method_name, value=None):
        method = getattr(widget, method_name)
        
        if value is not None:
            method(value)
        else:
            method()

    def getWidgetPara(self, widget, method_name):
        method = getattr(widget, method_name)
        return method()

    
    def getPageIndex(self, page_dict, arg):
        index = 0

        if isinstance(arg, int):
            index = arg

        if isinstance(arg, str):
            index = page_dict.get(arg)

        return index

    def showStackPage(self, widget, page_dict, arg):
        method_name = "setCurrentIndex"
        # self.util.debugPrint(f"arg : {arg}")

        index = self.getPageIndex(page_dict, arg)
        self.setWidgetPara(widget, method_name, value=index)

    
    def configCom(self, com, mode):
        # In main.py, 'com' arg is expected to be the SerialCom object or name
        # m.py passes 'self.com' which is a DictAsClass wrapper.
        # main.py 'initCom' calls: self.configSerial("maincom", ...)
        # This method configCom seems to be an Auto-connect helper called by showExceptionPopup
        
        # Adapting logic to match main.py's activateSerial structure
        if mode == "Auto":
             # "maincom" is the key used in main.py
             self.activateSerial("maincom", "auto")

    
    def recoverFirmware(self):
        """
        Brings firmware out of BUSY state after reconnect
        """
        self.util.debugPrint("Recovering firmware state...")
        self.logger.critical("Firmware recovery started")

        #  Flush planner / buffers
        self.sendGcode("M400")   # wait for moves
        self.sendGcode("M410")   # emergency stop (Marlin)
        self.sendGcode("G4 P0")  # dwell flush
        self.sendGcode("M114")   # force position sync

        #  Reset internal UI state
        self.resetPrintState(reason="firmware recovery")

        self.logger.critical("Firmware recovery completed")

    
    def updateData(self, msg):
        if not msg:
            return

        data = msg.strip()

        #  Pass raw line to GcodeHandler (protocol logic lives there)
        self.gh.decode(data)

        # UI formatting only
        if data == "ok":
            data += "\n"

        if self.gh.temp_report_flag and self.temp_report_hide_flag:
            self.gh.temp_report_flag = False
        else:
            self.util.debugPrint(f"Received : {data}")

        self.receiveACK(self.terminal_widgets.termresponse, data)

    def updateException(self, args):
        self.util.debugPrint(f"error args : {args}")
        self.com_errorFlag = True
        self.util.debugPrint(f"error flag : {self.com_errorFlag}")
        self.activateSerial("maincom", "disconnect")

        self.exceptionOccurred.emit(str(args))


    def sendGcode(self, gstr):
        """Send one G-code line to printer, ignoring comments, blanks, and stripping inline notes."""
        gstr = gstr.strip()

        # Ignore full-line comments or empty lines
        if not gstr or gstr.startswith(";") or gstr.startswith("("):
            self.util.debugPrint(f"Skipping comment/non-executable: {gstr}")
            return

        # Remove inline comments safely
        gstr = re.split(r'[;()]', gstr, maxsplit=1)[0].strip()
        if not gstr:
            self.util.debugPrint(f"Skipping empty after stripping comment")
            return
        
        # Encode & checksum handling
        self.gh.encode(gstr)
        if self.gh.sd_write_flag:
            cs = self.gh.checksum(gstr)
            gcode = f"{gstr}*{cs}\r\n"
        else:
            gcode = f"{gstr}\r\n"
            
        # Send and log
        self.sendSerial("maincom", gcode)
        self.util.debugPrint(f"Gcode - {gcode.strip()}")

        # Log to terminal UI
        if hasattr(self, "terminal_widgets") and hasattr(self.terminal_widgets, "termresponse"):
             try:
                 self.terminal_widgets.termresponse.append(f"{gstr}")
                 # Auto-scroll to bottom
                 sb = self.terminal_widgets.termresponse.verticalScrollBar()
                 sb.setValue(sb.maximum())
             except Exception as e:
                 print(f"Terminal logging error: {e}")
        
    def pgmGcode(self, gstr):
        cmd_dict = {"M3" : "ON",
                    "M5" : "OFF"}

        if self.pgm_laser:
             laser = self.lh.getLaser(self.pgm_laser)
             if laser and gstr in ["M3", "M5"]:
                 gcode = laser.cmd.get(cmd_dict.get(gstr))
                 self.sendGcode(gcode)
                 return

        self.sendGcode(gstr)

    
    def jogPosDisplay(self):                
        xpos = self.ah.getAxis("X").pos
        ypos = self.ah.getAxis("Y").pos
        zpos = self.ah.getAxis("Z").pos
        
        self.wh.invokeMethod(self.jog_widgets.xpos, "set", xpos)
        self.wh.invokeMethod(self.jog_widgets.ypos, "set", ypos)
        self.wh.invokeMethod(self.jog_widgets.zpos, "set", zpos)
        
        if hasattr(self.ui, 'xposgalvoLCDNumber'):
            self.ui.xposgalvoLCDNumber.display("0")
            self.ui.yposgalvoLCDNumber.display("0")
            self.ui.zposgalvoLCDNumber.display(f"{zpos:.2f}")

    
    def focusPosDisplay(self):
        zpos = self.ah.getAxis("Z").pos
        self.wh.invokeMethod(self.focus_widgets.focus, "set", zpos)
        
        if hasattr(self.ui, 'focusgalvoLCDNumber'):
            self.ui.focusgalvoLCDNumber.display(f"{zpos:.2f}")

    
    def offsetPosDisplay(self):
        xpos = self.ah.getAxis("X").pos
        ypos = self.ah.getAxis("Y").pos

        if self.zero_flag:
            self.wh.invokeMethod(self.offset_widgets.xoffset, "set", xpos - self.xtemp)
            self.wh.invokeMethod(self.offset_widgets.yoffset, "set", ypos - self.ytemp) 

        else:
            self.wh.invokeMethod(self.offset_widgets.xoffset, "set", xpos)
            self.wh.invokeMethod(self.offset_widgets.yoffset, "set", ypos)

    
    def canMoveZPlus(self, delta: float) -> bool:
        """
        Returns False if Z+ movement would exceed Z_MAX_LIMIT
        """
        current_z = self.ah.getAxis("Z").pos
        target_z = current_z + delta

        if target_z > self.Z_MAX_LIMIT:
            self.util.debugPrint(
                f"Z limit reached: current={current_z}, target={target_z}, limit={self.Z_MAX_LIMIT}"
            )
            return False

        return True

    
    def initLaser(self):
        self.laser_data_list = ["Laser 1", "Laser 2"]

        self.lh.addLaser("Laser 1", 10.0, 0, 0, {"ON" : "M106 P0 S255", "OFF" : "M106 P0 S0"})
        self.lh.addLaser("Laser 2", 10.0, 0, 0, {"ON" : "M106 P1 S255", "OFF" : "M106 P1 S0"})

        # Block signals to prevent initial OFF commands from triggering on startup
        if hasattr(self.focus_widgets, 'flaser'): self.focus_widgets.flaser.blockSignals(True)
        if hasattr(self.offset_widgets, 'offlaser'): self.offset_widgets.offlaser.blockSignals(True)
        if hasattr(self.program_widgets, 'pgmlaser'): self.program_widgets.pgmlaser.blockSignals(True)

        # Focus laser combo
        self.wh.invokeMethod(self.focus_widgets.flaser, "add", self.laser_data_list)
        self.focus_widgets.flaser.setPlaceholderText("Select Laser")
        self.focus_widgets.flaser.setCurrentIndex(-1)

        # Offset laser combo
        self.wh.invokeMethod(self.offset_widgets.offlaser, "add", self.laser_data_list)
        self.offset_widgets.offlaser.setPlaceholderText("Select Laser")
        self.offset_widgets.offlaser.setCurrentIndex(-1)

        # Program laser combo
        self.wh.invokeMethod(self.program_widgets.pgmlaser, "add", self.laser_data_list)
        self.program_widgets.pgmlaser.setPlaceholderText("Select Laser")
        self.program_widgets.pgmlaser.setCurrentIndex(-1)

        # Initial button states
        self.wh.invokeMethod(self.focus_widgets.flaser, "enable")
        self.wh.invokeMethod(self.focus_widgets.fset, "disable")
        self.wh.invokeMethod(self.focus_widgets.flaserset, "disable")

        self.wh.invokeMethod(self.offset_widgets.offlaser, "enable")
        self.wh.invokeMethod(self.offset_widgets.offlaserset, "disable")
        self.wh.invokeMethod(self.offset_widgets.offzero, "disable")
        self.wh.invokeMethod(self.offset_widgets.offset, "disable")
        
        # Unblock signals
        if hasattr(self.focus_widgets, 'flaser'): self.focus_widgets.flaser.blockSignals(False)
        if hasattr(self.offset_widgets, 'offlaser'): self.offset_widgets.offlaser.blockSignals(False)
        if hasattr(self.program_widgets, 'pgmlaser'): self.program_widgets.pgmlaser.blockSignals(False)
    
    
    def shutdownLaser(self, name=None):
        if name is not None:
             laser = self.lh.getLaser(name)
             if laser is not None:
                 gcode = laser.cmd.get("OFF")
                 if gcode:
                     self.sendGcode(gcode)
                     self.logger.critical(f"{name} : OFF")
        else:
             keys = self.lh.getKeys()
             
             for name in keys:
                 laser = self.lh.getLaser(name)
                 gcode = laser.cmd.get("OFF")
                 self.sendGcode(gcode)
                 self.logger.critical(f"{name} : OFF")

    
    def initAxis(self):
        pass
    
    def resetPrintState(self, reason="unknown"):
        # Reset inspection state if active
        if hasattr(self, "is_inspection_running") and self.is_inspection_running:
            self.wh.invokeMethod(self.camera_widgets.camstart, "set", "START")
            self.wh.invokeMethod(self.camera_widgets.camstart, "enable")
            self.wh.invokeMethod(self.camera_widgets.camstop, "enable")
            self.wh.invokeMethod(self.camera_widgets.campause, "set", "PAUSE")
            self.wh.invokeMethod(self.camera_widgets.campause, "enable")
            
            self.wh.invokeMethod(self.print_widgets.printinspect, "enable")
            self.is_inspection_running = False

        # Re-enable camera jog buttons using roles
        self.wh.invokeMethod(self.left_menu_widgets.camerajog, "enable")
        self.wh.invokeMethod(self.settings_widgets.cameraoffset, "enable")

        self.util.debugPrint(f"Resetting print state due to: {reason}")
        self.logger.critical(f"Print reset due to: {reason}")

        self.gh.reset()

        # Program flags
        self.pgm_run_flag = False
        self.pgm_pause_flag = False
        self.pause_flag = False

        # Indices
        self.pgm_index = 0
        self.seg_index = 0
        self.prev_segment = 0

        # UI
        self.wh.invokeMethod(self.print_widgets.printrun, "enable")
        self.wh.invokeMethod(self.print_widgets.printpause, "disable")        
        self.wh.invokeMethod(self.print_widgets.printabort, "disable")

        pausebtn = self.print_widgets.printpause
        # self.pauseWidget(pausebtn, "pause")
        self.pauseWidget(pausebtn, "resume")
        
        # Reset Camera Pause Button
        self.wh.invokeMethod(self.camera_widgets.campause, "set", "PAUSE")
        self.wh.invokeMethod(self.camera_widgets.campause, "disable")

        # Progress
        self.progress = 0
        self.updateProgress(self.sigPrintProgress, 0)
        self.wh.invokeMethod(self.print_widgets.progress, "set", "0.00%")

        # Preview
        self.clearPreview()

    def programInit(self):
        self.prev_segment = 0
        self.master_glist = []
        self.wh.invokeMethod(self.program_widgets.pgmsaveset, "disable")
        
    def runInspection(self):
        if self.pgm_file and self.pgm_glist:
            
            # Check for Camera before starting
            try:
                devices = FilterGraph().get_input_devices()
                if not any("AV TO USB2.0" in name for name in devices):
                     self.showAutoCloseMessage("Camera Error", "Device 'AV TO USB2.0' not found!\nCannot start inspection.\nPlease connect the USB")
                     return
            except Exception as e:
                self.logger.error(f"Error checking for camera: {e}")
                self.showAutoCloseMessage("Camera Error", f"Failed to detect camera: {e}")
                return

            # Force Camera Jog OFF if active before starting inspection
            btn_opt = getattr(self.ui, "cameraoffsetPushButton", None)
            if btn_opt and "OFF" in btn_opt.text().upper():
                self.toggleCameraJog()
            
            # Disable Camera Jog Buttons using roles
            self.wh.invokeMethod(self.left_menu_widgets.camerajog, "disable")
            self.wh.invokeMethod(self.settings_widgets.cameraoffset, "disable")

            self.is_inspection_running = True
            self.wh.invokeMethod(self.print_widgets.printinspect, "disable")
            self.wh.invokeMethod(self.camera_widgets.camstart, "set", "START")
            self.wh.invokeMethod(self.camera_widgets.camstart, "disable")

            if hasattr(self, 'master_glist') and self.master_glist:
                # Filter out G28, laser control commands (M3, M5, M106 P), and comments (;) for inspection
                base_glist = [line for line in self.master_glist if "G28" not in line and not line.strip().startswith(("M3", "M5", "M106 P", ";"))]

                # Fetch configured camera offset for active laser
                cam_ox, cam_oy = 0.0, 0.0
                try:
                    if self.pgm_laser == "Laser 1":
                        cam_ox = float(self.ch.getValues("camera_offset", "laser1_x") or 0.0)
                        cam_oy = float(self.ch.getValues("camera_offset", "laser1_y") or 0.0)
                    elif self.pgm_laser == "Laser 2":
                        cam_ox = float(self.ch.getValues("camera_offset", "laser2_x") or 0.0)
                        cam_oy = float(self.ch.getValues("camera_offset", "laser2_y") or 0.0)
                except (ValueError, TypeError):
                    self.logger.warning(f"Could not load camera offsets for {self.pgm_laser}")

                self.logger.info(f"Applying camera offset: X={cam_ox}, Y={cam_oy} for {self.pgm_laser}")

                self.pgm_glist = []
                import re
                for line in base_glist:
                    if "X" in line or "Y" in line:
                        def rx(m): return f"X{float(m.group(1)) + cam_ox:.2f}"
                        def ry(m): return f"Y{float(m.group(1)) + cam_oy:.2f}"
                        line = re.sub(r'X([-0-9.]+)', rx, line)
                        line = re.sub(r'Y([-0-9.]+)', ry, line)
                        
                        # Set speed to camera inspection feed
                        if "F" in line:
                            line = re.sub(r'F([-0-9.]+)', f'F{self.camera_inspection_feed}', line)
                        else:
                            line = line.strip() + f" F{self.camera_inspection_feed}"
                    
                    self.pgm_glist.append(line)

                # Save inspection G-code to config folder for user verification
                try:
                    output_path = self.config_dir_path / "inspection_output.gcode"
                    with open(output_path, 'w') as f:
                        for line in self.pgm_glist:
                            f.write(line + "\n")
                    self.logger.info(f"Inspection G-code saved to: {output_path}")
                except Exception as e:
                    self.logger.error(f"Failed to save G-code: {e}")
            
            # Switch to Camera Page
            self.showMainPages("camera")
            
            # Auto-start Camera (delayed to accept page switch)
            QTimer.singleShot(500, lambda: self.cameraAction(self.camera_widgets.camstart))
            
            # Start execution (reusing runProgram logic)
            self.runProgram("run")
            
            # Ensure Pause button is reset and enabled
            self.wh.invokeMethod(self.camera_widgets.campause, "set", "PAUSE")
            self.wh.invokeMethod(self.camera_widgets.campause, "enable")
            
        else:
            self.showAutoCloseMessage("No Program", "Please load a program first.")

    def pauseWidget(self, widget, arg):
        icon_dict = {"pause" : QIcon(":/icons/icons/play-circle.svg"),
                     "resume" : QIcon(":/icons/icons/pause.svg")
                     }
        
        if arg in icon_dict:
            widget.setIcon(icon_dict.get(arg))

    def runProgram(self, arg):
                
        if arg == "run":            
            if self.pgm_glist is not None:
                self.resetPreviewForNewRun()
                self.pgm_run_flag = True
                self.pgm_index = 0
                self.seg_index = 0
                self.initPrintRun()
                self.logger.info(f"Print Status : {arg.upper()}")
            
        if arg == "pause":
            self.pgm_pause_flag = True
            self.logger.info(f"Print Status : {arg.upper()}")
            
        if arg == "resume":
            self.pgm_pause_flag = False
            self.resumeProgram()
            self.logger.info(f"Print Status : {arg.upper()}")
            
        if arg == "abort":
            #  1. Stop everything
            self.shutdownLaser()

            #  2. HARD reset print state
            self.resetPrintState(reason="abort")

            #  3. HOME machine (AFTER reset)
            self.sendGcode("G28")

            # 4. UI + log
            self.programInit()
            self.logger.info("Print Status : ABORTED AND HOMED")
            self.showMainPages("program")

    def startProgram(self):
        if self.gh.ok_flag is False:
            self.util.debugPrint("Waiting for firmware idle...")
            return

        if self.pgm_index < len(self.pgm_glist):
            gcode = self.pgm_glist[self.pgm_index]
            self.pgm_index += 1
            self.pgmGcode(gcode)
            # M400 waits in firmware until all moves complete, THEN M114 runs.
            # This prevents M114 from being answered before the motion finishes.
            self.pgmGcode("M400")
            self.pgmGcode("M114")  # Triggers indexProgram via get-pos callback
        else:
            self.util.debugPrint("startProgram called but index already at end.")
            self.pgm_run_flag = False
            self.finishProgram()

    def initPrintRun(self):
        if self.pgm_run_flag:
            self.util.debugPrint(f"segment dict : {self.preview.segment_dict}")
            self.initProgress()
            self.util.debugPrint(f"len : {len(self.pgm_glist)}")
            self.util.debugPrint(f"Print init : {self.pgm_index}")
            self.startProgram()
            
    def resumeProgram(self):
        if self.pgm_run_flag:
            self.util.debugPrint(f"Print resume : {self.pgm_index}")
            self.startProgram()
    
    def finishProgram(self):
        self.pgm_index = 0
        self.seg_index  = 0
        self.prev_segment = 0
        self.wh.invokeMethod(self.print_widgets.printrun, "enable")
        self.wh.invokeMethod(self.print_widgets.printpause, "disable")
        self.wh.invokeMethod(self.print_widgets.printabort, "disable")
        self.wh.invokeMethod(self.camera_widgets.campause, "disable")
        
        if hasattr(self.print_widgets, "printinspect"):
             self.wh.invokeMethod(self.print_widgets.printinspect, "enable")
        
        if self.is_inspection_running:
             self.wh.invokeMethod(self.camera_widgets.camstart, "set", "RESTART")
             self.wh.invokeMethod(self.camera_widgets.camstart, "enable")
             self.wh.invokeMethod(self.camera_widgets.camstop, "disable")
             self.wh.invokeMethod(self.camera_widgets.campause, "disable")
             self.is_inspection_running = False

        # Re-enable camera jog buttons using roles
        self.wh.invokeMethod(self.left_menu_widgets.camerajog, "enable")
        self.wh.invokeMethod(self.settings_widgets.cameraoffset, "enable")

    def indexProgram(self):
        if self.pgm_run_flag:
            if not self.pgm_pause_flag:
                self.util.debugPrint(f"index : {self.pgm_index}")

                if self.pgm_index < len(self.pgm_glist):
                    gcode = self.pgm_glist[self.pgm_index]
                        
                    self.pgm_index += 1
                    self.pgmGcode(gcode)   # Send the actual G-code line
                    # M400 makes firmware wait until motion is done before proceeding.
                    # Without this, M114 is answered immediately (before motion starts)
                    # and indexProgram fires again flooding all remaining lines at once.
                    self.pgmGcode("M400")  # Wait for moves to finish
                    self.pgmGcode("M114")  # Get position → triggers next indexProgram
                    self.getProgress(self.pgm_index, len(self.pgm_glist))
                    self.markSegment(gcode)
                    
                else:
                    self.pgm_run_flag = False
                    self.finishProgram()


    def markSegment(self, gcode):
        self.preview.markSegment(gcode)

    def getProgress(self, index, total):
        if index is not None and total is not None:
            if total > 0:
                frac = index / total
                self.progress = round(frac * 100, 2)
                self.showProgress()

    def showProgress(self):
        self.updateProgress(self.sigPrintProgress, self.progress)
        self.wh.invokeMethod(self.print_widgets.progress, "set", f"{self.progress:.2f}%")

    def initProgress(self):
        self.progress = 0
        self.updateProgress(self.sigPrintProgress, self.progress)
        self.wh.invokeMethod(self.print_widgets.progress, "set", f"{self.progress:.2f}%")

    def clearPreview(self):
        self.preview.segment_dict = {}
        self.preview.update()

    def resetPreviewForNewRun(self):
        """
        Reset preview colors and reload G-code for a fresh run
        """
        if not self.pgm_glist:
            return

        # Clear old execution state
        self.preview.processed_gcode = None

        # Reload gcode → all segments back to RED
        self.preview.loadGcode(self.pgm_glist)

    def cameraAction(self, widget, *args, skip_restart=False):
        self.wh.getInfo(widget) 
        action = self.wh.getRole(widget)
        print(f"action : {action}")

        if action == "camstart":
            if not skip_restart and self.wh.invokeMethod(widget, "get") == "RESTART":
                self.wh.invokeMethod(widget, "set", "START")
                self.wh.invokeMethod(widget, "disable")
                self.wh.invokeMethod(self.camera_widgets.camstop, "enable")
                self.wh.invokeMethod(self.camera_widgets.campause, "set", "PAUSE")
                self.wh.invokeMethod(self.camera_widgets.campause, "enable")
                self.is_inspection_running = True
                self.runProgram("run")
                return

            if self.cam_thread and self.cam_thread.isRunning():
                return
            
            self.video_label.setText("Searching...")
            QApplication.processEvents()
            
            try:
                devices = FilterGraph().get_input_devices()
                target = next((i for i, n in enumerate(devices) if "AV TO USB2.0" in n), None)
            except:
                target = None

            if target is not None:
                 target_name = devices[target]
                 self.video_label.setText("Connecting...")
                 self.cam_thread = CameraThread(target, target_name)
                 self.cam_thread.frame_update.connect(self.update_frame)
                 self.cam_thread.error_occurred.connect(self.on_camera_error)
                 self.cam_thread.start()
                 
                 self.wh.invokeMethod(self.camera_widgets.camstart, "disable")
                 self.wh.invokeMethod(self.camera_widgets.camstop, "enable")
            else:
                 self.video_label.setText("Camera Not Found")
                 self.showAutoCloseMessage("Camera Error", "Device not found.")
        
        if action == "camstop":
            self.stop_camera()
            if hasattr(self, "is_inspection_running") and self.is_inspection_running:
                self.runProgram("abort")
            
        if action == "campause":
            arg = "pause" if not self.pgm_pause_flag else "resume"
            self.runProgram(arg)
            text = "RESUME" if arg == "pause" else "PAUSE"
            self.wh.invokeMethod(widget, "set", text)

        if "camstep" in action:
            val = action.replace("camstep", "")
            if val == "01": val = "0.1"
            self.cam_offset_travel = float(val)
            self.util.debugPrint(f"Camera Step changed to: {self.cam_offset_travel}")

        if action in ["camoffxplus", "camoffxminus", "camoffyplus", "camoffyminus", "camoffzplus", "camoffzminus"]:
            cmd_map = {
                "camoffxplus": "xplus", "camoffxminus": "xminus",
                "camoffyplus": "yplus", "camoffyminus": "yminus",
                "camoffzplus": "zplus", "camoffzminus": "zminus"
            }
            axis_cmd = cmd_map.get(action)
            
            # Use local step size and reset global travel temporarily
            orig_travel = self.travel
            self.travel = self.cam_offset_travel
            
            self.axisMotion(axis_cmd, mode="camera")
            
            # Restore global travel
            self.travel = orig_travel

    def stop_camera(self):
        if self.cam_thread:
            self.cam_thread.stop()
            self.cam_thread = None
        
        if hasattr(self, 'video_label'):
             # Clear the image first, then set the text
             self.video_label.setPixmap(QPixmap()) 
             self.video_label.setText("Camera is been stopped")
        
        # Reset buttons
        if hasattr(self, 'camera_widgets'):
            self.wh.invokeMethod(self.camera_widgets.camstart, "enable")
            self.wh.invokeMethod(self.camera_widgets.camstop, "disable")
            self.wh.invokeMethod(self.camera_widgets.campause, "disable")
            self.wh.invokeMethod(self.camera_widgets.campause, "set", "PAUSE")

    def update_frame(self, image):
        # Ignore frames if the camera thread has been stopped
        if self.cam_thread is None:
            return
            
        if hasattr(self, 'video_label'):
            self.video_label.setPixmap(QPixmap.fromImage(image))

    def on_camera_error(self, err_msg):
        self.stop_camera()
        if hasattr(self, 'video_label'):
            self.video_label.setText(err_msg)
        self.showAutoCloseMessage("Camera Error", err_msg)

    def receiveACK(self, widget, arg):
        if widget:
            self.wh.invokeMethod(widget, "add", arg)

    def resetProfile(self):
        if hasattr(self, 'program_widgets'):
            if hasattr(self.program_widgets, 'pgmheight'): self.wh.invokeMethod(self.program_widgets.pgmheight, "clear")
            if hasattr(self.program_widgets, 'pgmfeed'): self.wh.invokeMethod(self.program_widgets.pgmfeed, "clear")
            if hasattr(self.program_widgets, 'pgmlaser'): self.wh.invokeMethod(self.program_widgets.pgmlaser, "clear")
            if hasattr(self.program_widgets, 'pgmfile'): self.wh.invokeMethod(self.program_widgets.pgmfile, "clear")
            
            if hasattr(self.program_widgets, 'pgmheightset'): self.wh.invokeMethod(self.program_widgets.pgmheightset, "disable")
            if hasattr(self.program_widgets, 'pgmfeedset'): self.wh.invokeMethod(self.program_widgets.pgmfeedset, "disable")
            if hasattr(self.program_widgets, 'pgmlaserset'): self.wh.invokeMethod(self.program_widgets.pgmlaserset, "disable")
            if hasattr(self.program_widgets, 'pgmsaveset'): self.wh.invokeMethod(self.program_widgets.pgmsaveset, "disable")
        
        # Reset internal variables
        self.pgm_file = None
        self.pgm_height = None
        self.pgm_feed = None
        self.pgm_laser = None


  

    def setupAdvancedCalibration(self):
        from core.calibration_generator_ui import GridPreviewWidget
        from PySide6.QtWidgets import QVBoxLayout

        self.cal_state_idx = 0
        self.cal_default_w = 30.0
        self.cal_is_stopped = False
        
        # Attach preview widget
        if hasattr(self.ui, 'visualorientFrame'):
            layout = self.ui.visualorientFrame.layout()
            if not layout:
                layout = QVBoxLayout(self.ui.visualorientFrame)
            self.cal_preview = GridPreviewWidget(self.ui.visualorientFrame)
            layout.addWidget(self.cal_preview)
            
        # Lists for inputs
        self.cal_inputs_x = []
        self.cal_inputs_y = []
        for i in range(1, 10):
            le_x = getattr(self.ui, f"x{i}mmLineEdit", None)
            le_y = getattr(self.ui, f"y{i}mmLineEdit", None)
            if le_x: self.cal_inputs_x.append(le_x)
            if le_y: self.cal_inputs_y.append(le_y)

        # Connections
        if hasattr(self.ui, 'changeimgPushButton'):
            self.ui.changeimgPushButton.clicked.connect(self.next_cal_state)
        if hasattr(self.ui, 'targhalfwidLineEdit'):
            self.ui.targhalfwidLineEdit.setText(str(self.cal_default_w))
            self.ui.targhalfwidLineEdit.textChanged.connect(self.on_cal_w_changed)
        if hasattr(self.ui, 'resettonominalPushButton'):
            self.ui.resettonominalPushButton.clicked.connect(self.reset_cal_to_nominal)
            
        if hasattr(self.ui, 'markcalgridPushButton'):
            self.ui.markcalgridPushButton.clicked.connect(self.draw_cal_pattern)
        if hasattr(self.ui, 'stopPushButton'):
            self.ui.stopPushButton.clicked.connect(self.stop_cal_pattern)
        if hasattr(self.ui, 'calapplyPushButton'):
            self.ui.calapplyPushButton.clicked.connect(self.generate_calibration)
        if hasattr(self.ui, 'markvershapePushButton'):
            self.ui.markvershapePushButton.clicked.connect(self.dummy_cal_action)
        if hasattr(self.ui, 'ezcadclosePushButton'):
            self.ui.ezcadclosePushButton.clicked.connect(lambda: self.showMainPages("home"))
            
        # Initial values
        if hasattr(self.ui, 'imgindLineEdit'):
            self.ui.imgindLineEdit.setText(f"{self.cal_state_idx + 1}")
            self.ui.imgindLineEdit.setReadOnly(True)

    def on_cal_w_changed(self, text):
        try:
            val = float(text)
            if val > 0:
                self.cal_default_w = val
        except ValueError:
            pass

    def reset_cal_to_nominal(self):
        w = self.cal_default_w
        default_vals = [
            (w, w), (0, w), (w, w),
            (w, 0), (0, 0), (w, 0),
            (w, w), (0, w), (w, w)
        ]
        for i in range(9):
            if i < len(self.cal_inputs_x) and default_vals[i][0] != 0:
                self.cal_inputs_x[i].setText(f"{default_vals[i][0]:.3f}")
            if i < len(self.cal_inputs_y) and default_vals[i][1] != 0:
                self.cal_inputs_y[i].setText(f"{default_vals[i][1]:.3f}")
                
            if i < len(self.cal_inputs_x) and default_vals[i][0] == 0:
                self.cal_inputs_x[i].setText("0.000")
                self.cal_inputs_x[i].setEnabled(False)
            if i < len(self.cal_inputs_y) and default_vals[i][1] == 0:
                self.cal_inputs_y[i].setText("0.000")
                self.cal_inputs_y[i].setEnabled(False)

    def next_cal_state(self):
        self.cal_state_idx = (self.cal_state_idx + 1) % 8
        if hasattr(self.ui, 'imgindLineEdit'):
            self.ui.imgindLineEdit.setText(f"{self.cal_state_idx + 1}")
        if hasattr(self, 'cal_preview'):
            self.cal_preview.set_state(self.cal_state_idx)

    def dummy_cal_action(self):
        from PySide6.QtWidgets import QMessageBox, QApplication
        self.cal_is_stopped = False
        if not self.galvo_controller or not self.galvo_controller.connection:
            QMessageBox.warning(self, "Error", "Galvo controller not connected.")
            return
            
        scale = 533.89
        # User requested a 60x60mm square. So half-width is 30mm.
        hw = int(30.0 * scale)
        c = 32767
        
        min_x = c - hw
        max_x = c + hw
        min_y = c - hw
        max_y = c + hw
        
        conn = self.galvo_controller.connection
        
        try:
            pwr = float(self.ui.powerHorizontalSlider.value()) if hasattr(self.ui, 'powerHorizontalSlider') else 100.0
            freq = float(self.ui.freqHorizontalSlider.value()) if hasattr(self.ui, 'freqHorizontalSlider') else 30.0
            mark_speed = int(self.ui.markspeedLineEdit.text()) if hasattr(self.ui, 'markspeedLineEdit') and self.ui.markspeedLineEdit.text() else 5000
            jump_speed = int(self.ui.jumpspeedLineEdit.text()) if hasattr(self.ui, 'jumpspeedLineEdit') and self.ui.jumpspeedLineEdit.text() else 15000
        except ValueError:
            QMessageBox.warning(self, "Error", "Invalid laser parameters. Using defaults.")
            pwr, freq, mark_speed, jump_speed = 100.0, 30.0, 5000, 15000

        if hasattr(conn, 'set_analog_do_bit'):
            for test_bit in [0, 1, 2]:
                conn.set_analog_do_bit(100.0, pwr, freq, test_bit)
            import time
            time.sleep(0.05)
        
        queue = []
        def jump(x, y): queue.append({'type': 'jump', 'x': int(x), 'y': int(y), 'speed': jump_speed})
        def mark(x, y): queue.append({'type': 'mark', 'x': int(x), 'y': int(y), 'speed': mark_speed})
            
        try:
            # Draw outer 60x60 square
            jump(min_x, max_y)
            mark(max_x, max_y)
            mark(max_x, min_y)
            mark(min_x, min_y)
            mark(min_x, max_y)
            
            if hasattr(self.ui, 'markvershapePushButton'):
                self.ui.markvershapePushButton.setEnabled(False)
                
            success = self.galvo_controller.execute_queue(
                queue,
                loop_count=1,
                abort_check=lambda: self.cal_is_stopped,
                progress_callback=lambda idx, tot, x, y, ctype: QApplication.processEvents()
            )
            
            if self.cal_is_stopped or not success:
                raise InterruptedError("Drawing stopped by user or failed")
                
            conn.laser_off()
            conn.galvo_move_xy(c, c)
            
            QMessageBox.information(self, "Info", "Verification shape (60x60mm) drawn!")
        except InterruptedError:
            pass
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to draw pattern: {e}")
        finally:
            if conn: conn.laser_off()
            if hasattr(self.ui, 'markvershapePushButton'):
                self.ui.markvershapePushButton.setEnabled(True)

    def stop_cal_pattern(self):
        self.cal_is_stopped = True

    def draw_cal_pattern(self):
        from PySide6.QtWidgets import QMessageBox, QApplication
        self.cal_is_stopped = False
        if not self.galvo_controller or not self.galvo_controller.connection:
            QMessageBox.warning(self, "Error", "Galvo controller not connected.")
            return
            
        scale = 533.89
        hw = int(self.cal_default_w * scale)
        c = 32767
        
        min_x = c - hw
        max_x = c + hw
        min_y = c - hw
        max_y = c + hw
        
        conn = self.galvo_controller.connection
        
        try:
            pwr = float(self.ui.powerHorizontalSlider.value()) if hasattr(self.ui, 'powerHorizontalSlider') else 100.0
            freq = float(self.ui.freqHorizontalSlider.value()) if hasattr(self.ui, 'freqHorizontalSlider') else 30.0
            mark_speed = int(self.ui.markspeedLineEdit.text()) if hasattr(self.ui, 'markspeedLineEdit') and self.ui.markspeedLineEdit.text() else 5000
            jump_speed = int(self.ui.jumpspeedLineEdit.text()) if hasattr(self.ui, 'jumpspeedLineEdit') and self.ui.jumpspeedLineEdit.text() else 15000
        except ValueError:
            QMessageBox.warning(self, "Error", "Invalid laser parameters. Using defaults.")
            pwr, freq, mark_speed, jump_speed = 100.0, 30.0, 5000, 15000

        if hasattr(conn, 'set_analog_do_bit'):
            for test_bit in [0, 1, 2]:
                conn.set_analog_do_bit(100.0, pwr, freq, test_bit)
            import time
            time.sleep(0.05)
        
        queue = []
        def jump(x, y): queue.append({'type': 'jump', 'x': int(x), 'y': int(y), 'speed': jump_speed})
        def mark(x, y): queue.append({'type': 'mark', 'x': int(x), 'y': int(y), 'speed': mark_speed})
            
        try:
            jump(min_x, max_y)
            mark(max_x, max_y)
            mark(max_x, min_y)
            mark(min_x, min_y)
            mark(min_x, max_y)
            
            jump(c, max_y)
            mark(c, min_y)
            
            jump(min_x, c)
            mark(max_x, c)
            
            ms = int(2.0 * scale)
            
            jump(min_x - ms, max_y + ms)
            mark(min_x + ms, max_y + ms)
            mark(min_x + ms, max_y - ms)
            mark(min_x - ms, max_y - ms)
            mark(min_x - ms, max_y + ms)
            
            jump(max_x, min_y + ms)
            mark(max_x + ms, min_y)
            mark(max_x, min_y - ms)
            mark(max_x - ms, min_y)
            mark(max_x, min_y + ms)
            
            tick_x = c - int(hw * 0.3)
            tick_y_top = c + int(hw * 0.2)
            tick_y_bot = c - int(hw * 0.2)
            jump(tick_x, tick_y_top)
            mark(tick_x, tick_y_bot)
            
            if hasattr(self.ui, 'markcalgridPushButton'):
                self.ui.markcalgridPushButton.setEnabled(False)
                
            success = self.galvo_controller.execute_queue(
                queue,
                loop_count=1,
                abort_check=lambda: self.cal_is_stopped,
                progress_callback=lambda idx, tot, x, y, ctype: QApplication.processEvents()
            )
            
            if self.cal_is_stopped or not success:
                raise InterruptedError("Drawing stopped by user or failed")
                
            conn.laser_off()
            conn.galvo_move_xy(c, c)
            
            QMessageBox.information(self, "Info", "Pattern drawn! Please measure the 9 points and enter the values.")
        except InterruptedError:
            pass
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to draw pattern: {e}")
        finally:
            if conn: conn.laser_off()
            if hasattr(self.ui, 'markcalgridPushButton'):
                self.ui.markcalgridPushButton.setEnabled(True)

    def generate_calibration(self):
        from core.calibration_generator_ui import TRANSFORMS
        from core.calibration_generator import generate_cor_file
        from PySide6.QtWidgets import QMessageBox
        
        ui_measurements = []
        for i in range(9):
            try:
                x = float(self.cal_inputs_x[i].text()) if i < len(self.cal_inputs_x) else 0.0
                y = float(self.cal_inputs_y[i].text()) if i < len(self.cal_inputs_y) else 0.0
                ui_measurements.append((x, y))
            except ValueError:
                QMessageBox.warning(self, "Error", f"Invalid input at point {i+1}")
                return
                
        transform = TRANSFORMS[self.cal_state_idx]
        galvo_measurements = [None] * 9
        
        signs = [
            (-1, 1),  (0, 1),  (1, 1),
            (-1, 0),  (0, 0),  (1, 0),
            (-1, -1), (0, -1), (1, -1)
        ]
        
        for galvo_idx in range(9):
            ui_idx = transform.index(galvo_idx)
            raw_x, raw_y = ui_measurements[ui_idx]
            
            sx, sy = signs[galvo_idx]
            meas_x = raw_x * sx if sx != 0 else 0
            meas_y = raw_y * sy if sy != 0 else 0
            
            galvo_measurements[galvo_idx] = (meas_x, meas_y)
            
        scale = 533.89 
        
        try:
            generate_cor_file("generated_calibration.cor", scale, self.cal_default_w, galvo_measurements)
            QMessageBox.information(self, "Success", "generated_calibration.cor created successfully!")
            
            # Auto-load the newly generated file if connection available
            if hasattr(self.galvo_controller, 'connection') and hasattr(self.galvo_controller.connection, 'calibration'):
                self.galvo_controller.connection.calibration.load_calibration("generated_calibration.cor")
                if self.galvo_controller.connection.calibration.is_valid:
                    QMessageBox.information(self, "Loaded", "New calibration automatically loaded!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate: {e}")

if __name__ == '__main__':
    
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
