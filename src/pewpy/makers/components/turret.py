"""A gun turret: a round base, a housing with a dome, one to three barrels pointing forward."""

from pewpy.makers.common.geometry import Rng
from pewpy.makers.components.piece import Piece


def turret(rng: Rng, size: int) -> Piece:
    """Build a turret `size` big (1: a ship's, more on a boss)."""
    piece = Piece()
    r = size + 1
    piece.disc(r, r, 0, 0, "N")
    piece.disc(r, r - 0.5, 1, size, "h")
    piece.disc(r, max(0.5, r / 2), size + 1, size + 1, "S")
    barrels = rng.choice((1, 2) if size == 1 else (1, 2, 3))
    xs = {1: [0], 2: [1], 3: [0, 2]}[barrels]
    tip = 2 * r + size + 1
    for x in xs:
        piece.box(x, x, r, tip, size, size, "r")
        piece.weapon("turret", x, tip, size)
    return piece
