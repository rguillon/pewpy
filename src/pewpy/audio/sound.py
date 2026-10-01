"""Playing the sound effects and music through Panda3D's audio (OpenAL).

The effects are synthesized at start (see sfx.py) and the songs rendered in the background (see library.py); both
reach Panda3D as WAV files in a folder in memory (a ramdisk mounted in Panda3D's virtual file system).
"""

import itertools

from direct.showbase.Loader import Loader
from panda3d.core import AudioManager, AudioSound, Filename, VirtualFileMountRamdisk, VirtualFileSystem

from pewpy import config
from pewpy.audio import synth
from pewpy.audio.cues import Music, Throttle
from pewpy.audio.library import Library
from pewpy.audio.sfx import EFFECTS

MOUNT = "/pewpy-audio"
COPIES = 4  # of each effect, to play over each other
FADE_OUT = 0.8  # seconds, when the song changes
PAUSED_VOLUME = 0.35  # of the music's, while the game is paused

_counter = itertools.count()


def _mounted() -> VirtualFileSystem:
    vfs = VirtualFileSystem.getGlobalPtr()
    if not vfs.isDirectory(Filename(MOUNT)):
        vfs.mount(VirtualFileMountRamdisk(), Filename(MOUNT), 0)
    return vfs


class Audio:
    def __init__(
        self, loader: Loader, sfx_manager: AudioManager | None, music_manager: AudioManager | None, library: Library
    ) -> None:
        """Without audio managers (or with ones that found no sound device), it's all silent."""
        self.loader = loader
        self.library = library
        self.music_manager = music_manager
        self.vfs = _mounted()
        self.throttle = Throttle()
        self.effects: dict[str, list[AudioSound]] = {}
        self.turn: dict[str, int] = {}
        self.enabled = sfx_manager is not None and sfx_manager.isValid()
        if self.enabled:
            for name, make in EFFECTS.items():
                path = Filename(f"{MOUNT}/sfx-{name}.wav")
                self.vfs.writeFile(path, synth.wav_bytes(make()), False)
                copies = 1 if name == "laser" else COPIES
                loaded = [loader.loadSfx(path) for _ in range(copies)]
                self.effects[name] = [sound for sound in loaded if sound is not None]
                for sound in self.effects[name]:
                    sound.setVolume(config.SFX_VOLUME)
            for hum in self.effects["laser"]:
                hum.setLoop(True)
        self.laser_on = False
        self.music_on = config.MUSIC_ON
        self.wanted: Music | None = None  # the song that should be playing
        self.quiet = False
        self.playing: Music | None = None
        self.song: AudioSound | None = None
        self.song_path: Filename | None = None
        self.fading: list[tuple[AudioSound, Filename, float]] = []  # songs fading out: (sound, file, volume)

    def play(self, name: str) -> None:
        copies = self.effects.get(name)
        if not copies or not self.throttle.allow(name):
            return
        turn = self.turn.get(name, 0)
        self.turn[name] = (turn + 1) % len(copies)
        copies[turn].play()

    def play_all(self, names: list[str]) -> None:
        for name in names:
            self.play(name)

    def set_laser(self, on: bool) -> None:
        if on == self.laser_on or not self.effects.get("laser"):
            return
        self.laser_on = on
        hum = self.effects["laser"][0]
        if on:
            hum.play()
        else:
            hum.stop()

    def set_music(self, music: Music, quiet: bool = False) -> None:
        """The song to play (from its start when it changes); `quiet` lowers it (paused)."""
        self.quiet = quiet
        if music != self.wanted:
            self.wanted = music
            self.library.request(music.song, music.loop)
        self._apply_volume()

    def toggle_music(self) -> None:
        self.music_on = not self.music_on
        self._apply_volume()

    def _volume(self) -> float:
        if not self.music_on:
            return 0.0
        return config.MUSIC_VOLUME * (PAUSED_VOLUME if self.quiet else 1.0)

    def _apply_volume(self) -> None:
        if self.song is not None:
            self.song.setVolume(self._volume())

    def update(self, dt: float) -> None:
        self.throttle.update(dt)
        if self.wanted != self.playing:
            self._fade_out()
            self._start_wanted()
        still = []
        for sound, path, volume in self.fading:
            volume -= dt / FADE_OUT * config.MUSIC_VOLUME
            if volume <= 0:
                sound.stop()
                self.vfs.deleteFile(path)
            else:
                sound.setVolume(volume)
                still.append((sound, path, volume))
        self.fading = still

    def _fade_out(self) -> None:
        if self.song is not None and self.song_path is not None:
            self.fading.append((self.song, self.song_path, self.song.getVolume()))
        self.song = self.song_path = None
        self.playing = None

    def _start_wanted(self) -> None:
        music = self.wanted
        if music is None or self.music_manager is None or not self.music_manager.isValid():
            return
        wav = self.library.take(music.song, music.loop)
        if wav is None:  # still rendering (or there's no such song): tried again next frame
            return
        path = Filename(f"{MOUNT}/music-{music.song}-{next(_counter)}.wav")  # a new name: not a cached older one
        self.vfs.writeFile(path, wav, False)
        self.library.forget(music.song, music.loop)
        song = self.loader.loadMusic(path)
        if song is None:
            self.vfs.deleteFile(path)
            self.playing = music  # can't be played: not tried again
            return
        song.setLoop(music.loop)
        song.setVolume(self._volume())
        song.play()
        self.song, self.song_path, self.playing = song, path, music

    def stop(self) -> None:
        self.set_laser(False)
        for sound, path, _ in self.fading:
            sound.stop()
            self.vfs.deleteFile(path)
        self.fading = []
        if self.song is not None and self.song_path is not None:
            self.song.stop()
            self.vfs.deleteFile(self.song_path)
        self.song = self.song_path = None
        self.playing = self.wanted = None
