"""A radiator: thin fins side by side on a plate."""

from pewpy.generators.models.common.geometry import Rng
from pewpy.generators.models.components.piece import Piece


def radiator(_rng: Rng, size: int) -> Piece:
    """Build a radiator `size` big."""
    piece = Piece()
    long = 2 + 2 * size
    piece.box(-2 * size, 2 * size, 0, long, 0, 0, "N")
    for x in range(0, 2 * size + 1, 2):
        piece.box(x, x, 0, long, 1, size + 1, "W")
    return piece
