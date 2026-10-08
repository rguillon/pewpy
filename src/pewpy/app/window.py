"""The window, the camera and the lights.

The game keeps its shape in any window, the camera sees the whole play area.
"""

import math
import os
import sys
from typing import cast

from direct.showbase.ShowBase import ShowBase
from panda3d.core import (
    CardMaker,
    Filename,
    FrameBufferProperties,
    GraphicsBuffer,
    GraphicsEngine,
    GraphicsOutput,
    GraphicsPipe,
    PerspectiveLens,
    Point2,
    Point3,
    SamplerState,
    TextNode,
    Texture,
    Vec3,
    WindowProperties,
)

from pewpy import config
from pewpy.data import data_folder
from pewpy.graphics import lighting
from pewpy.scenery.background.view import space_color

Color = tuple[float, float, float, float]
BACKGROUND_COLOR: Color = space_color()
GAME_ASPECT = config.WINDOW_WIDTH / config.WINDOW_HEIGHT  # the game area keeps this shape (width / height)
FONT = "orbitron.ttf"  # every text's font, in data/fonts/ (with its license)
FONT_PIXELS_PER_UNIT = 64  # how finely its letters are rendered: higher, sharper big text


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
        # The game keeps its 5:4 shape whatever the window size: it's drawn in a centered region, with black bars
        # around it. The 3D view is drawn into a buffer of its own (at most SCENE_MAX_HEIGHT pixels tall, see
        # scene_size), cleared to the space color, then stretched over that region on the 2D layer, under the HUD
        # and the menus, which are drawn at the window's own resolution. The window clears to black.
        self.win.setClearColor((0, 0, 0, 1))
        self.scene_buffer = self._make_scene_buffer()
        self.win.removeDisplayRegion(self.camNode.getDisplayRegion(0))
        region = self.scene_buffer.makeDisplayRegion()
        region.setCamera(self.cam)
        region.setClearColorActive(True)
        region.setClearColor(BACKGROUND_COLOR)
        region.setClearDepthActive(True)
        maker = CardMaker("scene")
        maker.setFrameFullscreenQuad()
        card = self.render2d.attachNewNode(maker.generate())
        card.setTexture(self.scene_buffer.getTexture())
        card.setBin("background", 0)
        self._fit_letterbox()

    def _make_scene_buffer(self) -> GraphicsBuffer:
        properties = FrameBufferProperties()
        properties.setRgbColor(True)
        properties.setRgbaBits(8, 8, 8, 0)
        properties.setDepthBits(24)
        flags = GraphicsPipe.BFRefuseWindow | GraphicsPipe.BFResizeable
        size = WindowProperties()
        size.setSize(config.WINDOW_WIDTH, config.WINDOW_HEIGHT)
        output = self.graphicsEngine.makeOutput(
            self.pipe, "scene", -1, properties, size, flags, self.win.getGsg(), self.win
        )
        buffer = cast("GraphicsBuffer", output)  # a buffer, resizable: BFRefuseWindow, BFResizeable
        texture = Texture("scene")
        texture.setMinfilter(SamplerState.FT_linear)
        texture.setMagfilter(SamplerState.FT_linear)
        texture.setWrapU(SamplerState.WM_clamp)
        texture.setWrapV(SamplerState.WM_clamp)
        buffer.addRenderTexture(texture, GraphicsOutput.RTMBindOrCopy)
        return buffer

    def _fit_letterbox(self) -> None:
        if not self.win.hasSize():
            return
        dimensions = letterbox(self.win.getXSize(), self.win.getYSize())
        for camera in (self.cam2d, self.cam2dp):
            node = camera.node()
            for index in range(node.getNumDisplayRegions()):
                node.getDisplayRegion(index).setDimensions(*dimensions)
        left, right, bottom, top = dimensions
        width, height = scene_size(
            round(self.win.getXSize() * (right - left)), round(self.win.getYSize() * (top - bottom))
        )
        if (width, height) != (self.scene_buffer.getXSize(), self.scene_buffer.getYSize()):
            self.scene_buffer.setSize(width, height)

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
        """Check if all corners of the play area are visible in the camera's field of view.

        This method checks if four key points (corners) of the play area are projected 
        onto the screen by the camera lens. If any of those points fall outside the 
        viewing frustum, the whole play area is considered not visible.

        Args:
            margin: A factor to add padding around the play area (default 1.04).

        Returns:
            True if all corners are visible, False otherwise.
        """

    def _setup_lights(self) -> None:
        lighting.setup(self)

    def _setup_font(self) -> None:
        """Make the game's font the default one, for every text made from now on."""
        path = Filename.fromOsSpecific(str(data_folder() / "fonts" / FONT)).getFullpath()
        font = self.loader.loadFont(path, pixelsPerUnit=FONT_PIXELS_PER_UNIT)
        TextNode.setDefaultFont(font)


def scene_size(width: int, height: int, max_height: int = config.SCENE_MAX_HEIGHT) -> tuple[int, int]:
    """Return the 3D view's size in pixels for a game area of `width` x `height`: its own, or less, same shape."""
    scale = min(1.0, max_height / max(height, 1))
    return max(round(width * scale), 1), max(round(height * scale), 1)


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
