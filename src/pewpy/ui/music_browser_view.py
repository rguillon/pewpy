"""The Dev menu's music browser on screen (pewpy.generators.music): a console (menu_view.py), over the menus' ground.

Above: which song (what it plays for) and what it is; in the middle: whether it's playing; below: what's going on,
and the keys.
"""

from panda3d.core import NodePath

from pewpy.ui.menu_view import ITEM_COLOR, SELECTED_COLOR, TITLE_COLOR, console
from pewpy.ui.text_label import TextsView

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


class MusicBrowserView(TextsView):
    """The music browser's texts."""

    def __init__(self, aspect2d: NodePath) -> None:
        """Make the view: nothing written until `describe`."""
        super().__init__(aspect2d, "music_browser")
        console(self.root, PANEL, DISPLAY_TOP)  # first: under the texts
        self.title = self.centered_text(TITLE_HEIGHT, TITLE_SCALE, TITLE_COLOR)
        self.details = self.centered_text(DETAILS_HEIGHT, DETAILS_SCALE, ITEM_COLOR, wordwrap=DETAILS_WRAP)
        self.playing = self.centered_text(PLAYING_HEIGHT, PLAYING_SCALE, SELECTED_COLOR)
        self.status = self.centered_text(STATUS_HEIGHT, STATUS_SCALE, SELECTED_COLOR)
        self.keys = self.centered_text(KEYS_HEIGHT, KEYS_SCALE, ITEM_COLOR)
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
