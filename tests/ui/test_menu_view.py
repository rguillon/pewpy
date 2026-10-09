"""Drawing a menu."""

from panda3d.core import NodePath

from pewpy.ui.menu import Menu, MenuItem
from pewpy.ui.menu_view import LOWEST, TOP, MenuView


def drawn(count: int) -> MenuView:
    view = MenuView(NodePath("aspect2d"))
    view.show(Menu("TITLE", [MenuItem(f"Item {index}", lambda: None) for index in range(count)]))
    return view


def test_a_short_menu_starts_at_its_usual_height() -> None:
    view = drawn(4)
    assert view.texts[0].getTextPos()[1] == TOP


def test_a_long_menu_goes_up_to_stay_on_the_screen() -> None:
    view = drawn(17)
    assert view.texts[0].getTextPos()[1] > TOP
    bounds = view.panel.getTightBounds()
    assert bounds is not None
    low, high = bounds
    assert low.z >= LOWEST - 1e-6
    assert high.z < 1.0
