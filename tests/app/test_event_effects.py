import pytest

from pewpy.app import PewPewApp
from pewpy.app.entity_models import SECONDARY_COLORS
from pewpy.app.event_effects import DISARMED_EXPLOSION_SIZE, EVENT_EFFECTS, event_effect
from pewpy.game.events import Event
from pewpy.graphics import models
from pewpy.graphics.effects.blast import Blast
from pewpy.graphics.effects.burn import Burn
from pewpy.graphics.effects.explosion import Explosion
from pewpy.graphics.effects.impact import Impact
from tests.app.driving import play


def test_every_event_plays_its_effect(app: PewPewApp, monkeypatch: pytest.MonkeyPatch) -> None:
    play(app)
    played = []
    monkeypatch.setattr(app.effects, "play", played.append)
    events = [
        Event("impact", 0.0, 0.0, source="enemy"),
        Event("impact", 0.0, 0.0, source="player"),
        Event("explosion", 0.0, 0.0, 0.1, "drone"),
        Event("explosion", 0.0, 0.0, 0.1, "unknown"),
        Event("blast", 0.0, 0.0, 0.1),
        Event("burn", 0.0, 0.0),
        Event("disarmed", 0.0, 0.0, source="turret"),
        Event("hurt", 0.0, 0.0),  # sound only
    ]
    app._show_events(events, 1 / 60)
    assert len(played) == 7


def test_shots_hitting_throw_sparks_back_the_way_they_came() -> None:
    from_enemy = event_effect(Event("impact", 0.1, 0.2, source="enemy"), 1 / 60, {})
    from_player = event_effect(Event("impact", 0.1, 0.2, source="player"), 1 / 60, {})
    assert from_enemy == Impact(0.1, 0.2, towards=-1.0)
    assert from_player == Impact(0.1, 0.2, towards=1.0)


def test_an_explosion_throws_debris_of_what_blew_up_or_metal() -> None:
    red = (1.0, 0.0, 0.0, 1.0)
    known = event_effect(Event("explosion", 0.0, 0.0, 0.1, "drone"), 1 / 60, {"drone": (red,)})
    unknown = event_effect(Event("explosion", 0.0, 0.0, 0.1, "rock"), 1 / 60, {"drone": (red,)})
    assert known == Explosion(0.0, 0.0, 0.1, (red,))
    assert unknown == Explosion(0.0, 0.0, 0.1, (models.METAL,))


def test_blasts_burns_and_lost_weapons_have_their_effects() -> None:
    assert event_effect(Event("blast", 0.1, 0.2, 0.15), 1 / 60, {}) == Blast(0.1, 0.2, 0.15)
    assert event_effect(Event("burn", 0.1, 0.2), 0.02, {}) == Burn(0.1, 0.2, 0.02)
    disarmed = event_effect(Event("disarmed", 0.1, 0.2, source="turret"), 1 / 60, {})
    assert disarmed == Explosion(0.1, 0.2, DISARMED_EXPLOSION_SIZE, (SECONDARY_COLORS["turret"], models.METAL))


@pytest.mark.parametrize("kind", ["shot", "pickup", "boss", "hurt", "zap"])
def test_other_events_only_sound(kind: str) -> None:
    assert kind not in EVENT_EFFECTS
    assert event_effect(Event(kind, 0.0, 0.0), 1 / 60, {}) is None
