"""An engine: a long housing in bands, its nozzle on its back face, an intake at its front."""

from pewpy.makers.common.geometry import Rng
from pewpy.makers.components.piece import Piece


def engine(_rng: Rng, size: int) -> Piece:
    """Build an engine `size` big: its flame comes out of its back (y = 0)."""
    piece = Piece()
    front = 3 + 3 * size
    piece.housing(size + 1, 0, front, 0, size + 1)
    piece.box(-size, size, 0, 0, 1, size, "o")  # the nozzle
    piece.box(-size, size, front, front, 1, size, "k")  # the intake
    piece.nozzles.append((0, 0, (size + 1) / 2, 2 * size + 1.4))
    return piece
