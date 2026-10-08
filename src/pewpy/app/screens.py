"""The screens and their menus: main menu, ship, world and level select, pause, game over, level complete.

Also starting levels and going from one to the next.
"""

import random
from collections.abc import Callable
from enum import Enum
from functools import partial

from pewpy import config
from pewpy.app.drawing import Drawing
from pewpy.app.entity_models import fitted_model
from pewpy.app.window import BACKGROUND_COLOR
from pewpy.game.level import Level, LevelWorld
from pewpy.game.player import SHIPS, ShipSpec
from pewpy.game.states import State, StateMachine
from pewpy.game.weapons.player.arsenal import Arsenal
from pewpy.game.world import View, World
from pewpy.scenery.background import Scenery
from pewpy.scenery.background.view import BackgroundView, CameraView, sky_color
from pewpy.ui.level_preview import LevelPreview
from pewpy.ui.menu import Menu, MenuItem
from pewpy.ui.menu_view import MenuView
from pewpy.ui.ship_select_view import ShipSelectView


class Screens(Drawing):
    """The screens, one per state of the game (see pewpy.game.states), and the levels they start."""

    # Set up by PewPewApp.__init__.
    states: StateMachine
    worlds: list[LevelWorld]
    levels: list[Level]  # in playing order
    places: list[tuple[int, int]]  # for each level: (its world's index, its number in the world, from 1)
    level_index: int
    world_index: int  # the world picked in the world select
    ship_key: str  # the player's ship (picked on the ship selection screen)
    ship_select: ShipSelectView | None
    camera_view: CameraView
    menu_view: MenuView
    level_preview: LevelPreview  # the level select's window on the highlighted level
    menu_level: Level | None  # the level whose ground scrolls behind the menus (None: a level is played)
    menu_rng: random.Random  # draws it

    def _go(self, target: Enum) -> Callable[[], None]:
        return lambda: self.states.transition(target)

    def _main_menu_items(self) -> list[MenuItem]:
        """Return the main menu's items, but "Quit" (the last one)."""
        return [MenuItem("Start", self._go(State.SHIP_SELECT))]

    def _menu(self, state: Enum) -> Menu | None:
        """Return the menu shown in each state (None while playing)."""
        go = self._go
        main_menu = MenuItem("Main menu", go(State.MAIN_MENU))
        menus: dict[Enum, Callable[[], Menu]] = {
            State.MAIN_MENU: lambda: Menu("PEWPEW", [*self._main_menu_items(), MenuItem("Quit", self.userExit)]),
            State.SHIP_SELECT: self._ship_menu,
            State.WORLD_SELECT: self._world_menu,
            State.LEVEL_SELECT: self._level_menu,
            State.PAUSED: lambda: Menu(
                "PAUSED", [MenuItem("Resume", go(State.PLAYING)), main_menu], back=go(State.PLAYING)
            ),
            State.GAME_OVER: lambda: Menu(
                "GAME OVER", [MenuItem("Continue", self._continue), main_menu], back=go(State.MAIN_MENU)
            ),
            State.LEVEL_COMPLETE: lambda: self._level_complete_menu(main_menu),
        }
        make = menus.get(state)
        return make() if make is not None else None

    def _level_complete_menu(self, main_menu: MenuItem) -> Menu:
        if self._is_last_level():
            return Menu("ALL LEVELS COMPLETE\nYOU WIN!", [main_menu], back=main_menu.action)
        world, number = self.places[self.level_index]
        if number == len(self.worlds[world].levels):  # the world's last level
            title, next_item = f"WORLD COMPLETE\n{self.worlds[world].name}", "Next world"
        else:
            title, next_item = "LEVEL COMPLETE", "Next level"
        return Menu(title, [MenuItem(next_item, self._next_level), main_menu], back=main_menu.action)

    def _ship_menu(self) -> Menu:
        def pick(key: str) -> None:
            self.ship_key = key
            self.states.transition(State.WORLD_SELECT)

        items = [MenuItem(spec.name.title(), partial(pick, key)) for key, spec in SHIPS.items()]
        back = MenuItem("Back", self._leave_ship_select)
        # Starts on the ship played last.
        return Menu("SELECT SHIP", [*items, back], back=back.action, selected=list(SHIPS).index(self.ship_key))

    def _leave_ship_select(self) -> None:
        """Go back from the ship select: to the main menu."""
        self.states.transition(State.MAIN_MENU)

    def _show_ship_select(self) -> None:
        """Every ship side by side under the menu, with bars comparing them."""
        ships = list(SHIPS.values())
        fitted = [fitted_model(self.player_models[ship.drawing], ship.size) for ship in ships]
        lens = self.cam.node().getLens()
        extent = (self.a2dRight, self.a2dTop)
        self.ship_select = ShipSelectView(ships, fitted, self.cam, lens, self.aspect2d, extent)
        self._highlight_ship()

    def _on_highlight(self, menu: Menu) -> None:
        """Show what the item just highlighted is about: its ship, or its level's background."""
        self._highlight_ship()
        if self.states.state is State.LEVEL_SELECT:
            self._preview_level(menu)

    def _highlight_ship(self) -> None:
        menu = self.menu_view.menu
        if self.ship_select is not None and menu is not None:
            self.ship_select.select(menu.selected)  # past the ships: "Back", nothing highlighted

    def _world_menu(self) -> Menu:
        def pick(index: int) -> None:
            self.world_index = index
            self.states.transition(State.LEVEL_SELECT)

        items = [
            MenuItem(f"{index + 1}. {world.name}", partial(pick, index)) for index, world in enumerate(self.worlds)
        ]
        back = MenuItem("Back", lambda: self.states.transition(State.SHIP_SELECT))
        # Starts on the world of the last level played.
        return Menu("SELECT WORLD", [*items, back], back=back.action, selected=self.places[self.level_index][0])

    def _level_menu(self) -> Menu:
        world = self.worlds[self.world_index]
        first = self.places.index((self.world_index, 1))  # index of the world's first level among all levels
        items = [
            MenuItem(f"{self._label(first + offset)} {level.name}", partial(self._start_level, first + offset))
            for offset, level in enumerate(world.levels)
        ]
        back = MenuItem("Back", lambda: self.states.transition(State.WORLD_SELECT))
        # Starts on the last level played if it's in this world, so "play again" is just Enter.
        played = self.level_index - first if self.places[self.level_index][0] == self.world_index else 0
        return Menu(world.name.upper(), [*items, back], back=back.action, selected=played)

    def _preview_level(self, menu: Menu) -> None:
        """On the level select: the highlighted level's background in the preview window (none on "Back")."""
        world = self.worlds[self.world_index]
        if menu.selected >= len(world.levels):
            self.level_preview.hide()
            return
        index = self.places.index((self.world_index, 1)) + menu.selected
        self.level_preview.show(index, self.levels[index])

    def _label(self, index: int) -> str:
        """Return a level's place, like "2-5" (world 2, level 5)."""
        world, number = self.places[index]
        return f"{world + 1}-{number}"

    def _start_level(
        self, index: int, score: int = 0, lives: int = config.PLAYER_LIVES, arsenal: Arsenal | None = None
    ) -> None:
        self.level_index = index
        self._begin_level(
            self.levels[index], score=score, lives=lives, arsenal=arsenal, ship=SHIPS[self.ship_key], cutscenes=True
        )
        self.states.transition(State.PLAYING)

    def _begin_level(
        self,
        level: Level,
        score: int = 0,
        lives: int = config.PLAYER_LIVES,
        arsenal: Arsenal | None = None,
        ship: ShipSpec | None = None,
        cutscenes: bool = False,
    ) -> World:
        """Build the world for `level` and show its scenery, ready to be played (by the player or the AI)."""
        self.world = World(
            level,
            score=score,
            lives=lives,
            arsenal=arsenal,
            ship=ship,
            view=View.of(self.camera_view.area(0.0)),  # where the screen ends, on the play plane
            cutscenes=cutscenes,
        )
        self._show_background(level)
        self._prepare_level(level)
        self.effects.clear()
        return self.world

    def _show_background(self, level: Level | None = None) -> None:
        """Show a level's scenery; without one, the menus': a level's ground drawn at random, scrolling by."""
        if level is None:
            self._show_menu_ground(self.menu_rng.choice(self.levels))
            return
        self._show_scenery(level)
        self.menu_level = None

    def _show_menu_ground(self, level: Level) -> None:
        """Show a level's ground behind the menus, scrolling by."""
        self._show_scenery(level)
        self.menu_level = level

    def _show_scenery(self, level: Level) -> None:
        self.background.destroy()
        scenery = Scenery(level.scenery_params(), self.camera_view, seed=level.background_seed, clouds=level.clouds)
        self.background = BackgroundView(scenery, self.render, level.time_of_day)
        # The sky shows through gaps, like between clouds.
        self.sky = sky_color(scenery.params, level.time_of_day)
        self.camNode.getDisplayRegion(0).setClearColor(self.sky)

    def _plain_background(self, plain: bool) -> None:
        """Hide the scenery behind a plain dark background (to look at models), or show it again."""
        if plain:
            self.background.root.hide()
            self.camNode.getDisplayRegion(0).setClearColor(BACKGROUND_COLOR)
        else:
            self.background.root.show()
            self.camNode.getDisplayRegion(0).setClearColor(self.sky)

    def _continue(self) -> None:
        # Continue restarts the level with full lives, a score of 0 and weapons back to level 1.
        self._start_level(self.level_index)

    def _next_level(self) -> None:
        if self.world is None or self._is_last_level():
            self.states.transition(State.MAIN_MENU)
            return
        world = self.world
        self._start_level(self.level_index + 1, score=world.score, lives=world.lives, arsenal=world.arsenal)

    def _is_last_level(self) -> bool:
        return self.level_index >= len(self.levels) - 1

    def _on_state_change(self, previous: Enum, current: Enum) -> None:  # noqa: ARG002 - the layers above use it
        menu = self._menu(current)
        self.menu_view.show(menu)
        if self.ship_select is not None:
            self.ship_select.destroy()
            self.ship_select = None
        if current is State.SHIP_SELECT:
            self._show_ship_select()
        if current is State.LEVEL_SELECT and menu is not None:
            self._preview_level(menu)
        else:
            self.level_preview.clear()
        if current is State.MAIN_MENU:
            self.world = None
            self.effects.clear()
            if self.menu_level is None:
                self._show_background()
        self._show_hud(self.world is not None)
