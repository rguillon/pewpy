"""What space shows: stars, nebulas, a distant planet, asteroids."""

from dataclasses import dataclass

from pewpy.scenery.params.types import Color3


@dataclass(frozen=True)
class StarLayer:
    """A layer of stars: how fast, big and bright they are."""

    speed: float  # as a share of the scroll speed: far stars are slow...
    size: float  # ...small...
    brightness: float  # ...and dim


@dataclass(frozen=True)
class Stars:
    """The stars: how deep and how many, in layers."""

    depth: float
    count: int  # over the play area (more where the layer is bigger)
    layers: tuple[StarLayer, ...]


@dataclass(frozen=True)
class Nebulas:
    """Nebulas: soft glowing clouds far away."""

    depth: float
    speed: float
    count: int
    size: tuple[float, float]
    palettes: tuple[tuple[Color3, ...], ...]  # one is picked by the level's background seed


@dataclass(frozen=True)
class DistantPlanet:
    """A distant planet, slowly turning."""

    depth: float
    speed: float
    size: tuple[float, float]
    spin: float  # degrees per second
    palettes: tuple[tuple[Color3, ...], ...]  # its bands; one is picked by the level's background seed


@dataclass(frozen=True)
class RockLayer:
    """A layer of asteroids: how deep, how many, how big and how fast."""

    depth: float
    count: int
    size: tuple[float, float]
    speed: float


@dataclass(frozen=True)
class Rocks:
    """Asteroids: their layers, tumble and colors."""

    layers: tuple[RockLayer, ...]
    spin: float  # fastest tumble, degrees per second
    colors: tuple[Color3, ...]  # each voxel of an asteroid picks one
