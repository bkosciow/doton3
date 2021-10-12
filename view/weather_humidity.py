from kivy.uix.stencilview import StencilView
from kivy.lang import Builder
import pathlib

Builder.load_file(str(pathlib.Path(__file__).parent.absolute()) + pathlib.os.sep + 'weather_humidity.kv')


class WeatherHumidity(StencilView):
    pass
