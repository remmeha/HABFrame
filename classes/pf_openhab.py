##openhab communication

from settings import Settings
from logger import Logging
from settings import Singleton
import urllib3
import os
import colorsys
from resizeimage import resizeimage
from PIL import Image
import requests
import datetime
from io import BytesIO
from dateutil.relativedelta import relativedelta

class pf_openhab(Singleton):
	
    def __init__(self):
        try:
            if self.loadingdone:
                pass
        except:
            self.loadingdone = True
            self.logging = Logging()
            settings_c = Settings()
            self.openhab_server = settings_c.get_setting("main", "openhab_ip")
            self.openhab_port = settings_c.get_setting("main", "openhab_port")
            self.host = settings_c.get_setting("main", "hostname") 
            self.port = settings_c.get_setting("main", "port")                
            self.sitemap_name = settings_c.get_setting("main", "sitemap")
            self.sitemap_name = "main" if self.sitemap_name == None else self.sitemap_name
            self.resize_icons = settings_c.get_setting("main", "resize_icons")	
            self.iconh = 64
            self.iconw = 64	
            self.name = "pf_openhab"
            self.http = urllib3.PoolManager()   	
                
    def get_pages(self, filter):
        self.load_sitemap()
        data = []
        n = 0
        for i in range(len(self.sitemap["homepage"]["widgets"][0]["widgets"])):
            key = self.sitemap["homepage"]["widgets"][0]["widgets"][i]
            if key["label"].find(filter) != -1:
                icon_url = "/item/icon/" + key["icon"] + ".png"
                data.append({ "label": key["label"], "icon": icon_url, "id": n})
            n += 1
        return data
        
    def get_page(self, name):
        for i in range(len(self.sitemap["homepage"]["widgets"][0]["widgets"])):
            key = self.sitemap["homepage"]["widgets"][0]["widgets"][i]
            if key["label"] == name:
                return key
        
    def get_items(self, pagename, subpage="none", subsubpage = 0):
        self.load_sitemap()
        page = self.get_page(pagename)
        data = []
        n_subp = 1
        n = 0
        page_type = [page["label"], page["icon"]] 
        for key in page["linkedPage"]["widgets"]:
            n+=1
            item = self.convert_item_data(key)
            item["id"] = item["name"] + "__" + pagename + "__" + str(subpage) + "__" + str(n)
            if subpage == "none" or str(subpage) == "0":
                if item["type"] == "Frame":
                    item["page"] = pagename
                    item["subpage"] = item["label"]
                data.append(item)
            elif item["type"] == "Frame" and item["label"] == subpage:
                page_type[0] = page_type[0] + " / " + key["label"] 
                sub_n = 0
                for k in key["widgets"]:
                    sub_n += 1
                    item = self.convert_item_data(k)
                    item["id"] = item["name"] + "__" + pagename + "__" + str(subpage) + "__" + str(sub_n)
                    if item["type"] == "Frame":
                        item["type"] = "Text"
                    data.append(item)
        return [data, page_type]
               
    def load_sitemap(self):
        if self.host == None or self.openhab_server == None:
        #if self.openhab_server == None:
            data = self.load_error_sitemap(False)
        else:
            try:
                url = "http://" + self.openhab_server + ":" + self.openhab_port + "/rest/sitemaps/" + self.sitemap_name
                #print(url)
                content = self.http.request('GET', url)
                data = content.data.decode("utf-8")
            except:
                self.logging.error("Error connecting to openHAB server, please check settings", location=self.name)
                data = self.load_error_sitemap(True)
        data = data.replace("true", "True").replace("false", "False")
        data = eval(data)
        self.sitemap = data
    
    def load_error_sitemap(self, exception):
        PATH = os.path.dirname(os.path.abspath(__file__))
        errorfile = PATH + "/files/error_sitemap.txt"
        with open(errorfile, 'r') as f:
            data = f.read()
        if exception:
            data = data.replace("{{HOST_CONFIG_ERROR}}", "No error detected")
            data = data.replace("{{OPENHAB_CONFIG_ERROR}}", "Error connecting to server, check settings")
        else:
            data = data.replace("{{HOST_CONFIG_ERROR}}", "Check settings")
            data = data.replace("{{OPENHAB_CONFIG_ERROR}}", "Check settings")
        data = data.replace("{{IP}}", str(self.openhab_server))
        data = data.replace("{{PORT}}", str(self.openhab_port))
        data = data.replace("{{SITEMAP}}", str(self.sitemap_name))
        data = data.replace("{{RESIZE}}", str(self.resize_icons))
        data = data.replace("{{HOST_IP}}", str(self.host))
        data = data.replace("{{HOST_PORT}}", str(self.port))
        return data
        
    def get_item(self, item_name):
        name, pagename, subpage, n = self.split_item_name(item_name)
        #print(name, pagename, subpage, n)
        item = self.get_item_data(name, pagename, subpage, n)
        self.logging.debug("Item from get_item: " +str(item), location=self.name)
        return item
        
        
    def get_item_data(self, item_name, pagename, subpage, n):
        #search for the item
        self.load_sitemap()
        #print("Name: " + item_name)
        o = 1
        subpage_o = 1
        for i in range(len(self.sitemap["homepage"]["widgets"][0]["widgets"])):
            if self.sitemap["homepage"]["widgets"][0]["widgets"][i]["label"] == pagename:
                for key in self.sitemap["homepage"]["widgets"][0]["widgets"][i]["linkedPage"]["widgets"]:
                    if key["label"].find("[") != -1:
                        comp_label = key["label"][0:key["label"].find("[")]
                        while comp_label[-1:] == " ":
                            comp_label = comp_label[0:-1]
                    else:
                        comp_label = key["label"]
                    try:
                        if key["type"] == "Frame" and (str(subpage_o) == subpage or comp_label == subpage):
                            #print(subpage)
                            sub_o = 0
                            for k in key["widgets"]:
                                sub_o += 1
                                try: 
                                    if k["item"]["name"] == item_name and sub_o == n:
                                        item = self.convert_item_data(k)
                                        item["id"] = item["name"] + "__" + pagename + "__" + str(subpage) + "__" + str(n)
                                        item["page"] = pagename
                                        item["subpage"] = str(subpage)
                                        self.logging.debug("Item found, id: " + item["id"], location=self.name)
                                        return item
                                except Exception as e:
                                    self.logging.warn("Invalid item found in sitemap 2 %s" %(str(e)), location=self.name)
                        elif "item" in key and  key["item"]["name"] == item_name and o == n:
                            item = self.convert_item_data(key)
                            item["id"] = item["name"] + "__" + pagename + "__" + str(subpage) + "__" + str(n)
                            item["page"] = pagename
                            item["subpage"] = str(subpage)
                            self.logging.debug("Item found, id: " + item["id"], location=self.name)
                            return item
                        elif str(subpage) == "0" or subpage == "none":
                            o += 1
                        elif key["type"] == "Frame":
                            subpage_o += 1
                            o += 1
                    except Exception as e:
                        self.logging.warn("Invalid item found in sitemap 1: %s, %s" %(str(key), str(e)), location=self.name)
                    
    def convert_item_data(self, key):
        #print(key)
        item_data = { "icon": key["icon"], "type": key["type"], "name": key["label"], "state": "" }
        if "item" in key:
            item_data.update( { "state": key["item"]["state"], "link": key["item"]["link"], "name": key["item"]["name"] } )
            if key["item"]["state"] != "" and key["item"]["state"].find(" ") == -1:
                item_data["icon"] = key["icon"] + "-" + key["item"]["state"]
            if "transformedState" in key["item"]:
                transformedState = key["item"]["transformedState"]
                if len(str(transformedState)) < 15:
                    item_data.update( { "icon": key["icon"] + "-" + transformedState } )
            if "mappings" in key:
                item_data.update( { "mappings": key["mappings"] } )
        if "label" in key:
            item_data.update( { "label": key["label"] } )
        
        #### correct icon for state
        try:
            state = float(item_data["state"])
            if state < 0.0:
                item_data["icon"] = key["icon"] + "-" + str(-1*state+100) 
        except:
            if item_data["state"] == "NULL":
                item_data["state"] = "OFF"
                item_data["icon"] = key["icon"] + "-off"
            elif len(str(item_data["state"])) > 15:
                item_data["icon"] = key["icon"]
        
        #### transform state name
        if item_data["label"].find("[") != -1:
            label = item_data["label"][0:item_data["label"].find("[")]
            while label[-1:] == " ":
                label = label[0:-1]
            state = item_data["label"][item_data["label"].find("[")+1:item_data["label"].find("]")]
            item_data.update( { "state": state, "label": label } )
            
        if key["type"] == "Colorpicker":
            if item_data["state"].lower() != "off":
                item_data["state"] = self.convert_color_to_rgb(item_data["state"])
                item_data["icon"] = key["icon"] + "-on"
            if len(item_data["state"].split(",")) > 2:
                if item_data["state"].split(",")[2] == "0" or item_data["state"].split(",")[2] == "0.0":
                    item_data.update({"state": "off", "icon": key["icon"] + "-off" } )
        elif key["type"] == "Selection":
            item_state = ""
            if len(key["mappings"]) == 1:
                item_data["type"] = "Switch_single"
                item_state = key["mappings"][0]["label"]
            for mapp in key["mappings"]:
                if mapp["command"] == item_data["state"]:
                    ## mappings are like [ displayed state, actual state ]
                    item_state = mapp["label"]
            try:
                ##why is this?????
                #print(item_state)
                int(item_state)
                item_data.update( { "item_state": item_data["label"] } )
                item_data.update( { "label": "_" } )
            except:
                item_data.update({"state": item_state } )
        elif key["type"] == "Setpoint":
            try: 
                step = round(float(key["step"]), 1)
                if int(step) == step:
                    step = int(step)
                item_data.update( { "setpoint": [int(key["minValue"]), int(key["maxValue"]),step] } )
            except:
                pass  
        elif key["type"] == "Slider":
            item_data.update( { "setpoint": [0, 100, 10] } )
        
        ##update the icon to the right url:
        if self.resize_icons == "1":
            item_data["icon"] = "/item/icon/" + item_data["icon"] + ".png"
        else:
            item_data["icon"] = "http://"+self.openhab_server + ":" + self.openhab_port + "/icon/" + item_data["icon"] + ".png"
                    
        return item_data
        
        
    def set_state(self, item_name, state):
        item, pagename, subpage, n = self.split_item_name(item_name)
        if state[0:5] == "Color":
            state = self.convert_color_to_hsv(state[5:])
        #cmd = "curl --header \"Content-Type: text/plain\" --request POST --data \"" + state+ "\" " + self.openhab_server + ":" + self.openhab_port + "/rest/items/" + item
        url = "http://" + self.openhab_server + ":" + self.openhab_port + "/rest/items/" + item
        requests.post(url, data=state)
        self.logging.info("Put state openhab: " + url + " " + str(state), location="openhab")
        #os.system(cmd)
        #print(cmd)
        self.load_sitemap()
        return self.get_item(item_name)
        
        
    def get_mappings(self, item_name, occurrence = 1):
        ##self.load_sitemap()
        item = self.get_item(item_name)
        mappings = []
        for mapping in item["mappings"]:
            mappings.append([mapping["label"], mapping["command"]])
        return mappings
        
    def convert_color_to_rgb(self, color):
        if color == "":
            color = "0.0,0.0,0"
        color = color.split(",")
        color = colorsys.hsv_to_rgb(float(color[0])/360, float(color[1])/100, float(color[2])/100)
        red = hex(int(color[0]*255))[2:]
        if len(red) < 2:
            red = "0"+red
        blue = hex(int(color[1]*255))[2:]
        if len(blue) < 2:
            blue = "0"+blue
        green = hex(int(color[2]*255))[2:]
        if len(green) < 2:
            green = "0"+green
        return "#" + red + blue + green

    def convert_color_to_hsv(self, color):		
        color = colorsys.rgb_to_hsv(float(int("0x"+color[0:2],0))/255.0, float(int("0x"+color[2:4],0))/255.0, float(int("0x"+color[4:6],0))/255.0)
        return str(color[0]*360) + "," + str(color[1]*100) + "," + str(color[2]*100)
        
    def get_icon(self, name):
        URL = "http://"+self.openhab_server + ":" + self.openhab_port + "/icon/" + name
        response = requests.get(URL)
        with Image.open(BytesIO(response.content)) as image:
            imgByteArr = BytesIO()
            cover = Image.Image.resize(image, [self.iconh, self.iconw])
            cover.save(imgByteArr, image.format)
        return imgByteArr.getvalue()
        
    def get_chart_data(self, item, period):
        try:
            p = int(period[0:len(period)-1])
        except:
            p = 1
        if period[-1:] == "D":
            dt = datetime.datetime.now() - datetime.timedelta(days=p)
        elif period[-1:] == "H":
            p += 1
            dt = datetime.datetime.now() - datetime.timedelta(hours=p)
        elif period[-1:] == "W":
            dt = datetime.datetime.now() - datetime.timedelta(weeks=p)
        elif period[-1:] == "M":
            dt = datetime.datetime.now() - relativedelta(months=p)
        start = dt.strftime("%Y-%m-%dT%H:%M:%S.000+01:00")
        self.logging.info("Starting date for data: "+start, location="openhab")
        start = start.replace("+", "%2B").replace(":", "%3A") 
        name, pagename, subpage, n = self.split_item_name(item)      
        URL = "http://"+self.openhab_server + ":" + self.openhab_port + "/rest/persistence/items/"+name+"?serviceId=rrd4j&starttime=" + start
        response = requests.get(URL)
        ## get item info
        i = self.get_item(item)
        if i == None:
            return None
        else:
            if i["icon"].lower().find("temp") != -1:
                typ = "temp"
            elif i["icon"].lower().find("humi") != -1:
                typ = "humi"
            elif i["icon"].lower().find("press") != -1:
                typ = "pres"
            elif i["icon"].lower().find("energy") != -1:
                typ = "watt"
            else:
                typ = "value"
        return { "data": response.content, "type": typ }
        
    def split_item_name(self, item_name):
        a = item_name.split("__")
        if len(a) > 1:
            name = a[0]
            pagename = a[1]
            subpage = a[2]
            n = int(a[3])
        else:
            return item_name
        return name, pagename, subpage, n
