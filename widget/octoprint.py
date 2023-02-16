from kivy.uix.stacklayout import StackLayout
from kivy.lang import Builder
import pathlib
from service.widget import Widget
from datetime import datetime, timedelta

Builder.load_file(str(pathlib.Path(__file__).parent.absolute()) + pathlib.os.sep + 'octoprint.kv')


class Octoprint(Widget, StackLayout):
    def __init__(self, **kwargs):
        self.printer_name = kwargs['printer_name'] if 'printer_name' in kwargs else None
        if self.printer_name:
            del(kwargs['printer_name'])
        self.node_name = kwargs['node_name']
        del(kwargs['node_name'])
        super(StackLayout, self).__init__(**kwargs)
        self.ids['printer_name'].text = self.printer_name
        self._secondsLeft = None
        self._last_dt = None
        self.event = None

    def update_values(self, values, name):
        if self.node_name not in values:
            return
        values = values[self.node_name]

        if values['error']:
            self.error = 1
            self.printing = 0
            self.done = 0
            self.ids['status'].text = "OFFLINE"
            self.ids['nozzle_temp'].text = ""
            self.ids['bed_temp'].text = ""
            self.ids['printer_times'].text = ""
            self.ids['progress'].text = ""
        else:
            self.error = 0
            if values['print'] == '':
                self.printing = 0
            else:
                self.printing = 1
                self.done = 0
                if 'completion' in values['print']:
                    self.ids['progress'].text = str(values['print']['completion']) + " %"
                    if values['print']['completion'] == 100:
                        self.done = 1
                        self.printing = 0
                        self.ids['nozzle_temp'].text = ""
                        self.ids['bed_temp'].text = ""
                        self.ids['printer_times'].text = ""
                        self.ids['progress'].text = ""

                if 'printTimeLeft' in values['print']:
                    self.ids['printer_times'].text = ':'.join(str(timedelta(seconds=values['print']['printTimeLeft'])).split(':')[:2])

            self.ids['status'].text = values['status']
            if values['nozzle']:
                self.ids['nozzle_temp'].text = "{:.0f} / {:.0f}".format(values['nozzle'][0]['actual'], values['nozzle'][0]['target'])
            if values['bed']:
                self.ids['bed_temp'].text = "{:.0f} / {:.0f}".format(values['bed']['actual'], values['bed']['target'])
