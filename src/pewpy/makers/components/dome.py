"""A sensor dome: a half sphere, a sensor glowing on top."""

from pewpy.makers.common.geometry import Rng
from pewpy.makers.components.piece import Piece


def dome(_rng: Rng, size: int) -> Piece:
    """Build a sensor dome `size` big."""
    piece = Piece()
    r = size + 1
    for z in range(r):
        piece.disc(r, (r * r - z * z) ** 0.5, z, z, "S")
    piece.box(0, 0, r, r, r, r, "R")
    return piece
