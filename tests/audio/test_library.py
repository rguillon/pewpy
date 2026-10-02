from pathlib import Path

import pytest

from pewpy.audio import library as library_module
from pewpy.audio import midi
from pewpy.audio.library import Library
from pewpy.audio.midi import Note, Song
from pewpy.data import data_folder

GAME_SONGS = {"title", "boss", "level_complete", "game_over", *(f"world_{n}" for n in range(1, 9))}


@pytest.fixture
def songs(tmp_path: Path) -> Path:
    folder = tmp_path / "music"
    folder.mkdir()
    song = Song(tempo=240.0, notes=[Note(0, 1, 60), Note(1, 1, 64)], programs={0: 81}, length=2.0)
    (folder / "tune.mid").write_bytes(midi.write(song))
    return folder


def test_the_game_has_its_songs() -> None:
    names = Library(data_folder() / "music", None).names()
    assert set(names) >= GAME_SONGS


def test_a_song_is_rendered_once_then_read_from_the_cache(
    songs: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    library = Library(songs, tmp_path / "cache")
    first = library.wav("tune")
    assert first[:4] == b"RIFF"
    assert len(list((tmp_path / "cache").glob("tune-*.wav"))) == 1

    def fail(*_: object) -> bytes:
        raise AssertionError

    monkeypatch.setattr(library_module, "render_wav", fail)
    assert library.wav("tune") == first


def test_a_changed_song_is_rendered_again_replacing_the_old_one(songs: Path, tmp_path: Path) -> None:
    library = Library(songs, tmp_path / "cache")
    library.wav("tune")
    (songs / "tune.mid").write_bytes(midi.write(Song(tempo=200.0, notes=[Note(0, 1, 62)], programs={0: 81})))
    library.wav("tune")
    assert len(list((tmp_path / "cache").glob("tune-*.wav"))) == 1


def test_songs_are_rendered_in_the_background(songs: Path) -> None:
    library = Library(songs, None)
    assert library.take("tune") is None  # not yet: requested
    assert library.wait()
    wav = library.take("tune")
    assert wav is not None
    assert wav[:4] == b"RIFF"
    library.forget("tune")
    assert "tune" not in {name for name, _ in library.ready}


def test_a_missing_or_broken_song_is_never_ready(songs: Path) -> None:
    (songs / "broken.mid").write_bytes(b"not midi")
    library = Library(songs, None)
    library.request("missing")
    library.request("broken")
    assert library.wait()
    assert library.take("missing") is None
    assert library.take("broken") is None
    assert library.failed == {"broken"}


def test_the_cache_is_in_the_users_cache_folder(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setattr(library_module.sys, "platform", "linux")
    monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path))
    assert library_module.cache_folder() == tmp_path / "pewpy" / "music"


def test_the_cache_on_windows_and_without_a_home(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setattr(library_module.sys, "platform", "win32")
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
    assert library_module.cache_folder() == tmp_path / "pewpy" / "music"
    monkeypatch.delenv("LOCALAPPDATA")
    assert library_module.cache_folder() is None
    monkeypatch.setattr(library_module.sys, "platform", "linux")
    monkeypatch.delenv("XDG_CACHE_HOME", raising=False)
    monkeypatch.setattr(library_module.Path, "home", lambda: tmp_path)
    assert library_module.cache_folder() == tmp_path / ".cache" / "pewpy" / "music"

    def homeless() -> Path:
        raise RuntimeError

    monkeypatch.setattr(library_module.Path, "home", homeless)
    assert library_module.cache_folder() is None


def test_a_folder_without_songs(tmp_path: Path) -> None:
    assert Library(tmp_path / "nowhere", None).names() == []


def test_a_song_still_plays_when_the_cache_cant_be_written(songs: Path, tmp_path: Path) -> None:
    blocked = tmp_path / "a file, not a folder"
    blocked.write_text("")
    library = Library(songs, blocked / "cache")
    assert library.wav("tune")[:4] == b"RIFF"
    assert library.cached("tune") is None
    assert library.cached("missing") is None


def test_requests_wait_their_turn_unless_wanted_first(songs: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    library = Library(songs, None)
    monkeypatch.setattr(library, "_start", lambda: None)  # nothing renders: only the queue is looked at
    (songs / "other.mid").write_bytes((songs / "tune.mid").read_bytes())
    library.request("tune", first=False)
    library.request("other", first=False)
    assert list(library._queue) == [("tune", True), ("other", True)]
    library.request("other")  # wanted now: first in line
    assert list(library._queue) == [("other", True), ("tune", True)]
    assert not library.wait(timeout=0.1)  # still waiting: it gives up
