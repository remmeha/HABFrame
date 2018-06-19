import os
import sys
import time
from pf_openhab import pf_openhab
from data import main_database
from settings import Settings
from singleton import Singleton
from logger import Logging
import urllib3

PATH=os.path.dirname(os.path.abspath(__file__))

class setting_handler(Singleton):
	
    def __init__(self):
        try:
            if self.loadingdone:
                pass
        except:
            self.loadingdone = True
            self.name = "setting_handler"
            self.database = main_database()
            self.logging = Logging()
            self.http = urllib3.PoolManager()	
            self.settings = {}
            #self.settings["main_page"] = ["Front page", ["OpenHAB", "Weather"]]
            self.settings["screen_timeout"] = ["Screen timeout (min)", [1, 3, 5, 10, 15, 30, "off"]]
            self.settings["album_timeout"] = ["Album timeout (hr)", [1, 3, 5, 10, 15, 30]]
            self.settings["message_timeout"] = ["Message timeout (s)", [10, 30, 60, 120, 300]]
            self.settings["toast_timeout"] = ["Info timeout (s)", [7, 10, 15, 20, 30]]
            self.settings["mouse"] = ["Mouse button", ["on", "off"]]
            self.settings["items_per_page"] = ["Number of items per page", [6, 8, 9, 12]]
            self.settings["sensors_per_page"] = ["Number of sensor items per page", [6, 8, 9, 12]]
            self.settings["screen"] = ["Screen", ["on", "off"]]
            self.settings["frame"] = ["Photo / Clock", ["photoframe", "clock"]]
            self.settings["frame_info"] = ["Frame Info", ["none", "load", "album", "both"]]
            self.settings["frame_td"] = ["Frame Time/Date", ["none", "clock", "date", "both"]]
            self.settings["frame_display_time"] = ["Photo display time", ["short", "medium", "long", "extra long"]]
            self.settings["clock_type"] = ["Clock type", ["digital", "analog"]]
            self.settings["chart_period"] = ["Default chart period", ["auto", "4 hours", "12 hours", "1 day", "3 days", "1 week"]]
            
            for key, item in self.settings.items():
                value = self.database.data["settings"][key]
                self.settings[key].append(int(value))
                
            settings_c = Settings()
            self.enable_screen_control = settings_c.get_setting("main", "enable_screen_control")

            if self.enable_screen_control in ["pi", "black"]:
                pass
            elif self.enable_screen_control == "url":
                try:
                    self.screen_control_on_url = settings_c.get_setting("main", "screen_on_url")
                    self.screen_control_off_url = settings_c.get_setting("main", "screen_off_url")
                    self.settings["screen_control_on_url"] = [0,0,self.screen_control_on_url]
                    self.settings["screen_control_off_url"] = [0,0,self.screen_control_off_url]
                except:
                    self.logging.error("Add settings 'screen_on_url' and 'screen_off_url' for external url screen control", location="settings_handler")
                    self.enable_screen_control = "black"
            elif self.enable_screen_control == "cmd":
                try:
                    self.screen_control_on_cmd = settings_c.get_setting("main", "screen_on_cmd")
                    self.screen_control_off_cmd = settings_c.get_setting("main", "screen_off_cmd")
                    self.settings["screen_control_on_cmd"] = [0,0,self.screen_control_on_cmd]
                    self.settings["screen_control_off_cmd"] = [0,0,self.screen_control_off_cmd]
                except:
                    self.logging.error("Add settings 'screen_on_cmd' and 'screen_off_cmd' for external command screen control", location="settings_handler")
                    self.enable_screen_control = "black"
            elif self.enable_screen_control != "off":
                self.logging.error("Incorrect screen control enable settings, screen control is off", location="settings_handler")
                self.enable_screen_control = "off"
                
            self.settings["main_enable_clock"] = [0,0,settings_c.get_setting("main", "enable_clock")]
            self.settings["main_enable_album"] = [0,0,settings_c.get_setting("main", "enable_album")]
            if settings_c.get_setting("main", "enable_album") == "0":
                self.logging.warn("Album not enabled, setting frame to clock", location="settings_handler")
                self.__set_setting("frame", "clock")
            elif settings_c.get_setting("main", "enable_clock") == "0":
                self.logging.warn("clock not enabled, setting frame to photoframe", location="settings_handler")
                self.__set_setting("frame", "photoframe")
            if settings_c.get_setting("main", "enable_clock") == "0" and settings_c.get_setting("main", "enable_album") == "0":
                self.logging.warn("Album and clock not enabled, turning off screen setting", location="settings_handler")
                self.__set_setting("screen", "off")  ##in this case only the screensaver determines if the screen is turned on or off
            self.settings["main_screen_control"] = [0,0,self.enable_screen_control]
            
            
    def setting_request(self, request):
        if request[0] == "setsetting":
            setting = request[1]
            if setting == "screen" and self.get_setting("main_enable_album") == "0" and self.get_setting("main_enable_clock") == "0":
                return ["Enable album or clock to be able to control this setting"]
            if setting == "frame" and (self.get_setting("main_enable_album") == "0" or self.get_setting("main_enable_clock") == "0"):
                return ["Enable album and clock to be able to control this setting"]
            cur_value = self.settings[setting][2]
            if cur_value+1 < len(self.settings[setting][1]):
                self.settings[setting][2] = cur_value + 1
            else:
                self.settings[setting][2] = 0
            self.save_settings()
            self.logging.write(self.settings[setting][0] + ": " + str(self.settings[setting][1][self.settings[setting][2]]), level=2)
            return [self.settings[setting][0] + ": " + str(self.settings[setting][1][self.settings[setting][2]])]
        elif request[0] == "getsetting":
            return [str(self.get_setting(request[1]))]

    def set_setting(self, setting, value):
        if setting == "screen" and self.get_setting("main_enable_album") == "0" and self.get_setting("main_enable_clock") == "0":
            return ["Enable album or clock to be able to control this setting"]
        if setting == "frame" and (self.get_setting("main_enable_album") == "0" or self.get_setting("main_enable_clock") == "0"):
            return ["Enable album and clock to be able to control this setting"]
        self.__set_setting(setting, value)
            
    def __set_setting(self, setting, value):
        values = self.settings[setting][1]
        self.screen_timeout_start = time.time()
        for i in range(len(values)):
            if values[i] == value:
                self.settings[setting][2] = i
                self.save_settings()
        

    def get_settings(self):
        settings = []
        for key, item in self.settings.items():
            if (key == "clock_type") and self.get_setting("main_enable_clock") == "0": 
                pass
            elif (key == "album_timeout" or key == "frame_info" or key == "frame_td" or key == "frame_display_time") and self.get_setting("main_enable_album") == "0":
                pass
            elif key == "frame" and (self.get_setting("main_enable_album") == "0" or self.get_setting("main_enable_clock") == "0"):
                pass 
            elif key == "screen" and self.get_setting("main_enable_album") == "0" and self.get_setting("main_enable_clock") == "0":
                pass
            elif key == "screen" and self.enable_screen_control == "off":
                pass
            elif item[0] != 0:
                settings.append([key, item[0], item[1][item[2]]])
        return settings
        
    def save_settings(self):
        for key, item in self.settings.items():
            self.database.data["settings"][key] = item[2]
        self.database.save_datafile()
        
    def get_setting(self, setting):
        value = self.settings[setting][2]
        if self.settings[setting][0] != 0:
            return self.translate_setting(setting, self.settings[setting][1][value])
        else:
            return value

    def translate_setting(self, setting, value):
        if setting == "frame_display_time":
            timing = { "short": 5000, "medium": 13000, "long": 20000, "extra long": 60000 }
            if value == 0: 
                return "short"
            return timing[value]
        elif setting == "chart_period":
            period = { "auto": "auto", "4 hours": "4H", "12 hours": "12H", "1 day": "1D", "3 days": "3D", "1 week": "1W" }
            if value == 0: 
                return "auto"
            return period[value]
        return value
        
