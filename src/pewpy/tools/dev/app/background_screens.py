"""The Background candidates screen: the candidates listed page by page, the highlighted one scrolling in a window.

Like the level select: the list on the left, the highlighted candidate's background scrolling in the preview window
(pewpy.ui.level_preview). Choosing one shows it on the whole screen, scrolling, without the menu; Escape goes back to
the list. "Reload" reads the files again (after `make backgrounds`, or an edit).
"""

import math
from enum import Enum
from functools import partial

from direct.task.Task import Task

from pewpy.game.states import State
from pewpy.tools.dev import candidates
from pewpy.tools.dev.app.model_screens import ModelScreens
from pewpy.tools.dev.states import DevState
from pewpy.ui.menu import Menu, MenuItem

BACKGROUNDS_PER_PAGE = 6  # with the pages, Reload and Back: as many items as fit under the title


class BackgroundScreens(ModelScreens):
    """The screen showing the background candidates."""

    background_page = 0  # the page of the list shown
    background_full: str | None = None  # the candidate shown on the whole screen, if any

    def _background_names(self) -> list[str]:
        """Return the candidates on the page shown."""
        start = self.background_page * BACKGROUNDS_PER_PAGE
        return candidates.background_candidate_names()[start : start + BACKGROUNDS_PER_PAGE]

    def _background_menu(self, selected: int = 0) -> Menu:
        """Make the screen's menu: the page's candidates (by name), its pages, Reload and Back."""
        count = len(candidates.background_candidate_names())
        pages = max(1, math.ceil(count / BACKGROUNDS_PER_PAGE))
        items = []
        for name in self._background_names():
            level, _ = candidates.background_candidate(name)
            items.append(MenuItem(level.name, partial(self._show_background_full, name)))  # short: clear of the window
        if pages > 1:
            items.append(MenuItem("Next page", partial(self._turn_background_page, 1)))
        if pages > 2:
            items.append(MenuItem("Previous page", partial(self._turn_background_page, -1)))
        items.append(MenuItem("Reload", self._reload_backgrounds))
        back = MenuItem("Back", lambda: self.states.transition(State.MAIN_MENU))
        items.append(back)
        title = f"BACKGROUND CANDIDATES ({self.background_page + 1}/{pages})\n{count} candidates"
        return Menu(title, items, back=back.action, selected=selected)

    def _turn_background_page(self, step: int) -> None:
        pages = max(1, math.ceil(len(candidates.background_candidate_names()) / BACKGROUNDS_PER_PAGE))
        self.background_page = (self.background_page + step) % pages
        self._show_background_list()

    def _reload_backgrounds(self) -> None:
        """Read the candidates again: the previews are built anew."""
        self.level_preview.clear()
        count = len(candidates.background_candidate_names())
        self.background_page = min(self.background_page, max(0, math.ceil(count / BACKGROUNDS_PER_PAGE) - 1))
        self._show_background_list(selected=len(self._background_names()))  # on "Reload" (past the page's names)

    def _show_background_list(self, selected: int = 0) -> None:
        """Show the list (back from the whole screen too: space behind it), the highlighted candidate previewed."""
        if self.background_full is not None:
            self.background_full = None
            self._show_background()
        menu = self._background_menu(selected)
        self.menu_view.show(menu)
        self._preview_background(menu)

    def _preview_background(self, menu: Menu) -> None:
        """Preview the highlighted candidate in the window (none past the page's names)."""
        names = self._background_names()
        if menu.selected >= len(names):
            self.level_preview.hide()
            return
        level, note = candidates.background_candidate(names[menu.selected])
        self.level_preview.show(self.background_page * BACKGROUNDS_PER_PAGE + menu.selected, level)
        # The title's second line: what the highlighted one is.
        menu.title = f"{menu.title.split(chr(10))[0]}\n#{names[menu.selected]}, {note}, {level.time_of_day}"
        if self.menu_view.menu is menu and self.menu_view.texts:
            self.menu_view.texts[0].setText(menu.title)

    def _show_background_full(self, name: str) -> None:
        """Show a candidate on the whole screen, scrolling, without the menu (Escape: back to the list)."""
        level, _ = candidates.background_candidate(name)
        self.level_preview.hide()
        self.menu_view.show(None)
        self._show_background(level)
        self.background_full = name

    def _on_highlight(self, menu: Menu) -> None:
        super()._on_highlight(menu)
        if self.states.state is DevState.BACKGROUND_CANDIDATES:
            self._preview_background(menu)

    def _menu(self, state: Enum) -> Menu | None:
        if state is DevState.BACKGROUND_CANDIDATES:
            return self._background_menu()
        return super()._menu(state)

    def _on_state_change(self, previous: Enum, current: Enum) -> None:
        if current is DevState.BACKGROUND_CANDIDATES:
            self.background_page = 0  # before the menu is made
        if previous is DevState.BACKGROUND_CANDIDATES and self.background_full is not None:
            self.background_full = None
            self._show_background()  # space behind the menus again
        super()._on_state_change(previous, current)
        if current is DevState.BACKGROUND_CANDIDATES and self.menu_view.menu is not None:
            self._preview_background(self.menu_view.menu)

    def _on_back(self) -> None:
        if self.background_full is not None and self.states.state is DevState.BACKGROUND_CANDIDATES:
            self.audio.play("menu_back")
            names = self._background_names()
            self._show_background_list(
                selected=names.index(self.background_full) if self.background_full in names else 0
            )
            return
        super()._on_back()

    def _update(self, task: Task) -> int:
        if self.background_full is not None:
            self.background.scenery.update(self._frame_time(), candidates.BACKGROUND_SCROLL_SPEED)
        return super()._update(task)
