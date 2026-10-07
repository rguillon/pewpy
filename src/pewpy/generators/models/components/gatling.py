"""A gatling: a housing, a drum and four barrels round its middle."""

from pewpy.generators.models.common.geometry import Rng
from pewpy.generators.models.components.piece import Piece


def gatling(_rng: Rng, size: int) -> Piece:
    """Build a gatling `size` big."""
    piece = Piece()
    back = 1 + size
    piece.housing(size, 0, back, 0, size + 1)
    piece.box(-1, 1, back + 1, back + 1, 0, 2, "k")  # the drum
    tip = back + 2 + 2 * size
    for z in (0, 2):
        piece.box(1, 1, back + 2, tip, z, z, "r")
    piece.box(0, 0, back + 2, tip, 1, 1, "k")  # the spindle the barrels turn round
    piece.weapon("gatling", 0, tip, 1)  # one weapon, its barrels round it
    return piece
