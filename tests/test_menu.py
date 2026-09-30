import pytest

from pewpy.menu import Menu, MenuItem


def make_menu(chosen: list[str], back: bool = True, selected: int = 0) -> Menu:
    items = [MenuItem(label, lambda label=label: chosen.append(label)) for label in ("Start", "Levels", "Quit")]
    return Menu("TITLE", items, back=(lambda: chosen.append("back")) if back else None, selected=selected)


def test_up_and_down_move_the_highlight_and_wrap_around():
    menu = make_menu([])
    menu.move(1)
    assert menu.selected == 1
    menu.move(1)
    menu.move(1)
    assert menu.selected == 0  # past the last item: back to the first
    menu.move(-1)
    assert menu.selected == 2  # before the first item: the last


def test_enter_runs_the_highlighted_item():
    chosen: list[str] = []
    menu = make_menu(chosen)
    menu.move(1)
    menu.choose()
    assert chosen == ["Levels"]


def test_escape_goes_back_if_the_menu_can():
    chosen: list[str] = []
    make_menu(chosen).go_back()
    make_menu(chosen, back=False).go_back()
    assert chosen == ["back"]


def test_a_menu_can_start_on_any_item():
    assert make_menu([], selected=2).selected == 2
    assert make_menu([], selected=4).selected == 1  # wraps, e.g. a level index past the end


def test_a_menu_needs_items():
    with pytest.raises(ValueError, match="at least one item"):
        Menu("EMPTY", [])
