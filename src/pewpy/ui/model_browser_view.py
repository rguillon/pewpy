"""The Dev menu's model browser on screen (see pewpy.generators.models.browser).

The model in the middle (a boss with its parts in place, the parts blinking slowly so they stand out), swaying a
little to show its depth, inside a frame: the size
new models are made to. Both drawn to the scale that fits the bigger of them on the screen, so the model can be
compared with its size. Above: what the model is; below: its size, what's going on, and the keys.
"""

import math

from direct.gui.OnscreenText import OnscreenText
from panda3d.core import LineSegs, NodePath, TextNode

from pewpy.ui.menu_view import ITEM_COLOR, SELECTED_COLOR, TITLE_COLOR
from pewpy.ui.showcase import DISTANCE

Color = tuple[float, float, float, float]

VIEW_SIZE = 1.6  # world units, DISTANCE from the camera: the bigger of the model and its frame is drawn this big
VIEW_HEIGHT = -0.08  # where its middle is, up from the screen's
ROOM = 1.1  # the bigger of the two fills this share of VIEW_SIZE
SWAY = 25.0  # degrees: the model turns this much each way around its up axis...
SWAY_SPEED = 0.7  # ...this fast (radians a second)
PART_BLINK = 1.2  # seconds: a boss's parts are lit up for the first half of each, then plain (a slow blink)
PART_LIT: Color = (1.9, 1.9, 1.9, 1.0)  # how much brighter they are when lit up
FRAME_COLOR: Color = (1.0, 0.72, 0.22, 1)  # amber, like the HUD's readouts
TITLE_HEIGHT = 0.86  # the texts (aspect2d units)
TITLE_SCALE = 0.08
DETAILS_HEIGHT = 0.77
DETAILS_SCALE = 0.04
DETAILS_WRAP = 40  # in text units: the description's lines
INFO_HEIGHT = -0.72
INFO_SCALE = 0.04
STATUS_HEIGHT = -0.8
KEYS_HEIGHT = -0.9
KEYS = "Left/Right: model   Z/S: height   Q/D: width   Space: new model   Enter: save   Escape: back"


def fit_scale(extent: float) -> float:
    """Return how much to scale a model and its frame whose bigger side is `extent` (world units) to fit the view."""
    return VIEW_SIZE / (extent * ROOM)


class ModelBrowserView:
    """The model, its frame and the texts."""

    def __init__(self, camera: NodePath, aspect2d: NodePath) -> None:
        """Make the view: nothing on show until `show`."""
        self.root = camera.attachNewNode("model_browser")
        self.root.setPos(0, DISTANCE, VIEW_HEIGHT)
        self.scaled = self.root.attachNewNode("scaled")
        self.model = self.scaled.attachNewNode("model")
        self.texts_root = aspect2d.attachNewNode("model_browser_texts")
        self.title = self._text(TITLE_HEIGHT, TITLE_SCALE, TITLE_COLOR)
        self.details = self._text(DETAILS_HEIGHT, DETAILS_SCALE, ITEM_COLOR, wordwrap=DETAILS_WRAP)
        self.info = self._text(INFO_HEIGHT, INFO_SCALE, TITLE_COLOR)
        self.status = self._text(STATUS_HEIGHT, INFO_SCALE, SELECTED_COLOR)
        self.keys = self._text(KEYS_HEIGHT, INFO_SCALE, ITEM_COLOR)
        self.keys.setText(KEYS)
        self.time = 0.0
        self.parts: list[NodePath] = []  # a boss's destroyable parts on show, blinking

    def show(self, pieces: list[tuple[NodePath, float, float]], size: tuple[float, float]) -> None:
        """Show the model's pieces (each model, and where its middle goes, in world units) in a frame of `size`.

        The first piece is the model (a boss's core), the others a boss's destroyable parts.
        """
        for child in self.scaled.getChildren():
            child.removeNode()
        self.model = self.scaled.attachNewNode("model")
        placed = []
        for piece, x, y in pieces:
            node = self.model.attachNewNode("piece")
            piece.copyTo(node)
            node.setPos(x, 0, y)
            placed.append(node)
        self.parts = placed[1:]
        frame = _frame(size)
        frame.reparentTo(self.scaled)
        frame.setLightOff()
        frame.setShaderOff()
        frame.setBin("fixed", 10)
        frame.setDepthTest(False)
        bounds = self.model.getTightBounds()
        extent = max(size)
        if bounds is not None:
            low, high = bounds
            extent = max(extent, high.x - low.x, high.z - low.z)
        self.scaled.setScale(fit_scale(extent))
        self.update(0.0)

    def describe(self, title: str, details: str, info: str, status: str) -> None:
        """Write what the model is (`title`, `details`), its size (`info`) and what's going on (`status`)."""
        self.title.setText(title)
        self.details.setText(details)
        self.info.setText(info)
        self.status.setText(status)

    def update(self, dt: float) -> None:
        """Sway the model, and blink a boss's parts: lit up for half of every PART_BLINK seconds."""
        self.time += dt
        self.model.setH(SWAY * math.sin(self.time * SWAY_SPEED))
        lit = self.time % PART_BLINK < PART_BLINK / 2
        for part in self.parts:
            if lit:
                part.setColorScale(*PART_LIT)
            else:
                part.clearColorScale()

    def destroy(self) -> None:
        """Remove the view's nodes."""
        self.root.removeNode()
        for text in (self.title, self.details, self.info, self.status, self.keys):
            text.destroy()
        self.texts_root.removeNode()

    def _text(self, z: float, scale: float, color: Color, wordwrap: float | None = None) -> OnscreenText:
        return OnscreenText(
            text="",
            pos=(0, z),
            scale=scale,
            fg=color,
            align=TextNode.ACenter,
            wordwrap=wordwrap,
            mayChange=True,
            parent=self.texts_root,
        )


def _frame(size: tuple[float, float]) -> NodePath:
    """Make a rectangle `size` across and up (in the model's plane), its middle at the origin."""
    width, height = size
    lines = LineSegs("frame")
    lines.setColor(*FRAME_COLOR)
    lines.setThickness(2.0)
    corners = [(-width / 2, -height / 2), (width / 2, -height / 2), (width / 2, height / 2), (-width / 2, height / 2)]
    lines.moveTo(corners[-1][0], 0, corners[-1][1])
    for x, z in corners:
        lines.drawTo(x, 0, z)
    return NodePath(lines.create())
