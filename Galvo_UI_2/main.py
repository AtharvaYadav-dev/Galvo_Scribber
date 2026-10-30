import os
import sys
import re
import math
import numpy as np

# Ensure current working directory is the script directory so relative paths and configs resolve
_app_dir = os.path.dirname(os.path.abspath(__file__))
if os.getcwd() != _app_dir:
    try:
        os.chdir(_app_dir)
    except Exception:
        pass
if _app_dir not in sys.path:
    sys.path.insert(0, _app_dir)

from ui_interface import *
from Custom_Widgets.Widgets import *
from PySide6.QtCore import QTimer, QRegularExpression, Signal, Slot, Qt, QThread, QEvent, QEventLoop, QSize
from PySide6.QtGui import QIcon, QCloseEvent, QIntValidator, QDoubleValidator, QRegularExpressionValidator
from PySide6.QtWidgets import (
    QFileDialog, QMessageBox, QInputDialog, QFrame, QLabel, QLineEdit, 
    QComboBox, QCheckBox, QPushButton, QHBoxLayout, QVBoxLayout, QSizePolicy, QSlider
)

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
from text_ui_handler import TextUIHandler
from core.engraving_manager import EngravingManager
from core.heightmap_slicer import Heightmap3DSlicer
from core.coin_3d_engraver import Coin3DReliefEngraver


from pygrabber.dshow_graph import FilterGraph
from camera_thread import CameraThread
from PySide6.QtGui import QPixmap, QImage

from notifier_ui import NotifierUI


class MainWindow(QMainWindow):
    sigPrintProgress = Signal(float)
    exceptionOccurred = Signal(str)
    sigUpdateData = Signal(str)

    RESOLUTION_3D_TIERS = {
        "Draft / Low (~100 Passes - Fast)": {
            "passes": 100,
            "pitch": 0.025,
            "power_scale": 1.05,
            "freq_scale": 1.0,
            "speed_scale": 1.0,
            "desc": "Fast roughing & rapid 3D relief preview (100 passes)"
        },
        "Medium Detail (~250 Passes - Balanced)": {
            "passes": 250,
            "pitch": 0.020,
            "power_scale": 0.90,
            "freq_scale": 1.15,
            "speed_scale": 1.15,
            "desc": "Crisp bas-relief with balanced speed & detail (250 passes)"
        },
        "High Quality (~350 Passes - Fine)": {
            "passes": 350,
            "pitch": 0.018,
            "power_scale": 0.82,
            "freq_scale": 1.25,
            "speed_scale": 1.25,
            "desc": "High definition coin reliefs and fine chamfers (350 passes)"
        },
        "Ultra / Highest (~500 Passes - Die Grade)": {
            "passes": 500,
            "pitch": 0.015,
            "power_scale": 0.72,
            "freq_scale": 1.35,
            "speed_scale": 1.35,
            "desc": "Mirror-finish master die grade, ~1.5 µm micro-ablation (500 passes)"
        },
        "Custom (Manual Passes)": None
    }
    
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
        
        # Enable Drag and Drop for design and G-Code files
        self.setAcceptDrops(True)
        
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
        self.engraving_mgr = EngravingManager()
        self.galvo_preview_thread = None
        self.galvo_has_disconnected = False
        if not self.galvo_controller.is_connected:
            self.ui.titleLabel.setText("Patterning Machine (Demo Mode)")


        self.util.debugFlag = True
        
        self.temp_report_hide_flag = False 
        self.com_errorFlag = False
        # self.exceptionOccurred.connect(self.showExceptionPopup)
        
        self.lh = LaserHandler()
        self.text_ui_handler = TextUIHandler(self)
        
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
#         self.setupJog()
#         self.setupFocus()
#         self.setupOffset()
#         self.setupProgram()
#         self.setupPrint()
#         self.setupCamera()
        self.setupTerminal()
        self.setupJogGalvo()
        self.setupLaserConfGalvo()
        self.setupProgramsGalvo()
        self.setupPrintGalvo()
        self.setupConfigGalvo()
        self.setupAdvancedCalibration()
        self.setupMapMatrix()
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
#         self.initPrint()
#         self.initCamera()
        self.initTerminal()
        self.initJogGalvo()
        self.initLaserConfGalvo()
        self.initProgramsGalvo()
        self.initPrintGalvo()
        self.initConfigGalvo()
        self.initMapMatrix()
        
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
        self.di1_last_state = -1
        self.di2_last_state = -1
        self.di_timer = QTimer(self)
        self.di_timer.setInterval(100)
        self.di_timer.timeout.connect(self.poll_di_inputs)
        self.di_timer.start()

    def poll_di_inputs(self):
        if not hasattr(self, 'galvo_controller') or not self.galvo_controller.is_connected:
            return
            
        try:
            di1_state = self.galvo_controller.get_di_bit(0)
            di2_state = self.galvo_controller.get_di_bit(1)
            
            # Initialize last states on first run
            if self.di1_last_state == -1:
                self.di1_last_state = di1_state
            if self.di2_last_state == -1:
                self.di2_last_state = di2_state
            
            # Check DI1 state change
            if di1_state != self.di1_last_state:
                if di1_state == 0: # Pressed (under 1V)
                    msg = ">> Hardware Trigger: DI1 (Start) Pressed!"
                    self.logger.info(msg)
                    print(msg) # Print to console
                    if hasattr(self, 'terminal_widgets') and hasattr(self.terminal_widgets, 'termresponse'):
                        self.terminal_widgets.termresponse.append(msg)
                        
                    # Trigger the print logic
                    if str(self.galvo_mode).upper() == "ON":
                        if getattr(self, 'pgm_file', None) or getattr(self, 'current_test_shape', None):
                            if hasattr(self.ui, 'printrungalvoPushButton') and self.ui.printrungalvoPushButton.isEnabled():
                                self.showMainPages("printgalvo")
                                self.printGalvoAction(self.printgalvo_widgets.printrungalvo)
                    else:
                        if getattr(self, 'pgm_file', None):
                            if hasattr(self.ui, 'printrunPushButton') and self.ui.printrunPushButton.isEnabled():
                                self.showMainPages("print")
                                self.printAction(self.print_widgets.printrun)
                else: # Released (24V)
                    msg = ">> Hardware Trigger: DI1 (Start) Not Pressed!"
                    self.logger.info(msg)
                    print(msg) # Print to console
                    if hasattr(self, 'terminal_widgets') and hasattr(self.terminal_widgets, 'termresponse'):
                        self.terminal_widgets.termresponse.append(msg)
                        
            # Check DI2 state change
            if di2_state != self.di2_last_state:
                if di2_state == 0: # Pressed (under 1V)
                    msg = ">> Hardware Trigger: DI2 (Abort) Pressed!"
                    self.logger.info(msg)
                    print(msg) # Print to console
                    if hasattr(self, 'terminal_widgets') and hasattr(self.terminal_widgets, 'termresponse'):
                        self.terminal_widgets.termresponse.append(msg)
                        
                    # Trigger the abort logic
                    if hasattr(self, 'mapping_controller') and (getattr(self.mapping_controller, 'is_running', False) or getattr(self.mapping_controller, 'preview_active', False)):
                        self.mapping_controller.abort()
                    elif str(self.galvo_mode).upper() == "ON":
                        if hasattr(self.ui, 'printabortgalvoPushButton') and self.ui.printabortgalvoPushButton.isEnabled():
                            self.printGalvoAction(self.printgalvo_widgets.printabortgalvo)
                    else:
                        if hasattr(self.ui, 'printabortPushButton') and self.ui.printabortPushButton.isEnabled():
                            self.printAction(self.print_widgets.printabort)
                else: # Released (24V)
                    msg = ">> Hardware Trigger: DI2 (Abort) Not Pressed!"
                    self.logger.info(msg)
                    print(msg) # Print to console
                    if hasattr(self, 'terminal_widgets') and hasattr(self.terminal_widgets, 'termresponse'):
                        self.terminal_widgets.termresponse.append(msg)
                        
            self.di1_last_state = di1_state
            self.di2_last_state = di2_state
        except Exception as e:
            self.logger.error(f"Error polling DI inputs: {e}")

    def applyGalvoMode(self):
        is_on = (str(self.galvo_mode).upper() == "ON")
        
#         self.wh.invokeMethod(self.left_menu_widgets.home, "hide" if is_on else "show")
#         self.wh.invokeMethod(self.left_menu_widgets.programs, "hide" if is_on else "show")
#         self.wh.invokeMethod(self.left_menu_widgets.print, "hide" if is_on else "show")
#         self.wh.invokeMethod(self.left_menu_widgets.camera, "hide" if is_on else "show")
#         self.wh.invokeMethod(self.left_menu_widgets.camerajog, "hide" if is_on else "show")
        
        self.wh.invokeMethod(self.left_menu_widgets.joggalvo, "show" if is_on else "hide")
        self.wh.invokeMethod(self.left_menu_widgets.qrgalvo, "show" if is_on else "hide")
        if hasattr(self.left_menu_widgets, 'cadgalvo'):
            self.wh.invokeMethod(self.left_menu_widgets.cadgalvo, "show" if is_on else "hide")
#         self.wh.invokeMethod(self.left_menu_widgets.programsgalvo, "show" if is_on else "hide")
#         self.wh.invokeMethod(self.left_menu_widgets.printgalvo, "show" if is_on else "hide")
        
        if is_on:
#             self.wh.invokeMethod(self.left_menu_widgets.laser, "hide")
            pass
        else:
#             self.wh.invokeMethod(self.left_menu_widgets.laserconfgalvo, "hide")
            pass
            
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
        left_menu_widget_list.append(self.wh.configWidget(self, QPushButton, "terminalPushButton", role="terminal", toolTip="Terminal"))
        
        left_menu_widget_list.append(self.wh.configWidget(self, QPushButton, "joggalvoPushButton", role="joggalvo", toolTip="Jog Galvo"))
        left_menu_widget_list.append(self.wh.configWidget(self, QPushButton, "laserconfgalvoPushButton", role="laserconfgalvo", toolTip="Laser Galvo"))
        left_menu_widget_list.append(self.wh.configWidget(self, QPushButton, "programsgalvoPushButton", role="programsgalvo", toolTip="Program Galvo"))
        left_menu_widget_list.append(self.wh.configWidget(self, QPushButton, "printgalvoPushButton", role="printgalvo", toolTip="Print Galvo"))
        left_menu_widget_list.append(self.wh.configWidget(self, QPushButton, "paramapmatrixPushButton", role="paramapmatrix", toolTip="Param Matrix"))
        left_menu_widget_list.append(self.wh.configWidget(self, QPushButton, "qrgalvoPushButton", role="qrgalvo", toolTip="QR/Barcode DXF"))
        if hasattr(self.ui, 'printgalvoPushButton_2'):
            left_menu_widget_list.append(self.wh.configWidget(self, QPushButton, "printgalvoPushButton_2", role="cadgalvo", toolTip="Cad Page"))

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
        
        # Setup QR/Barcode DXF Generator widget in qrPage
        from qr_barcode_tool import QRBarcodeWidget
        from PySide6.QtWidgets import QVBoxLayout
        if hasattr(self.ui, 'qrPage'):
            self.qr_layout = QVBoxLayout(self.ui.qrPage)
            self.qr_widget = QRBarcodeWidget(self.ui.qrPage)
            self.qr_layout.addWidget(self.qr_widget)
            
        # Setup 2D CAD Canvas in cadPage
        from cad_canvas import CadCanvasWidget
        if hasattr(self.ui, 'cadPage'):
            self.cad_layout = QVBoxLayout(self.ui.cadPage)
            self.cad_layout.setContentsMargins(0, 0, 0, 0)
            self.cad_widget = CadCanvasWidget(self.ui.cadPage, main_window=self)
            self.cad_layout.addWidget(self.cad_widget)

        if hasattr(self.ui, 'printgalvoPushButton_2') and hasattr(self.ui, 'cadPage'):
            self.ui.printgalvoPushButton_2.clicked.connect(lambda: self.main_stack.setCurrentWidget(self.ui.cadPage))

        if hasattr(self, 'main_stack') and self.main_stack:
            self.main_stack.currentChanged.connect(self.on_main_page_changed)

    def on_main_page_changed(self, index):
        # Index 3 is printgalvo page
        target_idx = getattr(self, 'main_page_dict', {}).get("printgalvo", 3)
        if index == target_idx:
            is_3d = hasattr(self, 'cb_enable_3d_engraving') and self.cb_enable_3d_engraving.isChecked()
            if hasattr(self, 'layer_slider_frame'):
                self.layer_slider_frame.setVisible(is_3d)
            if is_3d:
                if hasattr(self, '_cached_3d_layers') and self._cached_3d_layers:
                    tot = len(self._cached_3d_layers)
                    cur = self.slider_3d_layer.value() if hasattr(self, 'slider_3d_layer') else 1
                    if hasattr(self, 'slider_3d_layer'):
                        self.slider_3d_layer.blockSignals(True)
                        self.slider_3d_layer.setMaximum(tot)
                        self.slider_3d_layer.setValue(cur)
                        self.slider_3d_layer.blockSignals(False)
                    self.render_3d_preview_layer(cur)
        else:
            # Leaving preview page
            pass
    
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
        program_widget_list.append(self.wh.configWidget(self, QLineEdit, "pgmlaserpowerLineEdit", "textChanged", self.onPgmDataChanged, role="pgmlaserpower", arg="laserpower", toolTip="Enter Laser Power"))
        program_widget_list.append(self.wh.configWidget(self, QLineEdit, "pgmlaserfreqLineEdit", "textChanged", self.onPgmDataChanged, role="pgmlaserfreq", arg="laserfreq", toolTip="Enter Laser Frequency"))
        program_widget_list.append(self.wh.configWidget(self, QPushButton, "pgmfilePushButton", "clicked", self.programAction, role="pgmfileset", toolTip="Browse File"))
        program_widget_list.append(self.wh.configWidget(self, QPushButton, "pgmsavePushButton", "clicked", self.programAction, role="pgmsaveset", toolTip="Save G-code"))
        # program_widget_list.append(self.wh.configWidget(self, QPushButton, "pgmstepsPushButton", "clicked", self.programAction))
        
        self.util.dedupeList(program_widget_list)
        self.program_widgets = self.wh.createMap(*program_widget_list)

        # Restrict inputs to numbers and a single decimal point
        regex_validator = QRegularExpressionValidator(QRegularExpression(r"^\d*\.?\d*$"), self)
        if hasattr(self.program_widgets, "pgmheight") and self.program_widgets.pgmheight:
            self.program_widgets.pgmheight.setValidator(regex_validator)
        if hasattr(self.program_widgets, "pgmfeed") and self.program_widgets.pgmfeed:
            self.program_widgets.pgmfeed.setValidator(regex_validator)
        if hasattr(self.program_widgets, "pgmlaserpower") and self.program_widgets.pgmlaserpower:
            self.program_widgets.pgmlaserpower.setValidator(regex_validator)
        if hasattr(self.program_widgets, "pgmlaserfreq") and self.program_widgets.pgmlaserfreq:
            self.program_widgets.pgmlaserfreq.setValidator(regex_validator)

    
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
        widget_list.append(self.wh.configWidget(self, QPushButton, "powersetgalvoPushButton_2", "clicked", self.printGalvoAction, role="powersetgalvo"))
        widget_list.append(self.wh.configWidget(self, QPushButton, "freqsetgalvoPushButton", "clicked", self.printGalvoAction, role="freqsetgalvo"))
        
        self.util.dedupeList(widget_list)
        self.laserconfgalvo_widgets = self.wh.createMap(*widget_list)
        
        # Configure Laser Frequency Controls (20 kHz to 80 kHz)
        if hasattr(self.ui, 'galvolaserfreqHorizontalSlider'):
            self.ui.galvolaserfreqHorizontalSlider.setRange(20, 80)
            self.ui.galvolaserfreqHorizontalSlider.setSingleStep(1)
            freq_val = self.ui.galvolaserfreqHorizontalSlider.value()
            if freq_val < 20 or freq_val > 80:
                freq_val = 30
                self.ui.galvolaserfreqHorizontalSlider.setValue(freq_val)
            if hasattr(self.ui, 'laserfreqLineEdit'):
                self.ui.laserfreqLineEdit.setText(str(freq_val))
                
        if hasattr(self.ui, 'laserfreqLineEdit'):
            self.ui.laserfreqLineEdit.setValidator(QIntValidator(20, 80, self))
            self.ui.laserfreqLineEdit.setPlaceholderText("20-80")
            self.ui.laserfreqLineEdit.setToolTip("Laser Frequency: 20 kHz to 80 kHz")
            
        if hasattr(self.ui, 'label_32'):
            self.ui.label_32.setText("Laser Freq (kHz):")

        # Configure Laser Power Controls (0% to 100%)
        if hasattr(self.ui, 'galvolaserpowerHorizontalSlider_2'):
            self.ui.galvolaserpowerHorizontalSlider_2.setRange(0, 100)
            pwr_val = self.ui.galvolaserpowerHorizontalSlider_2.value()
            if hasattr(self.ui, 'laserpowerLineEdit'):
                self.ui.laserpowerLineEdit.setText(str(pwr_val))
        if hasattr(self.ui, 'laserpowerLineEdit'):
            self.ui.laserpowerLineEdit.setValidator(QIntValidator(0, 100, self))
            self.ui.laserpowerLineEdit.setPlaceholderText("0-100")
            self.ui.laserpowerLineEdit.setToolTip("Laser Power: 0% to 100%")
        if hasattr(self.ui, 'label_108'):
            self.ui.label_108.setText("Laser Power (%):")
            
        # Ensure the laser button is enabled
        if hasattr(self.ui, 'flasergalvoPushButton'):
            self.ui.flasergalvoPushButton.setEnabled(True)
            
        if hasattr(self.ui, 'freddotlasergalvoPushButton'):
            self.ui.freddotlasergalvoPushButton.setEnabled(True)
            
        if hasattr(self.ui, 'galvoobjheightLineEdit'):
            self.ui.galvoobjheightLineEdit.setValidator(QDoubleValidator(-1000.0, 1000.0, 3, self))
            self.ui.galvoobjheightLineEdit.returnPressed.connect(self.save_galvoobjheight_to_config)

    def update_galvo_focus_calculations(self):
        try:
            focus_z_str = self.ch.getValues("focus", "galvo_z_focus")
            focus_z = float(focus_z_str) if focus_z_str else 0.0
        except Exception:
            focus_z = 0.0
            
        try:
            galvoobjheight = float(self.ui.galvoobjheightLineEdit.text() or 0.0)
        except Exception:
            galvoobjheight = 0.0
            
        try:
            galvosampleheight = float(self.ui.pgmheightgalvoLineEdit.text() or 0.0)
        except Exception:
            galvosampleheight = 0.0
            
        finalobjectfocus = focus_z - galvoobjheight
        finalgalvofocus = finalobjectfocus + galvosampleheight
        
        self.ch.addParameter("focus", "galvoobjheight", f"{galvoobjheight:.2f}")
        self.ch.addParameter("focus", "galvosampleheight", f"{galvosampleheight:.2f}")
        self.ch.addParameter("focus", "finalobjectfocus", f"{finalobjectfocus:.2f}")
        self.ch.addParameter("focus", "finalgalvofocus", f"{finalgalvofocus:.2f}")
        
        if hasattr(self, 'config_file_path'):
            self.ch.updateFile(self.config_file_path)

    def save_galvoobjheight_to_config(self):
        try:
            val = float(self.ui.galvoobjheightLineEdit.text() or 0.0)
        except ValueError:
            val = 0.0
        self.update_galvo_focus_calculations()
        self.showAutoCloseMessage("Saved", f"Object height saved as {val:.2f} mm.")

    def setupMapMatrix(self):
        widget_list = []
        widget_list.append(self.wh.configWidget(self, QLineEdit, "powstartLineEdit", role="powstart"))
        widget_list.append(self.wh.configWidget(self, QLineEdit, "powendLineEdit", role="powend"))
        widget_list.append(self.wh.configWidget(self, QLineEdit, "powstepsLineEdit", role="powsteps"))
        widget_list.append(self.wh.configWidget(self, QLineEdit, "freqstartLineEdit", role="freqstart"))
        widget_list.append(self.wh.configWidget(self, QLineEdit, "freqendLineEdit", role="freqend"))
        widget_list.append(self.wh.configWidget(self, QLineEdit, "freqstepsLineEdit", role="freqsteps"))
        widget_list.append(self.wh.configWidget(self, QLineEdit, "cellwidthLineEdit", role="cellwidth"))
        widget_list.append(self.wh.configWidget(self, QLineEdit, "cellheightLineEdit", role="cellheight"))
        widget_list.append(self.wh.configWidget(self, QLineEdit, "cellgapxLineEdit", role="cellgapx"))
        widget_list.append(self.wh.configWidget(self, QLineEdit, "cellgapyLineEdit", role="cellgapy"))
        widget_list.append(self.wh.configWidget(self, QComboBox, "cellfilltypeComboBox", role="cellfilltype"))
        widget_list.append(self.wh.configWidget(self, QCheckBox, "celllabelaxisCheckBox", role="celllabelaxis"))
        widget_list.append(self.wh.configWidget(self, QPushButton, "redmarkmatPushButton", "clicked", self.mapmatrixAction, role="redmarkmat"))
        widget_list.append(self.wh.configWidget(self, QPushButton, "lasermarkmatPushButton", "clicked", self.mapmatrixAction, role="lasermarkmat"))
        widget_list.append(self.wh.configWidget(self, QPushButton, "stopmatPushButton", "clicked", self.mapmatrixAction, role="stopmat"))
        widget_list.append(self.wh.configWidget(self, QFrame, "mappmatrixgalvoFrame", role="mappmatrixgalvo"))
        
        self.util.dedupeList(widget_list)
        self.mapmatrix_widgets = self.wh.createMap(*widget_list)
        
        # Apply input validations
        double_validator = QDoubleValidator(-10000.0, 10000.0, 3, self)
        int_validator = QIntValidator(-10000, 10000, self)
        
        for field in ["powstart", "powend", "powsteps", "freqstart", "freqend", "freqsteps"]:
            if hasattr(self.mapmatrix_widgets, field) and getattr(self.mapmatrix_widgets, field):
                getattr(self.mapmatrix_widgets, field).setValidator(int_validator)
                
        for field in ["cellwidth", "cellheight", "cellgapx", "cellgapy"]:
            if hasattr(self.mapmatrix_widgets, field) and getattr(self.mapmatrix_widgets, field):
                getattr(self.mapmatrix_widgets, field).setValidator(double_validator)
        
    def initMapMatrix(self):
        from mapping_controller import ParameterMappingController
        self.mapping_controller = ParameterMappingController(self)
    
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
        
        # Setup Deep Engraving UI directly below widget_26 (Enable Hatching)
        self.setupEngravingUI()
        
        # Apply input validations
        double_validator = QDoubleValidator(-10000.0, 10000.0, 4, self)
        int_validator = QIntValidator(-10000, 1000000, self)
        
        double_fields = ["pgmheightgalvo", "pgmstartposx", "pgmstartposy", "pgmangle", "pgmlinespace", "pgmedgeoff", "pgmstartoff", "pgmendoff", "pgmlinered", "pgmloopdist", "pgmautorotangl"]
        int_fields = ["pgmmarkspeedgalvo", "pgmjumpspeed", "pgmloopcount", "pgmcount", "pgmnumloops"]
        
        for field in double_fields:
            if hasattr(self.programgalvo_widgets, field) and getattr(self.programgalvo_widgets, field):
                getattr(self.programgalvo_widgets, field).setValidator(double_validator)
                
        for field in int_fields:
            if hasattr(self.programgalvo_widgets, field) and getattr(self.programgalvo_widgets, field):
                getattr(self.programgalvo_widgets, field).setValidator(int_validator)

        # Allow typing, pasting, and direct entry in pgmfilegalvoTextEdit
        if hasattr(self.ui, 'pgmfilegalvoTextEdit'):
            self.ui.pgmfilegalvoTextEdit.setReadOnly(False)
            self.ui.pgmfilegalvoTextEdit.setPlaceholderText("Select file with SELECT button, paste path here, or drag & drop...")
            self.ui.pgmfilegalvoTextEdit.textChanged.connect(self._on_pgmfile_text_edited)

    def setupPrintGalvo(self):
        from PySide6.QtWidgets import QPushButton, QHBoxLayout, QLabel, QLineEdit, QCheckBox
        widget_list = []
        widget_list.append(self.wh.configWidget(self, QPushButton, "printrungalvoPushButton", "clicked", self.printGalvoAction, role="printrungalvo"))
        widget_list.append(self.wh.configWidget(self, QPushButton, "printabortgalvoPushButton", "clicked", self.printGalvoAction, role="printabortgalvo"))
        widget_list.append(self.wh.configWidget(self, QPushButton, "redlightprePushButton", "clicked", self.printGalvoAction, role="redlightpre"))
        widget_list.append(self.wh.configWidget(self, QPushButton, "printpausePushButton", "clicked", self.printGalvoAction, role="printpausegalvo"))
        self.util.dedupeList(widget_list)
        self.printgalvo_widgets = self.wh.createMap(*widget_list)
        self.ui.redlightprePushButton.setText("START")
        
        # Serial Number UI
        sn_layout = QHBoxLayout()
        
        self.cb_use_serial = QCheckBox("Use Serial Number")
        self.cb_use_serial.setStyleSheet("color: white; font-weight: bold;")
        sn_layout.addWidget(self.cb_use_serial)
        
        self.serial_number_input = QLineEdit()
        self.serial_number_input.setPlaceholderText("SN-001")
        self.serial_number_input.setStyleSheet("background-color: #2c3e50; color: white; border: 1px solid #34495e; padding: 5px;")
        self.serial_number_input.setMinimumWidth(150)
        self.serial_number_input.setMaximumWidth(250)
        self.serial_number_input.setEnabled(False)  # Disabled by default
        
        self.cb_use_serial.toggled.connect(self.serial_number_input.setEnabled)
        
        sn_layout.addWidget(self.serial_number_input)
        sn_layout.addStretch()
        
        # Insert at the top of the print page layout
        if hasattr(self.ui, 'printgalvoPage') and self.ui.printgalvoPage.layout():
            self.ui.printgalvoPage.layout().insertLayout(0, sn_layout)
        

        from PySide6.QtGui import QShortcut, QKeySequence
        self.f1_shortcut = QShortcut(QKeySequence("F1"), self)
        self.f1_shortcut.activated.connect(self.handle_f1_shortcut)
        
        self.f2_shortcut = QShortcut(QKeySequence("F2"), self)
        self.f2_shortcut.activated.connect(self.handle_f2_shortcut)

        self.f3_shortcut = QShortcut(QKeySequence("F3"), self)
        self.f3_shortcut.activated.connect(self.handle_f3_shortcut)

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

    def handle_f3_shortcut(self):
        if hasattr(self.ui, 'printpausePushButton') and self.ui.printpausePushButton.isEnabled():
            self.printGalvoAction(self.ui.printpausePushButton)

    def updateGalvoPauseUI(self, is_paused=False, enabled=None):
        from PySide6.QtGui import QIcon
        if hasattr(self.ui, 'printpausePushButton'):
            btn = self.ui.printpausePushButton
            if enabled is not None:
                btn.setEnabled(enabled)
            if is_paused:
                btn.setToolTip("Resume (F3)")
                btn.setIcon(QIcon(":/icons/icons/play.svg"))
            else:
                btn.setToolTip("Pause (F3)")
                btn.setIcon(QIcon(":/icons/icons/pause.svg"))


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

        # Apply input validations
        double_validator = QDoubleValidator(-10000.0, 10000.0, 4, self)
        
        double_fields = ["fieldsizeconf", "offxconf", "offyconf", "angleconf", 
                         "confscalegalvo1", "confbargalvo1", "confpargalvo1", "conftrapgalvo1",
                         "confscalegalvo2", "confbargalvo2", "confpargalvo2", "conftrapgalvo2",
                         "confxmark", "confymark"]
                         
        for field in double_fields:
            if hasattr(self.configgalvo_widgets, field) and getattr(self.configgalvo_widgets, field):
                getattr(self.configgalvo_widgets, field).setValidator(double_validator)

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
#         self.wh.invokeMethod(self.left_menu_widgets.laserconfgalvo, "hide")
        self.wh.invokeMethod(self.center_menu_widgets.settings, "hide")
        if hasattr(self.ui, 'testpatterngalvoFrame'):
            self.wh.invokeMethod(self.ui.testpatterngalvoFrame, "hide")
        
    def initMainPages(self):
        self.main_page_dict = {}
        self.main_page_dict["joggalvo"] = 0
        self.main_page_dict["laserconfgalvo"] = 1
        self.main_page_dict["programsgalvo"] = 2
        self.main_page_dict["printgalvo"] = 3
        self.main_page_dict["configgalvo"] = 4
        self.main_page_dict["terminal"] = 5
        self.main_page_dict["ezcad"] = 6
        self.main_page_dict["parametermatrix"] = 7
        self.main_page_dict["text"] = 8
        self.main_page_dict["qr"] = 9
        self.main_page_dict["cad"] = 10
        self.main_page_dict["cadgalvo"] = 10
        self.main_page_dict["cadPage"] = 10

    
    def initInfoPages(self):
        pass
    
    def initSettings(self):
        conf_name = "index"
        self.xindex = float(self.ch.getValues(conf_name, "xindex") or 0.0)
        self.yindex = float(self.ch.getValues(conf_name, "yindex") or 0.0)

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

    
    def setupEngravingUI(self):
        """
        Creates and embeds the Deep Engraving / 2.5D Multi-layer controls into the Program Page,
        directly below widget_26 (Enable Hatching).
        """
        if not hasattr(self.ui, 'verticalLayout_64') or not hasattr(self.ui, 'widget_26'):
            return

        # Container Widget
        self.engraving_container = QWidget()
        eng_layout = QVBoxLayout(self.engraving_container)
        eng_layout.setContentsMargins(0, 4, 0, 4)
        eng_layout.setSpacing(6)

        # Style definitions matching the interface.ui palette
        lbl_style = "color: rgb(16, 42, 131); font-weight: bold; font-size: 13pt;"
        unit_style = "color: rgb(16, 42, 131); font-weight: bold; font-size: 13pt;"
        edit_style = (
            "QLineEdit {"
            " border: 2px solid #102a83;"
            " border-radius: 6px;"
            " padding: 4px;"
            " color: #102a83;"
            " font-weight: bold;"
            " font-size: 13pt;"
            " background-color: #ffffff;"
            "}"
        )
        combo_style = (
            "QComboBox {"
            " border: 2px solid #102a83;"
            " border-radius: 6px;"
            " padding: 4px 8px;"
            " color: #102a83;"
            " font-weight: bold;"
            " font-size: 12pt;"
            " background-color: #ffffff;"
            " min-height: 32px;"
            "}"
            "QComboBox QAbstractItemView {"
            " color: #102a83;"
            " background-color: #ffffff;"
            " selection-background-color: #a7c6e5;"
            " selection-color: #102a83;"
            " font-size: 12pt;"
            "}"
        )
        btn_style = (
            "QPushButton {"
            " color: #ffffff;"
            " background-color: #102a83;"
            " border-radius: 8px;"
            " padding: 6px 14px;"
            " font-weight: bold;"
            " font-size: 11pt;"
            "}"
            "QPushButton:hover {"
            " background-color: #a7c6e5;"
            " color: #102a83;"
            "}"
        )

        # --- Row 1: Enable Engraving Toggle Header ---
        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(10)

        lbl_engrave = QLabel("Enable Engraving :")
        lbl_engrave.setStyleSheet(lbl_style)
        header_layout.addWidget(lbl_engrave)

        self.cb_enable_engraving = QCheckBox()
        self.cb_enable_engraving.setCursor(Qt.PointingHandCursor)
        self.cb_enable_engraving.setStyleSheet("QCheckBox::indicator { width: 22px; height: 22px; }")
        header_layout.addWidget(self.cb_enable_engraving)
        header_layout.addStretch()

        eng_layout.addWidget(header_widget)

        # --- Expandable Options Panel ---
        self.engraving_options_widget = QFrame()
        self.engraving_options_widget.setStyleSheet(
            "QFrame {"
            " border: 2px solid #102a83;"
            " border-radius: 10px;"
            " background-color: rgba(16, 42, 131, 0.04);"
            " padding: 8px;"
            "}"
        )
        self.engraving_options_widget.setVisible(False)
        options_layout = QVBoxLayout(self.engraving_options_widget)
        options_layout.setSpacing(10)

        # Row A: Material Selection & Custom Add Button
        row_mat = QHBoxLayout()
        lbl_mat = QLabel("Material Preset :")
        lbl_mat.setStyleSheet(lbl_style)
        lbl_mat.setFixedWidth(160)
        row_mat.addWidget(lbl_mat)

        self.combo_engrave_material = QComboBox()
        self.combo_engrave_material.setStyleSheet(combo_style)
        self.combo_engrave_material.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.reload_engraving_materials()
        row_mat.addWidget(self.combo_engrave_material)

        self.btn_save_custom_material = QPushButton("+ Save As New Preset")
        self.btn_save_custom_material.setStyleSheet(btn_style)
        self.btn_save_custom_material.setCursor(Qt.PointingHandCursor)
        self.btn_save_custom_material.clicked.connect(self.on_save_new_material_preset)
        row_mat.addWidget(self.btn_save_custom_material)
        options_layout.addLayout(row_mat)

        # Row B: Substrate / Object Height & Target Engraving Depth
        row_depth = QHBoxLayout()
        lbl_obj = QLabel("Substrate Height :")
        lbl_obj.setStyleSheet(lbl_style)
        lbl_obj.setFixedWidth(160)
        row_depth.addWidget(lbl_obj)

        self.input_engrave_obj_height = QLineEdit("0.0")
        self.input_engrave_obj_height.setStyleSheet(edit_style)
        self.input_engrave_obj_height.setAlignment(Qt.AlignCenter)
        self.input_engrave_obj_height.setValidator(QDoubleValidator(0.0, 150.0, 3, self))
        row_depth.addWidget(self.input_engrave_obj_height)

        u1 = QLabel("mm")
        u1.setStyleSheet(unit_style)
        row_depth.addWidget(u1)

        row_depth.addSpacing(15)

        lbl_target = QLabel("Target Depth :")
        lbl_target.setStyleSheet(lbl_style)
        row_depth.addWidget(lbl_target)

        self.input_engrave_depth = QLineEdit("1.0")
        self.input_engrave_depth.setStyleSheet(edit_style)
        self.input_engrave_depth.setAlignment(Qt.AlignCenter)
        self.input_engrave_depth.setValidator(QDoubleValidator(0.01, 5.0, 3, self))
        row_depth.addWidget(self.input_engrave_depth)

        u2 = QLabel("mm")
        u2.setStyleSheet(unit_style)
        row_depth.addWidget(u2)
        options_layout.addLayout(row_depth)

        # Row C: Z-Drop Step per Pass & Calculated Loops
        row_step = QHBoxLayout()
        lbl_step = QLabel("Z-Drop Step :")
        lbl_step.setStyleSheet(lbl_style)
        lbl_step.setFixedWidth(160)
        row_step.addWidget(lbl_step)

        self.input_engrave_step = QLineEdit("0.05")
        self.input_engrave_step.setStyleSheet(edit_style)
        self.input_engrave_step.setAlignment(Qt.AlignCenter)
        self.input_engrave_step.setValidator(QDoubleValidator(0.005, 0.5, 4, self))
        row_step.addWidget(self.input_engrave_step)

        u3 = QLabel("mm")
        u3.setStyleSheet(unit_style)
        row_step.addWidget(u3)

        row_step.addSpacing(15)

        lbl_calc = QLabel("Total Passes :")
        lbl_calc.setStyleSheet(lbl_style)
        row_step.addWidget(lbl_calc)

        self.label_engrave_loops = QLabel("20 Passes (1.00 mm)")
        self.label_engrave_loops.setStyleSheet("color: #0b6623; font-weight: bold; font-size: 13pt; background: #e8f5e9; border: 1px solid #0b6623; border-radius: 6px; padding: 4px 10px;")
        self.label_engrave_loops.setAlignment(Qt.AlignCenter)
        row_step.addWidget(self.label_engrave_loops)
        options_layout.addLayout(row_step)

        # Row D: Engraving Pattern / Style & Hatch Pitch
        row_style = QHBoxLayout()
        lbl_style_title = QLabel("Engrave Pattern :")
        lbl_style_title.setStyleSheet(lbl_style)
        lbl_style_title.setFixedWidth(160)
        row_style.addWidget(lbl_style_title)

        self.combo_engrave_style = QComboBox()
        self.combo_engrave_style.setStyleSheet(combo_style)
        self.combo_engrave_style.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.combo_engrave_style.addItems(EngravingManager.ALL_STYLES)
        row_style.addWidget(self.combo_engrave_style)

        row_style.addSpacing(15)

        lbl_pitch = QLabel("Hatch Pitch :")
        lbl_pitch.setStyleSheet(lbl_style)
        row_style.addWidget(lbl_pitch)

        self.input_engrave_pitch = QLineEdit("0.04")
        self.input_engrave_pitch.setStyleSheet(edit_style)
        self.input_engrave_pitch.setAlignment(Qt.AlignCenter)
        self.input_engrave_pitch.setValidator(QDoubleValidator(0.005, 0.5, 4, self))
        self.input_engrave_pitch.setFixedWidth(80)
        row_style.addWidget(self.input_engrave_pitch)

        u4 = QLabel("mm")
        u4.setStyleSheet(unit_style)
        row_style.addWidget(u4)
        options_layout.addLayout(row_style)

        eng_layout.addWidget(self.engraving_options_widget)

        # =========================================================================
        # Row 2: Enable 3D Relief Engraving Toggle Header
        # =========================================================================
        header_3d_widget = QWidget()
        header_3d_layout = QHBoxLayout(header_3d_widget)
        header_3d_layout.setContentsMargins(0, 8, 0, 0)
        header_3d_layout.setSpacing(10)

        lbl_3d = QLabel("Enable 3D Relief Engraving :")
        lbl_3d.setStyleSheet("color: #0b6623; font-weight: bold; font-size: 13pt;")
        header_3d_layout.addWidget(lbl_3d)

        self.cb_enable_3d_engraving = QCheckBox()
        self.cb_enable_3d_engraving.setCursor(Qt.PointingHandCursor)
        self.cb_enable_3d_engraving.setStyleSheet("QCheckBox::indicator { width: 22px; height: 22px; }")
        header_3d_layout.addWidget(self.cb_enable_3d_engraving)
        header_3d_layout.addStretch()

        eng_layout.addWidget(header_3d_widget)

        # Material-specific calibrated 3D relief presets
        self.MATERIAL_3D_PRESETS = {
            "Brass Blank (~1.8 mm)": {
                "max_depth": 0.75,
                "passes": 65,
                "pitch": 0.025,
                "power": 65.0,
                "freq": 35.0,
                "mark_speed": 600.0,
                "jump_speed": 2000.0,
                "clean_enabled": True,
                "clean_interval": 6,
                "desc": "Calibrated for 27mm 1.8mm brass coin dies & bas-relief"
            },
            "Brass Sheet (1.0 mm)": {
                "max_depth": 0.45,
                "passes": 45,
                "pitch": 0.025,
                "power": 55.0,
                "freq": 38.0,
                "mark_speed": 650.0,
                "jump_speed": 2000.0,
                "clean_enabled": True,
                "clean_interval": 5,
                "desc": "Safe low-heat relief for 1.0mm brass sheets"
            },
            "Copper Blank / Sheet (~1.8 mm)": {
                "max_depth": 0.60,
                "passes": 70,
                "pitch": 0.020,
                "power": 82.0,
                "freq": 28.0,
                "mark_speed": 450.0,
                "jump_speed": 2000.0,
                "clean_enabled": True,
                "clean_interval": 5,
                "desc": "High power density for reflective copper"
            },
            "Stainless Steel / Steel (~1.8 mm)": {
                "max_depth": 0.80,
                "passes": 80,
                "pitch": 0.020,
                "power": 75.0,
                "freq": 30.0,
                "mark_speed": 700.0,
                "jump_speed": 2000.0,
                "clean_enabled": False,
                "clean_interval": 10,
                "desc": "Ultra-fine detail micro-ablation for steel dies"
            },
            "Aluminum Blank (~1.8 mm)": {
                "max_depth": 0.85,
                "passes": 40,
                "pitch": 0.030,
                "power": 68.0,
                "freq": 40.0,
                "mark_speed": 800.0,
                "jump_speed": 2500.0,
                "clean_enabled": False,
                "clean_interval": 0,
                "desc": "Fast volumetric ablation for aluminum alloys"
            },
            "Silver / Gold (Precious Metal)": {
                "max_depth": 0.50,
                "passes": 55,
                "pitch": 0.022,
                "power": 70.0,
                "freq": 32.0,
                "mark_speed": 500.0,
                "jump_speed": 2000.0,
                "clean_enabled": True,
                "clean_interval": 5,
                "desc": "Precious bullion coin & jewelry relief"
            },
            "Titanium / Tool Steel": {
                "max_depth": 0.60,
                "passes": 90,
                "pitch": 0.018,
                "power": 80.0,
                "freq": 25.0,
                "mark_speed": 550.0,
                "jump_speed": 2000.0,
                "clean_enabled": False,
                "clean_interval": 8,
                "desc": "Hardened alloy stamping die relief"
            },
            "Custom Metal (Manual Settings)": {
                "max_depth": 0.75,
                "passes": 50,
                "pitch": 0.025,
                "power": 70.0,
                "freq": 35.0,
                "mark_speed": 600.0,
                "jump_speed": 2000.0,
                "clean_enabled": True,
                "clean_interval": 6,
                "desc": "Manual custom user configuration"
            }
        }

        self.RESOLUTION_3D_TIERS = MainWindow.RESOLUTION_3D_TIERS

        # --- Expandable 3D Relief Options Panel ---
        self.engraving_3d_options_widget = QFrame()
        self.engraving_3d_options_widget.setStyleSheet(
            "QFrame {"
            " border: 2px solid #0b6623;"
            " border-radius: 10px;"
            " background-color: rgba(11, 102, 35, 0.04);"
            " padding: 8px;"
            "}"
        )
        self.engraving_3d_options_widget.setVisible(True)
        options_3d_layout = QVBoxLayout(self.engraving_3d_options_widget)
        options_3d_layout.setSpacing(10)

        # Row 3D-A: Mode Selector
        row_3d_mode = QHBoxLayout()
        lbl_3d_mode = QLabel("Relief Slicing Mode :")
        lbl_3d_mode.setStyleSheet("color: #0b6623; font-weight: bold; font-size: 13pt;")
        lbl_3d_mode.setFixedWidth(160)
        row_3d_mode.addWidget(lbl_3d_mode)

        self.combo_3d_mode = QComboBox()
        self.combo_3d_mode.setStyleSheet(combo_style)
        self.combo_3d_mode.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.combo_3d_mode.addItems([
            "3D Coin Relief (Continuous 50-Pass Slicing, 27mm)",
            "3D Mesh / STL Relief (Direct STL Slicing)",
            "Imported Sliced G-Code Relief (*.gcode, *.nc)",
            "Multi-Layer Vector Step Relief (Layers 00 to 05)",
            "Custom 16-Bit Heightmap File (.png, .bmp, .tiff)"
        ])
        row_3d_mode.addWidget(self.combo_3d_mode)
        options_3d_layout.addLayout(row_3d_mode)

        # Row 3D-B2: Selected 3D / G-Code File row with dedicated Browse button
        row_3d_file = QHBoxLayout()
        lbl_3d_file = QLabel("3D / G-Code File :")
        lbl_3d_file.setStyleSheet("color: #0b6623; font-weight: bold; font-size: 13pt;")
        lbl_3d_file.setFixedWidth(160)
        row_3d_file.addWidget(lbl_3d_file)

        self.input_3d_filepath = QLineEdit()
        self.input_3d_filepath.setPlaceholderText("Select file with Browse button, or paste path...")
        self.input_3d_filepath.setStyleSheet(edit_style)
        self.input_3d_filepath.returnPressed.connect(self._on_3d_filepath_entered)
        row_3d_file.addWidget(self.input_3d_filepath)

        self.btn_3d_browse = QPushButton("📂 Browse G-Code / 3D File")
        self.btn_3d_browse.setStyleSheet(
            "QPushButton { background-color: #0b6623; color: white; border-radius: 6px; padding: 6px 14px; font-weight: bold; font-size: 11pt; } "
            "QPushButton:hover { background-color: #084d1a; }"
        )
        self.btn_3d_browse.clicked.connect(self.browse_3d_model_file)
        row_3d_file.addWidget(self.btn_3d_browse)

        options_3d_layout.addLayout(row_3d_file)

        # Row 3D-C: Substrate Thickness, Max Depth & Target Relief Size
        row_3d_depth = QHBoxLayout()
        lbl_3d_mat = QLabel("Material Substrate :")
        lbl_3d_mat.setStyleSheet("color: #0b6623; font-weight: bold; font-size: 13pt;")
        lbl_3d_mat.setFixedWidth(160)
        row_3d_depth.addWidget(lbl_3d_mat)

        self.combo_3d_material = QComboBox()
        self.combo_3d_material.setStyleSheet(combo_style)
        self.combo_3d_material.addItems(list(self.MATERIAL_3D_PRESETS.keys()))
        row_3d_depth.addWidget(self.combo_3d_material)

        row_3d_depth.addSpacing(15)

        lbl_3d_depth = QLabel("Max Relief Depth :")
        lbl_3d_depth.setStyleSheet("color: #0b6623; font-weight: bold; font-size: 13pt;")
        row_3d_depth.addWidget(lbl_3d_depth)

        self.input_3d_max_depth = QLineEdit("0.75")
        self.input_3d_max_depth.setStyleSheet(edit_style)
        self.input_3d_max_depth.setAlignment(Qt.AlignCenter)
        self.input_3d_max_depth.setFixedWidth(70)
        row_3d_depth.addWidget(self.input_3d_max_depth)

        u_3d_1 = QLabel("mm")
        u_3d_1.setStyleSheet("color: #0b6623; font-weight: bold; font-size: 13pt;")
        row_3d_depth.addWidget(u_3d_1)

        row_3d_depth.addSpacing(15)

        lbl_3d_size = QLabel("Relief Size (Dia/Span) :")
        lbl_3d_size.setStyleSheet("color: #0b6623; font-weight: bold; font-size: 13pt;")
        row_3d_depth.addWidget(lbl_3d_size)

        self.input_3d_size = QLineEdit("27.0")
        self.input_3d_size.setStyleSheet(edit_style)
        self.input_3d_size.setAlignment(Qt.AlignCenter)
        self.input_3d_size.setFixedWidth(70)
        self.input_3d_size.setToolTip("Target Diameter (for coins) or Width/Span in mm")
        row_3d_depth.addWidget(self.input_3d_size)

        u_3d_sz = QLabel("mm")
        u_3d_sz.setStyleSheet("color: #0b6623; font-weight: bold; font-size: 13pt;")
        row_3d_depth.addWidget(u_3d_sz)

        options_3d_layout.addLayout(row_3d_depth)

        # Row 3D-C2: Resolution / Quality Selector (100 passes, 250 passes, 500 passes)
        row_3d_res = QHBoxLayout()
        lbl_3d_res = QLabel("Resolution (Passes) :")
        lbl_3d_res.setStyleSheet("color: #0b6623; font-weight: bold; font-size: 13pt; background-color: #e8f5e9; border: 1.5px solid #0b6623; border-radius: 5px; padding: 2px 6px;")
        lbl_3d_res.setFixedWidth(160)
        row_3d_res.addWidget(lbl_3d_res)

        self.combo_3d_resolution = QComboBox()
        self.combo_3d_resolution.setStyleSheet(combo_style)
        self.combo_3d_resolution.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.combo_3d_resolution.addItems(list(self.RESOLUTION_3D_TIERS.keys()))
        def_res_idx = self.combo_3d_resolution.findText("Medium Detail (~250 Passes - Balanced)")
        if def_res_idx >= 0:
            self.combo_3d_resolution.setCurrentIndex(def_res_idx)
        row_3d_res.addWidget(self.combo_3d_resolution)
        options_3d_layout.addLayout(row_3d_res)

        # Row 3D-D: Passes & Pitch & Soot Clean
        row_3d_passes = QHBoxLayout()
        lbl_3d_passes = QLabel("Total Slices/Passes :")
        lbl_3d_passes.setStyleSheet("color: #0b6623; font-weight: bold; font-size: 13pt;")
        lbl_3d_passes.setFixedWidth(160)
        row_3d_passes.addWidget(lbl_3d_passes)

        self.input_3d_passes = QLineEdit("50")
        self.input_3d_passes.setStyleSheet(edit_style)
        self.input_3d_passes.setAlignment(Qt.AlignCenter)
        self.input_3d_passes.setFixedWidth(70)
        row_3d_passes.addWidget(self.input_3d_passes)

        row_3d_passes.addSpacing(15)

        lbl_3d_pitch = QLabel("Hatch Pitch :")
        lbl_3d_pitch.setStyleSheet("color: #0b6623; font-weight: bold; font-size: 13pt;")
        row_3d_passes.addWidget(lbl_3d_pitch)

        self.input_3d_pitch = QLineEdit("0.025")
        self.input_3d_pitch.setStyleSheet(edit_style)
        self.input_3d_pitch.setAlignment(Qt.AlignCenter)
        self.input_3d_pitch.setFixedWidth(70)
        row_3d_passes.addWidget(self.input_3d_pitch)

        u_3d_2 = QLabel("mm")
        u_3d_2.setStyleSheet("color: #0b6623; font-weight: bold; font-size: 13pt;")
        row_3d_passes.addWidget(u_3d_2)

        row_3d_passes.addSpacing(15)

        self.cb_3d_clean = QCheckBox("Brass De-Oxidation Clean (Every 6 Passes)")
        self.cb_3d_clean.setChecked(True)
        self.cb_3d_clean.setStyleSheet("color: #0b6623; font-weight: bold; font-size: 12pt;")
        row_3d_passes.addWidget(self.cb_3d_clean)
        options_3d_layout.addLayout(row_3d_passes)

        # Row 3D-D2: Advanced Toolpath Options (Serpentine Hatch, Contour Cleanup, Invert Relief)
        row_3d_opts = QHBoxLayout()
        self.cb_3d_bidirectional = QCheckBox("Serpentine / Bidirectional Hatching")
        self.cb_3d_bidirectional.setChecked(True)
        self.cb_3d_bidirectional.setStyleSheet("color: #0b6623; font-weight: bold; font-size: 11pt;")
        self.cb_3d_bidirectional.setToolTip("Alternating scanlines reduce flyback travel by ~80% and prevent galvo overheating")
        row_3d_opts.addWidget(self.cb_3d_bidirectional)

        row_3d_opts.addSpacing(15)

        self.cb_3d_contour = QCheckBox("Perimeter Contour Cleanup")
        self.cb_3d_contour.setChecked(True)
        self.cb_3d_contour.setStyleSheet("color: #0b6623; font-weight: bold; font-size: 11pt;")
        self.cb_3d_contour.setToolTip("Outline trace on each layer removes stair-stepping scallops on relief edges")
        row_3d_opts.addWidget(self.cb_3d_contour)

        row_3d_opts.addSpacing(15)

        self.cb_3d_invert = QCheckBox("Invert Relief (Stamping Die / Mold)")
        self.cb_3d_invert.setChecked(False)
        self.cb_3d_invert.setStyleSheet("color: #0b6623; font-weight: bold; font-size: 11pt;")
        self.cb_3d_invert.setToolTip("Inverts bas-relief to create female stamping dies and intaglio molds")
        row_3d_opts.addWidget(self.cb_3d_invert)

        row_3d_opts.addStretch()
        options_3d_layout.addLayout(row_3d_opts)

        # Row 3D-E: Quick Action Buttons (Red Light Framing & 3D Preview)
        row_3d_actions = QHBoxLayout()
        self.btn_3d_frame = QPushButton("🔴 3D Red Light Framing")
        self.btn_3d_frame.setStyleSheet("QPushButton { background-color: #d32f2f; color: white; border-radius: 8px; padding: 7px 16px; font-weight: bold; font-size: 12pt; } QPushButton:hover { background-color: #b71c1c; }")
        self.btn_3d_frame.clicked.connect(self.on_3d_frame_clicked)
        row_3d_actions.addWidget(self.btn_3d_frame)

        self.btn_3d_preview = QPushButton("👁️ 3D Bas-Relief Preview")
        self.btn_3d_preview.setStyleSheet("QPushButton { background-color: #0b6623; color: white; border-radius: 8px; padding: 7px 16px; font-weight: bold; font-size: 12pt; } QPushButton:hover { background-color: #084d1a; }")
        self.btn_3d_preview.clicked.connect(self.on_3d_preview_clicked)
        row_3d_actions.addWidget(self.btn_3d_preview)

        row_3d_actions.addStretch()
        options_3d_layout.addLayout(row_3d_actions)

        eng_layout.addWidget(self.engraving_3d_options_widget)

        # Insert directly below widget_26 in verticalLayout_64
        idx = self.ui.verticalLayout_64.indexOf(self.ui.widget_26)
        if idx >= 0:
            self.ui.verticalLayout_64.insertWidget(idx + 1, self.engraving_container)
        else:
            self.ui.verticalLayout_64.addWidget(self.engraving_container)

        # Signal connections
        self.cb_enable_engraving.toggled.connect(self.on_engraving_toggled)
        self.cb_enable_3d_engraving.toggled.connect(self.on_3d_engraving_toggled)
        self.combo_3d_mode.currentIndexChanged.connect(self.on_3d_mode_changed)
        self.combo_3d_material.currentIndexChanged.connect(self.on_3d_material_changed)
        self.combo_3d_resolution.currentIndexChanged.connect(self.on_3d_resolution_changed)
        self.input_3d_max_depth.textChanged.connect(self.on_3d_param_custom_changed)
        self.input_3d_size.textChanged.connect(self.on_3d_param_custom_changed)
        self.cb_3d_bidirectional.toggled.connect(self.on_3d_param_custom_changed)
        self.cb_3d_contour.toggled.connect(self.on_3d_param_custom_changed)
        self.cb_3d_invert.toggled.connect(self.on_3d_param_custom_changed)
        self.input_3d_passes.textChanged.connect(self.on_3d_passes_manually_edited)
        self.input_3d_passes.returnPressed.connect(self.process_galvo_file)
        self.input_3d_pitch.textChanged.connect(self.on_3d_param_custom_changed)
        self.cb_3d_clean.toggled.connect(self.on_3d_param_custom_changed)
        self.combo_engrave_material.currentIndexChanged.connect(self.on_engraving_material_changed)
        self.input_engrave_depth.textChanged.connect(self.update_engraving_calculations)
        self.input_engrave_step.textChanged.connect(self.update_engraving_calculations)
        self.input_engrave_obj_height.textChanged.connect(self.on_engrave_obj_height_changed)
        if hasattr(self.ui, 'pgmheightgalvoLineEdit'):
            self.ui.pgmheightgalvoLineEdit.textChanged.connect(self.on_sample_height_changed_sync)

        # Default 3D Relief Engraving to checked so panel is expanded and visible
        self.cb_enable_3d_engraving.setChecked(True)
        self.engraving_3d_options_widget.setVisible(True)

    def reload_engraving_materials(self):
        if not hasattr(self, 'combo_engrave_material'):
            return
        curr = self.combo_engrave_material.currentText()
        self.combo_engrave_material.blockSignals(True)
        self.combo_engrave_material.clear()
        for mat_name in self.engraving_mgr.presets.keys():
            self.combo_engrave_material.addItem(mat_name)
        if curr and self.combo_engrave_material.findText(curr) >= 0:
            self.combo_engrave_material.setCurrentText(curr)
        self.combo_engrave_material.blockSignals(False)

    def on_engraving_toggled(self, checked):
        if hasattr(self, 'engraving_options_widget'):
            self.engraving_options_widget.setVisible(checked)
        if checked:
            # Sync object height from sample height if available
            if hasattr(self.ui, 'pgmheightgalvoLineEdit') and hasattr(self, 'input_engrave_obj_height'):
                curr_sample = self.ui.pgmheightgalvoLineEdit.text()
                if curr_sample:
                    self.input_engrave_obj_height.setText(curr_sample)
            # Apply current material preset settings
            self.on_engraving_material_changed(self.combo_engrave_material.currentIndex())
            self.update_engraving_calculations()

    def on_engraving_material_changed(self, idx):
        if not hasattr(self, 'combo_engrave_material') or not hasattr(self, 'cb_enable_engraving'):
            return
        mat_name = self.combo_engrave_material.currentText()
        preset = self.engraving_mgr.presets.get(mat_name)
        if not preset:
            return

        # Auto-fill Power
        pwr = preset.get("power", 20.0)
        if hasattr(self.ui, 'pgmlaserpowerLineEdit'):
            self.ui.pgmlaserpowerLineEdit.setText(str(pwr))
        if hasattr(self.ui, 'laserpowerLineEdit'):
            self.ui.laserpowerLineEdit.setText(str(pwr))
        if hasattr(self.ui, 'galvolaserpowerHorizontalSlider_2'):
            self.ui.galvolaserpowerHorizontalSlider_2.setValue(int(float(pwr)))

        # Auto-fill Frequency
        freq = preset.get("frequency", 30.0)
        if hasattr(self.ui, 'pgmlaserfreqLineEdit'):
            self.ui.pgmlaserfreqLineEdit.setText(str(freq))
        if hasattr(self.ui, 'laserfreqLineEdit'):
            self.ui.laserfreqLineEdit.setText(str(freq))
        if hasattr(self.ui, 'galvolaserfreqHorizontalSlider'):
            self.ui.galvolaserfreqHorizontalSlider.setValue(int(float(freq)))

        # Auto-fill Speed
        spd = preset.get("speed", 500.0)
        if hasattr(self.ui, 'pgmmarkspeedgalvoLineEdit'):
            self.ui.pgmmarkspeedgalvoLineEdit.setText(str(int(spd)))

        # Auto-fill Z-Step
        z_step = preset.get("z_step", 0.05)
        if hasattr(self, 'input_engrave_step'):
            self.input_engrave_step.setText(str(z_step))

        # Auto-fill Style & Pitch
        style = preset.get("hatch_style", EngravingManager.STYLE_CROSS_90)
        if hasattr(self, 'combo_engrave_style'):
            self.combo_engrave_style.setCurrentText(style)

        pitch = preset.get("hatch_pitch", 0.04)
        if hasattr(self, 'input_engrave_pitch'):
            self.input_engrave_pitch.setText(str(pitch))

        # Recommended depth
        rec_depth = preset.get("max_depth", 1.0)
        if hasattr(self, 'input_engrave_depth') and (not self.input_engrave_depth.text() or self.input_engrave_depth.text() in ["1.0", "0.0", ""]):
            self.input_engrave_depth.setText(str(rec_depth))

        self.update_engraving_calculations()

    def update_engraving_calculations(self):
        if not hasattr(self, 'input_engrave_depth') or not hasattr(self, 'input_engrave_step'):
            return
        try:
            depth_str = self.input_engrave_depth.text().strip()
            step_str = self.input_engrave_step.text().strip()
            depth = float(depth_str or 0.0)
            step = float(step_str or 0.05)

            # Safety cap
            if depth > 5.0:
                depth = 5.0
                self.input_engrave_depth.setText("5.0")
            if step <= 0.001:
                step = 0.05

            loops = EngravingManager.calculate_loops(depth, step)
            actual_depth = loops * step
            if hasattr(self, 'label_engrave_loops'):
                self.label_engrave_loops.setText(f"{loops} Passes ({actual_depth:.2f} mm)")

            # Sync with main Loop Count
            if hasattr(self, 'programgalvo_widgets') and hasattr(self.programgalvo_widgets, 'pgmloopcount'):
                self.wh.invokeMethod(self.programgalvo_widgets.pgmloopcount, "set", str(loops))
        except Exception:
            pass

    def on_save_new_material_preset(self):
        name, ok = QInputDialog.getText(self, "Save Material Preset", "Enter New Material Preset Name:")
        if not ok or not name.strip():
            return
        name = name.strip()

        try:
            pwr = float(self.ui.pgmlaserpowerLineEdit.text() or 20.0)
        except:
            pwr = 20.0
        try:
            freq = float(self.ui.pgmlaserfreqLineEdit.text() or 30.0)
        except:
            freq = 30.0
        try:
            spd = float(self.ui.pgmmarkspeedgalvoLineEdit.text() or 500.0)
        except:
            spd = 500.0
        try:
            z_step = float(self.input_engrave_step.text() or 0.05)
        except:
            z_step = 0.05
        try:
            depth = float(self.input_engrave_depth.text() or 2.0)
        except:
            depth = 2.0
        try:
            pitch = float(self.input_engrave_pitch.text() or 0.04)
        except:
            pitch = 0.04

        style = self.combo_engrave_style.currentText()

        saved = self.engraving_mgr.add_or_update_preset(
            name=name, power=pwr, frequency=freq, speed=spd,
            z_step=z_step, max_depth=depth, hatch_style=style, hatch_pitch=pitch
        )
        if saved:
            self.reload_engraving_materials()
            self.combo_engrave_material.setCurrentText(name)
            self.showAutoCloseMessage("Preset Saved", f"Material preset '{name}' saved successfully!")

    def on_engrave_obj_height_changed(self, text):
        if hasattr(self.ui, 'pgmheightgalvoLineEdit'):
            if self.ui.pgmheightgalvoLineEdit.text() != text:
                self.ui.pgmheightgalvoLineEdit.setText(text)

    def on_sample_height_changed_sync(self, text):
        if hasattr(self, 'input_engrave_obj_height'):
            if self.input_engrave_obj_height.text() != text:
                self.input_engrave_obj_height.setText(text)

    def on_engraving_depth_progress(self, current_layer, total_layers, current_depth, max_depth):
        self._current_engraving_info = f"Pass {current_layer}/{total_layers} | Depth: {current_depth:.2f} mm / {max_depth:.2f} mm"
        if hasattr(self.ui, 'progressLabel_2'):
            pct = int((current_layer / max(1, total_layers)) * 100)
            self.ui.progressLabel_2.setText(f"{self._current_engraving_info} | {pct}%")

    def on_3d_engraving_toggled(self, checked):
        if hasattr(self, 'engraving_3d_options_widget'):
            self.engraving_3d_options_widget.setVisible(checked)
        if hasattr(self, 'layer_slider_frame'):
            self.layer_slider_frame.setVisible(checked)
        if checked:
            # Mutual exclusion: uncheck 2D engraving to avoid conflicts
            if hasattr(self, 'cb_enable_engraving') and self.cb_enable_engraving.isChecked():
                self.cb_enable_engraving.setChecked(False)
            if hasattr(self, 'combo_3d_material'):
                self.on_3d_material_changed(self.combo_3d_material.currentIndex())
            self._cached_3d_key = None

    def on_3d_material_changed(self, idx):
        if not hasattr(self, 'combo_3d_material'):
            return
        mat_name = self.combo_3d_material.currentText()
        preset = getattr(self, 'MATERIAL_3D_PRESETS', {}).get(mat_name)
        if not preset or mat_name.startswith("Custom"):
            return

        # Check if a resolution tier is active
        res_tier = None
        if hasattr(self, 'combo_3d_resolution'):
            res_tier = getattr(self, 'RESOLUTION_3D_TIERS', {}).get(self.combo_3d_resolution.currentText())

        # Block textChanged signals to avoid premature re-slicing while updating multiple fields
        if hasattr(self, 'input_3d_max_depth'):
            self.input_3d_max_depth.blockSignals(True)
            self.input_3d_max_depth.setText(f"{preset['max_depth']:.2f}")
            self.input_3d_max_depth.blockSignals(False)

        passes = res_tier["passes"] if res_tier else preset['passes']
        pitch = res_tier["pitch"] if res_tier else preset['pitch']

        if hasattr(self, 'input_3d_passes'):
            self.input_3d_passes.blockSignals(True)
            self.input_3d_passes.setText(str(passes))
            self.input_3d_passes.blockSignals(False)

        if hasattr(self, 'input_3d_pitch'):
            self.input_3d_pitch.blockSignals(True)
            self.input_3d_pitch.setText(f"{pitch:.3f}")
            self.input_3d_pitch.blockSignals(False)

        if hasattr(self, 'cb_3d_clean'):
            self.cb_3d_clean.blockSignals(True)
            self.cb_3d_clean.setChecked(preset.get('clean_enabled', True))
            self.cb_3d_clean.blockSignals(False)

        pwr_scale = res_tier.get("power_scale", 1.0) if res_tier else 1.0
        freq_scale = res_tier.get("freq_scale", 1.0) if res_tier else 1.0
        spd_scale = res_tier.get("speed_scale", 1.0) if res_tier else 1.0

        pwr = max(20.0, min(95.0, round(preset['power'] * pwr_scale)))
        freq = max(20.0, min(80.0, round(preset['freq'] * freq_scale)))
        spd = max(100.0, min(2000.0, round(preset['mark_speed'] * spd_scale)))
        jmp = preset['jump_speed']

        # Synchronize laser power and frequency sliders & line edits
        if hasattr(self.ui, 'galvolaserpowerHorizontalSlider_2'):
            self.ui.galvolaserpowerHorizontalSlider_2.setValue(int(pwr))
        if hasattr(self.ui, 'galvolaserfreqHorizontalSlider'):
            self.ui.galvolaserfreqHorizontalSlider.setValue(int(freq))

        if hasattr(self.ui, 'pgmlaserpowerLineEdit'):
            self.ui.pgmlaserpowerLineEdit.setText(str(int(pwr)))
        if hasattr(self.ui, 'pgmlaserfreqLineEdit'):
            self.ui.pgmlaserfreqLineEdit.setText(str(int(freq)))
        if hasattr(self.ui, 'laserpowerLineEdit'):
            self.ui.laserpowerLineEdit.setText(str(int(pwr)))
        if hasattr(self.ui, 'laserfreqLineEdit'):
            self.ui.laserfreqLineEdit.setText(str(int(freq)))

        if hasattr(self.ui, 'pgmmarkspeedgalvoLineEdit'):
            self.ui.pgmmarkspeedgalvoLineEdit.setText(str(int(spd)))
        if hasattr(self.ui, 'pgmjumpspeedLineEdit'):
            self.ui.pgmjumpspeedLineEdit.setText(str(int(jmp)))

        if hasattr(self, 'galvo_controller'):
            self.galvo_controller.live_power = pwr
            self.galvo_controller.live_freq = freq

        self.showAutoCloseMessage(
            "Material Profile Applied",
            f"<b>{mat_name}</b><br>"
            f"Relief Depth: <b>{preset['max_depth']:.2f} mm</b> | Slices: <b>{passes} Passes</b><br>"
            f"Power: <b>{pwr:.0f}%</b> | Freq: <b>{freq:.0f} kHz</b> | Speed: <b>{spd:.0f} mm/s</b><br>"
            f"Hatch Pitch: <b>{pitch*1000:.0f} µm</b> ({preset['desc']})",
            timeout_ms=3500
        )

        self._cached_3d_key = None

    def on_3d_resolution_changed(self, idx):
        if not hasattr(self, 'combo_3d_resolution'):
            return
        res_name = self.combo_3d_resolution.currentText()
        preset = getattr(self, 'RESOLUTION_3D_TIERS', {}).get(res_name)
        if not preset or res_name.startswith("Custom"):
            return

        passes = preset["passes"]
        pitch = preset["pitch"]

        # Block textChanged signals to avoid premature re-slicing while updating multiple fields
        if hasattr(self, 'input_3d_passes'):
            self.input_3d_passes.blockSignals(True)
            self.input_3d_passes.setText(str(passes))
            self.input_3d_passes.blockSignals(False)

        if hasattr(self, 'input_3d_pitch'):
            self.input_3d_pitch.blockSignals(True)
            self.input_3d_pitch.setText(f"{pitch:.3f}")
            self.input_3d_pitch.blockSignals(False)

        # Adapt laser power, freq, and speed based on material and resolution tier
        mat_name = self.combo_3d_material.currentText() if hasattr(self, 'combo_3d_material') else "Brass Blank (~1.8 mm)"
        mat_preset = getattr(self, 'MATERIAL_3D_PRESETS', {}).get(mat_name, {})
        base_pwr = mat_preset.get("power", 70.0)
        base_freq = mat_preset.get("freq", 35.0)
        base_spd = mat_preset.get("mark_speed", 600.0)

        pwr = max(20.0, min(95.0, round(base_pwr * preset.get("power_scale", 1.0))))
        freq = max(20.0, min(80.0, round(base_freq * preset.get("freq_scale", 1.0))))
        spd = max(100.0, min(2000.0, round(base_spd * preset.get("speed_scale", 1.0))))

        if hasattr(self.ui, 'galvolaserpowerHorizontalSlider_2'):
            self.ui.galvolaserpowerHorizontalSlider_2.setValue(int(pwr))
        if hasattr(self.ui, 'galvolaserfreqHorizontalSlider'):
            self.ui.galvolaserfreqHorizontalSlider.setValue(int(freq))

        if hasattr(self.ui, 'pgmlaserpowerLineEdit'):
            self.ui.pgmlaserpowerLineEdit.setText(str(int(pwr)))
        if hasattr(self.ui, 'pgmlaserfreqLineEdit'):
            self.ui.pgmlaserfreqLineEdit.setText(str(int(freq)))
        if hasattr(self.ui, 'laserpowerLineEdit'):
            self.ui.laserpowerLineEdit.setText(str(int(pwr)))
        if hasattr(self.ui, 'laserfreqLineEdit'):
            self.ui.laserfreqLineEdit.setText(str(int(freq)))

        if hasattr(self.ui, 'pgmmarkspeedgalvoLineEdit'):
            self.ui.pgmmarkspeedgalvoLineEdit.setText(str(int(spd)))

        if hasattr(self, 'galvo_controller'):
            self.galvo_controller.live_power = pwr
            self.galvo_controller.live_freq = freq

        self.showAutoCloseMessage(
            "3D Resolution Applied",
            f"<b>{res_name}</b><br>"
            f"Total Slices: <b>{passes} Passes</b> | Pitch: <b>{pitch*1000:.0f} µm</b><br>"
            f"Laser Power: <b>{pwr:.0f}%</b> | Freq: <b>{freq:.0f} kHz</b> | Speed: <b>{spd:.0f} mm/s</b><br>"
            f"<i>{preset['desc']}</i>",
            timeout_ms=3500
        )

        # Sync preview page dropdown if present
        if hasattr(self, 'combo_preview_3d_resolution'):
            self.combo_preview_3d_resolution.blockSignals(True)
            self.combo_preview_3d_resolution.setCurrentText(res_name)
            self.combo_preview_3d_resolution.blockSignals(False)

        self._cached_3d_key = None
        self._cached_3d_queue = None
        self._cached_3d_layers = None

        if hasattr(self, 'slider_3d_layer'):
            self.slider_3d_layer.blockSignals(True)
            self.slider_3d_layer.setMaximum(passes)
            self.slider_3d_layer.setValue(1)
            self.slider_3d_layer.blockSignals(False)

        if getattr(self, 'pgm_file', None) and hasattr(self, 'cb_enable_3d_engraving') and self.cb_enable_3d_engraving.isChecked():
            try:
                self.process_galvo_file()
            except Exception as e:
                print(f"[3D Resolution Change] Preview refresh: {e}")

    def on_preview_3d_resolution_changed(self, idx):
        if hasattr(self, 'combo_preview_3d_resolution') and hasattr(self, 'combo_3d_resolution'):
            text = self.combo_preview_3d_resolution.currentText()
            if self.combo_3d_resolution.currentText() != text:
                self.combo_3d_resolution.blockSignals(True)
                self.combo_3d_resolution.setCurrentText(text)
                self.combo_3d_resolution.blockSignals(False)
            self.on_3d_resolution_changed(self.combo_3d_resolution.currentIndex())

    def on_3d_passes_manually_edited(self):
        if hasattr(self, 'combo_3d_resolution') and hasattr(self, 'input_3d_passes'):
            txt = self.input_3d_passes.text().strip()
            curr_tier = self.combo_3d_resolution.currentText()
            preset = getattr(self, 'RESOLUTION_3D_TIERS', {}).get(curr_tier)
            if preset and str(preset.get("passes")) != txt:
                custom_idx = self.combo_3d_resolution.findText("Custom (Manual Passes)")
                if custom_idx >= 0 and self.combo_3d_resolution.currentIndex() != custom_idx:
                    self.combo_3d_resolution.blockSignals(True)
                    self.combo_3d_resolution.setCurrentIndex(custom_idx)
                    self.combo_3d_resolution.blockSignals(False)
                if hasattr(self, 'combo_preview_3d_resolution'):
                    self.combo_preview_3d_resolution.blockSignals(True)
                    self.combo_preview_3d_resolution.setCurrentIndex(custom_idx)
                    self.combo_preview_3d_resolution.blockSignals(False)
            try:
                p_val = int(txt)
                if p_val > 0 and hasattr(self, 'slider_3d_layer'):
                    self.slider_3d_layer.blockSignals(True)
                    self.slider_3d_layer.setMaximum(p_val)
                    self.slider_3d_layer.blockSignals(False)
            except ValueError:
                pass
        self.on_3d_param_custom_changed()

    def on_3d_param_custom_changed(self):
        self._cached_3d_key = None
        self._cached_3d_queue = None
        self._cached_3d_layers = None

    def on_3d_mode_changed(self, idx):
        self._cached_3d_key = None
        mode = self.combo_3d_mode.currentText() if hasattr(self, 'combo_3d_mode') else ""
        if "Imported Sliced G-Code" in mode:
            if not (getattr(self, 'pgm_file', None) and self.pgm_file.lower().endswith(('.gcode', '.nc', '.tap', '.gco'))):
                self.showAutoCloseMessage(
                    "G-Code File Needed",
                    "Click 'Browse G-Code / 3D File' or 'SELECT' to choose your .gcode file.",
                    timeout_ms=3000
                )

    def get_3d_relief_parameters(self):
        """
        Unified parameter extractor and validator for all 3D relief slicing modes.
        Synchronizes material presets, laser power, frequency, speeds, offsets, dimensions,
        and advanced toolpath settings across all 3D components.
        """
        filepath = getattr(self, 'pgm_file', None)
        if not filepath or not os.path.exists(filepath):
            deep_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "DeepEngrave")
            filepath = os.path.join(deep_dir, "rupee_10_coin_27mm_relief_16bit.png")

        field_sz = float(self.galvo_config.field_size if self.galvo_config else 100.0)

        # Depth
        try:
            depth = float(self.input_3d_max_depth.text().strip() or 0.75)
        except Exception:
            depth = 0.75

        # Passes
        try:
            passes = int(self.input_3d_passes.text().strip() or 50)
        except Exception:
            passes = 50

        # Pitch
        try:
            pitch = float(self.input_3d_pitch.text().strip() or 0.025)
        except Exception:
            pitch = 0.025

        # Target Size (Diameter or Width/Span in mm)
        try:
            target_size = float(self.input_3d_size.text().strip() or 27.0)
        except Exception:
            target_size = 27.0

        mode = self.combo_3d_mode.currentText() if hasattr(self, 'combo_3d_mode') else "3D Coin Relief (Continuous 50-Pass Slicing, 27mm)"
        clean_int = 6 if hasattr(self, 'cb_3d_clean') and self.cb_3d_clean.isChecked() else 0
        bidirectional = self.cb_3d_bidirectional.isChecked() if hasattr(self, 'cb_3d_bidirectional') else True
        contour = self.cb_3d_contour.isChecked() if hasattr(self, 'cb_3d_contour') else True
        invert = self.cb_3d_invert.isChecked() if hasattr(self, 'cb_3d_invert') else False

        # Start position offsets
        start_x, start_y = 0.0, 0.0
        try:
            if hasattr(self, 'programgalvo_widgets'):
                sx = self.wh.invokeMethod(self.programgalvo_widgets.pgmstartposx, "get")
                if sx and str(sx).strip():
                    start_x = float(str(sx).strip())
                sy = self.wh.invokeMethod(self.programgalvo_widgets.pgmstartposy, "get")
                if sy and str(sy).strip():
                    start_y = float(str(sy).strip())
        except Exception:
            pass

        # Mark & Jump Speeds
        raw_jump = 2000.0
        raw_mark = 800.0
        try:
            if hasattr(self, 'programgalvo_widgets'):
                raw_jump = float(self.wh.invokeMethod(self.programgalvo_widgets.pgmjumpspeed, "get") or 2000.0)
                raw_mark = float(self.wh.invokeMethod(self.programgalvo_widgets.pgmmarkspeedgalvo, "get") or 800.0)
        except Exception:
            pass
        if raw_jump > 50000 or raw_jump <= 0: raw_jump = 2000.0
        if raw_mark > 50000 or raw_mark <= 0: raw_mark = 800.0

        # Laser Power & Frequency
        pwr = 70.0
        freq = 35.0
        try:
            if hasattr(self.ui, 'pgmlaserpowerLineEdit') and self.ui.pgmlaserpowerLineEdit.text().strip():
                pwr = float(self.ui.pgmlaserpowerLineEdit.text().strip())
            elif hasattr(self, 'galvo_controller') and getattr(self.galvo_controller, 'live_power', None) is not None:
                pwr = float(self.galvo_controller.live_power)
            elif hasattr(self.ui, 'laserpowerLineEdit') and self.ui.laserpowerLineEdit.text().strip():
                pwr = float(self.ui.laserpowerLineEdit.text().strip())
        except Exception:
            pass

        try:
            if hasattr(self.ui, 'pgmlaserfreqLineEdit') and self.ui.pgmlaserfreqLineEdit.text().strip():
                freq = float(self.ui.pgmlaserfreqLineEdit.text().strip())
            elif hasattr(self, 'galvo_controller') and getattr(self.galvo_controller, 'live_freq', None) is not None:
                freq = float(self.galvo_controller.live_freq)
            elif hasattr(self.ui, 'laserfreqLineEdit') and self.ui.laserfreqLineEdit.text().strip():
                freq = float(self.ui.laserfreqLineEdit.text().strip())
        except Exception:
            pass

        # Boundary mode
        if "Coin" in mode:
            boundary_mode = 'circle'
        elif "Vector" in mode:
            boundary_mode = 'auto'
        else:
            boundary_mode = 'auto'

        cache_key = (
            filepath,
            round(depth, 3),
            passes,
            round(pitch, 4),
            round(target_size, 3),
            mode,
            clean_int,
            bidirectional,
            contour,
            invert,
            round(start_x, 2),
            round(start_y, 2),
            round(pwr, 1),
            round(freq, 1),
            round(raw_mark, 1),
            round(raw_jump, 1)
        )

        return {
            'filepath': filepath,
            'field_sz': field_sz,
            'depth': depth,
            'passes': passes,
            'pitch': pitch,
            'target_size': target_size,
            'mode': mode,
            'clean_int': clean_int,
            'bidirectional': bidirectional,
            'contour': contour,
            'invert': invert,
            'start_x': start_x,
            'start_y': start_y,
            'raw_mark': raw_mark,
            'raw_jump': raw_jump,
            'laser_power': pwr,
            'laser_freq': freq,
            'boundary_mode': boundary_mode,
            'cache_key': cache_key
        }

    def start_background_3d_slicing(self):
        """
        Called upon clicking 'Save' on the Galvo Program page or when 3D params change.
        Initiates asynchronous slicing in the background without freezing the GUI.
        """
        params = self.get_3d_relief_parameters()
        cache_key = params['cache_key']

        # If already cached with identical settings, use cache immediately
        if hasattr(self, '_cached_3d_key') and self._cached_3d_key == cache_key and hasattr(self, '_cached_3d_queue') and self._cached_3d_queue:
            print("[3D Relief] Using pre-cached toolpaths.")
            self._on_3d_slicing_finished(True, self._cached_3d_queue, self._cached_3d_layers, "", cache_key)
            return

        # Disable the print run button while slicing
        if hasattr(self, 'printgalvo_widgets') and hasattr(self.printgalvo_widgets, 'printrungalvo'):
            self.wh.invokeMethod(self.printgalvo_widgets.printrungalvo, "disable")

        fname = os.path.basename(params['filepath'])
        if hasattr(self.ui, 'progressLabel_2'):
            self.ui.progressLabel_2.setText(f"⚙️ Slicing 3D Toolpaths in Background ({fname})...")

        # Stop existing slicing thread if active
        if hasattr(self, 'slicing_3d_thread') and self.slicing_3d_thread and self.slicing_3d_thread.isRunning():
            self.slicing_3d_thread.terminate()
            self.slicing_3d_thread.wait()

        from galvo_threads import Slicing3DThread
        self.slicing_3d_thread = Slicing3DThread(
            filepath=params['filepath'],
            field_sz=params['field_sz'],
            depth=params['depth'],
            passes=params['passes'],
            pitch=params['pitch'],
            mode=params['mode'],
            clean_int=params['clean_int'],
            target_size_mm=params['target_size'],
            laser_power=params['laser_power'],
            laser_freq=params['laser_freq'],
            mark_speed_mms=params['raw_mark'],
            jump_speed_mms=params['raw_jump'],
            offset_x_mm=params['start_x'],
            offset_y_mm=params['start_y'],
            boundary_mode=params['boundary_mode'],
            bidirectional=params['bidirectional'],
            enable_contour=params['contour'],
            invert_relief=params['invert'],
            cache_key=cache_key
        )
        self.slicing_3d_thread.finished_signal.connect(self._on_3d_slicing_finished)
        self.slicing_3d_thread.start()
        print(f"[3D Relief] Background slicing started for '{fname}' ({params['target_size']}mm, {params['passes']} passes)...")

    def _on_3d_slicing_finished(self, success, queue, layers, error_msg, cache_key):
        if not success:
            print(f"[3D Relief] Slicing error: {error_msg}")
            if hasattr(self.ui, 'progressLabel_2'):
                self.ui.progressLabel_2.setText("❌ 3D Slicing Error")
            self.showAutoCloseMessage("Slicing Error", f"Failed to slice 3D model: {error_msg}")
            return

        self._cached_3d_queue = queue
        self._cached_3d_layers = layers
        self._cached_3d_key = cache_key

        self.planner.clear()
        self.planner.send_queue = list(queue)
        self.planner.preview_queue = [cmd for cmd in queue if cmd.get('type') in ('jump', 'mark')]

        tot = len(layers)
        if hasattr(self, 'slider_3d_layer'):
            self.slider_3d_layer.blockSignals(True)
            self.slider_3d_layer.setMaximum(tot)
            self.slider_3d_layer.setValue(1)
            self.slider_3d_layer.blockSignals(False)

        if hasattr(self, 'layer_slider_frame'):
            self.layer_slider_frame.setVisible(True)

        self.render_3d_preview_layer(1)
        self.update_galvo_preview_bounds()

        # Re-enable the print button now that toolpaths are ready
        if hasattr(self, 'printgalvo_widgets') and hasattr(self.printgalvo_widgets, 'printrungalvo'):
            self.wh.invokeMethod(self.printgalvo_widgets.printrungalvo, "enable")

        if hasattr(self.ui, 'progressLabel_2'):
            self.ui.progressLabel_2.setText(f"✅ 3D Slicing Complete: {tot} Layers Ready")

        self.showAutoCloseMessage(
            "3D Relief Ready",
            f"Background slicing complete: <b>{tot} layers</b> prepared for laser engraving.",
            timeout_ms=3000
        )

    def warmup_3d_relief_queue(self):
        self.start_background_3d_slicing()

    def on_3d_frame_clicked(self):
        """
        Non-blocking Red Light framing toggle for 3D reliefs.
        Traces circular or rectangular bounds matching the actual 3D relief footprint.
        """
        if not hasattr(self, 'galvo_controller') or not self.galvo_controller:
            return

        # If framing thread is currently active, stop it
        if hasattr(self, 'galvo_3d_preview_thread') and self.galvo_3d_preview_thread and getattr(self.galvo_3d_preview_thread, 'running', False):
            self.galvo_3d_preview_thread.running = False
            self.galvo_3d_preview_thread.wait()
            self.galvo_3d_preview_thread = None
            if self.galvo_controller.connection:
                if hasattr(self.galvo_controller.connection, 'reddot_off'):
                    self.galvo_controller.connection.reddot_off()
                if hasattr(self.galvo_controller.connection, 'laser_off'):
                    self.galvo_controller.connection.laser_off()
            if hasattr(self, 'btn_3d_frame'):
                self.btn_3d_frame.setText("🔴 3D Red Light Framing")
                self.btn_3d_frame.setStyleSheet(
                    "QPushButton { background-color: #d32f2f; color: white; border-radius: 8px; padding: 7px 16px; font-weight: bold; font-size: 12pt; } "
                    "QPushButton:hover { background-color: #b71c1c; }"
                )
            self.showAutoCloseMessage("Framing", "Red light framing stopped.", timeout_ms=1500)
            return

        if not self.galvo_controller.is_connected:
            self.galvo_controller.connect()
            if not self.galvo_controller.is_connected:
                self.showAutoCloseMessage("Hardware Error", "Galvo controller is not connected.")
                return

        params = self.get_3d_relief_parameters()
        field_sz = params['field_sz']
        scale = 65535.0 / field_sz
        target_sz = params['target_size']
        cx = 32767 + int(params['start_x'] * scale)
        cy = 32767 + int(params['start_y'] * scale)
        hw = int((target_sz / 2.0) * scale)

        min_x = max(0, cx - hw)
        max_x = min(65535, cx + hw)
        min_y = max(0, cy - hw)
        max_y = min(65535, cy + hw)

        shape = 'circle' if 'Coin' in params['mode'] else 'rect'

        from galvo_threads import PreviewThread
        self.galvo_3d_preview_thread = PreviewThread(self.galvo_controller, min_x, max_x, min_y, max_y, shape=shape)
        self.galvo_3d_preview_thread.finished_signal.connect(self._on_3d_frame_finished)
        self.galvo_3d_preview_thread.start()

        if hasattr(self, 'btn_3d_frame'):
            self.btn_3d_frame.setText("⏹️ Stop Red Light Framing")
            self.btn_3d_frame.setStyleSheet(
                "QPushButton { background-color: #b71c1c; color: white; border-radius: 8px; padding: 7px 16px; font-weight: bold; font-size: 12pt; } "
                "QPushButton:hover { background-color: #7f0000; }"
            )

        shape_str = "Circular" if shape == 'circle' else "Rectangular"
        self.showAutoCloseMessage(
            "3D Framing Active",
            f"Projecting <b>{shape_str}</b> red pointer framing (Size: {target_sz:.1f} mm, Center: {params['start_x']:.1f}, {params['start_y']:.1f}).<br>Click button again to stop.",
            timeout_ms=3000
        )

    def _on_3d_frame_finished(self, success):
        if hasattr(self, 'btn_3d_frame'):
            self.btn_3d_frame.setText("🔴 3D Red Light Framing")
            self.btn_3d_frame.setStyleSheet(
                "QPushButton { background-color: #d32f2f; color: white; border-radius: 8px; padding: 7px 16px; font-weight: bold; font-size: 12pt; } "
                "QPushButton:hover { background-color: #b71c1c; }"
            )
        self.galvo_3d_preview_thread = None

    def on_3d_preview_clicked(self):
        """
        Interactive 3D preview window with real-time layer-scrubbing.
        Automatically exports or reuses true 3D G-code with Z-depth coordinates.
        """
        params = self.get_3d_relief_parameters()
        filepath = params['filepath']
        target_sz = params['target_size']
        depth = params['depth']
        passes = params['passes']
        pitch = params['pitch']

        custom_gcode = os.path.splitext(filepath)[0] + "_sliced.gcode"
        gcode_path = custom_gcode

        # If G-code already loaded directly:
        if filepath.lower().endswith(('.gcode', '.nc', '.tap', '.gco')):
            gcode_path = filepath
        else:
            # Check if we have cached layers from background slicing
            need_export = True
            if hasattr(self, '_cached_3d_layers') and self._cached_3d_layers:
                # Write cached layers directly to G-code
                try:
                    with open(gcode_path, "w", encoding="utf-8") as f:
                        f.write(f"; Galvo Studio 3D Relief Toolpaths\n")
                        f.write(f"; Source: {os.path.basename(filepath)}\n")
                        f.write(f"; Target Size: {target_sz:.2f}mm | Passes: {len(self._cached_3d_layers)} | Pitch: {pitch:.4f}mm\n")
                        f.write(f"G21\nG90\n\n")
                        for layer in self._cached_3d_layers:
                            z_val = layer.get('z_depth_mm', 0.0)
                            f.write(f"\n; --- Layer {layer.get('layer_index', 1)} | Z -{z_val:.3f} mm ---\n")
                            f.write(f"G0 Z-{z_val:.3f}\n")
                            for cmd in layer.get('commands', []):
                                ctype = cmd.get('type')
                                x, y = cmd.get('x_mm', 0.0), cmd.get('y_mm', 0.0)
                                if ctype == 'jump':
                                    f.write(f"G0 X{x:.3f} Y{y:.3f}\n")
                                elif ctype == 'mark':
                                    f.write(f"G1 X{x:.3f} Y{y:.3f}\n")
                        f.write("\nM30\n")
                    need_export = False
                except Exception as ex:
                    print(f"[3D Preview] Error writing cached G-code: {ex}")
                    need_export = True

            if need_export:
                self.showAutoCloseMessage("Compiling 3D Preview", "Generating true 3D toolpaths for interactive preview...", timeout_ms=2500)
                if filepath.lower().endswith(('.stl', '.obj')) or "3D Mesh / STL" in params['mode']:
                    from core.stl_3d_engraver import STL3DEngraver
                    engraver = STL3DEngraver(
                        stl_path=filepath,
                        target_size_mm=target_sz,
                        max_depth_mm=depth,
                        num_layers=passes,
                        offset_x_mm=params['start_x'],
                        offset_y_mm=params['start_y'],
                        invert_relief=params['invert']
                    )
                    engraver.export_gcode(
                        gcode_path,
                        hatch_pitch_mm=pitch,
                        clean_interval=params['clean_int'],
                        bidirectional=params['bidirectional'],
                        enable_contour=params['contour']
                    )
                elif "Multi-Layer Vector" in params['mode'] or filepath.lower().endswith(('.dxf', '.svg')):
                    from core.coin_3d_engraver import Coin3DReliefEngraver
                    engraver = Coin3DReliefEngraver(
                        dxf_path=filepath,
                        field_size=params['field_sz'],
                        offset_x_mm=params['start_x'],
                        offset_y_mm=params['start_y'],
                        bidirectional=params['bidirectional']
                    )
                    engraver.export_gcode(gcode_path, clean_interval=params['clean_int'])
                else:
                    from core.heightmap_slicer import Heightmap3DSlicer
                    slicer = Heightmap3DSlicer(
                        heightmap_path=filepath,
                        target_size_mm=target_sz,
                        max_depth_mm=depth,
                        num_layers=passes,
                        field_size=params['field_sz'],
                        offset_x_mm=params['start_x'],
                        offset_y_mm=params['start_y'],
                        boundary_mode=params['boundary_mode'],
                        invert_relief=params['invert']
                    )
                    slicer.export_sliced_gcode(
                        gcode_path,
                        hatch_pitch_mm=pitch,
                        clean_interval=params['clean_int'],
                        bidirectional=params['bidirectional'],
                        enable_contour=params['contour']
                    )

        if not os.path.exists(gcode_path):
            deep_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "DeepEngrave")
            gcode_path = os.path.join(deep_dir, "rupee_10_coin_27mm_sliced.gcode")

        from preview3d import GCode3DPreview
        self.preview_3d_win = QMainWindow(self)
        self.preview_3d_win.setWindowTitle(f"3D Bas-Relief Preview - {os.path.basename(filepath)} ({target_sz}mm, {passes} Layers)")
        self.preview_3d_win.resize(1100, 850)
        p_widget = GCode3DPreview(self.preview_3d_win)
        self.preview_3d_win.setCentralWidget(p_widget)
        self.preview_3d_win.show()

        if os.path.exists(gcode_path):
            with open(gcode_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
            p_widget.sigLoadGcode.emit(lines)

    # --- 3D Layer Preview Slider Handlers ---
    def on_preview_layer_slider_changed(self, layer_val):
        self.render_3d_preview_layer(layer_val)

    def on_prev_3d_layer(self):
        if hasattr(self, 'slider_3d_layer'):
            val = max(1, self.slider_3d_layer.value() - 1)
            self.slider_3d_layer.setValue(val)

    def on_next_3d_layer(self):
        if hasattr(self, 'slider_3d_layer'):
            val = min(self.slider_3d_layer.maximum(), self.slider_3d_layer.value() + 1)
            self.slider_3d_layer.setValue(val)

    def toggle_layer_display_mode(self):
        self._layer_mode_cumulative = not getattr(self, '_layer_mode_cumulative', False)
        if hasattr(self, 'btn_layer_mode'):
            if self._layer_mode_cumulative:
                self.btn_layer_mode.setText("Mode: Cumulative (1..N)")
            else:
                self.btn_layer_mode.setText("Mode: Single Layer")
        if hasattr(self, 'slider_3d_layer'):
            self.render_3d_preview_layer(self.slider_3d_layer.value())

    def render_3d_preview_layer(self, layer_num):
        layers = getattr(self, '_cached_3d_layers', None)
        if not layers:
            self.get_3d_engraving_queue()
            layers = getattr(self, '_cached_3d_layers', None)

        if not layers or layer_num < 1 or layer_num > len(layers):
            return

        target_layer = layers[layer_num - 1]
        depth_val = target_layer.get('depth_mm', 0.0)
        ang_val = target_layer.get('angle_deg', 0.0)
        tot = len(layers)

        if hasattr(self, 'label_3d_layer_status'):
            self.label_3d_layer_status.setText(
                f"Layer: {layer_num} / {tot} | Depth: -{depth_val:.3f} mm | Angle: {ang_val:.1f}°"
            )

        if getattr(self, '_layer_mode_cumulative', False):
            combined_cmds = []
            for i in range(layer_num):
                combined_cmds.extend(layers[i].get('commands', []))
            if hasattr(self, 'galvo_preview'):
                self.galvo_preview.draw_queue(combined_cmds)
        else:
            cmds = target_layer.get('commands', [])
            if hasattr(self, 'galvo_preview'):
                self.galvo_preview.draw_queue(cmds)

    def update_3d_layer_printing_ui(self, layer_num, total_layers, depth_val, ang_val):
        """Called in real time during laser execution as each 3D relief layer is printed."""
        if hasattr(self, 'slider_3d_layer'):
            self.slider_3d_layer.blockSignals(True)
            self.slider_3d_layer.setMaximum(total_layers)
            self.slider_3d_layer.setValue(layer_num)
            self.slider_3d_layer.blockSignals(False)

        if hasattr(self, 'label_3d_layer_status'):
            self.label_3d_layer_status.setText(
                f"🔴 PRINTING LAYER: {layer_num} / {total_layers} | Depth: -{depth_val:.3f} mm | Angle: {ang_val:.1f}°"
            )

        # Update preview canvas to show active layer
        layers = getattr(self, '_cached_3d_layers', None)
        if layers and layer_num <= len(layers) and hasattr(self, 'galvo_preview'):
            if getattr(self, '_layer_mode_cumulative', False):
                combined_cmds = []
                for i in range(layer_num):
                    combined_cmds.extend(layers[i].get('commands', []))
                self.galvo_preview.draw_queue(combined_cmds)
            else:
                cmds = layers[layer_num - 1].get('commands', [])
                self.galvo_preview.draw_queue(cmds)

        pct = int((layer_num / max(1, total_layers)) * 100)
        if hasattr(self.ui, 'printgalvoProgressBar'):
            self.ui.printgalvoProgressBar.setValue(pct)

        if hasattr(self.ui, 'progressLabel_2'):
            self.ui.progressLabel_2.setText(f"3D Relief Pass {layer_num}/{total_layers} (-{depth_val:.2f}mm) | {pct}%")

        from PySide6.QtWidgets import QApplication
        QApplication.instance().processEvents()

    def get_3d_engraving_queue(self):
        """
        Compiles or retrieves pre-cached hardware command queue for 3D relief engraving.
        Applies power, frequency, speeds, serpentine hatching, contour cleanup, and coordinate offsets.
        """
        params = self.get_3d_relief_parameters()
        cache_key = params['cache_key']

        # Check pre-compiled cache for instantaneous print start
        if hasattr(self, '_cached_3d_key') and self._cached_3d_key == cache_key and hasattr(self, '_cached_3d_queue') and self._cached_3d_queue:
            print("[3D Relief] Instant start using pre-cached toolpaths.")
            return self._cached_3d_queue

        filepath = params['filepath']
        field_sz = params['field_sz']
        depth = params['depth']
        passes = params['passes']
        pitch = params['pitch']
        target_sz = params['target_size']
        mode = params['mode']
        clean_int = params['clean_int']
        raw_mark = params['raw_mark']
        raw_jump = params['raw_jump']
        pwr = params['laser_power']
        freq = params['laser_freq']
        start_x = params['start_x']
        start_y = params['start_y']
        bidirectional = params['bidirectional']
        contour = params['contour']
        invert = params['invert']
        boundary_mode = params['boundary_mode']

        if filepath.lower().endswith(('.gcode', '.nc', '.tap', '.gco')) or "G-Code" in mode:
            from core.gcode_3d_adapter import GCode3DAdapter
            target_dia = target_sz if ("Coin" in mode and not filepath.lower().endswith(('.gcode', '.nc', '.tap', '.gco'))) else None
            adapter = GCode3DAdapter(
                gcode_path=filepath,
                field_size=field_sz,
                target_diameter_mm=target_dia,
                mark_speed_mms=raw_mark,
                jump_speed_mms=raw_jump,
                laser_power=pwr,
                laser_freq=freq,
                target_passes=passes,
                offset_x_mm=start_x,
                offset_y_mm=start_y
            )
            q = adapter.compile_job_queue(mark_speed_mms=raw_mark, jump_speed_mms=raw_jump, clean_interval=clean_int, target_passes=passes)
            self._cached_3d_layers = getattr(adapter, 'layers', [])
        elif filepath.lower().endswith(('.stl', '.obj')) or "3D Mesh / STL" in mode:
            from core.stl_3d_engraver import STL3DEngraver
            engraver = STL3DEngraver(
                stl_path=filepath,
                target_size_mm=target_sz,
                max_depth_mm=depth,
                num_layers=passes,
                field_size=field_sz,
                laser_power=pwr,
                laser_freq=freq,
                mark_speed_mms=raw_mark,
                jump_speed_mms=raw_jump,
                offset_x_mm=start_x,
                offset_y_mm=start_y,
                bidirectional=bidirectional,
                enable_contour=contour,
                invert_relief=invert
            )
            q = engraver.compile_job_queue(hatch_pitch_mm=pitch, clean_interval=clean_int)
            self._cached_3d_layers = getattr(engraver, 'layers', [])
        elif "Multi-Layer Vector" in mode or filepath.lower().endswith(('.dxf', '.svg')):
            from core.coin_3d_engraver import Coin3DReliefEngraver
            engraver = Coin3DReliefEngraver(
                dxf_path=filepath,
                field_size=field_sz,
                offset_x_mm=start_x,
                offset_y_mm=start_y,
                bidirectional=bidirectional
            )
            q = engraver.compile_job_queue(clean_interval=clean_int)
            self._cached_3d_layers = getattr(engraver, 'layers', [])
        else:
            from core.heightmap_slicer import Heightmap3DSlicer
            slicer = Heightmap3DSlicer(
                heightmap_path=filepath,
                target_size_mm=target_sz,
                max_depth_mm=depth,
                num_layers=passes,
                field_size=field_sz,
                laser_power=pwr,
                laser_freq=freq,
                mark_speed_mms=raw_mark,
                jump_speed_mms=raw_jump,
                offset_x_mm=start_x,
                offset_y_mm=start_y,
                boundary_mode=boundary_mode,
                bidirectional=bidirectional,
                enable_contour=contour,
                invert_relief=invert
            )
            q = slicer.compile_sliced_3d_queue(hatch_pitch_mm=pitch, clean_interval=clean_int)
            self._cached_3d_layers = getattr(slicer, 'layers', [])

        self._cached_3d_queue = q
        self._cached_3d_key = cache_key

        if hasattr(self, 'slider_3d_layer'):
            tot_l = len(self._cached_3d_layers) if hasattr(self, '_cached_3d_layers') and self._cached_3d_layers else passes
            self.slider_3d_layer.setMaximum(tot_l)

        return q
    
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

            # --- 3D Relief Layer Control Bar on Preview Page ---
            self.layer_slider_frame = QFrame()
            self.layer_slider_frame.setStyleSheet(
                "QFrame {"
                " background: #f1f8e9;"
                " border: 2px solid #0b6623;"
                " border-radius: 8px;"
                " padding: 4px 8px;"
                "}"
            )
            self.layer_slider_frame.setVisible(True)
            layer_layout = QHBoxLayout(self.layer_slider_frame)
            layer_layout.setContentsMargins(6, 4, 6, 4)
            layer_layout.setSpacing(8)

            lbl_preview_res = QLabel("Resolution:")
            lbl_preview_res.setStyleSheet("color: #0b6623; font-weight: bold; font-size: 11pt;")
            layer_layout.addWidget(lbl_preview_res)

            self.combo_preview_3d_resolution = QComboBox()
            self.combo_preview_3d_resolution.setStyleSheet(
                "QComboBox {"
                " border: 1.5px solid #0b6623;"
                " border-radius: 5px;"
                " padding: 3px 6px;"
                " color: #0b6623;"
                " font-weight: bold;"
                " font-size: 10pt;"
                " background-color: #ffffff;"
                " min-width: 175px;"
                "}"
                "QComboBox QAbstractItemView {"
                " color: #0b6623;"
                " background-color: #ffffff;"
                " selection-background-color: #c8e6c9;"
                " selection-color: #0b6623;"
                " font-size: 10pt;"
                "}"
            )
            self.combo_preview_3d_resolution.addItems(list(self.RESOLUTION_3D_TIERS.keys()))
            def_idx = self.combo_preview_3d_resolution.findText("Medium Detail (~250 Passes - Balanced)")
            if def_idx >= 0:
                self.combo_preview_3d_resolution.setCurrentIndex(def_idx)
            self.combo_preview_3d_resolution.currentIndexChanged.connect(self.on_preview_3d_resolution_changed)
            layer_layout.addWidget(self.combo_preview_3d_resolution)

            layer_layout.addSpacing(10)

            lbl_layer_title = QLabel("3D Layer:")
            lbl_layer_title.setStyleSheet("color: #0b6623; font-weight: bold; font-size: 11pt;")
            layer_layout.addWidget(lbl_layer_title)

            self.btn_layer_prev = QPushButton("◀")
            self.btn_layer_prev.setFixedWidth(28)
            self.btn_layer_prev.setStyleSheet("QPushButton { background: #0b6623; color: white; font-weight: bold; border-radius: 4px; padding: 3px; } QPushButton:hover { background: #084d1a; }")
            self.btn_layer_prev.clicked.connect(self.on_prev_3d_layer)
            layer_layout.addWidget(self.btn_layer_prev)

            self.slider_3d_layer = QSlider(Qt.Horizontal)
            self.slider_3d_layer.setRange(1, 250)
            self.slider_3d_layer.setValue(1)
            self.slider_3d_layer.setStyleSheet(
                "QSlider::groove:horizontal { height: 8px; background: #c8e6c9; border-radius: 4px; }"
                "QSlider::sub-page:horizontal { background: #0b6623; border-radius: 4px; }"
                "QSlider::handle:horizontal { background: #2e7d32; border: 2px solid white; width: 20px; margin-top: -6px; margin-bottom: -6px; border-radius: 10px; }"
                "QSlider::handle:horizontal:hover { background: #1b5e20; }"
            )
            self.slider_3d_layer.valueChanged.connect(self.on_preview_layer_slider_changed)
            layer_layout.addWidget(self.slider_3d_layer, stretch=1)

            self.btn_layer_next = QPushButton("▶")
            self.btn_layer_next.setFixedWidth(28)
            self.btn_layer_next.setStyleSheet("QPushButton { background: #0b6623; color: white; font-weight: bold; border-radius: 4px; padding: 3px; } QPushButton:hover { background: #084d1a; }")
            self.btn_layer_next.clicked.connect(self.on_next_3d_layer)
            layer_layout.addWidget(self.btn_layer_next)

            self.btn_layer_mode = QPushButton("Mode: Single Layer")
            self.btn_layer_mode.setStyleSheet("QPushButton { background: #e8f5e9; color: #0b6623; font-weight: bold; border: 1px solid #0b6623; border-radius: 5px; padding: 3px 8px; font-size: 10pt; } QPushButton:hover { background: #c8e6c9; }")
            self.btn_layer_mode.clicked.connect(self.toggle_layer_display_mode)
            layer_layout.addWidget(self.btn_layer_mode)

            self.label_3d_layer_status = QLabel("Layer: 1 / 250 | Depth: -0.003 mm | Angle: 0.0°")
            self.label_3d_layer_status.setStyleSheet("color: #0b6623; font-weight: bold; font-size: 10pt; padding: 2px 4px;")
            layer_layout.addWidget(self.label_3d_layer_status)

            galvo_plot_layout.addWidget(self.layer_slider_frame)
        
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
            if self.center_menu_btn is not None:
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

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls() or event.mimeData().hasText():
            event.acceptProposedAction()
        else:
            super().dragEnterEvent(event)

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                fpath = url.toLocalFile()
                if os.path.isfile(fpath):
                    self.load_design_file(fpath)
                    event.acceptProposedAction()
                    return
        elif event.mimeData().hasText():
            txt = event.mimeData().text().strip().strip('"\';\r\n ')
            if os.path.isfile(txt):
                self.load_design_file(txt)
                event.acceptProposedAction()
                return
        super().dropEvent(event)

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
#                 self.wh.invokeMethod(self.left_menu_widgets.laser, "hide")
#                 self.wh.invokeMethod(self.left_menu_widgets.laserconfgalvo, "hide")
                self.wh.invokeMethod(self.center_menu_widgets.settings, "hide")
                if hasattr(self.ui, 'testpatterngalvoFrame'):
                    self.wh.invokeMethod(self.ui.testpatterngalvoFrame, "hide")
            
            elif user == "Supervisor" and password == "452301":
                self.logger.info("Profile : Supervisor")
                self.wh.invokeMethod(self.left_menu_widgets.terminal, "show")
#                 self.wh.invokeMethod(self.left_menu_widgets.laser, "hide" if str(self.galvo_mode).upper() == "ON" else "show")
#                 self.wh.invokeMethod(self.left_menu_widgets.laserconfgalvo, "show" if str(self.galvo_mode).upper() == "ON" else "hide")
                self.wh.invokeMethod(self.center_menu_widgets.settings, "show")
                if hasattr(self.ui, 'testpatterngalvoFrame'):
                    self.wh.invokeMethod(self.ui.testpatterngalvoFrame, "show")

                QTimer.singleShot(600000, self.resetProfile)
            
            elif user == "Technician" and password == "543210":
                self.logger.info("Profile : Technician")
                self.wh.invokeMethod(self.left_menu_widgets.terminal, "hide") # Hide for technician too? User said "only show in supervisor mode"
#                 self.wh.invokeMethod(self.left_menu_widgets.laser, "hide" if str(self.galvo_mode).upper() == "ON" else "show")
#                 self.wh.invokeMethod(self.left_menu_widgets.laserconfgalvo, "show" if str(self.galvo_mode).upper() == "ON" else "hide")
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
            raw_jump = float(self.wh.invokeMethod(self.programgalvo_widgets.pgmjumpspeed, "get") or 2000)
            raw_mark = float(self.wh.invokeMethod(self.programgalvo_widgets.pgmmarkspeedgalvo, "get") or 1000)
        except:
            raw_jump = 2000.0
            raw_mark = 1000.0
            
        import math
        
        size_mm = min(100.0, self.galvo_config.field_size if self.galvo_config else 100.0)
        half_size = size_mm / 2.0
        
        # Calculate galvo_units_per_mm to convert mm/s to bits/sec (EZCAD style)
        galvo_units_per_mm = 65535.0 / (self.galvo_config.field_size if self.galvo_config else 100.0)
        jump_speed = int(raw_jump * galvo_units_per_mm)
        mark_speed = int(raw_mark * galvo_units_per_mm)

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

    def _apply_galvo_laser_settings(self):
        if not hasattr(self, 'galvo_controller') or not self.galvo_controller.is_connected:
            return
        if hasattr(self.galvo_controller, "connection") and hasattr(self.galvo_controller.connection, "set_analog_do_bit"):
            try:
                slider_percentage = float(self.ui.galvolaserpowerHorizontalSlider_2.value())
                freq_val = float(self.ui.galvolaserfreqHorizontalSlider.value())
                max_val = 100.0
                
                # Store live values for background thread injection
                self.galvo_controller.live_power = slider_percentage
                self.galvo_controller.live_freq = freq_val
                
                # Only write directly to hardware if NOT currently printing
                # If printing, the background thread (execute_queue) will pick up the live values
                is_printing = hasattr(self, 'galvo_exec_thread') and self.galvo_exec_thread and self.galvo_exec_thread.isRunning()
                if not is_printing:
                    # Invert the power signal in Python to compensate for the Blackpill's hardware mapping (0V = 100% power, 3.3V = 0% power)
                    if float(slider_percentage) <= 0:
                        if hasattr(self.galvo_controller.connection, 'laser_off'):
                            self.galvo_controller.connection.laser_off()
                        self.galvo_controller.connection.set_analog_do_bit(255.0, 0.0, 50.0, 2)
                    else:
                        mapped_power = (float(slider_percentage) / 100.0) * 255.0
                        self.galvo_controller.connection.set_analog_do_bit(255.0, mapped_power, 50.0, 2)
                    if hasattr(self.galvo_controller.connection, 'clamp_laser_freq'):
                        freq_val = self.galvo_controller.connection.clamp_laser_freq(freq_val)
                    
                    # Convert 20kHz - 80kHz to 10% - 90% Duty Cycle for the Blackpill
                    freq_duty_cycle = 10.0 + ((freq_val - 20.0) / (80.0 - 20.0)) * 80.0
                    freq_duty_cycle = max(10.0, min(90.0, freq_duty_cycle))
                    
                    self.galvo_controller.connection.set_analog_do_bit(100.0, freq_duty_cycle, 50.0, 0)
            except Exception as e:
                self.util.debugPrint(f"Error applying laser settings: {e}")

    def laserConfGalvoAction(self, widget, *args):
        action = self.wh.getRole(widget)
        self.util.debugPrint(f"laserConfGalvoAction : {action}")
        
        if action == "galvoobjheight":
            self.update_galvo_focus_calculations()
            
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
            self.update_galvo_focus_calculations()
            self.showAutoCloseMessage("Focus Set", f"Z Focus position saved at {focus_pos:.2f} mm.")
        elif action == "flasergalvoset":
            if not self.galvo_controller.is_connected:
                self.showAutoCloseMessage("Hardware Disconnected", "Ensure hardware is connected before operating laser.")
                return
                
            current_text = widget.text().upper()
            if current_text == "ON":
                try:
                    power = float(self.ui.galvolaserpowerHorizontalSlider_2.value())
                except:
                    power = 0.0
                    
                if power <= 0.0:
                    self.showAutoCloseMessage("Zero Power", "Cannot turn laser ON when power is set to 0%.")
                    return
                    
                print("UI COMMAND: Turning Laser ON (DO1 = HIGH)")
                self._apply_galvo_laser_settings()
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
            self._apply_galvo_laser_settings()
        elif action == "laserpower":
            try:
                val = int(self.ui.laserpowerLineEdit.text())
                val = max(0, min(100, val))
                self.ui.laserpowerLineEdit.setText(str(val))
                self.ui.galvolaserpowerHorizontalSlider_2.setValue(val)
                self._apply_galvo_laser_settings()
            except ValueError:
                pass
        elif action == "galvolaserfreq":
            val = self.ui.galvolaserfreqHorizontalSlider.value()
            self.ui.laserfreqLineEdit.setText(str(val))
            self._apply_galvo_laser_settings()
        elif action == "laserfreq":
            try:
                val = int(self.ui.laserfreqLineEdit.text())
                val = max(20, min(80, val))
                self.ui.laserfreqLineEdit.setText(str(val))
                self.ui.galvolaserfreqHorizontalSlider.setValue(val)
                self._apply_galvo_laser_settings()
            except ValueError:
                pass

    def _get_initial_file_dir(self):
        if getattr(self, 'pgm_file', None) and os.path.isfile(self.pgm_file):
            return os.path.dirname(self.pgm_file)
        base_dir = os.path.dirname(os.path.abspath(__file__))
        svg_dir = os.path.join(base_dir, "svg_files")
        if os.path.isdir(svg_dir):
            return svg_dir
        deep_dir = os.path.join(base_dir, "DeepEngrave")
        if os.path.isdir(deep_dir):
            return deep_dir
        return base_dir

    def browse_3d_model_file(self):
        initial_dir = self._get_initial_file_dir()
        filters = (
            "G-Code Files (*.gcode *.nc *.tap *.gco);;"
            "All Supported Files (*.gcode *.nc *.tap *.gco *.stl *.obj *.png *.bmp *.tiff *.svg *.dxf);;"
            "3D Mesh Files (*.stl *.obj);;"
            "All Files (*.*)"
        )
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Sliced G-Code or 3D Model",
            initial_dir,
            filters,
            "G-Code Files (*.gcode *.nc *.tap *.gco)"
        )
        if file_path:
            self.load_design_file(file_path)

    def _on_3d_filepath_entered(self):
        if not hasattr(self, 'input_3d_filepath') or not self.input_3d_filepath:
            return
        txt = self.input_3d_filepath.text().strip().strip('"\';\r\n ')
        if txt:
            self.load_design_file(txt)

    def _on_pgmfile_text_edited(self):
        if getattr(self, '_setting_pgm_text', False):
            return
        if not hasattr(self.ui, 'pgmfilegalvoTextEdit'):
            return
        txt = self.ui.pgmfilegalvoTextEdit.toPlainText().strip().strip('"\';\r\n ')
        if not txt:
            return
        if os.path.isfile(txt):
            self.load_design_file(txt)
        else:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            for sub in ["svg_files", "DeepEngrave", ""]:
                cand = os.path.join(base_dir, sub, txt) if sub else os.path.join(base_dir, txt)
                if os.path.isfile(cand):
                    self.load_design_file(cand)
                    break

    def load_design_file(self, filepath):
        if not filepath:
            return

        # If relative or filename only, check svg_files or DeepEngrave
        if not os.path.isabs(filepath) or not os.path.exists(filepath):
            base_dir = os.path.dirname(os.path.abspath(__file__))
            cand1 = os.path.join(base_dir, "svg_files", os.path.basename(filepath))
            cand2 = os.path.join(base_dir, "DeepEngrave", os.path.basename(filepath))
            cand3 = os.path.join(base_dir, filepath)
            if os.path.isfile(cand1):
                filepath = cand1
            elif os.path.isfile(cand2):
                filepath = cand2
            elif os.path.isfile(cand3):
                filepath = cand3

        if not os.path.isfile(filepath):
            self.showAutoCloseMessage("File Error", f"File not found:\n{filepath}", timeout_ms=3500)
            return

        self.pgm_file = filepath
        self.current_test_shape = None
        fname = os.path.basename(filepath)
        self.logger.info(f"File selected : {self.pgm_file}")

        self._setting_pgm_text = True
        try:
            if hasattr(self, 'programgalvo_widgets') and hasattr(self.programgalvo_widgets, 'pgmfilegalvotext'):
                self.wh.invokeMethod(self.programgalvo_widgets.pgmfilegalvotext, "set", fname)
            if hasattr(self.ui, 'pgmfilegalvoTextEdit'):
                self.ui.pgmfilegalvoTextEdit.setPlainText(fname)
            if hasattr(self, 'input_3d_filepath') and self.input_3d_filepath:
                self.input_3d_filepath.setText(fname)
            if hasattr(self, 'program_widgets') and hasattr(self.program_widgets, 'pgmfile'):
                self.wh.invokeMethod(self.program_widgets.pgmfile, "set", fname)
        finally:
            self._setting_pgm_text = False

        # Auto-detect Sliced G-Code or STL 3D Mesh and enable 3D Relief Engraving
        lower_path = filepath.lower()
        if lower_path.endswith(('.gcode', '.nc', '.tap', '.gco')):
            if hasattr(self, 'cb_enable_3d_engraving'):
                self.cb_enable_3d_engraving.setChecked(True)
            if hasattr(self, 'combo_3d_mode'):
                idx = self.combo_3d_mode.findText("Imported Sliced G-Code", Qt.MatchContains)
                if idx >= 0:
                    self.combo_3d_mode.setCurrentIndex(idx)
            self._cached_3d_key = None
            self.showAutoCloseMessage(
                "G-Code File Selected",
                f"Loaded: {fname}\n3D Imported G-Code mode enabled.\nClick 'Save' on Galvo Program page to slice.",
                timeout_ms=3500
            )
            # Immediately load and render the G-code toolpaths onto the preview canvas
            self.updatePreviewGalvo(filepath)
        elif lower_path.endswith(('.stl', '.obj')):
            if hasattr(self, 'cb_enable_3d_engraving'):
                self.cb_enable_3d_engraving.setChecked(True)
            if hasattr(self, 'combo_3d_mode'):
                idx = self.combo_3d_mode.findText("3D Mesh / STL Relief", Qt.MatchContains)
                if idx >= 0:
                    self.combo_3d_mode.setCurrentIndex(idx)
            self._cached_3d_key = None
            self.showAutoCloseMessage(
                "3D Mesh Selected",
                f"Loaded: {fname}\n3D STL Slicing mode enabled.\nClick 'Save' on Galvo Program page to slice.",
                timeout_ms=3500
            )

        # Cleanup orphaned param files and auto-fetch saved parameters
        dxf_dir = os.path.dirname(self.pgm_file)
        self.fh.cleanupOrphanedParams(dxf_dir)
        params = self.fh.loadDxfParams(self.pgm_file)
        if params:
            self._apply_loaded_params(params)

    def _apply_loaded_params(self, params):
        if not params:
            return
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

        pwr_val = nested_params.get("Laser Power")
        if pwr_val is not None:
            if hasattr(self.ui, 'laserpowerLineEdit'):
                self.ui.laserpowerLineEdit.setText(str(pwr_val))
            if hasattr(self.ui, 'pgmlaserpowerLineEdit'):
                self.ui.pgmlaserpowerLineEdit.setText(str(pwr_val))
            if hasattr(self.ui, 'galvolaserpowerHorizontalSlider_2'):
                self.ui.galvolaserpowerHorizontalSlider_2.setValue(int(float(pwr_val)))

        freq_val = nested_params.get("Laser Frequency")
        if freq_val is not None:
            if hasattr(self.ui, 'laserfreqLineEdit'):
                self.ui.laserfreqLineEdit.setText(str(freq_val))
            if hasattr(self.ui, 'pgmlaserfreqLineEdit'):
                self.ui.pgmlaserfreqLineEdit.setText(str(freq_val))
            if hasattr(self.ui, 'galvolaserfreqHorizontalSlider'):
                self.ui.galvolaserfreqHorizontalSlider.setValue(int(float(freq_val)))

        enable_hatch = nested_params.get("Enable Hatch")
        if enable_hatch is not None:
            self.ui.pgmenablehatchCheckBox.setChecked(enable_hatch)
            self.programsGalvoAction(self.ui.pgmenablehatchCheckBox)

        mode = nested_params.get("Mode")
        if mode is not None:
            cross = getattr(self.ui, 'pgmmodeCheckBox', None)
            if cross: cross.setChecked(mode)

        enable_engrave = nested_params.get("Enable Engraving")
        if enable_engrave is not None and hasattr(self, 'cb_enable_engraving'):
            self.cb_enable_engraving.setChecked(bool(enable_engrave))
            if nested_params.get("Engraving Material") and hasattr(self, 'combo_engrave_material'):
                self.combo_engrave_material.setCurrentText(str(nested_params.get("Engraving Material")))
            if nested_params.get("Engraving Depth") and hasattr(self, 'input_engrave_depth'):
                self.input_engrave_depth.setText(str(nested_params.get("Engraving Depth")))
            if nested_params.get("Engraving Step") and hasattr(self, 'input_engrave_step'):
                self.input_engrave_step.setText(str(nested_params.get("Engraving Step")))
            if nested_params.get("Engraving Style") and hasattr(self, 'combo_engrave_style'):
                self.combo_engrave_style.setCurrentText(str(nested_params.get("Engraving Style")))
            if nested_params.get("Engraving Pitch") and hasattr(self, 'input_engrave_pitch'):
                self.input_engrave_pitch.setText(str(nested_params.get("Engraving Pitch")))
            if nested_params.get("Engraving Substrate Height") and hasattr(self, 'input_engrave_obj_height'):
                self.input_engrave_obj_height.setText(str(nested_params.get("Engraving Substrate Height")))

        enable_3d = nested_params.get("Enable 3D Engraving")
        if enable_3d is not None and hasattr(self, 'cb_enable_3d_engraving'):
            self.cb_enable_3d_engraving.setChecked(bool(enable_3d))
            if nested_params.get("3D Material") and hasattr(self, 'combo_3d_material'):
                self.combo_3d_material.setCurrentText(str(nested_params.get("3D Material")))
            if nested_params.get("3D Resolution") and hasattr(self, 'combo_3d_resolution'):
                self.combo_3d_resolution.blockSignals(True)
                self.combo_3d_resolution.setCurrentText(str(nested_params.get("3D Resolution")))
                self.combo_3d_resolution.blockSignals(False)
            if nested_params.get("3D Slicing Mode") and hasattr(self, 'combo_3d_mode'):
                self.combo_3d_mode.setCurrentText(str(nested_params.get("3D Slicing Mode")))
            if nested_params.get("3D Model File") and hasattr(self, 'input_3d_filepath') and self.input_3d_filepath:
                self.input_3d_filepath.setText(str(nested_params.get("3D Model File")))
            if nested_params.get("3D Max Depth") and hasattr(self, 'input_3d_max_depth'):
                self.input_3d_max_depth.setText(str(nested_params.get("3D Max Depth")))
            if nested_params.get("3D Passes") and hasattr(self, 'input_3d_passes'):
                self.input_3d_passes.setText(str(nested_params.get("3D Passes")))
            if nested_params.get("3D Pitch") and hasattr(self, 'input_3d_pitch'):
                self.input_3d_pitch.setText(str(nested_params.get("3D Pitch")))

        self.showAutoCloseMessage("Parameters Fetched", "Previous parameters for this file have been loaded.", timeout_ms=3000)

    def programsGalvoAction(self, widget, *args):
        action = self.wh.getRole(widget)
        self.util.debugPrint(f"programsGalvoAction : {action}")
        
        if action == "pgmfilegalvo":
            initial_dir = self._get_initial_file_dir()
            filters = (
                "All Supported Files (*.gcode *.nc *.tap *.gco *.stl *.obj *.svg *.dxf *.bmp *.jpg *.png *.gbr *.txt);;"
                "G-Code Files (*.gcode *.nc *.tap *.gco);;"
                "All Files (*.*);;"
                "3D Mesh Files (*.stl *.obj);;"
                "SVG Files (*.svg);;"
                "DXF Files (*.dxf);;"
                "Image Files (*.bmp *.jpg *.png);;"
                "Gerber Files (*.gbr *.gtl *.gbl *.gto *.gbo *.gts *.gbs *.gml *.gtp *.gbp *.drl *.txt)"
            )
            selected_file, _ = QFileDialog.getOpenFileName(
                self,
                "Select Design / G-Code / 3D File",
                initial_dir,
                filters,
                "All Supported Files (*.gcode *.nc *.tap *.gco *.stl *.obj *.svg *.dxf *.bmp *.jpg *.png *.gbr *.txt)"
            )
            if selected_file:
                self.load_design_file(selected_file)

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
        elif action == "pgmheightgalvo":
            self.update_galvo_focus_calculations()
        elif action in ["pgmmarkspeedgalvo", "pgmjumpspeed", "pgmloopcount", "pgmstartposx", "pgmstartposy"]:
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
            self.update_galvo_focus_calculations()
                
            # Fetch Laser Power and Frequency from Design page widgets
            ui_laserpower = self.ui.pgmlaserpowerLineEdit.text() if hasattr(self.ui, 'pgmlaserpowerLineEdit') else None
            ui_laserfreq = self.ui.pgmlaserfreqLineEdit.text() if hasattr(self.ui, 'pgmlaserfreqLineEdit') else None
            try:
                self.pgm_laserpower = float(ui_laserpower) if ui_laserpower else None
                self.pgm_laserfreq = float(ui_laserfreq) if ui_laserfreq else None
            except ValueError:
                self.showAutoCloseMessage("Input Error", "Please enter valid numeric values for Power and Freq.")
                return

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
                        "Mode": getattr(self.ui, 'pgmmodeCheckBox', None) and self.ui.pgmmodeCheckBox.isChecked(),
                        "Laser Power": getattr(self, 'pgm_laserpower', None),
                        "Laser Frequency": getattr(self, 'pgm_laserfreq', None)
                    }
                }
                if hasattr(self, 'cb_enable_engraving'):
                    params["Galvo program page parameters"]["Enable Engraving"] = self.cb_enable_engraving.isChecked()
                    params["Galvo program page parameters"]["Engraving Material"] = self.combo_engrave_material.currentText()
                    params["Galvo program page parameters"]["Engraving Depth"] = self.input_engrave_depth.text()
                    params["Galvo program page parameters"]["Engraving Step"] = self.input_engrave_step.text()
                    params["Galvo program page parameters"]["Engraving Style"] = self.combo_engrave_style.currentText()
                    params["Galvo program page parameters"]["Engraving Pitch"] = self.input_engrave_pitch.text()
                    params["Galvo program page parameters"]["Engraving Substrate Height"] = self.input_engrave_obj_height.text()
                if hasattr(self, 'cb_enable_3d_engraving'):
                    params["Galvo program page parameters"]["Enable 3D Engraving"] = self.cb_enable_3d_engraving.isChecked()
                    if hasattr(self, 'combo_3d_material'):
                        params["Galvo program page parameters"]["3D Material"] = self.combo_3d_material.currentText()
                    if hasattr(self, 'combo_3d_resolution'):
                        params["Galvo program page parameters"]["3D Resolution"] = self.combo_3d_resolution.currentText()
                    params["Galvo program page parameters"]["3D Slicing Mode"] = self.combo_3d_mode.currentText()
                    params["Galvo program page parameters"]["3D Model File"] = str(getattr(self, 'pgm_file', ''))
                    params["Galvo program page parameters"]["3D Max Depth"] = self.input_3d_max_depth.text()
                    params["Galvo program page parameters"]["3D Passes"] = self.input_3d_passes.text()
                    params["Galvo program page parameters"]["3D Pitch"] = self.input_3d_pitch.text()
                if self.fh.saveDxfParams(self.pgm_file, params):
                    self.util.debugPrint(f"Saved parameters for Galvo file: {params}")
                    self.logger.info(f"Parameters saved for {self.pgm_file}")
            except Exception as e:
                self.logger.error(f"Failed to save parameters: {e}")
                
            # Apply to print page sliders so they reflect immediately
            pwr = getattr(self, 'pgm_laserpower', None)
            if pwr is not None:
                if hasattr(self.ui, 'galvolaserpowerHorizontalSlider_2'):
                    self.ui.galvolaserpowerHorizontalSlider_2.setValue(int(pwr))
            freq = getattr(self, 'pgm_laserfreq', None)
            if freq is not None:
                if hasattr(self.ui, 'galvolaserfreqHorizontalSlider'):
                    self.ui.galvolaserfreqHorizontalSlider.setValue(int(freq))
                
            is_3d = hasattr(self, 'cb_enable_3d_engraving') and self.cb_enable_3d_engraving.isChecked()
            if is_3d:
                self.showMainPages("printgalvo")
                self.start_background_3d_slicing()
            elif self.process_galvo_file():
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
        
        # Check if a .cor file is loaded and provides a native scale
        calib_scale = None
        if hasattr(self, 'galvo_controller') and hasattr(self.galvo_controller, 'connection'):
            if hasattr(self.galvo_controller.connection, 'calibration'):
                calib = self.galvo_controller.connection.calibration
                if calib.is_valid and calib.scale is not None:
                    calib_scale = calib.scale
        
        if calib_scale:
            galvo_units_per_mm = calib_scale
            lens_size = 65535 / calib_scale
            self.galvo_config.field_size = lens_size
        else:
            galvo_units_per_mm = 65535 / self.galvo_config.field_size
            lens_size = self.galvo_config.field_size

        try:
            raw_jump = float(self.wh.invokeMethod(self.programgalvo_widgets.pgmjumpspeed, "get") or 2000.0)
            raw_mark = float(self.wh.invokeMethod(self.programgalvo_widgets.pgmmarkspeedgalvo, "get") or 1000.0)
            
            # Auto-correct legacy raw bit speeds to standard mm/s speeds
            if raw_jump > 50000: raw_jump = 2000.0
            if raw_mark > 50000: raw_mark = 1000.0
            
            # Convert UI mm/s into galvo bits/s for the hardware (EZCAD equivalent)
            jump_speed = int(raw_jump * galvo_units_per_mm)
            mark_speed = int(raw_mark * galvo_units_per_mm)
            
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
        elif filepath.lower().endswith(('.bmp', '.jpg', '.jpeg', '.png')):
            is_3d = hasattr(self, 'cb_enable_3d_engraving') and self.cb_enable_3d_engraving.isChecked()
            if is_3d:
                target_sz = 27.0
                try:
                    if hasattr(self, 'input_3d_size') and self.input_3d_size.text().strip():
                        target_sz = float(self.input_3d_size.text().strip() or 27.0)
                except Exception:
                    target_sz = 27.0
                mode_text = self.combo_3d_mode.currentText() if hasattr(self, 'combo_3d_mode') else ""
                if "Coin" in mode_text:
                    r = target_sz / 2.0
                    angles = np.linspace(0, 2 * np.pi, 64, endpoint=False)
                    polygons = [[(float(start_x + r * np.cos(a)), float(start_y + r * np.sin(a))) for a in angles]]
                else:
                    hw = target_sz / 2.0
                    polygons = [[
                        (float(start_x - hw), float(start_y - hw)),
                        (float(start_x + hw), float(start_y - hw)),
                        (float(start_x + hw), float(start_y + hw)),
                        (float(start_x - hw), float(start_y + hw)),
                        (float(start_x - hw), float(start_y - hw))
                    ]]
            else:
                from core.image_parser import ImageParser
                parser = ImageParser(field_size=self.galvo_config.field_size)
                polygons = parser.parse_to_polygons(filepath)
        elif filepath.lower().endswith(('.gbr', '.gtl', '.gbl', '.gto', '.gbo', '.gts', '.gbs', '.gml', '.gtp', '.gbp', '.drl', '.txt')):
            from gerber_parser import GerberParser
            parser = GerberParser(filepath)
            polygons = parser.parse_to_polygons(field_size=self.galvo_config.field_size)
        elif filepath.lower().endswith(('.stl', '.obj')):
            from core.stl_3d_engraver import STL3DEngraver
            target_sz = 27.0
            try:
                if hasattr(self, 'input_3d_size') and self.input_3d_size.text().strip():
                    target_sz = float(self.input_3d_size.text().strip() or 27.0)
            except Exception:
                target_sz = 27.0
            engraver = STL3DEngraver(
                stl_path=filepath,
                target_size_mm=target_sz,
                field_size=self.galvo_config.field_size
            )
            mode_text = self.combo_3d_mode.currentText() if hasattr(self, 'combo_3d_mode') else ""
            if "Coin" in mode_text:
                r = engraver.target_size_mm / 2.0
                angles = np.linspace(0, 2 * np.pi, 64, endpoint=False)
                polygons = [[(float(start_x + r * np.cos(a)), float(start_y + r * np.sin(a))) for a in angles]]
            else:
                hw = (engraver.width_mm or target_sz) / 2.0
                hh = (engraver.height_mm or target_sz) / 2.0
                polygons = [[
                    (float(start_x - hw), float(start_y - hh)),
                    (float(start_x + hw), float(start_y - hh)),
                    (float(start_x + hw), float(start_y + hh)),
                    (float(start_x - hw), float(start_y + hh)),
                    (float(start_x - hw), float(start_y - hh))
                ]]
        elif filepath.lower().endswith(('.gcode', '.nc', '.tap', '.gco')):
            from core.gcode_3d_adapter import GCode3DAdapter
            try:
                passes_cnt = int(self.input_3d_passes.text() or 50)
            except Exception:
                passes_cnt = 50
            target_sz = None
            try:
                if hasattr(self, 'input_3d_size') and self.input_3d_size.text().strip():
                    target_sz = float(self.input_3d_size.text().strip() or 27.0)
            except Exception:
                target_sz = None
            mode_text = self.combo_3d_mode.currentText() if hasattr(self, 'combo_3d_mode') else ""
            target_dia = target_sz if "Coin" in mode_text else None
            adapter = GCode3DAdapter(
                gcode_path=filepath,
                field_size=self.galvo_config.field_size,
                target_passes=passes_cnt,
                target_diameter_mm=target_dia,
                offset_x_mm=start_x,
                offset_y_mm=start_y
            )
            w = adapter.bounding_box['width'] * adapter.scale_factor
            h = adapter.bounding_box['height'] * adapter.scale_factor
            half_w, half_h = w / 2.0, h / 2.0
            polygons = [[
                (float(start_x - half_w), float(start_y - half_h)),
                (float(start_x + half_w), float(start_y - half_h)),
                (float(start_x + half_w), float(start_y + half_h)),
                (float(start_x - half_w), float(start_y + half_h)),
                (float(start_x - half_w), float(start_y - half_h))
            ]]
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
        
        if w > lens_size or h > lens_size:
            self.showCustomPopup("Design Too Large", f"Design size ({w:.1f}x{h:.1f}mm) is larger than lens area ({lens_size}x{lens_size}mm).", buttons=QMessageBox.Ok)
            return False
            
        max_shift_x = (lens_size - w) / 2.0
        max_shift_y = (lens_size - h) / 2.0
        
        if abs(start_x) > max_shift_x or abs(start_y) > max_shift_y:
            self.showCustomPopup("Invalid Start Position", f"Design size is {w:.1f}x{h:.1f}mm.\nFor a {lens_size}x{lens_size}mm lens:\nValid Start Pos X: {-max_shift_x:.1f} to {max_shift_x:.1f}\nValid Start Pos Y: {-max_shift_y:.1f} to {max_shift_y:.1f}\n\nPlease adjust the Start Pos.", buttons=QMessageBox.Ok)
            return False
            
        design_center_x = min_x + w / 2.0
        design_center_y = min_y + h / 2.0
        shift_x = start_x - design_center_x
        shift_y = start_y - design_center_y

        self.planner.clear()
        
        is_3d = (hasattr(self, 'cb_enable_3d_engraving') and self.cb_enable_3d_engraving.isChecked()) or filepath.lower().endswith(('.gcode', '.nc', '.tap', '.gco'))
        if is_3d:
            if hasattr(self, 'cb_enable_3d_engraving'):
                self.cb_enable_3d_engraving.setChecked(True)
            q_3d = self.get_3d_engraving_queue()
            if q_3d:
                self.planner.send_queue = list(q_3d)
                self.planner.preview_queue = [cmd for cmd in q_3d if cmd.get('type') in ('jump', 'mark')]
                if hasattr(self, "galvo_preview"):
                    if hasattr(self, 'slider_3d_layer') and hasattr(self, '_cached_3d_layers') and self._cached_3d_layers:
                        curr_l = self.slider_3d_layer.value() if self.slider_3d_layer.value() > 0 else 1
                        self.render_3d_preview_layer(curr_l)
                    else:
                        self.galvo_preview.draw_queue(self.planner.preview_queue)
                self.update_galvo_preview_bounds()
                return True
            elif filepath.lower().endswith(('.gcode', '.nc', '.tap', '.gco')):
                return False
        
        is_hatch = self.ui.pgmenablehatchCheckBox.isChecked()
        is_engraving = hasattr(self, 'cb_enable_engraving') and self.cb_enable_engraving.isChecked()
        mark_contour = getattr(self.ui, 'pgmmarkcontourCheckBox', None) and self.ui.pgmmarkcontourCheckBox.isChecked()
        
        # If hatching is not enabled and engraving is not enabled, mark contour
        if not is_hatch and not is_engraving:
            mark_contour = True
        
        hatch_configs = []
        if is_hatch or is_engraving:
            if is_hatch:
                self.save_current_hatch_profile()
                
                def build_cfg(p):
                    return {
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
                
                for k, p in self.hatch_profiles.items():
                    if not p.get("enable", False):
                        continue
                    try:
                        hatch_configs.append(build_cfg(p))
                    except Exception as e:
                        self.util.debugPrint(f"Hatch config {k} error: {e}")
                        pass
                        
                if not hatch_configs and not is_engraving:
                    # If hatch is globally enabled but no profiles are enabled, force profile 1
                    if 1 not in self.hatch_profiles:
                        self.hatch_profiles[1] = {"enable": True}
                    else:
                        self.hatch_profiles[1]["enable"] = True
                    
                    k = 1
                    try:
                        hatch_configs.append(build_cfg(self.hatch_profiles[1]))
                        # Also update UI if it's the currently selected profile
                        if getattr(self, 'current_hatch_idx', 1) == 1:
                            self.ui.pgmenableCheckBox.setChecked(True)
                    except Exception as e:
                        self.util.debugPrint(f"Hatch config {k} fallback error: {e}")

            # If engraving is active and no manual hatch configs, inject engraving pattern
            if is_engraving and not hatch_configs:
                style_name = self.combo_engrave_style.currentText()
                try:
                    pitch_val = float(self.input_engrave_pitch.text() or 0.04)
                except Exception:
                    pitch_val = 0.04
                engrave_cfg = EngravingManager.get_hatch_config_for_style(style_name, pitch_val)
                engrave_cfg['hatch_idx'] = 1
                hatch_configs = [engrave_cfg]
                print(f"[Engraving] Auto-injected hatch config for '{style_name}' with pitch {pitch_val:.3f} mm")
                
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
                
        if (is_hatch or is_engraving) and hatch_configs:
            self.planner.generate_hatch(
                all_polys_galvo, 
                hatch_configs,
                mark_speed=mark_speed, 
                jump_speed=jump_speed,
                galvo_units_per_mm=galvo_units_per_mm
            )
            
        if not (is_hatch or is_engraving) or not hatch_configs:
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

        is_3d = hasattr(self, 'cb_enable_3d_engraving') and self.cb_enable_3d_engraving.isChecked()
        if hasattr(self, 'layer_slider_frame'):
            self.layer_slider_frame.setVisible(is_3d)

        if is_3d:
            if hasattr(self, '_cached_3d_layers') and self._cached_3d_layers:
                curr_l = self.slider_3d_layer.value() if hasattr(self, 'slider_3d_layer') and self.slider_3d_layer.value() > 0 else 1
                self.render_3d_preview_layer(curr_l)
        elif hasattr(self, "galvo_preview"):
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
                
                is_3d = hasattr(self, 'cb_enable_3d_engraving') and self.cb_enable_3d_engraving.isChecked()
                check_queue = self.planner.send_queue
                if is_3d and not check_queue:
                    check_queue = self.get_3d_engraving_queue()
                if not check_queue:
                    self.showAutoCloseMessage("Empty Queue", "Load a pattern first.")
                    return
                min_x, max_x, min_y, max_y = float('inf'), float('-inf'), float('inf'), float('-inf')
                for cmd in check_queue:
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
                
                # Check if hardware connection supports setting power and frequency
                if hasattr(self.galvo_controller, "connection") and hasattr(self.galvo_controller.connection, "set_analog_do_bit"):
                    # Invert the power signal in Python to compensate for the Blackpill's hardware mapping
                    if hasattr(self.galvo_controller.connection, 'map_laser_power'):
                        inverted_power = self.galvo_controller.connection.map_laser_power(slider_value)
                    else:
                        inverted_power =  100.0 - slider_value
                    # bit=2 is Analog Power (Pin 2). bit=3 is PRR Frequency (Pin 3).
                    self.galvo_controller.connection.set_analog_do_bit(max_val, inverted_power, 50.0, 2)
                    self.galvo_controller.connection.set_analog_do_bit(100.0, 50.0, self.galvo_controller.connection.clamp_laser_freq(freq_val) / 4.0 if hasattr(self.galvo_controller.connection, 'clamp_laser_freq') else freq_val / 4.0, 3)
                    
                    if action == "powersetgalvo":
                        self.showAutoCloseMessage("Power Set", f"Laser power set to {slider_percentage:.0f}%")
                    elif action == "freqsetgalvo":
                        self.showAutoCloseMessage("Frequency Set", f"Frequency set to {freq_val:.0f} kHz")
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
            is_gcode_file = getattr(self, 'pgm_file', '') and str(self.pgm_file).lower().endswith(('.gcode', '.nc', '.tap', '.gco'))
            enable_3d = (hasattr(self, 'cb_enable_3d_engraving') and self.cb_enable_3d_engraving.isChecked()) or is_gcode_file
            if is_gcode_file and hasattr(self, 'cb_enable_3d_engraving'):
                self.cb_enable_3d_engraving.setChecked(True)
            if not enable_3d and not self.planner.send_queue:
                self.showAutoCloseMessage("Empty Queue", "Load a pattern first.")
                return
                
            # Serial Number Validation
            if hasattr(self, 'cb_use_serial') and self.cb_use_serial.isChecked():
                sn_text = self.serial_number_input.text().strip()
                if not sn_text:
                    self.showCustomPopup("Error", "Please enter a Serial Number (e.g. SN-001) before printing.")
                    return
                if not sn_text[-1].isdigit():
                    self.showCustomPopup("Error", "Serial Number must end with a number!")
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
                        
                    finalobjectfocus = focus_z - galvoobjheight
                    
                    try:
                        galvosampleheight = float(self.ui.pgmheightgalvoLineEdit.text() or 0.0)
                    except ValueError:
                        galvosampleheight = 0.0
                        
                    finalgalvofocus = finalobjectfocus + galvosampleheight
                    
                    self.ch.addParameter("focus", "galvoobjheight", f"{galvoobjheight:.2f}")
                    self.ch.addParameter("focus", "galvosampleheight", f"{galvosampleheight:.2f}")
                    self.ch.addParameter("focus", "finalobjectfocus", f"{finalobjectfocus:.2f}")
                    self.ch.addParameter("focus", "finalgalvofocus", f"{finalgalvofocus:.2f}")
                    if hasattr(self, 'config_file_path'):
                        self.ch.updateFile(self.config_file_path)

                    current_z = getattr(self.stepper_controller, 'z_position', None)
                    is_already_homed = getattr(self.stepper_controller, 'is_homed', False)
                    
                    if current_z is not None and abs(current_z - finalgalvofocus) < 0.05:
                        print(f"Z axis is already at focus position ({current_z:.2f} mm). Skipping Z motion.")
                    else:
                        if not is_already_homed or current_z is None:
                            print("Homing Z axis before moving to focus position...")
                            self.showAutoCloseMessage("Homing", "Homing Z-axis...", timeout_ms=1500)
                            if not self.stepper_controller.home_z(app_instance=QApplication.instance()):
                                self.showAutoCloseMessage("Error", "Failed to home Z-axis. Cannot start print.")
                                return
                            self.stepper_controller.is_homed = True
                            
                        print(f"Moving Z axis to focus position: {finalgalvofocus:.2f} mm (Base: {focus_z}, ObjHeight: {galvoobjheight}, SampleHeight: {galvosampleheight})")
                        self.stepper_controller.move_z_absolute(finalgalvofocus, speed=1000)
                        self.ah.pos("Z", self.stepper_controller.z_position)
                        self.jogPosDisplay()
                        self.focusPosDisplay()
                        import time
                        while time.time() < getattr(self.stepper_controller, 'next_ready_time', time.time()):
                            QApplication.instance().processEvents()
                            time.sleep(0.02)
            except Exception as e:
                print(f"Failed to move Z axis to focus position: {e}")

            try:
                loop_count = int(self.wh.invokeMethod(self.programgalvo_widgets.pgmloopcount, "get") or 1)
            except:
                loop_count = 1
                
            try:
                slider_percentage = float(self.ui.galvolaserpowerHorizontalSlider_2.value())
                freq_val = float(self.ui.galvolaserfreqHorizontalSlider.value())
                
                # Fix: Update the controller's live power/freq tracking so ExecutionThread uses these values
                self.galvo_controller.live_power = slider_percentage
                self.galvo_controller.live_freq = freq_val
                
                if hasattr(self.galvo_controller, "connection") and hasattr(self.galvo_controller.connection, "set_analog_do_bit"):
                    # Invert the power signal in Python to compensate for the Blackpill's hardware mapping
                    if hasattr(self.galvo_controller.connection, 'map_laser_power'):
                        inverted_power = self.galvo_controller.connection.map_laser_power(slider_percentage)
                    else:
                        inverted_power =  100.0 - slider_percentage
                    # bit=2 is Analog Power (Pin 2). bit=3 is PRR Frequency (Pin 3).
                    self.galvo_controller.connection.set_analog_do_bit(100.0, inverted_power, 50.0, 2)
                    self.galvo_controller.connection.set_analog_do_bit(100.0, 50.0, self.galvo_controller.connection.clamp_laser_freq(freq_val) / 4.0 if hasattr(self.galvo_controller.connection, 'clamp_laser_freq') else freq_val / 4.0, 3)
                print(f"Applied Print Power: {slider_percentage}% | Freq: {freq_val}kHz")
            except Exception as e:
                print(f"Failed to apply print power/frequency: {e}")
                
            self.wh.invokeMethod(widget, "disable")
            self.wh.invokeMethod(self.printgalvo_widgets.printabortgalvo, "enable")
            self.wh.invokeMethod(self.printgalvo_widgets.redlightpre, "disable")
            
            # Enable Pause button
            self.updateGalvoPauseUI(is_paused=False, enabled=True)
            if hasattr(self, 'galvo_controller'):
                self.galvo_controller.is_paused = False
                
            enable_engrave = hasattr(self, 'cb_enable_engraving') and self.cb_enable_engraving.isChecked()
            enable_3d = (hasattr(self, 'cb_enable_3d_engraving') and self.cb_enable_3d_engraving.isChecked()) or is_gcode_file
            
            queue_to_execute = self.planner.send_queue
            if enable_3d:
                self.util.debugPrint("[3D Engraving] Compiling 3D relief toolpaths...")
                self.showAutoCloseMessage("Compiling 3D Model", "Generating 3D relief toolpaths and micro-hatch vectors...", timeout_ms=3000)
                q_3d = self.get_3d_engraving_queue()
                if q_3d:
                    queue_to_execute = q_3d
                    loop_count = 1
                    enable_engrave = False # Already multi-pass in the compiled 3D queue
                else:
                    self.showAutoCloseMessage("Error", "Failed to compile 3D relief toolpaths.")
                    return
            
            z_step = 0.05
            target_depth = 1.0
            if enable_engrave:
                try:
                    z_step = float(self.input_engrave_step.text() or 0.05)
                except ValueError:
                    z_step = 0.05
                try:
                    target_depth = float(self.input_engrave_depth.text() or 1.0)
                except ValueError:
                    target_depth = 1.0

            safe_z = locals().get('finalgalvofocus', getattr(self.stepper_controller, 'z_position', None))

            self.galvo_exec_thread = ExecutionThread(
                self.galvo_controller, 
                queue_to_execute, 
                loop_count,
                stepper_controller=self.stepper_controller,
                enable_engraving=enable_engrave,
                z_step_mm=z_step,
                target_depth_mm=target_depth,
                settle_delay_s=0.15,
                safe_return_z=safe_z
            )
            self.galvo_exec_thread.finished_signal.connect(self.on_galvo_execution_finished)
            self.galvo_exec_thread.progress_signal.connect(self.on_galvo_execution_progress)
            self.galvo_exec_thread.depth_signal.connect(self.on_engraving_depth_progress)
            
            if hasattr(self, "galvo_preview"):
                self.galvo_preview.reset_progress()
                
            if hasattr(self.ui, 'printgalvoProgressBar'):
                self.ui.printgalvoProgressBar.setValue(0)
            if hasattr(self.ui, 'progressLabel_2'):
                self.ui.progressLabel_2.setText("0%")
                
            self.galvo_exec_thread.start()

        elif action == "printabortgalvo":
            # Clear Serial Number on Abort
            if hasattr(self, 'cb_use_serial') and self.cb_use_serial.isChecked() and hasattr(self, 'serial_number_input'):
                self.serial_number_input.clear()
                
            self.updateGalvoPauseUI(is_paused=False, enabled=False)
            if hasattr(self, 'galvo_controller'):
                self.galvo_controller.is_paused = False
                
            if hasattr(self, "galvo_exec_thread") and self.galvo_exec_thread.isRunning():
                self.wh.invokeMethod(widget, "disable")
                self.galvo_exec_thread.abort()
                
            if self.galvo_controller.connection and hasattr(self.galvo_controller.connection, 'stop'):
                self.galvo_controller.connection.stop()
                
            self.showMainPages("programsgalvo")
            
            if hasattr(self.ui, 'printgalvoProgressBar'):
                self.ui.printgalvoProgressBar.setValue(0)
            if hasattr(self.ui, 'progressLabel_2'):
                self.ui.progressLabel_2.setText("0%")
                
            self.planner.clear()
            if hasattr(self, "galvo_preview"):
                self.galvo_preview.draw_queue([])

        elif action == "printpausegalvo":
            if hasattr(self, "galvo_controller"):
                if getattr(self.galvo_controller, "is_paused", False):
                    # It was paused, now resume
                    self.galvo_controller.is_paused = False
                    self.updateGalvoPauseUI(is_paused=False)
                else:
                    # It was running, now pause
                    self.galvo_controller.is_paused = True
                    self.updateGalvoPauseUI(is_paused=True)
                        
    def on_galvo_execution_progress(self, idx, total, x, y, ctype):
        if ctype and str(ctype).startswith("3d_layer:"):
            try:
                parts = str(ctype).split(":")
                layer_num = int(parts[1])
                total_layers = int(parts[2])
                depth_val = float(parts[3])
                ang_val = float(parts[4])
                self.update_3d_layer_printing_ui(layer_num, total_layers, depth_val, ang_val)
            except Exception as e:
                print(f"[3D Progress Parse Error] {e}")
            return

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
            if hasattr(self, "_current_engraving_info") and self._current_engraving_info:
                pass_str = f"{self._current_engraving_info} | "
            elif hasattr(self, "_current_printing_pass"):
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
        
        self.updateGalvoPauseUI(is_paused=False, enabled=False)
        if hasattr(self, 'galvo_controller'):
            self.galvo_controller.is_paused = False

        if hasattr(self, 'label_3d_layer_status'):
            if hasattr(self, 'cb_enable_3d_engraving') and self.cb_enable_3d_engraving.isChecked():
                tot = self.slider_3d_layer.maximum() if hasattr(self, 'slider_3d_layer') else 50
                self.label_3d_layer_status.setText(f"✅ 3D Relief Complete ({tot} Layers Finished)")
            
        is_disconnected = False
        if self.galvo_controller.connection and hasattr(self.galvo_controller.connection, 'is_physically_connected'):
            if not self.galvo_controller.connection.is_physically_connected():
                is_disconnected = True
                
        if success:
            if hasattr(self, '_current_engraving_info') and self._current_engraving_info:
                self.showAutoCloseMessage("Success", f"Engraving complete! {self._current_engraving_info}")
                self._current_engraving_info = ""
            else:
                self.showAutoCloseMessage("Success", "Galvo execution complete.")
            
            # Auto-increment Serial Number
            if hasattr(self, 'cb_use_serial') and self.cb_use_serial.isChecked() and hasattr(self, 'serial_number_input'):
                text = self.serial_number_input.text().strip()
                if text:
                    import re
                    match = re.search(r'(\d+)$', text)
                    if match:
                        num_str = match.group(1)
                        num_len = len(num_str)
                        new_num = int(num_str) + 1
                        new_text = text[:-num_len] + str(new_num).zfill(num_len)
                        self.serial_number_input.setText(new_text)
        else:
            if hasattr(self, '_current_engraving_info'):
                self._current_engraving_info = ""
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
                if hasattr(self, 'cad_widget') and self.cad_widget:
                    self.cad_widget.refresh_field_size()
                
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
            initial_dir = self._get_initial_file_dir()
            filters = (
                "All Supported Files (*.gcode *.nc *.tap *.gco *.dxf *.svg *.stl *.obj *.bmp *.jpg *.png);;"
                "G-Code Files (*.gcode *.nc *.tap *.gco);;"
                "DXF Files (*.dxf);;"
                "SVG Files (*.svg);;"
                "All Files (*.*)"
            )
            selected_file, _ = QFileDialog.getOpenFileName(
                self,
                "Select Program File",
                initial_dir,
                filters,
                "All Supported Files (*.gcode *.nc *.tap *.gco *.dxf *.svg *.stl *.obj *.bmp *.jpg *.png)"
            )
            
            if selected_file:
                self.load_design_file(selected_file)

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
                        
                    power = data.get("Laser Power") or data.get("laserpower")
                    if power is not None:
                        self.wh.invokeMethod(self.program_widgets.pgmlaserpower, "set", str(power))
                        self.pgm_laserpower = float(power)
                        
                    freq = data.get("Laser Frequency") or data.get("laserfreq")
                    if freq is not None:
                        self.wh.invokeMethod(self.program_widgets.pgmlaserfreq, "set", str(freq))
                        self.pgm_laserfreq = float(freq)
                    
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
            ui_laserpower = self.wh.invokeMethod(self.program_widgets.pgmlaserpower, "get")
            ui_laserfreq = self.wh.invokeMethod(self.program_widgets.pgmlaserfreq, "get")

            try:
                self.pgm_height = float(ui_height)
                self.pgm_feed = float(ui_feed)
                self.pgm_laserpower = float(ui_laserpower) if ui_laserpower else None
                self.pgm_laserfreq = float(ui_laserfreq) if ui_laserfreq else None
            except ValueError:
                 self.showAutoCloseMessage("Input Error", "Please enter valid numeric values for Height, Feed, Power, and Freq.")
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
            if hasattr(self, 'pgm_laserpower') and self.pgm_laserpower is not None:
                dxfparser.setPower(self.pgm_laserpower)
            if hasattr(self, 'pgm_laserfreq') and self.pgm_laserfreq is not None:
                dxfparser.setFreq(self.pgm_laserfreq)

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
                    "Selected Laser": self.pgm_laser,
                    "Laser Power": getattr(self, 'pgm_laserpower', None),
                    "Laser Frequency": getattr(self, 'pgm_laserfreq', None)
                }
            }
            if self.fh.saveDxfParams(self.pgm_file, params):
                self.util.debugPrint(f"Saved parameters for DXF: {params}")
                self.logger.info(f"Parameters saved for {self.pgm_file}")

            # Apply to print page sliders
            pwr = getattr(self, 'pgm_laserpower', None)
            if pwr is not None:
                if hasattr(self.ui, 'powerHorizontalSlider'):
                    self.ui.powerHorizontalSlider.setValue(int(pwr))
                if hasattr(self.ui, 'galvolaserpowerHorizontalSlider_2'):
                    self.ui.galvolaserpowerHorizontalSlider_2.setValue(int(pwr))
                    
            freq = getattr(self, 'pgm_laserfreq', None)
            if freq is not None:
                if hasattr(self.ui, 'freqHorizontalSlider'):
                    self.ui.freqHorizontalSlider.setValue(int(freq))
                if hasattr(self.ui, 'galvolaserfreqHorizontalSlider'):
                    self.ui.galvolaserfreqHorizontalSlider.setValue(int(freq))

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
        ui_laserpower = self.wh.invokeMethod(self.program_widgets.pgmlaserpower, "get")
        ui_laserfreq = self.wh.invokeMethod(self.program_widgets.pgmlaserfreq, "get")
        
        try:
            float(ui_height)
            float(ui_feed)
            if ui_laserpower: float(ui_laserpower)
            if ui_laserfreq: float(ui_laserfreq)
        except (ValueError, TypeError):
            return
            
        if not ui_laser or str(ui_laser).strip() == "" or str(ui_laser) == "Select Laser":
            return
            
        # If we pass all validation checks, enable the Save button
        self.wh.invokeMethod(self.program_widgets.pgmsaveset, "enable")
        
        # Sync with print page sliders for Galvo mode
        try:
            if ui_laserpower:
                pwr = float(ui_laserpower)
                if hasattr(self.ui, 'galvolaserpowerHorizontalSlider_2'):
                    self.ui.galvolaserpowerHorizontalSlider_2.setValue(int(pwr))
            if ui_laserfreq:
                freq = float(ui_laserfreq)
                if hasattr(self.ui, 'galvolaserfreqHorizontalSlider'):
                    self.ui.galvolaserfreqHorizontalSlider.setValue(int(freq))
        except ValueError:
            pass

                
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
    def mapmatrixAction(self, widget, *args):
        action = self.wh.getRole(widget)
        self.logger.info(f"mapmatrixAction : {action}")
        
        if not hasattr(self, 'mapping_controller'):
            return

        if action == "redmarkmat":
            self.mapping_controller.run_preview()
        elif action == "lasermarkmat":
            self.mapping_controller.run_mark()
        elif action == "stopmat":
            self.mapping_controller.abort()

        
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
            "printgalvo": "printgalvo",
            "qrgalvo": "qrgalvo",
            "cad": "cadgalvo",
            "cadgalvo": "cadgalvo",
            "cadPage": "cadgalvo"
        }
        
        role = button_map.get(page)
        btn = self.left_menu_widgets.get(role) if role else None
        
        if btn:
            btn.click()
        else:
            self.main_stack.setCurrentIndex(arg)

        if page == "printgalvo" or role == "printgalvo":
            is_3d = hasattr(self, 'cb_enable_3d_engraving') and self.cb_enable_3d_engraving.isChecked()
            if hasattr(self, 'layer_slider_frame'):
                self.layer_slider_frame.setVisible(is_3d)
            if is_3d:
                if hasattr(self, '_cached_3d_layers') and self._cached_3d_layers:
                    tot = len(self._cached_3d_layers)
                    cur = self.slider_3d_layer.value() if hasattr(self, 'slider_3d_layer') else 1
                    if hasattr(self, 'slider_3d_layer'):
                        self.slider_3d_layer.blockSignals(True)
                        self.slider_3d_layer.setMaximum(tot)
                        self.slider_3d_layer.setValue(cur)
                        self.slider_3d_layer.blockSignals(False)
                    self.render_3d_preview_layer(cur)
            
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
                 
                 # Dynamically scale power if S parameter exists in the ON command
                 if gstr == "M3" and hasattr(self, 'pgm_laserpower') and self.pgm_laserpower is not None:
                     import re
                     match = re.search(r'S(\d+)', gcode)
                     if match:
                         max_s = float(match.group(1))
                         # If max_s is 0 (unlikely for an ON command), fallback to 255
                         if max_s == 0: max_s = 255.0
                         new_s = int(max_s * (float(self.pgm_laserpower) / 100.0))
                         gcode = re.sub(r'S\d+', f'S{new_s}', gcode)
                         
                 self.sendGcode(gcode)
                 return

        self.sendGcode(gstr)

    
    def jogPosDisplay(self):                
        xpos = self.ah.getAxis("X").pos
        ypos = self.ah.getAxis("Y").pos
        zpos = self.ah.getAxis("Z").pos
        
        if hasattr(self, 'jog_widgets'):
            self.wh.invokeMethod(self.jog_widgets.xpos, "set", xpos)
            self.wh.invokeMethod(self.jog_widgets.ypos, "set", ypos)
            self.wh.invokeMethod(self.jog_widgets.zpos, "set", zpos)
        
        if hasattr(self.ui, 'xposgalvoLCDNumber'):
            self.ui.xposgalvoLCDNumber.display("0")
            self.ui.yposgalvoLCDNumber.display("0")
            self.ui.zposgalvoLCDNumber.display(f"{zpos:.2f}")

    
    def focusPosDisplay(self):
        zpos = self.ah.getAxis("Z").pos
        if hasattr(self, 'focus_widgets'):
            self.wh.invokeMethod(self.focus_widgets.focus, "set", zpos)
        
        if hasattr(self.ui, 'focusgalvoLCDNumber'):
            self.ui.focusgalvoLCDNumber.display(f"{zpos:.2f}")

    
    def offsetPosDisplay(self):
        xpos = self.ah.getAxis("X").pos
        ypos = self.ah.getAxis("Y").pos

        if hasattr(self, 'offset_widgets'):
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
        if hasattr(self, 'focus_widgets') and hasattr(self.focus_widgets, 'flaser'): self.focus_widgets.flaser.blockSignals(True)
        if hasattr(self, 'offset_widgets') and hasattr(self.offset_widgets, 'offlaser'): self.offset_widgets.offlaser.blockSignals(True)
        if hasattr(self, 'program_widgets') and hasattr(self.program_widgets, 'pgmlaser'): self.program_widgets.pgmlaser.blockSignals(True)

        # Focus laser combo
        if hasattr(self, 'focus_widgets'):
            self.wh.invokeMethod(self.focus_widgets.flaser, "add", self.laser_data_list)
            if hasattr(self.focus_widgets, 'flaser'):
                self.focus_widgets.flaser.setPlaceholderText("Select Laser")
                self.focus_widgets.flaser.setCurrentIndex(-1)

        # Offset laser combo
        if hasattr(self, 'offset_widgets'):
            self.wh.invokeMethod(self.offset_widgets.offlaser, "add", self.laser_data_list)
            if hasattr(self.offset_widgets, 'offlaser'):
                self.offset_widgets.offlaser.setPlaceholderText("Select Laser")
                self.offset_widgets.offlaser.setCurrentIndex(-1)

        # Program laser combo
        if hasattr(self, 'program_widgets'):
            self.wh.invokeMethod(self.program_widgets.pgmlaser, "add", self.laser_data_list)
            if hasattr(self.program_widgets, 'pgmlaser'):
                self.program_widgets.pgmlaser.setPlaceholderText("Select Laser")
                self.program_widgets.pgmlaser.setCurrentIndex(-1)

        # Initial button states
        if hasattr(self, 'focus_widgets'):
            self.wh.invokeMethod(self.focus_widgets.flaser, "enable")
            self.wh.invokeMethod(self.focus_widgets.fset, "disable")
            self.wh.invokeMethod(self.focus_widgets.flaserset, "disable")

        if hasattr(self, 'offset_widgets'):
            self.wh.invokeMethod(self.offset_widgets.offlaser, "enable")
            self.wh.invokeMethod(self.offset_widgets.offlaserset, "disable")
            self.wh.invokeMethod(self.offset_widgets.offzero, "disable")
            self.wh.invokeMethod(self.offset_widgets.offset, "disable")
        
        # Unblock signals
        if hasattr(self, 'focus_widgets') and hasattr(self.focus_widgets, 'flaser'): self.focus_widgets.flaser.blockSignals(False)
        if hasattr(self, 'offset_widgets') and hasattr(self.offset_widgets, 'offlaser'): self.offset_widgets.offlaser.blockSignals(False)
        if hasattr(self, 'program_widgets') and hasattr(self.program_widgets, 'pgmlaser'): self.program_widgets.pgmlaser.blockSignals(False)
    
    
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
#         self.wh.invokeMethod(self.left_menu_widgets.camerajog, "enable")
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
#             self.wh.invokeMethod(self.left_menu_widgets.camerajog, "disable")
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
            
            # Apply power and frequency to Galvo hardware if connected
            if hasattr(self, 'galvo_controller') and self.galvo_controller.is_connected:
                conn = self.galvo_controller.connection
                if hasattr(conn, 'set_analog_do_bit'):
                    pwr = getattr(self, 'pgm_laserpower', 100.0)
                    if pwr is None: pwr = 100.0
                    freq = getattr(self, 'pgm_laserfreq', 30.0)
                    if freq is None: freq = 30.0
                    
                    try:
                        if float(float(pwr)) <= 0:
                            if hasattr(self.galvo_controller.connection, 'laser_off'):
                                self.galvo_controller.connection.laser_off()
                            self.galvo_controller.connection.set_analog_do_bit(255.0, 0.0, 50.0, 2)
                        else:
                            mapped_power = (float(float(pwr)) / 100.0) * 255.0
                            self.galvo_controller.connection.set_analog_do_bit(255.0, mapped_power, 50.0, 2)
                        self.galvo_controller.connection.set_analog_do_bit(100.0, 50.0, self.galvo_controller.connection.clamp_laser_freq(float(freq)) / 4.0 if hasattr(self.galvo_controller.connection, 'clamp_laser_freq') else float(freq) / 4.0, 3)
                        self.util.debugPrint(f"Applied Galvo Power: {pwr}% | Freq: {freq}kHz via initPrintRun")
                    except Exception as e:
                        self.util.debugPrint(f"Failed to apply Galvo power/freq: {e}")
                        
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
#         self.wh.invokeMethod(self.left_menu_widgets.camerajog, "enable")
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
        from PySide6.QtGui import QDoubleValidator, QIntValidator

        self.cal_state_idx = 0
        self.cal_default_w = 30.0
        self.cal_is_stopped = False
        self.cal_reddot_thread = None
        
        # Attach preview widget to visual orientation frame
        if hasattr(self.ui, 'visualorientFrame'):
            layout = self.ui.visualorientFrame.layout()
            if not layout:
                layout = QVBoxLayout(self.ui.visualorientFrame)
                layout.setContentsMargins(0, 0, 0, 0)
            self.cal_preview = GridPreviewWidget(self.ui.visualorientFrame)
            layout.addWidget(self.cal_preview)
            
        # Collect line edit inputs for the 9 points
        self.cal_inputs_x = []
        self.cal_inputs_y = []
        for i in range(1, 10):
            le_x = getattr(self.ui, f"x{i}mmLineEdit", None)
            le_y = getattr(self.ui, f"y{i}mmLineEdit", None)
            if le_x:
                le_x.setValidator(QDoubleValidator(-1000.0, 1000.0, 3, self))
                self.cal_inputs_x.append(le_x)
            if le_y:
                le_y.setValidator(QDoubleValidator(-1000.0, 1000.0, 3, self))
                self.cal_inputs_y.append(le_y)
            if le_x: le_x.textChanged.connect(self.update_cal_preview)
            if le_y: le_y.textChanged.connect(self.update_cal_preview)

        # Connect image cycling controls
        if hasattr(self.ui, 'changeimgPushButton'):
            self.ui.changeimgPushButton.clicked.connect(self.next_cal_state)
        if hasattr(self.ui, 'imgindLineEdit'):
            self.ui.imgindLineEdit.setText(f"{self.cal_state_idx + 1}")
            self.ui.imgindLineEdit.setReadOnly(True)

        # Target half-width input
        if hasattr(self.ui, 'targhalfwidLineEdit'):
            self.ui.targhalfwidLineEdit.setText(f"{self.cal_default_w:.2f}")
            self.ui.targhalfwidLineEdit.setValidator(QDoubleValidator(1.0, 500.0, 2, self))
            self.ui.targhalfwidLineEdit.textChanged.connect(self.on_cal_w_changed)

        # Reset to nominal button
        if hasattr(self.ui, 'resettonominalPushButton'):
            self.ui.resettonominalPushButton.clicked.connect(self.reset_cal_to_nominal)

        # Sliders: Power and Frequency
        if hasattr(self.ui, 'powerHorizontalSlider'):
            self.ui.powerHorizontalSlider.setRange(0, 100)
            self.ui.powerHorizontalSlider.setValue(100)
            if hasattr(self.ui, 'indexLabel_4'):
                self.ui.indexLabel_4.setText("100")
            self.ui.powerHorizontalSlider.valueChanged.connect(self.on_cal_power_changed)

        if hasattr(self.ui, 'freqHorizontalSlider'):
            self.ui.freqHorizontalSlider.setRange(20, 80)
            self.ui.freqHorizontalSlider.setValue(30)
            if hasattr(self.ui, 'indexLabel_6'):
                self.ui.indexLabel_6.setText("30")
            self.ui.freqHorizontalSlider.valueChanged.connect(self.on_cal_freq_changed)

        # Speeds
        if hasattr(self.ui, 'markspeedLineEdit'):
            if not self.ui.markspeedLineEdit.text():
                self.ui.markspeedLineEdit.setText("5000")
            self.ui.markspeedLineEdit.setValidator(QIntValidator(100, 200000, self))

        if hasattr(self.ui, 'jumpspeedLineEdit'):
            if not self.ui.jumpspeedLineEdit.text():
                self.ui.jumpspeedLineEdit.setText("15000")
            self.ui.jumpspeedLineEdit.setValidator(QIntValidator(100, 200000, self))

        # Action Buttons
        if hasattr(self.ui, 'reddotPushButton'):
            self.ui.reddotPushButton.clicked.connect(self.toggle_cal_reddot_framing)

        if hasattr(self.ui, 'markcalgridPushButton'):
            self.ui.markcalgridPushButton.clicked.connect(self.draw_cal_pattern)

        if hasattr(self.ui, 'stopPushButton'):
            self.ui.stopPushButton.clicked.connect(self.stop_cal_pattern)

        if hasattr(self.ui, 'calapplyPushButton'):
            self.ui.calapplyPushButton.clicked.connect(self.generate_calibration)

        if hasattr(self.ui, 'maindesignPushButton'):
            self.ui.maindesignPushButton.clicked.connect(self.apply_calibration_to_main_design)

        if hasattr(self.ui, 'markvershapePushButton'):
            self.ui.markvershapePushButton.clicked.connect(self.mark_verification_shape)

        if hasattr(self.ui, 'ezcadclosePushButton'):
            self.ui.ezcadclosePushButton.clicked.connect(self.close_calibration_studio)

        # Initialize nominal distances on startup
        self.reset_cal_to_nominal()
        self.set_cal_status("Status : Ready")

    def set_cal_status(self, text):
        if hasattr(self.ui, 'indexLabel_8'):
            self.ui.indexLabel_8.setText(text)

    def on_cal_power_changed(self, val):
        if hasattr(self.ui, 'indexLabel_4'):
            self.ui.indexLabel_4.setText(str(val))

    def on_cal_freq_changed(self, val):
        if hasattr(self.ui, 'indexLabel_6'):
            self.ui.indexLabel_6.setText(str(val))

    def on_cal_w_changed(self, text):
        try:
            val = float(text)
            if val > 0:
                self.cal_default_w = val
                self.reset_cal_to_nominal()
                if hasattr(self.ui, 'nominalfieldLabel'):
                    self.ui.nominalfieldLabel.setText(f'Nominal Field: {2*val:.2f} x {2*val:.2f} mm')
                # If red dot preview is running, update its bounding box dynamically
                if self.cal_reddot_thread and getattr(self.cal_reddot_thread, 'running', False):
                    scale = 533.89
                    hw = int(self.cal_default_w * scale)
                    c = 32767
                    self.cal_reddot_thread.update_bounds(c - hw, c + hw, c - hw, c + hw)
        except ValueError:
            pass

    def update_cal_preview(self):
        if not hasattr(self, 'cal_preview'): return
        
        from core.calibration_generator_ui import TRANSFORMS
        transform = TRANSFORMS[self.cal_state_idx]
        
        pts = [(0, 0)] * 9
        for i in range(9):
            x_text = self.cal_inputs_x[i].text().strip() if i < len(self.cal_inputs_x) else "0.0"
            y_text = self.cal_inputs_y[i].text().strip() if i < len(self.cal_inputs_y) else "0.0"
            
            try: x = float(x_text or 0.0)
            except ValueError: x = 0.0
            try: y = float(y_text or 0.0)
            except ValueError: y = 0.0
            
            # Undo the orientation transform for rendering since the renderer maps it back!
            pts[i] = (x, y)
            
        self.cal_preview.set_measured_points(self.cal_default_w, pts)
        
    def reset_cal_to_nominal(self):
        w = self.cal_default_w
        default_vals = [
            (-w, w), (0, w), (w, w),
            (-w, 0), (0, 0), (w, 0),
            (-w, -w), (0, -w), (w, -w)
        ]
        for i in range(9):
            if i < len(self.cal_inputs_x):
                if default_vals[i][0] != 0:
                    self.cal_inputs_x[i].setText(f"{default_vals[i][0]:.3f}")
                    self.cal_inputs_x[i].setEnabled(True)
                else:
                    self.cal_inputs_x[i].setText("0.000")
                    self.cal_inputs_x[i].setEnabled(False)

            if i < len(self.cal_inputs_y):
                if default_vals[i][1] != 0:
                    self.cal_inputs_y[i].setText(f"{default_vals[i][1]:.3f}")
                    self.cal_inputs_y[i].setEnabled(True)
                else:
                    self.cal_inputs_y[i].setText("0.000")
                    self.cal_inputs_y[i].setEnabled(False)

    def next_cal_state(self):
        self.cal_state_idx = (self.cal_state_idx + 1) % 8
        if hasattr(self.ui, 'imgindLineEdit'):
            self.ui.imgindLineEdit.setText(f"{self.cal_state_idx + 1}")
        if hasattr(self, 'cal_preview'):
            self.cal_preview.set_state(self.cal_state_idx)

    def toggle_cal_reddot_framing(self):
        if self.cal_reddot_thread and getattr(self.cal_reddot_thread, 'running', False):
            self.stop_cal_reddot()
            return

        if not self.galvo_controller or not self.galvo_controller.is_connected:
            QMessageBox.warning(self, "Error", "Galvo controller is not connected.")
            return

        scale = 533.89
        hw = int(self.cal_default_w * scale)
        c = 32767
        min_x = c - hw
        max_x = c + hw
        min_y = c - hw
        max_y = c + hw

        from galvo_threads import PreviewThread
        self.cal_reddot_thread = PreviewThread(self.galvo_controller, min_x, max_x, min_y, max_y)
        self.cal_reddot_thread.finished_signal.connect(self.on_cal_reddot_finished)
        self.cal_reddot_thread.start()

        if hasattr(self.ui, 'reddotPushButton'):
            self.ui.reddotPushButton.setText("Stop Red Dot")
            self.ui.reddotPushButton.setStyleSheet(
                "color: rgb(255, 255, 255); background-color: rgb(220, 38, 38); "
                "border-style: outset; border-radius: 15px; border-width: 2px; padding: 6px;"
            )
        self.set_cal_status("Status : Red Dot Framing Active")

    def stop_cal_reddot(self):
        if self.cal_reddot_thread:
            self.cal_reddot_thread.running = False
            self.cal_reddot_thread.wait()
            self.cal_reddot_thread = None

        if self.galvo_controller and self.galvo_controller.connection:
            if hasattr(self.galvo_controller.connection, 'reddot_off'):
                self.galvo_controller.connection.reddot_off()

        if hasattr(self.ui, 'reddotPushButton'):
            self.ui.reddotPushButton.setText("Red Dot Frame")
            self.ui.reddotPushButton.setStyleSheet(
                "color: rgb(255, 255, 255); background-color: rgb(16, 42, 131); "
                "border-style: outset; border-radius: 15px; border-width: 2px; padding: 6px;"
            )
        self.set_cal_status("Status : Ready")

    def on_cal_reddot_finished(self, success):
        self.stop_cal_reddot()

    def draw_cal_pattern(self):
        from PySide6.QtWidgets import QMessageBox, QApplication
        self.cal_is_stopped = False

        if not self.galvo_controller or not self.galvo_controller.is_connected:
            QMessageBox.warning(self, "Error", "Galvo controller is not connected.")
            return

        # Stop red dot if running before marking
        self.stop_cal_reddot()

        scale = 533.89
        hw = int(self.cal_default_w * scale)
        c = 32767

        min_x = c - hw
        max_x = c + hw
        min_y = c - hw
        max_y = c + hw

        conn = self.galvo_controller.connection

        try:
            pwr = float(self.ui.galvolaserpowerHorizontalSlider_2.value()) if hasattr(self.ui, 'galvolaserpowerHorizontalSlider_2') else 100.0
            freq = float(self.ui.galvolaserfreqHorizontalSlider.value()) if hasattr(self.ui, 'galvolaserfreqHorizontalSlider') else 30.0
            
            field_size = self.galvo_config.field_size if hasattr(self, 'galvo_config') and self.galvo_config else 110.0
            galvo_units_per_mm = 65535.0 / field_size

            # Force slow printing for calibration to ensure clear, deep marks
            raw_mark = 20.0  # 20 mm/s is extremely slow and guarantees a perfect dark burn
            raw_jump = 200.0
            
            mark_speed = int(raw_mark * galvo_units_per_mm)
            jump_speed = int(raw_jump * galvo_units_per_mm)
        except ValueError:
            QMessageBox.warning(self, "Error", "Invalid laser parameters. Using defaults.")
            pwr, freq, mark_speed, jump_speed = 100.0, 30.0, int(1000 * (65535.0/110.0)), int(2000 * (65535.0/110.0))

        self.galvo_controller.live_power = pwr
        self.galvo_controller.live_freq = freq

        queue = []
        
        def jump(x, y): 
            # execute_queue does cmd_x = cmd['y'] and cmd_y = cmd['x'].
            # Then galvo_move_xy(cmd_x, cmd_y) physically maps its first argument to Physical Y, and second to Physical X.
            # So Physical Y = cmd_x = cmd['y']. Physical X = cmd_y = cmd['x'].
            # To get Physical X = x and Physical Y = y, we simply set cmd['x'] = x and cmd['y'] = y.
            queue.append({'type': 'jump', 'x': int(x), 'y': int(y), 'speed': jump_speed})
            queue.append({'type': 'delay', 'ms': 5})
            
        def mark(x, y): 
            queue.append({'type': 'mark', 'x': int(x), 'y': int(y), 'speed': mark_speed})
            queue.append({'type': 'flush'}) # Push command directly to hardware to prevent motion timeouts
            queue.append({'type': 'delay', 'ms': 2})
        
        def draw_digit(d, x0, y0):
            # x0, y0 is top-left of the digit. +Y is UP.
            # Make digits large and readable (2.5mm width, 5.0mm height)
            dw = int(2.5 * galvo_units_per_mm)
            dh = int(5.0 * galvo_units_per_mm)
            x1 = x0 + dw
            y1 = int(y0 - dh / 2.0)
            y2 = y0 - dh
            if d == 1: jump(x1, y0); mark(x1, y2)
            elif d == 2: jump(x0, y0); mark(x1, y0); mark(x1, y1); mark(x0, y1); mark(x0, y2); mark(x1, y2)
            elif d == 3: jump(x0, y0); mark(x1, y0); mark(x1, y1); mark(x0, y1); jump(x1, y1); mark(x1, y2); mark(x0, y2)
            elif d == 4: jump(x0, y0); mark(x0, y1); mark(x1, y1); jump(x1, y0); mark(x1, y2)
            elif d == 5: jump(x1, y0); mark(x0, y0); mark(x0, y1); mark(x1, y1); mark(x1, y2); mark(x0, y2)
            elif d == 6: jump(x1, y0); mark(x0, y0); mark(x0, y2); mark(x1, y2); mark(x1, y1); mark(x0, y1)
            elif d == 7: jump(x0, y0); mark(x1, y0); mark(x1, y2)
            elif d == 8: jump(x0, y0); mark(x1, y0); mark(x1, y2); mark(x0, y2); mark(x0, y0); jump(x0, y1); mark(x1, y1)
            elif d == 9: jump(x1, y1); mark(x0, y1); mark(x0, y0); mark(x1, y0); mark(x1, y2); mark(x0, y2)

        try:
            # Procedurally generate the exact calibration grid to match the 50x50 target 
            W_mm = self.cal_default_w  # Target Half-Width from UI (e.g. 25.0)
            # To get a 50x50 square, W_mm is 25.0. 
            hw = int(W_mm * galvo_units_per_mm)
            
            min_x, max_x = c - hw, c + hw
            min_y, max_y = c - hw, c + hw
            
            # Outer square
            jump(min_x, max_y)
            mark(max_x, max_y)
            mark(max_x, min_y)
            mark(min_x, min_y)
            mark(min_x, max_y)
            
            # Extended crosshairs (10% extension past the square)
            ext = int(hw * 0.1)
            
            # Vertical line
            jump(c, max_y + ext)
            mark(c, min_y - ext)
            
            # Horizontal line
            jump(min_x - ext, c)
            mark(max_x + ext, c)
            
            # Small square inside Top-Left (Point 1)
            ms = int(2.0 * galvo_units_per_mm)
            o = int(ms / 1.5)
            sq_x = min_x + o
            sq_y = max_y - o
            jump(sq_x, sq_y)
            mark(sq_x + ms, sq_y)
            mark(sq_x + ms, sq_y - ms)
            mark(sq_x, sq_y - ms)
            mark(sq_x, sq_y)
            
            # Small diamond inside Bottom-Right (Point 9)
            d_cx = max_x - o - int(ms/2)
            d_cy = min_y + o + int(ms/2)
            d_r = int(ms/2)
            jump(d_cx, d_cy + d_r)
            mark(d_cx + d_r, d_cy)
            mark(d_cx, d_cy - d_r)
            mark(d_cx - d_r, d_cy)
            mark(d_cx, d_cy + d_r)
            
            # Tick mark just to the right of the central vertical line, intersecting the horizontal axis
            tick_x = c + int(hw * 0.15)
            jump(tick_x, c + int(hw * 0.15))
            mark(tick_x, c - int(hw * 0.15))
            
            # Draw digital numbers 1-9
            pd = int(2.0 * galvo_units_per_mm)
            dh_half = int(2.5 * galvo_units_per_mm) # half of 5.0 height
            dw = int(2.5 * galvo_units_per_mm)
            dh = int(5.0 * galvo_units_per_mm)
            
            # '1' at the top-left outer corner. (above and to the left)
            draw_digit(1, min_x - dw - pd, max_y + dh + pd)
            
            # '2' directly above the top center intersection.
            draw_digit(2, c - int(dw/2), max_y + dh + pd)
            
            # '3' at the top-right outer corner.
            draw_digit(3, max_x + pd, max_y + dh + pd)
            
            # '4' to the left of the center-left intersection.
            draw_digit(4, min_x - dw - pd, c + dh_half)
            
            # '5' immediately to the top-right of the central crosshair intersection.
            draw_digit(5, c + pd, c + dh + pd)
            
            # '6' to the right of the center-right intersection.
            draw_digit(6, max_x + pd, c + dh_half)
            
            # '7' directly below the bottom-left outer corner.
            draw_digit(7, min_x - dw - pd, min_y - pd)
            
            # '8' directly below the bottom center intersection.
            draw_digit(8, c - int(dw/2), min_y - pd)
            
            # '9' directly below the bottom-right outer corner.
            draw_digit(9, max_x + pd, min_y - pd)

            if hasattr(self.ui, 'markcalgridPushButton'):
                self.ui.markcalgridPushButton.setEnabled(False)
            self.set_cal_status("Status : Marking Calibration Grid...")

            if hasattr(conn, 'enable_calibration'):
                original_cal_state = conn.enable_calibration
                conn.enable_calibration = False

            success = self.galvo_controller.execute_queue(
                queue,
                loop_count=1,
                abort_check=lambda: self.cal_is_stopped,
                progress_callback=self._throttled_process_events
            )

            if hasattr(conn, 'enable_calibration'):
                conn.enable_calibration = original_cal_state

            if self.cal_is_stopped or not success:
                raise InterruptedError("Drawing stopped by user or failed")

            conn.laser_off()
            conn.galvo_move_xy(c, c)

            self.set_cal_status("Status : Grid Marked - Measure Points")
            QMessageBox.information(
                self, "Success",
                "Calibration grid marked!\n\nPlease measure the distance of each of the 9 points "
                "from the center crosshair using calipers, and enter them in the table."
            )
        except InterruptedError:
            self.set_cal_status("Status : Stopped")
        except Exception as e:
            self.set_cal_status("Status : Error marking grid")
            QMessageBox.critical(self, "Error", f"Failed to mark pattern: {e}")
        finally:
            if conn:
                conn.laser_off()
            if hasattr(self.ui, 'markcalgridPushButton'):
                self.ui.markcalgridPushButton.setEnabled(True)

    def stop_cal_pattern(self):
        self.cal_is_stopped = True
        self.stop_cal_reddot()

        if self.galvo_controller and self.galvo_controller.connection:
            conn = self.galvo_controller.connection
            if hasattr(conn, 'laser_off'):
                conn.laser_off()
            if hasattr(conn, 'set_analog_do_bit'):
                conn.set_analog_do_bit(255.0, 0.0, 50.0, 2)
            if hasattr(conn, 'reddot_off'):
                conn.reddot_off()
            if hasattr(conn, 'stop'):
                conn.stop()

        if hasattr(self.ui, 'markcalgridPushButton'):
            self.ui.markcalgridPushButton.setEnabled(True)
        if hasattr(self.ui, 'markvershapePushButton'):
            self.ui.markvershapePushButton.setEnabled(True)
            
        self.set_cal_status("Status : Ready")

    def generate_calibration(self):
        from core.calibration_generator_ui import TRANSFORMS
        from core.calibration_generator import generate_cor_file

        self.set_cal_status("Status : Calculating Calibration...")

        ui_measurements = []
        for i in range(9):
            try:
                x_text = self.cal_inputs_x[i].text().strip() if i < len(self.cal_inputs_x) else "0.0"
                y_text = self.cal_inputs_y[i].text().strip() if i < len(self.cal_inputs_y) else "0.0"
                x = float(x_text or 0.0)
                y = float(y_text or 0.0)
                ui_measurements.append((x, y))
            except ValueError:
                self.set_cal_status("Status : Input Error")
                QMessageBox.warning(self, "Error", f"Invalid numeric input at Point {i+1}.")
                return

        # The hardware natively swaps X and Y. Our jump/mark routines cancel this by sending x: x, y: y
        # which results in cmd_x = y, cmd_y = x inside execute_queue. 
        # When calibration is applied, it takes cmd_x and cmd_y as input.
        # This means the .cor file grid is queried at (y, x).
        # To make the .cor file corrections map properly to the logical (x, y) space, we must build it 
        # using a Y=X reflection (TRANSFORMS[7]) and swap the X and Y error components.
        transform_swap = [8, 5, 2, 7, 4, 1, 6, 3, 0]
        galvo_measurements = [None] * 9

        for galvo_idx in range(9):
            ui_idx = transform_swap[galvo_idx]
            raw_x, raw_y = ui_measurements[ui_idx]

            # Since the .cor file's X output is added to cmd_x (Physical Y), it needs the User's Y measurement.
            # Since the .cor file's Y output is added to cmd_y (Physical X), it needs the User's X measurement.
            galvo_measurements[galvo_idx] = (raw_y, raw_x)

        try:
            field_size = self.galvo_config.field_size if hasattr(self, 'galvo_config') and self.galvo_config else 110.0
            scale = 65535.0 / field_size
        except:
            scale = 595.772

        W = self.cal_default_w
        nominals = [
            (-W, W), (0, W), (W, W),
            (-W, 0), (0, 0), (W, 0),
            (-W, -W), (0, -W), (W, -W)
        ]
        
        import math
        err_sum = sum(math.hypot(galvo_measurements[i][0] - nominals[i][0], galvo_measurements[i][1] - nominals[i][1]) for i in range(9))
        avg_err = err_sum / 9.0

        try:
            generate_cor_file("staged_calibration.cor", scale, self.cal_default_w, galvo_measurements)

            # Load into a staged calibration object for verification, keeping active machine calibration intact
            loaded_ok = False
            from core.calibration import GalvoCalibration
            self.stagedCalibrationTransform = GalvoCalibration("staged_calibration.cor")
            if self.stagedCalibrationTransform.is_valid:
                loaded_ok = True

            self.set_cal_status(f"Status : Calibration Computed (Ready to Verify)")
            msg = "staged_calibration.cor created successfully!"
            if loaded_ok:
                msg += "\n\nThe new calibration has been temporarily staged.\n" \
                       "You can now click 'Mark Verification Shape' to verify the result."
            else:
                msg += "\n\n(Calibration file saved but failed to load.)"
            QMessageBox.information(self, "Calibration Generated", msg)

        except Exception as e:
            self.set_cal_status("Status : Error generating calibration")
            QMessageBox.critical(self, "Error", f"Failed to generate calibration: {e}")

    def apply_calibration_to_main_design(self):
        import shutil
        from PySide6.QtWidgets import QMessageBox, QFileDialog
        
        if hasattr(self, 'stagedCalibrationTransform') and self.stagedCalibrationTransform and self.stagedCalibrationTransform.is_valid:
            try:
                # Prompt user for save location
                target_cor, _ = QFileDialog.getSaveFileName(self, "Save Calibration File", "new_calibration.cor", "Cor Files (*.cor)")
                if not target_cor:
                    return # User cancelled

                # Copy the staged calibration to the user's chosen target file
                shutil.copyfile("staged_calibration.cor", target_cor)
                
                # Also overwrite the permanent application default so it persists across restarts
                import os
                root_cor_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "newest100mm.cor")
                shutil.copyfile("staged_calibration.cor", root_cor_path)
                
                # Load it into the active galvo controller
                if hasattr(self.galvo_controller, 'connection') and hasattr(self.galvo_controller.connection, 'calibration'):
                    self.galvo_controller.connection.calibration.load_calibration(target_cor)
                    self.galvo_controller.connection.enable_calibration = True
                    
                    if self.galvo_controller.connection.calibration.is_valid:
                        self.set_cal_status("Status : Applied to Main Design")
                        
                        # Automatically mark verification shape
                        self.mark_verification_shape()
                        
                        QMessageBox.information(self, "Success", "Calibration successfully applied and loaded into the hardware.")
                    else:
                        QMessageBox.warning(self, "Error", "Failed to load the staged calibration into the hardware.")
                else:
                    QMessageBox.warning(self, "Error", "Hardware connection or calibration module not found.")
            except Exception as e:
                self.set_cal_status("Status : Error applying to main design")
                QMessageBox.critical(self, "Error", f"Failed to apply calibration: {e}")
        else:
            QMessageBox.warning(self, "Warning", "No valid calibration staged. Please 'Calculate & Apply Calibration' first.")

    def _throttled_process_events(self, idx, tot, x, y, ctype):
        import time
        from PySide6.QtWidgets import QApplication
        if not hasattr(self, '_last_cal_ui_update'):
            self._last_cal_ui_update = 0.0
        if time.time() - self._last_cal_ui_update > 0.05:
            QApplication.processEvents()
            self._last_cal_ui_update = time.time()

    def mark_verification_shape(self):
        from PySide6.QtWidgets import QMessageBox, QApplication
        self.cal_is_stopped = False

        if not self.galvo_controller or not self.galvo_controller.is_connected:
            QMessageBox.warning(self, "Error", "Galvo controller is not connected.")
            return

        self.stop_cal_reddot()

        try:
            field_size = self.galvo_config.field_size if hasattr(self, 'galvo_config') and self.galvo_config else 110.0
            galvo_units_per_mm = 65535.0 / field_size
        except:
            galvo_units_per_mm = 595.77

        W_mm = self.cal_default_w
        hw = int(W_mm * galvo_units_per_mm)
        c = 32767

        min_x = c - hw
        max_x = c + hw
        min_y = c - hw
        max_y = c + hw
        
        cross_hw = int(hw * 0.1)

        conn = self.galvo_controller.connection

        if not hasattr(self, 'stagedCalibrationTransform') or not self.stagedCalibrationTransform.is_valid:
            QMessageBox.warning(self, "Error", "Please compute calibration values before marking verification shape.")
            return

        try:
            pwr = float(self.ui.galvolaserpowerHorizontalSlider_2.value()) if hasattr(self.ui, 'galvolaserpowerHorizontalSlider_2') else 100.0
            freq = float(self.ui.galvolaserfreqHorizontalSlider.value()) if hasattr(self.ui, 'galvolaserfreqHorizontalSlider') else 30.0
            
            field_size = self.galvo_config.field_size if hasattr(self, 'galvo_config') and self.galvo_config else 110.0
            galvo_units_per_mm = 65535.0 / field_size

            # Force slow printing for calibration to ensure clear, deep marks
            raw_mark = 20.0  # 20 mm/s is extremely slow and guarantees a perfect dark burn
            raw_jump = 200.0
            
            mark_speed = int(raw_mark * galvo_units_per_mm)
            jump_speed = int(raw_jump * galvo_units_per_mm)
        except ValueError:
            QMessageBox.warning(self, "Error", "Invalid laser parameters. Using defaults.")
            pwr, freq, mark_speed, jump_speed = 100.0, 30.0, 5000, 15000

        self.galvo_controller.live_power = pwr
        self.galvo_controller.live_freq = freq

        queue = []
        
        # Apply staged calibration directly before dispatching to galvo hardware
        def jump(x, y): 
            cx, cy = self.stagedCalibrationTransform.apply(float(x), float(y))
            # Same fix: appending {x: x, y: y} maps to Physical X = x, Physical Y = y
            queue.append({'type': 'jump', 'x': int(cx), 'y': int(cy), 'speed': jump_speed})
        def mark(x, y): 
            cx, cy = self.stagedCalibrationTransform.apply(float(x), float(y))
            queue.append({'type': 'mark', 'x': int(cx), 'y': int(cy), 'speed': mark_speed})
            queue.append({'type': 'flush'})
            queue.append({'type': 'delay', 'ms': 2})

        import math
        try:
            # 1. Outer Square (50x50 mm, or whatever Target Half-Width * 2 is)
            jump(min_x, max_y)
            mark(max_x, max_y)
            mark(max_x, min_y)
            mark(min_x, min_y)
            mark(min_x, max_y)

            # 2. Vertical crosshair (-5 to +5 mm)
            jump(c, c + cross_hw)
            mark(c, c - cross_hw)

            # 3. Horizontal crosshair (-5 to +5 mm)
            jump(c - cross_hw, c)
            mark(c + cross_hw, c)

            if hasattr(self.ui, 'markvershapePushButton'):
                self.ui.markvershapePushButton.setEnabled(False)
            self.set_cal_status("Status : Marking Verification Shape...")

            if hasattr(conn, 'enable_calibration'):
                original_cal_state = conn.enable_calibration
                conn.enable_calibration = False # We already applied staged calibration

            success = self.galvo_controller.execute_queue(
                queue,
                loop_count=1,
                abort_check=lambda: self.cal_is_stopped,
                progress_callback=self._throttled_process_events
            )

            if hasattr(conn, 'enable_calibration'):
                conn.enable_calibration = original_cal_state

            if self.cal_is_stopped or not success:
                raise InterruptedError("Drawing stopped by user or failed")

            conn.laser_off()
            conn.galvo_move_xy(c, c)

            self.set_cal_status("Status : Verification Marked")
            QMessageBox.information(
                self, "Success",
                "Verification shape marked!\n\nPlease check the physical shape for orthogonal corners and precise dimensions."
            )
        except InterruptedError:
            self.set_cal_status("Status : Stopped")
        except Exception as e:
            self.set_cal_status("Status : Error marking verification shape")
            print(f"Error marking verification shape: {e}")

    def dummy_cal_action(self):
        """Backwards compatibility alias for mark_verification_shape."""
        self.mark_verification_shape()

    def close_calibration_studio(self):
        self.stop_cal_pattern()
        target_page = "joggalvo" if str(self.galvo_mode).upper() == "ON" else "jog"
        self.showMainPages(target_page)

if __name__ == '__main__':
    
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
