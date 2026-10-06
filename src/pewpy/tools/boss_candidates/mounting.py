"""Making the parts and placing them on the core, each on a socket."""

from pewpy.tools.boss_candidates.canvas import Canvas
from pewpy.tools.boss_candidates.details import trim
from pewpy.tools.boss_candidates.part_kinds import PARTS
from pewpy.tools.common.geometry import Rng

PARTS_BY_SIZE = {"medium": (0, 4), "large": (2, 7), "huge": (3, 10)}


def part(rng: Rng, kind: str, boss_width: int) -> Canvas:
    """Draw a part, sized to its boss."""
    scale = boss_width / 60
    size = max(9, round(rng.uniform(11, 23) * scale)) | 1  # odd
    cv = Canvas(size, max(9, round(size * rng.uniform(0.8, 1.4))))
    PARTS[kind](rng, cv)
    trim(cv, symmetric=True)
    return cv


def mount(rng: Rng, cv: Canvas, symmetric: bool, size: str) -> list[tuple[str, int, int, bool]]:
    """Where the parts go: (kind, x, y, mirrored too) on hull cells of the core, in cubes from its top-left."""
    low, high = PARTS_BY_SIZE[size]
    wanted = rng.randint(low, high)
    kinds = rng.sample(list(PARTS), rng.randint(1, 3))  # a boss uses a few kinds of parts, not all of them
    spots = [(x, y) for x, y in cv.cells_of("hHNTwL") if x < cv.w // 2 - 3]
    spacing = max(8, cv.w // 8)
    mounts: list[tuple[str, int, int, bool]] = []
    placed = 0
    while placed < wanted and spots:
        x, y = rng.choice(spots)
        mirrored = symmetric or rng.random() < 0.5
        mounts.append((rng.choice(kinds), x, y, mirrored))
        placed += 2 if mirrored else 1
        spots = [(sx, sy) for sx, sy in spots if abs(sx - x) > spacing or abs(sy - y) > spacing]
    if rng.random() < 0.35:  # something in the middle
        mounts.append((rng.choice(kinds), cv.w // 2, rng.randint(cv.h // 3, cv.h * 2 // 3), False))
    return mounts


def socket(cv: Canvas, x: int, y: int, part_cv: Canvas, mirrored: bool) -> None:
    """Draw a thin plate on the core under the part (so the part stands out over it, rather than clashing).

    It follows the part's outline with a cube to spare, so no flat plate shows round a rounded part.
    """
    left, top = part_cv.w // 2, part_cv.h // 2
    under = {
        (px - left + dx, py - top + dy)
        for px, py in part_cv.cells_of(part_cv.rows_chars())
        for dx in (-1, 0, 1)
        for dy in (-1, 0, 1)
    }
    for sx in [x] + ([cv.w - 1 - x] if mirrored else []):
        for dx, dy in under:
            if cv.filled(sx + dx, y + dy):
                cv.set(sx + dx, y + dy, "x")
