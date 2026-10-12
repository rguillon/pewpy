"""An area to fill and a stand-in for the camera's view of the background."""

from pewpy.scenery.background import Area

AREA = Area(-1.0, 1.0, -1.2, 1.8)


class FakeView:
    """Farther layers cover more and seem to move slower, like through the real camera."""

    def area(self, depth: float) -> Area:
        return Area(-1.0 - 0.2 * depth, 1.0 + 0.2 * depth, -1.2, 1.8 + 0.5 * depth)

    def parallax(self, depth: float) -> float:
        return 1 / (1 + 0.2 * depth)
