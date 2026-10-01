"""Drawing a Menu (menu.py) as centered text: the title, then the items, the highlighted one bright."""

from direct.gui.OnscreenText import OnscreenText
from panda3d.core import NodePath

from pewpy.ui.menu import Menu

Color = tuple[float, float, float, float]

TITLE_COLOR: Color = (1.0, 1.0, 1.0, 1)
SELECTED_COLOR: Color = (1.0, 0.9, 0.3, 1)
ITEM_COLOR: Color = (0.55, 0.57, 0.65, 1)
TITLE_SCALE = 0.1
ITEM_SCALE = 0.065
ITEM_SPACING = 0.1
TOP = 0.3  # height of the title on screen (aspect2d units)


class MenuView:
    def __init__(self, parent: NodePath) -> None:
        self.root = parent.attachNewNode("menu")
        self.menu: Menu | None = None
        self.texts: list[OnscreenText] = []

    def show(self, menu: Menu | None) -> None:
        """Draw `menu`, or nothing when it's None (while playing)."""
        for text in self.texts:
            text.destroy()
        self.texts = []
        self.menu = menu
        if menu is None:
            return
        title_lines = menu.title.count("\n") + 1
        self.texts.append(self._text(menu.title, TOP, TITLE_SCALE, TITLE_COLOR))
        first = TOP - TITLE_SCALE * title_lines - ITEM_SPACING
        for index, item in enumerate(menu.items):
            self.texts.append(self._text(item.label, first - index * ITEM_SPACING, ITEM_SCALE, ITEM_COLOR))
        self.refresh()

    def refresh(self) -> None:
        """Show which item is highlighted: bright, between arrows."""
        if self.menu is None:
            return
        for index, (item, text) in enumerate(zip(self.menu.items, self.texts[1:], strict=True)):
            selected = index == self.menu.selected
            text.setText(f"> {item.label} <" if selected else item.label)
            text.setFg(SELECTED_COLOR if selected else ITEM_COLOR)

    def _text(self, text: str, z: float, scale: float, color: Color) -> OnscreenText:
        return OnscreenText(text=text, pos=(0, z), scale=scale, fg=color, mayChange=True, parent=self.root)
