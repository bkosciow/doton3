from kivy.uix.label import Label
from kivy.lang import Builder
import pathlib

Builder.load_file(str(pathlib.Path(__file__).parent.absolute()) + pathlib.os.sep + 'weather_temperature.kv')


class WeatherTemperature(Label):
    pass
