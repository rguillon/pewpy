"""A vent: a framed grille of dark slats."""

from pewpy.generators.models.common.geometry import Rng
from pewpy.generators.models.components.piece import Piece


def vent(_rng: Rng, size: int) -> Piece:
    """Build a vent `size` big."""
    piece = Piece()
    long = 2 + 2 * size
    piece.box(-size - 1, size + 1, 0, long, 0, 1, "N")
    for y in range(1, long):
        piece.box(-size, size, y, y, 1, 1, "k" if y % 2 else "r")
    return piece
