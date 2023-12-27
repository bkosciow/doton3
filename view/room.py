from view.label_border import LabelBorder
from service.widget import Action
from kivy.uix.popup import Popup
from kivy.uix.stacklayout import StackLayout
from kivy.uix.boxlayout import BoxLayout
from widget.relay_switch import RelaySwitch
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from service.widget import FreshData


class Room(LabelBorder, FreshData):
    def __init__(self, **kwargs):
        super(LabelBorder, self).__init__(**kwargs)
        super(FreshData, self).__init__()
        self.popup = None
        self.data_ttl = 20

    def _create_popup(self, detected):
        content = StackLayout()
        content.padding = [15, 25, 15, 15]
        content.spacing = [10, 10]
        self.popup = Popup(title="Actions", size_hint=(0.6, 0.6))
        for item in detected:
            button = RelaySwitch(
                node_name=item.node_name,
                channel=item.channel,
                text=item.label,
                confirm=item.confirm if hasattr(item, 'confirm') else False
            )
            button.state = 'normal' if item.enabled == 1 else 'down'
            content.add_widget(button)
        self.popup.content = content

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            detected = []
            for obj in self.children:
                if isinstance(obj, Action):
                    detected.append(obj)

            if not detected:
                return

            if len(detected) == 1:
                detected[0].action(touch)
            else:
                if not self.popup:
                    self._create_popup(detected)

                self.popup.open()
