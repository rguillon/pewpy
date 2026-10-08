"""The shared part of the Dev menu's browser screens: a generated thing on show, moved along with the arrow keys.

A browser screen opens a browser and a view in a state of its own, Space makes a new one of what's on show, Left/Right
go from one to the next, Enter saves it, and going back to the menus closes the view. `BrowserScreen` holds that shared
part; a screen says which state opens its browser (`BROWSER_STATE`) and how it opens, shows and saves one
(`_open_browser`, `_show_browsed`, `_save_browsed`).

The hooks only act in `BROWSER_STATE`, so a screen built on one (see screenshots.py, which goes on to add a state of
its own) keeps its own behaviour everywhere else.
"""

from enum import Enum
from typing import Protocol, TypeVar

from pewpy.app.dev import BROWSER_MOVES, GENERATE_KEY, DevMenu
from pewpy.game.states import State
from pewpy.ui.menu import Menu


class Browsed(Protocol):
    """What a browser browses: things it moves along and makes new ones of."""

    def move(self, step: int) -> None:
        """Go `step` things along (Left and Right)."""

    def generate(self) -> None:
        """Make a new one of what's on show (it becomes the one on show)."""


class Drawn(Protocol):
    """The view drawing a browser: its nodes, which `destroy` takes away."""

    def destroy(self) -> None:
        """Remove the view's nodes."""


BrowserT = TypeVar("BrowserT", bound=Browsed)
ViewT = TypeVar("ViewT", bound=Drawn)


class BrowserScreen(DevMenu):
    """One browser open on a screen of its own.

    A screen subclasses this instead of DevMenu and says:

    - `BROWSER_STATE`: the state its browser opens in (no menu is shown then).
    - `browser`: the browser on show, and `view`: the view drawing it (None while none is). A screen that reaches them
      under its own names overrides the two properties.
    - `_open_browser`: make the browser and its view.
    - `_show_browsed`: draw the browser and what it is, with an optional `problem` in place of the status.
    - `_save_browsed`: what Enter does to what's on show.
    """

    BROWSER_STATE: Enum  # the state this browser opens in

    _browser: Browsed | None = None  # the one on show
    _view: Drawn | None = None  # the view drawing it

    @property
    def browser(self) -> Browsed | None:
        """Return the browser on show, or None while none is."""
        return self._browser

    @property
    def view(self) -> Drawn | None:
        """Return the view drawing the browser on show, or None while none is."""
        return self._view

    def _on_show(self) -> tuple[Browsed, Drawn] | None:
        """Return the browser and its view when they are the one on show: its screen is the current one."""
        browser, view = self._browser, self._view
        if browser is None or view is None or self.states.state is not self.BROWSER_STATE:
            return None
        return browser, view

    def _menu(self, state: Enum) -> Menu | None:
        """Return no menu while the browser is on show; the browser's view is the screen then."""
        if state is self.BROWSER_STATE:
            return None
        return super()._menu(state)

    def _on_state_change(self, previous: Enum, current: Enum) -> None:
        if previous is self.BROWSER_STATE:  # leaving it (for the menus or another screen): close the browser
            self._close_browser()
        super()._on_state_change(previous, current)
        if current is self.BROWSER_STATE:
            self._browser, self._view = self._open_browser()
            self._show_browsed(self._browser, self._view)

    def _on_key(self, key: str) -> None:
        super()._on_key(key)
        showing = self._on_show()
        if showing is None:
            return
        browser, view = showing
        if key == GENERATE_KEY:
            self.audio.play("menu_choose")
            try:
                browser.generate()
            except ValueError as problem:  # nothing could be made that size
                self._show_browsed(browser, view, str(problem))
                return
        elif key in BROWSER_MOVES:
            self.audio.play("menu_move")
            browser.move(BROWSER_MOVES[key])
        else:
            return  # Up and Down: nothing to change
        self._show_browsed(browser, view)

    def _on_choose(self) -> None:
        showing = self._on_show()
        if showing is None:
            super()._on_choose()
            return
        browser, view = showing
        self.audio.play("menu_choose")
        self._save_browsed(browser)
        self._show_browsed(browser, view)

    def _on_back(self) -> None:
        if self._on_show() is None:
            super()._on_back()
            return
        self.audio.play("menu_back")
        self.states.transition(State.DEV_MENU)

    def _close_browser(self) -> None:
        """Take the browser and its view away."""
        if self._view is not None:
            self._view.destroy()
        self._browser, self._view = None, None

    def _open_browser(self) -> tuple[BrowserT, ViewT]:
        raise NotImplementedError

    def _show_browsed(self, browser: BrowserT, view: ViewT, problem: str = "") -> None:
        """Draw the browser and what it is, with `problem` in place of its status when there is one."""
        raise NotImplementedError

    def _save_browsed(self, browser: BrowserT) -> None:
        raise NotImplementedError


__all__ = ["BROWSER_MOVES", "GENERATE_KEY", "Browsed", "BrowserScreen", "Drawn", "State"]
