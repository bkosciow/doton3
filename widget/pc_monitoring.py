from kivy.uix.stacklayout import StackLayout
from kivy.lang import Builder
import pathlib
from service.widget import Widget
from service.widget import FreshData

Builder.load_file(str(pathlib.Path(__file__).parent.absolute()) + pathlib.os.sep + 'pc_monitoring.kv')


class PCMonitoring(Widget, StackLayout, FreshData):
    def __init__(self, **kwargs):
        self.name = kwargs['name'] if 'name' in kwargs else None
        if self.name:
            del(kwargs['name'])
        super(StackLayout, self).__init__(**kwargs)
        super(FreshData, self).__init__()
        self.ids['name'].text = self.name
        self.data_ttl = 15

    def update_values(self, values, name):
        data = False
        if 'cpu_temperature' in values:
            self.cpu_temperature = round(float(values['cpu_temperature']), 1)
            data = True
        if 'gpu_temperature' in values:
            self.gpu_temperature = round(float(values['gpu_temperature']), 1)
            data = True
        if 'cpu_load' in values:
            self.cpu_load = round(float(values['cpu_load']), 1)
            data = True
        if 'gpu_load' in values:
            self.gpu_load = round(float(values['gpu_load']), 1)
            data = True

        if data:
            self.got_data()
