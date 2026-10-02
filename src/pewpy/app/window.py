"""The window, the camera and the lights.

The game keeps its shape in any window, the camera sees the whole play area.
"""

import math
import os
import sys

from direct.showbase.ShowBase import ShowBase
from panda3d.core import GraphicsEngine, PerspectiveLens, Point2, Point3, Vec3

from pewpy import config
from pewpy.graphics import lighting
from pewpy.scenery.background.view import space_color

Color = tuple[float, float, float, float]
BACKGROUND_COLOR: Color = space_color()
GAME_ASPECT = config.WINDOW_WIDTH / config.WINDOW_HEIGHT  # the game area keeps this shape (width / height)


class Window(ShowBase):
    """The window: the game's shape whatever its size (black bars around it), the camera and the lights."""

    def finalizeExit(self) -> None:  # noqa: N802 - overrides ShowBase
        """Leave at once under WSL, where the window can hang while it's torn down.

        There the GPU goes through Mesa's d3d12 driver (see `make run`); nothing is left to save.
        """
        if os.environ.get("GALLIUM_DRIVER") == "d3d12":
            sys.stdout.flush()
            sys.stderr.flush()
            os._exit(0)
        super().finalizeExit()

    def _setup_letterbox(self) -> None:
        # The game keeps its 3:4 shape whatever the window size: the 3D view and the HUD are drawn in a centered
        # region, with black bars around it. The window clears to black, the region to the space color.
        self.win.setClearColor((0, 0, 0, 1))
        region = self.camNode.getDisplayRegion(0)
        region.setClearColorActive(True)
        region.setClearColor(BACKGROUND_COLOR)
        self._fit_letterbox()

    def _fit_letterbox(self) -> None:
        if not self.win.hasSize():
            return
        dimensions = letterbox(self.win.getXSize(), self.win.getYSize())
        for camera in (self.cam, self.cam2d, self.cam2dp):
            node = camera.node()
            for index in range(node.getNumDisplayRegions()):
                node.getDisplayRegion(index).setDimensions(*dimensions)
        preview = getattr(self, "level_preview", None)  # not made yet when the window first opens
        if preview is not None:
            preview.fit(dimensions)

    # ShowBase calls these two on window changes. (The types-panda3d stubs say GraphicsEngine for `win`; it's
    # really the window, but we don't use it.)
    def windowEvent(self, win: GraphicsEngine) -> None:  # noqa: N802 - overrides ShowBase
        """Fit the letterbox to the window's new size."""
        super().windowEvent(win)
        self._fit_letterbox()

    def getAspectRatio(self, win: GraphicsEngine | None = None) -> float:  # noqa: ARG002, N802 - overrides ShowBase
        # ShowBase sizes the lens and the HUD (aspect2d) from this: always the game's shape, see _setup_letterbox.
        """Return the game's shape, whatever the window's: ShowBase sizes the lens and the HUD (aspect2d) from it."""
        return GAME_ASPECT

    def _setup_camera(self) -> None:
        # The game plays on the X/Z plane (X right, Z up the screen); the camera sits in front of it (-Y),
        # tilted so the top of the play area is farther away, and backs off until the whole area fits.
        lens = PerspectiveLens()
        aspect = GAME_ASPECT
        vertical_fov = config.CAMERA_FOV
        horizontal_fov = math.degrees(2 * math.atan(math.tan(math.radians(vertical_fov) / 2) * aspect))
        lens.setFov(horizontal_fov, vertical_fov)
        lens.setNearFar(0.1, 100)
        self.cam.node().setLens(lens)

        tilt = math.radians(config.CAMERA_TILT)
        direction = Vec3(0, -math.cos(tilt), -math.sin(tilt))
        distance = 1.0
        while True:
            self.cam.setPos(direction * distance)
            self.cam.lookAt(0, 0, 0)
            if self._play_area_visible() or distance > 50:
                break
            distance += 0.05

    def _play_area_visible(self, margin: float = 1.04) -> bool:
        lens = self.cam.node().getLens()
        half_width, half_height = config.PLAY_WIDTH / 2 * margin, config.PLAY_HEIGHT / 2 * margin
        for x in (-half_width, half_width):
            for z in (-half_height, half_height):
                point = self.cam.getRelativePoint(self.render, Point3(x, 0, z))
                if not lens.project(point, Point2()):
                    return False
        return True

    def _setup_lights(self) -> None:
        lighting.setup(self)


def letterbox(window_width: int, window_height: int, aspect: float = GAME_ASPECT) -> tuple[float, float, float, float]:
    """Return the biggest centered region of shape `aspect` (width / height) in the window.

    As (left, right, bottom, top), fractions of the window.
    """
    window_aspect = window_width / max(window_height, 1)
    if window_aspect > aspect:  # too wide: bars on the left and right
        width = aspect / window_aspect
        return (1 - width) / 2, (1 + width) / 2, 0.0, 1.0
    height = window_aspect / aspect  # too tall: bars at the top and bottom
    return 0.0, 1.0, (1 - height) / 2, (1 + height) / 2
