"""The AI screens: learning or rating in the background, the AI flying the ship on screen; the AI playing the game."""

import os
from dataclasses import dataclass, field
from enum import Enum

import numpy as np

from pewpy import config
from pewpy.game.player import SHIPS
from pewpy.game.weapons.player.arsenal import Arsenal
from pewpy.game.world import World
from pewpy.tools.ai import files as ai_files
from pewpy.tools.ai.brain import Brain
from pewpy.tools.ai.pilot import Pilot
from pewpy.tools.ai.rating import RUNS as RATING_RUNS
from pewpy.tools.ai.rating import places as rated_places
from pewpy.tools.ai.sessions import LearningSession, RatingSession, Session
from pewpy.tools.dev.app.model_screens import ModelScreens
from pewpy.tools.dev.states import DevState
from pewpy.tools.dev.ui.ai_panel import AIPanel, learning_text, playing_text, rating_columns, rating_title

AI_STATES = frozenset({DevState.AI_LEARNING, DevState.AI_RATING, DevState.AI_PLAYING})
AI_WORKERS = max(
    1, (os.cpu_count() or 2) - 2
)  # processes learning or rating: a core left for the game, one for the rest


@dataclass
class AIGame:
    """The AI playing the game on the AI playing screen: each ship in turn, from the first level until game over."""

    ship: int = -1  # which of SHIPS plays (the next one at each game)
    generation: int | None = None  # the saved brain's (None: no brain yet, a new one plays)
    reached: dict[str, int] = field(default_factory=dict)  # for each ship, the most levels cleared in a game


class AIScreens(ModelScreens):
    """The AI screens (see pewpy.tools.ai)."""

    # Set up by DevApp._setup_screens.
    ai_session: Session | None  # learning or rating in the background, on the AI screens
    stopped_ai: list[Session]  # stopped, still finishing what they were doing
    pilot: Pilot | None  # the AI flying the ship on screen
    ai_watching: str  # what the AI on screen plays
    ai_game: AIGame
    ai_panel: AIPanel

    def _switch_ai(self, previous: Enum, current: Enum) -> None:
        """Start the AI screens' work on the way in, stop it on the way out."""
        if previous in AI_STATES and current not in AI_STATES:
            self._stop_ai()
        if current is DevState.AI_LEARNING:
            self._start_learning()
        elif current is DevState.AI_RATING:
            self._start_rating()
        elif current is DevState.AI_PLAYING:
            self.ai_game = AIGame()
            self._new_ai_game()

    def _start_learning(self) -> None:
        self._finish_stopped_ai()
        self.ai_session = LearningSession(list(SHIPS), ai_files.ai_folder(), AI_WORKERS)
        self.ai_session.start()
        self._watch_ai()

    def _start_rating(self) -> None:
        self._finish_stopped_ai()
        self.ai_session = RatingSession(list(SHIPS), ai_files.ai_folder(), RATING_RUNS, AI_WORKERS)
        self.ai_session.start()

    def _stop_ai(self) -> None:
        """Ask the AI's work to stop: it ends what it is doing (a generation) and saves, in the background."""
        if self.ai_session is not None:
            self.ai_session.stop()
            self.stopped_ai.append(self.ai_session)
            self.ai_session = None
        self.pilot = None
        self.ai_panel.clear()

    def _finish_stopped_ai(self, wait: float = 60.0) -> None:
        """Wait for stopped work to have saved, before starting more (both would write the same brains)."""
        for session in self.stopped_ai:
            session.stop(wait)
        self.stopped_ai = []

    def _watch_ai(self) -> None:
        """Show a level played on screen by the brain (as it is so far), with a ship and on a level drawn at random.

        Another one starts when it ends.
        """
        session = self.ai_session
        if not isinstance(session, LearningSession):
            return
        rng = np.random.default_rng()
        brain = session.brain() or Brain.random(rng)
        ship = str(rng.choice(list(SHIPS)))
        index = int(rng.integers(len(self.levels)))
        level = self.levels[index]
        screen = self.camera_view.area(0.0)
        self.world = World(level, view_top=screen.top, view_side=screen.right, ship=SHIPS[ship])
        self.pilot = Pilot(brain)
        self.ai_watching = f"On screen: {SHIPS[ship].name} on {self._label(index)} {level.name}"
        self._show_background(level)
        self._prepare_bosses(level)
        self.effects.clear()
        self._show_hud(visible=True)

    def _new_ai_game(self) -> None:
        """Start a game with the next ship and the saved brain (it may have learned since the last game)."""
        game = self.ai_game
        game.ship = (game.ship + 1) % len(SHIPS)
        training = ai_files.load_training(ai_files.ai_folder())
        game.generation = training.generation if training else None
        self.pilot = Pilot(training.brain if training else Brain.random(np.random.default_rng()))
        self._ai_level(0)

    def _ai_level(
        self, index: int, score: int = 0, lives: int = config.PLAYER_LIVES, arsenal: Arsenal | None = None
    ) -> None:
        """Start the AI on a level, by the game's rules (going on with the score, lives and weapons it has)."""
        ship = list(SHIPS)[self.ai_game.ship]
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
        self._prepare_bosses(level)
        self.effects.clear()
        self._show_hud(visible=True)

    def _update_ai_game(self) -> None:
        """Go on to the next level once one is cleared, or to a new game once the lives are gone."""
        world, game = self.world, self.ai_game
        if world is None or not (world.completed or world.game_over):
            return
        ship = list(SHIPS)[game.ship]
        cleared = self.level_index + world.completed
        game.reached[ship] = max(game.reached.get(ship, 0), cleared)
        if world.completed and cleared < len(self.levels):
            self._ai_level(cleared, world.score, world.lives, world.arsenal)
        else:
            self._new_ai_game()

    def _update_ai(self, dt: float) -> None:
        session = self.ai_session
        world, pilot = self.world, self.pilot
        if world is not None and pilot is not None:
            self._play(world, pilot.fly(world), dt)
            if self.states.state is DevState.AI_PLAYING:
                self._update_ai_game()
                self.ai_panel.show_learning(
                    playing_text(self.ai_game.generation, self.ai_watching, self.ai_game.reached, len(self.levels))
                )
            elif world.game_over or world.completed:
                self._watch_ai()
        if isinstance(session, LearningSession):
            with session.lock:
                text = learning_text(session.report, dict(session.checks), self.ai_watching, session.error)
            self.ai_panel.show_learning(text)
        elif isinstance(session, RatingSession):
            table = session.table()
            places = [(place, level.name) for place, level in rated_places()]
            rated = sum(len(ratings) for ratings in table.values())
            total = len(places) * len(session.ships)
            now = next((ship for ship in session.ships if len(table[ship]) < len(places)), None)
            doing = f"Rating {SHIPS[now].name}: {rated}/{total} ratings" if now else ""
            saved = str(session.folder / "ratings.json") if session.saved else ""
            title = rating_title(session.ships, session.runs, doing, saved, session.error)
            self.ai_panel.show_rating(title, rating_columns(places, session.ships, table), len(session.ships))
