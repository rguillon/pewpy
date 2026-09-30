"""Panda3D application: window, camera, input and rendering."""

import importlib
import math
import re
from collections.abc import Callable
from functools import partial
from typing import Literal

from direct.gui.OnscreenText import OnscreenText
from direct.showbase.ShowBase import ShowBase
from direct.task.Task import Task
from panda3d.core import (
    AmbientLight,
    ButtonThrower,
    Camera,
    CardMaker,
    DirectionalLight,
    GraphicsEngine,
    ModifierButtons,
    NodePath,
    PerspectiveLens,
    Point2,
    Point3,
    TextNode,
    Vec3,
    loadPrcFileData,
)

from pewpy import config, lighting, models, showcase
from pewpy.background import Scenery
from pewpy.background_view import TIMES_OF_DAY, BackgroundView, CameraView
from pewpy.boss_catalog import BOSSES
from pewpy.bosses import Boss, BossPart, BossSpec
from pewpy.effects import Effects
from pewpy.effects_view import EffectsView
from pewpy.enemies import (
    Diver,
    Drone,
    Enemy,
    Gunship,
    Mine,
    MineLayer,
    ShieldCarrier,
    Sniper,
    Splitter,
    Swarmer,
    Turret,
    Weaver,
)
from pewpy.entities import Bullet, Entity, Pickup
from pewpy.level import Level, load_worlds
from pewpy.menu import Menu, MenuItem
from pewpy.menu_view import MenuView
from pewpy.player import Player
from pewpy.showcase import ModelShowcase
from pewpy.sprites import Sprite, SpriteBatch
from pewpy.states import State, StateMachine
from pewpy.terrain import BIOMES, GROUND_VOXEL
from pewpy.weapons import LETTERS, WEAPONS, Arsenal, Missile
from pewpy.world import Controls, Event, World

Color = tuple[float, float, float, float]
TextAlign = Literal[0, 1, 2, 3, 4, 5]  # TextNode.ALeft, ARight, ACenter...

MOVE_KEYS = {
    "arrow_left": (-1, 0),
    "arrow_right": (1, 0),
    "arrow_up": (0, 1),
    "arrow_down": (0, -1),
}
FIRE_KEY = "space"
SWITCH_WEAPON_KEY = "shift"
# Menus: Up/Down move the highlight, Enter chooses, Escape goes back (and pauses while playing).
MENU_MOVES = {"arrow_up": -1, "arrow_down": 1}
MENU_CHOOSE_KEY = "enter"
BACK_KEY = "escape"
WEAPON_COLORS: dict[str, Color] = {
    "bullets": (1.0, 0.9, 0.2, 1),
    "laser": (0.3, 0.9, 1.0, 1),
    "missiles": (1.0, 0.6, 0.15, 1),
}
HUD_DIM_COLOR: Color = (0.5, 0.5, 0.55, 1)
PICKUP_SPIN_SPEED = 120.0  # degrees per second

# The model of each kind of ship: the name of its function in models.py (looked up by name, so the Models
# screen can reload models.py).
SHIP_MODELS: dict[type[Entity], str] = {
    Player: "player_model",
    Drone: "drone_model",
    Weaver: "weaver_model",
    Diver: "diver_model",
    Gunship: "gunship_model",
    Turret: "turret_model",
    Swarmer: "swarmer_model",
    Sniper: "sniper_model",
    MineLayer: "mine_layer_model",
    Mine: "mine_model",
    ShieldCarrier: "shield_carrier_model",
    Splitter: "splitter_model",
    Missile: "missile_model",
}
MINE_SPIN_SPEED = 90.0  # degrees per second
SHOWCASE_STATES = frozenset({State.MODELS, State.BOSSES})  # screens showing models in a turning circle
# Particles keep moving after the last explosion of a level or a life (not in pause or the menus).
EFFECTS_RUN_IN = frozenset({State.PLAYING, State.GAME_OVER, State.LEVEL_COMPLETE})
FLASH_COLOR: Color = (1.0, 1.0, 1.0, 1)
BACKGROUND_COLOR: Color = (0.02, 0.02, 0.08, 1)
GAME_ASPECT = config.WINDOW_WIDTH / config.WINDOW_HEIGHT  # the game area keeps this shape (width / height)
PLAYER_BULLET_COLOR: Color = (0.3, 1.0, 0.25, 1)  # bright green
ENEMY_BULLET_COLOR: Color = (1.0, 0.5, 0.9, 1)
SNIPER_BULLET_COLOR: Color = (0.4, 0.6, 1.0, 1)
HEAVY_BULLET_COLOR: Color = (1.0, 0.55, 0.15, 1)  # bosses' big shots
ARMORED_SHADE: Color = (0.55, 0.55, 0.62, 1)  # a boss's core, darker while shots bounce off it
HIT_SHADE: Color = (1.6, 1.6, 1.6, 1)  # bosses light up when hit (white would hide them: they're shot all the time)
BULLET_GLOW = 1.8  # a bullet's sprite, compared with its hitbox
MAX_BULLETS = 512
HUD_MARGIN = 0.025  # space between the HUD and the edges of the game area (aspect2d units: the width is 2)
HUD_TEXT = 0.06  # score and lives
HUD_SMALL = 0.055  # weapon levels (the selected one is bigger)
WEAPON_SPACING = 0.15
HEALTH_BAR_WIDTH = 0.5
HEALTH_BAR_HEIGHT = 0.025
SHOWCASE_BOSS_SIZE = 0.28  # the Models screen's boss pages: fewer models, drawn bigger (see showcase.MODEL_SIZE)
SHOWCASE_BOSS_RADIUS = 0.6  # and a smaller circle, so the names fit on the screen
BOSS_BAR_WIDTH = 1.1  # at the top edge, with the boss's name under it
BOSS_BAR_HEIGHT = 0.025
PLAYER_BANK_ANGLE = 25.0  # degrees of roll at full sideways speed
FLAME_FLICKER = (0.12, 0.08)  # how much engine flames waver in length: a slow wave and a fast one
FLAME_THRUST = 0.35  # the player's flames: this much longer flying up at full speed, shorter flying down


class PewPewApp(ShowBase):
    def __init__(self) -> None:
        loadPrcFileData(
            "",
            f"""
            window-title {config.WINDOW_TITLE}
            win-size {config.WINDOW_WIDTH} {config.WINDOW_HEIGHT}
            sync-video true
            """,
        )
        super().__init__()
        self.disableMouse()
        self._setup_letterbox()
        # Set up the 2D overlay (menus, HUD) the way a window does when it opens or resizes, so it's the same
        # without a window (tests, screenshots): the game area is 2 units wide, its anchors on its edges.
        self.adjustWindowAspectRatio(self.getAspectRatio())
        self._setup_camera()
        self._setup_lights()
        # Bullets are soft round sprites (missiles have a model): solid in the middle, fading at the edge.
        self.bullet_sprites = SpriteBatch(
            self.render, self.cam.node().getLens(), MAX_BULLETS, glow=False, core=0.45, hot=0.35
        )
        self._build_models()
        self.showcase: ModelShowcase | None = None
        self.showcase_page = 0  # the page shown on the Models or Bosses screen
        self.laser_node = models.laser_beam_model()
        self.laser_node.reparentTo(self.render)
        self.laser_node.hide()

        self.worlds = load_worlds()
        self.levels = [level for world in self.worlds for level in world.levels]  # in playing order
        # For each level: (its world's index, its number in the world, from 1).
        self.places = [(w, n + 1) for w, world in enumerate(self.worlds) for n in range(len(world.levels))]
        self.level_index = 0
        self.world_index = 0  # the world picked in the world select
        self.world: World | None = None
        self.nodes: dict[Entity, NodePath] = {}
        self.flames: dict[Entity, list[tuple[NodePath, float]]] = {}  # engine flames and their steady length
        self.camera_view = CameraView(self.cam, self.cam.node().getLens(), self.render)
        self.background = BackgroundView(Scenery("space", self.camera_view), self.render)  # behind the menus
        self.effects = Effects()
        self.effects_view = EffectsView(self.effects, self.render, self.cam.node().getLens())

        self.keys_down: set[str] = set()
        for key in (*MOVE_KEYS, FIRE_KEY):
            # One handler per key (Panda3D keeps only the last one): the arrows also move menu highlights.
            self.accept(key, self._on_key, [key])
            self.accept(f"{key}-up", self.keys_down.discard, [key])
        self.accept(SWITCH_WEAPON_KEY, self._switch_weapon)
        self.accept(MENU_CHOOSE_KEY, self._on_choose)
        self.accept(BACK_KEY, self._on_back)
        self._disable_modifier_keys()

        self.menu_view = MenuView(self.aspect2d)
        self._setup_hud()

        self.states = StateMachine(on_change=self._on_state_change)
        self._on_state_change(self.states.state, self.states.state)
        self.taskMgr.add(self._update, "update")

    def _disable_modifier_keys(self) -> None:
        # By default Panda3D sends "shift-space" instead of "space" while Shift is held, which would stop
        # firing when switching weapons. Treat Shift like any other key.
        if self.mouseWatcher is None:  # no window, e.g. offscreen
            return
        for path in self.mouseWatcher.findAllMatches("**/+ButtonThrower"):
            thrower = path.node()
            if isinstance(thrower, ButtonThrower):
                thrower.setModifierButtons(ModifierButtons())
        if self.mouseWatcherNode is not None:
            self.mouseWatcherNode.setModifierButtons(ModifierButtons())

    def _switch_weapon(self) -> None:
        if self.world is not None and self.states.state is State.PLAYING:
            self.world.arsenal.switch()

    def _setup_letterbox(self) -> None:
        # The game keeps its 3:4 shape whatever the window size: the 3D view and the HUD are drawn in a centered
        # region, with black bars around it. The window clears to black, the region to the space color.
        if self.win is None:
            return
        self.win.setClearColor((0, 0, 0, 1))
        region = self.camNode.getDisplayRegion(0)
        region.setClearColorActive(True)
        region.setClearColor(BACKGROUND_COLOR)
        self._fit_letterbox()

    def _fit_letterbox(self) -> None:
        if self.win is None or not self.win.hasSize():
            return
        dimensions = letterbox(self.win.getXSize(), self.win.getYSize())
        for camera in (self.cam, self.cam2d, self.cam2dp):
            node = camera.node()
            if isinstance(node, Camera):
                for index in range(node.getNumDisplayRegions()):
                    node.getDisplayRegion(index).setDimensions(*dimensions)

    # ShowBase calls these two on window changes. (The types-panda3d stubs say GraphicsEngine for `win`; it's
    # really the window, but we don't use it.)
    def windowEvent(self, win: GraphicsEngine) -> None:
        super().windowEvent(win)
        self._fit_letterbox()

    def getAspectRatio(self, win: GraphicsEngine | None = None) -> float:
        # ShowBase sizes the lens and the HUD (aspect2d) from this: always the game's shape, see _setup_letterbox.
        return GAME_ASPECT

    def _setup_camera(self) -> None:
        # The game plays on the X/Z plane (X right, Z up the screen); the camera sits in front of it (-Y),
        # tilted so the top of the play area is farther away, and backs off until the whole area fits.
        lens = PerspectiveLens()
        aspect = GAME_ASPECT
        vertical_fov = config.CAMERA_FOV
        horizontal_fov = math.degrees(2 * math.atan(math.tan(math.radians(vertical_fov) / 2) * aspect))
        lens.setFov(horizontal_fov, vertical_fov)
        lens.setNearFar(0.1, 100)
        self.cam.node().setLens(lens)

        tilt = math.radians(config.CAMERA_TILT)
        direction = Vec3(0, -math.cos(tilt), -math.sin(tilt))
        distance = 1.0
        while True:
            self.cam.setPos(direction * distance)
            self.cam.lookAt(0, 0, 0)
            if self._play_area_visible() or distance > 50:
                break
            distance += 0.05

    def _play_area_visible(self, margin: float = 1.04) -> bool:
        lens = self.cam.node().getLens()
        half_width, half_height = config.PLAY_WIDTH / 2 * margin, config.PLAY_HEIGHT / 2 * margin
        for x in (-half_width, half_width):
            for z in (-half_height, half_height):
                point = self.cam.getRelativePoint(self.render, Point3(x, 0, z))
                if not lens.project(point, Point2()):
                    return False
        return True

    def _setup_lights(self) -> None:
        ambient = AmbientLight("ambient")
        ambient.setColor((0.35, 0.35, 0.4, 1))
        self.render.setLight(self.render.attachNewNode(ambient))
        sun = DirectionalLight("sun")
        sun.setColor((0.9, 0.9, 0.85, 1))
        sun_node = self.render.attachNewNode(sun)
        sun_node.setHpr(-30, 20, 0)  # shining away from the camera, lighting the faces the camera sees
        self.render.setLight(sun_node)
        lighting.setup(self)

    def _on_key(self, key: str) -> None:
        self.keys_down.add(key)
        menu = self.menu_view.menu
        if menu is not None and key in MENU_MOVES:
            menu.move(MENU_MOVES[key])
            self.menu_view.refresh()

    def _on_choose(self) -> None:
        if self.menu_view.menu is not None:
            self.menu_view.menu.choose()

    def _on_back(self) -> None:
        if self.menu_view.menu is not None:
            self.menu_view.menu.go_back()
        elif self.states.state is State.PLAYING:
            self.states.transition(State.PAUSED)

    def _menu(self, state: State) -> Menu | None:
        """The menu shown in each state (None while playing)."""

        def go(target: State) -> Callable[[], None]:
            return lambda: self.states.transition(target)

        main_menu = MenuItem("Main menu", go(State.MAIN_MENU))
        if state is State.MAIN_MENU:
            items = [
                MenuItem("Start", go(State.WORLD_SELECT)),
                MenuItem("Models", go(State.MODELS)),
                MenuItem("Bosses", go(State.BOSSES)),
            ]
            return Menu("PEWPEW", [*items, MenuItem("Quit", self.userExit)])
        if state in SHOWCASE_STATES:
            return self._models_menu()
        if state is State.WORLD_SELECT:
            return self._world_menu()
        if state is State.LEVEL_SELECT:
            return self._level_menu()
        if state is State.PAUSED:
            return Menu("PAUSED", [MenuItem("Resume", go(State.PLAYING)), main_menu], back=go(State.PLAYING))
        if state is State.GAME_OVER:
            return Menu("GAME OVER", [MenuItem("Continue", self._continue), main_menu], back=go(State.MAIN_MENU))
        if state is State.LEVEL_COMPLETE:
            return self._level_complete_menu(main_menu)
        return None

    def _level_complete_menu(self, main_menu: MenuItem) -> Menu:
        if self._is_last_level():
            return Menu("ALL LEVELS COMPLETE\nYOU WIN!", [main_menu], back=main_menu.action)
        world, number = self.places[self.level_index]
        if number == len(self.worlds[world].levels):  # the world's last level
            title, next_item = f"WORLD COMPLETE\n{self.worlds[world].name}", "Next world"
        else:
            title, next_item = "LEVEL COMPLETE", "Next level"
        return Menu(title, [MenuItem(next_item, self._next_level), main_menu], back=main_menu.action)

    def _models_menu(self, note: str = "") -> Menu:
        """The Models and Bosses screens' menu: the page's title, and "Next page" when there are several."""
        titles = self._showcase_titles()
        reload_item = MenuItem("Reload models", self._reload_models)
        back = MenuItem("Back", lambda: self.states.transition(State.MAIN_MENU))
        items = [reload_item, back]
        if len(titles) > 1:
            items.insert(0, MenuItem("Next page", self._next_showcase_page))
        title = f"{self.states.state.name}\n{titles[self.showcase_page]}" + (f"\n{note}" if note else "")
        selected = items.index(reload_item) if note else 0
        return Menu(title, items, back=back.action, selected=selected)

    def _next_showcase_page(self) -> None:
        self.showcase_page = (self.showcase_page + 1) % len(self._showcase_titles())
        self._show_showcase()
        self.menu_view.show(self._models_menu())

    def _show_showcase(self) -> None:
        if self.showcase:
            self.showcase.destroy()
        entries, size, radius = self._showcase_page(self.showcase_page)
        self.showcase = ModelShowcase(entries, self.cam, size, radius)

    def _build_models(self) -> None:
        """Build every model from models.py (looked up by name, so a reloaded models.py is used)."""
        self.ship_models = {kind: getattr(models, name)() for kind, name in SHIP_MODELS.items()}
        # Explosions throw debris in the colors of what blew up.
        self.debris_colors = {kind.__name__: models.main_colors(model) for kind, model in self.ship_models.items()}
        self.shield_bubble = models.shield_bubble_model()
        self.pickup_models = {weapon: models.pickup_model(LETTERS[weapon], WEAPON_COLORS[weapon]) for weapon in WEAPONS}
        self.pickup_models["repair"] = models.repair_model()
        # Bosses and their parts: one model per drawing, built when first needed (they're big: building them all
        # takes seconds), see _boss_model.
        self.boss_models: dict[str, NodePath] = {}

    def _boss_model(self, drawing: str) -> NodePath:
        if drawing not in self.boss_models:
            model = self.boss_models[drawing] = models.drawing_model(drawing)
            self.debris_colors[drawing] = models.main_colors(model)
        return self.boss_models[drawing]

    def _prepare_bosses(self, level: Level) -> None:
        """Build the level's boss models now, so the game doesn't stall when the boss comes."""
        for wave in level.waves:
            spec = BOSSES.get(wave.enemy)
            if spec:
                for drawing in [spec.drawing, *(part.drawing for part in spec.parts)]:
                    self._boss_model(drawing)

    def _showcase_titles(self) -> list[str]:
        """The pages of the screen being shown: the Models screen has one (ships and pickups), the Bosses screen one
        per world."""
        if self.states.state is not State.BOSSES:
            return ["Ships and pickups"]
        count = len(self.worlds)
        return [f"{world.name} ({index + 1}/{count})" for index, world in enumerate(self.worlds)]

    def _showcase_page(self, index: int) -> tuple[list[tuple[str, NodePath]], float, float]:
        """A page's (name, model) pairs, how big the models are drawn and the circle's radius. Only this page's
        models are built (boss models are big)."""
        if self.states.state is not State.BOSSES:
            return self._showcase_entries(), showcase.MODEL_SIZE, showcase.RADIUS
        world = self.worlds[index]
        specs = [BOSSES[wave.enemy] for level in world.levels for wave in level.waves if wave.enemy in BOSSES]
        entries = [(spec.name.title(), self._whole_boss(spec)) for spec in specs]
        return entries, SHOWCASE_BOSS_SIZE, SHOWCASE_BOSS_RADIUS

    def _showcase_entries(self) -> list[tuple[str, NodePath]]:
        """(name, model) of every ship, enemy, missile and pickup, for the Models screen: each fitted in a 1 x 1 x 1
        box by its hitbox (the models are in world units, all with the same cubes)."""
        entries = []
        for kind in self.ship_models:
            entity = kind()
            name = re.sub(r"(?<=[a-z])(?=[A-Z])", " ", kind.__name__)  # MineLayer: "Mine Layer"
            entries.append((name, _fitted(self._make_model(entity), max(entity.width, entity.height))))
        for kind in [*WEAPONS, "repair"]:
            name = f"{kind.capitalize()} {LETTERS[kind]}" if kind in LETTERS else "Repair"
            entries.append((name, _fitted(self.pickup_models[kind], config.PICKUP_SIZE)))
        return entries

    def _whole_boss(self, spec: BossSpec) -> NodePath:
        """A boss with its parts in place, fitted in a 1 x 1 x 1 box like the other models."""
        whole = NodePath(spec.drawing)
        pieces = [(spec.drawing, 0.0, 0.0, spec.width, spec.height)]
        pieces += [(part.drawing, part.x, part.y, part.width, part.height) for part in spec.parts]
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

    def _world_menu(self) -> Menu:
        def pick(index: int) -> None:
            self.world_index = index
            self.states.transition(State.LEVEL_SELECT)

        items = [
            MenuItem(f"{index + 1}. {world.name}", partial(pick, index)) for index, world in enumerate(self.worlds)
        ]
        back = MenuItem("Back", lambda: self.states.transition(State.MAIN_MENU))
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

    def _label(self, index: int) -> str:
        """A level's place, like "2-5" (world 2, level 5)."""
        world, number = self.places[index]
        return f"{world + 1}-{number}"

    def _setup_hud(self) -> None:
        # All along the bottom edge: score bottom-left, the weapon levels over the health bar in the middle, lives
        # bottom-right. Each part hangs on one of Panda3D's anchors (the game area's real edges, whatever the
        # window's shape), a few hundredths from the edge.
        left = self.a2dBottomLeft.attachNewNode("hud_left")
        center = self.a2dBottomCenter.attachNewNode("hud_center")
        right = self.a2dBottomRight.attachNewNode("hud_right")
        self.hud_parts = [left, center, right]
        baseline = HUD_MARGIN + 0.01  # letters sit on it, their bottoms reach down to the margin
        self.score_text = self._hud_text(left, HUD_MARGIN, baseline, TextNode.ALeft)
        self.lives_text = self._hud_text(right, -HUD_MARGIN, baseline, TextNode.ARight)

        maker = CardMaker("health")
        maker.setFrame(0, HEALTH_BAR_WIDTH, 0, HEALTH_BAR_HEIGHT)
        bar_pos = (-HEALTH_BAR_WIDTH / 2, 0, HUD_MARGIN)
        background = center.attachNewNode(maker.generate())
        background.setPos(*bar_pos)
        background.setColor(0.3, 0.1, 0.1, 1)
        self.health_fill = center.attachNewNode(maker.generate())
        self.health_fill.setPos(*bar_pos)
        self.health_fill.setColor(0.2, 0.9, 0.3, 1)

        # Weapon levels just over the health bar, e.g. "B2  L1  M3"; the selected weapon is highlighted.
        above_bar = HUD_MARGIN + HEALTH_BAR_HEIGHT + 0.02
        self.weapon_texts = {
            weapon: self._hud_text(center, x, above_bar, TextNode.ACenter, HUD_SMALL, HUD_DIM_COLOR)
            for weapon, x in zip(WEAPONS, (-WEAPON_SPACING, 0.0, WEAPON_SPACING), strict=True)
        }

        # The boss's health bar at the top edge, its name under it: only while a boss is on screen.
        self.boss_hud = self.a2dTopCenter.attachNewNode("hud_boss")
        maker = CardMaker("boss_health")
        maker.setFrame(0, BOSS_BAR_WIDTH, -BOSS_BAR_HEIGHT, 0)
        background = self.boss_hud.attachNewNode(maker.generate())
        background.setPos(-BOSS_BAR_WIDTH / 2, 0, -HUD_MARGIN)
        background.setColor(0.25, 0.07, 0.05, 1)
        self.boss_fill = self.boss_hud.attachNewNode(maker.generate())
        self.boss_fill.setPos(-BOSS_BAR_WIDTH / 2, 0, -HUD_MARGIN)
        self.boss_fill.setColor(1.0, 0.4, 0.15, 1)
        below_bar = -HUD_MARGIN - BOSS_BAR_HEIGHT - HUD_SMALL
        self.boss_name = self._hud_text(self.boss_hud, 0.0, below_bar, TextNode.ACenter, HUD_SMALL, (1, 0.75, 0.6, 1))
        self.boss_hud.hide()

    def _hud_text(
        self,
        parent: NodePath,
        x: float,
        z: float,
        align: TextAlign,
        scale: float = HUD_TEXT,
        color: Color = (1, 1, 1, 1),
    ) -> OnscreenText:
        return OnscreenText(pos=(x, z), align=align, scale=scale, fg=color, mayChange=True, parent=parent)

    def _show_hud(self, visible: bool) -> None:
        for part in self.hud_parts:
            part.show() if visible else part.hide()
        if not visible:
            self.boss_hud.hide()

    def _make_block(self, entity: Entity) -> NodePath:
        """The entity's model in the scene (bullets are sprites, see _sync_nodes)."""
        node = self._make_model(entity)
        node.reparentTo(self.render)
        return node

    def _make_model(self, entity: Entity) -> NodePath:
        """A copy of the entity's model: models are in world units, all with the same cubes, their size from their
        drawing (about their hitbox). Copied, not instanced, so each Turret can aim its own barrel."""
        node = NodePath("entity")
        if isinstance(entity, Boss | BossPart):
            self._boss_model(entity.drawing).copyTo(node)
            return node
        model = self.pickup_models[entity.kind] if isinstance(entity, Pickup) else self.ship_models[type(entity)]
        model.copyTo(node)
        if isinstance(entity, ShieldCarrier):
            bubble = node.attachNewNode("bubble")  # the bubble fits a 1 x 1 x 1 box: stretched around the ship
            bubble.setScale(entity.width)
            self.shield_bubble.copyTo(bubble)
        return node

    def _start_level(
        self, index: int, score: int = 0, lives: int = config.PLAYER_LIVES, arsenal: Arsenal | None = None
    ) -> None:
        self.level_index = index
        screen = self.camera_view.area(0.0)  # the edges of the screen, on the play plane
        self.world = World(
            self.levels[index], score=score, lives=lives, arsenal=arsenal, view_top=screen.top, view_side=screen.right
        )
        level = self.levels[index]
        self._show_background(
            level.background, level.ground_voxel, level.time_of_day, level.background_seed, level.clouds
        )
        self._prepare_bosses(level)
        self.effects.clear()
        self.states.transition(State.PLAYING)

    def _show_background(
        self,
        kind: str,
        ground_voxel: float = GROUND_VOXEL,
        time_of_day: str = "day",
        seed: int | None = None,
        clouds: float = 0.0,
    ) -> None:
        self.background.destroy()
        scenery = Scenery(kind, self.camera_view, seed=seed, ground_voxel=ground_voxel, clouds=clouds)
        self.background = BackgroundView(scenery, self.render, time_of_day)
        biome = BIOMES.get(kind)
        _, air = TIMES_OF_DAY[time_of_day]
        red, green, blue, alpha = biome.sky if biome and biome.sky else BACKGROUND_COLOR
        sky = (red * air[0], green * air[1], blue * air[2], alpha)  # shows through gaps, like between clouds
        if self.win is not None:
            self.camNode.getDisplayRegion(0).setClearColor(sky)

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

    def _on_state_change(self, previous: State, current: State) -> None:
        if current in SHOWCASE_STATES:
            self.showcase_page = 0  # before the menu: its title shows the page
        self.menu_view.show(self._menu(current))
        if current in SHOWCASE_STATES:
            self._show_showcase()
            self.background.root.hide()  # a plain dark background, to look at the models
        elif self.showcase:
            self.showcase.destroy()
            self.showcase = None
            self.background.root.show()
        if current is State.MAIN_MENU:
            self.world = None
            self.effects.clear()
            if self.background.scenery.kind != "space":
                self._show_background("space")
        self._show_hud(self.world is not None)

    def _controls(self) -> Controls:
        return Controls(
            move_x=sum(MOVE_KEYS[key][0] for key in self.keys_down if key in MOVE_KEYS),
            move_y=sum(MOVE_KEYS[key][1] for key in self.keys_down if key in MOVE_KEYS),
            fire=FIRE_KEY in self.keys_down,
        )

    def _update(self, task: Task) -> int:
        dt = min(self.clock.getDt(), 0.1)  # avoid huge steps after a stall
        world = self.world
        if world is not None and self.states.state is State.PLAYING:
            world.update(dt, self._controls())
            self._show_events(world.events, dt)
            self.background.scenery.update(dt, world.level.scroll_speed)
            if world.game_over:
                self.states.transition(State.GAME_OVER)
            elif world.completed:
                self.states.transition(State.LEVEL_COMPLETE)
        if self.states.state in EFFECTS_RUN_IN:
            self.effects.update(dt)
        if self.showcase:
            self.showcase.update(dt)
        self._sync_nodes()
        self._update_hud()
        return Task.cont

    def _show_events(self, events: list[Event], dt: float) -> None:
        for event in events:
            if event.kind == "impact":
                # Sparks fly back the way the shot came: down from enemies, up from the player.
                self.effects.impact(event.x, event.y, towards=-1.0 if event.source == "enemy" else 1.0)
            elif event.kind == "explosion":
                colors = self.debris_colors.get(event.source, (models.METAL,))
                self.effects.explosion(event.x, event.y, event.size, colors)
            elif event.kind == "blast":
                self.effects.blast(event.x, event.y, event.size)
            elif event.kind == "burn":
                self.effects.burn(event.x, event.y, dt)

    def _sync_nodes(self) -> None:
        self.effects_view.sync()
        self.background.sync()

        entities = self.world.entities() if self.world else []
        self.bullet_sprites.show([_bullet_sprite(entity) for entity in entities if _is_round_bullet(entity)])
        entities = [entity for entity in entities if not _is_round_bullet(entity)]
        alive = set(entities)
        for entity in [entity for entity in self.nodes if entity not in alive]:
            self.nodes.pop(entity).removeNode()
            self.flames.pop(entity, None)
        for entity in entities:
            node = self.nodes.get(entity)
            if node is None:
                node = self.nodes[entity] = self._make_block(entity)
                self.flames[entity] = [(flame, flame.getSz()) for flame in node.findAllMatches("**/flame")]
            node.setPos(entity.x, 0, entity.y)
            self._flicker(entity)
            if isinstance(entity, Player):
                blink_off = entity.invulnerable and int(entity.invulnerable_time * 10) % 2 == 1
                node.hide() if blink_off else node.show()
                node.setH(-entity.vx / config.PLAYER_SPEED * PLAYER_BANK_ANGLE)  # roll around the nose axis
            elif isinstance(entity, Enemy) and self.world is not None:
                self._show_enemy_appearance(entity, node)
                self._orient_enemy(entity, node, self.world.player)
            elif isinstance(entity, Missile):
                node.setR(models.facing_roll(entity.vx, entity.vy))
            elif isinstance(entity, Pickup) and self.world is not None:
                node.setH(self.world.time * PICKUP_SPIN_SPEED)
        self._show_laser()

    def _flicker(self, entity: Entity) -> None:
        thrust = entity.vy / config.PLAYER_SPEED if isinstance(entity, Player) else 0.0
        time = self.clock.getFrameTime()
        for index, (flame, length) in enumerate(self.flames.get(entity, ())):
            flame.setSz(length * flame_scale(time, id(entity) % 97 + index * 1.7, thrust))

    def _show_laser(self) -> None:
        beam = self.world.laser if self.world else None
        if beam is None:
            self.laser_node.hide()
            return
        self.laser_node.show()
        self.laser_node.setPos(beam.x, 0, (beam.bottom + beam.top) / 2)
        self.laser_node.setScale(beam.width, beam.width, max(beam.top - beam.bottom, 0.001))

    def _show_enemy_appearance(self, enemy: Enemy, node: NodePath) -> None:
        appearance = enemy.appearance()
        if appearance == "hidden":
            node.hide()
            return
        node.show()
        if appearance == "flash":
            node.setColor(*FLASH_COLOR)
        else:
            node.clearColor()  # show the model's own colors
        shade = {"armored": ARMORED_SHADE, "hit": HIT_SHADE}.get(appearance)
        if shade:
            node.setColorScale(*shade)
        else:
            node.clearColorScale()
        if isinstance(enemy, ShieldCarrier):
            bubble = node.find("**/shield")
            bubble.show() if appearance == "shield" else bubble.hide()

    def _orient_enemy(self, enemy: Enemy, node: NodePath, player: Player) -> None:
        if isinstance(enemy, Turret):
            node.find("**/barrel").setR(models.facing_roll(player.x - enemy.x, player.y - enemy.y))
        elif isinstance(enemy, Swarmer) or (isinstance(enemy, Diver) and enemy.phase == "dive"):
            node.setR(models.facing_roll(enemy.vx, enemy.vy))  # point where it's flying
        elif isinstance(enemy, Mine):
            node.setR(enemy.age * MINE_SPIN_SPEED)

    def _update_hud(self) -> None:
        if self.world is None:
            return
        self.score_text.setText(f"Score {self.world.score}")
        self.lives_text.setText(f"Lives {self.world.lives}")
        fraction = max(self.world.player.health, 0) / config.PLAYER_HEALTH
        self.health_fill.setSx(max(fraction, 0.001))  # a zero scale makes Panda3D print warnings
        arsenal = self.world.arsenal
        for weapon, text in self.weapon_texts.items():
            text.setText(f"{LETTERS[weapon]}{arsenal.levels[weapon]}")
            selected = weapon == arsenal.selected
            text.setFg(WEAPON_COLORS[weapon] if selected else HUD_DIM_COLOR)
            text.setTextScale(HUD_SMALL * 1.25 if selected else HUD_SMALL)
        boss = self.world.boss
        if boss is None or boss.y - boss.height / 2 > self.world.view_top:  # none, or still above the screen
            self.boss_hud.hide()
            return
        self.boss_hud.show()
        self.boss_name.setText(boss.spec.name)
        self.boss_fill.setSx(max(boss.health_fraction, 0.001))


def letterbox(window_width: int, window_height: int, aspect: float = GAME_ASPECT) -> tuple[float, float, float, float]:
    """(left, right, bottom, top) of the biggest centered region of shape `aspect` (width / height) in the window,
    as fractions of the window."""
    window_aspect = window_width / max(window_height, 1)
    if window_aspect > aspect:  # too wide: bars on the left and right
        width = aspect / window_aspect
        return (1 - width) / 2, (1 + width) / 2, 0.0, 1.0
    height = window_aspect / aspect  # too tall: bars at the top and bottom
    return 0.0, 1.0, (1 - height) / 2, (1 + height) / 2


def _fitted(model: NodePath, size: float) -> NodePath:
    """A copy of a world-sized model, `size` across, fitted in a 1 x 1 x 1 box (for the Models screen)."""
    box = NodePath("fitted")
    inner = box.attachNewNode("scaled")
    inner.setScale(1 / size)
    model.copyTo(inner)
    return box


def flame_scale(time: float, phase: float, thrust: float = 0.0) -> float:
    """An engine flame's length right now, compared with its steady length: wavering, longer with `thrust` (-1 to
    1). `phase` keeps flames from wavering together."""
    slow, fast = FLAME_FLICKER
    waver = slow * math.sin(time * 23 + phase) + fast * math.sin(time * 61 + phase * 2.3)
    return max(0.1, 1 + waver + FLAME_THRUST * thrust)


def _is_round_bullet(entity: Entity) -> bool:
    return isinstance(entity, Bullet) and not isinstance(entity, Missile)


def _bullet_sprite(bullet: Entity) -> Sprite:
    """A bullet as a soft circle (an oval for the player's long bullets), a bit bigger than its hitbox: the edge
    fades out, the solid middle is about the hitbox."""
    if isinstance(bullet, Bullet) and bullet.hostile:
        color = {"sniper": SNIPER_BULLET_COLOR, "heavy": HEAVY_BULLET_COLOR}.get(bullet.style, ENEMY_BULLET_COLOR)
    else:
        color = PLAYER_BULLET_COLOR
    return Sprite(bullet.x, bullet.y, bullet.width * BULLET_GLOW, bullet.height * BULLET_GLOW, color)


def main() -> None:
    PewPewApp().run()
