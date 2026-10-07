"""The Dev menu's backgrounds browser: background candidates, one theme at a time (pewpy.generators.backgrounds).

The candidate on show scrolls by on the whole screen, as in the game, under a panel saying what it is; Left/Right go
from one theme to the next, Space makes a new candidate of the theme, Escape goes back to the Dev menu.
"""

import random
from enum import Enum

from pewpy.app.dev import BROWSER_MOVES, GENERATE_KEY, DevMenu
from pewpy.game.states import State
from pewpy.generators.backgrounds.browser import BackgroundBrowser
from pewpy.ui.menu import Menu, MenuItem
from pewpy.ui.screenshot_view import BACKGROUND_KEYS, ScreenshotView

BACKGROUNDS = "backgrounds"  # the Dev menu's entry (see DevMenu.browsing)


class Backgrounds(DevMenu):
    """The backgrounds browser."""

    background_browser: BackgroundBrowser | None = None
    background_view: ScreenshotView | None = None

    def _dev_entries(self) -> list[tuple[str, MenuItem]]:
        return [*super()._dev_entries(), (BACKGROUNDS, MenuItem("Backgrounds", self._browse_backgrounds))]

    def _browse_backgrounds(self) -> None:
        self.browsing = BACKGROUNDS
        self.states.transition(State.BACKGROUND_BROWSER)

    def _menu(self, state: Enum) -> Menu | None:
        if state is State.BACKGROUND_BROWSER:
            return None
        return super()._menu(state)

    def _on_state_change(self, previous: Enum, current: Enum) -> None:
        if previous is State.BACKGROUND_BROWSER:  # back to the menus: their ground behind them
            self._show_background()
        super()._on_state_change(previous, current)
        if current is State.BACKGROUND_BROWSER:
            self.background_browser = BackgroundBrowser(random.Random())
            self.background_view = ScreenshotView(self.aspect2d, BACKGROUND_KEYS)
            self._show_candidate(self.background_browser, self.background_view)
        elif self.background_view is not None:
            self.background_view.destroy()
            self.background_view = None
            self.background_browser = None

    def _on_key(self, key: str) -> None:
        super()._on_key(key)
        browser, view = self.background_browser, self.background_view
        if browser is None or view is None:
            return
        if key == GENERATE_KEY:
            self.audio.play("menu_choose")
            browser.generate()
        elif key in BROWSER_MOVES:
            self.audio.play("menu_move")
            browser.move(BROWSER_MOVES[key])
        else:
            return
        self._show_candidate(browser, view)

    def _on_back(self) -> None:
        if self.background_view is not None:
            self.audio.play("menu_back")
            self.states.transition(State.DEV_MENU)
            return
        super()._on_back()

    def _show_candidate(self, browser: BackgroundBrowser, view: ScreenshotView) -> None:
        """Show the candidate's background scrolling by, and say what it is."""
        self._show_menu_ground(browser.level())
        view.describe(browser.title(), browser.details(), browser.made["note"])
