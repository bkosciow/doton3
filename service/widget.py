"""An abstract for Widget class"""
import abc


class Widget():
    @abc.abstractmethod
    def update_values(self, values, name):
        """change a value, values is a dict [name] = value"""
        pass


class Action():
    """Interface for action widget"""
    @abc.abstractmethod
    def action(self, touch):
        """action for touch"""
        return
