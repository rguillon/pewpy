"""The block core."""

from pewpewdev.tools.candidates.canvas import Canvas, Rng


def core_block(rng: Rng, cv: Canvas, mx: int, half: int) -> None:
    cut, bottom = rng.randint(1, 3), cv.h - 1
    cv.polygon(
        [(mx - half, cut), (mx - half + cut, 0), (mx + half - cut, 0), (mx + half, cut), (mx + half, bottom - cut),
         (mx + half - cut, bottom), (mx - half + cut, bottom), (mx - half, bottom - cut)],
        "h",
    )  # fmt: skip
