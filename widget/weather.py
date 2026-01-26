from kivy.uix.stacklayout import StackLayout
from kivy.lang import Builder
import pathlib
from service.widget import Widget
from datetime import datetime, timedelta
from service.widget import FreshData

Builder.load_file(str(pathlib.Path(__file__).parent.absolute()) + pathlib.os.sep + 'weather3.kv')


class Weather(Widget, StackLayout, FreshData):
    forecast_days = [0, 1, 2, 3]

    def __init__(self, **kwargs):
        super(StackLayout, self).__init__(**kwargs)
        super(FreshData, self).__init__()
        self.data_ttl = 60*10
        self.selected_city = '3103402'
        self.data = {}

    def update_values(self, values, name):
        # print(values, name)
        if values:
            self.data = values
            self.draw()

    def draw(self):
        if self.selected_city in self.data:
            values = self.data[self.selected_city]
            # print(values['city'])
            self.ids['city_name_label'].text = values['city']
            if 'current' in values and values['current'] is not None:
                normalized_values = self._normalize_values(values['current'])
                self.ids['current_wind_icon'].angle = normalized_values['wind_deg']
                self.ids['current_wind_label'].text = str(normalized_values['wind_speed'])
                self.ids['current_cloudiness'].value = normalized_values['clouds']
                self.ids['current_humidity'].value = normalized_values['humidity']
                source = 'assets/image/openweather/' + str(normalized_values['weather_id']) + '.png'
                if self.ids['current_icon'].source != source:
                    self.ids['current_icon'].source = source
                self.ids['current_temperature'].text = str(normalized_values['temperature_current'])

            if 'forecast' in values and values['forecast'] is not None:
                today = datetime.today()
                for offset in self.forecast_days:
                    date = today + timedelta(days=offset)
                    date = date.strftime('%Y-%m-%d')
                    if date in values['forecast']:
                        base_id = "day" + str(offset)
                        normalized_values = self._normalize_values(values['forecast'][date])
                        source = 'assets/image/openweather/' + str(normalized_values['weather_id']) + '.png'
                        if self.ids[base_id + '_icon'].source != source:
                            self.ids[base_id + '_icon'].source = source
                        if base_id + "_wind_icon" in self.ids:
                            self.ids[base_id + "_wind_icon"].angle = normalized_values['wind_deg']
                        if base_id + "_wind_label" in self.ids:
                            self.ids[base_id + "_wind_label"].text = str(normalized_values['wind_speed'])
                        if base_id + "_cloudiness" in self.ids:
                            self.ids[base_id + "_cloudiness"].value = normalized_values['clouds']
                        if base_id + "_humidity" in self.ids:
                            self.ids[base_id + "_humidity"].value = normalized_values['humidity']
                        if base_id + "_temperature_max" in self.ids:
                            self.ids[base_id + "_temperature_max"].text = str(normalized_values['temperature_max'])
                        if base_id + "_temperature_min" in self.ids:
                            self.ids[base_id + "_temperature_min"].text = str(normalized_values['temperature_min'])
            self.got_data()

    def _normalize_values(self, values):
        for name in values:
            if isinstance(values[name], float):
                values[name] = round(values[name])
            if name == 'wind_deg':
                values[name] = abs(360-values[name])

        return values

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            current_city = self.selected_city
            cities = list(self.data.keys())
            try:
                current_index = cities.index(current_city)
            except ValueError:
                current_index = -1

            next_index = (current_index + 1) % len(cities)

            self.selected_city = str(cities[next_index])
            self.draw()
