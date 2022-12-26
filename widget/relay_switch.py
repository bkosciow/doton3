from kivy.uix.stacklayout import StackLayout
from service.widget import Widget
from kivy.lang import Builder
from kivy.uix.gridlayout import GridLayout
from service.widget import Action
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
        self.ids['device_name'].text = self.text

    def update_values(self, values, name):
        self.ids['device_name'].disabled = False
        if 'relay' in values:
            if values['relay'][self.channel] == 0:
                self.state = 'down'
            else:
                self.state = 'normal'

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            if self.state == 'normal':
                state = 'down'
            else:
                state = 'normal'

            message = {
                'parameters': {
                    'channel': self.channel
                },
                'targets': [self.node_name],
                'event': "channel.off" if state == 'down' else "channel.on"
            }
            self.state = state
            self.ids['device_name'].disabled = True
            comm.send(message)
