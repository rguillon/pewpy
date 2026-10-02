"""The wing swept attachment."""

from pewpewdev.tools.candidates.canvas import Canvas, Rng


def wing_swept(rng: Rng, cv: Canvas, edge: int, side: str) -> None:
    root = rng.uniform(0.35, 0.65) * cv.h
    sweep = rng.uniform(-0.35, 0.35) * cv.h  # back (up) or forward (down)
    chord = rng.randint(2, 4)
    tip = max(1.0, chord * rng.uniform(0.3, 0.6))  # narrower at the tip
    cv.polygon(
        [(edge + 0.5, root), (0, root + sweep), (0, root + sweep + tip), (edge + 0.5, root + chord + 1)], "w", side
    )
    if rng.random() < 0.5:
        cv.rect(0, 1, root + sweep - 1, root + sweep + chord, "N", side)  # a pod on the tip
