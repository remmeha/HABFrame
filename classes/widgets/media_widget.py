from widget import widget
import time
import datetime

class media_widget(widget):
    
    def __init__(self):
        widget.__init__(self)
        
    def get_data(self, item_data):
        return self.render_media_widget_data(item_data)
        
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
        except Exception as e:
            self._logging.error("Exception in media widget: %s" %e, location="media_widget")
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
