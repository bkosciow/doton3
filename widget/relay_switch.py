from kivy.uix.stacklayout import StackLayout
from service.widget import Widget
from kivy.lang import Builder
from kivy.uix.gridlayout import GridLayout
import pathlib
import service.comm as comm

Builder.load_file(str(pathlib.Path(__file__).parent.absolute()) + pathlib.os.sep + 'relay_switch.kv')


class RelaySwitch(Widget, StackLayout):
    def __init__(self, **kwargs):
        self.node_name = kwargs['node_name']
        self.channel = kwargs['channel']
        self.text = ''
        self.skip_broadcast = False
        if 'text' in kwargs:
            self.text = kwargs['text']
            del(kwargs['text'])
        del(kwargs['node_name'])
        del(kwargs['channel'])
        super(StackLayout, self).__init__(**kwargs)
        self.ids['activator'].bind(state=self.on_state)
        self.ids['device_name'].text = self.text

    def update_values(self, values, name):
        if 'relay' in values:
            self.skip_broadcast = True
            if values['relay'][self.channel] == 0:
                self.ids['activator'].state = 'down'
            else:
                self.ids['activator'].state = 'normal'
            self.skip_broadcast = False

    def on_state(self, widget, value):
        message = {
            'parameters': {
                'channel': self.channel
            },
            'targets': [self.node_name],
            'event': "channel.off" if value == 'down' else "channel.on"
        }
        if not self.skip_broadcast:
            comm.send(message)

