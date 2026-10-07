"""The songs composed from their plans."""

import pytest

from pewpy.audio import midi
from pewpy.audio.midi import DRUMS
from pewpy.makers.songs.band import LEAD
from pewpy.makers.songs.compose import compose, midi_file
from pewpy.makers.songs.plans import PLANS, TEMPO_CHANGE, Plan, describe, vary


@pytest.mark.parametrize("plan", PLANS, ids=lambda plan: plan.name)
def test_every_plan_makes_a_midi_file_the_game_reads(plan: Plan) -> None:
    song = midi.read(midi_file(plan))
    assert song.tempo == pytest.approx(plan.tempo, rel=1e-5)
    assert song.notes
    assert any(note.channel == DRUMS for note in song.notes)
    assert all(1 <= note.velocity <= 127 for note in song.notes)


def test_the_same_seed_makes_the_same_song_and_another_seed_a_new_tune() -> None:
    plan = PLANS[1]
    assert compose(plan) == compose(plan)
    assert compose(plan, 7) == compose(plan, 7)
    tune = [note for note in compose(plan).notes if note.channel == LEAD]
    assert tune != [note for note in compose(plan, 7).notes if note.channel == LEAD]


def test_a_song_lasts_its_sections_and_a_jingle_its_chords() -> None:
    song = compose(PLANS[0])
    assert song.length == 4.0 * sum(bars for _, bars in PLANS[0].sections)
    lose = next(plan for plan in PLANS if plan.jingle == "lose")
    assert compose(lose).length == 4.0 * len(lose.progression)


def test_a_new_song_differs_from_the_start_in_key_tempo_chords_and_arrangement() -> None:
    plan = PLANS[0]
    songs = [midi.read(midi_file(plan, seed)) for seed in range(6)]
    intros = {tuple((n.start, n.pitch) for n in song.notes if n.start < 16) for song in [*songs, compose(plan)]}
    assert len(intros) == 7  # every new song sounds different from its first bar
    varied = [vary(plan, seed) for seed in range(20)]
    for field in ("key", "tempo", "progression", "drums", "bass", "arp", "brass"):
        assert len({getattr(each, field) for each in varied}) > 1, field
    assert all(abs(each.tempo - plan.tempo) <= plan.tempo * TEMPO_CHANGE + 0.5 for each in varied)
    assert {each.sections for each in varied} == {plan.sections}


def test_a_new_jingle_keeps_its_chords_in_another_key() -> None:
    win = next(plan for plan in PLANS if plan.jingle == "win")
    new = vary(win, 3)
    assert new.progression == win.progression
    assert (new.drums, new.bass, new.arp) == (win.drums, win.bass, win.arp)


def test_a_songs_file_is_titled_with_its_key_and_chords() -> None:
    plan = PLANS[1]
    assert midi.read(midi_file(plan)).title == "Starlit Orbit | E minor | i VI VII i"
    new = vary(plan, 5)
    assert midi.read(midi_file(plan, 5)).title == describe(new)
