import ppb
from ppb.features import animation


class Firefly(ppb.Sprite):
    size = 0.5
    image = animation.Animation("blink/resources/firefly/{0..5}.png", 30)
