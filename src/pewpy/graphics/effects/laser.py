"""Lasers' light: streaks of light shooting along the beams, away from what fires them.

Up from the player's ship to whatever it hits, down from an enemy to past the bottom of the screen. Unlike the other
effects it lasts: it follows each beam as long as it's on.
"""

import math
import random
from collections.abc import Sequence
from dataclasses import dataclass

from pewpy.graphics.effects import BURN_COLORS, Color

PHOTON_RATE = 160.0  # per second, for the thinnest beam (wider beams send more: by the square root of the width)
PHOTON_SPEED = (2.8, 4.2)  # world units per second, along the beam
PHOTON_SIZE = (0.01, 0.02)
PHOTON_STRETCH = 4.0  # a streak is this many times longer than wide
PHOTON_WOBBLE = 0.3  # sideways wobble, as a share of the beam's width
PHOTON_WOBBLE_SPEED = 25.0  # radians per second
PHOTON_FADE = 0.15  # seconds: once the beam is cut, the streaks still flying fade out in that time
THIN_BEAM = 0.03  # the level 1 laser's width
ENEMY_BURN_COLORS: tuple[Color, ...] = ((1.0, 0.45, 0.35, 1), (1.0, 0.95, 0.9, 1), (1.0, 0.2, 0.15, 1))  # red


@dataclass(frozen=True)
class LaserGlow:
    """A laser beam this frame, as the effects see it: from `bottom` to `top` at `x`.

    `hits`: heights where it burns something. The player's (not `hostile`) goes up from its bottom; an enemy's goes down
    from its top, red. `key` tells the beams apart, from one frame to the next.
    """

    x: float
    bottom: float
    top: float
    width: float
    hits: tuple[float, ...] = ()
    hostile: bool = False
    key: int = 0

    @property
    def source(self) -> float:
        """Where it starts: the ship's nose (its bottom), or an enemy's muzzle (its top)."""
        return self.top if self.hostile else self.bottom

    @property
    def direction(self) -> int:
        """Which way the light shoots: 1 up (the player's), -1 down (an enemy's)."""
        return -1 if self.hostile else 1

    @property
    def colors(self) -> tuple[Color, ...]:
        """The light's colors: red for an enemy's laser."""
        return ENEMY_BURN_COLORS if self.hostile else BURN_COLORS


@dataclass(eq=False)
class Photon:
    """A streak of light shooting along a laser."""

    key: int  # its laser's (see LaserGlow.key)
    direction: int  # 1 up the screen, -1 down
    offset: float  # across the beam, from its middle
    distance: float  # along the beam, from where it starts
    speed: float
    size: float
    color: Color
    wave: float  # phase of its sideways wobble
    x: float = 0.0  # where it is: follows the beam while it's on, flies on straight once it's cut
    y: float = 0.0
    fade: float = 1.0  # 1 while the beam is on, then down to 0


class LaserLight:
    """The lasers' light: the streaks shooting along every laser that's on."""

    def __init__(self) -> None:
        """Start with no light: no photons, and no beam lit up."""
        self.photons: list[Photon] = []
        self.lasers: dict[int, LaserGlow] = {}

    def set(self, lasers: Sequence[LaserGlow], dt: float, rng: random.Random) -> None:
        """Set the lasers this frame.

        While one is on, streaks of light keep shooting along it from where it starts.
        """
        self.lasers = {laser.key: laser for laser in lasers}
        for laser in lasers:
            count = PHOTON_RATE * math.sqrt(laser.width / THIN_BEAM) * dt
            for _ in range(int(count) + (rng.random() < count % 1)):
                self.photons.append(
                    Photon(
                        key=laser.key,
                        direction=laser.direction,
                        offset=rng.uniform(-0.45, 0.45) * laser.width,
                        distance=rng.uniform(0.0, 0.03),
                        speed=rng.uniform(*PHOTON_SPEED),
                        size=rng.uniform(*PHOTON_SIZE),
                        color=rng.choice(laser.colors),
                        wave=rng.uniform(0.0, 2 * math.pi),
                        x=laser.x,
                        y=laser.source,
                    )
                )

    def update(self, dt: float, time: float) -> None:
        """Move the streaks `dt` seconds on (`time`: the effects' clock, for the wobble)."""
        for photon in self.photons:
            photon.distance += photon.speed * dt
            laser = self.lasers.get(photon.key)
            if laser is not None and photon.fade == 1.0:
                wobble = math.sin(photon.wave + time * PHOTON_WOBBLE_SPEED) * PHOTON_WOBBLE * laser.width
                photon.x = laser.x + photon.offset + wobble
                photon.y = laser.source + photon.direction * photon.distance
            else:  # the beam was cut: it flies on and fades out
                photon.y += photon.direction * photon.speed * dt
                photon.fade -= dt / PHOTON_FADE
        # Streaks reaching the end of their beam (the enemy it hits, the top or the bottom of the screen) are gone.
        self.photons = [photon for photon in self.photons if photon.fade > 0 and self._within(photon)]

    def _within(self, photon: Photon) -> bool:
        laser = self.lasers.get(photon.key)
        if laser is None:
            return True
        return photon.y < laser.top if photon.direction > 0 else photon.y > laser.bottom

    def clear(self) -> None:
        """Remove all the light."""
        self.photons = []
        self.lasers = {}
