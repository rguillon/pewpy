"""The ship selection screen, under its menu: every ship side by side, spinning, with its name and bars comparing
their characteristics; the highlighted one bigger, with its description and numbers at the bottom."""

from panda3d.core import CardMaker, Lens, NodePath, Point2, Point3, TextNode

from pewpy.menu_view import ITEM_COLOR, SELECTED_COLOR
from pewpy.player import ShipSpec
from pewpy.showcase import DISTANCE, ModelShowcase

Color = tuple[float, float, float, float]

COLUMN_SPACING = 0.8  # between the ships' columns (aspect2d units)
SHIP_HEIGHT = -0.36  # where the ships spin (aspect2d units)
SHIP_SIZE = 0.2  # a ship's model (fitted to 1 x 1 x 1) is drawn this big; the highlighted one bigger
SELECTED_GROWTH = 1.25
NAME_HEIGHT = -0.54
NAME_SCALE = 0.055
FIRST_BAR = -0.62  # the bars, one under the other
BAR_SPACING = 0.052
BAR_WIDTH = 0.28
BAR_HEIGHT = 0.03
LABEL_SCALE = 0.04
LABEL_WIDTH = 0.22  # from a label's start to its bar
DETAILS_HEIGHT = -0.86
DETAILS_SCALE = 0.038
BAR_EMPTY: Color = (0.12, 0.13, 0.17, 1)
BAR_FULL: Color = (0.3, 0.85, 1.0, 1)
BAR_DIM: Color = (0.25, 0.3, 0.38, 1)
DETAILS_COLOR: Color = (0.7, 0.72, 0.8, 1)


def characteristics(ships: list[ShipSpec]) -> list[list[tuple[str, float]]]:
    """For each ship: (name, share of the best of all ships, 0 to 1) of what the bars show."""
    rows = [
        ("Armor", [ship.health for ship in ships]),
        ("Speed", [ship.speed for ship in ships]),
        ("Size", [ship.size for ship in ships]),
        ("Repair", [ship.regeneration for ship in ships]),
    ]
    return [[(name, values[index] / (max(values) or 1.0)) for name, values in rows] for index in range(len(ships))]


def details(ship: ShipSpec) -> str:
    text = f"{ship.description}\nHealth {ship.health:g}   Speed {ship.speed:g}   Size {ship.size:g}"
    if ship.regeneration:
        text += f"\nRepairs {ship.regeneration:g} health a second, {ship.regeneration_delay:g} s after it stops firing"
    return text


class ShipSelectView:
    def __init__(
        self,
        ships: list[ShipSpec],
        models: list[NodePath],
        camera: NodePath,
        lens: Lens,
        aspect2d: NodePath,
        extent: tuple[float, float],
    ) -> None:
        """`models`: each ship's model, fitted to 1 x 1 x 1 (copied, so they can be shared with the game).
        `extent`: aspect2d's right and top edges (the ships are placed in 3D to line up with the texts)."""
        self.ships = ships
        self.root = aspect2d.attachNewNode("ship_select")
        self.showcases: list[ModelShowcase] = []
        self.names: list[TextNode] = []
        self.bars: list[list[tuple[TextNode, NodePath]]] = []  # per ship: (label, fill) per bar
        right, top = extent
        for index, (model, stats) in enumerate(zip(models, characteristics(ships), strict=True)):
            x = (index - (len(ships) - 1) / 2) * COLUMN_SPACING
            showcase = ModelShowcase([("", model)], camera, SHIP_SIZE, radius=0.0)
            showcase.root.setPos(_on_screen(lens, x / right, SHIP_HEIGHT / top))
            self.showcases.append(showcase)
            self.names.append(self._text(ships[index].name.title(), x, NAME_HEIGHT, NAME_SCALE))
            left = x - (LABEL_WIDTH + BAR_WIDTH) / 2
            column = []
            for row, (label, share) in enumerate(stats):
                y = FIRST_BAR - row * BAR_SPACING
                text = self._text(label, left, y, LABEL_SCALE, centered=False)
                self._card(left + LABEL_WIDTH, y, BAR_WIDTH, BAR_EMPTY)
                fill = self._card(left + LABEL_WIDTH, y, BAR_WIDTH * max(share, 0.001), BAR_FULL)
                column.append((text, fill))
            self.bars.append(column)
        self.details = self._text("", 0.0, DETAILS_HEIGHT, DETAILS_SCALE)
        self.selected = -1

    def select(self, index: int) -> None:
        """Highlight ship `index` (none if it's out of range: the menu's "Back")."""
        self.selected = index
        for position, (showcase, name, column) in enumerate(zip(self.showcases, self.names, self.bars, strict=True)):
            chosen = position == index
            showcase.root.setScale(SELECTED_GROWTH if chosen else 1.0)
            name.setTextColor(SELECTED_COLOR if chosen else ITEM_COLOR)
            for label, fill in column:
                label.setTextColor(DETAILS_COLOR if chosen else ITEM_COLOR)
                fill.setColor(BAR_FULL if chosen else BAR_DIM)
        text = details(self.ships[index]) if 0 <= index < len(self.ships) else ""
        self.details.setText(text)

    def update(self, dt: float) -> None:
        for position, showcase in enumerate(self.showcases):
            if position == self.selected:  # only the highlighted ship spins
                showcase.update(dt)

    def destroy(self) -> None:
        for showcase in self.showcases:
            showcase.destroy()
        self.root.removeNode()

    def _text(self, text: str, x: float, y: float, scale: float, centered: bool = True) -> TextNode:
        node = TextNode("ship_select_text")
        node.setText(text)
        node.setAlign(TextNode.ACenter if centered else TextNode.ALeft)
        node.setTextColor(ITEM_COLOR)
        path = self.root.attachNewNode(node)
        path.setScale(scale)
        path.setPos(x, 0, y)
        return node

    def _card(self, left: float, y: float, width: float, color: Color) -> NodePath:
        maker = CardMaker("bar")
        maker.setFrame(0, width, -BAR_HEIGHT / 2, BAR_HEIGHT / 2)
        card = self.root.attachNewNode(maker.generate())
        card.setPos(left, 0, y + LABEL_SCALE * 0.3)  # centered on the label's letters
        card.setColor(color)
        return card


def _on_screen(lens: Lens, film_x: float, film_y: float) -> Point3:
    """The point DISTANCE in front of the camera (the showcase's plane) that shows at (film_x, film_y)."""
    near, far = Point3(), Point3()
    lens.extrude(Point2(film_x, film_y), near, far)
    return near + (far - near) * ((DISTANCE - near.y) / (far.y - near.y))
