import ppb
from ppb import keycodes as keys

from blink.field import Field

__all__ = ["Title"]


class Title(ppb.BaseScene):

    def __init__(self):
        super().__init__()
        title = ppb.sprites.RectangleSprite(
            image=ppb.Text("Blink", font=ppb.Font("blink/resources/strato-linked-webfont.ttf", size=72), color=(220, 235, 50)),
            layer=3,
            height=5,
            position=ppb.Vector(-6, 5.5)
        )
        self.add(title)

    def on_key_released(self, event, signal):
        if event.key is keys.Escape:
            signal(ppb.events.Quit())
        signal(ppb.events.StartScene(Field()))

    def on_button_released(self, event: ppb.events.ButtonReleased, signal):
        signal(ppb.events.StartScene(Field()))
