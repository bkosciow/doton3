"""An abstract for Widget class"""
import abc
import time
import time


class Widget:
    @abc.abstractmethod
    def update_values(self, values, name):
        """change a value, values is a dict [name] = value"""
        pass


class Action:
    """Interface for action widget"""
    @abc.abstractmethod
    def action(self, touch):
        """action for touch"""
        return


class FreshData:
    def __init__(self):
        self.is_data_fresh = True
        self.data_ttl = 60*10
        self.last_tick = time.time()

    def got_data(self):
        self.last_tick = time.time()
        if not self.is_data_fresh:
            self.enable_widget()

    def disable_widget(self):
        self.is_data_fresh = False
        self.disabled = True

    def enable_widget(self):
        self.is_data_fresh = True
        self.disabled = False

    def is_fresh(self):
        if self.is_data_fresh and self.last_tick + self.data_ttl < time.time():
            return False

        return True
