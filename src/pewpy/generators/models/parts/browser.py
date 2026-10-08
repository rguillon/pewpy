"""The parts browser of the Dev menu: the catalog's parts, one at a time.

Left and Right go from one part to the next; Space makes a new one of the same kind (another seed). Nothing is saved:
a part is made again from its name and size. Independent from showing: the app shows `part`.
"""

import random
from dataclasses import dataclass, field

from pewpy.generators.models.library.catalog import PART_NAMES, get_part
from pewpy.generators.models.library.part import Part


@dataclass
class PartBrowser:
    """The catalog's parts, the one on show, and its size."""

    rng: random.Random = field(default_factory=random.Random)
    index: int = 0
    size: int = 10  # the size parts are made to

    @property
    def name(self) -> str:
        """Return the name of the part on show."""
        return PART_NAMES[self.index]

    def move(self, step: int) -> None:
        """Show the next part (step 1) or the previous one (-1), wrapping around."""
        self.index = (self.index + step) % len(PART_NAMES)

    def generate(self) -> None:
        """Make a new part of the kind on show: another seed."""
        # the part is made fresh each time it's shown

    def part(self) -> Part:
        """Return the part on show, made to the size."""
        return get_part(self.name, self.rng, self.size)

    def title(self) -> str:
        """Return the part's name and number among the parts."""
        return f"{self.name}  ({self.index + 1}/{len(PART_NAMES)})"

    def details(self) -> str:
        """Return what the part is: its tags and size."""
        part = self.part()
        tags = ", ".join(sorted(part.tags)) if part.tags else "no tags"
        return f"tags: {tags}   size: {self.size}"

    def stretch(self, step: int) -> None:
        """Make the size parts are made to bigger (or smaller, below 1)."""
        self.size = max(1, self.size + step)
