import re
from queue import Queue, Empty


class GcodeHandler():
    def __init__(self):
        self.queue = Queue()
        self.callback = None
        self.gcode = None
        self.ack_list = []
        self.axis_pos_list = []
        self.sd_card_files_list = []
        self.ok_flag = False
        self.home_flag = False
        self.temp_report_flag = False
        self.sd_write_flag = False
        self.init_print_flag = False
        self.gcode_ext_tuple = (".gco", ".g", ".gcode")
        self.sd_card_files_list = []
        self.sd_file_open_flag = False
        self.m400_flag = False
        self.sd_abort_flag = False
        self.sd_abort_response_flag = False

        self.gcode_dict = {"linear" : "G1",
                           "lmove1" : "G1",
                           "dwell" : "G4", 
                           "home" : "G28",
                           "absolute" : "G90",
                           "relative" : "G91",
                           "set-pos" : "G92",
                           "ex-pos" : "G92 E0",
                           "list-SD" : "M20",
                           "init-SD" : "M21",
                           "select-SD" : "M23",
                           "start-SD" : "M24",
                           "resume-SD" : "M24",
                           "pause-SD" : "M25",
                           "delete-SD" : "M30",
                           "ext-rel" : "M82",
                           "set-stepsmm" : "M92",
                           "get-pos" : "M114",
                           "laser-com" : "M118 A1 P3",
                           "extruder" : "M302 S0",
                           "finish-move" : "M400",
                           "quick-stop": "M410",
                           "abort-SD" : "M524"                                                                                 
                           }

    def attachCallback(self, callback_obj):
        if callback_obj:
            self.callback = callback_obj

    def fireCallback(self, code):
        if self.callback:
            self.callback.fire(code)

    def encode(self, cmd):
        self.queue.put(cmd)
        self.parse(cmd)

    def isMotion(self, gcode):
        code = gcode.split(';')[0]
        retval = False

        if code is not None and code != " ":
            code = re.sub(r'G0([0-9])', r'G\1', code)  # normalize G01 → G1
            parts = re.findall(r"([A-Z])([-+]?[0-9]*\.?[0-9]+)", code)

            if parts:
                cmd = parts[0][0] + parts[0][1]

                if cmd:
                    if cmd in ["G0", "G1", "G2", "G3"]:
                        retval = True
                
        return retval   
        
    def parse(self, cmd):
        pass

    def readQueue(self):
        try:
            self.gcode = self.queue.get_nowait()
            print(f"Queue : {self.gcode}")
        except Empty:
            self.gcode = None


    def reset(self):
        """
        HARD reset of gcode state after disconnect / abort / reconnect
        """
        try:
            with self.queue.mutex:
                self.queue.queue.clear()
        except Exception:
            pass

        self.gcode = None
        self.ack_list = []
        self.ok_flag = True
        self.home_flag = False
        self.temp_report_flag = False
        self.sd_abort_flag = False
        self.sd_abort_response_flag = False


    def decode(self, response):
        rx_data = response.strip()
        self.append_response_flag = True

        #  BUSY → firmware still processing
        if "busy" in rx_data.lower():
            self.append_response_flag = False
            self.ok_flag = False
            return

        #  OK (supports: "ok", "ok P15 B3", etc.)
        if rx_data.startswith("ok"):
            self.append_response_flag = False
            self.ok_flag = True

            self.readQueue()
            if self.gcode:
                self.process(self.gcode, self.ack_list)

            self.ack_list = []
            self.fireCallback("ok")
            return


        # Temperature report
        if 'T:' in response and 'B:' in response and '@:' in response:
            self.append_response_flag = False
            self.temp_report_flag = True
            return

        #  Axis position
        if all(p in response for p in ["X:", "Y:", "Z:", "Count"]):
            self.append_response_flag = False
            self.decodeAxisPos(response)
            return

        # SD print done
        if 'Done printing file' in response:
            self.append_response_flag = False
            self.fireCallback("SDdone")
            return

        #  Accumulate multiline response
        if self.append_response_flag:
            self.ack_list.append(rx_data)

    def process(self, gcode, response_list):
        print(f"Gcode : {gcode}")
        print(f"ACK : {response_list}")

        try:
            if "G28" in gcode:
                self.goHome()
                # Do NOT fall through to else-block: the position callback
                # is pumped by the axis-position line that G28 generates.
                return

            if "G92" in gcode:
                self.getAxisPos()

            if gcode == "M114":
                self.getAxisPos()
                # Do NOT fall through to else-block: the "M114" callback is
                # already fired by decodeAxisPos() when the axis position line
                # (X:... Count...) arrives. Firing it again here would cause
                # indexProgram() to run twice and send each G-code line twice.
                return

            if gcode == "M20":
                self.listSDCard(response_list)

            if "M23" in gcode:
                self.initSDPrint(response_list)

            if "M28" in gcode:
                self.sd_write_flag = True

            if gcode == "M29": 
                self.sd_write_flag = False

            if "M524" in gcode:
                self.sd_abort_flag = True

        except Exception as e:
            print(f"exception : {e}")

        else:
            code = gcode.split(" ")[0]
            print(f"code = {code}")
            self.fireCallback(code)

    def checksum(self, gcode):
        cs = ord(gcode[0])
        for ch in gcode[1:]:
            cs = cs ^ ord(ch)

        return cs
    
    def goHome(self):
        self.home_flag = True
        self.getAxisPos()

    def decodeAxisPos(self, cmd):
        self.pos_list = [pos for pos in cmd.split('Count')[0].split()]
        # print(f"position : {self.pos_list}")
        self.fireCallback("M114")
        
    def getAxisPos(self):
        return self.pos_list

    def listSDCard(self, cmd_list):
        self.sd_card_files_list = [data.split(" ")[0] for data in cmd_list if data.split(" ")[0].lower().endswith(self.gcode_ext_tuple)]
        print(f"SD card : {self.sd_card_files_list}")

    def initSDPrint(self, response_list):
        if "File opened" in response_list[1]:
            self.sd_file_open_flag = True
        
        elif "open failed" in response_list[1]:
            self.sd_file_open_flag = False
