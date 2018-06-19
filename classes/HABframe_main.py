import threading
import time
import sys
import os
PATH=os.path.dirname(os.path.abspath(__file__))
sys.path.append(PATH + "/classes")
sys.path.append(PATH + "/data")
#print(PATH)
import data
import settings
import logger
import datetime
#from dateutil.relativedelta import relativedelta
from page_handler import page_handler
from setting_handler import setting_handler
from item_handler import item_handler
from state_handler import state_handler
from message_handler import message_handler
from task_scheduler import task_scheduler

class habframe_main():

    def __init__(self, interval=60):
        ##read settings from file
        self.settings_c = settings.Settings()
        ##enable logging
        self.logging = logger.Logging()
        ##loading database
        self.maindatabase = data.main_database()
        self.interval = interval
        self.page_handler = page_handler()
        self.setting_handler = setting_handler()
        self.item_handler = item_handler()
        self.state_handler = state_handler()
        self.message_handler = message_handler()
        self.task_scheduler = task_scheduler()
				
        thread = threading.Thread(target=self.run, args=())
        thread.daemon = True                            # Daemonize thread
        thread.start() # Start the execution
			


    def run(self):
        last_tasks_execute = time.time()
        while True:
            # Do something
            self.task_scheduler.check_tasks()
            time.sleep(self.interval)



    def process_request(self, env):
        string = ""

        request = self.convert_request_string(env["PATH_INFO"])
        ## request like:  0: user / 1: hash / 2: request / 3: item / 4-:values
        if request != False:
            self.logging.debug("Request: " + str(request), location="main")
            if request["request"] != "data":
                self.execute_request = request
                response = self.process_task()
            else:
                self.execute_buffer.append([0, request])
                self.execute_request = request
                thread1 = threading.Thread(target=self.process_task, args=())
                thread1.daemon = True                            # Daemonize thread
                thread1.start()	
                response = [True, "request added"]	
        else:
            response = [ False,  "Not a valid request" ]

        return response + [ False]


    def convert_request_string(self, string):
        #print(string)
        if "http" in string:
            pos = string[7:].find("/")
            string = string[8+pos:]
        request_split = string.replace("%20", " ").replace("%2F", "/").split('?')
        request_list = request_split[0].replace("%20", " ").split('/')
        request = {}
        try:
            d = request_split[1].split('&')
            data_get = {}
            for dat in d:
                data_get[dat.split("=")[0]] = dat.split("=")[1] 
        except:
            data_get = {}
        len_list = len(request_list)
        request = {}
        self.logging.debug("Convert request list: " + str(request_list), location="main")
        try:
            request["request"] = request_list[0]
            if len(request_list) > 1:
                request["page"] = request_list[1:]
            else:
                request["page"] = []
            request["data_get"] = data_get
            if request["request"] == "":
                request["request"] = "page"
                request["page"] = ["main"]
            return request
        except:
            return False

    def process_task(self):
        request = self.execute_request
        return_string = ""
        self.logging.info("Process request: " + str(request), location="main")
        if request["request"] == "page":
            page = self.page_handler.get_page(request)
            #for line in page:
            #    return_string += line + "\n"
            return [True, page]
        elif request["request"] == "setting":
            page = self.setting_handler.setting_request(request["page"])
            self.state_handler.refresh_screensaver_subpage()
            for line in page:
                return_string += line + "\n"
        elif request["request"] == "item":
            page = self.item_handler.item_request(request["page"])
            if page[0] == "jpg":
                return ["bytedata", page[1]]
            return [ True, page ]
        elif request["request"] == "state":
            page = self.state_handler.state_request(request["page"])
            if page[0] == "jpg":
                return ["bytedata", page[1]]
            return [ True, page ]
        elif request["request"] == "check":
            page = self.state_handler.state_check(request["page"])
            for line in page:
                return_string += line + "\n"					
        elif request["request"] == "message":
            page = self.message_handler.message_request(request["page"], request["data_get"])
            if request["page"][0] in ["showmessage", "showmessagepage"]:
                self.state_handler.refresh_screensaver_subpage()
            if type(page) == list:
                string = ""
                for line in page:
                    string += line + "\n"
                return [ True, string ]
            return [ True, page ]
        return [True, return_string]

