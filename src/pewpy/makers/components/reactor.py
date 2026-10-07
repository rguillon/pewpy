"""A reactor: a round housing, its core glowing on top, fins round it."""

from pewpy.makers.common.geometry import Rng
from pewpy.makers.components.piece import Piece


def reactor(_rng: Rng, size: int) -> Piece:
    """Build a reactor `size` big."""
    piece = Piece()
    r = size + 1
    piece.disc(r + 1, r, 0, size, "N")
    piece.disc(r + 1, r - 0.5, size + 1, size + 1, "h")
    piece.disc(r + 1, max(0.5, r / 2), size + 1, size + 2, "G")
    for dy in (-r - 1, r + 1):  # fins, front and back, and on the sides
        piece.box(0, 0, r + 1 + dy, r + 1 + dy, 0, size, "W")
    piece.box(r + 1, r + 1, r + 1, r + 1, 0, size, "W")
    return piece
