from view.label_border import LabelBorder
from service.widget import Action


class Room(LabelBorder):
    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            detected = []
            for obj in self.children:
                if isinstance(obj, Action):
                    detected.append(obj)

            print(detected)
            if not detected:
                return
            if len(detected) == 1:
                detected[0].action(touch)
            else:
                print('popup')
