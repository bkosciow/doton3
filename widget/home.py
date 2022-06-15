from kivy.uix.stacklayout import StackLayout
from kivy.lang import Builder
import pathlib
from service.widget import Widget

Builder.load_file(str(pathlib.Path(__file__).parent.absolute()) + pathlib.os.sep + 'home.kv')


class Home(Widget, StackLayout):
    def update_values(self, values, name):
        name = name.replace("node-", "")
        # print(values, name)
        if name in self.ids:
            self.ids[name].text = (values['temp'] if 'temp' in values else '--') + "\n" + \
                   (values['humi'] if 'humi' in values else '--')
            if "light" in values:
                self.ids[name].light = int(values['light'])
            if "pir" in values:
                self.ids[name].movement = int(values['pir'])
            if "relay" in values:
                idx = 0
                for v in values['relay']:
                    name = "relay-" + name + "-" + str(idx)
                    if name in self.ids:
                        self.ids[name].enabled = int(v)
                    idx += 1
