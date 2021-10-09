from kivy.uix.stacklayout import StackLayout
from kivy.lang import Builder
import pathlib

Builder.load_file(str(pathlib.Path(__file__).parent.absolute()) + pathlib.os.sep + 'home.kv')


class Home(StackLayout):
    def update_values(self, values, name):
        name = name.replace("node-", "")
        print(values, name)
        if name in self.ids:
            self.ids[name].text = values['temp'] + "\n" + values['humi']
            if "light" in values:
                self.ids[name].light = int(values['light'])
            if "pir" in values:
                self.ids[name].movement = int(values['pir'])

