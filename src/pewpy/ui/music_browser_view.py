"""The Dev menu's music browser on screen (pewpy.generators.music): a console (menu_view.py), over the menus' ground.

Above: which song (what it plays for) and what it is; in the middle: whether it's playing; below: what's going on,
and the keys.
"""

from direct.gui.OnscreenText import OnscreenText
from panda3d.core import NodePath, TextNode

from pewpy.ui.menu_view import ITEM_COLOR, SELECTED_COLOR, SHADOW_OFFSET, TEXT_SHADOW, TITLE_COLOR, console

Color = tuple[float, float, float, float]

TITLE_HEIGHT = 0.5  # the texts (aspect2d units)
TITLE_SCALE = 0.08
DETAILS_HEIGHT = 0.36
DETAILS_SCALE = 0.045
DETAILS_WRAP = 36  # in text units: the description's lines
PLAYING_HEIGHT = 0.0
PLAYING_SCALE = 0.06
STATUS_HEIGHT = -0.6
STATUS_SCALE = 0.045
KEYS_HEIGHT = -0.9
KEYS_SCALE = 0.04
PANEL = (-1.05, 1.05, -0.1, 0.6)  # under the texts but the status and the keys: left, right, bottom, top
DISPLAY_TOP = 0.44  # the title stencilled on the plate above it
KEYS = "Left/Right: song   Space: new song   Enter: save   M: music on/off   Escape: back"


class MusicBrowserView:
    """The music browser's texts."""

    def __init__(self, aspect2d: NodePath) -> None:
        """Make the view: nothing written until `describe`."""
        self.root = aspect2d.attachNewNode("music_browser")
        console(self.root, PANEL, DISPLAY_TOP)  # first: under the texts
        self.title = self._text(TITLE_HEIGHT, TITLE_SCALE, TITLE_COLOR)
        self.details = self._text(DETAILS_HEIGHT, DETAILS_SCALE, ITEM_COLOR, wordwrap=DETAILS_WRAP)
        self.playing = self._text(PLAYING_HEIGHT, PLAYING_SCALE, SELECTED_COLOR)
        self.status = self._text(STATUS_HEIGHT, STATUS_SCALE, SELECTED_COLOR)
        self.keys = self._text(KEYS_HEIGHT, KEYS_SCALE, ITEM_COLOR)
        self.keys.setText(KEYS)

    def describe(self, title: str, details: str, status: str) -> None:
        """Write which song it is (`title`), what it is (`details`) and what's going on (`status`)."""
        self.title.setText(title)
        self.details.setText(details)
        self.status.setText(status)

    def show_playing(self, text: str) -> None:
        """Write whether the song plays (only when it changed: Panda3D remakes a text's geometry each time)."""
        if self.playing.getText() != text:
            self.playing.setText(text)

    def destroy(self) -> None:
        """Remove the view's nodes."""
        for text in (self.title, self.details, self.playing, self.status, self.keys):
            text.destroy()
        self.root.removeNode()

    def _text(
        self, z: float, scale: float, color: Color, shadow: Color = TEXT_SHADOW, wordwrap: float | None = None
    ) -> OnscreenText:
        return OnscreenText(
            text="",
            pos=(0, z),
            scale=scale,
            fg=color,
            shadow=shadow,
            shadowOffset=SHADOW_OFFSET,
            align=TextNode.ACenter,
            wordwrap=wordwrap,
            mayChange=True,
            parent=self.root,
        )
