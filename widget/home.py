from kivy.uix.stacklayout import StackLayout
from kivy.lang import Builder
import pathlib
from service.widget import Widget

Builder.load_file(str(pathlib.Path(__file__).parent.absolute()) + pathlib.os.sep + 'home.kv')


class Home(Widget, StackLayout):
    def update_values(self, values, name):
        for room in self.supported_rooms(name):
            # print(room.node_names)
            self.update_room_values(room, values)

        self.update_powers_sockets(name, values)

    def update_room_values(self, room, values):
        if 'temp' in values or 'humi' in values:
            room.text = (values['temp'] if 'temp' in values else '--') + "\n" + \
                       (values['humi'] if 'humi' in values else '--')
        if "light" in values:
            room.light = int(values['light'])
        if "pir" in values:
            room.movement = int(values['pir'])

    def update_powers_sockets(self, name, values):
        if "relay" in values:
            idx = 0
            for v in values['relay']:
                power_socket_name = name + "-relay-" + str(idx)
                if power_socket_name in self.ids:
                    self.ids[power_socket_name].enabled = int(v)
                idx += 1

    def supported_rooms(self, name):
        for widget_name in self.ids:
            item = self.ids[widget_name]
            if hasattr(item, 'node_names') and name in item.node_names:
                yield item

