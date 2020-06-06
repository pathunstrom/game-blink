from time import perf_counter

from ppb import BaseScene
from ppb import Image
from ppb import Font
from ppb import Sprite
from ppb import Text
from ppb import Vector
from ppb.events import ReplaceScene
from ppb.sprites import RectangleSprite


text_opacity = int(255 * 0.8)


class Splash(BaseScene):
    background_color = 106, 48, 147
    run_time = 1

    def __init__(self, *args, next_scene=None, **kwargs):
        super().__init__()
        c = 255, 255, 255

        a = RectangleSprite(
            image=Text("A",
                       font=Font("blink/resources/Comfortaa_Bold.ttf", size=64),
                       color=c),
            height=2,
            position=Vector(0, -2),
            opacity=text_opacity
        )
        name = RectangleSprite(
            image=Text("Piper Thunstrom",
                       font=Font("blink/resources/Comfortaa_Bold.ttf", size=64),
                       color=c),
            height=2,
            opacity=text_opacity
        )
        game = RectangleSprite(
            image=Text("Game",
                       font=Font("blink/resources/Comfortaa_Bold.ttf", size=64),
                       color=c),
            height=2,
            opacity=text_opacity
        )
        icon = Sprite(
            image=Image("blink/resources/piper.png"),
            size=5
        )
        icon.bottom = a.top + 1
        name.top = a.bottom
        game.top = name.bottom
        self.add(a)
        self.add(name)
        self.add(game)
        self.add(icon)
        self.start = perf_counter()
        self.next_scene = next_scene

    def on_idle(self, event, signal):
        if perf_counter() >= self.start + self.run_time and self.next_scene:
            signal(ReplaceScene(self.next_scene()))
