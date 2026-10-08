"""A blueprint for building a ship kind: which parts to place in which slots.

Blueprints know the frame layout for a given ship kind, which slots to fill,
and in what order. They use the part library to stamp parts into the frame.
"""

from dataclasses import dataclass, field
from random import Random

from pewpy.generators.models.assembly.assembler import Assembler
from pewpy.generators.models.assembly.frame import Frame
from pewpy.generators.models.assembly.slots import derive_slots
from pewpy.generators.models.library.catalog import PARTS, get_part


@dataclass
class ShipBlueprint:
    """A blueprint for building a ship of a given kind.

    Fills a frame's slots with parts from the library to create a new model.
    """

    # The target size (span, length) in cubes the ship should be approximately
    target_size: tuple[int, int]

    # Names of slots to fill, in order of priority
    slot_priority: list[str] = field(
        default_factory=lambda: [
            "tail_center",
            "spine_mid",
            "wing_root_left",
            "wing_root_right",
            "nose",
            "flank_left",
            "flank_right",
        ]
    )

    # Minimum and maximum parts of each type
    min_parts: dict[str, int] = field(default_factory=lambda: {"engine": 1, "weapon": 1})
    max_parts: dict[str, int] | None = field(default_factory=lambda: None)

    def fill(self, frame: Frame, rng: Random) -> None:
        """Fill the frame's slots with parts from the library.

        Tries to fill slots in priority order, using random parts from the library.
        Stops when all priority slots are filled or no more parts fit.
        """
        # Derive slots from the frame if not already done
        if not frame.slots:
            derived = derive_slots(frame)
            for name, slot in derived.items():
                frame.slots[name] = slot

        # Fill slots in priority order
        for slot_name in self.slot_priority:
            if slot_name not in frame.slots:
                continue
            slot = frame.slots[slot_name]

            # Try up to 8 different parts for this slot
            for _ in range(8):
                # Pick a random part name
                part_name = rng.choice(list(PARTS.keys()))
                try:
                    part = get_part(part_name, rng, 1)  # size 1 = ship-sized
                except ValueError:
                    continue

                # Try stamping it
                if frame.stamp_part(part, slot_name):
                    # Successfully placed; continue to next slot
                    break
            else:
                # No part fit in this slot after 8 tries; leave it empty
                pass

    def assemble(self, frame: Frame, rng: Random) -> Frame:
        """Assemble the full model: fill slots then score and pick best."""
        self.fill(frame, rng)
        assembler = Assembler(PARTS, rng, target_size=self.target_size)
        return assembler.assemble(frame)
