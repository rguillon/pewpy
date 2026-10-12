import pytest

from pewpy.audio.midi import DRUMS
from pewpy.generators.music.band import CRASH, KICK, OPEN_HAT, SNARE, TOMS
from pewpy.generators.music.tracks.drums import drums, hats
from tests.generators.music.writing import writer


def pitches(style: str, **asked: bool) -> list[int]:
    written = writer(drums=style)
    drums(
        written, 0.0, 1, busy=asked.get("busy", False), fill=asked.get("fill", False), crash=asked.get("crash", False)
    )
    assert all(note.channel == DRUMS for note in written.notes)
    return [note.pitch for note in written.notes]


@pytest.mark.parametrize(("style", "kicks", "snares"), [("half", 2, 1), ("standard", 3, 2), ("four", 4, 2)])
def test_each_style_has_its_kicks_and_snares(style: str, kicks: int, snares: int) -> None:
    played = pitches(style)
    assert (played.count(KICK), played.count(SNARE)) == (kicks, snares)


def test_a_crash_starts_and_a_fill_rolls_down_the_toms_at_the_end() -> None:
    played = pitches("standard", fill=True, crash=True)
    assert played[0] == CRASH
    toms = [pitch for pitch in played if pitch in TOMS]
    assert len(toms) == 8
    assert toms == sorted(toms, reverse=True)


def test_busy_hats_play_sixteenths_and_four_on_the_floor_opens_them_offbeat() -> None:
    quiet, busy = writer(), writer()
    hats(quiet, 0.0, busy=False, until=4)
    hats(busy, 0.0, busy=True, until=4)
    assert (len(quiet.notes), len(busy.notes)) == (8, 16)
    four = writer(drums="four")
    hats(four, 0.0, busy=False, until=4)
    assert [note.pitch for note in four.notes].count(OPEN_HAT) == 4
    short = writer()
    hats(short, 0.0, busy=False, until=2)
    assert len(short.notes) == 4
