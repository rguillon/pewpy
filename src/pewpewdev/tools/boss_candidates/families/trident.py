"""The trident family."""

from pewpewdev.tools.candidates.canvas import Canvas, Rng


def trident(rng: Rng, cv: Canvas, mx: float, top: float, bottom: float, half: float) -> None:
    """A heavy body at the back with three prongs reaching forward."""
    length = bottom - top
    split = top + length * rng.uniform(0.35, 0.5)
    cv.rect(mx - half, mx + half, top, split, "h")
    width = max(2.0, half * 0.14)
    for x in (mx - half + width, mx):
        cv.polygon([(x - width, split), (x + width, split), (x + 0.5, bottom - (0 if x == mx else length * 0.1)),
                    (x - 0.5, bottom - (0 if x == mx else length * 0.1))], "N", "both" if x != mx else "one")  # fmt: skip
