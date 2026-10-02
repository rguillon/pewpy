"""What happens during play, for the effects and the sounds."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Event:
    """Something the effects show (see graphics/effects/) or the sounds play (see audio/cues.py), collected during one
    update.

    kind: "impact" (a shot hit `source`: "enemy" or "player"), "explosion" (`source` blew up: an enemy
    kind like "drone", a drawing like "dart" or "warden", or "Player"), "blast" (a missile exploded, `size` = its splash
    radius), "burn" (the laser is burning an enemy at x, y), "shot" (the player fired `source`: "bullets",
    "missiles" or "turret"), "zap" (the lightning gun struck), "hurt" (the player was hit), "disarmed" (a hit took
    the player's secondary weapon `source` instead of health), "pickup" (the player picked up `source`: "repair",
    "life", a weapon or a secondary weapon) or "boss" (a boss came).
    """

    kind: str
    x: float
    y: float
    size: float = 0.0
    source: str = ""
