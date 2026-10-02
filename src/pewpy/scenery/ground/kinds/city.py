"""The city: blocks of buildings between streets, alleys, the odd park."""

import random

from pewpy.scenery.ground.settlement import Canvas, Layout, Rect, Settlement, Surface, grid, lots, shrink
from pewpy.scenery.params import Knobs


class City(Settlement):
    knobs = (
        "block",
        "street",
        "alley",
        "alley_share",
        "lot",
        "sidewalk",
        "park_share",
        "tower_share",
        "midrise_share",
        "tower",
        "midrise",
        "lowrise",
        "tree_size",
    )

    def layout(self, rng: random.Random, width: float, loop: float, knobs: Knobs) -> Layout:
        """Blocks of buildings between streets (`block` apart, `street` wide): mostly low buildings, some mid-rises,
        a few towers (`tower_share`, `midrise_share`; their heights between `tower`, `midrise`, `lowrise`), the odd park
        (`park_share`). Lots are `lot` wide at least, a `sidewalk` around them.
        """
        canvas = Canvas(rng, width, loop, Surface.STREET, knobs["tree_size"])
        street = knobs["street"]
        towers, midrises = knobs["tower_share"], knobs["tower_share"] + knobs["midrise_share"]
        for top, bottom, left, right in grid(width, loop, knobs["block"]):
            block = (top + street, bottom, left + street, right)  # the street runs along its top and left
            canvas.fill(block, Surface.PAVEMENT)
            for part in _alleys(canvas, block, knobs["alley"], knobs["alley_share"]):
                for lot in lots(rng, shrink(part, knobs["sidewalk"]), knobs["lot"]):
                    if rng.random() < knobs["park_share"]:
                        _park(canvas, lot)
                        continue
                    roll = rng.random()
                    span = (
                        knobs["tower"] if roll < towers else knobs["midrise"] if roll < midrises else knobs["lowrise"]
                    )
                    canvas.add("building", shrink(lot, rng.uniform(0.004, 0.012)), rng.uniform(*span))
        return canvas.layout()


def _alleys(canvas: Canvas, block: Rect, width: float, share: float) -> list[Rect]:
    """Some blocks (`share` of them) are cut in two by a narrow alley, one way or the other: the two halves (or the
    whole block).
    """
    rng = canvas.rng
    if rng.random() >= share:
        return [block]
    top, bottom, left, right = block
    if rng.random() < 0.5:  # across the block
        middle = rng.uniform(top + 0.35 * (bottom - top), top + 0.65 * (bottom - top))
        alley = (middle - width / 2, middle + width / 2, left, right)
        halves = [(top, alley[0], left, right), (alley[1], bottom, left, right)]
    else:  # along it
        middle = rng.uniform(left + 0.35 * (right - left), left + 0.65 * (right - left))
        alley = (top, bottom, middle - width / 2, middle + width / 2)
        halves = [(top, bottom, left, alley[2]), (top, bottom, alley[3], right)]
    canvas.fill(alley, Surface.STREET)
    return halves


def _park(canvas: Canvas, lot: Rect) -> None:
    canvas.fill(lot, Surface.NATURAL)
    top, bottom, left, right = shrink(lot, 0.02)
    for _ in range(round((bottom - top) * (right - left) / 0.004)):
        canvas.tree(canvas.rng.uniform(left, right), canvas.rng.uniform(top, bottom))
