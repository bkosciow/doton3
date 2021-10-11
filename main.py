import kivy
import random

from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.stencilview import StencilView
from kivy.clock import Clock
from kivy.properties import ObjectProperty
from kivy.uix.stacklayout import StackLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from service.config import Config
from connector.listener import Listener
import service.comm as comm
from view.label_border import LabelBorder
from view.air_indicator import AirIndicator
from view.image_rotate import ImageRotate
from view.weather_cloudiness import WeatherCloudiness
from widget.home import Home
from widget.air_quality import AirQuality
from widget.weather import Weather
from service.exceptions import *

config = Config()
comm.address = (config.get("message.ip"), int(config.get("message.port")))
listener = Listener(config.get('grpc.address'))


# class ImageCloud(StencilView):
#     pass

class DotonApp(App):
    def build(self):
        layout = FloatLayout(size=(800, 480))

        home = Home(pos=(490, 280))
        # air_quality = AirQuality(pos=(0, 250), group=['Bielsko-Biała, ul.Partyzantów'])
        air_quality = AirQuality(pos=(0, 350))
        weather = Weather()

        layout.add_widget(home)
        layout.add_widget(air_quality)
        layout.add_widget(weather)

        listener.add_widget('node-kitchen', home)
        listener.add_widget('node-living', home)
        listener.add_widget('node-north', home)

        listener.add_widget('openaq', air_quality)

        listener.start()

        return layout
        # Clock.schedule_interval(home.update, 5.0)

    def on_request_close(self, *args):
        print("HALTING")
        listener.stop()
        listener.join()
        return True


if __name__ == '__main__':
    DotonApp().run()



