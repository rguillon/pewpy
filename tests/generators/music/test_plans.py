from pewpy.generators.music.harmony import ARPS, CHORDS
from pewpy.generators.music.plans import BASS_STYLES, DRUM_STYLES, PLANS, PROGRESSIONS, describe, vary


def test_a_new_jingle_keeps_its_chords_in_another_key() -> None:
    win = next(plan for plan in PLANS if plan.jingle == "win")
    new = vary(win, 3)
    assert new.progression == win.progression
    assert (new.drums, new.bass, new.arp) == (win.drums, win.bass, win.arp)


def test_every_plan_is_named_once_and_plays_what_the_band_knows() -> None:
    names = [plan.name for plan in PLANS]
    assert len(set(names)) == len(names)
    for plan in PLANS:
        assert set(plan.progression) <= set(CHORDS)
        assert plan.drums in DRUM_STYLES
        assert plan.bass in BASS_STYLES
        assert plan.arp in ARPS
        assert plan.jingle in ("", "win", "lose")


def test_a_new_song_picks_its_chords_among_the_progressions() -> None:
    song = next(plan for plan in PLANS if not plan.jingle)
    assert all(vary(song, seed).progression in PROGRESSIONS for seed in range(10))
    assert all(set(progression) <= set(CHORDS) for progression in PROGRESSIONS)


def test_a_title_says_the_key_and_the_chords() -> None:
    plan = PLANS[1]
    assert describe(plan) == f"{plan.title} | {plan.key} minor | {' '.join(plan.progression)}"
