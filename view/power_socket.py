from kivy.uix.label import Label
from kivy.lang import Builder
import pathlib
from service.widget import Action
import service.comm as comm

Builder.load_file(str(pathlib.Path(__file__).parent.absolute()) + pathlib.os.sep + 'power_socket.kv')


class PowerSocket(Label, Action):
    def action(self, touch):
        message = {
            'parameters': {
                'channel': 0
            },
            'targets': [self.node_name],
            'event': "channel.off" if self.enabled == 1 else "channel.on"
        }
        comm.send(message)
