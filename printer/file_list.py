from kivy.uix.button import Button


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
        self.communication = None

    def build_filelist(self, data):
        self.current_dir = ""
        if self.ts < data['ts']:
            self.list = data['list']
            self.ts = data['ts']
            self.initialized = False

    def message_get_files(self):
        message = self.communication.get_filelist(self.node_name)
        self.communication.send(message)
        # message = {
        #     'parameters': {
        #         'node_name': self.node_name
        #     },
        #     'event': "octoprint.get_filelist"
        # }
        # comm.send(message)

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
