import pytest

from pewpy.audio import midi
from pewpy.audio.midi import DRUMS
from tools import make_songs
from tools.make_songs import PLANS, compose

PLAN = {plan.name: plan for plan in PLANS}


@pytest.mark.parametrize("plan", PLANS, ids=lambda plan: plan.name)
def test_every_song_has_its_parts_in_its_key(plan):
    song = compose(plan)
    channels = {note.channel for note in song.notes}
    assert {make_songs.BASS, make_songs.PAD, make_songs.LEAD, DRUMS} <= channels
    assert song.beats == pytest.approx(song.length)
    assert all(0 <= note.start < song.length and note.length > 0 for note in song.notes)
    tonic = make_songs.NOTES[plan.key]
    if not plan.jingle:
        lead = [note.pitch for note in song.notes if note.channel == make_songs.LEAD]
        in_key = sum((pitch - tonic) % 12 in make_songs.MINOR for pitch in lead)
        assert in_key >= 0.9 * len(lead)  # the tune keeps to the key (a raised seventh on a major V aside)
        assert lead[-1] % 12 == tonic  # and ends home


def test_the_same_seed_makes_the_same_song_and_another_a_new_tune():
    plan = PLAN["world_1"]
    assert compose(plan) == compose(plan)
    tune = [note.pitch for note in compose(plan).notes if note.channel == make_songs.LEAD]
    other = [note.pitch for note in compose(plan, seed=5).notes if note.channel == make_songs.LEAD]
    assert tune != other


def test_the_tool_writes_midi_files(tmp_path, monkeypatch):
    monkeypatch.setattr("sys.argv", ["make_songs", "--only", "level_complete", "--out", str(tmp_path)])
    make_songs.main()
    song = midi.read((tmp_path / "level_complete.mid").read_bytes())
    assert song.tempo == pytest.approx(PLAN["level_complete"].tempo, rel=1e-4)
    assert song.programs[make_songs.LEAD] == make_songs.PROGRAMS[make_songs.LEAD]
