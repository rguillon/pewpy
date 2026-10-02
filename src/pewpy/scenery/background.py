"""Per-level scrolling backgrounds (placeholder until 05-visuals.md is decided).

Each level picks one kind of background (`background` in its JSON file), a preset of `levels/sceneries.json` whose
values it can change (`scenery`, see params.py):

- space: stars, a few dim nebula clouds far away, a distant planet.
- planet: flying high over a ground that scrolls slower than the enemies (see GROUND_SPEED).
- debris: stars and slowly tumbling asteroids at two depths.
- city: flying over a city: a grid of streets and buildings, lit windows.
- ocean: flying over a sea with islands; the water is a flat animated surface.
- desert, forest, canyon, farmland, pack_ice, volcano, swamp, clouds, refinery, mountains: more grounds, see
  terrain.py.

What a scenery has decides what's drawn: stars, nebulas, a distant planet, asteroids, a ground (terrain.py).

Everything sits behind the play plane (depth = world Y, farther from the camera as it grows). The camera is
tilted, so a layer covers a bigger area the farther it is: `View.area(depth)` gives the rectangle to fill,
`View.parallax(depth)` how fast something there seems to move on screen compared with the play plane.
This module only moves things around; app.py draws them. Kept dark and muted so bullets stay easy to see.
"""

import random
from dataclasses import dataclass, field
from typing import Protocol

from pewpy import config
from pewpy.scenery import params
from pewpy.scenery.params import Mist, SceneryParams, Stars
from pewpy.scenery.terrain import GROUND_SPEED, Area, Terrain

ROCK_SHAPES = 6  # different asteroid models, see models.py


def mist_depths(scenery: SceneryParams) -> list[float]:
    """The cloud layers' depths over a ground: as deep as their `depth`, but always well above its highest point
    (the peaks of the mountains, the tops of the tallest towers), which is its depth less its highest height: so
    nothing pokes up through them.
    """
    ground = scenery.ground
    if ground is None:
        return []
    top = ground.depth - ground.max_height  # the ground's closest point to the ships
    return [min(layer.depth, top * layer.above_ground) for layer in scenery.mist.layers]


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
    def __init__(self, stars: Stars, area: Area, count: int | None = None, seed: int | None = None) -> None:
        """Stars over `area`; `count`: in all (default: the stars' count)."""
        rng = random.Random(seed)  # noqa: S311 - visual randomness, not cryptography
        count = stars.count if count is None else count
        self.layers = [
            StarLayer(
                area,
                layer.speed,
                layer.size,
                layer.brightness,
                [
                    (rng.uniform(area.left, area.right), rng.uniform(area.bottom, area.top))
                    for _ in range(count // len(stars.layers))
                ],
            )
            for layer in stars.layers
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
    """Everything behind the play area for one level's scenery (see params.py)."""

    def __init__(
        self,
        scenery: SceneryParams | str,
        view: View,
        seed: int | None = None,
        clouds: float = 0.0,
    ) -> None:
        """`scenery`: its parameters, or a preset's name. `clouds`: how much see-through cloud drifts between the
        ground and the ships, from 0 (none) to 1.
        """
        self.params = params.resolve(scenery) if isinstance(scenery, str) else scenery
        scenery = self.params
        self.kind = scenery.name
        self.rng = random.Random(seed)  # noqa: S311 - visual randomness, not cryptography
        self.variant = self.rng.randrange(1000)  # picks colors in space (nebulas, planet), see background_view.py
        self.starfield: Starfield | None = None
        self.layers: list[DriftLayer] = []
        self.terrain: Terrain | None = None
        if scenery.stars is not None:
            stars = scenery.stars
            area = view.area(stars.depth)
            count = round(stars.count * area.width * area.height / (config.PLAY_WIDTH * config.PLAY_HEIGHT))
            self.starfield = Starfield(stars, area, count, self._seed())
        if scenery.nebulas is not None:
            self.layers.append(self._clouds(view.area(scenery.nebulas.depth)))
        if scenery.planet is not None:
            self.layers.append(self._distant_planet(view.area(scenery.planet.depth)))
        if scenery.rocks is not None:
            for layer in scenery.rocks.layers:
                self.layers.append(
                    self._rocks(view.area(layer.depth), layer.depth, layer.count, layer.size, layer.speed)
                )
        if scenery.ground is not None:
            depth = scenery.ground.depth
            # The ground is farther than the play plane, so it must move faster to look like GROUND_SPEED.
            speed_factor = GROUND_SPEED / view.parallax(depth)
            self.terrain = Terrain(view.area(depth), speed_factor, scenery, self._seed())
            if clouds > 0:
                mist = scenery.mist
                wind = self.rng.uniform(-mist.wind, mist.wind)
                for depth, layer in zip(mist_depths(scenery), mist.layers, strict=True):
                    self.layers.append(self._mist(view, mist, depth, layer.speed, clouds, wind))

    def update(self, dt: float, scroll_speed: float) -> None:
        if self.starfield:
            self.starfield.update(dt, scroll_speed)
        for layer in self.layers:
            layer.update(dt, scroll_speed)
        if self.terrain:
            self.terrain.update(dt, scroll_speed)

    def _mist(
        self, view: View, mist: Mist, depth: float, screen_speed: float, amount: float, wind: float
    ) -> DriftLayer:
        area = view.area(depth)
        speed_factor = screen_speed / view.parallax(depth)
        count = round(amount * mist.count)
        drifters = [
            Drifter(
                self.rng.uniform(area.left, area.right),
                area.bottom + area.height * (i + self.rng.random()) / max(count, 1),  # spread out from the start
                self.rng.uniform(*mist.size),
                speed_factor * self.rng.uniform(0.9, 1.1),
                shape=self.rng.randrange(1000),  # its texture and how see-through it is, see background_view.py
                angle=(0.0, 0.0, self.rng.uniform(0, 360)),
                wind=wind * self.rng.uniform(0.8, 1.2),
            )
            for i in range(count)
        ]
        return DriftLayer("mist", depth, area, drifters, self.rng)

    def _seed(self) -> int:
        return self.rng.randrange(2**32)

    def _clouds(self, area: Area) -> DriftLayer:
        nebulas = self.params.nebulas
        assert nebulas is not None  # noqa: S101 - only called when there are some
        count = nebulas.count
        clouds = [
            Drifter(
                self.rng.uniform(area.left, area.right),
                area.bottom + area.height * (i + self.rng.random()) / count,
                self.rng.uniform(*nebulas.size),
                nebulas.speed,
                shape=i % 3,  # its color, see background_view.py
            )
            for i in range(count)
        ]
        return DriftLayer("cloud", nebulas.depth, area, clouds, self.rng)

    def _distant_planet(self, area: Area) -> DriftLayer:
        planet = self.params.planet
        assert planet is not None  # noqa: S101 - only called when there is one
        side = self.rng.choice((0.25, 0.75))  # left or right
        size = self.rng.uniform(*planet.size)
        drifter = Drifter(area.left + area.width * side, area.top - area.height * 0.25, size, planet.speed)
        drifter.spin = (planet.spin, 0.0, 0.0)
        return DriftLayer("planet", planet.depth, area, [drifter], self.rng)

    def _rocks(self, area: Area, depth: float, count: int, size: tuple[float, float], speed: float) -> DriftLayer:
        rocks_spin = self.params.rocks.spin if self.params.rocks else 0.0

        def spin() -> float:
            return self.rng.uniform(-rocks_spin, rocks_spin)

        rocks = [
            Drifter(
                self.rng.uniform(area.left, area.right),
                self.rng.uniform(area.bottom, area.top),
                self.rng.uniform(*size),
                speed * self.rng.uniform(0.85, 1.15),
                shape=self.rng.randrange(ROCK_SHAPES),
                spin=(spin(), spin(), spin()),
                angle=(self.rng.uniform(0, 360), self.rng.uniform(0, 360), 0.0),
            )
            for _ in range(count)
        ]
        return DriftLayer("rock", depth, area, rocks, self.rng)
