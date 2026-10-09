"""Drawing a Menu (menu.py): a console like the HUD's instrument panels (see panel.py).

A gunmetal plate with the title stencilled on it, and a recessed display with faint scanlines where the items glow
amber, the highlighted one bright, on a lit row, between markers. Behind it, the game's ground scrolls by.
"""

from direct.gui.OnscreenText import OnscreenText
from panda3d.core import NodePath

from pewpy.ui import panel
from pewpy.ui.menu import Menu

Color = tuple[float, float, float, float]

TITLE_COLOR: Color = panel.LABEL  # stencilled on the plate
SELECTED_COLOR: Color = panel.AMBER
ITEM_COLOR: Color = (0.62, 0.43, 0.13, 1)  # a dimmer amber
ROW_LIGHT: Color = (1.0, 0.72, 0.22, 0.12)  # behind the highlighted item
TEXT_SHADOW: Color = (0.0, 0.0, 0.0, 0.8)  # under texts over the ground, to read them
SHADOW_OFFSET = (0.05, 0.05)  # in text units
TITLE_SCALE = 0.075
ITEM_SCALE = 0.06
ITEM_SPACING = 0.09
TOP = 0.42  # height of the title on screen (aspect2d units): the ship select's ships fit under its menu...
LOWEST = -0.95  # ...but a long menu goes up as much as it takes for its console to end above this
ASCENT = 0.8  # of a line above its baseline, and DESCENT under it, in its scale
DESCENT = 0.3
PADDING = 0.06  # from the plate's edges to the display (its screws are in the corners)
DISPLAY_GAP = 0.035  # between the title and the display, and around the items in it
SCANLINE_STEP = 0.012
MARKERS = "> {} <"  # around the highlighted item


def console(parent: NodePath, frame: tuple[float, float, float, float], display_top: float) -> NodePath:
    """Draw a console: a plate, and a display with scanlines from its bottom up to `display_top`.

    `frame` is the plate's (left, right, bottom, top).
    """
    left, right, bottom, top = frame
    root = parent.attachNewNode("console")
    panel.plate(root, left, right, bottom, top)
    inside = (left + PADDING, right - PADDING, bottom + PADDING / 2, display_top)
    panel.display(root, *inside)
    panel.scanlines(root, *inside, SCANLINE_STEP)
    return root


class MenuView:
    """The menu on screen (or none)."""

    def __init__(self, parent: NodePath) -> None:
        """Make the menu's nodes under `parent`, with no menu on show."""
        self.root = parent.attachNewNode("menu")
        self.panel = self.root.attachNewNode("panel")  # first: drawn under the texts
        self.row = panel.card(self.root, -1, 1, -1, 1, ROW_LIGHT)  # the highlighted item's lit row
        self.row.hide()
        self.menu: Menu | None = None
        self.texts: list[OnscreenText] = []
        self.half_width = 0.0  # the display's, from the middle

    def show(self, menu: Menu | None) -> None:
        """Draw `menu`, or nothing when it's None (while playing)."""
        for text in self.texts:
            text.destroy()
        self.texts = []
        for child in self.panel.getChildren():
            child.removeNode()
        self.row.hide()
        self.menu = menu
        if menu is None:
            return
        title_lines = menu.title.count("\n") + 1
        below = TITLE_SCALE * (title_lines - 1) + TITLE_SCALE * DESCENT + 2 * DISPLAY_GAP + ITEM_SCALE * ASCENT
        below += (len(menu.items) - 1) * ITEM_SPACING + ITEM_SCALE * DESCENT + DISPLAY_GAP + PADDING / 2
        top = max(TOP, LOWEST + below)  # the title's height
        title = self._text(menu.title, top, TITLE_SCALE, TITLE_COLOR)
        self.texts.append(title)
        display_top = top - TITLE_SCALE * (title_lines - 1) - TITLE_SCALE * DESCENT - DISPLAY_GAP
        first = display_top - DISPLAY_GAP - ITEM_SCALE * ASCENT
        for index, item in enumerate(menu.items):
            self.texts.append(self._text(item.label, first - index * ITEM_SPACING, ITEM_SCALE, ITEM_COLOR))
        bottom = first - (len(menu.items) - 1) * ITEM_SPACING - ITEM_SCALE * DESCENT - DISPLAY_GAP
        self._console(title, menu, bottom, display_top, top)
        self.refresh()

    def refresh(self) -> None:
        """Show which item is highlighted: bright, between markers, on a lit row."""
        if self.menu is None:
            return
        for index, (item, text) in enumerate(zip(self.menu.items, self.texts[1:], strict=True)):
            selected = index == self.menu.selected
            text.setText(MARKERS.format(item.label) if selected else item.label)
            text.setFg(SELECTED_COLOR if selected else ITEM_COLOR)
            if selected:
                z = text.getTextPos()[1]
                self.row.setScale(self.half_width, 1, ITEM_SPACING / 2)
                self.row.setPos(0, 0, z + ITEM_SCALE * (ASCENT - DESCENT) / 2)
                self.row.show()

    def _console(self, title: OnscreenText, menu: Menu, bottom: float, display_top: float, title_top: float) -> None:
        """Draw the console under the texts: as wide as the widest (highlighted), as tall as them all."""
        widths = [title.textNode.getWidth() * TITLE_SCALE]
        for text, item in zip(self.texts[1:], menu.items, strict=True):
            text.setText(MARKERS.format(item.label))
            widths.append(text.textNode.getWidth() * ITEM_SCALE)
        self.half_width = max(widths) / 2 + DISPLAY_GAP
        half = self.half_width + PADDING
        top = title_top + TITLE_SCALE * ASCENT + PADDING / 2
        console(self.panel, (-half, half, bottom - PADDING / 2, top), display_top)

    def _text(self, text: str, z: float, scale: float, color: Color) -> OnscreenText:
        return OnscreenText(text=text, pos=(0, z), scale=scale, fg=color, mayChange=True, parent=self.root)
