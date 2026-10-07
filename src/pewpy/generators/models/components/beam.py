"""A beam emitter: a long prism narrowing to a glowing tip."""

from pewpy.generators.models.common.geometry import Rng
from pewpy.generators.models.components.piece import Piece


def beam(_rng: Rng, size: int) -> Piece:
    """Build a beam emitter `size` big."""
    piece = Piece()
    long = 4 + 4 * size
    for y in range(long):
        half = max(0, round((size + 1) * (1 - 0.6 * y / long)))
        piece.box(-half, half, y, y, 0, half, "N" if y % 3 == 0 else "h")
        piece.box(0, 0, y, y, half + 1, half + 1, "S")
    piece.box(0, 0, long, long + 1, 0, 1, "G")
    piece.weapon("laser", 0, long + 1, 0)
    return piece
