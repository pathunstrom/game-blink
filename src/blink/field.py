import ppb

from blink.firefly import Firefly


class Field(ppb.BaseScene):
    background_color = (30, 0, 75)

    def on_scene_started(self, event, signal):
        self.add(Firefly())
