from kivy.uix.popup import Popup
from printer.file_list import FileList
from view.popup_confirm import ConfirmationPopup
from kivy.uix.button import Button
from kivy.uix.label import Label


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
        self.communication = None

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

    def _connect_printer(self):
        port = self.ids['detail_selected_port'].text
        baud = self.ids['detail_selected_baud'].text
        if port == "":
            self.ids['detail_selected_port_message'].text = "select a port"
            return

        if baud == "":
            self.ids['detail_selected_port_message'].text = "select a baud rate"
            return

        self.ids['detail_selected_port_message'].text = "Connecting"
        message = self.communication.connect(port, baud, self.node_name)
        self.communication.send(message)

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
            message = self.communication.start_print(self.filelist.selected_path, self.node_name)
            self.filelist.reset_selection()
            self.communication.send(message)

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
        message = self.communication.stop_print(self.node_name)
        self.communication.send(message)

    def _send_pause(self):
        message = self.communication.pause_print(self.node_name)
        self.communication.send(message)

    def _send_resume(self):
        message = self.communication.resume_print(self.node_name)
        self.communication.send(message)
