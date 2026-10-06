"""The Models, Bosses and candidates (enemy, boss, prop) screens: models on show in a turning circle.

Page by page, to work on them ("Reload models" reads their files again).
"""

import importlib
import math
from collections.abc import Callable
from functools import partial

from panda3d.core import NodePath

from pewpy import config
from pewpy.app import GAME_ASPECT, PewPewApp, fitted_model
from pewpy.game.enemies.enemy import Enemy
from pewpy.game.enemies.kinds import BOSSES, ENEMIES, FINAL_BOSSES
from pewpy.game.enemies.spec import EnemySpec, load_enemy_specs
from pewpy.game.player import SHIPS
from pewpy.game.states import State
from pewpy.game.weapons.bullets import Missile
from pewpy.game.weapons.player.arsenal import LETTERS, WEAPONS
from pewpy.game.weapons.player.secondary import SECONDARY_LETTERS, SECONDARY_WEAPONS
from pewpy.graphics import models
from pewpy.scenery.ground.shader.geometry import mesh_node
from pewpy.tools.dev import candidates
from pewpy.tools.dev.states import DevState
from pewpy.ui import showcase
from pewpy.ui.menu import Menu, MenuItem
from pewpy.ui.showcase import ModelShowcase

SHOWCASE_STATES = frozenset({
    DevState.MODELS,
    DevState.BOSSES,
    DevState.CANDIDATES,
    DevState.PLAYER_CANDIDATES,
    DevState.BOSS_CANDIDATES,
    DevState.PROP_CANDIDATES,
})  # screens showing models in a turning circle
CANDIDATE_STATES = frozenset({
    DevState.CANDIDATES,
    DevState.PLAYER_CANDIDATES,
    DevState.BOSS_CANDIDATES,
    DevState.PROP_CANDIDATES,
})  # screens showing candidates, numbered, page by page
SECONDARY_NAMES = {"turret": "Turret", "lightning": "Lightning gun"}
PICKUPS_PAGE = "Player, pickups and projectiles"
# The second fleet (data/enemies/fleet.json), on pages of their own.
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
PLAYER_CANDIDATE_SCALE = 22  # the same for the player's ships: about the biggest's size (0.14 across, 21 cubes)
PROP_CANDIDATES_PER_PAGE = 10
PROP_SCALE = 0.16  # world units: a prop this big fills the Candidates screen's size (all drawn to the same scale)
PROP_TILT = 30.0  # degrees: the props lean their tops towards the camera, to show their roofs
PART_TAG = "part"  # tags a boss's destroyable parts, to blink them
PART_BLINK = 1.2  # seconds: a boss's parts are lit up for the first half of each, then plain (a slow blink)
PART_LIT = (1.9, 1.9, 1.9, 1.0)  # how much brighter they are when lit up
SHOWCASE_BOSS_SIZE = 0.28  # the Models screen's boss pages: fewer models, drawn bigger (see showcase.MODEL_SIZE)
SHOWCASE_BOSS_RADIUS = 0.6  # and a smaller circle, so the names fit on the screen


class ModelScreens(PewPewApp):
    """The screens showing models."""

    # Set up by DevApp._setup_screens.
    showcase: ModelShowcase | None
    showcase_page: int  # the page shown on the Models or Bosses screen
    blinking: list[NodePath]  # the bosses' parts on show (see blink_parts)

    def _models_menu(self, note: str = "") -> Menu:
        """Make the Models, Bosses and Candidates screens' menu: the page's title, "Next page" when there are several.

        "Previous page" too when there are more than two.
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
        tilt = PROP_TILT if self.states.state is DevState.PROP_CANDIDATES else 0.0
        self.showcase = ModelShowcase(entries, self.cam, size, radius, SHOWCASE_STRETCH, tilt)
        self.blinking = list(self.showcase.root.findAllMatches(f"**/={PART_TAG}"))

    def blink_parts(self) -> None:
        """Light up the bosses' destroyable parts for half of every PART_BLINK seconds, so they stand out."""
        if not self.showcase:
            return
        lit = self.showcase.time % PART_BLINK < PART_BLINK / 2
        for part in self.blinking:
            if lit:
                part.setColorScale(*PART_LIT)
            else:
                part.clearColorScale()

    def _showcase_titles(self) -> list[str]:
        """Return the pages of the screen being shown.

        The Models screen's (see MODEL_PAGES), the Bosses screen's two per world (its mini bosses, then its final
        bosses).
        """
        if self.states.state in CANDIDATE_STATES:
            count, per_page = {
                DevState.CANDIDATES: (len(candidates.candidate_names()), CANDIDATES_PER_PAGE),
                DevState.PLAYER_CANDIDATES: (len(candidates.player_candidate_names()), CANDIDATES_PER_PAGE),
                DevState.BOSS_CANDIDATES: (len(candidates.boss_candidate_names()), BOSS_CANDIDATES_PER_PAGE),
                DevState.PROP_CANDIDATES: (len(candidates.prop_candidate_names()), PROP_CANDIDATES_PER_PAGE),
            }[self.states.state]
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
        """Return a page's (name, model) pairs, how big the models are drawn and the circle's radius.

        Only this page's models are built (boss models are big).
        """
        if self.states.state is DevState.CANDIDATES:
            names = candidates.candidate_names()[index * CANDIDATES_PER_PAGE : (index + 1) * CANDIDATES_PER_PAGE]
            return [self._candidate(name) for name in names], SHOWCASE_CANDIDATE_SIZE, showcase.RADIUS
        if self.states.state is DevState.PLAYER_CANDIDATES:
            names = candidates.player_candidate_names()[index * CANDIDATES_PER_PAGE : (index + 1) * CANDIDATES_PER_PAGE]
            return (
                [self._candidate(name, PLAYER_CANDIDATE_SCALE) for name in names],
                SHOWCASE_CANDIDATE_SIZE,
                showcase.RADIUS,
            )
        if self.states.state is DevState.PROP_CANDIDATES:
            per_page = PROP_CANDIDATES_PER_PAGE
            names = candidates.prop_candidate_names()[index * per_page : (index + 1) * per_page]
            return [self._prop_candidate(name) for name in names], SHOWCASE_CANDIDATE_SIZE, showcase.RADIUS
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
        """Return (name, model) of the ships, enemies, projectiles and pickups on a page of the Models screen.

        Each is fitted in a 1 x 1 x 1 box by its hitbox (the models are in world units, all with the same cubes).
        """
        entries = []
        if page == PICKUPS_PAGE:
            entries.extend(
                (spec.name.title(), fitted_model(self.player_models[spec.drawing], spec.size))
                for spec in SHIPS.values()
            )
            missile = Missile()
            entries.append(("Missile", fitted_model(self._make_model(missile), missile.height)))
        for kind in ENEMIES:
            if MODEL_PAGES[page](kind):
                enemy = Enemy.of_kind(kind)
                name = kind.replace("_", " ").title()  # mine_layer: "Mine Layer"
                entries.append((name, fitted_model(self._make_model(enemy), max(enemy.width, enemy.height))))
        if page == PICKUPS_PAGE:
            for kind in [*WEAPONS, "repair", "life", *SECONDARY_WEAPONS]:
                names = {"repair": "Repair", "life": "Extra life"}
                names.update({key: f"{SECONDARY_NAMES[key]} {SECONDARY_LETTERS[key]}" for key in SECONDARY_WEAPONS})
                name = f"{kind.capitalize()} {LETTERS[kind]}" if kind in LETTERS else names[kind]
                entries.append((name, fitted_model(self.pickup_models[kind], config.PICKUP_SIZE)))
        return entries

    def _candidate(self, name: str, scale: int = CANDIDATE_SCALE) -> tuple[str, NodePath]:
        """Return a model candidate, numbered like its file ("#007" for candidates/enemies/007) with its size in cubes.

        All are drawn at the same scale (`scale` model cubes across fill the slot) so small and big ones compare (read
        again every time: edited drawings show when the page is shown again).
        """
        voxels = models.load_voxels(name)
        label = f"#{name.rsplit('/', 1)[-1]}  {voxels.width}x{voxels.height}"
        return label, fitted_model(models.drawing_model(name), scale * config.MODEL_VOXEL)

    def _boss_candidate(self, name: str) -> tuple[str, NodePath]:
        """Return a boss candidate with its parts in place, numbered like its file, all drawn to the same scale.

        Read again every time, like the enemy candidates.
        """
        voxels = models.load_voxels(name)
        whole = NodePath(name)
        models.drawing_model(name).reparentTo(whole)
        parts = candidates.boss_candidate_parts(name)
        for drawing, x, y in parts:
            piece = models.drawing_model(drawing)
            piece.reparentTo(whole)
            piece.setPos(x * config.MODEL_VOXEL, 0, y * config.MODEL_VOXEL)
            piece.setTag(PART_TAG, "")
        label = f"#{name.rsplit('/', 1)[-1]}  {voxels.width}x{voxels.height} +{len(parts)}"  # size, and parts
        return label, fitted_model(whole, BOSS_CANDIDATE_SCALE * config.MODEL_VOXEL)

    def _prop_candidate(self, name: str) -> tuple[str, NodePath]:
        """Return a prop candidate, numbered like its file with its size (in hundredths), all drawn to the same scale.

        Upright, its middle at the slot's; lit like the models. A file that doesn't build shows its number and the
        mistake, without a model.
        """
        try:
            prop = candidates.prop_candidate(name)
        except (ValueError, KeyError, TypeError) as error:
            return f"#{name}  {type(error).__name__}", NodePath(name)
        vertices = prop.vertices.copy()
        width, length, height = prop.size
        vertices[:, 2] -= height / 2
        vertices[:, 9] = 1.0  # opaque: the 4th color number is the ground shader's material
        vertices[:, 10:12] = 0.5  # no bevel (see pewpy.graphics.lighting)
        model = mesh_node(name, vertices, prop.indices)
        model.setTwoSided(True)
        label = f"#{name}  {width * 100:.0f}x{length * 100:.0f}x{height * 100:.0f}"
        return label, fitted_model(model, PROP_SCALE)

    def _whole_boss(self, spec: EnemySpec) -> NodePath:
        """Return a boss with its parts in place, fitted in a 1 x 1 x 1 box like the other models."""
        whole = NodePath(spec.drawing)
        pieces = [(spec.drawing, 0.0, 0.0, spec.width, spec.height)]
        pieces += [(part.spec.drawing, part.x, part.y, part.spec.width, part.spec.height) for part in spec.parts]
        for index, (drawing, x, y, _, _) in enumerate(pieces):
            piece = whole.attachNewNode(drawing)
            self._ship_model(drawing).copyTo(piece)
            piece.setPos(x, 0, y)
            if index:  # the parts, not the core
                piece.setTag(PART_TAG, "")
        bottom = min(y - height / 2 for _, _, y, _, height in pieces)
        extent = max(2 * spec.half_span, spec.top_reach - bottom)
        box = NodePath("boss")
        whole.reparentTo(box)
        whole.setZ(-(spec.top_reach + bottom) / 2)
        box.setScale(1 / extent)
        return box

    def _reload_models(self) -> None:
        """Read the models' code (pewpy.graphics.models) again and rebuild every model.

        On a mistake, keep the old ones and say what's wrong.
        """
        try:
            importlib.reload(models)
            self._build_models()
        except Exception as error:  # noqa: BLE001 - any mistake in the edited code is shown, not raised
            message = f"{type(error).__name__}: {error}"
            self.menu_view.show(self._models_menu(f"reload failed:\n{message[:60]}"))
            return
        self._show_showcase()
        self.menu_view.show(self._models_menu("reloaded"))
