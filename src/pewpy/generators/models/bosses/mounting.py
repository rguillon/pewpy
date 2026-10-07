"""Making the destroyable parts (built-in parts, see pewpy.generators.models.components) and placing them on sockets."""

from pewpy.generators.models.bosses.canvas import Canvas
from pewpy.generators.models.common.geometry import Rng
from pewpy.generators.models.components import COMPONENTS, PART_COMPONENTS, Piece

PARTS_BY_SIZE = {"medium": (0, 4), "large": (2, 7), "huge": (3, 10)}
PART_WIDTH = 40  # cubes of a core's width for each size step of its parts (one more on wider cores)


def part(rng: Rng, kind: str, boss_width: int) -> Piece:
    """Build a destroyable part: a built-in part of a kind (see PART_COMPONENTS), sized to its boss."""
    return COMPONENTS[kind](rng, rng.randint(1, 2) + boss_width // PART_WIDTH)


def mount(
    rng: Rng, cv: Canvas, symmetric: bool, size: str, wanted: int | None = None
) -> list[tuple[str, int, int, bool]]:
    """Where the parts go: (kind, x, y, mirrored too) on hull cells of the core, in cubes from its top-left.

    As many as the size class has room for, or exactly `wanted` (pairs mirroring each other, one in the middle for an
    odd count, the ones there's no room left for in the middle too).
    """
    low, high = PARTS_BY_SIZE[size]
    exact = wanted is not None
    wanted = rng.randint(low, high) if wanted is None else wanted
    kinds = rng.sample(PART_COMPONENTS, rng.randint(1, 3))  # a boss uses a few kinds of parts, not all of them
    spots = [(x, y) for x, y in cv.cells_of("hHNTwL") if x < cv.w // 2 - 3]
    spacing = max(8, cv.w // 8)
    mounts: list[tuple[str, int, int, bool]] = []
    placed = 0
    while wanted - placed >= (2 if exact and symmetric else 1) and spots:
        x, y = rng.choice(spots)
        mirrored = (symmetric or rng.random() < 0.5) and not (exact and wanted - placed < 2)
        mounts.append((rng.choice(kinds), x, y, mirrored))
        placed += 2 if mirrored else 1
        spots = [(sx, sy) for sx, sy in spots if abs(sx - x) > spacing or abs(sy - y) > spacing]
    if exact:
        missing = wanted - placed
        mounts += [
            (rng.choice(kinds), cv.w // 2, cv.h * (index + 1) // (missing + 1), False) for index in range(missing)
        ]
    elif rng.random() < 0.35:  # something in the middle
        mounts.append((rng.choice(kinds), cv.w // 2, rng.randint(cv.h // 3, cv.h * 2 // 3), False))
    return mounts


def socket(cv: Canvas, x: int, y: int, piece: Piece, mirrored: bool) -> None:
    """Draw a thin plate on the core under the part, its middle at (x, y) (so it stands out over it, not clashing).

    It follows the part's outline with a cube to spare, so no flat plate shows round a rounded part.
    """
    middle = middle_row(piece)
    under = {(px + dx, py - middle + dy) for px, py in piece.footprint() for dx in (-1, 0, 1) for dy in (-1, 0, 1)}
    for sx in [x] + ([cv.w - 1 - x] if mirrored else []):
        for dx, dy in under:
            if cv.filled(sx + dx, y + dy):
                cv.set(sx + dx, y + dy, "x")


def middle_row(piece: Piece) -> int:
    """Return a built-in part's middle row (its rows from its back, 0)."""
    return max(y for _, y in piece.footprint()) // 2
