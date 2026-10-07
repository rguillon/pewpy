"""The AI playing screen, from the Dev menu: the AI plays the game from the ship and level picked (pewpy.ai).

The ship, world and level menus pick what it plays (titled "AI PLAYING"; Back from the ship select goes back to the
Dev menu); it plays by the game's rules, going on to
the next level once one is cleared, and a new game from the level picked at game over. Escape goes back to the level
select. Nothing is learned or saved: the AI learns with the dev tools (`make learn`).
"""

from dataclasses import dataclass
from enum import Enum

import numpy as np

from pewpy import config
from pewpy.ai import files
from pewpy.ai.brain import Brain
from pewpy.ai.pilot import Pilot
from pewpy.app.backgrounds import Backgrounds
from pewpy.game.player import SHIPS
from pewpy.game.states import State
from pewpy.game.weapons.player.arsenal import Arsenal
from pewpy.game.world import World
from pewpy.ui.ai_panel import AIPanel, playing_text
from pewpy.ui.menu import Menu, MenuItem

AI = "ai"  # the Dev menu's entry (see DevMenu.browsing)
PICKING = frozenset({State.SHIP_SELECT, State.WORLD_SELECT, State.LEVEL_SELECT})  # the menus picking what to play


@dataclass
class AIGame:
    """The AI's games from the ship and level picked, one after the other.

    Each game starts on the level picked and goes on to the next levels until game over.
    """

    ship: str  # one of SHIPS
    start: int  # the level each game starts on (its index)
    generation: int | None = None  # the saved brain's (None: no brain yet, a new one plays)
    games: int = 0  # the games started
    cleared: int = 0  # the games that cleared the level they started on
    best: int = 0  # the most levels cleared in a game


class AIPlaying(Backgrounds):
    """The AI playing screen."""

    ai_picking = False  # the ship, world and level menus pick what the AI plays, not what the player plays
    ai_panel: AIPanel  # set up by PewPewApp.__init__
    # Set up as the AI starts playing.
    ai_game: AIGame
    pilot: Pilot  # the AI flying the ship
    ai_watching: str  # what the AI plays

    def _dev_entries(self) -> list[tuple[str, MenuItem]]:
        return [*super()._dev_entries(), (AI, MenuItem("AI playing", self._pick_for_ai))]

    def _menu(self, state: Enum) -> Menu | None:
        menu = super()._menu(state)
        if menu is not None and self.ai_picking and state in PICKING:
            menu.title = f"AI PLAYING\n{menu.title}"
        return menu

    def _pick_for_ai(self) -> None:
        """Pick the ship, world and level the AI plays, with the game's menus."""
        self.ai_picking = True
        self.browsing = AI
        self.states.transition(State.SHIP_SELECT)

    def _leave_ship_select(self) -> None:
        if self.ai_picking:
            self.states.transition(State.DEV_MENU)
        else:
            super()._leave_ship_select()

    def _start_level(
        self, index: int, score: int = 0, lives: int = config.PLAYER_LIVES, arsenal: Arsenal | None = None
    ) -> None:
        """Play the level, or watch the AI play it when the menus pick for the AI."""
        if not self.ai_picking:
            super()._start_level(index, score, lives, arsenal)
            return
        self.ai_game = AIGame(self.ship_key, index)
        self._new_ai_game()
        self.states.transition(State.AI_PLAYING)

    def _on_state_change(self, previous: Enum, current: Enum) -> None:
        if current in (State.MAIN_MENU, State.DEV_MENU):
            self.ai_picking = False
        if previous is State.AI_PLAYING:  # back to the menus: no level behind them
            self.world = None
            self.effects.clear()
            self._show_background()
            self.ai_panel.hide()
        super()._on_state_change(previous, current)

    def _new_ai_game(self) -> None:
        """Start a game on the level picked, with the saved brain (it may have learned since the last game)."""
        game = self.ai_game
        game.games += 1
        training = files.load_training(files.brain_folder())
        game.generation = training.generation if training else None
        self.pilot = Pilot(training.brain if training else Brain.random(np.random.default_rng()))
        self._ai_level(game.start)

    def _ai_level(
        self, index: int, score: int = 0, lives: int = config.PLAYER_LIVES, arsenal: Arsenal | None = None
    ) -> None:
        """Start the AI on a level, by the game's rules (going on with the score, lives and weapons it has).

        The level select opens on it again.
        """
        ship = self.ai_game.ship
        level = self.levels[index]
        screen = self.camera_view.area(0.0)
        self.level_index = index
        self.world = World(
            level,
            score=score,
            lives=lives,
            arsenal=arsenal,
            view_top=screen.top,
            view_side=screen.right,
            view_bottom=screen.bottom,
            ship=SHIPS[ship],
        )
        self.ai_watching = f"{SHIPS[ship].name} on {self._label(index)} {level.name}"
        self._show_background(level)
        self._prepare_level(level)
        self.effects.clear()
        self._show_hud(visible=True)

    def _follow_ai(self, world: World) -> None:
        """After a step of the AI's game: the next level, or a new game; and the text over it."""
        game = self.ai_game
        if world.completed or world.game_over:
            following = self.level_index + world.completed  # the level after the last one cleared
            if world.completed and following < len(self.levels):
                self._ai_level(following, world.score, world.lives, world.arsenal)
            else:
                cleared = following - game.start  # in this game
                game.cleared += cleared > 0
                game.best = max(game.best, cleared)
                self._new_ai_game()
        place = self._label(game.start)
        self.ai_panel.show(playing_text(game.generation, self.ai_watching, place, game.games, game.cleared, game.best))

    def _on_back(self) -> None:
        if self.states.state is State.AI_PLAYING:
            self.audio.play("menu_back")
            self.states.transition(State.LEVEL_SELECT)
            return
        super()._on_back()
