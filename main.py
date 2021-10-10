import kivy
import random

from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.properties import ObjectProperty
from kivy.uix.stacklayout import StackLayout
from service.config import Config
from connector.listener import Listener
import service.comm as comm
from view.label_border import LabelBorder
from widget.home import Home
from service.exceptions import *

config = Config()
comm.address = (config.get("message.ip"), int(config.get("message.port")))
listener = Listener(config.get('grpc.address'))


class DotonApp(App):
    def build(self):
        home = Home(pos=(440, 250))
        listener.add_widget('node-kitchen', home)
        listener.add_widget('node-living', home)
        listener.add_widget('node-north', home)
        listener.start()
        # Clock.schedule_interval(home.update, 5.0)
        return home

    def on_request_close(self, *args):
        print("HALTING")
        listener.stop()
        listener.join()
        return True


if __name__ == '__main__':
    DotonApp().run()



