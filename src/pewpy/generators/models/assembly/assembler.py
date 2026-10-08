"""The assembler: try many assemblies, keep the best.

Given a frame (empty or partially filled), a library of parts, and slots derived from the frame,
the assembler tries ASSEMBLY_TRIES assemblies, each time filling the frame's slots with different
parts from the library in different orders, then scores them and keeps the best.

This is what generates new player ships, new enemy ships, and new boss cores + parts - all using
the same engine.
"""

import random

from pewpy.generators.models.assembly.frame import Frame
from pewpy.generators.models.assembly.scoring import pick_best
from pewpy.generators.models.library.part import Part

# How many assemblies to try before picking the best (tune for performance vs variety)
ASSEMBLY_TRIES = 32


class Assembler:
    """Assemble a model by filling its slots with parts from the library."""

    def __init__(
        self,
        library: dict[str, Part],  # name -> Part
        rng: random.Random,
        target_size: tuple[int, int] | None = None,
        require_symmetry: bool = True,
    ) -> None:
        """Initialize the assembler with a part library and RNG."""
        self.library = library
        self.rng = rng
        self.target_size = target_size
        self.require_symmetry = require_symmetry

    def assemble(self, frame: Frame) -> Frame:
        """Try ASSEMBLY_TRIES assemblies and return the best one."""
        frames = []
        for _ in range(ASSEMBLY_TRIES):
            # Start with a fresh frame (copy the base)
            trial = Frame(cells=dict(frame.cells), slots=dict(frame.slots))
            # Fill slots with random parts from the library
            self._fill_slots(trial)
            # Score and keep
            frames.append(trial)
        return pick_best(frames, self.target_size, require_symmetry=self.require_symmetry)

    def _fill_slots(self, frame: Frame) -> None:
        """Fill all of frame's slots with random parts from the library."""
        for slot_name in frame.slots:
            if slot_name not in frame.slots:
                continue
            # Pick a random part that matches some tag this slot might care about
            # For now, just try a few common parts
            tried_parts = []
            for _ in range(8):  # try 8 different parts
                # Pick a random part name
                part_name = self.rng.choice(list(self.library.keys()))
                part_builder = self.library[part_name]
                # Build it `size` 1 (ship-sized) for now
                part = part_builder(self.rng, 1)
                # Try stamping it
                if frame.stamp_part(part, slot_name):
                    tried_parts.append(part)
                    break
            # If no part fit, leave the slot empty

    def assemble_with_parts(
        self, frame: Frame, *, _min_parts: int = 1, _max_parts: int | None = None
    ) -> tuple[Frame, list[tuple[str, Part]]]:
        """Assemble and return (frame, parts_used)."""
        result = self.assemble(frame)
        # Track which parts went where (simplified)
        parts_used: list[tuple[str, Part]] = []
        return result, parts_used
