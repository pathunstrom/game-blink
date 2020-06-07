from dataclasses import dataclass
from functools import partial
from random import randint
from random import uniform
from typing import List, NamedTuple


import ppb
from ppb.features import animation


LIGHT_RADIUS = 2.5
URGE_MULTIPLIER = 20


def clamp(x, _min, _max):
    return max(_min, min(x, _max))


def smootherstep(minimum, maximum, current):
    # Scale, and clamp x to 0..1 range
    x = clamp((current - minimum) / (maximum - minimum), 0.0, 1.0)
    # Evaluate polynomial
    return x * x * x * (x * (x * 6 - 15) + 10)


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
    "one": _one,
    "small_range": partial(uniform, 0.1, 0.5)
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
    urge_increase = "small_range"
    max_urge = 200
    velocity: ppb.Vector = ppb.Vector(0, 1)
    max_velocity = 0.75
    wander_vector: ppb.Vector
    basis = ppb.Vector(0, 1)
    layer = 3
    _wall_buffer = 2
    _others_buffer = 3
    _flocking_distance = 10
    _mouse_buffer = 5
    spawn_point: ppb.Vector

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.initialize_urge()
        self.wander_vector = ppb.Vector(0, 1).rotate(randint(0, 359))
        self.spawn_point = getattr(self, "spawn_point", self.position)

    def on_update(self, event, signal):
        self.urge += _urge_increase(self.urge_increase)
        if self.urge >= self.max_urge:
            event.scene.add(Light(position=self.position))
            signal(Blink(self))
            self.urge = 0

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
            forces.append(Force(avoid_mouse, 6))

        seek_center = self.seek_if_far(ppb.Vector(0, 0), 8)
        if seek_center:
            forces.append(Force(seek_center, 5))

        avoid_spawn = self.flee_if_near(self.spawn_point, 2)
        if avoid_spawn:
            forces.append(Force(avoid_spawn, 10))

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

    def on_button_pressed(self, event, signal):
        if (event.position - self.position).length <= self._mouse_buffer:
            self.initialize_urge()

    def on_blink(self, event, signal):
        distance = (self.position - event.source.position).length
        if event.source is not self and distance <= LIGHT_RADIUS:
            self.urge += sum(_urge_increase(self.urge_increase) for _ in range(URGE_MULTIPLIER))

    def initialize_urge(self):
        self.urge = uniform(0, self.max_urge)

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
                3
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

    def seek_if_far(self, point, distance):
        if (self.position - point).length >= distance:
            return self.seek(point)
        return ppb.Vector(0, 0)


class Light(ppb.Sprite):
    image = ppb.Circle(246, 255, 77)
    _opacity = 0.3
    _max_opacity = 0.3
    size = LIGHT_RADIUS * 2.2
    parent = None
    layer = 5

    def on_update(self, event, signal):
        self._opacity -= 0.0125
        if self._opacity <= 0:
            event.scene.remove(self)

    @property
    def opacity(self):
        return int(255 * smootherstep(0, self._max_opacity, self._opacity) * self._max_opacity)
