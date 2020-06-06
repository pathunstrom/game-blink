"""
A tiny emergent behavior toy.
"""
import ppb

from blink.splash import Splash
from blink.title import Title


def main():
    # This should start and launch your app!
    ppb.run(starting_scene=Splash, scene_kwargs={"next_scene": Title})
