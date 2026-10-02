"""Making the parts and placing them on the core, each on a socket."""

from pewpewdev.tools.boss_candidates.part_kinds import PARTS
from pewpewdev.tools.candidates.canvas import Canvas, Rng
from pewpewdev.tools.candidates.details import trim

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
    """Draw a thin plate on the core under the part (so the part stands out over it, rather than clashing)."""
    half_w, half_h = part_cv.w // 2 - 1, part_cv.h // 2 - 1
    for sx in [x] + ([cv.w - 1 - x] if mirrored else []):
        for cy in range(y - half_h, y + half_h + 1):
            for cx in range(sx - half_w, sx + half_w + 1):
                if cv.filled(cx, cy):
                    cv.set(cx, cy, "x")
