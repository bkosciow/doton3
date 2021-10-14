from kivy.uix.stacklayout import StackLayout
from kivy.lang import Builder
import pathlib
from service.widget import Widget
from pprint import pprint
from datetime import datetime, timedelta
import random

Builder.load_file(str(pathlib.Path(__file__).parent.absolute()) + pathlib.os.sep + 'weather3.kv')


class Weather(Widget, StackLayout):
    forecast_days = [0, 1, 2, 3]

    def update_values(self, values, name):
        print(values, name)
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
            # {'clouds': 88,
            #  'humidity': 78,
            #  'pressure': 1018,
            #  'temperature_max': 11.46,
            #  'temperature_min': 6.19,
            #  'weather': 'light rain',
            #  'weather_id': 500,
            #  'wind_deg': 227,
            #  'wind_speed': 5.15}

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

    def _normalize_values(self, values):
        for name in values:
            if isinstance(values[name], float):
                values[name] = round(values[name])
            if name == 'wind_deg':
                values[name] = abs(360-values[name])

        return values
