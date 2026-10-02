"""Panda3D application: window, camera, input and rendering."""

import itertools
import math
import os
import random
import sys
from collections.abc import Callable
from enum import Enum
from functools import partial
from typing import Literal, cast

from direct.gui.OnscreenText import OnscreenText
from direct.showbase.ShowBase import ShowBase
from direct.task.Task import Task
from panda3d.core import (
    ButtonThrower,
    CardMaker,
    GraphicsEngine,
    LineSegs,
    ModifierButtons,
    NodePath,
    PerspectiveLens,
    Point2,
    Point3,
    TextNode,
    Vec3,
    loadPrcFileData,
)

from pewpy import config
from pewpy.audio.cues import event_sounds, music
from pewpy.audio.library import Library, cache_folder
from pewpy.audio.sound import Audio
from pewpy.data import data_folder
from pewpy.game.bosses.boss import Boss, BossPart
from pewpy.game.bosses.catalog import BOSSES
from pewpy.game.enemies.catalog import (
    Bomber,
    Buckshot,
    Diver,
    Drone,
    FlakCannon,
    Gunship,
    Hunter,
    Lancer,
    Mine,
    MineLayer,
    MissileSilo,
    Rocketeer,
    RocketTruck,
    Serpent,
    ShieldCarrier,
    Sniper,
    Splitter,
    Swarmer,
    Tank,
    Turret,
    Weaver,
)
from pewpy.game.enemies.enemy import Enemy
from pewpy.game.enemies.fleet import FLEET
from pewpy.game.entities import Bullet, Entity, Pickup
from pewpy.game.level import Level, load_worlds
from pewpy.game.player import DEFAULT_SHIP, SHIPS, Player
from pewpy.game.states import TRANSITIONS, State, StateMachine, Transitions
from pewpy.game.weapons.enemy.projectiles import ClusterBomb, HomingMissile, Rocket
from pewpy.game.weapons.player.arsenal import LETTERS, WEAPONS, Arsenal, Missile
from pewpy.game.weapons.player.secondary import SECONDARY_LETTERS, SECONDARY_WEAPONS
from pewpy.game.world import Controls, Event, World
from pewpy.graphics import lighting, models
from pewpy.graphics.effects.blast import Blast
from pewpy.graphics.effects.burn import Burn
from pewpy.graphics.effects.explosion import Explosion
from pewpy.graphics.effects.impact import Impact
from pewpy.graphics.effects.laser import LaserGlow
from pewpy.graphics.effects_view import EffectsView
from pewpy.graphics.particle_system import ParticleSystem
from pewpy.graphics.sprites import Sprite, SpriteBatch
from pewpy.scenery.background import Scenery
from pewpy.scenery.background_view import BackgroundView, CameraView, sky_color, space_color
from pewpy.ui.level_preview import LevelPreview
from pewpy.ui.menu import Menu, MenuItem
from pewpy.ui.menu_view import MenuView
from pewpy.ui.ship_select_view import ShipSelectView

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
MUSIC_KEY = "m"  # music on and off
WEAPON_COLORS: dict[str, Color] = {
    "bullets": (1.0, 0.9, 0.2, 1),
    "laser": (0.3, 0.9, 1.0, 1),
    "missiles": (1.0, 0.6, 0.15, 1),
}
SECONDARY_COLORS: dict[str, Color] = {
    "turret": (0.45, 1.0, 0.4, 1),
    "lightning": (0.8, 0.55, 1.0, 1),
}
DISARMED_EXPLOSION_SIZE = 0.08
BOLT_COLOR: Color = (0.85, 0.75, 1.0, 1)
BOLT_THICKNESS = 3.0  # pixels
BOLT_STEP = 0.05  # a lightning bolt zigzags every this many world units...
BOLT_ZIGZAG = 0.025  # ...this far to each side, differently every frame
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
    FlakCannon: "flak_cannon_model",
    Tank: "tank_model",
    RocketTruck: "rocket_truck_model",
    Rocketeer: "rocketeer_model",
    Hunter: "hunter_model",
    MissileSilo: "missile_silo_model",
    Bomber: "bomber_model",
    Lancer: "lancer_model",
    Serpent: "serpent_model",
    Buckshot: "buckshot_model",
    Rocket: "rocket_model",
    HomingMissile: "homing_missile_model",
    ClusterBomb: "cluster_bomb_model",
}
MINE_SPIN_SPEED = 90.0  # degrees per second
# Particles keep moving after the last explosion of a level or a life (not in pause or the menus).
EFFECTS_RUN_IN: frozenset[Enum] = frozenset({State.PLAYING, State.GAME_OVER, State.LEVEL_COMPLETE})
FLASH_COLOR: Color = (1.0, 1.0, 1.0, 1)
BACKGROUND_COLOR: Color = space_color()
GAME_ASPECT = config.WINDOW_WIDTH / config.WINDOW_HEIGHT  # the game area keeps this shape (width / height)
PLAYER_BULLET_COLOR: Color = (0.3, 1.0, 0.25, 1)  # bright green
ENEMY_BULLET_COLOR: Color = (1.0, 0.5, 0.9, 1)
SNIPER_BULLET_COLOR: Color = (0.4, 0.6, 1.0, 1)
HEAVY_BULLET_COLOR: Color = (1.0, 0.55, 0.15, 1)  # big shots: bosses, Rocket Trucks
LASER_FLICKER = 0.12  # the player's laser beam's width flickers by this share
BEAM_COLOR: Color = (1.0, 0.35, 0.25, 1)  # the Lancer's laser beam
WAVE_BULLET_COLOR: Color = (0.75, 0.45, 1.0, 1)  # the Serpent's snaking shots
ACCEL_BULLET_COLOR: Color = (0.3, 0.95, 1.0, 1)  # bosses' shots speeding up
CURVE_BULLET_COLOR: Color = (1.0, 0.9, 0.3, 1)  # bosses' shots on bending paths
WARNING_BEAM_COLOR: Color = (1.0, 0.35, 0.25, 0.6)  # a boss's laser about to fire: thin, harmless
BULLET_COLORS: dict[str, Color] = {
    "sniper": SNIPER_BULLET_COLOR,
    "heavy": HEAVY_BULLET_COLOR,
    "beam": BEAM_COLOR,
    "warning": WARNING_BEAM_COLOR,
    "wave": WAVE_BULLET_COLOR,
    "accel": ACCEL_BULLET_COLOR,
    "curve": CURVE_BULLET_COLOR,
}  # by Bullet.style; enemy shots of any other style (the Buckshot's pellets too) are pink
ARMORED_SHADE: Color = (0.55, 0.55, 0.62, 1)  # a boss's core, darker while shots bounce off it
HIT_SHADE: Color = (1.6, 1.6, 1.6, 1)  # bosses light up when hit (white would hide them: they're shot all the time)
BULLET_GLOW = 1.8  # a bullet's sprite, compared with its hitbox
MAX_BULLETS = 512
HUD_MARGIN = 0.025  # space between the HUD and the edges of the game area (aspect2d units: the width is 2)
HUD_TEXT = 0.06  # score and lives
HUD_SMALL = 0.055  # weapon levels (the selected one is bigger)
FPS_SCALE = 0.045
FPS_REFRESH = 0.5  # seconds between two updates of the frames per second
WEAPON_SPACING = 0.15
HEALTH_BAR_WIDTH = 0.5
HEALTH_BAR_HEIGHT = 0.025
BOSS_BAR_WIDTH = 1.1  # at the top edge, with the boss's name under it
BOSS_BAR_HEIGHT = 0.025
PLAYER_BANK_ANGLE = 25.0  # degrees of roll at full sideways speed
FLAME_FLICKER = (0.12, 0.08)  # how much engine flames waver in length: a slow wave and a fast one
FLAME_THRUST = 0.35  # the player's flames: this much longer flying up at full speed, shorter flying down


class PewPewApp(ShowBase):
    """The game. The dev tools (pewpewdev.app) add screens of their own through `state_transitions`, `effects_run_in`,
    `_main_menu_items`, `_setup_screens` and the methods they override."""

    state_transitions: Transitions = TRANSITIONS
    effects_run_in: frozenset[Enum] = EFFECTS_RUN_IN

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
        self.ship_key = DEFAULT_SHIP  # the player's ship (picked on the ship selection screen)
        self.ship_select: ShipSelectView | None = None
        self.laser_node = models.laser_beam_model()
        self.laser_node.reparentTo(self.render)
        self.laser_node.hide()
        self.bolt_node = self.render.attachNewNode("bolt")
        self.bolt_rng = random.Random()  # noqa: S311 - looks only

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
        self.effects = ParticleSystem()
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
        self._setup_audio()
        self.accept(MUSIC_KEY, self.audio.toggle_music)

        self.menu_view = MenuView(self.aspect2d)
        self._setup_hud()
        # The level select's window on the highlighted level.
        self.level_preview = LevelPreview(self.win, self.cam, self.render, self.aspect2d)
        self._fit_letterbox()
        self._setup_screens()

        self.states = StateMachine(on_change=self._on_state_change, transitions=self.state_transitions)
        self._on_state_change(self.states.state, self.states.state)
        self.taskMgr.add(self._update, "update")

    def _setup_screens(self) -> None:
        """Set up more screens before the first one shows (the dev tools' screens)."""

    def _disable_modifier_keys(self) -> None:
        # By default Panda3D sends "shift-space" instead of "space" while Shift is held, which would stop
        # firing when switching weapons. Treat Shift like any other key.
        if self.mouseWatcher is None:  # no window, e.g. offscreen
            return
        for path in self.mouseWatcher.findAllMatches("**/+ButtonThrower"):
            cast(ButtonThrower, path.node()).setModifierButtons(ModifierButtons())
        self.mouseWatcherNode.setModifierButtons(ModifierButtons())

    def _switch_weapon(self) -> None:
        if self.world is not None and self.states.state is State.PLAYING:
            self.world.arsenal.switch()
            self.audio.play("switch")

    def _setup_audio(self) -> None:
        library = Library(data_folder() / "music", cache_folder())
        manager = self.sfxManagerList[0] if self.sfxManagerList else None
        self.audio = Audio(self.loader, manager, self.musicManager, library)
        # Rendered in the background in the order they're likely needed (once: they're kept on disk).
        library.request("title", first=False)
        for index in range(len(self.worlds)):
            library.request(f"world_{index + 1}", first=False)
        library.request("boss", first=False)
        library.request("level_complete", loop=False, first=False)
        library.request("game_over", loop=False, first=False)

    def _update_audio(self, dt: float) -> None:
        world, state = self.world, self.states.state
        self.audio.set_laser(world is not None and state is State.PLAYING and world.laser is not None)
        boss = world is not None and (world.boss is not None or world.boss_beaten)
        self.audio.set_music(music(state, self.places[self.level_index][0], boss), quiet=state is State.PAUSED)
        self.audio.update(dt)

    def finalizeExit(self) -> None:
        """Under WSL, the GPU goes through Mesa's d3d12 driver (see `make run`), which can hang while the window is
        torn down: leave at once instead (nothing is left to save).
        """
        if os.environ.get("GALLIUM_DRIVER") == "d3d12":
            sys.stdout.flush()
            sys.stderr.flush()
            os._exit(0)
        super().finalizeExit()

    def _setup_letterbox(self) -> None:
        # The game keeps its 3:4 shape whatever the window size: the 3D view and the HUD are drawn in a centered
        # region, with black bars around it. The window clears to black, the region to the space color.
        self.win.setClearColor((0, 0, 0, 1))
        region = self.camNode.getDisplayRegion(0)
        region.setClearColorActive(True)
        region.setClearColor(BACKGROUND_COLOR)
        self._fit_letterbox()

    def _fit_letterbox(self) -> None:
        if not self.win.hasSize():
            return
        dimensions = letterbox(self.win.getXSize(), self.win.getYSize())
        for camera in (self.cam, self.cam2d, self.cam2dp):
            node = camera.node()
            for index in range(node.getNumDisplayRegions()):
                node.getDisplayRegion(index).setDimensions(*dimensions)
        preview = getattr(self, "level_preview", None)  # not made yet when the window first opens
        if preview is not None:
            preview.fit(dimensions)

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
        lighting.setup(self)

    def _on_key(self, key: str) -> None:
        self.keys_down.add(key)
        menu = self.menu_view.menu
        if menu is not None and key in MENU_MOVES:
            menu.move(MENU_MOVES[key])
            self.audio.play("menu_move")
            self.menu_view.refresh()
            self._highlight_ship()
            if self.states.state is State.LEVEL_SELECT:
                self._preview_level(menu)

    def _on_choose(self) -> None:
        if self.menu_view.menu is not None:
            self.audio.play("menu_choose")
            self.menu_view.menu.choose()

    def _on_back(self) -> None:
        if self.menu_view.menu is not None:
            self.audio.play("menu_back")
            self.menu_view.menu.go_back()
        elif self.states.state is State.PLAYING:
            self.audio.play("menu_back")
            self.states.transition(State.PAUSED)

    def _go(self, target: Enum) -> Callable[[], None]:
        return lambda: self.states.transition(target)

    def _main_menu_items(self) -> list[MenuItem]:
        """The main menu's items, but "Quit" (the last one)."""
        return [MenuItem("Start", self._go(State.SHIP_SELECT))]

    def _menu(self, state: Enum) -> Menu | None:
        """The menu shown in each state (None while playing)."""
        go = self._go
        main_menu = MenuItem("Main menu", go(State.MAIN_MENU))
        if state is State.MAIN_MENU:
            return Menu("PEWPEW", [*self._main_menu_items(), MenuItem("Quit", self.userExit)])
        if state is State.SHIP_SELECT:
            return self._ship_menu()
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

    def _build_models(self) -> None:
        """Build every model from models.py (looked up by name, so a reloaded models.py is used)."""
        self.ship_models = {kind: getattr(models, name)() for kind, name in SHIP_MODELS.items()}
        self.ship_models.update({kind: models.drawing_model(kind.drawing) for kind in FLEET.values()})
        # Explosions throw debris in the colors of what blew up.
        self.debris_colors = {kind.__name__: models.main_colors(model) for kind, model in self.ship_models.items()}
        self.shield_bubble = models.shield_bubble_model()
        self.pickup_models = {weapon: models.pickup_model(LETTERS[weapon], WEAPON_COLORS[weapon]) for weapon in WEAPONS}
        self.pickup_models["repair"] = models.repair_model()
        self.pickup_models["life"] = models.extra_life_model()
        for kind in SECONDARY_WEAPONS:
            self.pickup_models[kind] = models.pickup_model(SECONDARY_LETTERS[kind], SECONDARY_COLORS[kind])
        self.secondary_models = {"turret": models.gun_turret_model(), "lightning": models.lightning_coil_model()}
        self.player_models = {spec.drawing: models.drawing_model(spec.drawing) for spec in SHIPS.values()}
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

    def _ship_menu(self) -> Menu:
        def pick(key: str) -> None:
            self.ship_key = key
            self.states.transition(State.WORLD_SELECT)

        items = [MenuItem(spec.name.title(), partial(pick, key)) for key, spec in SHIPS.items()]
        back = MenuItem("Back", lambda: self.states.transition(State.MAIN_MENU))
        # Starts on the ship played last.
        return Menu("SELECT SHIP", [*items, back], back=back.action, selected=list(SHIPS).index(self.ship_key))

    def _show_ship_select(self) -> None:
        """Every ship side by side under the menu, with bars comparing them."""
        ships = list(SHIPS.values())
        fitted = [fitted_model(self.player_models[ship.drawing], ship.size) for ship in ships]
        lens = self.cam.node().getLens()
        extent = (self.a2dRight, self.a2dTop)
        self.ship_select = ShipSelectView(ships, fitted, self.cam, lens, self.aspect2d, extent)
        self._highlight_ship()

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
        # Frames per second, top-right on every screen (not part of the in-game HUD, which menus hide).
        fps_corner = self.a2dTopRight.attachNewNode("fps")
        top_line = -HUD_MARGIN - FPS_SCALE * 0.8  # the letters' tops reach up to the margin
        self.fps_text = self._hud_text(fps_corner, -HUD_MARGIN, top_line, TextNode.ARight, FPS_SCALE, HUD_DIM_COLOR)
        self._fps_shown = -1
        self._fps_next = 1.0  # the clock averages over the last second: nothing to show before
        if not config.SHOW_FPS:
            fps_corner.hide()

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
        # The secondary weapon after them, if the ship carries one: "+T" or "+Z".
        self.secondary_text = self._hud_text(center, 2 * WEAPON_SPACING, above_bar, TextNode.ACenter, HUD_SMALL * 1.25)

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
        # What's currently shown, so _update_hud only touches a text (Panda3D rebuilds its geometry each time)
        # when its value actually changed, instead of every single frame.
        self._hud_score: int | None = None
        self._hud_lives: int | None = None
        self._hud_weapon_state: dict[str, tuple[int, bool]] = {}
        self._hud_secondary: str | None = None
        self._hud_boss_name: str | None = None
        self._hud_boss_visible = False

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
        drawing (about their hitbox). Copied, not instanced, so each Turret can aim its own barrel.
        """
        node = NodePath("entity")
        if isinstance(entity, Boss | BossPart):
            self._boss_model(entity.drawing).copyTo(node)
            return node
        if isinstance(entity, Player):
            self.player_models[entity.ship.drawing].copyTo(node)
            bounds = node.getTightBounds()
            front = bounds[0].y if bounds else 0.0  # the secondary weapons sit on top of the ship, hidden until carried
            for kind, model in self.secondary_models.items():
                mount = node.attachNewNode(f"secondary_{kind}")
                mount.setY(front)
                model.copyTo(mount)
                mount.hide()
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
            self.levels[index],
            score=score,
            lives=lives,
            arsenal=arsenal,
            view_top=screen.top,
            view_side=screen.right,
            ship=SHIPS[self.ship_key],
        )
        level = self.levels[index]
        self._show_background(level)
        self._prepare_bosses(level)
        self.effects.clear()
        self.states.transition(State.PLAYING)

    def _show_background(self, level: Level | None = None) -> None:
        """A level's scenery (none: space, behind the menus)."""
        self.background.destroy()
        if level is None:
            scenery = Scenery("space", self.camera_view)
            time_of_day = "day"
        else:
            scenery = Scenery(
                level.scenery_params(),
                self.camera_view,
                seed=level.background_seed,
                clouds=level.clouds,
            )
            time_of_day = level.time_of_day
        self.background = BackgroundView(scenery, self.render, time_of_day)
        # The sky shows through gaps, like between clouds.
        self.camNode.getDisplayRegion(0).setClearColor(sky_color(scenery.params, time_of_day))

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

    def _on_state_change(self, previous: Enum, current: Enum) -> None:
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
            if self.background.scenery.kind != "space":
                self._show_background()
        self._show_hud(self.world is not None)

    def _controls(self) -> Controls:
        return Controls(
            move_x=sum(MOVE_KEYS[key][0] for key in self.keys_down if key in MOVE_KEYS),
            move_y=sum(MOVE_KEYS[key][1] for key in self.keys_down if key in MOVE_KEYS),
            fire=FIRE_KEY in self.keys_down,
        )

    def _frame_time(self) -> float:
        """Seconds since the last frame (at most 0.1: no huge steps after a stall)."""
        return min(self.clock.getDt(), 0.1)

    def _update(self, task: Task) -> int:
        dt = self._frame_time()
        world = self.world
        if world is not None and self.states.state is State.PLAYING:
            self._play(world, self._controls(), dt)
            if world.game_over:
                self.states.transition(State.GAME_OVER)
            elif world.completed:
                self.states.transition(State.LEVEL_COMPLETE)
        if self.states.state in self.effects_run_in:
            self.effects.update(dt)
        if self.ship_select:
            self.ship_select.update(dt)
        self.level_preview.update(dt)
        self._update_audio(dt)
        self._sync_nodes()
        self._update_hud()
        self._update_fps()
        return Task.cont

    def _play(self, world: World, controls: Controls, dt: float) -> None:
        """One step of a level: the world, its effects, sounds and scenery."""
        world.update(dt, controls)
        self._show_events(world.events, dt)
        self.audio.play_all(event_sounds(world.events))
        self.effects.set_laser(self._laser_glow(world), dt)
        self.background.scenery.update(dt, world.level.scroll_speed)

    def _show_events(self, events: list[Event], dt: float) -> None:
        for event in events:
            if event.kind == "impact":
                # Sparks fly back the way the shot came: down from enemies, up from the player.
                self.effects.play(Impact(event.x, event.y, towards=-1.0 if event.source == "enemy" else 1.0))
            elif event.kind == "explosion":
                colors = self.debris_colors.get(event.source, (models.METAL,))
                self.effects.play(Explosion(event.x, event.y, event.size, colors))
            elif event.kind == "blast":
                self.effects.play(Blast(event.x, event.y, event.size))
            elif event.kind == "burn":
                self.effects.play(Burn(event.x, event.y, dt))
            elif event.kind == "disarmed":  # the secondary weapon blew up on the ship
                colors = (SECONDARY_COLORS[event.source], models.METAL)
                self.effects.play(Explosion(event.x, event.y, DISARMED_EXPLOSION_SIZE, colors))

    def _sync_nodes(self) -> None:
        self.effects_view.sync()
        self.background.sync()

        world = self.world
        entities = world.entities() if world else []
        self.bullet_sprites.show([_bullet_sprite(entity) for entity in entities if _is_round_bullet(entity)])
        entities = [entity for entity in entities if not _is_round_bullet(entity)]
        alive = set(entities)
        for entity in [entity for entity in self.nodes if entity not in alive]:
            self.nodes.pop(entity).removeNode()
            self.flames.pop(entity, None)
        if world is not None:
            self._show_entities(world, entities)
        self._show_laser()
        self._show_bolt()

    def _show_entities(self, world: World, entities: list[Entity]) -> None:
        """Place the models of what's on screen (all but the round bullets), each turned and shaded as it is now."""
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
                node.setH(-entity.vx / entity.ship.speed * PLAYER_BANK_ANGLE)  # roll around the nose axis
                self._show_secondary(node)
            elif isinstance(entity, Enemy):
                self._show_enemy_appearance(entity, node)
                self._orient_enemy(entity, node, world.player)
            elif isinstance(entity, Missile):
                node.setR(models.facing_roll(entity.vx, entity.vy))
            else:  # a pickup
                node.setH(world.time * PICKUP_SPIN_SPEED)

    def _show_secondary(self, ship: NodePath) -> None:
        secondary = self.world.arsenal.secondary if self.world else None
        for kind in SECONDARY_WEAPONS:
            mount = ship.find(f"secondary_{kind}")
            mount.show() if secondary is not None and secondary.kind == kind else mount.hide()
        if secondary is not None and secondary.kind == "turret":
            ship.find("secondary_turret/**/barrel").setR(models.facing_roll(secondary.aim_x, secondary.aim_y))

    def _show_bolt(self) -> None:
        """The lightning gun's last strike, while it shows: a zigzag line, redrawn every frame so it crackles."""
        self.bolt_node.getChildren().detach()
        points = self.world.bolt if self.world else []
        if len(points) < 2:
            return
        lines = LineSegs("bolt")
        lines.setThickness(BOLT_THICKNESS)
        lines.setColor(*BOLT_COLOR)
        lines.moveTo(points[0][0], 0, points[0][1])
        for (x0, z0), (x1, z1) in itertools.pairwise(points):
            length = math.hypot(x1 - x0, z1 - z0)
            steps = max(1, round(length / BOLT_STEP))
            side_x, side_z = (-(z1 - z0) / length, (x1 - x0) / length) if length else (0.0, 0.0)
            for step in range(1, steps + 1):
                along = step / steps
                zig = self.bolt_rng.uniform(-BOLT_ZIGZAG, BOLT_ZIGZAG) if step < steps else 0.0
                lines.drawTo(x0 + (x1 - x0) * along + side_x * zig, 0, z0 + (z1 - z0) * along + side_z * zig)
        bolt = self.bolt_node.attachNewNode(lines.create())
        bolt.setLightOff()
        bolt.setShaderOff()
        bolt.setBin("fixed", 0)
        bolt.setDepthTest(False)
        bolt.setDepthWrite(False)

    def _flicker(self, entity: Entity) -> None:
        thrust = entity.vy / entity.ship.speed if isinstance(entity, Player) else 0.0
        time = self.clock.getFrameTime()
        for index, (flame, length) in enumerate(self.flames.get(entity, ())):
            flame.setSz(length * flame_scale(time, id(entity) % 97 + index * 1.7, thrust))

    @staticmethod
    def _laser_glow(world: World) -> LaserGlow | None:
        beam = world.laser
        if beam is None:
            return None
        hits = tuple(event.y for event in world.events if event.kind == "burn")
        return LaserGlow(beam.x, beam.bottom, beam.top, beam.width, hits)

    def _show_laser(self) -> None:
        beam = self.world.laser if self.world else None
        if beam is None:
            self.laser_node.hide()
            return
        self.laser_node.show()
        self.laser_node.setPos(beam.x, 0, (beam.bottom + beam.top) / 2)
        width = beam.width * (1.0 + LASER_FLICKER * math.sin(self.clock.getFrameTime() * 53.0))
        self.laser_node.setScale(width, width, max(beam.top - beam.bottom, 0.001))

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
        if isinstance(enemy, Turret | Tank):
            node.find("**/barrel").setR(models.facing_roll(player.x - enemy.x, player.y - enemy.y))
        elif isinstance(enemy, Swarmer | Rocket | HomingMissile) or (
            (isinstance(enemy, Diver) and enemy.phase == "dive") or (enemy.faces_travel and (enemy.vx or enemy.vy))
        ):
            node.setR(models.facing_roll(enemy.vx, enemy.vy))  # point where it's flying
        elif isinstance(enemy, Mine | ClusterBomb):
            node.setR(enemy.age * MINE_SPIN_SPEED)

    def _update_fps(self) -> None:
        """Averaged over the last second, rewritten twice a second at most (setText rebuilds the text)."""
        now = self.clock.getFrameTime()
        if not config.SHOW_FPS or now < self._fps_next:
            return
        self._fps_next = now + FPS_REFRESH
        fps = round(self.clock.getAverageFrameRate())
        if fps != self._fps_shown:
            self._fps_shown = fps
            self.fps_text.setText(f"{fps} FPS")

    def _update_hud(self) -> None:
        if self.world is None:
            return
        if self.world.score != self._hud_score:
            self._hud_score = self.world.score
            self.score_text.setText(f"Score {self.world.score}")
        if self.world.lives != self._hud_lives:
            self._hud_lives = self.world.lives
            self.lives_text.setText(f"Lives {self.world.lives}")
        fraction = max(self.world.player.health, 0) / self.world.ship.health
        self.health_fill.setSx(max(fraction, 0.001))  # a zero scale makes Panda3D print warnings
        self._update_weapons_hud(self.world.arsenal)
        boss = self.world.boss
        if boss is None or boss.y - boss.height / 2 > self.world.view_top:  # none, or still above the screen
            if self._hud_boss_visible:
                self.boss_hud.hide()
                self._hud_boss_visible = False
            return
        if not self._hud_boss_visible:
            self.boss_hud.show()
            self._hud_boss_visible = True
        if boss.spec.name != self._hud_boss_name:
            self._hud_boss_name = boss.spec.name
            self.boss_name.setText(boss.spec.name)
        self.boss_fill.setSx(max(boss.health_fraction, 0.001))

    def _update_weapons_hud(self, arsenal: Arsenal) -> None:
        for weapon, text in self.weapon_texts.items():
            selected = weapon == arsenal.selected
            state = (arsenal.levels[weapon], selected)
            if self._hud_weapon_state.get(weapon) == state:
                continue  # setText/setFg/setTextScale rebuild the text's geometry: skip when nothing changed
            self._hud_weapon_state[weapon] = state
            text.setText(f"{LETTERS[weapon]}{arsenal.levels[weapon]}")
            text.setFg(WEAPON_COLORS[weapon] if selected else HUD_DIM_COLOR)
            text.setTextScale(HUD_SMALL * 1.25 if selected else HUD_SMALL)
        secondary = arsenal.secondary.kind if arsenal.secondary else None
        if secondary != self._hud_secondary:
            self._hud_secondary = secondary
            self.secondary_text.setText(f"+{SECONDARY_LETTERS[secondary]}" if secondary else "")
            if secondary:
                self.secondary_text.setFg(SECONDARY_COLORS[secondary])


def letterbox(window_width: int, window_height: int, aspect: float = GAME_ASPECT) -> tuple[float, float, float, float]:
    """(left, right, bottom, top) of the biggest centered region of shape `aspect` (width / height) in the window,
    as fractions of the window.
    """
    window_aspect = window_width / max(window_height, 1)
    if window_aspect > aspect:  # too wide: bars on the left and right
        width = aspect / window_aspect
        return (1 - width) / 2, (1 + width) / 2, 0.0, 1.0
    height = window_aspect / aspect  # too tall: bars at the top and bottom
    return 0.0, 1.0, (1 - height) / 2, (1 + height) / 2


def fitted_model(model: NodePath, size: float) -> NodePath:
    """A copy of a world-sized model, `size` across, fitted in a 1 x 1 x 1 box (for the ship select, and the dev
    tools' Models screen)."""
    box = NodePath("fitted")
    inner = box.attachNewNode("scaled")
    inner.setScale(1 / size)
    model.copyTo(inner)
    return box


def flame_scale(time: float, phase: float, thrust: float = 0.0) -> float:
    """An engine flame's length right now, compared with its steady length: wavering, longer with `thrust` (-1 to
    1). `phase` keeps flames from wavering together.
    """
    slow, fast = FLAME_FLICKER
    waver = slow * math.sin(time * 23 + phase) + fast * math.sin(time * 61 + phase * 2.3)
    return max(0.1, 1 + waver + FLAME_THRUST * thrust)


def _is_round_bullet(entity: Entity) -> bool:
    return isinstance(entity, Bullet) and not isinstance(entity, Missile)


def _bullet_sprite(bullet: Entity) -> Sprite:
    """A bullet as a soft circle (an oval for the player's long bullets), a bit bigger than its hitbox: the edge
    fades out, the solid middle is about the hitbox.
    """
    if isinstance(bullet, Bullet) and bullet.hostile:
        color = BULLET_COLORS.get(bullet.style, ENEMY_BULLET_COLOR)
        if bullet.style in ("beam", "warning"):  # as long as the beam itself: only its sides fade out
            return Sprite(bullet.x, bullet.y, bullet.width * BULLET_GLOW, bullet.height, color)
    else:
        color = PLAYER_BULLET_COLOR
    return Sprite(bullet.x, bullet.y, bullet.width * BULLET_GLOW, bullet.height * BULLET_GLOW, color)


def main() -> None:
    PewPewApp().run()
