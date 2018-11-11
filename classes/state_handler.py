import os
import sys
import time
from pf_openhab import pf_openhab
from data import main_database
from setting_handler import setting_handler
from message_handler import message_handler
from settings import Settings
from logger import Logging
from singleton import Singleton
import datetime
import json
import requests
from resizeimage import resizeimage
from PIL import Image
from io import BytesIO
import urllib3

PATH=os.path.dirname(os.path.abspath(__file__))

class state_handler(Singleton):
	
    def __init__(self):
        try:
            if self.loadingdone:
                pass
        except:
            self.loadingdone = True
            self.openhab = pf_openhab()
            self.name = "state_handler"
            self.database = main_database()
            self.setting_handler = setting_handler()
            self.message_handler = message_handler()
            self.logging = Logging()
            settings_c = Settings()
            self.host = settings_c.get_setting("main", "hostname")
            self.port = settings_c.get_setting("main", "port")
            self.http = urllib3.PoolManager()
            self.timeouts = {}
            self.update_timeout("screensaver", 60)
            self.update_timeout("message", -1)
            self.screentrigger = 0
            self.screen_state = True
            try:
                self.im_size = settings_c.get_setting("album", "image_size") 
                self.album_url = settings_c.get_setting("album", "random_picture_url") 
            except Exception as e:
                self.logging.error("Invalid album settings: " + str(e), location=self.name)
                self.album_url = "none"
            try:
                self.album_info_url = settings_c.get_setting("album", "picture_info_url") 
                if self.album_info_url == None:
                    raise Exception("No data")
            except:
                self.logging.warn("No album info url", location=self.name)
                self.album_info_url = "none"

    def state_request(self, request):
        action = request[0]
        if len(request) > 1:
            item = request[1]
        ##handle a button press per type of item:
        #print(item)
        if action == "photoframe":
            if item == "frame":
                ans = self.setting_handler.set_setting("frame", request[2])
                if ans != None:
                    return ans[0]
                return "Setting saved"
            elif item == "screen":
                ans = self.setting_handler.set_setting("screen", request[2])
                if ans != None:
                    return ans[0]
                return "Setting saved"
            elif item == "trigger":  
                self.screentrigger = time.time()
                self.refresh_screensaver()
                self.logging.info("Triggered frame on externally", location=self.name)
                return "Screen triggered"
            else:
                return "none_none"            
        elif action == "icon":
            icon = self.openhab.get_icon(item)
            return ["jpg", icon]
        elif action == "picture":
            try:
                if item == "new" and self.album_url != "none":
                    response = requests.get(self.album_url)
                    with Image.open(BytesIO(response.content)) as image:
                        imgByteArr = BytesIO()
                        cover = Image.Image.resize(image, [int(self.im_size.split("x")[0]), int(self.im_size.split("x")[1])])
                        cover.save(imgByteArr, image.format)
                    return ["jpg", imgByteArr.getvalue()]
                elif item == "info" and self.album_info_url != "none" and self.album_info_url != "":
                    content = self.http.request('GET', self.album_info_url)
                    return content.data.decode("utf-8") 
                elif item == "info":
                    return "no album info"
            except Exception as e:
                self.logging.error("Error occured in processing picture for album %s" %e, location=self.name)
            return "error"
        
        
    def state_check(self, request):
        page = []
        main_page = request[0]
        subpage = "none"
        if len(request) > 1:
            subpage = request[1]
        
        ## get used settings
        setting_album_timeout = self.setting_handler.get_setting("album_timeout") ##not used
        setting_popup_timeout = self.setting_handler.get_setting("message_timeout")
        setting_screen_user = self.setting_handler.get_setting("screen")  ##screen on or off
        
        main_setting_screen_control = self.setting_handler.get_setting("main_screen_control")
        current_screen_state = self.get_screen_state()
        screensaver_page = self.get_screensaver_page()

        desired_screen_state = "off"
        desired_page = "unchanged"
        
        ##reset old screen trigger
        if self.screentrigger != 0 and time.time() > self.screentrigger + 5*60:
            self.screentrigger = 0
        
        ##calculate desired screen state (on / off) ##switching is done depending on configuration
        if main_page in  ["main", "settings", "messages"]:
            if self.check_timeout("screensaver") and setting_screen_user == "off":
                desired_screen_state = "off"
            else:
                desired_screen_state = "on"
        elif main_page in ["photoframe", "clock", "black"]:
            desired_screen_state = setting_screen_user
            
        ## check desired screen state for messages
        if self.message_handler.check_unread() and not self.message_handler.get_popup_flag():
            self.message_handler.set_popup_active(True)
            self.message_handler.set_popup_flag()
            self.logging.write("responding new message", level=2, location="item_handle")
            desired_screen_state = "on"
            new_message = True ###turn on screen and make popup
        elif not self.check_timeout("message"):
            desired_screen_state = "on"   ##keep screen on for message
            new_message = False
        else:
            new_message = False
            
        ##calculate desired page (main, black, album or clock) ##switching is done depending on configuration
        if main_page in  ["main", "settings", "messages"]:
            if self.check_timeout("screensaver") and setting_screen_user == "on" and screensaver_page != "main":
                desired_page = screensaver_page
        elif main_page == "photoframe" and screensaver_page != "album":
            desired_page = screensaver_page
        elif main_page == "clock" and screensaver_page != "clock":
            desired_page = screensaver_page
        elif main_page == "black" and setting_screen_user == "on":
            desired_page = screensaver_page            
        
        self.logging.debug("Screensaver page: %s" %(screensaver_page), location=self.name)
        self.logging.debug("Desired page: %s, desired_screen_state: %s" %(desired_page, desired_screen_state), location=self.name)
        self.logging.debug("Message timeout: %s, Subpage timeout: %s" %(self.check_timeout("message"), self.check_timeout("screensaver_subpage")), location=self.name)
        
        ## switch screen off is desired state is off
        if desired_screen_state == "off" and main_setting_screen_control != "off" and current_screen_state:  ##=="on"
            return self.switch_off_screen(main_setting_screen_control)
        elif desired_screen_state == "off" and current_screen_state:  ##=="on"
            link = self.get_desired_page_link("clock")
            return [link]
        elif self.screentrigger != 0:
            self.toggle_screen(state = True)
            self.screentrigger = 0
            self.refresh_screensaver()
            self.logging.info("turn on screen for trigger", location=self.name)
            return ["close_return_main"]
        
        ##actions when we want the screen on
        elif new_message:
            if not current_screen_state:
                self.toggle_screen(state = "on")  ##no need for a page change
                self.update_timeout("message", self.setting_handler.get_setting("message_timeout") + 2) ##in seconds
            return ["new_message"]
        elif self.message_handler.check_toast():  ##even if the screen is off
            self.logging.write("responding new toast message", level=2, location="item_handle")
            return ["new_toast"]
        elif desired_screen_state == "on" and desired_page != "unchanged" and self.check_timeout("message"): ##except when there is a message popup
            self.toggle_screen(state = setting_screen_user)
            link = self.get_desired_page_link(desired_page)
            return [link]
        elif self.check_timeout("screensaver_subpage") and self.check_timeout("message") and main_page not in ["photoframe", "clock"]:  ##except when there is a message popup
            self.delete_timeout("screensaver_subpage")
            return ["close_return_main"]
        elif self.check_timeout("screensaver_subpage") and self.check_timeout("message"):
            self.delete_timeout("screensaver_subpage")
        
                     
        ##if for some reason it end here;
        return ["no_actionHERE"]
                    

    def switch_off_screen(self, main_setting_screen_control):
        self.toggle_screen(state = "off")
        if main_setting_screen_control == "black":
            link = self.get_desired_page_link("black")
            return [link]
        else:
            link = self.get_desired_page_link("main")
            return [link]
            
    def get_screensaver_page(self):
        enable_clock = self.setting_handler.get_setting("main_enable_clock")
        enable_album = self.setting_handler.get_setting("main_enable_album")
        setting_album_clock = self.setting_handler.get_setting("frame") ##photoframe or clock when screen is on
        
        if enable_album == "1" and setting_album_clock == "photoframe":
            return "album"
        elif enable_clock == "1" and setting_album_clock == "clock":
            return "clock"
        else:
            return "main"
        
       
    def get_desired_page_link(self, page):
        if page == "album":
            self.logging.info("http://"+self.host+":"+self.port+"/page/photoframe", location=self.name)
            return "http://"+self.host+":"+self.port+"/page/photoframe"
        elif page == "clock":
            type_clock = self.setting_handler.get_setting("clock_type")
            self.logging.info("http://"+self.host+":"+self.port+"/page/clock/"+type_clock, location=self.name)
            return "http://"+self.host+":"+self.port+"/page/clock/"+type_clock
        elif page == "main":
            main_setting_screen_control = self.setting_handler.enable_screen_control
            self.logging.info("External screen control: %s, no action, stay on main page" %main_setting_screen_control, location=self.name)
            return "http://"+self.host+":"+self.port+"/page/maindiv/screensaver"
        elif page == "black":
            self.logging.write("http://"+self.host+":"+self.port+"/black", level=2)
            return "http://"+self.host+":"+self.port+"/page/black"

    def update_timeout(self, name, delta): ##delta in seconds
        self.timeouts[name] = time.time() + delta
        
    def check_timeout(self, name):
        if name in self.timeouts:
            self.logging.debug(("Timeout %s: "%name).ljust(30) + str(time.ctime(int(self.timeouts[name]))), location=self.name)
            if self.timeouts[name] < time.time():
                return True
            else:
                return False
        else:
            return False
    
    def delete_timeout(self, name):
        if name in self.timeouts:
            del self.timeouts[name]
        else:
            self.logging.debug("Timeout %s not deleted, not existing" %name, location=self.name)
    
    def refresh_screensaver(self):
        to = self.setting_handler.get_setting("screen_timeout")
        if to == "off":
            to = 24*60*300
        self.logging.info("refreshing screensaver", location=self.name)
        self.update_timeout("screensaver", int(to)*6)
        self.delete_timeout("screensaver_subpage")
        
    def refresh_screensaver_subpage(self):
        self.refresh_screensaver()
        self.logging.info("refreshing screensaver for popup", location=self.name)
        self.update_timeout("screensaver_subpage", 25)
        
            
    def toggle_screen(self, state = True):
        screen_control = self.setting_handler.get_setting("main_screen_control")
        switch = False
        if str(self.screen_state) != str(state):
            self.logging.info("Switching screen state: %s, %s" %(str(self.screen_state), str(state)), location=self.name)
        else:
            self.logging.debug("Switching screen state: %s, %s" %(str(self.screen_state), str(state)), location=self.name)
        if (state == "off" or state == "0" or state == False) and self.get_screen_state() == True:
            state = False
            self.screen_state = False
            switch = True
        elif (state == "on" or state == "1" or state == True) and self.get_screen_state() == False:
            state = True
            self.screen_state = True
            switch = True
        if screen_control == "pi":
            if not state:
                self.logging.write("Turn off screen", level=2)
                cmd = "echo 1 > /sys/class/backlight/rpi_backlight/bl_power"
                os.system(cmd)
            else:
                self.logging.write("Turn on screen", level=2)
                cmd = "echo 0 > /sys/class/backlight/rpi_backlight/bl_power"
                os.system(cmd)
        elif screen_control == "url" and switch:
            if not state:
                self.logging.info("Turn off screen via url", location=self.name)
                url = self.setting_handler.get_setting("screen_control_off_url")
            else:
                self.logging.info("Turn on screen via url", location=self.name)
                url = self.setting_handler.get_setting("screen_control_on_url")
            self.logging.debug("Screensaver url: %s" %url, location=self.name) 
            self.http.request('GET', url)
        elif screen_control == "cmd" and switch:
            if not state:
                self.logging.info("Turn off screen via cmd", location=self.name)
                cmd = self.setting_handler.get_setting("screen_control_off_cmd")
            else:
                self.logging.info("Turn on screen via cmd", location=self.name)
                cmd = self.setting_handler.get_setting("screen_control_on_cmd")
            self.logging.debug("Screensaver cmd: %s" %cmd, location=self.name) 
            os.system(cmd)

    def get_screen_state(self):
        return self.screen_state
