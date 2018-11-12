##default widget
from logger import Logging

class widget():
    
    def __init__(self):
        self._logging = Logging()
        pass

    def get_data(self, item_data):
        return item_data
