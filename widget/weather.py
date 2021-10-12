from kivy.uix.stacklayout import StackLayout
from kivy.lang import Builder
import pathlib
from service.widget import Widget

Builder.load_file(str(pathlib.Path(__file__).parent.absolute()) + pathlib.os.sep + 'weather3.kv')


class Weather(Widget, StackLayout):
    def update_values(self, values, name):
        print(values, name)
