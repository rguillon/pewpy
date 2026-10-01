"""The laser's light: streaks of light shooting up the beam, from the ship's nose to whatever it hits.

Unlike the other effects it lasts: it follows the beam as long as it's on.
"""

import math
import random
from dataclasses import dataclass

from pewpy.graphics.effects import BURN_COLORS, Color

PHOTON_RATE = 160.0  # per second, for the thinnest beam (wider beams send more: by the square root of the width)
PHOTON_SPEED = (2.8, 4.2)  # world units per second, up the beam
PHOTON_SIZE = (0.01, 0.02)
PHOTON_STRETCH = 4.0  # a streak is this many times longer than wide
PHOTON_WOBBLE = 0.3  # sideways wobble, as a share of the beam's width
PHOTON_WOBBLE_SPEED = 25.0  # radians per second
PHOTON_FADE = 0.15  # seconds: once the beam is cut, the streaks still flying fade out in that time
THIN_BEAM = 0.03  # the level 1 laser's width


@dataclass(frozen=True)
class LaserGlow:
    """The laser this frame, as the effects see it: from `bottom` to `top` at `x`; `hits`: heights where it burns
    something.
    """

    x: float
    bottom: float
    top: float
    width: float
    hits: tuple[float, ...] = ()


@dataclass(eq=False)
class Photon:
    """A streak of light shooting up the laser."""

    offset: float  # across the beam, from its middle
    distance: float  # up the beam, from its bottom
    speed: float
    size: float
    color: Color
    wave: float  # phase of its sideways wobble
    x: float = 0.0  # where it is: follows the beam while it's on, flies on straight once it's cut
    y: float = 0.0
    fade: float = 1.0  # 1 while the beam is on, then down to 0


class LaserLight:
    def __init__(self) -> None:
        self.photons: list[Photon] = []
        self.laser: LaserGlow | None = None

    def set(self, laser: LaserGlow | None, dt: float, rng: random.Random) -> None:
        """The laser this frame (None: off). While it's on, streaks of light keep shooting up from the ship."""
        self.laser = laser
        if laser is None:
            return
        count = PHOTON_RATE * math.sqrt(laser.width / THIN_BEAM) * dt
        for _ in range(int(count) + (rng.random() < count % 1)):
            self.photons.append(
                Photon(
                    offset=rng.uniform(-0.45, 0.45) * laser.width,
                    distance=rng.uniform(0.0, 0.03),
                    speed=rng.uniform(*PHOTON_SPEED),
                    size=rng.uniform(*PHOTON_SIZE),
                    color=rng.choice(BURN_COLORS),
                    wave=rng.uniform(0.0, 2 * math.pi),
                    x=laser.x,
                    y=laser.bottom,
                )
            )

    def update(self, dt: float, time: float) -> None:
        """Move the streaks `dt` seconds on (`time`: the effects' clock, for the wobble)."""
        laser = self.laser
        for photon in self.photons:
            photon.distance += photon.speed * dt
            if laser is not None and photon.fade == 1.0:
                wobble = math.sin(photon.wave + time * PHOTON_WOBBLE_SPEED) * PHOTON_WOBBLE * laser.width
                photon.x = laser.x + photon.offset + wobble
                photon.y = laser.bottom + photon.distance
            else:  # the beam was cut: it flies on and fades out
                photon.y += photon.speed * dt
                photon.fade -= dt / PHOTON_FADE
        # Streaks reaching the top of the beam (the enemy it hits, or the top of the screen) are gone.
        top = laser.top if laser is not None else math.inf
        self.photons = [photon for photon in self.photons if photon.fade > 0 and photon.y < top]

    def clear(self) -> None:
        self.photons = []
        self.laser = None
