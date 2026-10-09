"""Keeping a model in one piece: every cube touching the others through its faces, no part floating on its own.

A model is cells: tuples of whole coordinates, a plan's (x, y) or a model's (x, y, z). Two cells touch when they are
one apart along one axis. `bridges` finds the cells joining every piece to the others: from each piece, the shortest
way through the empty cells to another piece, mirrored on a symmetric model so it stays symmetric.
"""

from collections import deque
from collections.abc import Callable, Iterable

Cell = tuple[int, ...]
Mirror = Callable[[Cell], Cell]


def pieces(cells: Iterable[Cell]) -> list[set[Cell]]:
    """Split cells into the pieces touching each other, the biggest first (ties: the one with the first cell)."""
    left = set(cells)
    found = []
    while left:
        start = left.pop()
        piece, todo = {start}, [start]
        while todo:
            for near in _around(todo.pop()):
                if near in left:
                    left.remove(near)
                    piece.add(near)
                    todo.append(near)
        found.append(piece)
    return sorted(found, key=lambda piece: (-len(piece), min(piece)))


def bridges(cells: Iterable[Cell], mirror: Mirror | None = None) -> set[Cell]:
    """Return the empty cells to fill so that all the cells are one piece (with their mirror images, if `mirror`).

    Each round, every piece but the biggest gets its way to the nearest other piece; until there's one piece. Only the
    pieces apart from the biggest are found again after each round (the biggest is most of a big model).
    """
    filled = set(cells)
    added: set[Cell] = set()
    biggest, *rest = pieces(filled) or [set()]
    box = _box(filled) if rest else ((), ())  # the ways stay within it: it doesn't grow
    while rest:
        for piece in rest:
            path = _way_out(piece, filled, box)
            path |= {mirror(cell) for cell in path} if mirror else set()
            path -= filled
            added |= path
            filled |= path
        # The pieces again: the biggest stays as it is (it only grows), the others joined to it now go into it.
        rest = []
        for piece in pieces(filled - biggest):
            if any(near in biggest for cell in piece for near in _around(cell)):
                biggest |= piece
            else:
                rest.append(piece)
    return added


def _box(cells: set[Cell]) -> tuple[Cell, Cell]:
    """Return the lowest and highest coordinates of the cells, along each axis."""
    axes = list(zip(*cells, strict=True))
    return tuple(min(axis) for axis in axes), tuple(max(axis) for axis in axes)


def _way_out(piece: set[Cell], filled: set[Cell], box: tuple[Cell, Cell]) -> set[Cell]:
    """Return the empty cells of the shortest way from a piece to any other cell (within the model's `box`)."""
    low, high = box
    came: dict[Cell, Cell] = {cell: cell for cell in piece}  # where each cell was reached from
    todo = deque(sorted(piece))
    while True:  # another piece is always within the box: the way ends there
        cell = todo.popleft()
        for near in _around(cell):
            if near in came or not all(lo <= value <= hi for lo, value, hi in zip(low, near, high, strict=True)):
                continue
            came[near] = cell
            if near in filled:  # another piece: the way there is found
                way, step = set(), cell
                while step not in piece:
                    way.add(step)
                    step = came[step]
                return way
            todo.append(near)


def _around(cell: Cell) -> tuple[Cell, ...]:
    """Return the cells touching a cell through its faces."""
    if len(cell) == 3:  # a model's (the most of them, and big ones: written out, as fast as it goes)
        x, y, z = cell
        return (x - 1, y, z), (x + 1, y, z), (x, y - 1, z), (x, y + 1, z), (x, y, z - 1), (x, y, z + 1)
    x, y = cell  # a plan's
    return (x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)
