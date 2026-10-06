import os
import json
import collections
import logging
import traceback
from pathlib import Path
from configparser import ConfigParser
from datetime import datetime
from typing import Optional
from PySide6.QtCore import QObject, QEvent, Qt
from dataclasses import dataclass
from threading import Lock

#util
@dataclass
class SubstringResult:
    found: bool
    matches: list[str]

class CallbackHandler(object):
    handlers = None

    def __init__(self):
        self.handlers = collections.defaultdict(set)

    def register(self, event, callback):
        self.handlers[event].add(callback)

    def fire(self, event, **kwargs):
        for handler in self.handlers.get(event, []):
            handler(**kwargs)


class FileHandler():
    def __init__(self):
        self.cwd = Path(__file__).resolve().parent
            
    def getCWD(self):
        return self.cwd

    def getPath(self, dir=None, file=None):
        path = ""
        if dir and file:
            path = Path(dir, file)
        
        else:
            if dir:
                path = Path(self.cwd, dir)

            if file:
                path = Path(self.cwd, file)
        
        return path
    
    def makeDir(self, directory):
        if directory:
            dir_path = Path(directory) if Path(directory).is_absolute() else Path(self.cwd, directory)
            os.makedirs(dir_path, exist_ok=True)

    def checkDir(self, directory):
        if directory:
            dir_path = Path(directory) if Path(directory).is_absolute() else Path(self.cwd, directory)
            if not os.path.isdir(dir_path):
                os.makedirs(dir_path, exist_ok=True)      

    def saveDxfParams(self, dxf_path, params):
        """Save parameters as a JSON sidecar file for a DXF."""
        if not dxf_path:
            return
        
        save_path = Path(dxf_path).with_suffix(Path(dxf_path).suffix + ".json")
        try:
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(params, f, indent=4)
            return True
        except Exception as e:
            print(f"Error saving DXF params: {e}")
            return False

    def loadDxfParams(self, dxf_path):
        """Load parameters from a JSON sidecar file for a DXF."""
        if not dxf_path:
            return None
            
        load_path = Path(dxf_path).with_suffix(Path(dxf_path).suffix + ".json")
        if os.path.exists(load_path):
            try:
                with open(load_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading DXF params: {e}")
                return None
        return None

    def cleanupOrphanedParams(self, directory):
        """Delete .json files in the directory that don't have a matching .dxf file."""
        if not directory or not os.path.isdir(directory):
            return
            
        try:
            for filename in os.listdir(directory):
                if filename.endswith(".dxf.json"):
                    json_path = Path(directory) / filename
                    dxf_filename = filename[:-5] # remove .json
                    dxf_path = Path(directory) / dxf_filename
                    
                    if not dxf_path.exists():
                        os.remove(json_path)
                        print(f"Cleaned up orphaned param file: {filename}")
        except Exception as e:
            print(f"Error during orphaned param cleanup: {e}")


class ConfigHandler():
    def __init__(self):
        self.ini_parser = ConfigParser()

    def updateFile(self, config_path):
        with open(config_path, 'w') as configfile:
            self.ini_parser.write(configfile)

    def addParameter(self, section, key, value):
        if self.ini_parser.has_section(section):
            self.ini_parser.set(section, key, value)
        
        else:
            self.ini_parser[section] = {key : value}

    def getSection(self, section):
        if self.ini_parser.has_section(section):
            return dict(self.ini_parser.items(section))

    def getValues(self, section, key):
        if self.ini_parser.has_section(section):
            if self.ini_parser.has_option(section, key):
                return self.ini_parser.get(section, key)


class CyclicBuffer:
    def __init__(self, max_len=1):
        if max_len <= 0:
            raise ValueError("max_len must be > 0")
        
        self._index = -1
        self._max_len = max_len
        self._buffer = collections.deque(maxlen=max_len)
        self._lock = Lock()
        
    def __len__(self):
        # current number of elements
        with self._lock:
            return len(self._buffer)

    def __repr__(self):
        # debugging info for developer
        with self._lock:
            return f"CyclicBuffer(max_len={self._max_len}, buffer={list(self._buffer)})"
        
    def currentIndex(self):
        # return the current index of the buffer
        with self._lock:
            return self._index
        
    def push(self, value):
        # add a value to the buffer (thread-safe)
        with self._lock:
            self._buffer.append(value)
            self._index = len(self._buffer) - 1

    def get(self):
        # return a snapshot list of the buffer
        with self._lock:
            return list(self._buffer)
        
    def peek(self, arg=-1):
        # return the value of the buffer present at the provided index
        with self._lock:
            if not self._buffer:
                return None
        
            try:
                return self._buffer[arg]
            
            except IndexError:
                self.index = 0
                raise IndexError("peek index out of range")
            
    def increment(self):
        # move buffer index forward till latest element is reach
        with self._lock:
            if not self._buffer:
                return None

            self._index = min(self._index + 1, len(self._buffer) - 1)
            return self._buffer[self._index]
    
    def decrement(self):
        # move buffer index backward till oldest element is reach
        with self._lock:
            if not self._buffer:
                return None

            self._index = max(self._index - 1, 0)
            return self._buffer[self._index]

    def clear(self):
        # clear the buffer
        with self._lock:
            self.index = 0
            self._buffer.clear()

    def is_full(self):
        # check if buffer is full
        with self._lock:
            return len(self._buffer) == self._max_len

class AppLogger():
    def __init__(self, 
                 logger_name = __name__,
                 log_file = "app.log",
                 log_level = "DEBUG",
                 log_format = "{asctime} - {levelname} - {message}",
                 date_format = "%Y-%m-%d %H:%M",
                 file_mode = "a",
                 encoding = "utf-8",
                 max_file_size = None,
                 backup_count = 5):
        
        self.logger_name = logger_name
        self.log_file = log_file
        self.log_level = log_level
        self.log_format = log_format
        self.date_format = date_format
        self.file_mode = file_mode
        self.encoding = encoding
        self.max_file_size = max_file_size
        self.backup_count = backup_count
        
        # Create the logger instance
        self.logger = self._setup_logger()

    def _setup_logger(self):

        # Create logger
        logger = logging.getLogger(self.logger_name)
        logger.setLevel(self.log_level)
        
        # Avoid adding multiple handlers if logger already exists
        if logger.handlers:
            return logger
        
        # Create formatter
        formatter = logging.Formatter(
            self.log_format,
            style="{",
            datefmt=self.date_format
        )
        
        # Create file handler (with rotation if specified)
        if self.max_file_size:
            from logging.handlers import RotatingFileHandler
            file_handler = RotatingFileHandler(
                self.log_file,
                mode=self.file_mode,
                maxBytes=self.max_file_size,
                backupCount=self.backup_count,
                encoding=self.encoding
            )
        else:
            file_handler = logging.FileHandler(
                self.log_file,
                mode=self.file_mode,
                encoding=self.encoding
            )
        
        # Set formatter and add handler
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        return logger
    
    def get_logger(self):
        return self.logger
    
    def debug(self, message):
        self.logger.debug(message)
    
    def info(self, message):
        self.logger.info(message)
    
    def warning(self, message):
        self.logger.warning(message)
    
    def error(self, message):
        self.logger.error(message)
    
    def critical(self, message):
        self.logger.critical(message)
    
    def logUiAction(self, action, widget_name = "", details = ""):

        message = f"UI Action: {action}"
        if widget_name:
            message += f" | Widget: {widget_name}"
        if details:
            message += f" | Details: {details}"
        
        self.logger.info(message)
    
    def logErrorTraceback(self, error, context = ""):
        message = f"Error occurred"
        if context:
            message += f" in {context}"
        message += f": {str(error)}"
        
        self.logger.error(message)
        self.logger.error(f"Traceback: {traceback.format_exc()}")
    
    def sessionSeparator(self, position):
        """Add a separator to mark the start of a new session."""
        separator = "=" * 50
        timestamp = datetime.now().strftime(self.date_format)
        self.logger.info(f"{separator}")
        self.logger.info(f"New session {position} at {timestamp}")
        self.logger.info(f"{separator}")

class WheelBlocker(QObject):
    def eventFilter(self, obj, event):
        # Block mouse wheel
        if event.type() == QEvent.Wheel:
            return True
        
        # Block arrow keys, page up/down
        if event.type() == QEvent.KeyPress:
            if event.key() in (Qt.Key_Up, Qt.Key_Down, Qt.Key_PageUp, Qt.Key_PageDown):
                return True

        return False

class Utils():
    def __init__(self):
        self.debugFlag = False
        self.debugflag = [False]    # flag to print debug info
        self.msg_list = []

    def setDebugMsgFlag(self, setFlag):
        self.debugflag[0] = setFlag

    def debugMsg(self, text):
        if self.debugflag[0]:
            print(text)
            
    def debugPrint(self, msg):
        if self.debugFlag:
            print(msg)            

    def putMessage(self, *args):
        for msg in args:
            self.msg_list.append(msg)

    def getMessage(self):
        return self.msg_list

    def clearMessage(self):
        self.msg_list = []

    def argIsNotNone(*args):
        return all(arg is not None for arg in args)
    
    def checkSubString(self, string, *substrings):
        matches = []
        
        for sub in substrings:
            if sub in string:
                matches.append(sub)
                 
        return SubstringResult(bool(matches), matches)
    
    def dedupeList(self, lst):
        seen = set()
        idx = 0
        
        for x in lst:
            if x not in seen:
                seen.add(x)
                lst[idx] = x
                idx += 1
                
        del lst[idx:]
        
        
def fileRead(path):
    """Write content to a file at the specified path."""
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
        print(content)

def fileWrite(path, content, mode="a"):
    """Write content to a file at the specified path."""
    with open(path, mode, encoding="utf-8") as f:
        f.write(content + "\n")


def writeLog(logfile, message):
    """Write log messages to file with timestamps and print to console."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    full_msg = f"[{timestamp}] {message}"
    print(full_msg)
    fileWrite(logfile, full_msg, mode="a")

if __name__ == "__main__":
    pos_list = ['X:1.00', 'Y:20.00', 'Z:12.00', 'E:0.00']

    pos = [pos.split(':') for pos in pos_list]
    print(f"pos : {pos}")

