"""The Dev menu's screenshots: one per world, its picture for the README, a moment of one of its levels.

Left and Right go from one world to the next, Space plays one of its levels, drawn at random, to a moment drawn at
random (`random_shot`: a ship, its weapon and their levels, maybe a secondary weapon, a time into the level or into its
first boss fight) and shows it, Enter saves the frame as the world's screenshot (docs/screenshots/world_<number>.png).
The ship weaves around the screen with the fire button held, and can't die (`steer`), so it's there for the picture.
Independent from rendering: `play` runs the level with a step the app gives.
"""

import math
import random
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from pewpy import config
from pewpy.data import SOURCE_DATA
from pewpy.game.controls import Controls
from pewpy.game.player import REGULAR_SHIPS
from pewpy.game.weapons.player.arsenal import MAX_LEVEL, WEAPONS, Arsenal
from pewpy.game.weapons.player.secondary import SECONDARY_WEAPONS, SecondaryWeapon
from pewpy.game.world import World

SCREENSHOTS = SOURCE_DATA.parent / "docs" / "screenshots"  # in the project, next to the README
STEP = 1 / 30  # seconds per step while playing to the moment (nothing is drawn in between)
LONGEST = 180.0  # seconds: a shot waiting for a boss gives up then (and is taken anyway)
DEAD_ZONE = 0.04  # how near its path's point the ship stops steering
TIMES = (8.0, 45.0)  # seconds into the level a shot is taken, at random between these...
BOSS_TIMES = (2.0, 6.0)  # ...or into the first boss fight
BOSS_SHARE = 0.25  # of the shots taken in a boss fight
SECONDARY_SHARE = 0.4  # of the shots with a secondary weapon
LOWEST_WEAPON_LEVEL = 2  # the weapons' levels are drawn from here to MAX_LEVEL


@dataclass(frozen=True)
class Shot:
    """How a level is shot."""

    ship: str
    weapon: str  # the selected one
    weapon_level: int  # of every weapon
    time: float  # seconds into the level (with `boss`: since the boss came)
    secondary: str | None = None
    phase: float = 0.0  # where the ship's path starts (radians)
    boss: bool = False  # wait for the level's first boss (the mini boss)

    def describe(self) -> str:
        """Say what the shot is."""
        when = f"{self.time:.0f} s into the boss fight" if self.boss else f"{self.time:.0f} s in"
        extra = f" + {self.secondary}" if self.secondary else ""
        return f"{REGULAR_SHIPS[self.ship].name.title()}, {self.weapon} level {self.weapon_level}{extra}, {when}"

    def arsenal(self) -> Arsenal:
        """Return the ship's weapons."""
        return Arsenal(
            levels=dict.fromkeys(WEAPONS, self.weapon_level),
            selected=self.weapon,
            secondary=SecondaryWeapon(self.secondary) if self.secondary else None,
        )


def random_shot(rng: random.Random) -> Shot:
    """Draw a shot at random."""
    boss = rng.random() < BOSS_SHARE
    return Shot(
        ship=rng.choice(list(REGULAR_SHIPS)),
        weapon=rng.choice(WEAPONS),
        weapon_level=rng.randint(LOWEST_WEAPON_LEVEL, MAX_LEVEL),
        time=rng.uniform(*(BOSS_TIMES if boss else TIMES)),
        secondary=rng.choice(list(SECONDARY_WEAPONS)) if rng.random() < SECONDARY_SHARE else None,
        phase=rng.uniform(0.0, 2 * math.pi),
        boss=boss,
    )


def steer(world: World, time: float, secondary: str | None) -> Controls:
    """Return the controls taking the ship towards its path's point at `time` (a slow figure of eight), firing.

    The ship can't die (its health is refilled), and gets its `secondary` weapon back when a hit takes it.
    """
    player = world.player
    player.health = player.ship.health
    if secondary and world.arsenal.secondary is None:
        world.arsenal.secondary = SecondaryWeapon(secondary)
    target_x = 0.38 * config.PLAY_WIDTH * math.sin(0.5 * time)
    target_y = -0.25 * config.PLAY_HEIGHT + 0.15 * config.PLAY_HEIGHT * math.sin(time)
    dx, dy = target_x - player.x, target_y - player.y
    move_x = (dx > DEAD_ZONE) - (dx < -DEAD_ZONE)
    move_y = (dy > DEAD_ZONE) - (dy < -DEAD_ZONE)
    return Controls(move_x=float(move_x), move_y=float(move_y), fire=True)


def play(world: World, shot: Shot, step: Callable[[Controls, float], None]) -> None:
    """Play `world` to the shot's moment, `step` moving it on with the controls, STEP seconds each time.

    With `boss`, it waits for the first boss (LONGEST seconds at most), then plays `time` more.
    """
    time, until = 0.0, LONGEST if shot.boss else shot.time
    waiting = shot.boss
    while time < until:
        step(steer(world, time + shot.phase, shot.secondary), STEP)
        time += STEP
        if waiting and world.boss is not None:
            waiting, until = False, time + shot.time  # the boss has come
    world.player.invulnerable_time = 0.0  # not blinking


def screenshot_path(world: int) -> Path:
    """Return where a world's screenshot is saved (`world` from 0)."""
    return SCREENSHOTS / f"world_{world + 1}.png"


def game_area(width: int, height: int, region: tuple[float, float, float, float]) -> tuple[int, int, int, int]:
    """Return the game area in a window's picture: (left, top, width, height) in pixels, from its top-left.

    `region`: (left, right, bottom, top), fractions of the window from its bottom-left (see app.window.letterbox).
    """
    left, right, bottom, top = region
    x, y = round(left * width), round((1 - top) * height)
    return x, y, round(right * width) - x, round((1 - bottom) * height) - y
