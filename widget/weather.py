from kivy.uix.stacklayout import StackLayout
from kivy.lang import Builder
import pathlib
from service.widget import Widget
from pprint import pprint
from datetime import datetime, timedelta

Builder.load_file(str(pathlib.Path(__file__).parent.absolute()) + pathlib.os.sep + 'weather3.kv')


class Weather(Widget, StackLayout):
    forecast_days = [0, 1, 2]

    def update_values(self, values, name):
        print(values, name)
        if 'current' in values and values['current'] is not None:
            normalized_values = self._normalize_values(values['current'])
            self.ids['current_wind_icon'].angle = normalized_values['wind_deg']
            self.ids['current_wind_label'].text = str(normalized_values['wind_speed'])
            self.ids['current_cloudiness'].value = normalized_values['clouds']
            self.ids['current_humidity'].value = normalized_values['humidity']
            self.ids['current_icon'].remove_from_cache()
            self.ids['current_icon'].source = 'assets/image/openweather/' + str(normalized_values['weather_id']) + '.png'
            self.ids['current_icon'].reload()
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
                    pass
                    # normalized_values = self._normalize_values(values['forecast'][date])
                    # pprint(normalized_values)
                    # pprint(values['forecast'][date])

    def _normalize_values(self, values):
        for name in values:
            if isinstance(values[name], float):
                values[name] = round(values[name])
            if name == 'wind_deg':
                values[name] = abs(360-values[name])

        return values
