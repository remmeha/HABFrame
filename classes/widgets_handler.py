
from flask import render_template
from flask import Markup
from pf_openhab import pf_openhab
import page_handler
import time, datetime
import wunderground as wg
from logger import Logging
from settings import Settings
import os
from pathlib import Path

class widgets_handler:
    
    def __init__(self):
        self.openhab = pf_openhab()
        self.logging = Logging()
        self.name = "widget_handler" 
        PATH=os.path.dirname(os.path.abspath(__file__))
        self.template_dir = PATH + "/../templates/"       
    
    def render_widget(self, page, lowerpage):
        w_info = self.get_widget_info(lowerpage, main_page = page)
        
        data = self.openhab.get_items(page, lowerpage)
        item_data = self.render_item_data_for_widget(data[0])
        
        if w_info["name"] in ["weather_wg", "weather_wg_small"]:
            item_data = self.get_weather()
            if "error" in item_data:
                return render_template("error.html", data = item_data )
        elif w_info["name"].find( "media" ) != -1:
            try:
                item_data.update(self.render_media_widget_data(item_data))
            except Exception as e:
                self.logging.error("Error creating widget %s" %str(e), location=self.name)
                er = self.render_widget_error(e, lowerpage)  
                return render_template("error.html", data = { "error": str(er) })
            
        item_data["gen_name"] = w_info["name"]
        item_data["pagename"] = page
        try:
            self.logging.debug("Rendering widget: %s" %w_info["template"], location=self.name)
            return render_template("widgets/%s.html" %w_info["template"].lower(), data = item_data)
        except Exception as e:
            self.logging.error("Error creating widget %s" %str(e), location=self.name)
            er = self.render_widget_error(e, lowerpage)  
            return render_template("error.html", data = { "error": str(er) })
        
    
    def create_mainpage_popup(self, page, subpage):
        data = self.openhab.get_items(page, subpage)
        item_data = self.render_item_data_for_widget(data[0])
        if len(item_data) == 0:
            return "widget not in sitemap"
        info = self.get_widget_info(subpage, main_page = page)
        if info["name"] in ["weather_wg", "weather_wg_small"]:
            item_data = self.get_weather()
            if "error" in item_data:
                return render_template("popups/error.html", data = item_data )
        elif info["name"].find( "media" ) != -1:
            try:
                item_data.update(self.render_media_widget_data(item_data))
            except Exception as e:
                self.logging.error("Error creating widget %s" %str(e), location=self.name)
                er = self.render_widget_error(e, subpage)  
                return render_template("popups/error.html", data = { "error": str(er) })
        
        item_data["page_name"] = page
        item_data["widget_name"] = subpage
        
        if info == None:
            return render_template("popups/error.html", data = { "error": "Popup widget template for %s does not exist" %subpage.lower() } )
        elif info["template"] == "generic_button_page":
            return info["template"]
        else:
            try:
                self.logging.debug("Rendering popup widget: %s" %info["template"], location=self.name)
                return render_template("popup_widgets/"+info["template"]+".html", data = item_data)
            except Exception as e:
                self.logging.error("Error creating popup widget %s" %str(e), location=self.name)
                er = self.render_widget_error(e, subpage)  
                return render_template("popups/error.html", data = { "error": str(er) })
    
    def check_widget_type(self, name):
        if name[0:2] == "m_":
            return "menu_button"
        if name[0:2] in ["a_", "c_", "d_"]:
            return "menu_popup"
        if name[0:2] == "s_":
            info = self.get_widget_info(name)
            return "widget_"+str(info["rows"])
        else:
            return name
        
    def get_widget_label(self, name):
        if name.find("[") != -1 and name.find("]") != -1:
            name = name[name.find("[")+1:name.find("]")]
            return name
        for n in [ "m_", "a_", "b_", "c_", "d_"]:
            if name.find(n) != -1:
                return name[name.find(n)+2:]
        i = self.get_widget_info(name)
        if i == None:
            return name
        else:
            return i["name"]
        
    
    def get_widget_info(self, name, main_page = "none"):
        ##  s_  frontpage widget with possible popup widget
        ##  a_  generic button page (with large button on frontpage
        ##  b_  bottom page
        ##  c_  popup widget with button
        ##  d_  popup widget with button
        ##  m_  generic button linking to a page instead of popup
        widget_data = {}
        widget_data["a_"] = { "type": "popup_widget", "name": name[2:], "template": "generic_button_page" }
    
        if name[0:2] in widget_data:
            return widget_data[name[0:2]]
        else:
            ##try to find the info from the widget template
            data = "_"
            name_lower = name[2:].lower()
            if name[0:2] == "s_":  ##widget
                f_name = self.template_dir + "widgets/" + name_lower + ".html"
                if Path(f_name).is_file():
                    with open(f_name, 'r') as myfile:
                        data=myfile.read().replace('\n', '')
                    n = self.find_var(data, "Name")
                    rows = self.find_var(data, "Rows")
                    if rows != None and n != None:
                        return { "name": n, "rows": int(rows), "template": name_lower, "type": "frontpage_widget", "pagename": main_page }
            else:   ##popup
                f_name = self.template_dir + "popup_widgets/" + name_lower + ".html"
                if Path(f_name).is_file():
                    with open(f_name, 'r') as myfile:
                        data=myfile.read().replace('\n', '')
                    n = self.find_var(data, "Name")
                    if n != None:
                        return { "name": n, "template": name_lower, "type": "popup_widget", "pagename": main_page }          
            return None
    
    def find_var(self, data, var):
        if data.find(var+"=") != -1:
            pos = data.find(var+"=")
            pos2 = data[pos+5:].find("/")
            return data[pos+5:pos+5+pos2]
        else:
            return None
    
    def render_item_data_for_widget(self, data):
        d = {}
        for dat in data:
            dat["state_length"] = len(dat["state"])
            d[dat["label"].lower()] = dat
        return d
    
    def render_widget_error(self, e, w):
        e = str(e)
        if e.find("attribute") != -1:
            pos = e.find("attribute")
            n = e[pos+10:]
            return "Please add an item labeled %s to the widget named %s" %(n, str(w))
        else:
            return "Widget: " + str(w) + "  " + str(e)

    def get_weather(self):
        try:
            self.lm = wg.LocationManager()	
            settings_c = Settings()
            location = settings_c.get_setting("wunderground", "location")
            loc = self.lm.GetLocation(location)
            try:
                current = loc.read_current()
                forecast = loc.read_forecast()
                alerts = loc.read_alerts()
                if len(alerts) > 0:
                    current["alerts"] = alerts[0]["description"]
                    current["alerts_short"] = "Attention weather alerts!"
                else:
                    current["alerts"] = "No alerts"
                    current["alerts_short"] = ""
                return { "cw": current, "fw": forecast, "location": location }
            except:
                link = loc.link
                error = "Check WG location: %s" %(link)
        except Exception as e:
            error = "Check wunderground settings: %s" %str(e)
        self.logging.error(error, location=self.name)
        return { "error": error }

    def render_media_widget_data(self, d):
        if "endtime" not in d:
            raise Exception("attribute 'endtime'")
        for n in ["starttime", "endtime", "player", "media_state"]:
            if n not in d:
                raise Exception("attribute '%s'" %n)
        try:
            duration = float(d["endtime"]["state"]) - float(d["starttime"]["state"])
            now = time.time()*1000.0
            p = now - float(d["starttime"]["state"])
            progress = datetime.datetime.fromtimestamp(p/1000.0).strftime("%M:%S") + " / " + datetime.datetime.fromtimestamp(duration/1000.0).strftime("%M:%S")
            if duration > 10*60*1000:
                progress = progress + " (%.1f%%)" %(p/duration*100)
        except:
            if d["player"]['state'].lower() == "play":
                progress = "Playing"
            elif d["player"]['state'].lower() == "pause":
                progress = "Paused"
            else:
                progress = "-" 
            for state in ["Playing", "Stopped", "Paused"]:
                if d['media_state']['state'].lower().find(state) != -1:
                    progress = state
        d['media_state']['state'] = d['media_state']['state'].replace("playing", "").replace("grouped", "").replace(":", "")
        d["time"] = { "now": time.time()*1000 }
        d["progress"] = progress
        return d
    
