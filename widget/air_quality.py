from kivy.uix.stacklayout import StackLayout
from kivy.lang import Builder
import pathlib
from service.widget import Widget
from service.widget import FreshData

Builder.load_file(str(pathlib.Path(__file__).parent.absolute()) + pathlib.os.sep + 'air_quality.kv')


class AirQuality(Widget, StackLayout, FreshData):
    def __init__(self, **kwargs):
        self.group = kwargs['group'] if 'group' in kwargs else None
        if self.group:
            del(kwargs['group'])
        super(StackLayout, self).__init__(**kwargs)
        super(FreshData, self).__init__()
        self.data_ttl = 60*15
        self.selected_city = None
        self.data = {}

    def draw(self):
        if self.selected_city is None:
            return

        if self.selected_city in self.data:
            self.ids['city_name_label'].text = self.selected_city
            current = {
                'PM25': None,
                'PM10': None,
                'O3': None,
                'SO2': None,
                'CO': None,
                'NO2': None,
            }
            data = self.data[self.selected_city]
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

    def update_values(self, values, name):
        if values is not None:
            if self.selected_city is None:
                self.selected_city = list(values.keys())[0]
            self.data = self.data | values
            self.draw()

            self.got_data()

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            current_city = self.selected_city
            cities = [x for x in list(self.data.keys()) if x!='ts']
            if len(cities) == 0:
                return

            current_index = cities.index(current_city)
            next_index = current_index + 1
            if next_index >= len(cities):
                next_index = 0

            self.selected_city = str(cities[next_index])
            self.draw()
