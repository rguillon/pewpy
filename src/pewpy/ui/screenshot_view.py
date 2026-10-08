"""The Dev menu's screenshots on screen (see pewpy.generators.screenshots): their texts, on a console at the top.

Hidden while a screenshot is saved, so only the game is in it. The backgrounds browser shows its texts the same way.
"""

from panda3d.core import NodePath

from pewpy.ui.menu_view import ITEM_COLOR, SELECTED_COLOR, TITLE_COLOR, console
from pewpy.ui.text_label import TextsView

PANEL = (-1.15, 1.15, 0.58, 0.97)  # left, right, bottom, top (aspect2d units)
DISPLAY_TOP = 0.84  # the title stencilled on the plate above it
TITLE_HEIGHT = 0.885
TITLE_SCALE = 0.055
DETAILS_HEIGHT = 0.78
STATUS_HEIGHT = 0.71
KEYS_HEIGHT = 0.64
SCALE = 0.04
KEYS = "Left/Right: world   Space: new screenshot   Enter: save   Escape: back"
BACKGROUND_KEYS = "Left/Right: theme   Space: new background   Escape: back"


class ScreenshotView(TextsView):
    """The screenshots' texts."""

    def __init__(self, aspect2d: NodePath, keys: str = KEYS) -> None:
        """Make the view, with its `keys`: nothing else written until `describe`."""
        super().__init__(aspect2d, "screenshots")
        console(self.root, PANEL, DISPLAY_TOP)  # first: under the texts
        self.title = self.centered_text(TITLE_HEIGHT, TITLE_SCALE, TITLE_COLOR)
        self.details = self.centered_text(DETAILS_HEIGHT, SCALE, ITEM_COLOR)
        self.status = self.centered_text(STATUS_HEIGHT, SCALE, SELECTED_COLOR)
        self.keys = self.centered_text(KEYS_HEIGHT, SCALE, ITEM_COLOR)
        self.keys.setText(keys)

    def describe(self, title: str, details: str, status: str) -> None:
        """Write which world it is (`title`), the shot (`details`) and what's going on (`status`)."""
        self.title.setText(title)
        self.details.setText(details)
        self.status.setText(status)
