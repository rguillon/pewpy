"""The light, the haze, the times of day and the mist: what every scenery has."""

from dataclasses import dataclass

from pewpy.scenery.params.types import Color3


@dataclass(frozen=True)
class TimeOfDay:
    ground: Color3  # tint of the ground (and what stands on it)
    air: Color3  # tint of the haze and the sky


@dataclass(frozen=True)
class Light:
    sun: Color3
    sky: Color3  # light from the sky, in the open


@dataclass(frozen=True)
class Haze:
    color: Color3  # the air far away
    amount: float  # how much of it, at the farthest
    near: float  # from this distance to the camera (world units)...
    range: float  # ...to this much farther, where it's thickest


@dataclass(frozen=True)
class MistLayer:
    depth: float  # the deepest it goes (world units behind the play plane); over high ground it comes closer...
    above_ground: float  # ...staying at most this share of the way from the ships down to the highest ground
    speed: float  # how fast it moves on screen, as a share of the level's scroll speed


@dataclass(frozen=True)
class Mist:
    """See-through clouds between a ground and the ships, when a level has some (`clouds`)."""

    color: Color3  # pale, mixed with the air's color...
    air: float  # ...this much
    night: float  # how bright they stay when the ground goes dark (lights below still catch them)
    opacity: tuple[float, float]  # each one somewhere between
    layers: tuple[MistLayer, ...]
    count: int  # per layer, with the most clouds (clouds = 1)
    size: tuple[float, float]
    wind: float  # fastest sideways drift, world units per second
