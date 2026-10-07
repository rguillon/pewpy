"""A boss's core: its outline (a family, maybe two, with appendages), then its details."""

from pewpy.makers.bosses.appendages import APPENDAGES
from pewpy.makers.bosses.canvas import Canvas
from pewpy.makers.bosses.families import FAMILIES
from pewpy.makers.common.geometry import Rng

COMBINED_SHARE = 0.25
APPENDAGES_COUNT = (0, 0, 1, 1, 2)  # how many appendages a core gets, picked from these: few big shapes
SIZES = {  # (share, width range, height range), in cubes
    "medium": (0.35, (41, 61), (31, 51)),
    "large": (0.4, (61, 85), (41, 71)),
    "huge": (0.25, (85, 115), (55, 95)),
}


def core(rng: Rng, lopsided: bool, cubes: tuple[int, int] | None = None) -> tuple[Canvas, str, str]:
    """Draw the core's outline: return (canvas, family, size class).

    Its size picked at random, or `cubes` (columns and rows; its class the one nearest that).
    """
    if cubes is None:
        size = rng.choices(list(SIZES), [share for share, _, _ in SIZES.values()])[0]
        _, widths, heights = SIZES[size]
        cv = Canvas(rng.randrange(widths[0], widths[1] + 1, 2), rng.randint(*heights))
    else:
        size = min(SIZES, key=lambda name: abs(cubes[0] - sum(SIZES[name][1]) / 2))
        cv = Canvas(cubes[0] | 1, cubes[1])  # odd: a middle column
    mx = cv.w // 2
    family = rng.choice(list(FAMILIES))
    reach = cv.w * rng.uniform(0.3, 0.45)  # half-width of the main hull (appendages go beyond)
    if rng.random() < COMBINED_SHARE:  # a second family: at the back, or on the sides
        second = rng.choice([name for name in FAMILIES if name != family])
        if rng.random() < 0.5:
            FAMILIES[family](rng, cv, mx, cv.h * 0.35, cv.h - 1, reach)
            FAMILIES[second](rng, cv, mx, 0, cv.h * 0.45, reach * 0.6)
        else:
            FAMILIES[family](rng, cv, mx, 0, cv.h - 1, reach * 0.6)
            side_x = mx - reach * 0.75
            FAMILIES[second](rng, cv, side_x, cv.h * 0.2, cv.h * 0.8, reach * 0.3)
            FAMILIES[second](rng, cv, cv.mirror(side_x), cv.h * 0.2, cv.h * 0.8, reach * 0.3)
        family = f"{family}+{second}"
    else:
        FAMILIES[family](rng, cv, mx, 0, cv.h - 1, reach)
    for _ in range(rng.choice(APPENDAGES_COUNT)):
        side = "one" if lopsided and rng.random() < 0.6 else "both"
        rng.choice(APPENDAGES)(rng, cv, mx, reach, side)
    if lopsided:  # a chunk shorn off one side, a bulge on the other
        cut = rng.uniform(0.2, 0.35) * cv.w
        cv.polygon([(-0.5, rng.uniform(0.2, 0.6) * cv.h), (cut, -0.5), (-0.5, -0.5)], ".")
        y, tall = rng.uniform(0.3, 0.7) * cv.h, rng.randint(4, 8)
        rows = range(round(y), round(y + tall) + 1)
        edge = max((x for x in range(cv.w) for row in rows if cv.filled(x, row)), default=cv.w // 2)
        cv.rect(edge - 1, min(cv.w - 1, edge + rng.randint(3, 7)), y, y + tall, "N")  # against the hull's side
    return cv, family, size


def superstructure(rng: Rng, cv: Canvas) -> None:
    """Draw raised decks towards the back, a bridge with a sensor near the middle, hangar bays, lights."""
    mx = _middle(cv)
    top = rng.randint(2, max(2, cv.h // 3))
    width = rng.randint(2, max(2, cv.w // 10))
    for x, y in cv.cells_of("hH"):
        if abs(x - mx) <= width and top <= y <= top + cv.h // 4:
            cv.set(x, y, "T")
    for x, y in cv.cells_of("T"):
        if abs(x - mx) <= max(1, width // 2) and y <= top + cv.h // 6:
            cv.set(x, y, "S")
    bridge = top + cv.h // 6
    for x in range(mx - 1, mx + 2):
        cv.set(x, bridge, "c")
    cv.set(mx, bridge, "R")
    _hangars(rng, cv)
    _lights(rng, cv)


def _hangars(rng: Rng, cv: Canvas) -> None:
    """Hangar bays: dark rectangles on the hull."""
    for _ in range(rng.randint(1, 3 + cv.w // 30)):
        x, y = rng.randrange(cv.w), rng.randrange(cv.h)
        if cv.get(x, y) in "hH":
            cv.rect(x - 1, x + 1, y, y + rng.randint(2, 4), "k", "both" if rng.random() < 0.7 else "one")


def _lights(rng: Rng, cv: Canvas) -> None:
    """Rows of lights along the armor."""
    rows = set(range(3, cv.h, rng.randint(5, 8)))
    for x, y in cv.cells_of("N"):
        if y in rows and x % 3 == 0:
            cv.set(x, y, "p")


def _middle(cv: Canvas) -> int:
    counts = [sum(cv.filled(x, y) for y in range(cv.h)) for x in range(cv.w)]
    return max(range(cv.w), key=lambda x: (counts[x], -abs(x - cv.w // 2)))


def armor(rng: Rng, cv: Canvas) -> None:
    """Armor bands along the hull's edges."""
    for x, y in cv.cells_of("hH"):
        if any(not cv.filled(x + dx, y + dy) for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1))) and rng.random() < 0.8:
            cv.set(x, y, "N")


def paint(rng: Rng, cv: Canvas) -> str:
    """Pick a paint scheme: plain, two-tone (big areas of the hull in the livery color) or glowing seams."""
    scheme = rng.choice(("plain", "plain", "two-tone", "seams"))
    if scheme == "two-tone":
        split = rng.uniform(0.3, 0.7) * cv.h
        stripes = rng.random() < 0.5
        for x, y in cv.cells_of("hH"):
            if (stripes and (y // 4) % 3 == 0) or (not stripes and y < split):
                cv.set(x, y, "L")
    elif scheme == "seams":
        for x, y in cv.cells_of("k"):
            if rng.random() < 0.5:
                cv.set(x, y, "g")
    return scheme


def engine_bank(rng: Rng, cv: Canvas) -> list[dict]:
    """Nozzles along the back of the hull, spread out, with big flames (more on bigger bosses)."""
    backs = []
    for x in range(cv.w):
        top = next((y for y in range(cv.h) if cv.filled(x, y)), None)
        if top is not None and cv.get(x, top) in "hHNTSkL" and top <= cv.h // 3:
            backs.append((top, x))
    chosen: list[tuple[int, int]] = []
    wanted = rng.randint(3, 6 + cv.w // 20)
    for top, x in sorted(backs):
        if len(chosen) < wanted and all(abs(x - other) >= 4 for _, other in chosen):
            chosen.append((top, x))
    width, length = rng.uniform(3.5, 6.0) * (1 + cv.w / 150), rng.randint(10, 16 + cv.w // 10)
    for top, x in chosen:
        cv.rect(x - 1, x + 1, top, top, "o")
    return [{"x": x, "y": top, "width": round(width, 1), "length": length, "towards": "top"} for top, x in chosen]
