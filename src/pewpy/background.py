"""Per-level scrolling backgrounds (placeholder until 05-visuals.md is decided).

Each level picks one kind of background (`background` in its JSON file):

- space: stars, a few dim nebula clouds far away, a distant planet.
- planet: flying high over a voxel ground that scrolls slower than the enemies (see GROUND_SPEED).
- debris: stars and slowly tumbling asteroids at two depths.
- city: flying over a sci-fi city at night: a grid of streets and buildings of voxels, lit windows.
- ocean: flying over a sea with voxel islands; the water is a flat animated surface.
- desert, forest, canyon, farmland, pack_ice, volcano, swamp, clouds, refinery, mountains: more voxel grounds,
  see the generators in terrain.py.

The voxel grounds are described in terrain.py (BIOMES).

Everything sits behind the play plane (depth = world Y, farther from the camera as it grows). The camera is
tilted, so a layer covers a bigger area the farther it is: `View.area(depth)` gives the rectangle to fill,
`View.parallax(depth)` how fast something there seems to move on screen compared with the play plane.
This module only moves things around; app.py draws them. Kept dark and muted so bullets stay easy to see.
"""

import random
from dataclasses import dataclass, field
from typing import Protocol

from pewpy import config
from pewpy.terrain import BIOMES, GROUND_SPEED, GROUND_VOXEL, Area, Terrain

BACKGROUNDS = ("space", "debris", *BIOMES)


def mist_depths(kind: str) -> list[float]:
    """The cloud layers' depths over a ground: MIST_LAYERS's, but always well above its highest point (the peaks of
    the mountains, the tops of the tallest towers), which is its depth less its highest height."""
    biome = BIOMES[kind]
    top = biome.depth - biome.max_height  # the ground's closest point to the ships
    return [min(depth, top * share) for (depth, _), share in zip(MIST_LAYERS, MIST_ABOVE_GROUND, strict=True)]


# See-through clouds in the atmosphere levels, between the ground and the ships: (depth, speed on screen as a
# fraction of the scroll speed). Closer ones move faster, like the rest of the parallax. The depths are the deepest
# they go: over high ground (mountain peaks, towers), they come closer, so nothing pokes up through them (see
# `mist_depths`).
MIST_LAYERS = ((0.08, 0.5), (0.18, 0.42))
MIST_ABOVE_GROUND = (0.4, 0.75)  # at most these shares of the way from the ships down to the highest ground
MIST_COUNT = 10  # per layer, when a level has the most clouds (Level.clouds = 1)
MIST_SIZE = (0.6, 1.3)  # world units
MIST_WIND = 0.02  # fastest sideways drift, world units per second

STAR_DEPTH = 0.3
# Parallax layers: (speed factor, star size, brightness). Far stars are small, dim and slow.
STAR_LAYERS = ((0.4, 0.008, 0.35), (0.7, 0.012, 0.6), (1.0, 0.018, 1.0))

CLOUD_DEPTH = 3.5
CLOUD_SPEED_FACTOR = 0.12
DISTANT_PLANET_DEPTH = 6.0
DISTANT_PLANET_SPEED_FACTOR = 0.04
ROCK_LAYERS = (  # (depth, count, smallest size, largest size, speed factor)
    (2.2, 12, 0.08, 0.16, 0.35),
    (0.9, 6, 0.1, 0.2, 0.7),
)
ROCK_SHAPES = 6  # different asteroid models, see models.py
ROCK_SPIN = 40.0  # fastest tumble, degrees per second


class View(Protocol):
    def area(self, depth: float) -> Area: ...

    def parallax(self, depth: float) -> float: ...


@dataclass(eq=False)
class StarLayer:
    """Stars that scroll together. The layer is drawn twice, one copy above the other, and slides down by
    `offset` (wrapping every `area.height`), so it loops seamlessly without moving each star.
    """

    area: Area
    speed_factor: float
    size: float
    brightness: float
    stars: list[tuple[float, float]]  # (x, y) inside `area`, before scrolling
    offset: float = 0.0

    def update(self, dt: float, scroll_speed: float) -> None:
        self.offset = (self.offset + scroll_speed * self.speed_factor * dt) % self.area.height


class Starfield:
    def __init__(self, count: int = config.STAR_COUNT, seed: int | None = None, area: Area | None = None) -> None:
        rng = random.Random(seed)  # noqa: S311 - visual randomness, not cryptography
        area = area or Area.play_area()
        self.layers = [
            StarLayer(
                area,
                speed_factor,
                size,
                brightness,
                [
                    (rng.uniform(area.left, area.right), rng.uniform(area.bottom, area.top))
                    for _ in range(count // len(STAR_LAYERS))
                ],
            )
            for speed_factor, size, brightness in STAR_LAYERS
        ]

    def update(self, dt: float, scroll_speed: float) -> None:
        for layer in self.layers:
            layer.update(dt, scroll_speed)


@dataclass(eq=False)
class Drifter:
    """Something sliding down the background: a cloud, a planet, an asteroid. `angle` is (heading, pitch, roll)."""

    x: float
    y: float
    size: float
    speed_factor: float
    shape: int = 0
    spin: tuple[float, float, float] = (0.0, 0.0, 0.0)  # degrees per second
    angle: tuple[float, float, float] = (0.0, 0.0, 0.0)
    wind: float = 0.0  # sideways speed, world units per second


@dataclass(eq=False)
class DriftLayer:
    """Drifters at one depth. One that leaves the bottom comes back above the top, somewhere else."""

    kind: str  # "cloud", "planet", "rock" or "mist": what background_view.py draws
    depth: float
    area: Area
    drifters: list[Drifter]
    rng: random.Random = field(default_factory=random.Random)

    def update(self, dt: float, scroll_speed: float) -> None:
        for drifter in self.drifters:
            drifter.y -= scroll_speed * drifter.speed_factor * dt
            (heading, pitch, roll), (spin_h, spin_p, spin_r) = drifter.angle, drifter.spin
            drifter.angle = (heading + spin_h * dt, pitch + spin_p * dt, roll + spin_r * dt)
            if drifter.y < self.area.bottom - drifter.size:
                drifter.y += self.area.height + 2 * drifter.size
                drifter.x = self.rng.uniform(self.area.left, self.area.right)
            drifter.x += drifter.wind * dt  # blown sideways: gone off one side, it comes back on the other
            if drifter.x > self.area.right + drifter.size:
                drifter.x -= self.area.width + 2 * drifter.size
            elif drifter.x < self.area.left - drifter.size:
                drifter.x += self.area.width + 2 * drifter.size


class Scenery:
    """Everything behind the play area for one kind of background."""

    def __init__(
        self, kind: str, view: View, seed: int | None = None, ground_voxel: float = GROUND_VOXEL, clouds: float = 0.0
    ) -> None:
        """`clouds`: how much see-through cloud drifts between the ground and the ships, from 0 (none) to 1."""
        if kind not in BACKGROUNDS:
            raise ValueError(f"unknown background {kind!r}, expected one of {BACKGROUNDS}")  # noqa: TRY003
        self.kind = kind
        self.rng = random.Random(seed)  # noqa: S311 - visual randomness, not cryptography
        self.variant = self.rng.randrange(1000)  # picks colors in space (nebulas, planet), see background_view.py
        self.starfield: Starfield | None = None
        self.layers: list[DriftLayer] = []
        self.terrain: Terrain | None = None
        if kind in ("space", "debris"):
            area = view.area(STAR_DEPTH)
            count = round(config.STAR_COUNT * area.width * area.height / (config.PLAY_WIDTH * config.PLAY_HEIGHT))
            self.starfield = Starfield(count, self._seed(), area)
        if kind == "space":
            self.layers.append(self._clouds(view.area(CLOUD_DEPTH)))
            self.layers.append(self._distant_planet(view.area(DISTANT_PLANET_DEPTH)))
        elif kind == "debris":
            for depth, count, smallest, largest, speed in ROCK_LAYERS:
                self.layers.append(self._rocks(view.area(depth), depth, count, smallest, largest, speed))
        else:
            biome = BIOMES[kind]
            # The ground is farther than the play plane, so it must move faster to look like GROUND_SPEED.
            speed_factor = GROUND_SPEED / view.parallax(biome.depth)
            self.terrain = Terrain(view.area(biome.depth), speed_factor, self._seed(), ground_voxel, kind)
            if clouds > 0:
                wind = self.rng.uniform(-MIST_WIND, MIST_WIND)
                for depth, (_, screen_speed) in zip(mist_depths(kind), MIST_LAYERS, strict=True):
                    self.layers.append(self._mist(view, depth, screen_speed, clouds, wind))

    def update(self, dt: float, scroll_speed: float) -> None:
        if self.starfield:
            self.starfield.update(dt, scroll_speed)
        for layer in self.layers:
            layer.update(dt, scroll_speed)
        if self.terrain:
            self.terrain.update(dt, scroll_speed)

    def _mist(self, view: View, depth: float, screen_speed: float, amount: float, wind: float) -> DriftLayer:
        area = view.area(depth)
        speed_factor = screen_speed / view.parallax(depth)
        count = round(amount * MIST_COUNT)
        mist = [
            Drifter(
                self.rng.uniform(area.left, area.right),
                area.bottom + area.height * (i + self.rng.random()) / max(count, 1),  # spread out from the start
                self.rng.uniform(*MIST_SIZE),
                speed_factor * self.rng.uniform(0.9, 1.1),
                shape=self.rng.randrange(1000),  # its texture and how see-through it is, see background_view.py
                angle=(0.0, 0.0, self.rng.uniform(0, 360)),
                wind=wind * self.rng.uniform(0.8, 1.2),
            )
            for i in range(count)
        ]
        return DriftLayer("mist", depth, area, mist, self.rng)

    def _seed(self) -> int:
        return self.rng.randrange(2**32)

    def _clouds(self, area: Area) -> DriftLayer:
        clouds = [
            Drifter(
                self.rng.uniform(area.left, area.right),
                area.bottom + area.height * (i + self.rng.random()) / 5,
                self.rng.uniform(1.2, 2.4),
                CLOUD_SPEED_FACTOR,
                shape=i % 3,  # color, see app.py
            )
            for i in range(5)
        ]
        return DriftLayer("cloud", CLOUD_DEPTH, area, clouds, self.rng)

    def _distant_planet(self, area: Area) -> DriftLayer:
        side = self.rng.choice((0.25, 0.75))  # left or right
        size = self.rng.uniform(1.2, 2.2)
        planet = Drifter(
            area.left + area.width * side, area.top - area.height * 0.25, size, DISTANT_PLANET_SPEED_FACTOR
        )
        planet.spin = (4.0, 0.0, 0.0)
        return DriftLayer("planet", DISTANT_PLANET_DEPTH, area, [planet], self.rng)

    def _rocks(self, area: Area, depth: float, count: int, smallest: float, largest: float, speed: float) -> DriftLayer:
        def spin() -> float:
            return self.rng.uniform(-ROCK_SPIN, ROCK_SPIN)

        rocks = [
            Drifter(
                self.rng.uniform(area.left, area.right),
                self.rng.uniform(area.bottom, area.top),
                self.rng.uniform(smallest, largest),
                speed * self.rng.uniform(0.85, 1.15),
                shape=self.rng.randrange(ROCK_SHAPES),
                spin=(spin(), spin(), spin()),
                angle=(self.rng.uniform(0, 360), self.rng.uniform(0, 360), 0.0),
            )
            for _ in range(count)
        ]
        return DriftLayer("rock", depth, area, rocks, self.rng)
