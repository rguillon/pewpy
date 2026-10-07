"""An antenna: a base, a thin mast, a light on its tip."""

from pewpy.generators.models.common.geometry import Rng
from pewpy.generators.models.components.piece import Piece


def antenna(rng: Rng, size: int) -> Piece:
    """Build an antenna `size` big."""
    piece = Piece()
    piece.box(-1, 1, 0, 2, 0, 0, "N")
    tall = 1 + 2 * size + rng.randint(0, 2)
    piece.box(0, 0, 1, 1, 1, tall, "k")
    piece.box(0, 0, 1, 1, tall + 1, tall + 1, rng.choice("Rp"))
    return piece
