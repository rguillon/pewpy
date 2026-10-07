"""A fuel tank: a cylinder lying along the hull, banded, its ends darker."""

from pewpy.makers.common.geometry import Rng
from pewpy.makers.components.piece import Piece


def tank(_rng: Rng, size: int) -> Piece:
    """Build a fuel tank `size` big."""
    piece = Piece()
    r = size + 0.5
    long = 3 + 3 * size
    for y in range(long + 1):
        end = y in (0, long)
        for x in range(size + 1):
            for z in range(2 * size + 2):
                if x * x + (z - r) ** 2 <= r * r + 0.5:
                    piece.box(x, x, y, y, z, z, "N" if end else ("k" if y % 3 == 0 else "H"))
    return piece
