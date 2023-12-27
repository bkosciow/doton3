from service.widget import FreshData
import time
from kivy.logger import Logger


class FreshDataChecker:
    def __init__(self):
        self.widgets = []

    def add(self, widget):
        if isinstance(widget, FreshData):
            self.widgets.append(widget)
            Logger.info("Adding: " + str(widget.__class__))
        else:
            Logger.info("Skipping: " + str(widget.__class__))

    def add_from_listener(self, listener):
        for name in listener.widgets:
            for item in listener.widgets[name]:
                self.add(item)

    def check(self, dt):
        for item in self.widgets:
            if item.is_data_fresh and item.last_tick + item.data_ttl < time.time():
                Logger.warning("No data for: " + str(item))
                item.disable_widget()
