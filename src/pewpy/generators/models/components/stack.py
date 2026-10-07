"""Exhaust stacks: one or two chimneys, dark at their mouths."""

from pewpy.generators.models.common.geometry import Rng
from pewpy.generators.models.components.piece import Piece


def stack(rng: Rng, size: int) -> Piece:
    """Build exhaust stacks `size` big."""
    piece = Piece()
    tall = 2 + 2 * size
    x = rng.choice((0, size))  # one in the middle, or a pair
    piece.box(x, x + size - 1, 0, size - 1, 0, tall, "N")
    piece.box(x, x + size - 1, 0, size - 1, tall, tall, "k")
    piece.box(x, x + size - 1, 0, size - 1, tall // 2, tall // 2, "H")  # a band
    return piece
