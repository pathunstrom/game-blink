from dataclasses import dataclass
from random import randint
from typing import List, NamedTuple


import ppb
from ppb.features import animation


LIGHT_RADIUS = 2.5
URGE_MULTIPLIER = 30


@dataclass
class Blink:
    source: 'Firefly'


class Force(NamedTuple):
    vector: ppb.Vector
    weight: float


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
    velocity: ppb.Vector = ppb.Vector(0, 1)
    max_velocity = 0.75
    max_steering_force = 3
    wander_vector: ppb.Vector
    basis = ppb.Vector(0, 1)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.intialize_urge()
        self.wander_vector = ppb.Vector(0, 1).rotate(randint(0, 359))

    def on_update(self, event, signal):
        self.urge += _urge_increase(self.urge_increase)
        if self.urge >= self.max_urge:
            event.scene.add(Light(position=self.position))
            signal(Blink(self))
            self.intialize_urge()

        forces: List[Force] = []
        self.wander(forces)
        self.avoid_walls(forces, event.scene.main_camera)
        force_vector = ppb.Vector(0, 0)
        weights = 0
        for force in forces:
            force_vector += force.vector * force.weight
            weights += force.weight
        self.velocity += force_vector / weights * event.time_delta
        self.velocity = self.velocity.truncate(self.max_velocity)
        self.position += self.velocity * event.time_delta
        self.facing = self.velocity.normalize()
        self.velocity *= .998

    def on_blink(self, event, signal):
        distance = (self.position - event.source.position).length
        if event.source is not self and distance <= LIGHT_RADIUS:
            self.urge += sum(_urge_increase(self.urge_increase) for _ in range(URGE_MULTIPLIER))

    def intialize_urge(self):
        self.urge = randint(0, 55)

    def wander(self, forces):
        self.wander_vector = self.wander_vector.rotate(randint(-5, 5))
        steering_force = self.velocity.scale_to(2) + self.wander_vector
        forces.append(Force(steering_force, 1))

    def avoid_walls(self, forces, camera):
        necessary_force = ppb.Vector(0, 0)
        necessary_weight = 1

        left_distance = self.position.x - camera.left
        if left_distance <= 2:
            necessary_force += ppb.Vector(1 * (3 - left_distance), 0)
            necessary_weight = max(necessary_weight, 3 - left_distance)

        right_distance = camera.right - self.position.x
        if right_distance <= 2:
            necessary_force += ppb.Vector(-1 * (3 - right_distance), 0)
            necessary_weight = max(necessary_weight, 3 - right_distance)

        top_distance = camera.top - self.position.y
        if top_distance <= 2:
            necessary_force += ppb.Vector(0, -1 * (3 - top_distance))
            necessary_weight = max(necessary_weight, 3 - top_distance)

        bottom_distance = self.position.y - camera.bottom
        if bottom_distance <= 2:
            necessary_force += ppb.Vector(0, 1 * (3 - bottom_distance))
            necessary_weight = max(necessary_weight, 3 - bottom_distance)

        if necessary_force:
            forces.append(Force(necessary_force, necessary_weight))


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
