"""The Dev menu, from the main menu: browsing the player's ships', the enemies' and the bosses' models, the built-in
parts ships are made of, and the songs (pewpy.generators).

Each category opens the model browser: Left/Right go from one model to the next, Z/S make the size new models are
made to taller or shorter and D/Q wider or narrower (its shape), Space makes a new one, Enter saves it in place of the
model, Escape goes back to the Dev menu. Parts opens the Parts menu, one entry for each kind of part; each opens the
parts browser on that kind, in the same view: Left/Right go from one part to the next, Escape goes back to the Parts
menu. Music opens the
music browser: Left/Right go from one song to the next (it plays), Space composes a new one, Enter saves it in place of
the song.
"""  # noqa: D205 - the summary needs two lines

import random
from enum import Enum
from functools import partial

from pewpy import config
from pewpy.app.sound import Sound
from pewpy.audio.cues import Music
from pewpy.game.enemies.kinds import reload_kinds
from pewpy.game.states import State
from pewpy.generators.models.browser import ModelBrowser
from pewpy.generators.models.catalog import CATEGORIES
from pewpy.generators.models.parts_browser import LEAST, PartBrowser, part_drawing
from pewpy.generators.models.ships.parts import KINDS
from pewpy.generators.music.browser import MusicBrowser
from pewpy.generators.music.plans import PLANS
from pewpy.graphics import models
from pewpy.ui.menu import Menu, MenuItem
from pewpy.ui.model_browser_view import PART_KEYS, ModelBrowserView
from pewpy.ui.music_browser_view import MusicBrowserView

BROWSER_MOVES = {"arrow_left": -1, "arrow_right": 1}  # the model on show
# The size new models are made to, its shape: (wider, taller) steps. Z up, S down, Q left, D right (on AZERTY).
SHAPE_KEYS = {"z": (0, 1), "s": (0, -1), "q": (-1, 0), "d": (1, 0)}
GENERATE_KEY = "space"
PARTS = "parts"  # the Dev menu's entry after the model categories
MUSIC = "music"  # the one after it


class DevMenu(Sound):
    """The Dev menu, its model browser and its parts browser."""

    model_browser: ModelBrowser | None = None
    part_browser: PartBrowser | None = None
    browser_view: ModelBrowserView | None = None  # the model browser's, or the parts browser's
    music_browser: MusicBrowser | None = None
    music_view: MusicBrowserView | None = None
    browsing = "players"  # the Dev menu's entry picked last (see `_dev_entries`)
    parts_kind = 0  # the Parts menu's entry picked last: a kind of part (its index in KINDS)

    def _main_menu_items(self) -> list[MenuItem]:
        return [*super()._main_menu_items(), MenuItem("Dev", self._go(State.DEV_MENU))]

    def _menu(self, state: Enum) -> Menu | None:
        if state is State.DEV_MENU:
            entries = self._dev_entries()
            back = MenuItem("Back", self._go(State.MAIN_MENU))
            selected = [key for key, _ in entries].index(self.browsing)
            return Menu("DEV", [*(item for _, item in entries), back], back=back.action, selected=selected)
        if state is State.PARTS_MENU:
            kinds = [MenuItem(title, partial(self._browse_parts, index)) for index, title in enumerate(KINDS.values())]
            back = MenuItem("Back", self._go(State.DEV_MENU))
            return Menu("PARTS", [*kinds, back], back=back.action, selected=self.parts_kind)
        if state in (State.MODEL_BROWSER, State.MUSIC_BROWSER):
            return None
        return super()._menu(state)

    def _dev_entries(self) -> list[tuple[str, MenuItem]]:
        """Return the Dev menu's entries but Back, each with what it browses (see `browsing`)."""
        models = [
            (category, MenuItem(title, partial(self._browse, category))) for category, title in CATEGORIES.items()
        ]
        parts = (PARTS, MenuItem("Parts", self._parts_menu))
        return [*models, parts, (MUSIC, MenuItem("Music", self._browse_music))]

    def _browse(self, category: str) -> None:
        self.browsing = category
        self.states.transition(State.MODEL_BROWSER)

    def _parts_menu(self) -> None:
        self.browsing = PARTS
        self.states.transition(State.PARTS_MENU)

    def _browse_parts(self, kind: int) -> None:
        self.parts_kind = kind
        self.states.transition(State.MODEL_BROWSER)

    def _browse_music(self) -> None:
        self.browsing = MUSIC
        self.states.transition(State.MUSIC_BROWSER)

    def _on_state_change(self, previous: Enum, current: Enum) -> None:
        super()._on_state_change(previous, current)
        if current is State.MODEL_BROWSER and self.browsing == PARTS:
            self.part_browser = PartBrowser(self.parts_kind)
            self.browser_view = ModelBrowserView(self.cam, self.aspect2d, PART_KEYS)
            self._plain_background(plain=True)  # to look at the parts
            self._show_part(self.part_browser, self.browser_view)
        elif current is State.MODEL_BROWSER:
            self.model_browser = ModelBrowser(self.browsing, random.Random())
            self.browser_view = ModelBrowserView(self.cam, self.aspect2d)
            self._plain_background(plain=True)  # to look at the models
            self._show_browser(self.model_browser, self.browser_view)
        elif self.browser_view is not None:
            self.browser_view.destroy()
            self.browser_view = None
            self.model_browser = None
            self.part_browser = None
            self._plain_background(plain=False)
        if current is State.MUSIC_BROWSER:
            self.music_browser = MusicBrowser(random.Random())
            self.music_view = MusicBrowserView(self.aspect2d)
            self._show_music(self.music_browser, self.music_view)
        elif self.music_view is not None:
            self.music_view.destroy()
            self.music_view = None
            self.music_browser = None

    def _on_key(self, key: str) -> None:
        super()._on_key(key)
        if self.music_browser is not None and self.music_view is not None:
            self._on_music_key(self.music_browser, self.music_view, key)
            return
        if self.part_browser is not None and self.browser_view is not None:
            self._on_part_key(self.part_browser, self.browser_view, key)
            return
        browser, view = self.model_browser, self.browser_view
        if browser is None or view is None:
            return
        if key == GENERATE_KEY:  # else an arrow (the keys sent here: see keys.py)
            self._generate_model(browser, view)
            return
        if key not in BROWSER_MOVES:  # Up and Down: nothing to change (the shape keys change the size)
            return
        browser.move(BROWSER_MOVES[key])
        self.audio.play("menu_move")
        self._show_browser(browser, view)

    def _on_part_key(self, browser: PartBrowser, view: ModelBrowserView, key: str) -> None:
        """Go from one part of the kind to the next (Left/Right)."""
        if key not in BROWSER_MOVES:  # Space, Up, Down: nothing to make nor change
            return
        browser.move(BROWSER_MOVES[key])
        self.audio.play("menu_move")
        self._show_part(browser, view)

    def _setup_keys(self) -> None:
        super()._setup_keys()
        for key in SHAPE_KEYS:
            self.accept(key, self._on_shape_key, [key])

    def _on_shape_key(self, key: str) -> None:
        """Make the size new models are made to wider, narrower, taller or shorter: the model's shape."""
        browser, view = self.model_browser, self.browser_view
        if browser is None or view is None:
            return
        browser.stretch(*SHAPE_KEYS[key])
        self.audio.play("menu_move")
        self._show_browser(browser, view)

    def _generate_model(self, browser: ModelBrowser, view: ModelBrowserView) -> None:
        """Make a new model of what's on show; if none can be that size, the view says why instead."""
        self.audio.play("menu_choose")
        try:
            browser.generate()
        except ValueError as error:  # no model could be made that size
            self._show_browser(browser, view, str(error))
            return
        self._show_browser(browser, view)

    def _on_music_key(self, browser: MusicBrowser, view: MusicBrowserView, key: str) -> None:
        if key == GENERATE_KEY:
            self.audio.play("menu_choose")
            new = browser.generate()
            self.audio.library.add(browser.name(), new)
        elif key in BROWSER_MOVES:
            self.audio.play("menu_move")
            browser.move(BROWSER_MOVES[key])
        else:  # Up and Down: nothing to change
            return
        self._show_music(browser, view)

    def _music(self) -> Music:
        if self.music_browser is not None:
            return self.music_browser.music()
        return super()._music()

    def _update_music_view(self) -> None:
        """Say whether the song on show plays (it's rendered first, which takes a few seconds)."""
        browser, view = self.music_browser, self.music_view
        if browser is None or view is None:
            return
        if not self.audio.music_on:
            view.show_playing("Music off: M turns it on")
        elif self.audio.playing == browser.music():
            view.show_playing("Playing")
        else:
            view.show_playing("Rendering...")

    def _on_choose(self) -> None:
        if self.music_browser is not None and self.music_view is not None:
            self.audio.play("menu_choose")
            self.music_browser.save()
            self.audio.forget_song(self.music_browser.plan.name)  # the game plays the new song
            self._show_music(self.music_browser, self.music_view)
            return
        if self.part_browser is not None:  # nothing to save
            return
        browser, view = self.model_browser, self.browser_view
        if browser is None or view is None:
            super()._on_choose()
            return
        self.audio.play("menu_choose")
        browser.save()
        reload_kinds()  # the game plays the new models
        self._build_models()
        self._show_browser(browser, view)

    def _on_back(self) -> None:
        if self.music_browser is not None:
            self.audio.play("menu_back")
            self.states.transition(State.DEV_MENU)
            return
        if self.model_browser is None and self.part_browser is None:
            super()._on_back()
            return
        self.audio.play("menu_back")
        self.states.transition(State.PARTS_MENU if self.part_browser is not None else State.DEV_MENU)

    def _show_browser(self, browser: ModelBrowser, view: ModelBrowserView, problem: str = "") -> None:
        """Show the browser's model and what it is."""
        pieces = [
            (models.drawn_model(piece.name, piece.data, piece.name), piece.x, piece.y) for piece in browser.pieces()
        ]
        view.show(pieces, browser.size)
        entry = browser.entry
        title = f"{entry.title}  ({browser.index + 1}/{len(browser.models)})"
        view.describe(title, entry.description, _size_info(browser), problem or _status(browser))

    def _show_part(self, browser: PartBrowser, view: ModelBrowserView) -> None:
        """Show the part on show and what it is."""
        part = browser.part
        view.show([(models.drawn_model(part.name, part_drawing(part), part.name), 0.0, 0.0)], browser.size(), LEAST)
        view.describe(browser.title(), browser.details(), browser.info(), "")

    def _show_music(self, browser: MusicBrowser, view: MusicBrowserView) -> None:
        """Show the song on show and what it is."""
        title = f"{browser.plan.name}  ({browser.index + 1}/{len(PLANS)})"
        view.describe(title, browser.details(), _music_status(browser))
        self._update_music_view()


def _music_status(browser: MusicBrowser) -> str:
    if browser.saved:
        return "Saved"
    if browser.new is not None:
        return "New song: Enter saves it in place of this one"
    return ""


def _size_info(browser: ModelBrowser) -> str:
    """Describe the size new models are made to, and the model's own, in cubes."""
    width, height = browser.size
    core = browser.pieces()[0].data
    rows = core["layers"][0] if "layers" in core else core["rows"]
    cube = config.MODEL_VOXEL
    return (
        f"Size {width:.3f} x {height:.3f} ({width / cube:.0f} x {height / cube:.0f} cubes)"
        f"   Model {len(rows[0])} x {len(rows)} cubes"
    )


def _status(browser: ModelBrowser) -> str:
    if browser.saved:
        return "Saved"
    if browser.new is not None:
        return "New model: Enter saves it in place of this one"
    return ""
