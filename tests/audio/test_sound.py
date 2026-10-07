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

    def setLoop(self, loop: bool) -> None:  # noqa: N802 - like Panda3D's
        self.loop = loop

    def setVolume(self, volume: float) -> None:  # noqa: N802 - like Panda3D's
        self.volume = volume

    def getVolume(self) -> float:  # noqa: N802 - like Panda3D's
        return self.volume

    def play(self) -> None:
        self.playing = True

    def stop(self) -> None:
        self.playing = False


class FakeLoader:
    def __init__(self, loads: bool = True) -> None:
        self.loaded: list[Filename] = []
        self.loads = loads  # False: every song fails to load

    def loadMusic(self, path: Filename) -> FakeSound | None:  # noqa: N802 - like Panda3D's
        self.loaded.append(Filename(path))
        return FakeSound(path) if self.loads else None

    def loadSfx(self, path: Filename) -> FakeSound:  # noqa: N802 - like Panda3D's
        return FakeSound(path)


class FakeManager:
    def isValid(self) -> bool:  # noqa: N802 - like Panda3D's
        return True


def play_until(audio: Audio, song: str) -> None:
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
def test_a_songs_file_is_made_once_and_never_deleted(songs: Path, tmp_path: Path, with_cache: bool) -> None:
    """OpenAL keeps finished songs' streams open: deleting or replacing their file crashed the game."""
    loader = FakeLoader()
    library = Library(songs, tmp_path / "cache" if with_cache else None)
    audio = Audio(cast("Any", loader), None, cast("Any", FakeManager()), library)  # fakes for Panda3D's
    for song in ("one", "two", "one", "two", "one"):
        play_until(audio, song)
    first, second = loader.loaded[0], loader.loaded[1]
    assert loader.loaded == [first, second, first, second, first]  # the same file each time
    vfs = VirtualFileSystem.getGlobalPtr()
    assert vfs.exists(first)
    assert vfs.exists(second)
    if with_cache:
        assert str(tmp_path / "cache") in first.toOsSpecific()  # played from the cache, not a copy


def fake(sound: object) -> FakeSound:
    """One of the fake sounds, as the Audio holds it (an AudioSound for the type checker)."""
    return cast("FakeSound", sound)


def test_effects_play_in_turns_and_not_too_often(songs: Path) -> None:
    audio = Audio(cast("Any", FakeLoader()), cast("Any", FakeManager()), None, Library(songs, None))
    assert audio.enabled
    first, second = (fake(sound) for sound in audio.effects["menu_move"][:2])
    audio.play("menu_move")
    assert first.playing
    audio.play("menu_move")  # too soon after itself: not again
    assert not second.playing
    audio.update(1.0)
    audio.play_all(["menu_move", "no such sound"])
    assert second.playing


def test_the_laser_hums_while_it_fires(songs: Path) -> None:
    audio = Audio(cast("Any", FakeLoader()), cast("Any", FakeManager()), None, Library(songs, None))
    hum = fake(audio.effects["laser"][0])
    audio.set_laser(True)
    assert hum.playing
    assert hum.loop
    audio.set_laser(True)  # already on
    audio.set_laser(False)
    assert not hum.playing


def test_music_off_mutes_the_song_and_stop_stops_everything(songs: Path) -> None:
    loader = FakeLoader()
    audio = Audio(cast("Any", loader), None, cast("Any", FakeManager()), Library(songs, None))
    play_until(audio, "one")
    assert audio.song is not None
    song = fake(audio.song)
    audio.toggle_music()
    assert song.getVolume() == 0.0
    audio.toggle_music()
    audio.set_music(Music("two"))
    audio.update(1 / 30)  # "one" fading out, "two" not rendered yet
    assert audio.fading
    assert audio.song is None
    audio.stop()
    assert not song.playing
    assert audio.fading == []
    assert audio.playing is None
    assert audio.library.wait()
    play_until(audio, "two")
    audio.stop()
    assert audio.song is None


def test_without_music_or_a_song_that_wont_load_nothing_plays(songs: Path) -> None:
    silent = Audio(cast("Any", FakeLoader()), None, None, Library(songs, None))
    silent.set_music(Music("one"))
    silent.update(1 / 30)
    assert silent.playing is None
    loader = FakeLoader(loads=False)
    broken = Audio(cast("Any", loader), None, cast("Any", FakeManager()), Library(songs, None))
    broken.set_music(Music("one"))
    assert broken.library.wait()
    broken.update(1 / 30)
    assert broken.playing == Music("one")
    assert broken.song is None
    assert len(loader.loaded) == 1


def test_a_song_added_in_memory_plays_and_a_changed_song_is_rendered_again(songs: Path, tmp_path: Path) -> None:
    loader = FakeLoader()
    library = Library(songs, tmp_path / "cache")
    audio = Audio(cast("Any", loader), None, cast("Any", FakeManager()), library)  # fakes for Panda3D's
    new = Song(tempo=240.0, notes=[Note(0, 1, 67)], programs={0: 81}, length=1.0)
    library.add("new-one", midi.write(new))
    assert library.has("new-one")
    play_until(audio, "new-one")
    play_until(audio, "one")
    first = loader.loaded[-1]
    (songs / "one.mid").write_bytes(midi.write(new))  # saved over
    audio.forget_song("one")
    play_until(audio, "two")
    play_until(audio, "one")
    assert loader.loaded[-1] != first  # its new file: the old one is kept
    assert VirtualFileSystem.getGlobalPtr().exists(first)
