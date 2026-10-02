"""The game with the dev tools' screens (`make dev`): the main menu also opens the Models, Bosses, Enemy candidates
and Boss candidates screens (models on show, to work on them) and the AI learning and AI rating screens.
"""

import importlib
import math
import os
from collections.abc import Callable
from enum import Enum
from functools import partial

import numpy as np
from direct.task.Task import Task
from panda3d.core import NodePath

from pewpewdev import candidates
from pewpewdev.ai import files as ai_files
from pewpewdev.ai.brain import Brain
from pewpewdev.ai.pilot import Pilot
from pewpewdev.ai.rating import RUNS as RATING_RUNS
from pewpewdev.ai.rating import places as rated_places
from pewpewdev.ai.sessions import LearningSession, RatingSession, Session
from pewpewdev.states import DEV_TRANSITIONS, DevState
from pewpewdev.ui.ai_panel import AIPanel, learning_text, rating_columns, rating_title
from pewpy import config
from pewpy.app import EFFECTS_RUN_IN, GAME_ASPECT, PewPewApp, fitted_model
from pewpy.game.enemies.enemy import make
from pewpy.game.enemies.kinds import BOSSES, ENEMIES, FINAL_BOSSES
from pewpy.game.enemies.spec import EnemySpec, load_enemy_specs
from pewpy.game.player import SHIPS
from pewpy.game.states import State
from pewpy.game.weapons.bullets import Missile
from pewpy.game.weapons.player.arsenal import LETTERS, WEAPONS
from pewpy.game.weapons.player.secondary import SECONDARY_LETTERS, SECONDARY_WEAPONS
from pewpy.game.world import World
from pewpy.graphics import models
from pewpy.ui import showcase
from pewpy.ui.menu import Menu, MenuItem
from pewpy.ui.showcase import ModelShowcase

SHOWCASE_STATES = frozenset({
    DevState.MODELS,
    DevState.BOSSES,
    DevState.CANDIDATES,
    DevState.BOSS_CANDIDATES,
})  # screens showing models in a turning circle
AI_STATES = frozenset({DevState.AI_LEARNING, DevState.AI_RATING})
AI_WORKERS = max(
    1, (os.cpu_count() or 2) - 2
)  # processes learning or rating: a core left for the game, one for the rest
SECONDARY_NAMES = {"turret": "Turret", "lightning": "Lightning gun"}
PICKUPS_PAGE = "Player, pickups and projectiles"
# The second fleet (src/pewpy/enemies/fleet.json), on pages of their own.
FLEET_KINDS: tuple[str, ...] = tuple(load_enemy_specs("enemies/fleet.json"))
# The Models screen's pages (too many models for one circle): which enemies each shows, by kind; the first also
# shows the player's ships, its missile and the pickups.
MODEL_PAGES: dict[str, Callable[[str], bool]] = {
    PICKUPS_PAGE: lambda kind: not ENEMIES[kind].placeable,
    "Flying enemies": lambda kind: ENEMIES[kind].placeable and not ENEMIES[kind].ground and kind not in FLEET_KINDS,
    "The fleet (1/2)": lambda kind: kind in FLEET_KINDS[: len(FLEET_KINDS) // 2],
    "The fleet (2/2)": lambda kind: kind in FLEET_KINDS[len(FLEET_KINDS) // 2 :],
    "Ground enemies": lambda kind: ENEMIES[kind].ground,
}
CANDIDATES_PER_PAGE = 10
SHOWCASE_CANDIDATE_SIZE = 0.26  # the Candidates screen's models (see showcase.MODEL_SIZE)...
BOSS_CANDIDATES_PER_PAGE = 4
BOSS_CANDIDATE_RADIUS = 0.75
# How much wider than tall the model screens' circle is: an ellipse using a wide screen's sides (1 on a 3:4 screen).
SHOWCASE_STRETCH = max(1.0, GAME_ASPECT / 0.75)
SHOWCASE_BOSS_CANDIDATE_SIZE = 0.42  # bigger than the Bosses screen's: some candidates are huge...
BOSS_CANDIDATE_SCALE = 125  # ...a boss this many cubes across fills that size (all drawn to the same scale)
CANDIDATE_SCALE = 32  # ...a model this many cubes across fills that size: they're all drawn to the same scale
SHOWCASE_BOSS_SIZE = 0.28  # the Models screen's boss pages: fewer models, drawn bigger (see showcase.MODEL_SIZE)
SHOWCASE_BOSS_RADIUS = 0.6  # and a smaller circle, so the names fit on the screen


class DevApp(PewPewApp):
    state_transitions = DEV_TRANSITIONS
    effects_run_in = EFFECTS_RUN_IN | {DevState.AI_LEARNING}

    def _setup_screens(self) -> None:
        self.showcase: ModelShowcase | None = None
        self.showcase_page = 0  # the page shown on the Models or Bosses screen
        self.ai_session: Session | None = None  # learning or rating in the background, on the AI screens
        self.stopped_ai: list[Session] = []  # stopped, still finishing what they were doing
        self.pilot: Pilot | None = None  # the AI flying the ship on screen
        self.ai_watching = ""  # what the AI on screen plays
        self.ai_panel = AIPanel(self.aspect2d)

    def _main_menu_items(self) -> list[MenuItem]:
        go = self._go
        return [
            *super()._main_menu_items(),
            MenuItem("Models", go(DevState.MODELS)),
            MenuItem("Bosses", go(DevState.BOSSES)),
            MenuItem("Enemy candidates", go(DevState.CANDIDATES)),
            MenuItem("Boss candidates", go(DevState.BOSS_CANDIDATES)),
            MenuItem("AI learning", go(DevState.AI_LEARNING)),
            MenuItem("AI rating", go(DevState.AI_RATING)),
        ]

    def _menu(self, state: Enum) -> Menu | None:
        if state in SHOWCASE_STATES:
            return self._models_menu()
        return super()._menu(state)

    def _on_state_change(self, previous: Enum, current: Enum) -> None:
        if current in SHOWCASE_STATES:
            self.showcase_page = 0  # before the menu: its title shows the page
        super()._on_state_change(previous, current)
        if current in SHOWCASE_STATES:
            self._show_showcase()
            self.background.root.hide()  # a plain dark background, to look at the models
        elif self.showcase:
            self.showcase.destroy()
            self.showcase = None
            self.background.root.show()
        self._switch_ai(previous, current)

    def _update(self, task: Task) -> int:
        dt = self._frame_time()
        if self.states.state in AI_STATES:
            self._update_ai(dt)
        if self.showcase:
            self.showcase.update(dt)
        return super()._update(task)

    def _on_back(self) -> None:
        if self.menu_view.menu is None and self.states.state in AI_STATES:
            self.audio.play("menu_back")
            self.states.transition(State.MAIN_MENU)
            return
        super()._on_back()

    def finalizeExit(self) -> None:
        self._stop_ai()
        self._finish_stopped_ai(wait=30.0)  # the brains are saved as it stops
        super().finalizeExit()

    def _models_menu(self, note: str = "") -> Menu:
        """The Models, Bosses and Candidates screens' menu: the page's title, and "Next page" when there are several
        ("Previous page" too when there are more than two).
        """
        titles = self._showcase_titles()
        reload_item = MenuItem("Reload models", self._reload_models)
        back = MenuItem("Back", lambda: self.states.transition(State.MAIN_MENU))
        items = [reload_item, back]
        if len(titles) > 2:
            items.insert(0, MenuItem("Previous page", partial(self._turn_showcase_page, -1)))
        if len(titles) > 1:
            items.insert(0, MenuItem("Next page", partial(self._turn_showcase_page, 1)))
        title = f"{self.states.state.name.replace('_', ' ')}\n{titles[self.showcase_page]}" + (
            f"\n{note}" if note else ""
        )
        selected = items.index(reload_item) if note else 0
        return Menu(title, items, back=back.action, selected=selected)

    def _turn_showcase_page(self, step: int) -> None:
        self.showcase_page = (self.showcase_page + step) % len(self._showcase_titles())
        self._show_showcase()
        self.menu_view.show(self._models_menu())

    def _show_showcase(self) -> None:
        if self.showcase:
            self.showcase.destroy()
        entries, size, radius = self._showcase_page(self.showcase_page)
        if self.states.state is DevState.BOSS_CANDIDATES:
            radius = BOSS_CANDIDATE_RADIUS  # big models: farther from the title and menu, up and down
        self.showcase = ModelShowcase(entries, self.cam, size, radius, SHOWCASE_STRETCH)

    def _showcase_titles(self) -> list[str]:
        """The pages of the screen being shown: the Models screen's (see MODEL_PAGES), the Bosses screen's two per
        world (its mini bosses, then its final bosses).
        """
        if self.states.state in (DevState.CANDIDATES, DevState.BOSS_CANDIDATES):
            bosses = self.states.state is DevState.BOSS_CANDIDATES
            count = len(candidates.boss_candidate_names() if bosses else candidates.candidate_names())
            per_page = BOSS_CANDIDATES_PER_PAGE if bosses else CANDIDATES_PER_PAGE
            pages = max(1, math.ceil(count / per_page))
            return [
                f"{page * per_page + 1}-{min(count, (page + 1) * per_page)} ({page + 1}/{pages})"
                for page in range(pages)
            ]
        if self.states.state is not DevState.BOSSES:
            return list(MODEL_PAGES)
        count = 2 * len(self.worlds)
        return [
            f"{world.name}: {kind} ({2 * index + offset + 1}/{count})"
            for index, world in enumerate(self.worlds)
            for offset, kind in enumerate(("mini bosses", "final bosses"))
        ]

    def _showcase_page(self, index: int) -> tuple[list[tuple[str, NodePath]], float, float]:
        """A page's (name, model) pairs, how big the models are drawn and the circle's radius. Only this page's
        models are built (boss models are big).
        """
        if self.states.state is DevState.CANDIDATES:
            names = candidates.candidate_names()[index * CANDIDATES_PER_PAGE : (index + 1) * CANDIDATES_PER_PAGE]
            return [self._candidate(name) for name in names], SHOWCASE_CANDIDATE_SIZE, showcase.RADIUS
        if self.states.state is DevState.BOSS_CANDIDATES:
            per_page = BOSS_CANDIDATES_PER_PAGE
            names = candidates.boss_candidate_names()[index * per_page : (index + 1) * per_page]
            return [self._boss_candidate(name) for name in names], SHOWCASE_BOSS_CANDIDATE_SIZE, SHOWCASE_BOSS_RADIUS
        if self.states.state is not DevState.BOSSES:
            return self._showcase_entries(list(MODEL_PAGES)[index]), showcase.MODEL_SIZE, showcase.RADIUS
        world = self.worlds[index // 2]
        final = index % 2 == 1
        specs = [
            BOSSES[wave.enemy]
            for level in world.levels
            for wave in level.waves
            if wave.enemy in BOSSES and (wave.enemy in FINAL_BOSSES) == final
        ]
        entries = [(spec.name.title(), self._whole_boss(spec)) for spec in specs]
        return entries, SHOWCASE_BOSS_SIZE, SHOWCASE_BOSS_RADIUS

    def _showcase_entries(self, page: str) -> list[tuple[str, NodePath]]:
        """(name, model) of the ships, enemies, projectiles and pickups on a page of the Models screen: each fitted in
        a 1 x 1 x 1 box by its hitbox (the models are in world units, all with the same cubes).
        """
        entries = []
        if page == PICKUPS_PAGE:
            for spec in SHIPS.values():
                entries.append((spec.name.title(), fitted_model(self.player_models[spec.drawing], spec.size)))
            missile = Missile()
            entries.append(("Missile", fitted_model(self._make_model(missile), missile.height)))
        for kind in ENEMIES:
            if MODEL_PAGES[page](kind):
                enemy = make(kind)
                name = kind.replace("_", " ").title()  # mine_layer: "Mine Layer"
                entries.append((name, fitted_model(self._make_model(enemy), max(enemy.width, enemy.height))))
        if page == PICKUPS_PAGE:
            for kind in [*WEAPONS, "repair", "life", *SECONDARY_WEAPONS]:
                names = {"repair": "Repair", "life": "Extra life"}
                names.update({key: f"{SECONDARY_NAMES[key]} {SECONDARY_LETTERS[key]}" for key in SECONDARY_WEAPONS})
                name = f"{kind.capitalize()} {LETTERS[kind]}" if kind in LETTERS else names[kind]
                entries.append((name, fitted_model(self.pickup_models[kind], config.PICKUP_SIZE)))
        return entries

    def _candidate(self, name: str) -> tuple[str, NodePath]:
        """A model candidate, numbered like its file ("#007" for candidates/007) with its size in cubes, all drawn at
        the same scale so small and big ones compare (read again every time: edited drawings show when the page is
        shown again).
        """
        voxels = models.load_voxels(name)
        label = f"#{name.rsplit('/', 1)[-1]}  {voxels.width}x{voxels.height}"
        return label, fitted_model(models.drawing_model(name), CANDIDATE_SCALE * config.MODEL_VOXEL)

    def _boss_candidate(self, name: str) -> tuple[str, NodePath]:
        """A boss candidate with its parts in place, numbered like its file, all drawn to the same scale (read again
        every time, like the enemy candidates).
        """
        voxels = models.load_voxels(name)
        whole = NodePath(name)
        models.drawing_model(name).reparentTo(whole)
        parts = candidates.boss_candidate_parts(name)
        for drawing, x, y in parts:
            piece = models.drawing_model(drawing)
            piece.reparentTo(whole)
            piece.setPos(x * config.MODEL_VOXEL, 0, y * config.MODEL_VOXEL)
        label = f"#{name.rsplit('/', 1)[-1]}  {voxels.width}x{voxels.height} +{len(parts)}"  # size, and parts
        return label, fitted_model(whole, BOSS_CANDIDATE_SCALE * config.MODEL_VOXEL)

    def _whole_boss(self, spec: EnemySpec) -> NodePath:
        """A boss with its parts in place, fitted in a 1 x 1 x 1 box like the other models."""
        whole = NodePath(spec.drawing)
        pieces = [(spec.drawing, 0.0, 0.0, spec.width, spec.height)]
        pieces += [(part.spec.drawing, part.x, part.y, part.spec.width, part.spec.height) for part in spec.parts]
        for drawing, x, y, _, _ in pieces:
            piece = whole.attachNewNode(drawing)
            self._boss_model(drawing).copyTo(piece)
            piece.setPos(x, 0, y)
        bottom = min(y - height / 2 for _, _, y, _, height in pieces)
        extent = max(2 * spec.half_span, spec.top_reach - bottom)
        box = NodePath("boss")
        whole.reparentTo(box)
        whole.setZ(-(spec.top_reach + bottom) / 2)
        box.setScale(1 / extent)
        return box

    def _reload_models(self) -> None:
        """Read models.py again and rebuild every model; on a mistake, keep the old ones and say what's wrong."""
        try:
            importlib.reload(models)
            self._build_models()
        except Exception as error:
            message = f"{type(error).__name__}: {error}"
            self.menu_view.show(self._models_menu(f"reload failed:\n{message[:60]}"))
            return
        self._show_showcase()
        self.menu_view.show(self._models_menu("reloaded"))

    def _switch_ai(self, previous: Enum, current: Enum) -> None:
        """Start the AI screens' work on the way in, stop it on the way out."""
        if previous in AI_STATES and current not in AI_STATES:
            self._stop_ai()
        if current is DevState.AI_LEARNING:
            self._start_learning()
        elif current is DevState.AI_RATING:
            self._start_rating()

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
        """A level played on screen by the brain (as it is so far), with a ship and on a level drawn at random;
        another one when it ends."""
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
        self._show_hud(True)

    def _update_ai(self, dt: float) -> None:
        session = self.ai_session
        world, pilot = self.world, self.pilot
        if world is not None and pilot is not None:
            self._play(world, pilot.fly(world), dt)
            if world.game_over or world.completed:
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


def main() -> None:
    DevApp().run()
