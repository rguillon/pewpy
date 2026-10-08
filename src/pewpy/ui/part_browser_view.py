"""The Dev menu's parts browser on screen (see pewpy.generators.models.parts.browser).

The part in the middle, swaying a little to show its depth. Above: what the part is; below: its tags, and the keys.
"""

import math

from panda3d.core import NodePath

from pewpy.ui.menu_view import ITEM_COLOR, SELECTED_COLOR, TITLE_COLOR
from pewpy.ui.showcase import DISTANCE
from pewpy.ui.text_label import Color, TextsView

VIEW_SIZE = 1.6  # world units, DISTANCE from the camera: the part is drawn this big
VIEW_HEIGHT = -0.08  # where its middle is, up from the screen's
ROOM = 1.1  # the part fills this share of VIEW_SIZE
SWAY = 25.0  # degrees: the part turns this much each way around its up axis...
SWAY_SPEED = 0.7  # ...this fast (radians a second)
TITLE_HEIGHT = 0.86  # the texts (aspect2d units)
TITLE_SCALE = 0.08
DETAILS_HEIGHT = 0.77
DETAILS_SCALE = 0.04
DETAILS_WRAP = 40  # in text units: the description's lines
INFO_HEIGHT = -0.72
INFO_SCALE = 0.04
STATUS_HEIGHT = -0.8
KEYS_HEIGHT = -0.9
KEYS = "Left/Right: part   Z/S: size   Space: new part   Escape: back"
PART_LIT: Color = (1.0, 1.0, 1.0, 1.0)


def fit_scale(extent: float) -> float:
    """Return how much to scale a part whose bigger side is `extent` (world units) to fit the view."""
    return VIEW_SIZE / (extent * ROOM)


class PartBrowserView:
    """The part and the texts."""

    def __init__(self, camera: NodePath, aspect2d: NodePath) -> None:
        """Make the view: nothing on show until `show`."""
        self.root = camera.attachNewNode("part_browser")
        self.root.setPos(0, DISTANCE, VIEW_HEIGHT)
        self.scaled = self.root.attachNewNode("scaled")
        self.model = self.scaled.attachNewNode("model")
        self.texts = TextsView(aspect2d, "part_browser_texts")
        self.title = self.texts.centered_text(TITLE_HEIGHT, TITLE_SCALE, TITLE_COLOR)
        self.details = self.texts.centered_text(DETAILS_HEIGHT, DETAILS_SCALE, ITEM_COLOR, wordwrap=DETAILS_WRAP)
        self.info = self.texts.centered_text(INFO_HEIGHT, INFO_SCALE, TITLE_COLOR)
        self.status = self.texts.centered_text(STATUS_HEIGHT, INFO_SCALE, SELECTED_COLOR)
        self.keys = self.texts.centered_text(KEYS_HEIGHT, INFO_SCALE, ITEM_COLOR)
        self.keys.setText(KEYS)
        self.time = 0.0

    def show(self, model: NodePath, size: int) -> None:
        """Show the part's model, scaled to fit the view."""
        for child in self.scaled.getChildren():
            child.removeNode()
        self.model = self.scaled.attachNewNode("model")
        model.copyTo(self.model)
        bounds = self.model.getTightBounds()
        extent = 1.0
        if bounds is not None:
            low, high = bounds
            extent = max(extent, high.x - low.x, high.z - low.z)
        self.scaled.setScale(fit_scale(extent))
        self.info.setText(f"size: {size}")
        self.update(0.0)

    def describe(self, title: str, details: str, status: str) -> None:
        """Write what the part is (`title`, `details`) and what's going on (`status`)."""
        self.title.setText(title)
        self.details.setText(details)
        self.status.setText(status)

    def update(self, dt: float) -> None:
        """Sway the model."""
        self.time += dt
        self.model.setH(SWAY * math.sin(self.time * SWAY_SPEED))

    def destroy(self) -> None:
        """Remove the view's nodes."""
        self.root.removeNode()
        self.texts.destroy()
