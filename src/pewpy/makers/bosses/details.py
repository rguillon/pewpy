"""Details painted on a plan (the bosses' cores): bands, wing edges, panel lines, markings; and trimming it."""

from pewpy.makers.bosses.canvas import Canvas
from pewpy.makers.common.connect import bridges
from pewpy.makers.common.geometry import Rng


def trim(cv: Canvas, symmetric: bool, also: Canvas | None = None) -> None:
    """Drop the empty rows and columns around the ship (a symmetric one stays centred).

    `also` is cropped the same way.
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


def bands(rng: Rng, cv: Canvas) -> None:
    """Paint darker bands across the hull and a pattern on the wings."""
    band = rng.randint(2, 4)
    for x, y in cv.cells_of("hw"):
        if cv.get(x, y) == "h" and y % band == 0:
            cv.set(x, y, "H")
        elif cv.get(x, y) == "w" and (x + y) % 4 == 0:
            cv.set(x, y, "W")


def wing_edges(cv: Canvas) -> None:
    """Paint a light leading edge (towards the nose), a dark line of flaps at the back."""
    for x, y in cv.cells_of("wW"):
        if not cv.filled(x, y + 1):
            cv.set(x, y, "W")
        elif not cv.filled(x, y - 1) and cv.get(x, y + 1) in "wW":
            cv.set(x, y, "k")


def panel_lines(rng: Rng, cv: Canvas) -> None:
    """Draw panel lines across the hull."""
    rows = set(range(2, cv.h - 2, rng.randint(3, 5)))
    for x, y in cv.cells_of("hH"):
        if y in rows and cv.filled(x, y - 1) and cv.filled(x, y + 1):
            cv.set(x, y, "k")


def markings(rng: Rng, cv: Canvas) -> None:
    """Paint the accent color: on the wings' edges (as thin as the wing), and on a few plates."""
    for x, y in cv.cells_of("wW"):
        if (not cv.filled(x - 1, y) or not cv.filled(x + 1, y)) and y % 3 == 0:
            cv.set(x, y, "q")
    plates = cv.cells_of("N")
    for x, y in rng.sample(plates, min(len(plates), rng.randint(1, 4))):
        cv.set(x, y, "p")


def join(cv: Canvas, symmetric: bool) -> None:
    """Join every piece of the plan to the others with a strut 3 cells wide (mirrored on a symmetric boss)."""
    mirror = (lambda cell: (cv.w - 1 - cell[0], cell[1])) if symmetric else None
    way = bridges(cv.cells_of(cv.rows_chars()), mirror)
    for x, y in way:
        for dx, dy in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)):
            for sx in {x + dx, cv.w - 1 - x - dx} if symmetric else {x + dx}:
                if not cv.filled(sx, y + dy):
                    cv.set(sx, y + dy, "N")
