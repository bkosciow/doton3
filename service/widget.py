"""An abstract for Widget class"""
import abc


class Widget:

    @abc.abstractmethod
    def update_values(self, values, name):
        """change a value, values is a dict [name] = value"""
        pass


class Clickable(metaclass=abc.ABCMeta):
    """Interface for clickable widget"""
    @abc.abstractmethod
    def action(self, name, pos_x, pos_y):
        """action for touch"""
        return
