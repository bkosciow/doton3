from view.label_border import LabelBorder
from service.widget import Action
from kivy.uix.popup import Popup
from kivy.uix.stacklayout import StackLayout
from kivy.uix.boxlayout import BoxLayout
from widget.relay_switch import RelaySwitch
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label


class Room(LabelBorder):
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
                content = StackLayout()
                content.padding = [15, 25, 15, 15]
                content.spacing = [10, 10]
                popup = Popup(title="Actions", size_hint=(0.6, 0.6))
                for item in detected:
                    button = RelaySwitch(node_name=item.node_name, channel=item.channel, text=item.label)
                    button.state = 'normal' if item.enabled == 1 else 'down'
                    content.add_widget(button)
                popup.content = content

                popup.open()

