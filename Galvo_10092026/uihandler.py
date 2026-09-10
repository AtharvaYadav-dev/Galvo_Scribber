from dataclasses import dataclass
from PySide6.QtCore import QObject, QEvent
from PySide6.QtWidgets import *
from Custom_Widgets.Widgets import *

class DictAsClass():
    def __init__(self, dictionary):
        self._data = dictionary
    
    def __getattr__(self, key):
        if key in self._data:
            return self._data[key]
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{key}'")
    
    def get(self, key, default=None):
        return self._data.get(key, default)

@dataclass
class Axis:
    name: str
    pos: float
    min: float
    max: float
    center: float
    feed: float
    stepsmm: float
    motion: str
    fcmd: str
    home: str

        
class AxisHandler():
    def __init__(self):
        self.axis_dict = {}
        
    def addAxis(self, name, pos=None, min=None, max=None, center=None, feed=None, stepsmm=None, motion=None, fcmd=None, home=None):
        axis = Axis(name, pos, min, max, center, feed, stepsmm, motion, fcmd, home=f"{home} {name}")
        self.axis_dict[name] = axis
        
    def getAxis(self, name):
        if name in self.axis_dict:
            return self.axis_dict[name]
        
    def setValue(self, name, key, value):
        axis = self.getAxis(name)
        
        if axis is not None and key is not None and value is not None:
            setattr(axis, key, value)

    def pos(self, name, pos):
        self.setValue(name, "pos", pos)
        
    def min(self, name, min):
        self.setValue(name, "min", min)
        
    def max(self, name, max):
        self.setValue(name, "max", max)
        
    def center(self, name, center):
        self.setValue(name, "center", center)
        
    def feed(self, name, feed):
        self.setValue(name, "feed", feed)
        
    def stepsmm(self, name, stepsmm):
        self.setValue(name, "stepsmm", stepsmm)
        
    def home(self, name, home):
        self.setValue(name, "home", f"{home} {name}")
        
    def fcmd(self, name, fcmd):
        self.setValue(name, "fcmd", fcmd)
        
    def motion(self, name, motion):
        self.setValue(name, "motion", motion)
        
    def move(self, name, travel=None, dir=None, feed=None):
        axis = self.getAxis(name)        
        motion = getattr(axis, "motion")
        
        dir_dict = {"plus" : "",
                    "minus" : "-",
                    "center" : ""
                    }
        
        if travel is not None:
            disp = travel
        
        else:
            disp = 0
            
        if feed is not None:
            fval = f"{getattr(axis, "fcmd")}{feed}"
        
        else:
            fval = f"{getattr(axis, "fcmd")}{getattr(axis, "feed")}"
            
        if dir is not None:
            if dir == "center":
                disp = getattr(axis, "center")
                
            dval = dir_dict.get(dir)
            
        else:
            dval = ""
            
        return f"{motion} {name}{dval}{disp} {fval}"


@dataclass
class Laser:
    name: str
    focus: float
    xpos: float
    ypos: float
    cmd: dict


class LaserHandler():
    def __init__(self):
        self.laser_dict = {}

    def getHandlerData(self):
        return self.laser_dict
        
    def addLaser(self, name, focus, xpos, ypos, cmd):
        laser = Laser(name, focus, xpos, ypos, cmd)
        self.laser_dict[name] = laser

    def getKeys(self):
        return self.laser_dict.keys()
        
    def getLaser(self, name):
        if name in self.laser_dict:
            return self.laser_dict[name]
        
    def setValue(self, name, key, value):
        laser = self.getLaser(name)
        
        if laser and key and value is not None:
            setattr(laser, key, value)
        
    def focus(self, name, focus):
        self.setValue(name, "focus", focus)
            
    def xpos(self, name, xpos):
        self.setValue(name, "xpos", xpos)
    
    def ypos(self, name, ypos):
        self.setValue(name, "ypos", ypos)
    
    def cmd(self, name, cmd):
        self.setValue(name, "cmd", cmd)


@dataclass
class Nozzle:
    name: str
    zpos: float
    xpos: float
    ypos: float
    cmd: dict


class NozzleHandler():
    def __init__(self):
        self.nozzle_dict = {}

    def getHandlerData(self):
        return self.nozzle_dict
        
    def addNozzle(self, name, zpos, xpos, ypos, cmd):
        nozzle = Nozzle(name, zpos, xpos, ypos, cmd)
        self.nozzle_dict[name] = nozzle

    def getKeys(self):
        return self.nozzle_dict.keys()
        
    def getNozzle(self, name):
        return self.nozzle_dict.get(name, None)
        
    def setValue(self, name, key, value):
        nozzle = self.getNozzle(name)
        if nozzle and key and value is not None:
            setattr(nozzle, key, value)
        
    # --- Setters ---
    def zpos(self, name, zpos):
        self.setValue(name, "zpos", zpos)
            
    def xpos(self, name, xpos):
        self.setValue(name, "xpos", xpos)
    
    def ypos(self, name, ypos):
        self.setValue(name, "ypos", ypos)
    
    def cmd(self, name, cmd):
        self.setValue(name, "cmd", cmd)

    # --- New getters ---
    def getZpos(self, name):
        nozzle = self.getNozzle(name)
        return getattr(nozzle, "zpos", 0.0) if nozzle else 0.0

    def getXpos(self, name):
        nozzle = self.getNozzle(name)
        return getattr(nozzle, "xpos", 0.0) if nozzle else 0.0

    def getYpos(self, name):
        nozzle = self.getNozzle(name)
        return getattr(nozzle, "ypos", 0.0) if nozzle else 0.0


            
class WidgetManger():
    def __init__(self):
        self.widget_methods = {"QLineEdit" : {"get" : lambda w : w.text(),
                                              "set" : lambda w, arg : w.setText(arg),
                                              "enable" : lambda w, arg : w.setEnabled(arg),
                                              "clear" : lambda w : w.clear(),
                                              "show" : lambda w : w.setVisible(True),
                                              "hide" : lambda w : w.setVisible(False)
                                              },
                               
                               "QTextEdit" : {"get" : lambda w : w.text(),
                                              "set" : lambda w, arg : w.setText(arg),
                                              "enable" : lambda w, arg : w.setEnabled(arg),
                                              "clear" : lambda w : w.clear(),
                                              "add" : lambda w, arg : w.append(str(arg)),
                                              "show" : lambda w : w.setVisible(True),
                                              "hide" : lambda w : w.setVisible(False)
                                              },
                               
                               "QLabel" : {"get" : lambda w : w.text(),
                                           "set" : lambda w, arg : w.setText(arg),
                                           "enable" : lambda w, arg : w.setEnabled(arg),
                                           "clear" : lambda w : w.clear(),
                                           "show" : lambda w : w.setVisible(True),
                                           "hide" : lambda w : w.setVisible(False)
                                           },
                               
                               "QComboBox" : {"get" : lambda w : w.currentText(),
                                              "set" : lambda w, arg : w.setCurrentText(arg),
                                              "enable" : lambda w, arg : w.setEnabled(arg),
                                              "clear" : lambda w : w.clear(),
                                              "add" : lambda w, args : w.addItems(args),
                                              "show" : lambda w : w.setVisible(True),
                                              "hide" : lambda w : w.setVisible(False)
                                              },
                               
                               "QPushButton" : {"get" : lambda w : w.text(),
                                                "set" : lambda w, arg : w.setText(arg),
                                                "enable" : lambda w, arg : w.setEnabled(arg),
                                                "clear" : lambda w : w.setText(""),
                                                "show" : lambda w : w.setVisible(True),
                                                "hide" : lambda w : w.setVisible(False)
                                                },
                               
                               "QLCDNumber" : {"set" : lambda w, arg: w.display(arg),
                                               "get" : lambda w: w.value(),
                                               "show" : lambda w : w.setVisible(True),
                                               "hide" : lambda w : w.setVisible(False)
                                               },
                               
                               "QProgressBar" : {"get" : lambda w : w.value(),
                                                 "set" : lambda w, arg : w.setValue(arg),
                                                 "enable" : lambda w, arg : w.setEnabled(arg),
                                                 "clear" : lambda w : w.setValue(0),
                                                 "min" : lambda w, min : w.setMinimum(min),
                                                 "max" : lambda w, max : w.setMaximum(max),
                                                 "show" : lambda w : w.setVisible(True),
                                                 "hide" : lambda w : w.setVisible(False)
                                                 }
                               }
        
    def operate(self, widget, operation, value=None):
        widget_type = type(widget).__name__
        
        if widget_type not in self.widget_methods:
            return False
        
        method_dict = self.widget_methods[widget_type]
        
        if operation not in method_dict:
            return False
        
        method = method_dict[operation]
        
        if method is None:
            return False
        
        if operation == "get":
            return method(widget)
        
        if operation in ["set", "enable", "add", "min", "max", "clear", "show", "hide"]:
            if value is not None:
                method(widget, value)
            
            else:
                method(widget)
                
                
                

class WidgetCallback(QObject):
    # helper class which adapts Qt signals to call functions with (widget, *args)

    def __init__(self, widget, func):
        super().__init__(widget)
        self.widget = widget
        self.func = func

    def __call__(self, *args):
        return self.func(self.widget, *args)
    
            
class WidgetHandler():
    def __init__(self):
        self.mro_cache = {}
        self.methods = {}
        self._buildMethods()
         
    @staticmethod
    def _type(w):
        return type(w).__name__
    
    @staticmethod
    def _mro(w): 
        return [cls.__name__ for cls in type(w).mro()]
            
    @staticmethod
    def _name(w):
        return w.objectName()
        
    def _buildMethods(self):
        # QLineEdit widgets method names
        self.methods["QLineEdit"] = {}
        self.methods["QLineEdit"]["get"] = "text"
        self.methods["QLineEdit"]["set"] = "setText"
        self.methods["QLineEdit"]["clear"] = "clear"
        self.methods["QLineEdit"]["show"] = ("setVisible", True)
        self.methods["QLineEdit"]["hide"] = ("setVisible", False)
        self.methods["QLineEdit"]["enable"] = ("setEnabled", True)
        self.methods["QLineEdit"]["disable"] = ("setEnabled", False)
        self.methods["QLineEdit"]["tooltip"] = "setToolTip"
        
        # QTextEdit widgets method names
        self.methods["QTextEdit"] = {}
        self.methods["QTextEdit"]["get"] = "text"
        self.methods["QTextEdit"]["set"] = "setText"
        self.methods["QTextEdit"]["clear"] = "clear"
        self.methods["QTextEdit"]["add"] = "append"

        self.methods["QTextEdit"]["show"] = ("setVisible", True)
        self.methods["QTextEdit"]["hide"] = ("setVisible", False)
        self.methods["QTextEdit"]["enable"] = ("setEnabled", True)
        self.methods["QTextEdit"]["disable"] = ("setEnabled", False)
        self.methods["QTextEdit"]["tooltip"] = "setToolTip"
        
        # QLabel widgets method names
        self.methods["QLabel"] = {}
        self.methods["QLabel"]["get"] = "text"
        self.methods["QLabel"]["set"] = "setText"
        self.methods["QLabel"]["clear"] = "clear"
        self.methods["QLabel"]["show"] = ("setVisible", True)
        self.methods["QLabel"]["hide"] = ("setVisible", False)
        self.methods["QLabel"]["enable"] = ("setEnabled", True)
        self.methods["QLabel"]["disable"] = ("setEnabled", False)
        self.methods["QLabel"]["tooltip"] = "setToolTip"
        
        # QPushButton widgets method names
        self.methods["QPushButton"] = {}
        self.methods["QPushButton"]["get"] = "text"
        self.methods["QPushButton"]["set"] = "setText"
        self.methods["QPushButton"]["clear"] = ("setText", "")
        self.methods["QPushButton"]["show"] = ("setVisible", True)
        self.methods["QPushButton"]["hide"] = ("setVisible", False)
        self.methods["QPushButton"]["enable"] = ("setEnabled", True)
        self.methods["QPushButton"]["disable"] = ("setEnabled", False)
        self.methods["QPushButton"]["tooltip"] = "setToolTip"
        
        # QComboBox widgets method names
        self.methods["QComboBox"] = {}
        self.methods["QComboBox"]["get"] = "currentText"
        self.methods["QComboBox"]["set"] = "setCurrentText"
        self.methods["QComboBox"]["clear"] = "clear"
        self.methods["QComboBox"]["add"] = "addItems"
        self.methods["QComboBox"]["show"] = ("setVisible", True)
        self.methods["QComboBox"]["hide"] = ("setVisible", False)
        self.methods["QComboBox"]["enable"] = ("setEnabled", True)
        self.methods["QComboBox"]["disable"] = ("setEnabled", False)
        self.methods["QComboBox"]["tooltip"] = "setToolTip"
        
        # QLCDNumber widgets method names
        self.methods["QLCDNumber"] = {}
        self.methods["QLCDNumber"]["get"] = "value"
        self.methods["QLCDNumber"]["set"] = "display"
        self.methods["QLCDNumber"]["show"] = ("setVisible", True)
        self.methods["QLCDNumber"]["hide"] = ("setVisible", False)
        self.methods["QLCDNumber"]["enable"] = ("setEnabled", True)
        self.methods["QLCDNumber"]["disable"] = ("setEnabled", False)
        self.methods["QLCDNumber"]["tooltip"] = "setToolTip"
        
        # QProgressBar widgets method names
        self.methods["QProgressBar"] = {}
        self.methods["QProgressBar"]["get"] = "value"
        self.methods["QProgressBar"]["set"] = "setValue"
        self.methods["QProgressBar"]["clear"] = ("setValue", 0)
        self.methods["QProgressBar"]["show"] = ("setVisible", True)
        self.methods["QProgressBar"]["hide"] = ("setVisible", False)
        self.methods["QProgressBar"]["enable"] = ("setEnabled", True)
        self.methods["QProgressBar"]["disable"] = ("setEnabled", False)
        self.methods["QProgressBar"]["min"] = "setMinimum"
        self.methods["QProgressBar"]["max"] = "setMaximum"
        self.methods["QProgressBar"]["tooltip"] = "setToolTip"
        
        #QStackedWidget widgets method names
        self.methods["QStackedWidget"] = {}
        self.methods["QStackedWidget"]["get"] = "currentIndex"
        self.methods["QStackedWidget"]["set"] = "setCurrentIndex"

        # QCheckBox widgets method names
        self.methods["QCheckBox"] = {}
        self.methods["QCheckBox"]["get"] = "isChecked"
        self.methods["QCheckBox"]["set"] = "setChecked"
        self.methods["QCheckBox"]["enable"] = ("setEnabled", True)
        self.methods["QCheckBox"]["disable"] = ("setEnabled", False)
        self.methods["QCheckBox"]["show"] = ("setVisible", True)
        self.methods["QCheckBox"]["hide"] = ("setVisible", False)
        self.methods["QCheckBox"]["tooltip"] = "setToolTip"

        # QWidget (Generic) method names - Fallback for frames/containers
        self.methods["QWidget"] = {}
        self.methods["QWidget"]["show"] = ("setVisible", True)
        self.methods["QWidget"]["hide"] = ("setVisible", False)
        self.methods["QWidget"]["enable"] = ("setEnabled", True)
        self.methods["QWidget"]["disable"] = ("setEnabled", False)
        
    def getMRO(self, widget=None):
        if widget is not None:
            return WidgetHandler._mro(widget)
                        
    def getType(self, widget=None):
        if widget is not None:
            return WidgetHandler._type(widget)
    
    def getName(self, widget=None):
        if widget is not None:
            return WidgetHandler._name(widget)
        
    def getClass(self, widget=None):
        if widget is not None:
            wtype = self.getType(widget)
            
            if wtype not in self.mro_cache:
                self.mro_cache[wtype] = WidgetHandler._mro(widget)                        
            
            for clsname in self.mro_cache[wtype]:
                if clsname in self.methods:
                    return clsname
        
    def getRole(self, widget=None):
        if widget is not None:
            role = widget.property("role")
            
            if not role:
                raise RuntimeError(f"Widget '{widget.objectName()}' is missing required 'role' property")
            
            return role
                            
    def getInfo(self, widget=None):
        wname = self.getName(widget)
        wtype = self.getType(widget)
        
        print(f"widget : {widget} | type : {wtype} | name : {wname}")
        
    def checkRole(self, widget=None, name=None):
        retval = False
        
        if widget is not None and name is not None:
            if name in self.getRole(widget):
                retval = True
        
        return retval
        
    def invokeMethod(self, widget=None, action=None, *args):
        if widget is None:
            return
        
        TEXT_SETTERS = {"setText",
                        "setCurrentText",
                        }
        
        wclass = self.getClass(widget) or self.getType(widget)
        
        if action not in self.methods[wclass]:
            raise RuntimeError(f"Action '{action}' not supported for {wclass}")
                
        entry = self.methods[wclass][action]
        
        if isinstance(entry, tuple):
            method_name = entry[0]
            fixed_args = entry[1:]
        
        else:
            method_name = entry
            fixed_args = ()
            
        method = getattr(widget, method_name)
        
        if method_name in TEXT_SETTERS:
            norm_args = ["" if a is None else str(a) for a in args]
        else:
            norm_args = list(args)
        
        return method(*fixed_args, *norm_args)            
    
    def createMap(self, *widgets):
        widget_map = {}
        
        for widget in widgets:
            key = self.getRole(widget)
            
            if key not in widget_map:
                widget_map.update({key : widget})
            
            else:
                raise RuntimeError(f"Duplicate widget role '{key}' detected")
            
        return DictAsClass(widget_map)
    
    def configWidget(self, parent, widget_type, widget_name, connect_type=None, connect_func=None, event_filter=None, **kwargs):
        widget = parent.findChild(widget_type, widget_name)
        
        if not widget:
            print(f"Widget : {widget_name} not found")
            return None        
        
        # apply dynamic properties
        for name, value in kwargs.items():
            widget.setProperty(name, value)
            
        if "role" in kwargs and not kwargs["role"]:
            raise ValueError("role cannot be empty")
        
        # re-apply QSS after properties
        if kwargs:
            widget.style().polish(widget)
    
        # optional signal connection
        if  connect_type and connect_type != "event" and connect_func:
            signal = getattr(widget, connect_type, None)
        
            if signal:
                adapter = WidgetCallback(widget, connect_func)
                signal.connect(adapter)
            
            else:
                print(f"Signal '{connect_type}' not found on {widget_name}")
                
        # optional event connection
        widget._event_handler = connect_func
                
        # optional event filter
        if event_filter:
            widget.installEventFilter(event_filter)
        
        return widget
    
    def cyclicStateButton(self, btn, *args):
        if not args:
            raise ValueError(f"cyclicStateButton : {args} At least one value is required")
        
        if not isinstance(btn, QAbstractButton):
            raise RuntimeError(f"cyclicStateButton : {btn} is not a button widget")
        
        prop = "_cycle_index"
        index = btn.property(prop) or 0
        idx = (index + 1) % len(args)
        value = args[idx]
        
        btn.setProperty(prop, idx)
        self.invokeMethod(btn, "set", value)
        return value
    
    
class KeyFilter(QObject):
    # generic event filter for widget-atttached event handlers
    
    def __init__(self, parent=None, trigger_events=None):
        super().__init__(parent)

        # Normalize trigger events
        if trigger_events is None:
            self.trigger_events = set()
            
        elif isinstance(trigger_events, (list, tuple, set)):
            self.trigger_events = set(trigger_events)
            
        else:
            self.trigger_events = {trigger_events}

    def eventFilter(self, obj, event):
        
        if not hasattr(obj, "_keys_pressed"):
            obj._keys_pressed = set()
        
        if self.trigger_events and event.type() not in self.trigger_events:
            return False

        handler = getattr(obj, "_event_handler", None)

        if handler:
            # handler decides whether event is handled
            return bool(handler(obj, event))

        return False
            
            
class EventHandler():
    # generic key event handler with press-lock-release semantics.

    def __init__(self):
        # key -> callback
        self._key_map = {}

    def attachCallback(self, key, callback):
        # register a key with a callback.
        self._key_map[key] = callback

    def handle(self, widget, event):
        # handle the callback functions on events
        key = event.key()

        # key press event
        if event.type() == QEvent.KeyPress:

            # ignore repeated press while key is held
            if key in widget._keys_pressed:
                return True

            widget._keys_pressed.add(key)

            callback = self._key_map.get(key)
            if callback:
                return bool(callback(widget, event))

        # key release event
        elif event.type() == QEvent.KeyRelease:
            widget._keys_pressed.discard(key)
            return True

        return False