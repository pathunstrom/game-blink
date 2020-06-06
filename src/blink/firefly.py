from dataclasses import dataclass
from random import randint

import ppb
from ppb.features import animation


LIGHT_RADIUS = 2.5
URGE_MULTIPLIER = 30


@dataclass
class Blink:
    source: 'Firefly'


def _one():
    return 1


def _half():
    return 0.5


_urge_increase_functions = {
    "half": _half,
    "one": _one
}


def _urge_increase(key="one"):
    return _urge_increase_functions[key]()


class Firefly(ppb.Sprite):
    size = 0.5
    image = animation.Animation("blink/resources/firefly/{0..5}.png", 30)
    urge = 0
    urge_increase = "half"
    max_urge = 100

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.urge = randint(0, 35)

    def on_update(self, event, signal):
        self.urge += _urge_increase(self.urge_increase)
        if self.urge >= self.max_urge:
            event.scene.add(Light(position=self.position))
            signal(Blink(self))
            self.urge -= self.max_urge

    def on_blink(self, event, signal):
        distance = (self.position - event.source.position).length
        if distance <= LIGHT_RADIUS:
            self.urge += sum(_urge_increase(self.urge_increase) for _ in range(URGE_MULTIPLIER))


class Light(ppb.Sprite):
    image = ppb.Circle(246, 255, 77)
    _opacity = 0.3
    size = LIGHT_RADIUS * 2
    parent = None

    def on_update(self, event, signal):
        self._opacity -= 0.025
        if self._opacity <= 0:
            event.scene.remove(self)

    @property
    def opacity(self):
        return int(255 * self._opacity)
