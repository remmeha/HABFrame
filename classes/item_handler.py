import os
import sys
import time
from pf_openhab import pf_openhab
from data import main_database
from setting_handler import setting_handler
from page_handler import page_handler
from message_handler import message_handler
from settings import Settings
from logger import Logging
import datetime
import json
import requests
from resizeimage import resizeimage
from PIL import Image
from io import BytesIO
import urllib3

PATH=os.path.dirname(os.path.abspath(__file__))

class item_handler():
	
    def __init__(self):
        self.openhab = pf_openhab()
        self.name = "item_handler"
        self.database = main_database()
        self.setting_handler = setting_handler()
        self.page_handler = page_handler()
        self.message_handler = message_handler()
        self.logging = Logging()
        settings_c = Settings()
        self.host = settings_c.get_setting("main", "hostname")
        self.port = settings_c.get_setting("main", "port")
        self.enable_clock = settings_c.get_setting("main", "enable_clock")
        self.enable_album = settings_c.get_setting("main", "enable_album")
        self.openhab_server = settings_c.get_setting("main", "openhab_ip")
        self.openhab_port = settings_c.get_setting("main", "openhab_port")
        self.http = urllib3.PoolManager()
        self.timeout_message_popup = 0
        self.saved_chart_periods = {}
        self.screentrigger = 0
        
    def item_request(self, request):
        action = request[0]
        if len(request) > 1:
            item = request[1]
        if action != "photoframe" and action != "popup_chart" and action != "icon":
            item_info = self.openhab.get_item(item)
            self.logging.debug("Item info for request: " + str(item_info), location=self.name)
        ##handle a button press per type of item:
        #print(item)
        if action == "set":
            if item_info == None: 
                return "none_none"
            elif item_info["type"] == "Switch_single":
                item_info = self.openhab.set_state(item, item_info["mappings"][0]["command"])
            elif item_info["type"] == "Switch":
                if item_info["state"] == "ON":
                    item_info = self.openhab.set_state(item, "OFF")
                else:
                    item_info = self.openhab.set_state(item, "ON")
            return self.page_handler.create_item_button(item_info, header = False)
        elif action == "cmd":
            command = request[2]
            item_info = self.openhab.set_state(item, command)
            if item_info == None:
                return "reload_widget_popup"
            elif item_info["subpage"][0:2] in ["a_", "c_", "d_", "s_"]:
                return "reload_widget_popup"
            else:
                return self.page_handler.create_item_button(item_info, header = False)
        elif action == "popup":
            if item_info == None:
                return "none_none"
                #return self.page_handler.create_popup("error", data = { "error": "Invalid Item" })
            self.setting_handler.screen_timeout_start = time.time()
            if item_info["state"][-1:] == "%":
                s = item_info["state"][0:-1]
            elif item_info["state"][-1:] == "C":
                s = item_info["state"][0:-2]
            else:
                s = item_info["state"]
            if item_info["type"] == "Selection":
                mappings = self.openhab.get_mappings(item)
                return self.page_handler.create_popup("selection", data = { "id": item, "mappings": mappings, "n": len(mappings) })
            elif item_info["type"] == "Colorpicker":
                return self.page_handler.create_popup("colorpicker", data = item_info )
            elif item_info["type"] == "Setpoint":
                item_info["state"] = s
                return self.page_handler.create_popup("setpoint", data = item_info )
            elif item_info["type"] == "Slider":
                item_info["state"] = s
                return self.page_handler.create_popup("slider", data = item_info )
            elif item_info["type"] == "Chart":
                ##item_info.update( { "chart_period": request[2] } )
                return self.page_handler.create_popup("chart", data = item_info )
            else:
                return "none_none"
        elif action == "popup_chart":
            data = { "id": item, "periods": [["4 Hours", "4h"], ["Day", "D"], ["3 Days", "3D"], ["Week", "W"], ["2 Weeks","2W"]] }
            return self.page_handler.create_popup("chart_period", data )
        elif action == "chart_data":
            data = self.get_chart_data(item, request[2].upper())
            return data
        elif action == "icon":
            icon = self.openhab.get_icon(item)
            return ["jpg", icon]
		
        
        
    def get_chart_data(self, item, period):
        default_period = self.setting_handler.get_setting("chart_period")
        #print(default_period, period)
        if default_period == "auto" and period.lower() == "default":
            if item in self.saved_chart_periods:
                period = self.saved_chart_periods[item]
            else:
                period = "D"
        elif period.lower() == "default":
            period = default_period
        self.saved_chart_periods[item] = period        
        data = self.openhab.get_chart_data(item, period)
        if data == None:
            self.logging.warn("No Chart data returned for %s" %item, location=self.name)
            return "None"
        d = eval(data["data"])
        try:
            p = int(period[0:len(period)-1])
            e = "s"
        except:
            p = 1
            e = ""
        formats = { "H": ["%H:%M", "Hour"+e], "D": ["%a %Hh", "Day"+e], "W": ["%d-%m", "Week"+e], "M": ["%d-%m", "Month"+e] }
        f = formats[period[-1:]]
        db = { "name": d["name"], "data": [], "labels": [], "fill": False, "grid": True, "color": "red", "xlabel": str(p) + " " + f[1], "ylabel": "Value", "points": 4 }
        if data["type"] == "temp":
            db.update( { "ylabel": "Temperature (°C)" } )
        elif data["type"] == "humi":
            db.update( { "ylabel": "Humidity (%)", "color": "blue" } )
        elif data["type"] == "pres":
            db.update( { "ylabel": "Pressure (mb)", "color": "green" } )
        elif data["type"] == "watt":
            db.update( { "ylabel": "Power (W)", "fill": True, "color": "yellow" } )
        for i in range(len(d["data"])):
            t = str(d["data"][i]["time"])
            t = datetime.datetime.fromtimestamp(float(t[0:-3])).strftime(f[0])
            val = "%.4f" %(float(d["data"][i]["state"]))
            if i == 0 or val != db["data"][-1]:
                db["data"].append(val)
                db["labels"].append(t)
        ##do not show point when there are a lot of datapoints
        if len(db["data"]) > 25:
            db["points"] = 0		
        return json.dumps(db)


		
		
