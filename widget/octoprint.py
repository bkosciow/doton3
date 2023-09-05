from kivy.uix.stacklayout import StackLayout
from kivy.lang import Builder
import pathlib
from service.widget import Widget
from datetime import datetime, timedelta
from view.popup_confirm import ConfirmationPopup
from service.widget import Action
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.uix.label import Label
import service.comm as comm
from pprint import pprint
from kivy.clock import Clock


Builder.load_file(str(pathlib.Path(__file__).parent.absolute()) + pathlib.os.sep + 'octoprint.kv')

STATUS_IDLE = "idle"
STATUS_PRINTING = "work"
STATUS_DISCONNECTED = "dc"
STATUS_ERROR = "error"
STATUS_UNKNOWN = "unknown"


class Settings:
    def __init__(self):
        self.sort = "name"
        self.sort_values = ["default", "name"]
        self.shutdown_after_done = True
        self.shutdown_after_dc = True
        self.shutdown_time = 60
        # self.shutdown_min_temp = 50  # only when done


class FileList:
    def __init__(self, node_name, settings, container, selection):
        self.node_name = node_name
        self.container = container
        self.selection = selection
        self.settings = settings
        self.initialized = False
        self.ts = 0
        self.list = []
        self.current_dir = ""
        self.selected_path = ""
        self.current_sort = settings.sort

    def build_filelist(self, data):
        self.current_dir = ""
        if self.ts < data['ts']:
            self.list = data['list']
            self.ts = data['ts']
            self.initialized = False

    def message_get_files(self):
        message = {
            'parameters': {
                'node_name': self.node_name
            },
            'event': "octoprint.get_filelist"
        }
        comm.send(message)

    def _get_font_size(self, text):
        if len(text) < 23:
            return "20sp"
        elif len(text) < 30:
            return "16sp"
        elif len(text) < 40:
            return "13sp"

        return "10sp"

    def display_filelist(self):
        if not self.initialized or self.current_sort != self.settings.sort:
            self.container.clear_widgets()
            self.initialized = True
            self.current_sort = self.settings.sort
            for item in self._get_sorted_list(self.list):
                a = Button(
                    text=item['path'],
                    size_hint_y=None,
                    height="30dp",
                    font_size=self._get_font_size(item['path']),
                    on_press=self._select_file_filelist,
                )
                self.container.add_widget(a)

    def _get_sorted_list(self, file_list):
        if self.settings.sort == "name":
            return sorted(file_list, key=lambda x: x['display'])

        return file_list

    def _select_file_filelist(self, item):
        self.selection.text = item.text
        self.selection.font_size = item.font_size
        self.selected_path = item.text

    def reset_selection(self):
        self.selection.text = ""
        self.selected_path = ""


class DetailPopup(Popup):
    def __init__(self, **kwargs):
        self.node_name = kwargs['node_name']
        del (kwargs['node_name'])
        self.settings = kwargs['settings']
        del (kwargs['settings'])
        super(Popup, self).__init__(**kwargs)
        self.filelist = FileList(
            self.node_name,
            self.settings,
            self.ids['detail_filelist'],
            self.ids['detail_filelist_selected']
        )
        self.confirmation_popup = ConfirmationPopup()
        self.setting_open = False
        self.tab_open = None

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

    def _show_settings(self):
        self.ids['option_shutdown_after_done'].state = "down" if self.settings.shutdown_after_done else "normal"
        self.ids['option_shutdown_after_dc'].state = "down" if self.settings.shutdown_after_dc else "normal"
        for v in self.settings.sort_values:
            w = self.ids['option_sort_'+v]
            w.state = "down" if w.text.lower() == self.settings.sort else "normal"
        self.ids['detail_status_tabs'].switch_to(self.ids['detail_status_options'])
        self.setting_open = True

    def save_settings(self):
        for v in self.settings.sort_values:
            w = self.ids['option_sort_'+v]
            if w.state == "down":
                self.settings.sort = w.text.lower()
        self.settings.shutdown_after_done = True if self.ids['option_shutdown_after_done'].state == "down" else False
        self.settings.shutdown_after_dc = True if self.ids['option_shutdown_after_dc'].state == "down" else False
        self.setting_open = False
        self.change_panel(self.tab_open)
        self.filelist.display_filelist()

    def change_panel(self, panel_id):
        self.tab_open = panel_id
        if not self.setting_open:
            self.ids['detail_status_tabs'].switch_to(self.ids[panel_id])

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
        if not self.filelist.initialized:
            self._reload_filelist()

    def _reload_filelist(self):
        self.ids['detail_filelist'].clear_widgets()
        self.ids['detail_filelist_selected'].text = "select a file"
        self.filelist.ts = 0
        self.filelist.message_get_files()

    def build_filelist(self, data):
        self.filelist.build_filelist(data)
        self.filelist.display_filelist()

    def start_print(self):
        if self.filelist.selected_path == "":
            warning = Popup(
                title="no file selected",
                content=Label(text="Select a file first.", font_size="30sp"),
                size_hint=(0.5, 0.5)
            )
            warning.open()
        else:
            message = {
                'parameters': {
                    'node_name': self.node_name,
                    'path': self.filelist.selected_path
                },
                'event': "octoprint.print_start"
            }
            self.filelist.reset_selection()
            comm.send(message)

    def print_pause_resume(self):
        if self.print_paused:
            self.confirmation_popup.callback = self._send_resume
            self.confirmation_popup.text = "Resume current print?"

        else:
            self.confirmation_popup.callback = self._send_pause
            self.confirmation_popup.text = "Pause current print?"

        self.confirmation_popup.show()

    def print_stop(self):
        self.confirmation_popup.callback = self._send_stop
        self.confirmation_popup.text = "Stop current print?"
        self.confirmation_popup.show()

    def _send_stop(self):
        message = {
            'parameters': {
                'node_name': self.node_name,
            },
            'event': "octoprint.print_stop"
        }
        comm.send(message)

    def _send_pause(self):
        message = {
            'parameters': {
                'node_name': self.node_name,
            },
            'event': "octoprint.print_pause"
        }
        comm.send(message)

    def _send_resume(self):
        message = {
            'parameters': {
                'node_name': self.node_name,
            },
            'event': "octoprint.print_resume"
        }
        comm.send(message)


class Octoprint(Widget, StackLayout):
    def __init__(self, **kwargs):
        self.printer_name = kwargs['printer_name'] if 'printer_name' in kwargs else None
        if self.printer_name:
            del(kwargs['printer_name'])
        self.node_name = kwargs['node_name']
        del(kwargs['node_name'])
        super(StackLayout, self).__init__(**kwargs)
        self.settings = Settings()
        self.ids['printer_name'].text = self.printer_name
        self.event = None
        self.was_printing = 0
        self.timer = None
        self.timer_tick = 0
        self.popup = DetailPopup(node_name=self.node_name, settings=self.settings)
        self.popup.add_port('VIRTUAL')
        self.popup.add_port('/dev/ttyUSB0')
        self.popup.add_port('/dev/ttyUSB1')
        self.popup.add_port('/dev/ttyACM0')

    def update_values(self, values, name):
        if self.node_name not in values:
            return
        values = values[self.node_name]
        if 'connection' in values:
            self.popup.ids['detail_connection'].text = str(values['connection']['port']) + " @ " + str(values['connection']['baudrate'])

        if 'octoprint' in values:
            self.popup.ids['detail_octoprint'].text = str(values['octoprint'])

        if 'files' in values:
            self.popup.build_filelist(values['files'])

        if 'error' in values:
            if values['error']:
                self._update_error_data(values)
            else:
                self._update_operational_data(values)

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
                    self.start_shutdown_timer()
                self.was_printing = 0
        else:
            self.popup.ids['detail_status'].text = values['status']
            self.ids['status'].text = "OFFLINE"
            self.popup.title = self.printer_name

    def _update_operational_data(self, values):
        self.error = 0
        paused = True if 'flags' in values and (values['flags']['paused'] or values['flags']['pausing']) else False
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
                        self.start_shutdown_timer()

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
            if self.timer:
                Clock.unschedule(self.timer)
                self.timer = None
            else:
                self.popup.reset()
                self.popup.open()

    def start_shutdown_timer(self):
        self.timer_tick = self.settings.shutdown_time
        if self.done == 1:
            self.timer_tick *= 2
        if self.timer:
            Clock.unschedule(self.timer)
            self.timer = None
        self.timer = Clock.schedule_interval(self.tick_shutdown_timer, 1)

    def tick_shutdown_timer(self, dt):
        if self.timer_tick == 0:
            print("STOP")
            return False
        self.timer_tick -= 1
        self.ids['status'].text = str(self.timer_tick)
        return True

