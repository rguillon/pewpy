"""The dreadnought family."""

from pewpewdev.tools.candidates.canvas import Canvas, Rng


def dreadnought(rng: Rng, cv: Canvas, mx: float, top: float, bottom: float, half: float) -> None:
    """A huge arrowhead, stepped towards its middle."""
    length = bottom - top
    cv.polygon([(mx - half, top + rng.uniform(0.0, 0.25) * length), (mx, top), (mx + half, top + rng.uniform(0.0, 0.25) * length),
                (mx + 2, bottom), (mx - 2, bottom)], "h")  # fmt: skip
    for step, char in ((1, "T"), (2, "S")):
        inset = step * half / 3.5
        cv.polygon([(mx - half + inset, top + length * 0.2 + inset * 0.3), (mx, top + inset * 0.4),
                    (mx + half - inset, top + length * 0.2 + inset * 0.3), (mx, bottom - inset)], char)  # fmt: skip
