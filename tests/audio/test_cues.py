import pytest

from pewpy.audio import cues
from pewpy.audio.cues import Music, Throttle, event_sound, event_sounds, music
from pewpy.game.states import State
from pewpy.game.world import Event


@pytest.mark.parametrize(
    ("event", "sound"),
    [
        (Event("shot", 0, 0, source="bullets"), "shot"),
        (Event("shot", 0, 0, source="missiles"), "missile"),
        (Event("impact", 0, 0, source="enemy"), "hit"),
        (Event("impact", 0, 0, source="player"), None),  # sounds as the "hurt" that comes with it
        (Event("hurt", 0, 0), "hurt"),
        (Event("explosion", 0, 0, 0.06, "Drone"), "explosion_small"),
        (Event("explosion", 0, 0, 0.2, "Bomber"), "explosion"),
        (Event("explosion", 0, 0, 0.8, "warden"), "explosion_big"),
        (Event("explosion", 0, 0, 0.2, "Player"), "player_explosion"),
        (Event("blast", 0, 0, 0.1), "blast"),
        (Event("shot", 0, 0, source="turret"), "shot"),
        (Event("zap", 0, 0), "zap"),
        (Event("disarmed", 0, 0, source="turret"), "disarmed"),
        (Event("pickup", 0, 0, source="lightning"), "pickup"),
        (Event("burn", 0, 0), None),
        (Event("pickup", 0, 0, source="repair"), "repair"),
        (Event("pickup", 0, 0, source="laser"), "pickup"),
        (Event("pickup", 0, 0, source="life"), "extra_life"),
        (Event("boss", 0, 0, source="warden"), "alarm"),
    ],
)
def test_each_event_has_its_sound(event, sound):
    assert event_sound(event) == sound


def test_a_sound_is_played_once_for_many_events():
    events = [Event("impact", 0, 0, source="enemy")] * 5 + [Event("shot", 0, 0, source="bullets")]
    assert event_sounds(events) == ["hit", "shot"]


def test_a_sound_doesnt_start_again_too_soon():
    throttle = Throttle()
    assert throttle.allow("shot")
    assert not throttle.allow("shot")
    assert throttle.allow("hit")  # others are free
    throttle.update(cues.MIN_GAP)
    assert throttle.allow("shot")


@pytest.mark.parametrize(
    ("state", "world", "boss", "expected"),
    [
        (State.MAIN_MENU, 0, False, Music("title")),
        (State.LEVEL_SELECT, 3, False, Music("title")),
        (State.PLAYING, 0, False, Music("world_1")),
        (State.PLAYING, 4, False, Music("world_5")),
        (State.PLAYING, 7, False, Music("world_8")),
        (State.PAUSED, 2, False, Music("world_3")),
        (State.PLAYING, 2, True, Music("boss")),
        (State.LEVEL_COMPLETE, 2, True, Music("level_complete", loop=False)),
        (State.GAME_OVER, 0, False, Music("game_over", loop=False)),
    ],
)
def test_each_screen_has_its_song(state, world, boss, expected):
    assert music(state, world, boss) == expected
