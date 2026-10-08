"""The Dev menu's backgrounds browser: background candidates, one theme at a time (pewpy.generators.backgrounds).

The candidate on show scrolls by on the whole screen, as in the game, under a panel saying what it is; Left/Right go
from one theme to the next, Space makes a new candidate of the theme, Escape goes back to the Dev menu.
"""

import random
from enum import Enum
from typing import cast

from pewpy.app.browsers import BrowserScreen
from pewpy.game.states import State
from pewpy.generators.backgrounds.browser import BackgroundBrowser
from pewpy.ui.menu import MenuItem
from pewpy.ui.screenshot_view import BACKGROUND_KEYS, ScreenshotView

BACKGROUNDS = "backgrounds"  # the Dev menu's entry (see DevMenu.browsing)


class Backgrounds(BrowserScreen):
    """The backgrounds browser."""

    BROWSER_STATE = State.BACKGROUND_BROWSER

    def _dev_entries(self) -> list[tuple[str, MenuItem]]:
        return [*super()._dev_entries(), (BACKGROUNDS, MenuItem("Backgrounds", self._browse_backgrounds))]

    def _browse_backgrounds(self) -> None:
        self.browsing = BACKGROUNDS
        self.states.transition(State.BACKGROUND_BROWSER)

    def _on_state_change(self, previous: Enum, current: Enum) -> None:
        if previous is State.BACKGROUND_BROWSER:  # back to the menus: their ground behind them
            self._show_background()
        super()._on_state_change(previous, current)

    # The browser and its view, under the names the rest of the app (and the tests) reach them by.
    @property
    def background_browser(self) -> BackgroundBrowser | None:
        """Return the background browser on show, or None while none is."""
        return cast("BackgroundBrowser | None", self.browser)

    @property
    def background_view(self) -> ScreenshotView | None:
        """Return the view drawing the background browser, or None while none is."""
        return cast("ScreenshotView | None", self.view)

    def _open_browser(self) -> tuple[BackgroundBrowser, ScreenshotView]:
        return BackgroundBrowser(random.Random()), ScreenshotView(self.aspect2d, BACKGROUND_KEYS)

    def _show_browsed(self, browser: BackgroundBrowser, view: ScreenshotView, problem: str = "") -> None:
        """Show the candidate's background scrolling by, and say what it is (or why there is none)."""
        self._show_menu_ground(browser.level())
        view.describe(browser.title(), browser.details(), problem or browser.made["note"])

    def _save_browsed(self, browser: BackgroundBrowser) -> None:
        """Nothing to save: a background is generated and read from `data/` (see BackgroundBrowser)."""
