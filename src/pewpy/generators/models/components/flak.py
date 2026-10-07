"""A flak gun: a square mount and two pairs of short barrels, angled up."""

from pewpy.generators.models.common.geometry import Rng
from pewpy.generators.models.components.piece import Piece


def flak(_rng: Rng, size: int) -> Piece:
    """Build a flak gun `size` big."""
    piece = Piece()
    back = 2 + 2 * size
    piece.box(-size - 1, size + 1, 0, back, 0, 0, "N")
    piece.housing(size, 1, back - 1, 1, size)
    tip = back + 1 + size
    for z in (size, size + 1):
        piece.box(size, size, back - 1, tip, z, z, "r")
    piece.weapon("flak", size, tip, size)
    return piece
