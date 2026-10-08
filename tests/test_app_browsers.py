"""The shared part of the Dev menu's browser screens (app/browsers.py), driven like a player does."""

from typing import Any, NoReturn

import pytest

from pewpy.app import PewPewApp, keys
from pewpy.app.browsers import BrowserScreen
from pewpy.app.dev import GENERATE_KEY
from pewpy.game.states import State

NO_SUCH_BACKGROUND = "nothing that size"  # what a browser says when it can't make what was asked for


class Bare(BrowserScreen):
    """A browser screen that says nothing about what it browses: its hooks are the ones to learn."""

    BROWSER_STATE = State.MODEL_BROWSER


def bare() -> Bare:
    """Return a browser screen with nothing set up: only its hooks, which need nothing of their own."""
    return object.__new__(Bare)


def boom() -> NoReturn:
    raise ValueError(NO_SUCH_BACKGROUND)


def choose(app: PewPewApp, label: str) -> None:
    """Choose an item of the menu on show, by its label."""
    assert app.menu_view.menu is not None
    app.menu_view.menu.selected = [item.label for item in app.menu_view.menu.items].index(label)
    app.messenger.send(keys.MENU_CHOOSE_KEY)


def open_backgrounds(app: PewPewApp) -> None:
    """Open the backgrounds browser, like a player does from the main menu."""
    choose(app, "Dev")
    choose(app, "Backgrounds")


def test_a_browser_screen_leaves_opening_showing_and_saving_to_its_screen() -> None:
    screen = bare()
    nothing: Any = None  # the hooks are never reached: they are only here to be overridden
    with pytest.raises(NotImplementedError):
        screen._open_browser()
    with pytest.raises(NotImplementedError):
        screen._show_browsed(nothing, nothing)
    with pytest.raises(NotImplementedError):
        screen._save_browsed(nothing)


def test_leaving_the_browsers_screen_takes_its_browser_and_view_away(app: PewPewApp) -> None:
    open_backgrounds(app)
    assert app.background_browser is not None
    assert app.background_view is not None
    app.messenger.send(keys.BACK_KEY)
    assert app.states.state is State.DEV_MENU
    assert app.background_browser is None
    assert app.background_view is None


def test_the_keys_drive_no_browser_from_another_screen(app: PewPewApp) -> None:
    open_backgrounds(app)
    app.messenger.send(keys.BACK_KEY)  # the browser is closed, so these are the Dev menu's keys
    assert app.background_browser is None
    app.messenger.send(GENERATE_KEY)
    assert app.states.state is State.DEV_MENU


def test_a_candidate_that_cannot_be_made_says_why(app: PewPewApp, monkeypatch: pytest.MonkeyPatch) -> None:
    open_backgrounds(app)
    view = app.background_view
    assert view is not None
    monkeypatch.setattr(app.background_browser, "generate", boom)
    app.messenger.send(GENERATE_KEY)
    assert view.status.getText() == NO_SUCH_BACKGROUND
    app.messenger.send("arrow_up")  # not a move over the candidates: the status stays
    assert view.status.getText() == NO_SUCH_BACKGROUND


def test_a_browser_screen_shows_no_menu_while_its_browser_is_on_show(app: PewPewApp) -> None:
    open_backgrounds(app)
    assert app.menu_view.menu is None  # the view is the screen then
