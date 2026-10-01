from pathlib import Path
from typing import Any, cast

import pytest
from panda3d.core import Filename, VirtualFileSystem

from pewpy.audio import midi
from pewpy.audio.cues import Music
from pewpy.audio.library import Library
from pewpy.audio.midi import Note, Song
from pewpy.audio.sound import FADE_OUT, Audio


class FakeSound:
    def __init__(self, path: Filename) -> None:
        self.path = path
        self.volume = 1.0
        self.playing = False

    def setLoop(self, loop: bool) -> None:
        self.loop = loop

    def setVolume(self, volume: float) -> None:
        self.volume = volume

    def getVolume(self) -> float:
        return self.volume

    def play(self) -> None:
        self.playing = True

    def stop(self) -> None:
        self.playing = False


class FakeLoader:
    def __init__(self) -> None:
        self.loaded: list[Filename] = []

    def loadMusic(self, path: Filename) -> FakeSound:
        self.loaded.append(Filename(path))
        return FakeSound(path)


class FakeManager:
    def isValid(self) -> bool:
        return True


def play_until(audio: Audio, song: str, loader: FakeLoader) -> None:
    audio.set_music(Music(song))
    assert audio.library.wait()
    for _ in range(round(2 * FADE_OUT * 30) + 2):
        audio.update(1 / 30)
    assert audio.playing == Music(song)


@pytest.fixture
def songs(tmp_path: Path) -> Path:
    folder = tmp_path / "music"
    folder.mkdir()
    for name, pitch in (("one", 60), ("two", 64)):
        song = Song(tempo=240.0, notes=[Note(0, 1, pitch)], programs={0: 81}, length=1.0)
        (folder / f"{name}.mid").write_bytes(midi.write(song))
    return folder


@pytest.mark.parametrize("with_cache", [True, False])
def test_a_songs_file_is_made_once_and_never_deleted(songs, tmp_path, with_cache):
    """OpenAL keeps finished songs' streams open: deleting or replacing their file crashed the game."""
    loader = FakeLoader()
    library = Library(songs, tmp_path / "cache" if with_cache else None)
    audio = Audio(cast("Any", loader), None, cast("Any", FakeManager()), library)  # fakes for Panda3D's
    for song in ("one", "two", "one", "two", "one"):
        play_until(audio, song, loader)
    first, second = loader.loaded[0], loader.loaded[1]
    assert loader.loaded == [first, second, first, second, first]  # the same file each time
    vfs = VirtualFileSystem.getGlobalPtr()
    assert vfs.exists(first) and vfs.exists(second)  # still there after their fades
    if with_cache:
        assert str(tmp_path / "cache") in first.toOsSpecific()  # played from the cache, not a copy
