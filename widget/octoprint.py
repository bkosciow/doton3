from kivy.uix.stacklayout import StackLayout
from kivy.lang import Builder
import pathlib
from service.widget import Widget
from datetime import datetime, timedelta
from service.widget import Action
from kivy.uix.popup import Popup
from kivy.uix.button import Button
import service.comm as comm


Builder.load_file(str(pathlib.Path(__file__).parent.absolute()) + pathlib.os.sep + 'octoprint.kv')

STATUS_IDLE = "idle"
STATUS_PRINTING = "work"
STATUS_DISCONNECTED = "dc"
STATUS_ERROR = "error"
STATUS_UNKNOWN = "unknown"


class DetailPopup(Popup):
    def __init__(self, **kwargs):
        self.node_name = kwargs['node_name']
        del (kwargs['node_name'])
        super(Popup, self).__init__(**kwargs)

    def add_port(self, name):
        self.ids['detail_port_list'].add_widget(
            Button(
                text=name,
                on_press=self._select_port_action,
                font_size="20sp",
                height="30dp",
                size_hint=(1, None),
            )
        )

    def _select_port_action(self, item):
        self.ids['detail_selected_port'].text = item.text
        self.ids['detail_selected_port_message'].text = ""

    def _select_baud_action(self, baud):
        self.ids['detail_selected_baud'].text = str(baud)
        self.ids['detail_selected_port_message'].text = ""

    def _connect_octoprint(self):
        port = self.ids['detail_selected_port'].text
        baud = self.ids['detail_selected_baud'].text
        if port == "":
            self.ids['detail_selected_port_message'].text = "select a port"
            return

        if baud == "":
            self.ids['detail_selected_port_message'].text = "select a baud rate"
            return

        self.ids['detail_selected_port_message'].text = "Connecting"
        message = {
            'parameters': {
                'port': port,
                'baudrate': baud,
                'node_name': self.node_name
            },
            'event': "octoprint.connect"
        }
        comm.send(message)

    def reset(self):
        self.ids['detail_selected_port_message'].text = ""


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
        self.popup = DetailPopup(node_name=self.node_name)
        self.popup.add_port('/dev/ttyUSB0')
        self.popup.add_port('/dev/ttyUSB1')
        self.popup.add_port('/dev/ttyACM0')

        # self.popup.ids['detail_btn_stop'].bind(on_press=self.on_stop)
        # self.popup.ids['detail_btn_pause'].bind(on_press=self.on_pause)

    def update_values(self, values, name):
        if self.node_name not in values:
            return
        values = values[self.node_name]
        if 'connection' in values:
            self.popup.ids['detail_connection'].text = str(values['connection']['port']) + " @ " + str(values['connection']['baudrate'])

        if 'octoprint' in values:
            self.popup.ids['detail_octoprint'].text = str(values['octoprint'])

        if values['error']:
            self._update_error_data(values)
        else:
            self._update_operational_data(values)
        # print(values)
        if 'octoprint' in values and values['octoprint']:
            if values['connection']['port'] is None:
                self.popup.status = STATUS_DISCONNECTED
            elif self.printing:
                self.popup.status = STATUS_PRINTING
            elif self.error:
                self.popup.status = STATUS_ERROR
            else:
                self.popup.status = STATUS_IDLE
        else:
            self.popup.status = STATUS_UNKNOWN

        self.popup.ids['detail_status_tabs'].switch_to(self.popup.ids['detail_status_'+self.popup.status])

    def _update_error_data(self, values):
        self.printing = 0
        self.ids['nozzle_temp'].text = ""
        self.ids['bed_temp'].text = ""
        self.ids['printer_times'].text = ""
        self.ids['progress'].text = ""
        self.error = 1
        self.done = 0

        if 'error_message' in values and values['error_message'] != '':
            self.ids['status'].text = values['status']
            self.popup.title = self.printer_name + " -- " + values['error_message']
            self.popup.ids['detail_status'].text = values['error_message']
        else:
            self.popup.ids['detail_status'].text = values['status']
            self.ids['status'].text = "OFFLINE"
            self.popup.title = self.printer_name

    def _update_operational_data(self, values):
        self.error = 0
        if values['print'] == '' or values['print'] == {}:
            self.printing = 0
        else:
            if 'flags' in values and values['flags']['printing']:
                self.printing = 1
                self.done = 0
            if 'completion' in values['print']:
                self.ids['progress'].text = str(round(values['print']['completion'])) + " %"
                self.popup.ids['detail_completion'].value = values['print']['completion']
                if float(values['print']['completion']) > 99.8:
                    self.done = 1
                    self.printing = 0
                    self.ids['nozzle_temp'].text = ""
                    self.ids['bed_temp'].text = ""
                    self.ids['printer_times'].text = ""
                    self.ids['progress'].text = ""

            if 'printTimeLeft' in values['print']:
                self.ids['printer_times'].text = ':'.join(
                    str(timedelta(seconds=values['print']['printTimeLeft'])).split(':')[:2])
                self.popup.ids['detail_print_time_left'].text = self.ids['printer_times'].text
            if 'printTime' in values['print']:
                self.popup.ids['detail_print_time'].text = ':'.join(
                    str(timedelta(seconds=values['print']['printTime'])).split(':')[:2])
            if 'name' in values['print']:
                self.popup.title = self.printer_name + " -- " + values['print']['name'][:-6] + " -- " + self.ids[
                    'progress'].text
            else:
                self.popup.title = self.printer_name

        self.ids['status'].text = values['status']
        self.popup.ids['detail_status'].text = self.ids['status'].text
        if values['nozzle']:
            self.ids['nozzle_temp'].text = "{:.0f} / {:.0f}".format(values['nozzle'][0]['actual'],
                                                                    values['nozzle'][0]['target'])
            self.popup.ids['detail_nozzle'].text = self.ids['nozzle_temp'].text
        if values['bed']:
            self.ids['bed_temp'].text = "{:.0f} / {:.0f}".format(values['bed']['actual'], values['bed']['target'])
            self.popup.ids['detail_bed'].text = self.ids['bed_temp'].text

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.popup.reset()
            self.popup.open()

    def on_stop(self, a):
        print(a)

    def on_pause(self, a):
        print(a)
