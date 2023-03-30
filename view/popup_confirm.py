from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label


class ConfirmationPopup:
    def __init__(self, callback=None, text="Are you sure?", title="Confirm", yes="Yes", no="Cancel"):
        self.callback = callback
        self.yes = yes
        self.no = no
        self.title = title
        self.text = text
        self.popup = None

    def show(self):
        self.popup = Popup(title=self.title, size_hint=(0.6, 0.5))
        popup_layout = BoxLayout(spacing=10)
        popup_layout2 = BoxLayout(orientation='vertical')
        popup_layout2.add_widget(Label(
            markup=True,
            text=self.text,
            font_size=20
        ))
        popup_layout.add_widget(Button(
            text=self.yes,
            on_press=self._execute_action,
            size_hint=(0.3, 0.7)
        ))
        popup_layout.add_widget(Button(
            text=self.no,
            on_press=self._execute_close_popup,
            size_hint=(0.3, 0.7)
        ))
        popup_layout2.add_widget(popup_layout)
        self.popup.add_widget(popup_layout2)
        self.popup.open()

    def _execute_action(self, event):
        if self.callback is not None:
            self.callback()
        self.popup.dismiss()
        self.popup = None

    def _execute_close_popup(self, event):
        self.popup.dismiss()
        self.popup = None
