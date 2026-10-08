"""The Dev menu's parts browser: the catalog's parts, one at a time (pewpy.generators.models.parts).

Left and Right go from one part to the next, Z/S make the size new parts are made to bigger or smaller, Space makes a
new one of the kind on show, Escape goes back to the Dev menu. Nothing is saved: a part is made again from its name
and size.
"""

import random
from typing import cast

from panda3d.core import NodePath

from pewpy.app.ai_playing import AIPlaying
from pewpy.game.states import State
from pewpy.generators.models.common.drawing import layered_drawing
from pewpy.generators.models.common.palette import HULL_TINTS, PART_GREYS, Colors, palette
from pewpy.generators.models.parts.browser import PartBrowser
from pewpy.graphics.models.drawn import drawn_model
from pewpy.ui.menu import MenuItem
from pewpy.ui.part_browser_view import PartBrowserView

PARTS = "parts"  # the Dev menu's entry (see DevMenu.browsing)


class Parts(AIPlaying):
    """The parts browser."""

    BROWSER_STATE = State.PART_BROWSER

    def _dev_entries(self) -> list[tuple[str, MenuItem]]:
        return [*super()._dev_entries(), (PARTS, MenuItem("Parts", self._browse_parts))]

    def _browse_parts(self) -> None:
        self.browsing = PARTS
        self.states.transition(State.PART_BROWSER)

    # The browser and its view, under the names the rest of the app (and the tests) reach them by.
    @property
    def part_browser(self) -> PartBrowser | None:
        """Return the parts browser on show, or None while none is."""
        return cast("PartBrowser | None", self.browser)

    @property
    def part_view(self) -> PartBrowserView | None:
        """Return the view drawing the parts browser, or None while none is."""
        return cast("PartBrowserView | None", self.view)

    # The hooks are only called with this BROWSER_STATE active (see browsers.BrowserScreen._on_show), so the types
    # are always right at runtime; the override is safe despite the different signatures.
    def _open_browser(self) -> tuple[PartBrowser, PartBrowserView]:  # ty: ignore[invalid-method-override]
        return PartBrowser(random.Random()), PartBrowserView(self.cam, self.aspect2d)

    def _show_browsed(self, browser: PartBrowser, view: PartBrowserView, problem: str = "") -> None:  # ty: ignore[invalid-method-override]
        """Show the part on show and what it is."""
        self._plain_background(plain=True)  # to look at the parts
        part = browser.part()
        colors = palette(PART_GREYS, _plain_colors())
        drawing = layered_drawing(part.cells, part.span(), part.length(), colors)
        model = _drawing_model(browser.name, drawing)
        view.show(model, browser.size)
        view.describe(browser.title(), browser.details(), problem or _status())

    def _save_browsed(self, browser: PartBrowser) -> None:  # ty: ignore[invalid-method-override]
        """Nothing to save: a part is made from its name and size."""


def _plain_colors() -> Colors:
    """Return plain colors for the parts browser: no tint, no accent."""
    return Colors(HULL_TINTS["grey"], "red", (1.0, 1.0, 1.0))


def _drawing_model(name: str, drawing: dict) -> NodePath:
    """Build a model from a drawing dict."""
    return drawn_model(name, drawing, "part")


def _status() -> str:
    return ""
