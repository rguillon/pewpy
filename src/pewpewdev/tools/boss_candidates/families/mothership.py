"""The mothership family."""

from pewpewdev.tools.candidates.canvas import Canvas, Rng


def mothership(rng: Rng, cv: Canvas, mx: float, top: float, bottom: float, half: float) -> None:
    """A great disc with rings, a hangar mouth open at the front."""
    my = (top + bottom) / 2
    rx, ry = half, (bottom - top) / 2
    cv.ellipse(mx, my, rx, ry, "h")
    cv.ellipse(mx, my, rx * 0.8, ry * 0.8, "N")
    cv.ellipse(mx, my, rx * 0.76, ry * 0.76, "h")
    cv.ellipse(mx, my, rx * 0.35, ry * 0.35, "T")
    cv.rect(mx - rx * 0.15, mx + rx * 0.15, bottom - ry * 0.35, bottom, "k")  # the hangar mouth
