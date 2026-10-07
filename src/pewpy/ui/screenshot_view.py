"""The Dev menu's screenshots on screen (see pewpy.dev.screenshots): their texts, on a console at the top.

Hidden while a screenshot is saved, so only the game is in it. The backgrounds browser shows its texts the same way.
"""

from direct.gui.OnscreenText import OnscreenText
from panda3d.core import NodePath, TextNode

from pewpy.ui.menu_view import ITEM_COLOR, SELECTED_COLOR, SHADOW_OFFSET, TEXT_SHADOW, TITLE_COLOR, console

Color = tuple[float, float, float, float]

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


class ScreenshotView:
    """The screenshots' texts."""

    def __init__(self, aspect2d: NodePath, keys: str = KEYS) -> None:
        """Make the view, with its `keys`: nothing else written until `describe`."""
        self.root = aspect2d.attachNewNode("screenshots")
        console(self.root, PANEL, DISPLAY_TOP)  # first: under the texts
        self.title = self._text(TITLE_HEIGHT, TITLE_SCALE, TITLE_COLOR)
        self.details = self._text(DETAILS_HEIGHT, SCALE, ITEM_COLOR)
        self.status = self._text(STATUS_HEIGHT, SCALE, SELECTED_COLOR)
        self.keys = self._text(KEYS_HEIGHT, SCALE, ITEM_COLOR)
        self.keys.setText(keys)

    def describe(self, title: str, details: str, status: str) -> None:
        """Write which world it is (`title`), the shot (`details`) and what's going on (`status`)."""
        self.title.setText(title)
        self.details.setText(details)
        self.status.setText(status)

    def destroy(self) -> None:
        """Remove the view's nodes."""
        for text in (self.title, self.details, self.status, self.keys):
            text.destroy()
        self.root.removeNode()

    def _text(self, z: float, scale: float, color: Color, shadow: Color = TEXT_SHADOW) -> OnscreenText:
        return OnscreenText(
            text="",
            pos=(0, z),
            scale=scale,
            fg=color,
            shadow=shadow,
            shadowOffset=SHADOW_OFFSET,
            align=TextNode.ACenter,
            mayChange=True,
            parent=self.root,
        )
