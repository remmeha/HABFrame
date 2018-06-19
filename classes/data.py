

import settings
from settings import Singleton
from logger import Logging
import pickle
from pathlib import Path
import time
import datetime
import hashlib
from math import ceil
import os

class main_database(Singleton):

    def __init__(self):
        try:
            if self.loadingdone:
                pass
        except:
            self.loadingdone = True
            settings_c = settings.Settings()
            self.logging = Logging()
            self.data_location = settings_c.get_setting("data", "location")
            PATH = os.path.dirname(os.path.abspath(__file__))
            self.datafile = PATH + "/../" + self.data_location + "/main_db.pckl"
            my_file = Path(self.datafile)
            if not my_file.is_file():
                self.logging.write("Creating database", level=1)
                self.data = { "last_saved" : time.time() , "settings" : {} , "messages" : [] }
                self.data["settings"]["main_page"] = 0
                self.data["settings"]["items_per_page"] = 0
                self.data["settings"]["sensors_per_page"] = 0
                self.data["settings"]["screen_timeout"] = 1
                self.data["settings"]["album_timeout"] = 0
                self.data["settings"]["message_timeout"] = 0
                self.data["settings"]["mouse"] = 0
                self.data["settings"]["screen"] = 0
                self.data["settings"]["frame"] = 0
                self.data["settings"]["frame_info"] = 0
                self.data["settings"]["frame_td"] = 0
                self.data["settings"]["frame_display_time"] = 0
                self.data["settings"]["toast_timeout"] = 0
                self.data["settings"]["clock_type"] = 0
                self.data["settings"]["chart_period"] = 0
                self.data["settings"]["first_run_messages_flag"] = False
                self.data["messages"] = []
                self.save_datafile()
            self.data = self.load_datafile()
                
    def load_datafile(self):
        return pickle.load( open( self.datafile, "rb" ) )

    def save_datafile(self):
        self.data["last_saved"] = time.time()
        self.logging.write("Saving database", level=2)
        pickle.dump( self.data, open( self.datafile, "wb" ) )


