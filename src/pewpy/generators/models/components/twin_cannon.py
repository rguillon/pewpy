"""A twin cannon: a boxy breech and two long barrels with muzzle collars."""

from pewpy.generators.models.common.geometry import Rng
from pewpy.generators.models.components.piece import Piece


def twin_cannon(_rng: Rng, size: int) -> Piece:
    """Build a twin cannon `size` big."""
    piece = Piece()
    back = 2 * size + 1
    piece.housing(size + 1, 0, back, 0, size)
    x = size // 2 + 1
    tip = back + 3 + 3 * size
    piece.box(x, x, back + 1, tip, size // 2 + 1, size // 2 + 1, "r")
    piece.box(x, x, tip - 1, tip - 1, size // 2 + 1, size // 2 + 2, "N")  # the muzzle collar
    piece.weapon("cannon", x, tip, size // 2 + 1)
    return piece
