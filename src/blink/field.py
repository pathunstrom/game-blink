from itertools import product

import ppb

from blink.firefly import Firefly, MousePosition


class Field(ppb.BaseScene):
    background_color = (30, 0, 75)

    def on_scene_started(self, event, signal):
        for x, y in product(range(-3, 4, 2), range(-3, 4, 2)):
            self.add(Firefly(position=ppb.Vector(x, y)))
            self.add(MousePosition())
