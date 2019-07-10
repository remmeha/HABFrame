import os
import sys
from data import main_database
from flask import render_template
from singleton import Singleton
from logger import Logging
from setting_handler import setting_handler
import page_handler
import time
import datetime
from mqtt import mqtt
from settings import Settings

PATH=os.path.dirname(os.path.abspath(__file__))

class message_handler(Singleton):
	
    def __init__(self):
        try:
            if self.loadingdone:
                pass
        except:
            self.loadingdone = True
            self.database = main_database()
            self.popupflag = False
            self.popupactive = False
            self.logging = Logging()
            self.setting_handler = setting_handler()
            self.setting_popup_timeout = self.setting_handler.get_setting("message_timeout")
            self.page_handler = page_handler.page_handler()
            self.toast_flag = False
            self.toast_db = []
            self.toast_message = "none"
            self.toast_sender = "none"
            self.toast_received = 0
            self.mqtt = mqtt()
            settings_c = Settings()
            self.mqtt_topics = settings_c.get_setting("messaging", "mqtt_topics").split(",")
            for topic in self.mqtt_topics:
                self.mqtt.add_listener(topic, self, "received_mqtt_message")
            ##send information messages on first run
            if not self.database.data["settings"]["first_run_messages_flag"]:
                self.database.data["settings"]["first_run_messages_flag"] = True
                message = "On a black screen, clock or photoframe, click on the bottom left corner to return to the main screen. "
                self.database.data["messages"].append([time.time(), "HABframe", "Return from screensaver", message, False])
                message = "Thank you for using HABframe!"
                self.database.data["messages"].append([time.time(), "HABframe", "welcome message", message, False])
                self.database.save_datafile()
                self.del_popup_flag()

    def get_name(self):
        return "message_handler"               
                

    def message_request(self, request, data_get):
        if request[0] == "new":			
            try:
                if "message" in data_get:
                    message = data_get["message"].replace("@20", "/").replace("%3B", ":")
                else:
                    message = request[2].replace("@20", "/").replace("%3B", ":")
                if "sender" in data_get:
                    sender = data_get["sender"]
                else:
                    sender = request[1]
                if "subject" in data_get:
                    subject = data_get["subject"]
                else:
                    subject = "-"
                self.new_message(sender, subject, message)
                return ["Message received"]
            except Exception as e:
                self.logging.error("Error in message: " +str(e), location="messages")
                return ["Invalid new message"]
        elif request[0] == "message_popup":
            i = 0
            found = False
            while i < len(self.database.data["messages"]) and not found:
                message = self.database.data["messages"][i]
                if not message[-1]: 
                    show_message = [i] + message
                    #we want the last unread message
                    #found = True
                i += 1
            n_unread = self.check_amount_unread()
            times = datetime.datetime.fromtimestamp(float(show_message[1])).strftime('%a %d-%m, %H:%M')
            return self.page_handler.create_popup("message", { "id": show_message[0], "from": show_message[2], "time": times, "message": show_message[4], "subject": show_message[3], "n_unread": n_unread } , renew_screensaver = False)
        elif request[0] == "markread_popup":
            message_id = int(request[1])
            self.logging.info("Marking message as read "+str(message_id), location="messages")
            self.database.data["messages"][message_id][-1] = True
            self.database.save_datafile()
            self.popupactive = False
            self.popupflag = False
            return ["Marked as read"]
        elif request[0] == "markallread_popup":
            message_id = int(request[1])
            self.logging.info("Marking all messages as read ", location="messages")
            for i in range(len(self.database.data["messages"])):
                self.database.data["messages"][i][-1] = True
            self.database.save_datafile()
            self.popupactive = False
            self.del_popup_flag()
            return ["Marked as read"]
        elif request[0] == "message_timeout":
            timeout = self.setting_handler.get_setting("message_timeout")
            return [str(timeout)]
        elif request[0] == "toast_timeout":
            timeout = self.setting_handler.get_setting("toast_timeout")
            return [str(timeout)]
        elif request[0] == "delete_popup":
            message_id = int(request[1])
            del(self.database.data["messages"][message_id])
            self.logging.info("Deleting message: "+str(message_id), location="messages")
            if len(self.database.data["messages"]) == 0:
                self.database.data["messages"] = []
                #self.database.data["messages"].append([time.time(), "none", "message database is empty", True])
            self.database.save_datafile()
            self.popupactive = False
            self.del_popup_flag()
            return ["Message deleted"]
        elif request[0] == "deactivate_popup":
            self.popupactive = False
            return ["popup deactive"]
        elif request[0] == "showmessage":
            message_id = int(request[1])
            return self.format_message(message_id = message_id)
        elif request[0] == "deletemessage":
            if request[1] == "all":
                self.database.data["messages"] = []
                #self.database.data["messages"].append([time.time(), "none", "message database is empty", True])
            else:
                message_id = int(request[1])
                del(self.database.data["messages"][message_id])
                self.logging.info("Deleting message: "+str(message_id), location="messages")
                if len(self.database.data["messages"]) == 0:
                    self.database.data["messages"] = []
                    #self.database.data["messages"].append([time.time(), "none", "message database is empty", True])
            self.database.save_datafile()
            return self.format_message_list(start = 0)
        elif request[0] == "showmessagepage":
            message_id = int(request[1])
            return self.format_message_list(start = message_id)
        elif request[0] == "toast":
            if "message" in data_get:
                self.toast_message = data_get["message"].replace("@20", "/").replace("%3B", ":")
            else:
                self.toast_message = request[2].replace("@20", "/").replace("%3B", ":")
            if "sender" in data_get:
                self.toast_sender = data_get["sender"].replace("@20", "/").replace("%3B", ":")
            else:
                self.toast_sender = request[1].replace("@20", "/").replace("%3B", ":")
            self.logging.debug("Received new toast message from http", location="messages")
            self.new_toast()	
            return ["Toast received"]		
        elif request[0] == "get_toast":
            return self.create_toast(len_max = 31)

    def new_message(self, sender, subject, message):
        self.database.data["messages"].append([time.time(), sender, subject, message, False])
        self.database.save_datafile()
        self.del_popup_flag()
        self.logging.write("Received new message from "+sender+": "+message, level="info", location="messages") 

    def new_toast(self):
        self.toast_received = time.time()
        self.toast_db.append([self.toast_sender, self.toast_message, time.time(), False, 0])
        self.logging.info("Received new toast message: "+self.toast_message, location="messages")
                   
    def create_toast(self, len_max): 
        toast = self.get_toast_message()
        data = { "text": toast[0], "from": toast[1], "len": len(toast[0]), "max": len_max }
        return self.page_handler.create_popup("toast", data = data, renew_screensaver = False)

    def get_messages(self):
        messages = []
        for i in reversed(range(len(self.database.data["messages"]))):
            m = self.database.data["messages"][i]
            messages.append( { "id": i, "date": m[0], "from": m[1], "subject": m[2], "message": m[3] } )
        return messages

    def check_amount_unread(self):
        unread = 0
        for message in self.database.data["messages"]:
            if not message[-1]:
                unread += 1
        return unread
        
    def check_unread(self):
        unread = False
        for message in self.database.data["messages"]:
            if not message[-1]:
                unread = True
        return unread
        
    def get_popup_flag(self):  ##The popup flag is set when a new message has generated a popup
        return self.popupflag
        
    def set_popup_flag(self):
        self.logging.write("Setting popup flag", level="warn", location="messages")
        self.popupflag = True
    
    def del_popup_flag(self): ##Only a new message can delete a popup
        if self.popupflag:
            self.logging.write("Removing popup flag", level="warn", location="messages")
        self.popupflag = False
        
    def get_popup_active(self):
        if time.time() > self.popup_time_activated + self.setting_popup_timeout+1:  ##seconds
            return False
        else:
            return True
        
    def set_popup_active(self, state):
        self.popup_time_activated = time.time()

    def check_toast(self):
        #print("=========================, checking toast")
        timeout = self.setting_handler.get_setting("toast_timeout")
        new_toast = False
        last_toast_send = 0
        for i in range(len(self.toast_db)):
            if self.toast_db[i][3]:
                last_toast_send = self.toast_db[i][4]
            if self.toast_db[i][2] < time.time()-600:
                self.toast_db[i][3] = True
            if not self.toast_db[i][3]:
                new_toast = True
        if len(self.toast_db) > 50:
            del self.toast_db[0:25]
        if self.toast_received > time.time()-600 and new_toast and last_toast_send < time.time()-timeout-3:
            return True
        else:
            return False

    def get_toast_message(self):
        ##return the first unread toast message
        for i in range(len(self.toast_db)):
            if not self.toast_db[i][3]: ##toast is unread
                self.toast_db[i][3] = True
                self.toast_db[i][4] = time.time()
                self.logging.write("Sending toast message: "+self.toast_db[i][0] + " / " + self.toast_db[i][1], level=2, location="messages")
                return [self.toast_db[i][1], self.toast_db[i][0]]
        self.logging.write("No unread toast message, sending last one: "+self.toast_message + " / " + self.toast_sender, level="warning", location="messages")
        return [self.toast_message, self.toast_sender]
        
    def format_message_list(self, start = 0):
        messages = self.get_messages()
        page_data = { "next_page": False, "prev_page": False, "messages": [] }
        try:
            start_page = int(start)
        except:
            start_page = 0
        if start_page == 0:
            start_message = 0
            stop_message = 6
        else:
            page_data["prev_page"] = start_page
            start_message = start_page*5 + 1
            stop_message = start_page*5 + 6
        n_messages = len(messages)
        if stop_message >= n_messages:
            stop_message = n_messages
        else:
            page_data["next_page"] = start_page + 1
        for i in range(start_message, stop_message):
            messages[i]["date"] = datetime.datetime.fromtimestamp(messages[i]["date"]).strftime('%a %d-%m, %H:%M')
            page_data["messages"].append(messages[i])
        return render_template("message_list.html", data = page_data)
        
    def format_message(self, message_id = 0):
        messages = self.get_messages()
        if message_id == -1:
            message_id = len(messages) -1
        if len(messages) > 0:
            for m in messages:
                if m["id"] == message_id:
                    message = m
            message["date"] = datetime.datetime.fromtimestamp(message["date"]).strftime('%a %d-%m, %H:%M') 
        else:
            message = { "date": "", "message": "No messages", "from": "" }
        if len(messages) > 0 and message["subject"] == "-":
            message["subject"] = message["date"]
        return render_template("message.html", data = message)
		
    def received_mqtt_message(self, topic, payload):
        try:
            message = payload['message']
            if "message" in topic.lower():
                t = "message"
            elif "toast" in topic.lower():
                t = "toast"
            else:
                try:
                    t = payload['type']
                except:
                    t = 'message'
            try:
                sender = payload['sender']
            except:
                sender = "unknown"
            if t == "message":
                subject = payload['subject']
                self.new_message(sender, subject, message)
            else:
                self.toast_sender = sender
                self.toast_message = message
                self.new_toast()
        except Exception as e:
            raise Exception(e)
        
        
		
