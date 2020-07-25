import io
from collections import deque
from dataclasses import dataclass

from ppb import assetlib
from ppb.systems._sdl_utils import mix_call
from ppb.systems.sound import SoundController
from sdl2 import rw_from_object
from sdl2.sdlmixer import Mix_FreeMusic
from sdl2.sdlmixer import Mix_LoadMUS_RW
from sdl2.sdlmixer import MIX_MAX_VOLUME
from sdl2.sdlmixer import Mix_PlayMusic
from sdl2.sdlmixer import Mix_PlayingMusic
from sdl2.sdlmixer import Mix_VolumeMusic


@dataclass
class QueueBackgroundMusic:
    background_music: 'BackgroundMusic'


@dataclass
class SetMusicVolume:
    volume_level: float


class BackgroundMusic(assetlib.Asset):
    """
    A ppb asset that wraps a SDL MIX_MUSIC pointer.
    """

    def __new__(cls, name, *, play_forever=False, play_loops=1):
        return super().__new__(cls, name)

    def __init__(self, name, *, play_forever=False, play_loops=1):
        """

        :param name: The filename of the music file.
        :param play_forever: If true, the background music will play infinitely.
        :param play_loops: If not play_forever, the number of times to loop the
           track. Defaults to 1.
        """
        super().__init__(name)
        self._file = None
        if play_forever:
            self.loops = -1
        else:
            self.loops = play_loops

    def background_parse(self, data: bytes):
        self._file = rw_from_object(io.BytesIO(data))

        rv = mix_call(
            Mix_LoadMUS_RW, self._file, _check_error=lambda rv: not rv
        )
        return rv

    def free(self, object, _Mix_FreeMusic=Mix_FreeMusic):
        if object:
            _Mix_FreeMusic(object)


class BackgroundMusicController(SoundController):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bgm_currently_playing = None
        self.bgm_queue = deque()

    def on_queue_background_music(self, event: QueueBackgroundMusic, signal):
        self.bgm_queue.append(event.background_music)

    def on_scene_started(self, event, signal):
        mix_call(Mix_VolumeMusic, 255)

    def on_idle(self, event, signal):
        if not mix_call(Mix_PlayingMusic) and self.bgm_queue:
            _next: BackgroundMusic = self.bgm_queue.popleft()
            self.bgm_currently_playing = _next.load()
            mix_call(Mix_PlayMusic, self.bgm_currently_playing, _next.loops)
