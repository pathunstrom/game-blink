"""
A tiny emergent behavior toy.
"""
import ppb
from ppb import assetlib

from blink.splash import Splash
from blink.title import Title
from blink.bgm import BackgroundMusicController


def main():
    # This should start and launch your app!
    ppb.run(
        starting_scene=Splash,
        scene_kwargs={"next_scene": Title},
        basic_systems=(
            ppb.systems.Renderer,
            ppb.systems.Updater,
            ppb.systems.EventPoller,
            BackgroundMusicController,
            assetlib.AssetLoadingSystem
        )
    )
