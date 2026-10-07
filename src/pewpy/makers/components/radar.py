"""A radar: a mast, a dish on it, a glowing feed in the dish's middle."""

from pewpy.makers.common.geometry import Rng
from pewpy.makers.components.piece import Piece


def radar(_rng: Rng, size: int) -> Piece:
    """Build a radar `size` big."""
    piece = Piece()
    r = size + 1
    piece.box(0, 0, r, r, 0, size + 1, "k")
    piece.disc(r, r, size + 2, size + 2, "W")
    piece.disc(r, max(0.5, r - 1.5), size + 2, size + 2, "S")
    piece.box(0, 0, r, r, size + 3, size + 3, "R")
    return piece
