from kivy.uix.stacklayout import StackLayout
from kivy.lang import Builder
import pathlib
from service.widget import Widget
from service.widget import FreshData

Builder.load_file(str(pathlib.Path(__file__).parent.absolute()) + pathlib.os.sep + 'home.kv')


class Home(Widget, StackLayout, FreshData):

    def __init__(self, **kwargs):
        super(StackLayout, self).__init__(**kwargs)
        super(FreshData, self).__init__()
        self.data_ttl = 20
        self.rooms_staled = []

    def update_values(self, values, name):
        for room in self.supported_rooms(name):
            self.update_room_values(room, values)

        self.update_powers_sockets(name, values)

    def update_room_values(self, room, values):
        data = False
        if 'temp' in values or 'humi' in values:
            room.text = (values['temp'] if 'temp' in values else '--') + "\n" + \
                       (values['humi'] if 'humi' in values else '--')
            data = True
        if "light" in values:
            room.light = int(values['light'])
            data = True
        if "pir" in values:
            room.movement = int(values['pir'])
            data = True

        if data:
            room.got_data()

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

    def is_fresh(self):
        self.rooms_staled = []
        for room in self.children:
            if not room.is_fresh():
                self.rooms_staled.append(room)

        if not self.rooms_staled:
            return True

        return False

    def disable_widget(self):
        for room in self.rooms_staled:
            room.disable_widget()
