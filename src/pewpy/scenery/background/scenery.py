"""A level's scenery: the layers behind the play area, built from its parameters."""

import random
from typing import Protocol

from pewpy import config
from pewpy.scenery import params
from pewpy.scenery.background.drift import DriftLayer
from pewpy.scenery.background.layers.distant_planet import planet_layer
from pewpy.scenery.background.layers.mist import mist_layer
from pewpy.scenery.background.layers.nebulas import nebula_layer
from pewpy.scenery.background.layers.rocks import rock_layer
from pewpy.scenery.background.stars import Starfield
from pewpy.scenery.ground.terrain import GROUND_SPEED, Area, Terrain
from pewpy.scenery.params import SceneryParams


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


class Scenery:
    """Everything behind the play area for one level's scenery (see pewpy.scenery.params)."""

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
        self.variant = self.rng.randrange(1000)  # picks colors in space (nebulas, planet), see view.py
        self.starfield: Starfield | None = None
        self.layers: list[DriftLayer] = []
        self.terrain: Terrain | None = None
        if scenery.stars is not None:
            stars = scenery.stars
            area = view.area(stars.depth)
            count = round(stars.count * area.width * area.height / (config.PLAY_WIDTH * config.PLAY_HEIGHT))
            self.starfield = Starfield(stars, area, count, self._seed())
        if scenery.nebulas is not None:
            self.layers.append(nebula_layer(self.rng, scenery.nebulas, view.area(scenery.nebulas.depth)))
        if scenery.planet is not None:
            self.layers.append(planet_layer(self.rng, scenery.planet, view.area(scenery.planet.depth)))
        if scenery.rocks is not None:
            for layer in scenery.rocks.layers:
                self.layers.append(rock_layer(self.rng, layer, view.area(layer.depth), scenery.rocks.spin))
        if scenery.ground is not None:
            depth = scenery.ground.depth
            # The ground is farther than the play plane, so it must move faster to look like GROUND_SPEED.
            speed_factor = GROUND_SPEED / view.parallax(depth)
            self.terrain = Terrain(view.area(depth), speed_factor, scenery, self._seed())
            if clouds > 0:
                mist = scenery.mist
                wind = self.rng.uniform(-mist.wind, mist.wind)
                for depth, layer in zip(mist_depths(scenery), mist.layers, strict=True):
                    speed_factor = layer.speed / view.parallax(depth)
                    self.layers.append(mist_layer(self.rng, view.area(depth), speed_factor, mist, depth, clouds, wind))

    def update(self, dt: float, scroll_speed: float) -> None:
        if self.starfield:
            self.starfield.update(dt, scroll_speed)
        for layer in self.layers:
            layer.update(dt, scroll_speed)
        if self.terrain:
            self.terrain.update(dt, scroll_speed)

    def _seed(self) -> int:
        return self.rng.randrange(2**32)
