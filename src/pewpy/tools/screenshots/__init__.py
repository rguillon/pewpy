"""Take one screenshot of every world, for the README: docs/screenshots/world_<number>.png.

The game runs without a window (drawing offscreen), silent. Each world is shot in its own way (`SHOTS`): one of its
levels, a moment of it (a boss for some), a ship, its weapon and their levels, a secondary weapon or not. The ship
weaves around the screen with the fire button held, and can't die (its health is refilled every step), so it's there
for the picture; the frame is saved with the HUD.
"""

import math
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from direct.task.Task import Task
from panda3d.core import Filename, loadPrcFileData

from pewpy import config
from pewpy.app import PewPewApp
from pewpy.app.keys import FIRE_KEY, MOVE_KEYS
from pewpy.audio.library import Library
from pewpy.game.states import State
from pewpy.game.weapons.player.arsenal import WEAPONS, Arsenal
from pewpy.game.weapons.player.secondary import SecondaryWeapon

STEP = 1 / 30  # seconds per step of the game (nothing is drawn between two screenshots)
DEAD_ZONE = 0.04  # how near its target the ship stops steering
LONGEST = 180.0  # seconds: a shot waiting for a boss gives up then (and is taken anyway)


@dataclass(frozen=True)
class Shot:
    """How a world is shot."""

    level: int  # its number in the world, from 1
    time: float  # seconds into the level (with `boss`: since the boss came)
    ship: str
    weapon: str  # the selected one
    weapon_level: int  # of every weapon
    secondary: str | None = None
    phase: float = 0.0  # where the ship's path starts (radians)
    boss: bool = False  # wait for the level's first boss (the mini boss)


SHOTS = (  # one per world, in order
    Shot(2, 14.0, "vanguard", "bullets", 3),
    Shot(3, 22.0, "phantom", "laser", 4, "turret", phase=1.5),
    Shot(4, 42.0, "juggernaut", "missiles", 4, "lightning", phase=3.0),
    Shot(2, 3.0, "vanguard", "laser", 2, phase=4.5, boss=True),
    Shot(5, 18.0, "juggernaut", "bullets", 5, "turret", phase=0.8),
    Shot(5, 44.0, "phantom", "missiles", 5, phase=2.2),
    Shot(6, 26.0, "vanguard", "bullets", 4, "lightning", phase=3.7),
    Shot(4, 4.0, "juggernaut", "bullets", 3, "turret", phase=5.2, boss=True),
)


class ScreenshotApp(PewPewApp):
    """The game, offscreen and silent, its steps all the same length however slow the drawing."""

    def __init__(self) -> None:
        loadPrcFileData(
            "", "window-type offscreen\nload-display p3headlessgl\naudio-library-name null\nsync-video false"
        )
        Library.request = lambda *_, **__: None  # no songs rendered
        super().__init__()
        self.fps_text.hide()  # the frames per second of the offscreen drawing mean nothing

    def _frame_time(self) -> float:
        return STEP

    def shoot(self, world: int, shot: Shot, path: Path) -> None:
        """Play world `world` (from 0) as `shot` says, then save the frame to `path`."""
        self.ship_key = shot.ship
        self._go_to(State.MAIN_MENU)  # wherever the last level ended
        for state in (State.SHIP_SELECT, State.WORLD_SELECT, State.LEVEL_SELECT):
            self.states.transition(state)
        arsenal = Arsenal(
            levels=dict.fromkeys(WEAPONS, shot.weapon_level),
            selected=shot.weapon,
            secondary=SecondaryWeapon(shot.secondary) if shot.secondary else None,
        )
        self._start_level(self.places.index((world, shot.level)), arsenal=arsenal)
        time, until = 0.0, LONGEST if shot.boss else shot.time
        waiting = shot.boss
        while time < until:
            self._steer(time + shot.phase, shot.secondary)
            self._update(Task())
            time += STEP
            if waiting and self.world is not None and self.world.boss is not None:
                waiting, until = False, time + shot.time  # the boss has come
        if self.world is not None:
            self.world.player.invulnerable_time = 0.0  # not blinking
            self._sync_nodes()
        self.graphicsEngine.renderFrame()
        self.graphicsEngine.renderFrame()  # the 3D view's buffer is drawn in a frame, the window shows it the next
        self.win.saveScreenshot(Filename.fromOsSpecific(str(path)))

    def _steer(self, time: float, secondary: str | None) -> None:
        """Hold the keys taking the ship towards its path's point at `time` (a slow figure of eight), and fire.

        The ship can't die, and gets its `secondary` weapon back when a hit takes it.
        """
        self.keys_down.clear()
        self.keys_down.add(FIRE_KEY)
        world = self.world
        if world is None:
            return
        player = world.player
        player.health = player.ship.health
        if secondary and world.arsenal.secondary is None:
            world.arsenal.secondary = SecondaryWeapon(secondary)
        target_x = 0.38 * config.PLAY_WIDTH * math.sin(0.5 * time)
        target_y = -0.25 * config.PLAY_HEIGHT + 0.15 * config.PLAY_HEIGHT * math.sin(time)
        for key, (dx, dy) in MOVE_KEYS.items():
            if (dx and dx * (target_x - player.x) > DEAD_ZONE) or (dy and dy * (target_y - player.y) > DEAD_ZONE):
                self.keys_down.add(key)

    def _go_to(self, state: Enum) -> None:
        previous, self.states.state = self.states.state, state
        self._on_state_change(previous, state)
