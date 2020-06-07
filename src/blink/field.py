from itertools import product
from random import uniform

import ppb
from ppb import buttons

from blink.firefly import Firefly, MousePosition


class Field(ppb.BaseScene):
    background_color = (30, 0, 75)

    def on_scene_started(self, event, signal):
        self.add(MousePosition())
        for _ in range(5):
            self.spawn_firefly()

    def on_button_pressed(self, event, signal):
        if event.button is buttons.Secondary and len(list(self.get(kind=Firefly))) < 25:
            self.spawn_firefly()

    def spawn_firefly(self):
        spawn = ppb.Vector(uniform(self.main_camera.left, self.main_camera.right), self.main_camera.top + 1)
        velocity = ppb.Vector(uniform(-1, 1), uniform(-1, 1))
        if velocity:
            velocity = velocity.scale_to(Firefly.max_velocity)
        self.add(
            Firefly(
                position=spawn + ppb.Vector(0, -0.5),
                spawn=spawn,
                velocity=velocity
            )
        )