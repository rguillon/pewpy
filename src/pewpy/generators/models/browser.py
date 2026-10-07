"""The model browser of the Dev menu: one category's models, one at a time, to make new ones in their place.

Left and Right go from one model to the next; its width and height can each be made bigger or smaller, to change the
model's shape; Space makes a new model of that size (shown, not saved), Enter saves it in place of the model (or only
the size, without a new model). Independent from rendering: the app shows `pieces`.
"""

import random
from dataclasses import dataclass, field

from pewpy import config
from pewpy import data as game_data
from pewpy.generators.models.catalog import Entry, entries
from pewpy.generators.models.common.geometry import Rng
from pewpy.generators.models.saving import lopsided, save_boss, save_ship, write_model
from pewpy.generators.models.sized import Size, rounded, sized_boss, sized_ship
from pewpy.graphics.models import drawing_size, parse_voxels

SIZE_STEP = 1.05  # each step makes the width (or the height) this much bigger or smaller


@dataclass(frozen=True)
class Piece:
    """A drawing on show: its name, its data (as its file has it) and where its middle is, in world units."""

    name: str
    data: dict
    x: float = 0.0
    y: float = 0.0


def read_model(drawing: str) -> dict:
    """Read a model's drawing (a part's from its model's file, see pewpy.data.read_model)."""
    return game_data.read_model(drawing)[0]


def model_size(data: dict) -> Size:
    """Return the size a model is meant to be (see pewpy.graphics.models.drawing_size)."""
    return drawing_size(data, parse_voxels(data))


@dataclass
class ModelBrowser:
    """A category's models (see catalog.CATEGORIES), the one on show, its size, and the new model made for it."""

    category: str
    rng: Rng = field(default_factory=random.Random)
    models: list[Entry] = field(init=False)
    index: int = 0
    size: Size = (0.0, 0.0)  # the size new models are made to
    new: dict | None = None  # the new model made, not saved: a ship's drawing, or a boss's (see sized_boss)
    saved: bool = False  # just saved

    def __post_init__(self) -> None:
        """Read the category's models; show the first."""
        self.models = entries(self.category)
        self._show(self.index)

    @property
    def entry(self) -> Entry:
        """Return the model on show."""
        return self.models[self.index]

    def _show(self, index: int) -> None:
        self.index = index % len(self.models)
        self.size = model_size(read_model(self.entry.drawing))
        self.new = None
        self.saved = False

    def move(self, step: int) -> None:
        """Show the next model (step 1) or the previous one (-1), wrapping around; a new model not saved is lost."""
        self._show(self.index + step)

    def stretch(self, across: int, up: int) -> None:
        """Make the width `across` steps bigger (or smaller, below 0) and the height `up` steps: the model's shape."""
        self.size = (self.size[0] * SIZE_STEP**across, self.size[1] * SIZE_STEP**up)
        self.saved = False

    def generate(self) -> None:
        """Make a new model of the size."""
        if self.category == "bosses":
            self.new = sized_boss(self.rng, self.size, lopsided=lopsided(self.entry.parts))
        else:
            self.new = sized_ship(self.rng, self.size, player=self.category == "players")
        self.saved = False

    def save(self) -> None:
        """Save the new model in place of the one on show, or only the size when there's no new model."""
        entry = self.entry
        model = read_model(entry.drawing)
        if self.category == "bosses":
            if self.new is None:
                write_model(entry.drawing, {**model, "size": rounded(self.size)})
            else:
                save_boss(entry, self.new)
        else:
            save_ship(entry, {**(self.new or model), "size": rounded(self.size)}, model_size(model))
        self.models = entries(self.category)  # a boss's parts changed
        self._show(self.index)
        self.saved = True

    def pieces(self) -> list[Piece]:
        """Return what's on show: the model (the new one, if any), and a boss's parts in their places."""
        entry = self.entry
        if self.new is None:
            core = Piece(entry.drawing, read_model(entry.drawing))
            parts = [Piece(part.drawing, read_model(part.drawing), part.x, part.y) for part in entry.parts]
            return [core, *parts]
        if self.category != "bosses":
            return [Piece(entry.drawing, self.new)]
        cube = config.MODEL_VOXEL
        parts = [
            Piece(f"part {index}", data, x * cube, y * cube) for index, (data, x, y) in enumerate(self.new["parts"])
        ]
        return [Piece(entry.drawing, self.new["core"]), *parts]
