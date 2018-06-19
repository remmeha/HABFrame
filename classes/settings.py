import sys
import xml.etree.ElementTree as xml
import time
import datetime
import os
from singleton import Singleton

class Settings(Singleton):

    def __init__(self, settings_file="config/settings.xml"):
        PATH = os.path.dirname(os.path.abspath(__file__))
        self.file = PATH + "/../" + settings_file
        try:
            if self.doneloading: 
                pass
        except:
            self.doneloading = True
            from pathlib import Path
            if not Path(self.file).is_file():
                from shutil import copyfile
                copyfile(PATH + "/../config/settings_example.xml", self.file)
            self.settings = self.load_settings()

    def load_settings(self):	
        ##load settings from file
        set_xml = xml.parse(self.file).getroot()
        
        settings = {}
        for sub in set_xml:
            if sub.tag == 'protocol':
                settings["protocol"] = {}
                for subvar in sub:
                    settings["protocol"][subvar.tag] = {}
                    for subsubvar in subvar:
                        settings["protocol"][subvar.tag][subsubvar.tag] = subsubvar.text
            else:
                if sub.tag not in settings:
                    settings[sub.tag] = {}
                for subvar in sub:
                    settings[sub.tag][subvar.tag] = subvar.text

        #print("Done loading settings file: " + self.file)
        return settings

    def get_setting(self, setting_base, setting):
        return self.settings[setting_base][setting]

