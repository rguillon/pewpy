"""Playing the sound effects and music through Panda3D's audio (OpenAL).

The effects are synthesized at start (see sfx/) and reach Panda3D as WAV files in a folder in memory (a ramdisk
mounted in Panda3D's virtual file system). The songs are rendered in the background (see library.py) and played
from their WAV file in the cache (or, without a cache, from the ramdisk).

A song is streamed from its file, and OpenAL keeps finished songs in its own cache, their streams still open: a
song's file must never be deleted or rewritten while the game runs (deleting one from the ramdisk made the game
crash when OpenAL later let go of it). So each song's file is made once, under a name of its own, and kept.
"""

from pathlib import Path

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


def _mounted() -> VirtualFileSystem:
    vfs = VirtualFileSystem.getGlobalPtr()
    if not vfs.isDirectory(Filename(MOUNT)):
        vfs.mount(VirtualFileMountRamdisk(), Filename(MOUNT), 0)
    return vfs


class Audio:
    """The game's sounds: the effects and the music."""

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
                self.vfs.writeFile(path, synth.wav_bytes(make()), auto_wrap=False)
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
        self.fading: list[tuple[AudioSound, float]] = []  # songs fading out: (sound, volume)
        self.song_files: dict[tuple[str, bool], Filename] = {}  # each song's file, once it's made: kept

    def play(self, name: str) -> None:
        """Play a sound effect (a copy of it, so the same sound can overlap), unless it played too recently."""
        copies = self.effects.get(name)
        if not copies or not self.throttle.allow(name):
            return
        turn = self.turn.get(name, 0)
        self.turn[name] = (turn + 1) % len(copies)
        copies[turn].play()

    def play_all(self, names: list[str]) -> None:
        """Play these sound effects."""
        for name in names:
            self.play(name)

    def set_laser(self, on: bool) -> None:
        """Start or stop the laser's hum."""
        if on == self.laser_on or not self.effects.get("laser"):
            return
        self.laser_on = on
        hum = self.effects["laser"][0]
        if on:
            hum.play()
        else:
            hum.stop()

    def set_music(self, music: Music, quiet: bool = False) -> None:
        """Set the song to play (from its start when it changes); `quiet` lowers it (paused)."""
        self.quiet = quiet
        if music != self.wanted:
            self.wanted = music
            self.library.request(music.song, music.loop)
        self._apply_volume()

    def toggle_music(self) -> None:
        """Turn the music on or off."""
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
        """Move the sounds on: songs fading out, the wanted song starting when it's ready."""
        self.throttle.update(dt)
        if self.wanted != self.playing:
            self._fade_out()
            self._start_wanted()
        still = []
        for sound, old_volume in self.fading:
            volume = old_volume - dt / FADE_OUT * config.MUSIC_VOLUME
            if volume <= 0:
                sound.stop()
            else:
                sound.setVolume(volume)
                still.append((sound, volume))
        self.fading = still

    def _fade_out(self) -> None:
        if self.song is not None:
            self.fading.append((self.song, self.song.getVolume()))
        self.song = None
        self.playing = None

    def _song_file(self, music: Music) -> Filename | None:
        """Return the song's WAV file (None while it's still rendering, or if there's no such song)."""
        key = (music.song, music.loop)
        if key in self.song_files:
            return self.song_files[key]
        wav = self.library.take(music.song, music.loop)
        if wav is None:
            return None
        cached = self.library.cached(music.song, music.loop)
        if cached is not None:
            path = Filename.fromOsSpecific(str(Path(cached).resolve()))
        else:  # no cache folder: a copy in memory, for as long as the game runs
            path = Filename(f"{MOUNT}/music-{music.song}-{'loop' if music.loop else 'once'}.wav")
            self.vfs.writeFile(path, wav, auto_wrap=False)
        self.library.forget(music.song, music.loop)
        self.song_files[key] = path
        return path

    def _start_wanted(self) -> None:
        music = self.wanted
        if music is None or self.music_manager is None or not self.music_manager.isValid():
            return
        path = self._song_file(music)
        if path is None:  # still rendering (or there's no such song): tried again next frame
            return
        song = self.loader.loadMusic(path)
        if song is None:
            self.playing = music  # can't be played: not tried again
            return
        song.setLoop(music.loop)
        song.setVolume(self._volume())
        song.play()
        self.song, self.playing = song, music

    def stop(self) -> None:
        """Stop every sound."""
        self.set_laser(False)
        for sound, _ in self.fading:
            sound.stop()
        self.fading = []
        if self.song is not None:
            self.song.stop()
        self.song = None
        self.playing = self.wanted = None
