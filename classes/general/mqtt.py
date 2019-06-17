from singleton import Singleton
from logger import Logging
import paho.mqtt.client as mqtt_cl
from settings import Settings
import ast

class mqtt(Singleton):
    
    def __init__(self):
        try:
            if self.loadingdone:
                pass
        except:
            self.loadingdone = True
            self.started = True
            self.logging = Logging()
            self.name = "mqtt"
            self.settings_c = Settings()
            try:
                self.server = self.settings_c.get_setting("mqtt", "server")
                self.port = int(self.settings_c.get_setting("mqtt", "port"))
                self.timeout = int(self.settings_c.get_setting("mqtt", "timeout"))
            except Exception as e:
                self.logging.error("Configuration not correct, check settings", location=self.name)
            self.listeners = []
            self.client = mqtt_cl.Client()
            self.client.on_connect = self.on_connect
            self.client.on_message = self.on_message
            self.client.connect(self.server, self.port, self.timeout)
            self.client.loop_start()
            self.logging.info("Connected to mqtt broker at: " + self.server, location=self.name)
            
    
    def on_connect(self, client, userdata, flags, rc):
        self.logging.info("Resubscribing for all listeners at " + self.server, location=self.name)
        for listen in self.listeners:
            self.client.subscribe(listen[0])
        
    def on_message(self, client, userdata, msg):
        self.logging.info("Received message: "+ msg.topic+" "+str(msg.payload), location=self.name)
        if self.started:
            for listen in self.listeners:
                topic = listen[0][0:-1]
                if msg.topic.find(topic) != -1:
                    self.logging.debug("Topic match for %s at %s" %(listen[1].get_name(), listen[0]), location=self.name)
                    try:
                        data = ast.literal_eval(msg.payload.decode("utf-8"))
                    except:
                        data = msg.payload.decode("utf-8")
                    try:
                        p = getattr(listen[1], listen[2])
                        p(msg.topic, data)
                    except Exception as e:
                        self.logging.error("Error executing: " + str(e), location=self.name)
        
    def add_listener(self, topic, class_item, functionname):
        self.listeners.append([topic, class_item, functionname])
        self.client.subscribe(topic)
        try:
            name = class_item.get_name()
        except:
            name = "unknown"
        self.logging.info("Added listener for %s at %s" %(name, topic), location=self.name)
        
    def publish(self, topic, payload):
        self.logging.info("Publish %s, %s " %(topic, str(payload)), location=self.name)
        self.client.publish(topic, payload)
