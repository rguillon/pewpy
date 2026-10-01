"""Particle effects: sparks on impacts, voxel debris and flashes on explosions (placeholder until 05-visuals.md
is decided). Only moves particles around; app.py draws them. Independent from Panda3D.

Positions are in world units: x right, y up the screen (like the game), z depth (away from the camera).
Particles are tiny cubes: "debris" is lit like the ships, "glow" (sparks, flashes) shines on its own.
"""

import math
import random
from dataclasses import dataclass

Color = tuple[float, float, float, float]

MAX_PARTICLES = 512  # the oldest go first when there are more
DRAG = 2.5  # how fast particles slow down, per second

SPARK_COLORS: tuple[Color, ...] = ((1.0, 0.85, 0.4, 1), (1.0, 0.55, 0.15, 1), (1.0, 1.0, 0.8, 1))
FIRE_COLORS: tuple[Color, ...] = ((1.0, 0.95, 0.7, 1), (1.0, 0.75, 0.3, 1), (1.0, 0.5, 0.15, 1), (0.9, 0.3, 0.1, 1))
DEBRIS_METAL: Color = (0.3, 0.31, 0.35, 1)
BLAST_COLORS: tuple[Color, ...] = ((1.0, 0.85, 0.4, 1), (1.0, 0.6, 0.15, 1), (1.0, 0.35, 0.1, 1))
BURN_COLORS: tuple[Color, ...] = ((0.6, 0.95, 1.0, 1), (1.0, 1.0, 1.0, 1), (0.3, 0.9, 1.0, 1))  # laser cyan
BURN_SPARKS = 40.0  # per second while the laser touches an enemy
# The laser's light: streaks of light shooting up the beam, from the ship's nose to whatever it hits.
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


@dataclass(eq=False)
class Particle:
    x: float
    y: float
    z: float
    vx: float
    vy: float
    vz: float
    size: float  # edge of the cube at birth; it shrinks to nothing by the end of its life
    color: Color
    life: float  # seconds
    glow: bool = False
    axis: tuple[float, float, float] = (0.0, 0.0, 1.0)  # tumbling axis (unit vector)
    spin: float = 0.0  # radians per second
    angle: float = 0.0
    age: float = 0.0
    grow: bool = False  # flashes swell quickly before shrinking

    @property
    def current_size(self) -> float:
        t = min(self.age / self.life, 1.0)
        if self.grow:
            return self.size * (min(t / 0.25, 1.0) if t < 0.25 else 1.0 - (t - 0.25) / 0.75)
        return self.size * (1.0 - t * t)


class Effects:
    def __init__(self, seed: int | None = None) -> None:
        self.rng = random.Random(seed)  # noqa: S311 - visual randomness, not cryptography
        self.particles: list[Particle] = []
        self.photons: list[Photon] = []
        self.laser: LaserGlow | None = None
        self.time = 0.0

    def update(self, dt: float) -> None:
        self.time += dt
        self._move_photons(dt)
        slow = math.exp(-DRAG * dt)
        for particle in self.particles:
            particle.age += dt
            particle.x += particle.vx * dt
            particle.y += particle.vy * dt
            particle.z += particle.vz * dt
            particle.vx *= slow
            particle.vy *= slow
            particle.vz *= slow
            particle.angle += particle.spin * dt
        self.particles = [particle for particle in self.particles if particle.age < particle.life]

    def clear(self) -> None:
        self.particles = []
        self.photons = []
        self.laser = None

    def set_laser(self, laser: LaserGlow | None, dt: float) -> None:
        """The laser this frame (None: off). While it's on, streaks of light keep shooting up from the ship."""
        self.laser = laser
        if laser is None:
            return
        count = PHOTON_RATE * math.sqrt(laser.width / THIN_BEAM) * dt
        for _ in range(int(count) + (self.rng.random() < count % 1)):
            self.photons.append(
                Photon(
                    offset=self.rng.uniform(-0.45, 0.45) * laser.width,
                    distance=self.rng.uniform(0.0, 0.03),
                    speed=self.rng.uniform(*PHOTON_SPEED),
                    size=self.rng.uniform(*PHOTON_SIZE),
                    color=self.rng.choice(BURN_COLORS),
                    wave=self.rng.uniform(0.0, 2 * math.pi),
                    x=laser.x,
                    y=laser.bottom,
                )
            )

    def _move_photons(self, dt: float) -> None:
        laser = self.laser
        for photon in self.photons:
            photon.distance += photon.speed * dt
            if laser is not None and photon.fade == 1.0:
                wobble = math.sin(photon.wave + self.time * PHOTON_WOBBLE_SPEED) * PHOTON_WOBBLE * laser.width
                photon.x = laser.x + photon.offset + wobble
                photon.y = laser.bottom + photon.distance
            else:  # the beam was cut: it flies on and fades out
                photon.y += photon.speed * dt
                photon.fade -= dt / PHOTON_FADE
        # Streaks reaching the top of the beam (the enemy it hits, or the top of the screen) are gone.
        top = laser.top if laser is not None else math.inf
        self.photons = [photon for photon in self.photons if photon.fade > 0 and photon.y < top]

    def impact(self, x: float, y: float, towards: float = -1.0, color: Color | None = None) -> None:
        """A few quick sparks where a shot hits, thrown mostly `towards` (+1 up the screen, -1 down)."""
        for _ in range(self.rng.randint(4, 6)):
            angle = math.radians(90 * towards + self.rng.uniform(-60, 60))
            speed = self.rng.uniform(0.4, 1.0)
            self._add(
                Particle(
                    x, y, 0.0,
                    math.cos(angle) * speed, math.sin(angle) * speed, self.rng.uniform(-0.2, 0.2),
                    size=self.rng.uniform(0.006, 0.011),
                    color=color or self.rng.choice(SPARK_COLORS),
                    life=self.rng.uniform(0.12, 0.25),
                    glow=True,
                )
            )  # fmt: skip

    def burn(self, x: float, y: float, dt: float) -> None:
        """The laser burning something: a steady trickle of sparks (BURN_SPARKS per second on average)."""
        count = BURN_SPARKS * dt
        for _ in range(int(count) + (self.rng.random() < count % 1)):
            angle = math.radians(self.rng.uniform(-150, -30))  # thrown back down and to the sides
            speed = self.rng.uniform(0.3, 0.8)
            self._add(
                Particle(
                    x + self.rng.uniform(-0.01, 0.01), y, 0.0,
                    math.cos(angle) * speed, math.sin(angle) * speed, self.rng.uniform(-0.2, 0.2),
                    size=self.rng.uniform(0.005, 0.009),
                    color=self.rng.choice(BURN_COLORS),
                    life=self.rng.uniform(0.1, 0.2),
                    glow=True,
                )
            )  # fmt: skip

    def explosion(self, x: float, y: float, size: float, colors: tuple[Color, ...]) -> None:
        """Something `size` wide blows up: a fireball, sparks, and debris in its `colors` (plus some metal)."""
        scale = size / 0.1  # sizes and speeds are tuned for a 0.1-wide enemy
        self._fireball(x, y, size * 0.7, FIRE_COLORS)
        for _ in range(round(8 * math.sqrt(scale))):
            self._burst(x, y, speed=(0.6, 1.4), size=(0.006, 0.012), life=(0.2, 0.45), colors=SPARK_COLORS, glow=True)
        for _ in range(round(14 * scale) + 4):
            debris_colors = (*colors, DEBRIS_METAL)
            self._burst(x, y, speed=(0.25, 0.85), size=(0.1 * size, 0.22 * size), life=(0.5, 1.0), colors=debris_colors)

    def blast(self, x: float, y: float, radius: float) -> None:
        """A missile's explosion: an orange fireball about as wide as its splash and a ring of sparks."""
        self._fireball(x, y, radius, BLAST_COLORS)
        for i in range(12):
            angle = 2 * math.pi * i / 12 + self.rng.uniform(-0.2, 0.2)
            speed = self.rng.uniform(0.6, 1.0)
            self._add(
                Particle(
                    x, y, 0.0, math.cos(angle) * speed, math.sin(angle) * speed, 0.0,
                    size=self.rng.uniform(0.008, 0.014),
                    color=self.rng.choice(BLAST_COLORS),
                    life=self.rng.uniform(0.2, 0.35),
                    glow=True,
                )
            )  # fmt: skip

    def _fireball(self, x: float, y: float, radius: float, colors: tuple[Color, ...]) -> None:
        """A few glowing cubes that swell and shrink around (x, y): the brightest in the middle."""
        for i in range(6):
            distance = 0.0 if i == 0 else self.rng.uniform(0.3, 0.7) * radius
            heading = self.rng.uniform(0, 2 * math.pi)
            dx, dy = math.cos(heading) * distance, math.sin(heading) * distance
            self._add(
                Particle(
                    x + dx, y + dy, 0.0, dx * 2, dy * 2, 0.0,
                    size=radius * (0.9 if i == 0 else self.rng.uniform(0.35, 0.6)),
                    color=colors[0] if i == 0 else self.rng.choice(colors[1:]),
                    life=self.rng.uniform(0.16, 0.26),
                    glow=True,
                    grow=True,
                    axis=_unit((self.rng.uniform(-1, 1), self.rng.uniform(-1, 1), self.rng.uniform(-1, 1))),
                    spin=self.rng.uniform(-6, 6),
                )
            )  # fmt: skip

    def _burst(
        self,
        x: float,
        y: float,
        speed: tuple[float, float],
        size: tuple[float, float],
        life: tuple[float, float],
        colors: tuple[Color, ...],
        glow: bool = False,
    ) -> None:
        """One particle flying off in a random direction (mostly flat: the depth is a third of the rest)."""
        heading = self.rng.uniform(0, 2 * math.pi)
        velocity = self.rng.uniform(*speed)
        axis = _unit((self.rng.uniform(-1, 1), self.rng.uniform(-1, 1), self.rng.uniform(-1, 1)))
        self._add(
            Particle(
                x, y, 0.0,
                math.cos(heading) * velocity, math.sin(heading) * velocity, self.rng.uniform(-0.33, 0.33) * velocity,
                size=self.rng.uniform(*size),
                color=self.rng.choice(colors),
                life=self.rng.uniform(*life),
                glow=glow,
                axis=axis,
                spin=self.rng.uniform(-12, 12),
            )
        )  # fmt: skip

    def _add(self, particle: Particle) -> None:
        self.particles.append(particle)
        if len(self.particles) > MAX_PARTICLES:
            del self.particles[: len(self.particles) - MAX_PARTICLES]


def _unit(vector: tuple[float, float, float]) -> tuple[float, float, float]:
    length = math.sqrt(sum(value * value for value in vector)) or 1.0
    x, y, z = vector
    return x / length, y / length, z / length
