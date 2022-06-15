from kivy.uix.label import Label
from kivy.lang import Builder
import pathlib

Builder.load_file(str(pathlib.Path(__file__).parent.absolute()) + pathlib.os.sep + 'power_socket.kv')


class PowerSocket(Label):
    pass
