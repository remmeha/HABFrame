import sys
import xml.etree.ElementTree as xml
import time
import datetime
import os
from singleton import Singleton
from settings import Settings

class Logging(Singleton):
	
    def __init__(self):
        try:
            if self.doneloading:
                pass
        except:
            self.__uptime__ = time.time()
            self.doneloading = True
            self.settings_c = Settings()
            self.logfile = self.settings_c.get_setting("logging", "log")
            self.errorlogfile = self.settings_c.get_setting("logging", "errorlog")
            self.eventlogfile = self.settings_c.get_setting("logging", "eventlog")
            level = self.settings_c.get_setting("logging", "level")
            self.loglevel = self.__convertLevel(level, return_type = "int")
            self.max_rotation = int(self.settings_c.get_setting("logging", "rotation"))
            self.log_db = []
            self.__empty()

    def write(self, text, level=1, location="main"):
        location = location.lower()
        write, level = self.__CheckLevel(level, location)	
        if write:
            self.__write(text, level, location=location)
            
    def info(self, text, location="unknown"):
        self.write(text, level="INFO", location = location)

    def debug(self, text, location="unknown"):
        self.write(text, level="DEBUG", location = location)
        
    def event(self, text, location="unknown"):
        self.write(text, level="EVENT", location = location)
        
    def error(self, text, location="unknown"):
        self.write(text, level="ERROR", location = location)
        
    def trace(self, text, location="unknown"):
        self.write(text, level="TRACE", location = location)
    
    def warn(self, text, location="unknown"):
        self.write(text, level="WARN", location = location)

    def get_name(self):
        return "Logging"
        
    def __write(self, text, level, location):
        self.log_db.append([time.time(), level, location, text])
        if len(self.log_db) > 5000:
            del self.log_db[0:2500]        
        if len(location) > 12:
            location = location[0:12]
        level2 = ("["+level +"]").ljust(8) + (" [" + location + "]").ljust(15)
        text = time.strftime('%c') + " " + level2 + " " + text
        ##leave uncommented for when running the server from shell
        print(text)
        self.__writefile(text, self.logfile)
        if level.lower() == "error" or level.lower() == "warn":
            self.__writefile(text, self.errorlogfile)
        if level.lower() == "event":
            self.__writefile(text, self.eventlogfile)
            
    def __writefile(self, text, filename, filehandle = 'a'):
        f = open(filename, filehandle)
        f.write(text + "\n")
        f.close()
        
    def __empty(self):
        self.__writefile("", self.logfile, 'w')
        self.write("Logging initiated", level="INFO", location="Logging")
        self.__writefile("", self.errorlogfile, 'w')
        self.write("Error Logging initiated", level="INFO", location="Logging")
        self.__writefile("", self.eventlogfile, 'w')
        self.write("Event Logging initiated", level="INFO", location="Logging")

    def getlogs(self, typelog, n = 10, filter="none"):
        logs = []
        ##print(n)
        for i in range(len(self.log_db)):
            if filter == "none" or self.log_db[i][2].find(filter) != -1 or self.log_db[i][3].find(filter) != -1:
                if typelog == self.log_db[i][1]:
                    logs.append([i, self.__convert_timestamp(self.log_db[i][0]), self.log_db[i][2], self.log_db[i][3]])
                elif typelog == "ew" and (self.log_db[i][1] == "error" or self.log_db[i][1] == "warning"):
                    logs.append([i, self.__convert_timestamp(self.log_db[i][0]), self.log_db[i][1], self.log_db[i][2], self.log_db[i][3]])
                elif typelog == "noew" and (self.log_db[i][1] != "error" and self.log_db[i][1] != "warning"):
                    logs.append([i, self.__convert_timestamp(self.log_db[i][0]), self.log_db[i][1], self.log_db[i][2], self.log_db[i][3]])
                elif typelog == "all":
                    logs.append([i, self.__convert_timestamp(self.log_db[i][0]), self.log_db[i][1], self.log_db[i][2], self.log_db[i][3]])
                else:
                    try:
                        if (int(typelog)+1) > int(self.log_db[i][1]):
                            logs.append([i, self.__convert_timestamp(self.log_db[i][0]), self.log_db[i][2]])
                    except:
                        pass
        if len(logs) > n:
            start = len(logs) - n
        else:
            start = 0
        ret_logs = []
        #print(len(logs))
        for i in range(start,len(logs)):
            ret_logs.append(logs[i])
        return ret_logs
        
    def __convert_timestamp(self, time):
        return datetime.datetime.fromtimestamp(time).strftime('%c')

    def log_rotate(self):
        ##rotate log
        if self.max_rotation < 3:
            self.max_rotation = 3
        if self.max_rotation > 10:
            self.max_rotation = 10
        for i in range(2,10):
            h = 10-i
            if os.path.isfile(self.logfile + "."+str(h)) and h <= self.max_rotation:
                os.system("mv " + self.logfile + "."+str(h) + " " + self.logfile + "."+str(h+1))
            elif os.path.isfile(self.logfile + "."+str(h)):
                os.system("rm " + self.logfile + "."+str(h))
            if os.path.isfile(self.errorlogfile + "."+str(h)) and h <= self.max_rotation:
                os.system("mv " + self.errorlogfile + "."+str(h) + " " + self.errorlogfile + "."+str(h+1))
            elif os.path.isfile(self.errorlogfile + "."+str(h)):
                os.system("rm " + self.errorlogfile + "."+str(h))
            if os.path.isfile(self.eventlogfile + "."+str(h)) and h <= self.max_rotation:
                os.system("mv " + self.eventlogfile + "."+str(h) + " " + self.eventlogfile + "."+str(h+1))
            elif os.path.isfile(self.eventlogfile + "."+str(h)):
                os.system("rm " + self.eventlogfile + "."+str(h))
                    
        os.system("mv " + self.logfile + " " + self.logfile + ".1")
        os.system("mv " + self.errorlogfile + " " + self.errorlogfile + ".1")
        os.system("mv " + self.eventlogfile + " " + self.eventlogfile + ".1")

    def __convertLevel(self, level, return_type = "other"):
        ## 0 == OFF
        ## 1 == ERROR
        ## 2 == INFO
        ## 3 == WARN(ING)
        ## 4 == DEBUG
        ## 5 == TRACE
        try:
            level = int(level)
            if return_type == "int":
                return level
            elif level == 0:
                return "OFF"
            elif level == 1:
                return "ERROR"
            elif level == 2:
                return "WARN"
            elif level == 3:
                return "EVENT"
            elif level == 4:
                return "INFO"
            elif level == 5:
                return "DEBUG"
            elif level == 6:
                return "TRACE"
            else:
                return "ERROR"
        except:
            if return_type == "string":
                return level
            if level.upper() == "OFF":
                return 0
            elif level.upper() == "ERROR":
                return 1
            elif level.upper() == "WARNING" or level.upper() == "WARN":
                return 2
            elif level.upper() == "EVENT":
                return 3
            elif level.upper() == "INFO":
                return 4
            elif level.upper() == "DEBUG":
                return 5
            elif level.upper() == "TRACE":
                return 6
            else:
                return 1
    
    def __CheckLevel(self, level, location):
        ## check loglevel and return string loglevel and write: true / false
        level = self.__convertLevel(level, return_type = "int")
        try:
            loglevel = self.settings_c.get_setting("logging", location)
            loglevel = self.__convertLevel(loglevel, return_type = "int")
        except:
            loglevel = self.loglevel
        if loglevel >= level:
            return True, self.__convertLevel(level)
        else:
            return False, "none"
