"""The details on every ship: bands, panel lines, plates, a spine, the cockpit, markings, guns, nozzles."""

from pewpewdev.tools.candidates.canvas import Canvas, Rng
from pewpewdev.tools.candidates.palette import HULL


def trim(cv: Canvas, symmetric: bool, also: Canvas | None = None) -> None:
    """Drop the empty rows and columns around the ship (a symmetric one stays centred); `also` is cropped the same
    way.
    """
    rows = [y for y in range(cv.h) if any(cv.filled(x, y) for x in range(cv.w))]
    columns = [x for x in range(cv.w) if any(cv.filled(x, y) for y in range(cv.h))]
    if not rows or not columns:
        return
    left, right = columns[0], columns[-1]
    if symmetric:
        left = min(left, cv.w - 1 - right)
        right = cv.w - 1 - left
    for canvas in [cv] + ([also] if also is not None else []):
        canvas.cells = [row[left : right + 1] for row in canvas.cells[rows[0] : rows[-1] + 1]]
        canvas.h, canvas.w = len(canvas.cells), len(canvas.cells[0])


def detail(rng: Rng, cv: Canvas, symmetric: bool) -> list[dict]:
    """Bands, panel lines, plates, a spine, the cockpit and sensor, markings, guns, nozzles; the engines' flames. A
    symmetric ship gets them on its left half, mirrored.
    """
    bands(rng, cv)
    wing_edges(cv)
    panel_lines(rng, cv)
    plates(rng, cv)
    spine = cv.w // 2 if symmetric else thickest_column(cv)
    if rng.random() < 0.7:
        for x, y in cv.cells_of("hHk"):
            if x == spine:
                cv.set(x, y, "S")
    if rng.random() < 0.35:
        livery(rng, cv)
    cockpit(rng, cv, spine, symmetric)
    markings(rng, cv)
    guns(rng, cv)
    nozzles(rng, cv, spine, symmetric)
    if symmetric:
        for row in cv.cells:
            for x in range(cv.w // 2):
                row[cv.w - 1 - x] = row[x]
    width, length = rng.choice((2.0, 2.4, 3.0)), rng.randint(4, 8)
    return [{"x": x, "y": y, "width": width, "length": length, "towards": "top"} for x, y in cv.cells_of("o")]


def bands(rng: Rng, cv: Canvas) -> None:
    band = rng.randint(2, 4)
    for x, y in cv.cells_of("hw"):
        if cv.get(x, y) == "h" and y % band == 0:
            cv.set(x, y, "H")
        elif cv.get(x, y) == "w" and (x + y) % 4 == 0:
            cv.set(x, y, "W")


def wing_edges(cv: Canvas) -> None:
    """A light leading edge (towards the nose), a dark line of flaps at the back."""
    for x, y in cv.cells_of("wW"):
        if not cv.filled(x, y + 1):
            cv.set(x, y, "W")
        elif not cv.filled(x, y - 1) and cv.get(x, y + 1) in "wW":
            cv.set(x, y, "k")


def panel_lines(rng: Rng, cv: Canvas) -> None:
    rows = set(range(2, cv.h - 2, rng.randint(3, 5)))
    for x, y in cv.cells_of("hH"):
        if y in rows and cv.filled(x, y - 1) and cv.filled(x, y + 1):
            cv.set(x, y, "k")


def plates(rng: Rng, cv: Canvas) -> None:
    """Heavy plates along the hull's sides."""
    for x, y in cv.cells_of("hH"):
        if (not cv.filled(x - 1, y) or not cv.filled(x + 1, y)) and rng.random() < 0.6:
            cv.set(x, y, "N")


def thickest_column(cv: Canvas) -> int:
    counts = [sum(cv.get(x, y) in HULL for y in range(cv.h)) for x in range(cv.w)]
    return max(range(cv.w), key=lambda x: (counts[x], -abs(x - cv.w // 2)))


def livery(rng: Rng, cv: Canvas) -> None:
    """A painted band across the hull."""
    top = rng.randint(0, max(0, cv.h // 2))
    bottom = top + rng.randint(2, 5)
    for x, y in cv.cells_of("hH"):
        if top <= y < bottom:
            cv.set(x, y, "L")


def cockpit(rng: Rng, cv: Canvas, spine: int, symmetric: bool) -> None:
    nose = max((y for y in range(cv.h) if cv.filled(spine, y)), default=cv.h - 1)
    offset = 0 if symmetric or rng.random() < 0.5 else rng.choice((-1, 1)) * rng.randint(1, 2)  # off-centre
    y = max(0, nose - rng.randint(1, max(1, min(5, cv.h // 3))))
    size = 1 if cv.w < 11 else rng.randint(1, 2)
    for cy in range(y - size + 1, y + 1):
        for cx in range(spine + offset - (size - 1), spine + offset + size):
            if cv.filled(cx, cy):
                cv.set(cx, cy, "c")
    if cv.filled(spine + offset, y):
        cv.set(spine + offset, y, "R")


def markings(rng: Rng, cv: Canvas) -> None:
    """The accent color: on the wings' edges (as thin as the wing), and on a few plates."""
    for x, y in cv.cells_of("wW"):
        if (not cv.filled(x - 1, y) or not cv.filled(x + 1, y)) and y % 3 == 0:
            cv.set(x, y, "q")
    plates = cv.cells_of("N")
    for x, y in rng.sample(plates, min(len(plates), rng.randint(1, 4))):
        cv.set(x, y, "p")


def guns(rng: Rng, cv: Canvas) -> None:
    """Barrels pointing down (forward) from the front of the ship."""
    for _ in range(rng.randint(0, 2)):
        x = rng.randrange(cv.w)
        bottom = max((y for y in range(cv.h) if cv.filled(x, y)), default=cv.h - 1)
        for y in range(bottom + 1, min(cv.h, bottom + rng.randint(2, 3) + 1)):
            cv.set(x, y, "r")


def nozzles(rng: Rng, cv: Canvas, spine: int, symmetric: bool) -> None:
    """On the backmost hull cells: 1 to 4 of them, spread out (a symmetric ship's on its left half)."""
    backs = []
    for x in range(cv.w if not symmetric else (cv.w - 1) // 2 + 1):
        top = next((y for y in range(cv.h) if cv.filled(x, y)), None)
        if top is not None and cv.get(x, top) in HULL + "wW" and top <= cv.h // 2:
            backs.append((top, x))
    chosen: list[tuple[int, int]] = []
    wanted = rng.randint(1, 4)
    for top, x in sorted(backs):
        if len(chosen) < wanted and all(abs(x - other) >= 3 for _, other in chosen):
            chosen.append((top, x))
    if not chosen:  # nothing at the back to put one on: the spine's first cell
        chosen = [(next(y for y in range(cv.h) if cv.filled(spine, y)), spine)]
    for top, x in chosen:
        cv.set(x, top, "o")
