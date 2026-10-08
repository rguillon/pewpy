"""What each game event looks like: the effect it plays, if any (the kinds are the ones pewpy.game.events names).

This is one place to look for every event's effect, beside `cues.py` for every event's sound: an event is added here
and there, and nowhere else. An event with no effect here (a shot, a pickup, a boss) only sounds.
"""

from collections.abc import Callable, Mapping

from pewpy.app.entity_models import SECONDARY_COLORS
from pewpy.game.events import Event
from pewpy.graphics import models
from pewpy.graphics.effects import Effect
from pewpy.graphics.effects.blast import Blast
from pewpy.graphics.effects.burn import Burn
from pewpy.graphics.effects.explosion import Explosion
from pewpy.graphics.effects.impact import Impact

DebrisColors = Mapping[str, tuple[models.Color, ...]]  # what blew up, by the event's source

DISARMED_EXPLOSION_SIZE = 0.08  # the secondary weapon blowing up on the ship


def _impact(event: Event, dt: float, debris: DebrisColors) -> Effect:
    """Make sparks flying back the way the shot came: down from enemies, up from the player."""
    _ = dt, debris  # every effect takes the same three, and only some use all of them
    return Impact(event.x, event.y, towards=-1.0 if event.source == "enemy" else 1.0)


def _explosion(event: Event, dt: float, debris: DebrisColors) -> Effect:
    """Make a burst of debris in the colors of whatever blew up: a player's ship, or an enemy kind or drawing."""
    _ = dt
    return Explosion(event.x, event.y, event.size, debris.get(event.source, (models.METAL,)))


def _blast(event: Event, dt: float, debris: DebrisColors) -> Effect:
    """Make a missile exploding, its splash radius wide."""
    _ = dt, debris
    return Blast(event.x, event.y, event.size)


def _burn(event: Event, dt: float, debris: DebrisColors) -> Effect:
    """Make the flame of the laser burning an enemy: it lives as long as the beam does, so it takes `dt`."""
    _ = debris
    return Burn(event.x, event.y, dt)


def _disarmed(event: Event, dt: float, debris: DebrisColors) -> Effect:
    """Make the secondary weapon blowing up on the ship, in its own colors and the ship's."""
    _ = dt, debris
    return Explosion(event.x, event.y, DISARMED_EXPLOSION_SIZE, (SECONDARY_COLORS[event.source], models.METAL))


# Every effect takes the event, the frame's seconds and what blew up (see DebrisColors), so they can be looked up alike.
MakeEffect = Callable[[Event, float, DebrisColors], Effect]

# Each kind of event that has an effect: how to make it.
EVENT_EFFECTS: dict[str, MakeEffect] = {
    "impact": _impact,
    "explosion": _explosion,
    "blast": _blast,
    "burn": _burn,
    "disarmed": _disarmed,
}


def event_effect(event: Event, dt: float, debris: DebrisColors) -> Effect | None:
    """Return the effect for `event`, or None when it has none (a shot, a pickup, a boss coming)."""
    make = EVENT_EFFECTS.get(event.kind)
    return make(event, dt, debris) if make is not None else None


__all__ = ["DISARMED_EXPLOSION_SIZE", "EVENT_EFFECTS", "event_effect"]
