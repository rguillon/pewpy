"""The carrier family."""

from pewpewdev.tools.candidates.canvas import Canvas, Rng


def carrier(rng: Rng, cv: Canvas, mx: float, top: float, bottom: float, half: float) -> None:
    """A long flat-topped hull with chamfered corners, a flight deck down the middle, sponsons on the sides."""
    cut, length = max(2.0, half * 0.25), bottom - top
    cv.polygon([(mx - half, top + cut), (mx - half + cut, top), (mx + half - cut, top), (mx + half, top + cut),
                (mx + half, bottom - 2 * cut), (mx, bottom), (mx - half, bottom - 2 * cut)], "h")  # fmt: skip
    cv.rect(mx - 2, mx + 2, top + 2, bottom - 2 * cut, "k")
    for y in range(round(top) + 4, round(bottom - 2 * cut), 4):
        cv.set(round(mx), y, "W")
    y = top + rng.uniform(0.15, 0.4) * length
    cv.rect(mx - half * 1.4, mx - half - 1, y, y + rng.uniform(0.25, 0.45) * length, "w", "both")
