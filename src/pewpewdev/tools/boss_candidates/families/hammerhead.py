"""The hammerhead family."""

from pewpewdev.tools.candidates.canvas import Canvas, Rng


def hammerhead(rng: Rng, cv: Canvas, mx: float, top: float, bottom: float, half: float) -> None:
    """A long body with a wide armored bar across its front."""
    body, head = half * rng.uniform(0.25, 0.4), (bottom - top) * rng.uniform(0.12, 0.2)
    cv.rect(mx - body, mx + body, top, bottom, "h")
    cv.rect(mx - half, mx + half, bottom - head - 2, bottom - 2, "N")
    cv.polygon([(mx - body, top + (bottom - top) * 0.2), (mx - half, top + (bottom - top) * 0.35),
                (mx - half, top + (bottom - top) * 0.45), (mx - body, top + (bottom - top) * 0.45)], "w", "both")  # fmt: skip
