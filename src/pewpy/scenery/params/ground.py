"""A ground: its landscape, a fluid below height 0, a settlement, flora, outposts."""

from dataclasses import dataclass

from pewpy.scenery.params.types import Color3, Knobs


@dataclass(frozen=True)
class Ground:
    """A ground: its shape, how it's painted, how deep it lies and how high it rises."""

    landscape: str  # its shape (grounds/ LANDSCAPES)...
    shape: Knobs  # ...and that landscape's numbers
    style: str  # how the ground shader paints it (pewpy.scenery.ground.shader STYLES)...
    colors: dict[str, Color3]  # ...with these colors (STYLE_COLORS names them; built-up grounds: the settlement's)
    depth: float  # its base layer, world units behind the play plane; it rises towards the camera from there...
    max_height: float  # ...this high at most (keep depth - max_height > 0.1: behind the ships)


@dataclass(frozen=True)
class Fluid:
    """What's below height 0: "water"."""

    kind: str
    colors: dict[str, Color3]  # see colors.py FLUID_COLORS


@dataclass(frozen=True)
class Settlement:
    """Streets, fields, yards painted on the ground, and what stands on them (grounds/ SETTLEMENTS)."""

    kind: str  # grounds/ SETTLEMENTS
    colors: dict[str, Color3]  # of what covers the ground (colors.py SURFACE_COLORS)
    layout: Knobs  # the settlement's numbers


@dataclass(frozen=True)
class Flora:
    """Sparse props placed from the landscape's shape (grounds/ FLORAS)."""

    kind: str
    knobs: Knobs


@dataclass(frozen=True)
class Outposts:
    """Compounds set on the ground wherever it is flattest, on a levelled apron (grounds/outposts.py)."""

    kinds: tuple[str, ...]  # grounds/outposts.py COMPOUNDS: each compound picks one
    spacing: float  # about this far apart (world units)
    size: tuple[float, float]  # across, each somewhere between
