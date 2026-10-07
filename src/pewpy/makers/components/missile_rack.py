"""A missile rack: a box, the warheads of a grid of tubes showing on its front."""

from pewpy.makers.common.geometry import Rng
from pewpy.makers.components.piece import Piece


def missile_rack(_rng: Rng, size: int) -> Piece:
    """Build a missile rack `size` big."""
    piece = Piece()
    front = 2 + 2 * size
    piece.housing(size + 1, 0, front, 0, size + 1)
    for x in range(0, size + 2, 2):
        for z in range(0, size + 2, 2):
            piece.box(x, x, front + 1, front + 1, z, z, "p")  # a warhead
    piece.weapon("missile", 0, front + 1, 0)  # its middle warhead, bottom row
    return piece
