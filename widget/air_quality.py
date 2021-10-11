from kivy.uix.stacklayout import StackLayout
from kivy.lang import Builder
import pathlib
from service.widget import Widget

Builder.load_file(str(pathlib.Path(__file__).parent.absolute()) + pathlib.os.sep + 'air_quality.kv')


class AirQuality(Widget, StackLayout):
    def __init__(self, **kwargs):
        self.group = kwargs['group'] if 'group' in kwargs else None
        if self.group:
            del(kwargs['group'])
        super(StackLayout, self).__init__(**kwargs)

    def update_values(self, values, name):
        print(values, name)
        current = {
            'PM25': None,
            'PM10': None,
            'O3': None,
            'SO2': None,
            'CO': None,
            'NO2': None,
        }
        for location in values:
            if self.group is None or location in self.group:
                data = values[location]
                if isinstance(data, dict):
                    for item in data:
                        if data[item] is not None:
                            if item in current and (
                                    current[item] is None or current[item] < data[item]['index']):
                                current[item] = data[item]['index']

        for k, v in current.items():
            name = k.lower()
            for i in range(0, 6):
                if v is not None and i <= v:
                    self.ids[name + "_" + str(i)].enabled = 1
                else:
                    self.ids[name + "_" + str(i)].enabled = 0
