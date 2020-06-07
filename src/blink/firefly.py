from dataclasses import dataclass
from random import randint
from random import uniform
from typing import List, NamedTuple


import ppb
from ppb.features import animation


LIGHT_RADIUS = 2.5
URGE_MULTIPLIER = 6


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


class MousePosition(ppb.Sprite):
    image = None

    def on_mouse_motion(self, event, signal):
        self.position = event.position


class Firefly(ppb.Sprite):
    size = 0.5
    image = animation.Animation("blink/resources/firefly/{0..5}.png", 30)
    urge = 0
    urge_increase = "half"
    max_urge = 100
    velocity: ppb.Vector = ppb.Vector(0, 1)
    max_velocity = 0.75
    wander_vector: ppb.Vector
    basis = ppb.Vector(0, 1)
    layer = 3
    _wall_buffer = 2
    _others_buffer = 4
    _flocking_distance = 10
    _mouse_buffer = 4

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

        others = set(event.scene.get(kind=Firefly))
        others.remove(self)
        self.avoid_others(forces, others)
        self.seek_others(forces, others)

        mouse = next(event.scene.get(kind=MousePosition))
        avoid_mouse = self.flee_if_near(mouse.position, self._mouse_buffer)
        if avoid_mouse:
            forces.append(Force(avoid_mouse, 3))

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
        self.wander_vector = self.wander_vector.rotate(uniform(-0.5, 0.5))
        steering_force = self.velocity.scale_to(2) + self.wander_vector
        forces.append(Force(steering_force, 1))

    def avoid_walls(self, forces, camera):
        necessary_force = ppb.Vector(0, 0)
        necessary_weight = 0

        points = (
            ppb.Vector(camera.left, self.position.y),
            ppb.Vector(camera.right, self.position.y),
            ppb.Vector(self.position.x, camera.top),
            ppb.Vector(self.position.x, camera.bottom)
        )

        for point in points:
            if (point - self.position).length <= self._wall_buffer:
                necessary_force += self.flee(point)
                necessary_weight += 3

        if necessary_force:
            forces.append(Force(necessary_force, necessary_weight))

    def avoid_others(self, forces, others):
        positions = []
        local_center = self.position
        for other in others:
            if (self.position - other.position).length < self._others_buffer:
                positions.append(other.position)
        if positions:
            local_center = sum(positions, ppb.Vector(0, 0)) / len(positions)
        forces.append(
            Force(
                self.flee(local_center),
                self._others_buffer - (local_center - self.position).length * 2
            )
        )

    def seek_others(self, forces, others):
        positions = [self.position]
        for other in others:
            if (self.position - other.position).length <= self._flocking_distance:
                positions.append(other.position)
        local_center = sum(positions, ppb.Vector(0, 0)) / len(positions)
        forces.append(Force(self.seek(local_center), 1))

    def flee(self, point):
        desired_direction = (self.position - point)
        desired_velocity = self.velocity
        if desired_direction:
            desired_velocity = (self.position - point).scale_to(self.max_velocity)
        steering = desired_velocity - self.velocity
        return steering

    def seek(self, point):
        desired_velocity = self.velocity
        desired_direction = (self.position - point)
        if desired_direction:
            desired_velocity = (point - self.position).scale_to(self.max_velocity)
        steering = desired_velocity - self.velocity
        return steering

    def flee_if_near(self, point, distance):
        if (self.position - point).length <= distance:
            return self.flee(point)
        return ppb.Vector(0, 0)


class Light(ppb.Sprite):
    image = ppb.Circle(246, 255, 77)
    _opacity = 0.3
    size = LIGHT_RADIUS * 2
    parent = None
    layer = 5

    def on_update(self, event, signal):
        self._opacity -= 0.025
        if self._opacity <= 0:
            event.scene.remove(self)

    @property
    def opacity(self):
        return int(255 * self._opacity)
