"""The Dev menu's screenshots: one per world, a moment of a level drawn at random (pewpy.generators.screenshots).

Left/Right go from one world to the next, Space plays one of its levels, drawn at random, to a new moment (in an
instant, nothing drawn in between) and shows it, frozen, with the HUD; Enter saves the game area as the world's
screenshot, without the texts over it; Escape goes back to the Dev menu.
"""

import random
from enum import Enum

from panda3d.core import Filename, PNMImage

from pewpy.app.ai_playing import AIPlaying
from pewpy.app.dev import BROWSER_MOVES, GENERATE_KEY
from pewpy.app.window import letterbox
from pewpy.game.controls import Controls
from pewpy.game.player import SHIPS
from pewpy.game.states import State
from pewpy.generators.screenshots import Shot, game_area, play, random_shot, screenshot_path
from pewpy.ui.menu import MenuItem
from pewpy.ui.screenshot_view import ScreenshotView

SCREENSHOTS = "screenshots"  # the Dev menu's entry (see DevMenu.browsing)


class Screenshots(AIPlaying):
    """The screenshots screen.

    Its own screen rather than a BrowserScreen (see browsers.py): what Space takes is a moment of a level played out
    (see `random_shot`), not a candidate the browser keeps, and Left/Right go from one world to the next.
    """

    screenshot_view: ScreenshotView | None = None
    shot: Shot | None = None  # the one on show
    shot_world = 0  # the world shot (its index)
    shot_level = 0  # the level the shot on show is of (its index)
    shot_rng: random.Random  # set up as the screen opens

    def _dev_entries(self) -> list[tuple[str, MenuItem]]:
        return [*super()._dev_entries(), (SCREENSHOTS, MenuItem("Screenshots", self._browse_screenshots))]

    def _browse_screenshots(self) -> None:
        self.browsing = SCREENSHOTS
        self.states.transition(State.SCREENSHOTS)

    def _on_state_change(self, previous: Enum, current: Enum) -> None:
        if previous is State.SCREENSHOTS:  # back to the menus: no shot, and their ground behind them
            self._drop_shot()
            self._show_background()
        super()._on_state_change(previous, current)
        if current is State.SCREENSHOTS:
            self._open_shot()
        else:
            self._close_shot()  # the texts go down with the screen (nothing to do when it isn't up)

    def _open_shot(self) -> None:
        """Open the screen: the texts, and the world whose levels it shoots (its ground behind them)."""
        self.screenshot_view = ScreenshotView(self.aspect2d)
        self.shot_world = self.places[self.level_index][0]
        self._show_world_ground()
        self.shot_rng = random.Random()
        self._describe_shot(self.screenshot_view, "Space: take a screenshot")

    def _close_shot(self) -> None:
        """Take the texts away. A shot taken stays: `_drop_shot` is what takes that away."""
        if self.screenshot_view is not None:
            self.screenshot_view.destroy()
            self.screenshot_view = None

    def _on_key(self, key: str) -> None:
        super()._on_key(key)
        if self.screenshot_view is None:
            return
        if key == GENERATE_KEY:
            self.audio.play("menu_choose")
            self._take_shot(self.screenshot_view)
        elif key in BROWSER_MOVES:
            view = self.screenshot_view
            self.audio.play("menu_move")
            self.shot_world = (self.shot_world + BROWSER_MOVES[key]) % len(self.worlds)
            self._drop_shot()  # the texts stay: only the shot's level goes
            self._show_world_ground()
            self._show_hud(visible=False)
            self._describe_shot(view, "Space: take a screenshot")

    def _on_choose(self) -> None:
        if self.screenshot_view is None:
            super()._on_choose()
            return
        if self.shot is not None:
            self.audio.play("menu_choose")
            self._save_shot(self.screenshot_view)

    def _on_back(self) -> None:
        if self.screenshot_view is not None:
            self.audio.play("menu_back")
            self.states.transition(State.DEV_MENU)
            return
        super()._on_back()

    def _take_shot(self, view: ScreenshotView) -> None:
        """Play one of the world's levels, drawn at random, to a moment drawn at random, and show it."""
        shot = random_shot(self.shot_rng)
        first = self.places.index((self.shot_world, 1))
        self.shot_level = first + self.shot_rng.randrange(len(self.worlds[self.shot_world].levels))
        level = self.levels[self.shot_level]
        world = self._begin_level(level, arsenal=shot.arsenal(), ship=SHIPS[shot.ship])
        self.shot = shot

        def step(controls: Controls, dt: float) -> None:
            world.update(dt, controls)
            self._show_events(world.events, dt)
            self.effects.set_lasers(self._laser_glows(world), dt)
            self.effects.update(dt)
            self.background.scenery.update(dt, level.scroll_speed)

        play(world, shot, step)
        self._show_hud(visible=True)
        self._sync_nodes()
        self._describe_shot(view, "Enter saves it as the world's screenshot")

    def _save_shot(self, view: ScreenshotView) -> None:
        """Save the game area, as it's drawn, without the texts over it."""
        view.root.hide()
        self.fps_text.hide()
        self.graphicsEngine.renderFrame()
        self.graphicsEngine.renderFrame()  # the 3D view's buffer is drawn in a frame, the window shows it the next
        image = PNMImage()
        self.win.getScreenshot(image)
        view.root.show()
        self.fps_text.show()
        x, y, width, height = game_area(
            image.getXSize(), image.getYSize(), letterbox(self.win.getXSize(), self.win.getYSize())
        )
        area = PNMImage(width, height)
        area.copySubImage(image, 0, 0, x, y, width, height)
        path = screenshot_path(self.shot_world)
        path.parent.mkdir(parents=True, exist_ok=True)
        area.write(Filename.fromOsSpecific(str(path)))
        self._describe_shot(view, f"Saved to {path.parent.name}/{path.name}")

    def _drop_shot(self) -> None:
        """Take the shot's level away, leaving the texts."""
        self.world, self.shot = None, None
        self.effects.clear()

    def _show_world_ground(self) -> None:
        """Show the world's ground behind the texts until a shot is taken: its first level's."""
        self._show_menu_ground(self.levels[self.places.index((self.shot_world, 1))])

    def _describe_shot(self, view: ScreenshotView, status: str) -> None:
        world = self.worlds[self.shot_world]
        title = f"World {self.shot_world + 1}: {world.name}  ({self.shot_world + 1}/{len(self.worlds)})"
        details = ""
        if self.shot is not None:
            level = self.levels[self.shot_level]
            details = f"{self._label(self.shot_level)} {level.name}: {self.shot.describe()}"
        view.describe(title, details, status)
