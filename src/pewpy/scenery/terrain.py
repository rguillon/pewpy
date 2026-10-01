"""The grounds scrolling under the ship: hills, cities, islands in a sea... (see background.py).

A ground is a smooth relief (relief.py) shaped by its landscape, maybe built up with a settlement or dotted with
flora (each kind in grounds/), all from the level's scenery (params.py). It's a seamless loop of strips
("chunks") scrolling down; background_view.py draws them (ground_shader.py). Independent from Panda3D.
"""

import math
import random
from dataclasses import dataclass

import numpy as np

from pewpy import config
from pewpy.scenery import relief, settlement
from pewpy.scenery.grounds import FLORAS, LANDSCAPES, SETTLEMENTS, outposts
from pewpy.scenery.params import SceneryParams
from pewpy.scenery.relief import RELIEF_STEP, Relief
from pewpy.scenery.settlement import Layout, Prop

# How fast the ground seems to move on screen, as a fraction of the level's scroll speed. Kept away from the
# enemies' speeds (as fractions of level 2's scroll speed: parked Snipers 0, Gunships 0.6, Turrets 1.0,
# Drones 1.2, Weavers 1.4), or they look like they sit on the ground. Turrets slide over it too.
GROUND_SPEED = 0.3
CHUNK_HEIGHT = 0.84  # world units: the ground is drawn in strips this long (about: a whole number of relief rows)...
CHUNKS = 5  # ...and loops after this many strips (more if the screen needs it)


@dataclass(frozen=True)
class Area:
    """A rectangle on a background layer, in world units (X right, Z up the screen)."""

    left: float
    right: float
    bottom: float
    top: float

    @classmethod
    def play_area(cls) -> "Area":
        half_width, half_height = config.PLAY_WIDTH / 2, config.PLAY_HEIGHT / 2
        return cls(-half_width, half_width, -half_height, half_height)

    @property
    def width(self) -> float:
        return self.right - self.left

    @property
    def height(self) -> float:
        return self.top - self.bottom


class Terrain:
    """A ground: a seamless loop of strips ("chunks") of relief, scrolling down.

    Row 0 of the relief is the top of the loop, and its last row joins back onto row 0. The loop is longer than the
    screen (it gets more chunks if needed), so each chunk shows at most once.
    """

    def __init__(self, area: Area, speed_factor: float, scenery: SceneryParams, seed: int | None = None) -> None:
        ground = scenery.ground
        if ground is None:
            raise ValueError(f"{scenery.name}: no ground")  # noqa: TRY003
        self.rng = random.Random(seed)  # noqa: S311 - visual randomness, not cryptography
        self.area = area
        self.speed_factor = speed_factor
        self.scenery = scenery
        self.depth = ground.depth
        self.relief_rows = max(round(CHUNK_HEIGHT / RELIEF_STEP), 1)  # rows of the relief per chunk
        self.chunk_height = self.relief_rows * RELIEF_STEP
        self.chunks = max(CHUNKS, math.ceil(area.height / self.chunk_height) + 1)
        self.loop_length = self.chunks * self.chunk_height
        columns = math.ceil(area.width / RELIEF_STEP) + 2
        self.width = (columns - 1) * RELIEF_STEP
        self.offset = 0.0  # how far the ground has scrolled, in world units
        rng = np.random.default_rng(self.rng.randrange(2**32))
        landscape = LANDSCAPES[ground.landscape]
        shape = landscape.shape(
            rng, self.relief_rows * self.chunks, columns, ground.max_height, RELIEF_STEP, ground.shape
        )
        fluid = scenery.fluid is not None
        props: list[Prop] = []
        self.layout: Layout | None = None
        if scenery.settlement is not None:
            built_up = SETTLEMENTS[scenery.settlement.kind]
            self.layout = built_up.layout(self.rng, self.width, self.loop_length, scenery.settlement.layout)
            props += self.layout.props
        if scenery.flora is not None:
            flora = FLORAS[scenery.flora.kind]
            props += flora.props(self.rng, shape, RELIEF_STEP, RELIEF_STEP, scenery.flora.knobs)
        if scenery.outposts is not None:  # levels the ground under them, makes room among the rest
            rng = random.Random(self.rng.randrange(2**32))  # noqa: S311 - visual randomness
            shape, compounds, sites = outposts.build(rng, shape, RELIEF_STEP, scenery.outposts, fluid)
            props = [*outposts.outside(props, sites), *compounds]
            if self.layout is not None and scenery.settlement is not None:
                self.layout = outposts.clear(self.layout, sites, outposts.SURFACES[scenery.settlement.kind])
        surface = np.maximum(shape.heights, 0.0) if fluid else shape.heights
        self.props: list[Prop] = []  # standing on the relief
        occluders = None
        if props:
            self.props = settlement.place(props, surface, RELIEF_STEP, RELIEF_STEP)
            occluders = settlement.occluders(self.props, surface, RELIEF_STEP, RELIEF_STEP)
        self.relief: Relief = relief.make_relief(shape, RELIEF_STEP, RELIEF_STEP, occluders, fluid=fluid)

    def update(self, dt: float, scroll_speed: float) -> None:
        self.offset = (self.offset + scroll_speed * self.speed_factor * dt) % self.loop_length

    def chunk_props(self, chunk: int) -> list[Prop]:
        """The props standing in a chunk (by the middle of their footprint)."""
        start = chunk * self.chunk_height
        return [prop for prop in self.props if start <= prop.y < start + self.chunk_height]

    def chunk_top(self, chunk: int) -> float:
        """World Z of the top edge of a chunk."""
        start = self.area.top + self.chunk_height
        return start - (chunk * self.chunk_height + self.offset) % self.loop_length

    @property
    def left(self) -> float:
        """World X of the left edge of the ground (it's centered)."""
        return -self.width / 2
