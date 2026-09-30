"""A small live view of a level's background, in a window of its own on the level select screen.

The preview has its own scene (its own lights and shading, like the game's: lighting.py), its own camera placed like
the game's but seeing only the middle of the ground, and its own display region: a rectangle near the top of the
game area, drawn over the game's 3D view and under the menus. The highlighted level's ground scrolls in it at the
level's speed. Previews are built once and kept until `clear` (moving up and down the list doesn't rebuild them).
"""

import math

from panda3d.core import Camera, CardMaker, GraphicsOutput, NodePath, PerspectiveLens

from pewpy import lighting
from pewpy.background import Scenery
from pewpy.background_view import BackgroundView, CameraView, sky_color
from pewpy.level import Level

Color = tuple[float, float, float, float]

# Where the window is, in aspect2d units: above the level select's title, as wide as fits.
FRAME = (-0.72, 0.72, 0.46, 1.24)  # left, right, bottom, top
FRAME_COLOR: Color = (0.55, 0.57, 0.65, 1)  # the menus' dim color
FRAME_WIDTH = 0.006
FIELD_OF_VIEW = 26.0  # vertical, degrees: the middle of what the game's camera sees
REGION_SORT = 5  # after the game's 3D view (0), before the menus (render2d, 10)


class LevelPreview:
    def __init__(self, window: GraphicsOutput, main_camera: NodePath, render: NodePath, aspect2d: NodePath) -> None:
        self.root = NodePath("preview")
        lighting.light(self.root)
        left, right, bottom, top = FRAME
        extent_x, extent_y = aspect2d_extent(aspect2d)
        # The same rectangle as a share of the game area (letterboxed in the window: see `fit`).
        self.share = (
            (left / extent_x + 1) / 2,
            (right / extent_x + 1) / 2,
            (bottom / extent_y + 1) / 2,
            (top / extent_y + 1) / 2,
        )
        lens = PerspectiveLens()
        aspect = (right - left) / (top - bottom)
        horizontal = math.degrees(2 * math.atan(math.tan(math.radians(FIELD_OF_VIEW) / 2) * aspect))
        lens.setFov(horizontal, FIELD_OF_VIEW)
        lens.setNearFar(0.1, 100)
        self.camera = self.root.attachNewNode(Camera("preview_camera", lens))
        self.camera.setPos(main_camera.getPos(render))
        self.camera.setHpr(main_camera.getHpr(render))
        self.view = CameraView(self.camera, lens, self.root)
        self.region = window.makeDisplayRegion(*self.share)
        self.region.setSort(REGION_SORT)
        self.region.setCamera(self.camera)
        self.region.setClearColorActive(True)
        self.region.setClearDepthActive(True)
        self.frame = self._frame(aspect2d)
        self.cache: dict[int, tuple[BackgroundView, Level]] = {}
        self.shown: int | None = None
        self.hide()

    def show(self, key: int, level: Level) -> None:
        """Show level `key` (built the first time)."""
        if self.shown is not None and self.shown != key:
            self.cache[self.shown][0].root.hide()
        if key not in self.cache:
            scenery = Scenery(
                level.background,
                self.view,
                seed=level.background_seed,
                ground_voxel=level.ground_voxel,
                clouds=level.clouds,
            )
            self.cache[key] = (BackgroundView(scenery, self.root, level.time_of_day), level)
        view, _ = self.cache[key]
        view.root.show()
        self.shown = key
        self.region.setClearColor(sky_color(level.background, level.time_of_day))
        self.region.setActive(True)
        self.frame.show()

    def hide(self) -> None:
        self.region.setActive(False)
        self.frame.hide()
        if self.shown is not None:
            self.cache[self.shown][0].root.hide()
        self.shown = None

    def clear(self) -> None:
        """Forget every preview built so far (and hide the window)."""
        self.hide()
        for view, _ in self.cache.values():
            view.destroy()
        self.cache.clear()

    def update(self, dt: float) -> None:
        """Scroll the shown level's background."""
        if self.shown is None:
            return
        view, level = self.cache[self.shown]
        view.scenery.update(dt, level.scroll_speed)
        view.sync()

    def fit(self, game_area: tuple[float, float, float, float]) -> None:
        """Follow the game area (the letterboxed part of the window, as shares of it)."""
        area_left, area_right, area_bottom, area_top = game_area
        left, right, bottom, top = self.share
        width, height = area_right - area_left, area_top - area_bottom
        self.region.setDimensions(
            area_left + left * width,
            area_left + right * width,
            area_bottom + bottom * height,
            area_bottom + top * height,
        )

    def _frame(self, aspect2d: NodePath) -> NodePath:
        """A thin border around the window, on the menus' layer."""
        frame = aspect2d.attachNewNode("preview_frame")
        left, right, bottom, top = FRAME
        w = FRAME_WIDTH
        for x0, x1, y0, y1 in (
            (left - w, right + w, top, top + w),
            (left - w, right + w, bottom - w, bottom),
            (left - w, left, bottom, top),
            (right, right + w, bottom, top),
        ):
            maker = CardMaker("edge")
            maker.setFrame(x0, x1, y0, y1)
            edge = frame.attachNewNode(maker.generate())
            edge.setColor(FRAME_COLOR)
        return frame


def aspect2d_extent(aspect2d: NodePath) -> tuple[float, float]:
    """How far aspect2d reaches right and up from the middle of the game area (1 along the shorter side)."""
    scale = aspect2d.getScale()
    return 1 / scale[0], 1 / scale[2]
