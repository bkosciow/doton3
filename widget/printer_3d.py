from kivy.uix.stacklayout import StackLayout
from kivy.lang import Builder
from kivy.clock import Clock
import math
import pathlib
from service.widget import Widget
import datetime

Builder.load_file(str(pathlib.Path(__file__).parent.absolute()) + pathlib.os.sep + 'printer_3d.kv')


class Printer3D(Widget, StackLayout):
    def __init__(self, **kwargs):
        self.printer_name = kwargs['printer_name'] if 'printer_name' in kwargs else None
        if self.printer_name:
            del(kwargs['printer_name'])
        super(StackLayout, self).__init__(**kwargs)
        self.ids['printer_progress'].value = 10
        self.ids['printer_progress'].value = 0
        self.ids['printer_name'].text = self.printer_name
        self._secondsLeft = None
        self._last_dt = None
        self.event = None

    def tick(self, dt):
        if self.event is None or self._secondsLeft is None or self._last_dt is None:
            return
        now = datetime.datetime.now()
        d = now - self._last_dt
        if d.total_seconds() > 1:
            diff = self._secondsLeft - math.floor(d.total_seconds())
            if diff >= 0:
                dt = datetime.timedelta(seconds=diff)
                self.ids['printer_times'].text = ':'.join(str(dt).split(':')[:2])

    def stop_tick(self):
        if self.event is not None:
            self.event.cancel()
            self.event = None

    def update_values(self, values, name):
        if 'percentage' in values:
            self.ids['printer_progress'].value = int(values['percentage'])
        if 'secondsLeft' in values:
            # self.ids['printer_times'].text = str(values["secondsLeft"])
            if values['secondsLeft'] != 0 and values['secondsLeft'] != '-':
                self._secondsLeft = int(values['secondsLeft'])
                self._last_dt = datetime.datetime.now()
                if self.event is None:
                    self.event = Clock.schedule_interval(self.tick, 1)

        if 'status' in values:
            if values['status'] == "connected":
                self.stop_tick()
                self.error = 0
                self.ids['printer_times'].text = "online"
                self.ids['printer_progress'].value = 0
            if values['status'] == "disconnected":
                self.stop_tick()
                self.error = 1
                self.ids['printer_times'].text = "OFFLINE"
            if values['status'] == "aborted":
                self.stop_tick()
                self.error = 1
                self.ids['printer_times'].text = "ABORTED"
            if values['status'] == "printed" and values['secondsLeft'] == 0:
                self.stop_tick()
                self.error = 0
                self.ids['printer_times'].text = "done"

