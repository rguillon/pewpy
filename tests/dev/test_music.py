"""The Dev menu's music browser, without the app."""

import random
import shutil
from pathlib import Path

import pytest

from pewpy import data
from pewpy.audio import midi
from pewpy.audio.cues import Music
from pewpy.dev import music
from pewpy.dev.music import MusicBrowser
from pewpy.makers.songs.plans import PLANS


@pytest.fixture
def music_copy(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Give the browser a copy of the game's songs, to save over."""
    shutil.copytree(data.SOURCE_DATA / "music", tmp_path / "music")
    monkeypatch.setattr(music, "data_folder", lambda: tmp_path)
    return tmp_path / "music"


@pytest.mark.usefixtures("music_copy")
def test_left_and_right_go_from_song_to_song_and_play_it() -> None:
    browser = MusicBrowser(random.Random(1))
    assert browser.plan is PLANS[0]
    assert browser.music() == Music("title")
    browser.move(-1)
    assert browser.plan is PLANS[-1]
    assert browser.music() == Music("game_over", loop=False)  # a jingle plays once
    browser.move(1)
    assert browser.index == 0
    details = browser.details()
    assert details.startswith('"Neon Horizon": A minor, 96 bpm')  # a file titled without them: its plan's
    assert "loops" in details
    assert "Chords: i VImaj7 III VII" in details


@pytest.mark.usefixtures("music_copy")
def test_space_makes_a_new_song_that_plays_under_a_name_of_its_own() -> None:
    browser = MusicBrowser(random.Random(1))
    browser.move(1)
    new = browser.generate()
    assert browser.new == new
    assert midi.read(new).notes
    assert browser.music().song == f"new-world_1-{browser.seed}"
    assert browser.data() == new
    title, key, chords = midi.read(new).title.split(" | ")
    assert browser.details().startswith(f'"{title}": {key}, ')
    assert browser.details().endswith(f"Chords: {chords}")
    browser.move(1)  # not saved: lost
    assert browser.new is None
    assert browser.music() == Music("world_2")


def test_enter_saves_the_new_song_in_place_of_the_song(music_copy: Path) -> None:
    browser = MusicBrowser(random.Random(1))
    old = (music_copy / "title.mid").read_bytes()
    browser.save()  # nothing new: nothing saved
    assert not browser.saved
    new = browser.generate()
    assert new != old
    browser.save()
    assert browser.saved
    assert (music_copy / "title.mid").read_bytes() == new
    assert browser.music().song.startswith("new-title-")  # it goes on playing


def test_a_song_without_a_file_says_so(music_copy: Path) -> None:
    (music_copy / "title.mid").unlink()
    assert MusicBrowser().details() == '"Neon Horizon": A minor, 96 bpm, no file yet (loops). Chords: i VImaj7 III VII'
