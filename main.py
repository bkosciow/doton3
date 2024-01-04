import kivy
import random
import signal
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
from socket_conn.listener import Listener
import service.comm as comm
from view.label_border import LabelBorder
from view.room import Room
from view.air_indicator import AirIndicator
from view.image_rotate import ImageRotate
from view.weather_cloudiness import WeatherCloudiness
from view.weather_humidity import WeatherHumidity
from view.weather_temperature import WeatherTemperature
from view.circular_progress_bar import CircularProgressBar
from view.power_socket import PowerSocket
from widget.pc_monitoring import PCMonitoring
from widget.home import Home
from widget.air_quality import AirQuality
from widget.weather import Weather
from widget.printer_3d import Printer3D
from widget.printer_control import PrinterControl
from widget.relay_switch import RelaySwitch
from service.exceptions import *
from service.fresh_data_checker import FreshDataChecker
from kivy.app import App
from kivy.core.window import Window
from kivy.logger import Logger


config = Config()
comm.address = (config.get("message.ip"), int(config.get("message.port")))
listener = Listener(config.get('socket.address'))
data_checker = FreshDataChecker()


def handler(signum, frame):
    Logger.info("Stopping")
    listener.stop()
    listener.join()
    App.get_running_app().stop()
    Window.close()
    exit(1)


signal.signal(signal.SIGINT, handler)


class DotonApp(App):

    widget_counter = 0
    initialized = False

    def on_start(self):
        Clock.schedule_interval(self.tick, 0.3)

    def step_0(self):
        octo_e5plus = PrinterControl(pos=(685, 3), printer_name='E5Plus', node_name='ender5plus')
        self.layout.add_widget(octo_e5plus)
        listener.add_widget('ender5plus', octo_e5plus)

    def step_1(self):
        air_quality = AirQuality(pos=(0, 350))
        self.layout.add_widget(air_quality)
        listener.add_widget('openaq', air_quality)

    def step_2(self):
        weather = Weather(pos=(220, 290))
        self.layout.add_widget(weather)
        listener.add_widget('openweather', weather)

    def step_3(self):
        home = Home(pos=(490, 280))
        self.layout.add_widget(home)
        listener.add_widget('node-kitchen', home)
        listener.add_widget('node-living', home)
        listener.add_widget('node-north', home)
        listener.add_widget('node-lib', home)
        listener.add_widget('node-corridor', home)
        listener.add_widget('node-toilet', home)
        listener.add_widget('node-printers', home)
        listener.add_widget('node-relaybox2', home)

    def step_4(self):
        upperLight = RelaySwitch(pos=(700, 170), text='top', node_name='node-printers', channel=3)
        self.layout.add_widget(upperLight)
        listener.add_widget('node-printers', upperLight)

        lowerLight = RelaySwitch(pos=(610, 170), text='down', node_name='node-printers', channel=2)
        self.layout.add_widget(lowerLight)
        listener.add_widget('node-printers', lowerLight)

        box2Light2 = RelaySwitch(pos=(520, 170), text='box', node_name='node-relaybox2', channel=1)
        self.layout.add_widget(box2Light2)
        listener.add_widget('node-relaybox2', box2Light2)

        pcmonitoring1 = PCMonitoring(pos=(0, 220), name="PC Hone")
        self.layout.add_widget(pcmonitoring1)
        listener.add_widget('pc-node', pcmonitoring1)

    def step_5(self):
        def completed_e5pro():
            message = {
                'parameters': {
                    'channel': 3,
                },
                'targets': ['node-relaybox2'],
                'event': "channel.off"
            }
            comm.send(message)

        octo_e5pro = PrinterControl(pos=(445, 3), printer_name='E5pro', node_name='ender5pro')
        octo_e5pro.add_callback('shutdown', completed_e5pro)
        self.layout.add_widget(octo_e5pro)
        listener.add_widget('ender5pro', octo_e5pro)

    def step_6(self):
        return
        octo_cr6se = PrinterControl(pos=(565, 3), printer_name='CR6SE', node_name='cr6se')
        self.layout.add_widget(octo_cr6se)
        listener.add_widget('cr6se', octo_cr6se)

    def tick(self, dt):
        if self.initialized:
            return

        name = "step_" + str(self.widget_counter)
        step = getattr(self, name, None)
        if step:
            Logger.info("Executing "+name)
            step()
        else:
            Logger.info("Starting listener ")
            listener.start()
            data_checker.add_from_listener(listener)
            self.initialized = True

        self.widget_counter += 1

    def build(self):
        self.layout = FloatLayout(size=(800, 480))

        Clock.schedule_interval(data_checker.check, 4)

        return self.layout

    def on_request_close(self, *args):
        listener.stop()
        listener.join()

        return True


if __name__ == '__main__':
    DotonApp().run()
