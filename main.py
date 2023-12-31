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
from kivy.logger import Logger


config = Config()
comm.address = (config.get("message.ip"), int(config.get("message.port")))
listener = Listener(config.get('socket.address'))
data_checker = FreshDataChecker()

class DotonApp(App):
    def build(self):
        layout = FloatLayout(size=(800, 480))

        home = Home(pos=(490, 280))
        # air_quality = AirQuality(pos=(0, 250), group=['Bielsko-Biała, ul.Partyzantów'])
        air_quality = AirQuality(pos=(0, 350))
        weather = Weather(pos=(220, 290))

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
        # octo_cr6se = PrinterControl(pos=(565, 3), printer_name='CR6SE', node_name='cr6se')
        octo_e5plus = PrinterControl(pos=(685, 3), printer_name='E5Plus', node_name='ender5plus')

        upperLight = RelaySwitch(pos=(700, 170), text='top', node_name='node-printers', channel=3)
        lowerLight = RelaySwitch(pos=(610, 170), text='down', node_name='node-printers', channel=2)

        box2Light2 = RelaySwitch(pos=(520, 170), text='box', node_name='node-relaybox2', channel=1)

        # fake1 = Printer3D(pos=(0, 10), printer_name='FAKE1')

        pcmonitoring1 = PCMonitoring(pos=(0, 220), name="PC Hone")
        layout.add_widget(pcmonitoring1)

        layout.add_widget(home)
        layout.add_widget(air_quality)
        layout.add_widget(weather)
        layout.add_widget(lowerLight)
        layout.add_widget(upperLight)

        layout.add_widget(octo_e5pro)
        layout.add_widget(octo_e5plus)
        # layout.add_widget(octo_cr6se)

        layout.add_widget(box2Light2)

        listener.add_widget('node-kitchen', home)
        listener.add_widget('node-living', home)
        listener.add_widget('node-north', home)
        listener.add_widget('node-lib', home)
        listener.add_widget('node-corridor', home)
        listener.add_widget('node-toilet', home)
        listener.add_widget('node-printers', home)
        listener.add_widget('node-relaybox2', home)

        listener.add_widget('openweather', weather)
        listener.add_widget('openaq', air_quality)

        listener.add_widget('ender5pro', octo_e5pro)
        listener.add_widget('ender5plus', octo_e5plus)

        # listener.add_widget('3dprinters', octo_cr6se)

        listener.add_widget('node-printers', lowerLight)
        listener.add_widget('node-printers', upperLight)
        # listener.add_widget('node-printers', power5pro)
        # listener.add_widget('node-printers', powerCr6se)

        # listener.add_widget('node-relaybox2', power5plus)
        listener.add_widget('node-relaybox2', box2Light2)
        # listener.add_widget('node-fake1', fake1)

        listener.add_widget('pc-node', pcmonitoring1)
        listener.start()

        data_checker.add_from_listener(listener)
        Clock.schedule_interval(data_checker.check, 4)

        return layout

    def on_request_close(self, *args):
        Logger.info("Halting")
        listener.stop()
        listener.join()
        return True


if __name__ == '__main__':
    DotonApp().run()

