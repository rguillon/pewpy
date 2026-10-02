"""The wing straight attachment."""

from pewpewdev.tools.candidates.canvas import Canvas, Rng


def wing_straight(rng: Rng, cv: Canvas, edge: int, side: str) -> None:
    y, chord = rng.uniform(0.3, 0.7) * cv.h, rng.randint(2, 4)
    tip = max(1.0, chord * rng.uniform(0.3, 0.6))
    shift = (chord - tip) * 0.7
    cv.polygon([(edge + 0.5, y), (-0.5, y + shift), (-0.5, y + shift + tip), (edge + 0.5, y + chord)], "w", side)
