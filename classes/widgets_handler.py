from flask import render_template
from flask import Markup
from pf_openhab import pf_openhab
import page_handler
import time, datetime
from logger import Logging
from settings import Settings
import os, sys
from pathlib import Path

PATH=os.path.dirname(os.path.abspath(__file__))
sys.path.append(PATH + "/widgets")

class widgets_handler:
    
    def __init__(self):
        self.openhab = pf_openhab()
        self.logging = Logging()
        self.name = "widget_handler" 
        PATH=os.path.dirname(os.path.abspath(__file__))
        self.template_dir = PATH + "/../templates/" 
        self.imported_widget_classes = {}      
    
    def render_widget(self, page, lowerpage):
        w_info = self.get_widget_info(lowerpage, main_page = page)
        
        data = self.openhab.get_items(page, lowerpage)
        item_data = self.render_item_data_for_widget(data[0])
        
        try:
            item_data = self.get_widget_data(w_info, item_data)
            if "error" in item_data:
                return render_template("error.html", data = item_data )
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
        
    
    def create_mainpage_popup(self, page, subpage, menuwidget = False):
        data = self.openhab.get_items(page, subpage)
        item_data = self.render_item_data_for_widget(data[0])
        if len(item_data) == 0:
            #return "widget not in sitemap"
            self.logging.error("Widget is not in sitemap", location=self.name)
            er = self.render_widget_error("cannot find widget in sitemap", subpage)  
            return render_template("popups/error.html", data = { "error": str(er) })
        info = self.get_widget_info(subpage, main_page = page)
        try:
            item_data = self.get_widget_data(info, item_data)
            if "error" in item_data:
                return render_template("popups/error.html", data = item_data )
        except Exception as e:
            self.logging.error("Error creating widget %s" %str(e), location=self.name)
            er = self.render_widget_error(e, subpage)  
            if menuwidget:
                return render_template("popups/error.html", data = { "error": str(er) }), "Error"
            else:
                return render_template("popups/error.html", data = { "error": str(er) })
            
        item_data["page_name"] = page
        item_data["widget_name"] = subpage
        item_data["menuwidget"] = menuwidget
        if info == None:
            return render_template("popups/error.html", data = { "error": "Popup widget template for %s does not exist" %subpage.lower() } )
        elif info["template"] == "generic_button_page":
            return info["template"]
        else:
            try:
                self.logging.debug("Rendering popup widget: %s" %info["template"], location=self.name)
                data = render_template("popup_widgets/"+info["template"]+".html", data = item_data)
                if menuwidget:
                    title = self.find_var(data, "Title")
                    if title == None:
                        title = ""
                    return data, title
                else:
                    return data
            except Exception as e:
                self.logging.error("Error creating popup widget %s" %str(e), location=self.name)
                er = self.render_widget_error(e, subpage) 
                if menuwidget: 
                    return render_template("popups/error.html", data = { "error": str(er) }), "Error"
                else:
                    return render_template("popups/error.html", data = { "error": str(er) })
                
    def get_widget_data(self, w_info, item_data):
        if w_info["name"] not in self.imported_widget_classes:
            try:
                a = __import__(w_info["name"] + "_widget")
                self.imported_widget_classes[w_info["name"]] = getattr(a, w_info["name"] + "_widget")()
            except Exception as e:
                self.logging.warn("Could not create widget %s" %str(e), location=self.name)
                self.logging.warn("Could not create widget %s" %str(w_info["name"]), location=self.name)
                self.logging.warn("Importing normal widget", location=self.name)
                a = __import__("widget")
                self.imported_widget_classes[w_info["name"]] = a.widget()
        cl = self.imported_widget_classes[w_info["name"]]
        item_data = cl.get_data(item_data)
        return item_data
    
    def check_widget_type(self, name):
        if name[0:2] == "m_":
            return "menu_button"
        if name[0:2] in ["a_", "d_"]:
            return "menu_popup"
        if name[0:2] in ["c_"]:
            return "menuwidget"
        if name[0:2] in ["b_"]:
            return "button"
        if name[0:2] == "s_":
            info = self.get_widget_info(name)
            return "widget_"+str(info["rows"])
        else:
            return name
        
    def get_widget_label(self, name):
        for n in ["b_"]:
            if name.find(n) != -1:
                return name[name.find(n)+2:]
        if name.find("[") != -1 and name.find("]") != -1:
            name = name[name.find("[")+1:name.find("]")]
            return name
        for n in [ "m_", "a_", "b_", "c_", "d_"]:
            if name.find("/ " + n) != -1:
                return name[name.find("/ "+n)+4:]
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
                    title = self.find_var(data, "Title")
                    if rows != None and n != None:
                        return { "title": title, "name": n, "rows": int(rows), "template": name_lower, "type": "frontpage_widget", "pagename": main_page }
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
            pos2 = data[pos+len(var)+1:].find("/")
            return data[pos+len(var)+1:pos+len(var)+1+pos2]
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
    
