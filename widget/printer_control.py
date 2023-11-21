from kivy.uix.stacklayout import StackLayout
from kivy.lang import Builder
import pathlib
import importlib
import importlib.util
from service.widget import Widget
from datetime import datetime, timedelta
from pprint import pprint
from kivy.clock import Clock
from printer.settings_model import Settings
from printer.detail_popup import DetailPopup

Builder.load_file(str(pathlib.Path(__file__).parent.absolute()) + pathlib.os.sep + 'printer_control.kv')

STATUS_IDLE = "idle"
STATUS_PRINTING = "work"
STATUS_DISCONNECTED = "dc"
STATUS_ERROR = "error"
STATUS_UNKNOWN = "unknown"


class PrinterControl(Widget, StackLayout):
    def __init__(self, **kwargs):
        self.printer_name = kwargs['printer_name'] if 'printer_name' in kwargs else None
        if self.printer_name:
            del(kwargs['printer_name'])
        self.node_name = kwargs['node_name']
        self.callbacks = {
            'shutdown': None,
        }
        del(kwargs['node_name'])
        super(StackLayout, self).__init__(**kwargs)
        self.settings = Settings()
        self.ids['printer_name'].text = self.printer_name
        self.event = None
        self.was_printing = 0
        self.timer = None
        self.timer_tick = 0
        self.configured = False

        self.popup = DetailPopup(node_name=self.node_name, settings=self.settings)

    def _configure(self, values):
        self.configured = True
        if values['type'] == "octoprint":
            from printer.octopring_cfg import Config
        elif values['type'] == "klipper":
            from printer.klipper_cfg import Config
        else:
            raise Exception(values['type'] + "not supported")
        cfg = Config()
        cfg.configure(self)

    def add_callback(self, name, fun):
        if name not in self.callbacks:
            raise Exception('PrinterControl callback not found')
        self.callbacks[name] = fun

    def update_values(self, values, name):
        if self.node_name not in values:
            return

        values = values[self.node_name]

        if not self.configured:
            self._configure(values)

        if 'connection' in values:
            self.popup.ids['detail_connection'].text = str(values['connection']['port']) + " @ " + str(values['connection']['baudrate'])

        if 'version' in values:
            self.popup.ids['detail_printer'].text = str(values['version'])

        if 'files' in values:
            self.popup.build_filelist(values['files'])

        if 'error' in values:
            if values['error']:
                self._update_error_data(values)
            else:
                self._update_operational_data(values)

        if 'version' in values and values['version']:
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

        self.popup.change_panel('detail_status_'+self.popup.status)
        # self.popup.ids['detail_status_tabs'].switch_to(self.popup.ids['detail_status_work'])

    def _update_error_data(self, values):
        if self.printing == 1:
            self.was_printing = 1
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
            if values['status'] == "D/C" and self.was_printing == 1:
                if self.settings.shutdown_after_dc:
                    self.start_shutdown_timer(self.settings.shutdown_time)
                self.was_printing = 0
        else:
            self.popup.ids['detail_status'].text = values['status']
            self.ids['status'].text = "OFFLINE"
            self.popup.title = self.printer_name

    def _update_operational_data(self, values):
        self.error = 0
        paused = True if 'flags' in values and (('paused' in values['flags'] and values['flags']['paused']) or ('pausing' in values['flags'] and values['flags']['pausing'])) else False
        if (values['print'] == '' or values['print'] == {}) and not paused:
            self.printing = 0
        else:
            if 'flags' in values:
                if values['flags']['printing']:
                    self.printing = 1
                    self.done = 0
                if values['flags']['paused'] != self.popup.print_paused:
                    self.printing = 1
                    self.popup.print_paused = values['flags']['paused']
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
                    if self.settings.shutdown_after_done:
                        self.start_shutdown_timer(2 * self.settings.shutdown_time)

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
        if values['bed'] and values['bed']['actual'] != '' and values['bed']['target'] != '' :
            self.ids['bed_temp'].text = "{:.0f} / {:.0f}".format(values['bed']['actual'], values['bed']['target'])
            self.popup.ids['detail_bed'].text = self.ids['bed_temp'].text

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            if self.timer:
                Clock.unschedule(self.timer)
                self.timer = None
            else:
                self.popup.reset()
                self.popup.open()

    def start_shutdown_timer(self, shutdown_time):
        self.timer_tick = shutdown_time
        if self.timer:
            Clock.unschedule(self.timer)
            self.timer = None
        self.timer = Clock.schedule_interval(self.tick_shutdown_timer, 1)

    def tick_shutdown_timer(self, dt):
        if self.timer_tick == 0:
            if self.callbacks['shutdown']:
                self.callbacks['shutdown']()
            return False
        self.timer_tick -= 1
        self.ids['status'].text = str(self.timer_tick)
        return True

