from random import choice, uniform

import ppb
from ppb import buttons
from ppb.features import animation as anim
from blink.firefly import Firefly, MousePosition


sound_wave = anim.Animation("blink/resources/sound-wave/{01..08}.png", frames_per_second=24)
bg_fronds = ppb.Image(f"blink/resources/bg-fronds-small-1.png")
SECONDS_TO_FOCUS = 1
CAMERA_SPEED = 25 / SECONDS_TO_FOCUS
FOREGROUND = 10
CENTER_FRONT = 5
CENTER = 0
BACKGROUND = -10
DEEP_BACKGROUND = -100


class Field(ppb.BaseScene):
    background_color = (30, 0, 75)

    def on_scene_started(self, event, signal):
        self.add(MousePosition())
        for _ in range(5):
            self.spawn_firefly()

        sections = 7
        section_width = self.main_camera.width / sections
        modifier = choice((0, sections - 1))  # Left side or right side
        normalized_position = uniform(0, 1)
        x_offset = normalized_position * section_width
        x_root = self.main_camera.left + (modifier * section_width) + x_offset
        foreground = ppb.RectangleSprite(
            height=self.main_camera.height,
            width=9.375,
            image=ppb.Image("blink/resources/foreground-fronds.png"),
            layer=FOREGROUND,
            position=ppb.Vector(x_root + x_offset, 0)
        )
        self.add(foreground)

        x_position = self.main_camera.left + uniform(0, 4)
        while x_position <= self.main_camera.right:
            self.add(
                ppb.RectangleSprite(
                    image=bg_fronds,
                    height=self.main_camera.height,
                    width=1,
                    layer=BACKGROUND,
                    position=ppb.Vector(x_position, 0)
                )
            )
            x_position += uniform(4, 8)

        self.add(
            ppb.RectangleSprite(
                image=ppb.Image("blink/resources/background.png"),
                width=25,
                layer=DEEP_BACKGROUND
            )
        )

        self.add(
            ppb.sprites.RectangleSprite(
                image=ppb.Text("Blink", font=ppb.Font("blink/resources/strato-linked-webfont.ttf", size=72),
                               color=(220, 235, 50)),
                layer=FOREGROUND,
                height=5,
                position=ppb.Vector(-6-25, 5.5)
            ),
            ["cleanup"]
        )

        self.add(
            ppb.RectangleSprite(
                image=ppb.Image("src/blink/resources/background.png"),
                layer=DEEP_BACKGROUND,
                width=25,
                position=ppb.Vector(-25, 0)
            ),
            ["cleanup"]
        )

        self.main_camera.position = ppb.Vector(-25, 0)

    def on_pre_render(self, event, signal):
        if self.main_camera.position.x < 0:
            self.main_camera.position = ppb.Vector(
                min(
                    self.main_camera.position.x + CAMERA_SPEED * .016,
                    0
                ),
                0
            )
            if self.main_camera.position.x == 0:
                for sprite in self.get(tag="cleanup"):
                    self.remove(sprite)

    def on_button_pressed(self, event: ppb.events.ButtonPressed, signal):
        if event.button is buttons.Secondary and len(list(self.get(kind=Firefly))) < 25:
            self.spawn_firefly()
        self.add(
            RunOnceAnimation(
                position=event.position,
                image=anim.Animation("blink/resources/sound-wave/{01..08}.png", frames_per_second=24),
                life_span=0.30,
                size=10,
                layer=CENTER_FRONT
            )
        )

    def spawn_firefly(self):
        spawn = ppb.Vector(uniform(self.main_camera.left, self.main_camera.right), self.main_camera.top + 1)
        velocity = ppb.Vector(uniform(-1, 1), uniform(-1, 1))
        if velocity:
            velocity = velocity.scale_to(Firefly.max_velocity)
        self.add(
            Firefly(
                position=spawn + ppb.Vector(0, -0.5),
                spawn=spawn,
                velocity=velocity,
                layer=CENTER
            )
        )


class RunOnceAnimation(ppb.Sprite):
    life_span = 0.5
    counter = 0
    end_event = None

    def on_update(self, event, signal):
        self.counter += event.time_delta
        if self.counter >= self.life_span:
            event.scene.remove(self)
            if self.end_event is not None:
                signal(self.end_event)