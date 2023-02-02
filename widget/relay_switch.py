from kivy.uix.stacklayout import StackLayout
from service.widget import Widget
from kivy.uix.button import Button
from kivy.lang import Builder
from kivy.uix.gridlayout import GridLayout
from service.widget import Action
import pathlib
import service.comm as comm
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label

Builder.load_file(str(pathlib.Path(__file__).parent.absolute()) + pathlib.os.sep + 'relay_switch.kv')


class RelaySwitch(Widget, StackLayout):
    def __init__(self, **kwargs):
        self.node_name = kwargs['node_name']
        self.channel = kwargs['channel']
        self.text = ''
        self.confirm = False
        self.popup = None
        if 'text' in kwargs:
            self.text = kwargs['text']
            del(kwargs['text'])
        if 'confirm' in kwargs:
            self.confirm = kwargs['confirm']
            del(kwargs['confirm'])
        del(kwargs['node_name'])
        del(kwargs['channel'])
        super(StackLayout, self).__init__(**kwargs)
        self.ids['device_name'].text = self.text

    def update_values(self, values, name):
        self.ids['device_name'].disabled = False
        if 'relay' in values:
            if values['relay'][self.channel] == 0:
                self.state = 'down'
            else:
                self.state = 'normal'
            # print(name, values, self.state, self.channel)

    def _action(self, event=None):
        if self.state == 'normal':
            state = 'down'
        else:
            state = 'normal'

        message = {
            'parameters': {
                'channel': self.channel
            },
            'targets': [self.node_name],
            'event': "channel.off" if state == 'down' else "channel.on"
        }
        self.state = state
        self.ids['device_name'].disabled = True
        comm.send(message)
        if event:
            self._close_popup(event)

    def _close_popup(self, event):
        self.popup.dismiss()

    def _create_popup(self):
        self.popup = Popup(title="Confirm", size_hint=(0.6, 0.5))
        popup_layout = BoxLayout(spacing=10)
        popup_layout2 = BoxLayout(orientation='vertical')
        popup_layout2.add_widget(Label(
            markup=True,
            text="""Execute action for [b]{}[/b] ?""".format(self.text),
            font_size=20
        ))
        popup_layout.add_widget(Button(
            text="Yes",
            on_press=self._action,
            size_hint=(0.3, 0.7)
        ))
        popup_layout.add_widget(Button(
            text="Cancel",
            on_press=self._close_popup,
            size_hint=(0.3, 0.7)
        ))
        popup_layout2.add_widget(popup_layout)
        self.popup.add_widget(popup_layout2)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            if self.confirm:
                if not self.popup:
                    self._create_popup()

                self.popup.open()

            else:
                self._action()
