import os
import sys
import time
import datetime
from pf_openhab import pf_openhab
from flask import render_template
from flask import Markup
from data import main_database
from setting_handler import setting_handler
from message_handler import message_handler
from widgets_handler import widgets_handler
from state_handler import state_handler
from settings import Settings
from logger import Logging
import numpy as np

class page_handler():
	
    def __init__(self):
        self.openhab = pf_openhab()
        self.name = "page_handler"
        self.database = main_database()
        self.setting_handler = setting_handler()
        self.message_handler = message_handler()
        self.widgets_handler = widgets_handler()
        self.state_handler = state_handler()
        self.logging = Logging()	
        settings_c = Settings()
        self.host = settings_c.get_setting("main", "hostname")
        self.port = settings_c.get_setting("main", "port")
        self.enable_screen_control = settings_c.get_setting("main", "enable_screen_control")
        self.openhab_host = settings_c.get_setting("main", "openhab_ip")
        self.openhab_port = settings_c.get_setting("main", "openhab_port")
        
    def get_page(self, request):
        pagelist = request["page"]
        dataget = request["data_get"]
        page = []
        lowerpage = [0]
        if len(pagelist) > 3:
            lowerpage = pagelist[3:]
            subsubpage = pagelist[2]
            subpage = pagelist[1]
        elif len(pagelist) > 2:
            subsubpage = pagelist[2]
            subpage = pagelist[1]
        elif len(pagelist) > 1:
            subpage = pagelist[1]
            subsubpage = "none"
        else:
            subsubpage = "none"
            subpage = "none"
        pagename = pagelist[0]
        
        if pagename == "main":
            self.logging.info("Loading main page: "+subpage+"/"+subsubpage, location=self.name)
            if self.message_handler.get_popup_flag() and subpage != "reload":
                self.message_handler.del_popup_flag()
            self.state_handler.toggle_screen(state = True)
            self.state_handler.refresh_screensaver()
            return self.create_main_page()
        elif pagename == "maindiv":
            self.logging.info("Loading main div: "+subpage+"/"+subsubpage, location=self.name)
            ##turn on screen
            if subpage != "screensaver":
                self.state_handler.toggle_screen(state=True)
            if not "reload" in pagelist and not "screensaver" in pagelist:
                ##enable popup of message when there is a new message
                self.message_handler.del_popup_flag()
                self.state_handler.refresh_screensaver()
                if subpage not in ["none", "popup", "", "reload", "screensaver"]:
                    self.state_handler.refresh_screensaver_subpage()
            else:
                self.logging.info("Not refreshing screensaver", location=self.name)
            if subpage in ["none", "popup", "", "reload", "screensaver"]:
                return self.create_main_div()
            elif subpage == "settings":
                return self.create_settings_page(subpage = subsubpage)
            elif subpage == "messages":
                return self.create_messages_page()
            else:
                if subsubpage == "reload":
                    subsubpage = 0
                if lowerpage[0] == "reload":
                    lowerpage = [0]
                return self.create_subpage(subpage, subsubpage, lowerpage[0])
        elif pagename == "popup": ##this is a popup widget
            self.logging.write("Loading popup div: "+subpage+"/"+subsubpage, level=2, location=self.name)
            if not "reload" in pagelist and not "screensaver" in pagelist:
                self.state_handler.toggle_screen(state = True)
                self.state_handler.refresh_screensaver_subpage()
            page = self.widgets_handler.create_mainpage_popup(subpage, subsubpage)
            if page == "generic_button_page":
                return self.create_subpage(subpage, 0, subsubpage, True)
            elif page == "widget not in sitemap":
                return "widget not in sitemap"
            else:
                return page
        elif pagename in ["clock", "black"]:
            cl = self.setting_handler.get_setting("clock_type")
            return render_template("clock.html", data = { "type_clock": cl })
        elif pagename == "photoframe":
            return self.create_photoframe()
        
        pagestr = ""
        for i in range(len(page)):
            pagestr = pagestr + page[i] + "\n"
        return pagestr
        
        
    def read_file(self, filename):
        PATH=os.path.dirname(os.path.abspath(__file__))
        with open(PATH + "/../" + filename) as f:
            content = f.readlines()
        content = [x.strip() for x in content]
        return content
        
    def create_main_page(self):
        page_data = {}
        page_data["host"] = [self.host, self.port]
        settings_c = Settings()
        page_data["mouse"] = self.setting_handler.get_setting("mouse")
        page_data["event_reload"] = settings_c.get_setting("page", "event_check_reload")
        page_data["page_reload"] = settings_c.get_setting("page", "page_reload")
        page_data["enable_album"] = settings_c.get_setting("main", "enable_album")
        if settings_c.get_setting("main", "enable_album") == "1":
            page_data["album_display_time"] = self.setting_handler.get_setting("frame_display_time")
        return render_template("main.html", data = page_data)
    
    def create_main_div(self):
        ml = self.openhab.get_items("items_left")[0]
        page_data_ml = self.format_items_frontpage("items_left", ml)
        main_left = render_template("maindiv_half.html", data = page_data_ml)
        
        mr = self.openhab.get_items("items_right")[0]
        page_data_mr = self.format_items_frontpage("items_right", mr)
        main_right = render_template("maindiv_half.html", data = page_data_mr)
        
        page_data = {}
        page_data["bottom"] = self.openhab.get_pages("b_")
        page = render_template("maindiv.html", data = page_data)
        
        
        page = page.replace("[[MAINLEFT]]", main_left)
        page = page.replace("[[MAINRIGHT]]", main_right)
        
        for item in page_data_ml:
            if item["group"][1:] == "rows":
                page = page.replace("[[%s]]" %item["label"].upper(), self.widgets_handler.render_widget("items_left", item["label_c"]))
        
        for item in page_data_mr:
            if item["group"][1:] == "rows":
                page = page.replace("[[%s]]" %item["label"].upper(), self.widgets_handler.render_widget("items_right", item["label_c"]))
        return self.add_bottom_bar(page)
       
    def format_items_frontpage(self, name, itemdata):
        while len(itemdata) < 10:
            itemdata.append( { "label": "", "state": "", "type": "text", "id": "", "icon": "static/pictures/black.png" } )
        data = []
        row = 1
        item = 0
        while row < 6:
            itemdata[item].update( { "onclick": "" } )
            itemtype = self.widgets_handler.check_widget_type(itemdata[item]["label"])
            if itemtype == "menu_button":  ##this is a menu button
                itemdata[item].update( { "onclick": "reload_main_div('page/maindiv/"+name+"/0/"+itemdata[item]["label"]+"')" } )
                data.append(itemdata[item])
                data[-1]["group"] = "menu_popup"
                data[-1]["label"] = self.widgets_handler.get_widget_label(itemdata[item]["label"])
                if data[-1]["state"] != "":
                    data[-1]["label"] = data[-1]["state"]
                item += 1
                data[-1]["fontsize"] = self.determine_text_size(data[-1]["label"], max_len = 13, start_font = "xlargefont")
            elif itemtype == "menu_popup":  ##this is a menu button
                itemdata[item].update( { "onclick": "frontpage_action('"+name+"', '"+itemdata[item]["label"]+"')" } )
                data.append(itemdata[item])
                data[-1]["group"] = "menu_popup"
                data[-1]["label"] = self.widgets_handler.get_widget_label(itemdata[item]["label"])
                if data[-1]["state"] != "":
                    data[-1]["label"] = data[-1]["state"]
                item += 1
                data[-1]["fontsize"] = self.determine_text_size(data[-1]["label"], max_len = 13, start_font = "xlargefont")
            elif itemtype[0:6] == "widget" and row < 6-int(itemtype[7:8])+1: ##special item takes 3 rows              
                data.append(itemdata[item])
                data[-1]["group"] = itemtype[7:8]+"rows"
                data[-1]["label_c"] = itemdata[item]["label"]
                data[-1]["label"] = self.widgets_handler.get_widget_label(itemdata[item]["label"]).upper()
                item += 1
                row += int(itemtype[7:8])-1
            elif itemtype[0:6] == "widget": ## skip this item
                item += 1
                row -= 1
            else:
                col = 0
                data.append( { "data": [0, 0], "group": "cols" } )
                while col < 2:
                    itemtype = self.widgets_handler.check_widget_type(itemdata[item]["label"])
                    if itemdata[item]["type"] == "Text":
                        data[-1]["data"][col] = itemdata[item]
                        data[-1]["data"][col]["group"] = "text"
                        item += 1
                    elif itemtype in ["menu_button", "menu_popup"] or itemtype[0:6] == "widget":  ##two columns needed for this type
                        data[-1]["data"][col] = { "label": "", "state": "", "type": "text" } 
                        data[-1]["data"][col]["group"] = "empty"
                    else:
                        itemdata[item].update( { "onclick": "item_action('"+itemdata[item]["type"]+"', '"+itemdata[item]["id"]+"', 'main')" } )
                        data[-1]["data"][col] = itemdata[item]
                        data[-1]["data"][col]["group"] = "popup"
                        item += 1
                    col += 1
                if data[-1]["data"][1]["group"] != "empty":
                    if data[-1]["data"][1]["label"] == "" or (data[-1]["data"][1]["label"] == "Empty" and data[-1]["data"][1]["state"] == "Empty"):
                        d = data[-1]["data"][0]
                        d.update({ "group": "wide_text" })
                        data[-1] = d
                        data[-1]["fontsize"] = self.determine_text_size(data[-1]["state"], max_len = 16)
                    else:
                        for i in [0,1]:
                            data[-1]["data"][i]["fontsize"] = self.determine_text_size(data[-1]["data"][i]["state"])
                else:
                    d = data[-1]["data"][0]
                    d.update({ "group": "wide_text" })
                    data[-1] = d
                    data[-1]["fontsize"] = self.determine_text_size(data[-1]["state"], max_len = 16)
                    
            row += 1
        return data
                
    def create_subpage(self, page, subpage=0, lowerpage = 0, handle_as_popup = False ):
        data = self.openhab.get_items(page, lowerpage)
        if subpage == "none":
            subpage = 0
        else:
            subpage = int(subpage)
        items = data[0]
        page_data = data[1]
        if page_data[1] != "temperature" and page_data[1] != "temp" and page_data[0].find("sensor") == -1:
            N_items_pp = self.setting_handler.get_setting("items_per_page")
            sensor_page = False
        else:
            N_items_pp = self.setting_handler.get_setting("sensors_per_page")
            if N_items_pp == 12:
                sensor_page = False
            else:
                sensor_page = True
        if handle_as_popup:
            N_items_pp = self.setting_handler.get_setting("items_per_page")
            if int(N_items_pp) < 9:
                N_items_pp = 6
            else:
                N_items_pp = 9
        page_format = self.__get_page_data__(len(items), N_items_pp, sensor_page = sensor_page)
        page_format.update( { "title": self.widgets_handler.get_widget_label(page_data[0]), "returnbutton": False, "linkback": "", "linknext": "", "showbacknext": True } )
        if handle_as_popup:
            sensor_page = False
            page_format["showbacknext"] = False
        if str(lowerpage) != "0" and str(lowerpage)[0:2] != "m_":
            d = self.openhab.get_items(page)
            pos = 0
            for i in range(len(d[0])):
                b = d[0][i]
                if b["type"] == "Frame" and b["label"] == lowerpage:
                    pos = i
            page_format["returnbutton"] = "%s/%d" %(page, int(pos/N_items_pp))
        if subpage != 0: 
            page_format["linkback"] = str(page)+"/" + str(int(subpage)-1)+"/"+str(lowerpage)
        if subpage < page_format["n_pages"]-1:
            page_format["linknext"] = str(page)+"/" + str(int(subpage)+1)+"/"+str(lowerpage)
        offset = subpage*N_items_pp
        page = render_template("subpage.html", data = page_format)
        n = 0
        ##iterator
        for row in range(page_format["n_rows"]):
            for col in range(page_format["n_cols"]):
                if n+offset < len(items) and (items[n+offset]["name"] != "Empty" and items[n+offset]["state"] != "Empty" and items[n+offset]["label"] != "Empty"):
                    button = self.create_item_button(items[n+offset], page_format["small_icon"], sensor_page)
                else:
                    button = ""
                page = page.replace("[[button_"+str(n)+"]]", button)
                n += 1
        if handle_as_popup:
            page += render_template("popups/generic.html")
            return page
        else:
            return self.add_bottom_bar(page, returnbutton = page_format["returnbutton"] )
                       
    def create_settings_page(self, subpage = 0):
        settings = sorted(self.setting_handler.get_settings())
        n = { 'linkback': "", 'linknext': "", 'n': len(settings) }
        try:
            subpage = int(subpage)
        except:
            subpage = 0
        if subpage != 0: 
            n["linkback"] = subpage-1
        if subpage < np.ceil(len(settings)/12)-1:
            n["linknext"] = subpage+1
        if subpage != 0:
            settings = settings[12*subpage:]
        n['n'] = len(settings)
        return self.add_bottom_bar(render_template("settings.html", data = settings, n = n))
 
    def create_messages_page(self, start = 0):
        page = render_template("messages.html")
        page = page.replace("[[LIST]]", self.message_handler.format_message_list(start = start))
        page = page.replace("[[MESSAGE]]", self.message_handler.format_message(message_id = -1))
        return self.add_bottom_bar(page)
        
    def add_bottom_bar(self, page, returnbutton = False):
        page_format = { "bottom": self.openhab.get_pages("b_") }
        page_format["returnbutton"] = returnbutton
        page_format["habpanel_link"] = Settings().get_setting("main", "habpanel_link")
        page += "\n\n\n"
        page += render_template("bottombar.html", data = page_format)
        return page
    
    def __get_page_data__(self, n_items, n_perpage, sensor_page = False):
        n_page = np.ceil(n_items / n_perpage)
        small_icon = False
        page_format = { "n_pages": n_page, "n_rows": 2, "n_cols": 3, "row_height": "50", "col_width": "33", "small_icon": False }
        if n_perpage == 8 and not sensor_page:
            page_format.update( { "n_rows": 4, "n_cols": 2, "row_height": "25", "col_width": "50", "small_icon": True } )
        elif n_perpage == 8 and sensor_page:
            page_format.update( { "n_rows": 2, "n_cols": 4, "row_height": "50", "col_width": "25" } )
        elif n_perpage == 9:
            page_format.update( { "n_rows": 3, "n_cols": 3, "row_height": "33", "col_width": "33" } )
        elif n_perpage == 12:
            page_format.update( { "n_rows": 4, "n_cols": 3, "row_height": "25", "col_width": "33" } )
        return page_format
            
    def create_item_button(self, item_info, small_icon = False, sensor_button = False, header = True):
        if not sensor_button:
            N_items_pp = self.setting_handler.get_setting("items_per_page")
            button_width = int(self.__get_page_data__(1, N_items_pp, sensor_button)["col_width"])
        else:
            N_items_pp = self.setting_handler.get_setting("sensors_per_page")
            button_width = int(float(self.__get_page_data__(1, N_items_pp, sensor_button)["col_width"])*1.2)
        
        data = { "icon": item_info["icon"], "icon_width": 90, "icon_height": 60, "action_id": item_info["id"], "header": header }
        if small_icon:
            data.update( { "icon_width": 70, "icon_height": 70 } )
        data.update( { "onclick": "item_action('"+item_info["type"]+"', '"+item_info["id"]+"')" } )
        if item_info["type"] == "Frame":
            data.update( { "onclick": "reload_main_div('/page/maindiv/" + str(item_info["page"]) +"/0/"+ str(item_info["subpage"]) +"')", "text_width": 80 } )
        ##
        if item_info["type"] == "Switch":
            data.update( { "text": self.format_string(item_info["label"], int(20*(button_width/100))), "state": item_info["state"].lower(), "text_width": 60, "state_width": 20 } )
            data.update( { "type": "switch" } )
        elif item_info["type"] == "Switch_single":
            data.update( { "text": self.format_string(item_info["label"], int(20*(button_width/100))), "state": item_info["state"].lower(), "text_width": 60, "state_width": 20 } )
        elif item_info["type"] == "Colorpicker":  ##openhab item type
            data.update( { "text": self.format_string(item_info["label"], int(20*(button_width/100))), "state": item_info["state"], "text_width": 60, "state_width": 20 } )
            data.update( { "type": "Colorpicker" } )
        else:
            data.update( self.format_item_string(item_info["label"], item_info["state"], button_width) )
            data.update( { "type": "state" } )
        #print(data)
        if sensor_button:
            data.update( { "text_width": 70, "state_width": 70, "icon_width": 80 } )
            page = render_template("buttons/sensor.html", data = data)
        else:
            page = render_template("buttons/button.html", data = data)
        return page
        
    def create_popup(self, type, data, renew_screensaver = True):
        if renew_screensaver:
            self.state_handler.refresh_screensaver_subpage()
        page = render_template("popups/"+type+".html", data = data)
        return page

    def create_photoframe(self):
        td = self.setting_handler.get_setting("frame_td")
        info = self.setting_handler.get_setting("frame_info")
        page_data = { "time": "none", "date": "none", "load": "none", "album": "none" }
        if td == "clock" or td == "both":
            page_data["time"] = ""
        if td == "date" or td == "both":			
            page_data["date"] = ""	
        if info == "load" or info == "both":		
            page_data["load"] = ""
        if info == "album" or info == "both":
            page_data["album"] = ""
        return render_template("album.html", data = page_data)
        
    def format_item_string(self, text, state, button_width = 50):
        if text == "_":
            return { "text": self.format_string(state, width=int(54*(button_width/100))), "state": "", "text_width": 80, "state_width": 0 }
        elif state == "" and len(text) < 25:
            return { "text": text, "state": "", "text_width": 80, "state_width": 0 }
        elif state == "":
            return { "text": self.format_string(text, width=int(32*(button_width/100))), "state": "", "text_width": 80, "state_width": 0 }
        elif len(text) < 13 and len(state) > 7:
            return { "text": text, "state": self.format_string(state, width=int(26*(button_width/100))), "text_width": 40, "state_width": 40 }
        elif len(text)> 20 and len(state) > 20:
            return { "text": self.format_string(text, width=int(26*(button_width/100))), "state": self.format_string(state, width=int(26*(button_width/100))), "text_width": 40, "state_width": 40 }
        else:
            return { "text": self.format_string(text, width=int(38*(button_width/100))), "state": self.format_string(state, width=int(14*(button_width/100))), "text_width": 40, "state_width": 40 }
        
    def format_string(self, string, width=27):
        position = 0
        for i in range(3):
            if len(string[position:]) > width:
                a = self.find(string[position:], " ")
                found = False
                for pos in range(len(a)):
                    val = a[len(a)-pos-1]
                    if val < 27 and not found:
                        string = string[0:position+val] + "<br>" + string[position+val+1:]
                        position = val + position + 4
                        found = True
        return Markup(string)
            
    def find(self, s, ch):
        return [i for i, ltr in enumerate(s) if ltr == ch]
		
    def determine_text_size(self, text, max_len = 7, start_font = "largefont"):
        if text == text.upper():
            max_len -= 1
        if start_font == "largefont":
            if len(text) < max_len+1:
                return "largefont"
            else:
                return "smallfont"
        else:
            if len(text) < max_len+1:
                return "xlargefont"
            else:
                return "smallfont"
			
