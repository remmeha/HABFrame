from settings import Singleton
from logger import Logging
import time
import datetime
import gc

class task_scheduler(Singleton):
	
    def __init__(self):
        try:
            if self.loadingdone:
                pass
        except:
            self.loadingdone = True
            self.logging = Logging()
            self.scheduled_tasks = []
            self.add_task(self.logging, "log_rotate", (time.time()+4*60*60), period=24*60*60)
            
    def check_tasks(self):
        self.logging.write("Checking tasks, running scheduler", level=6, location="tasks")
        cur_time = time.time()
        length = len(self.scheduled_tasks)
        for h in range(length):
            try:
                i = length-h-1  ##reverse iteration
                task = self.scheduled_tasks[i]
                if cur_time > task[2]:  ##task[2] == next_time
                    class_name = task[0].get_name()
                    try:
                        item_name = task[0].get_item().get_name()
                        self.logging.write("Executing task: " + class_name + "." + task[1] + " for item: "+item_name, level='info', location="tasks")
                    except:
                        self.logging.write("Executing task: " + class_name + "." + task[1], level='info', location="tasks")
                    try:
                        getattr(task[0], task[1])()
                    except Exception as e: 
                        self.logging.write("Processing task failed: " + str(e), level = "error", location="tasks")
                        self.logging.write("Could not execute task: " + class_name + "." + task[1], level="error", location="tasks")
                    if task[3] == 0 and task[4] == 0:
                        del self.scheduled_tasks[i]
                    elif task[3] != 0:
                        task[3] = task[3] - 1 ##repeat n times
                        task[2] = cur_time + task[4] ## add period for next time
                        timestamp = datetime.datetime.fromtimestamp(task[2]).strftime('%c')
                        self.logging.write("Repeating task: " + class_name + "." + task[1] + " scheduled at " + str(timestamp), level=2, location="tasks")
                    elif task[4] != 0:
                        task[2] = cur_time + task[4] ## add period for next time
                        timestamp = datetime.datetime.fromtimestamp(task[2]).strftime('%c')
                        self.logging.write("Repeating task: " + class_name + "." + task[1] + " scheduled at " + str(timestamp), level=4, location="tasks")
                    else:
                        ##delete task anyway
                        del self.scheduled_tasks[i]
                    gc.collect()
            except Exception as e:
                self.logging.write("Could not handle task in list: "+str(e), level="error", location="tasks")
        
    def add_task(self, class_item, functionname, next_time, repeat=0, period=0):
        self.scheduled_tasks.append([class_item, functionname, next_time, repeat, period])
        task = self.scheduled_tasks[-1]
        class_name = task[0].get_name()
        timestamp = datetime.datetime.fromtimestamp(next_time).strftime('%c')
        self.logging.write("Added task: " + class_name + "." + task[1] + " scheduled at " + str(timestamp), level='info', location="tasks")

    def list_tasks(self):
        self.logging.write("Listing tasks: " + str(len(self.scheduled_tasks)) + " tasks active", level='info', location="tasks")
        tasks = []
        for i in range(len(self.scheduled_tasks)):
            try:
                task = self.scheduled_tasks[i]
                class_name = task[0].get_name()
                timestamp = datetime.datetime.fromtimestamp(task[2]).strftime('%c')
                try:
                    item_name = task[0].get_item().get_name()
                    if len(item_name) > 20:
                        item_name = item_name[0:19]
                    task_string = (class_name + "." + task[1]).ljust(25) + " for item: "+(item_name).ljust(20)+" scheduled at: " + str(timestamp)
                    tasks.append([class_name + "." + task[1], str(timestamp), item_name])
                except:
                    task_string = (class_name + "." + task[1]).ljust(56) + " scheduled at: " + str(timestamp)
                    tasks.append([class_name + "." + task[1], str(timestamp)])
                self.logging.write(("Task "+str(i+1)+": ").ljust(9) + task_string, level='debug', location="tasks")
            except:
                pass
        return tasks

    def delete_tasks(self):
        self.logging.write("Deleting tasks: " + str(len(self.scheduled_tasks)) + " tasks active", level="warning", location="tasks")
        self.scheduled_tasks = []
        self.add_task(self.logging, "log_rotate", (time.time()+4*60*60), period=24*60*60)	
