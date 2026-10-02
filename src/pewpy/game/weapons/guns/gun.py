"""What a gun is: data, read from the YAML files.

The player's weapons are in `data/weapons/`, the enemies' with them (see pewpy.game.enemies.spec).
"""

import re
from dataclasses import dataclass
from typing import Any

from pewpy import config

Distance = float | str  # see `distance`


@dataclass(frozen=True)
class Gun:
    """How one gun fires. Angles in degrees; 0 is straight ahead (down for enemies, up for the player).

    pattern: "aimed" (at the target), "fan" (around straight ahead), "ring" (all around), "laser" (a boss's beams
    straight down, following it), "beam" (a beam straight down from the muzzle, for `duration` seconds), "ray" (the
    player's laser: `width` wide, `damage` per second, through every enemy if it `pierces`, else up to the first
    one) or "chain" (lightning: strikes the nearest target within `chain_range`, then the nearest one not struck yet
    within `chain_jump` of the last, `chain_count` at most, `damage` each; the bolt shows `flash` seconds). `count`
    shots `spread` degrees apart (a ring spreads them evenly), or one shot per `angles` (from the pattern's middle);
    all turned by `angle`. Every `interval` seconds, `volley` times in a row `gap` seconds apart; the volley's shots
    are also turned by `volley_angles` (the first shot by the first one, and so on). Each time it fires, the pattern
    turns by `turn` degrees (a ring firing fast with a turn is a spiral). `sweep`: a fan's middle swings that far left
    and right. `delay`: the first shot waits that much more, so guns take turns. `speeds`: each shot's own speed, in
    turn, instead of `speed`; `velocities`: each shot's (vx, vy), instead of a pattern.

    It fires from each of its `origins`: (x, y) from the middle of what carries it (see `distance`). `sequence`:
    guns whose patterns are fired in turn, one per volley (this gun only times them).

    `style`: "normal", "sniper" (blue), "heavy" (bigger, orange), "pellet" (small), "wave" (violet, snaking across its
    line of flight), "accel" (cyan, starts slow and speeds up) or "curve" (yellow, its path bends by `curve` degrees per
    second for CURVE_TIME seconds, see pewpy.game.weapons.bullets.curve). Its shots do `damage` (None:
    config.ENEMY_BULLET_DAMAGE) and are `size` (width, height; None: by style). `bullet`: "missile" for the player's
    missiles, homing at `homing` degrees per second (0: not homing), blowing up enemies within `splash_radius` too
    (`splash` damage each).

    Instead of bullets it can launch enemies: `projectile` ("rocket", "missile" (homing) or "cluster", see
    PROJECTILES, flying the shot's way) or `spawn` (any kind of enemy). A spawned enemy flies the shot's way at
    `spawn_speed`, or at `spawn_velocity` (its x turned round on the left of the middle), or as it would on its own;
    `spawn_heading` turns it (degrees, counterclockwise from the right); with `spawn_fuse`, its first timer is set so
    it gets where the player is now.

    A laser fires one beam per `offsets` (x from the gun's middle), `width` wide, for `duration` seconds, each
    announced by a thin harmless beam LASER_WARNING seconds before; the beams follow the gun as the boss sways.

    When to fire: while its trigger is held (always, for enemies), when `interval` has gone by ("reset": counted again
    from then; "carry": what it was late by is taken off the next wait; "clamp": the wait never goes below 0, so it
    doesn't make up for the time it had nothing to fire at). `needs_target`: it only fires at a target (the nearest
    enemy, for the player's guns). `off_screen`: "hold" (the shot waits until it's on screen), "skip" (that shot is
    skipped) or "fire". `aligned`: it fires only within that of the player's column. `staggered`: the first wait is the
    enemy's own (set when it's placed). `charge`: seconds of glowing before it fires (the wait starts again after);
    `hold`: the enemy stands still while charging and while its beam lasts. `wait_volley`: no reloading during a volley,
    which starts on the next frame (a volley of one fires at once). `at`: fires once, when the state has that many
    seconds left. `window`: fires every `gap` seconds during the first `window` seconds of each `interval` of the state,
    sweeping from `-reach` to `reach` degrees (the other way round every other time).
    """

    pattern: str
    interval: float
    speed: float
    count: int = 1
    spread: float = 15.0
    volley: int = 1
    gap: float = 0.15
    turn: float = 0.0
    sweep: float = 0.0
    delay: float = 0.0
    style: str = "normal"
    curve: float = 0.0
    projectile: str = ""
    width: float = 0.06
    duration: float = 1.0
    offsets: tuple[float, ...] = (0.0,)
    angle: float = 0.0
    angles: tuple[float, ...] = ()
    speeds: tuple[float, ...] = ()
    velocities: tuple[tuple[float, float], ...] = ()
    volley_angles: tuple[float, ...] = ()
    origins: tuple[tuple[Distance, Distance], ...] = ((0.0, 0.0),)
    sequence: tuple["Gun", ...] = ()
    spawn: str = ""
    spawn_speed: float | None = None
    spawn_velocity: tuple[float, float] | None = None
    spawn_heading: float | None = None
    spawn_fuse: bool = False
    reload: str = "reset"
    off_screen: str = "hold"
    aligned: float = 0.0
    staggered: bool = False
    charge: float = 0.0
    hold: bool = False
    wait_volley: bool = False
    at: float | None = None
    window: float = 0.0
    reach: float = 0.0
    damage: float | None = None
    size: tuple[float, float] | None = None
    bullet: str = ""
    homing: float = 0.0
    splash: float = 0.0
    splash_radius: float = 0.0
    pierces: bool = False
    needs_target: bool = False
    chain_range: float = 0.0
    chain_jump: float = 0.0
    chain_count: int = 0
    flash: float = 0.0


def parse_gun(data: dict[str, Any]) -> Gun:
    """Read a gun as written in the YAML files.

    Like Gun, with lists for tuples, `rate` (shots per second) instead of `interval`, and `from` (what fires it: see
    pewpy.game.enemies.spec) left out.
    """
    values: dict[str, Any] = {}
    for key, value in data.items():
        if key == "from":
            continue
        if key == "rate":
            values["interval"] = 1.0 / value
        elif key == "sequence":
            values[key] = tuple(parse_gun({"interval": 0.0, "speed": 0.0, **item}) for item in value)
        elif key in ("origins", "velocities"):
            values[key] = tuple(tuple(pair) for pair in value)
        else:
            values[key] = tuple(value) if isinstance(value, list) else value
    return Gun(**values)


TERM = re.compile(r"[+-]?[^+-]+")


def distance(value: Distance, width: float, height: float) -> float:
    """Read a distance: a number (world units), or a string adding up terms.

    Like "0.45w" (that share of the width), "-0.5h" (of the height), "3v" (model cubes, config.MODEL_VOXEL each) or
    "0.05": "0.5w-0.05".
    """
    if not isinstance(value, str):
        return float(value)
    total = 0.0
    for term in TERM.findall(value):
        units = {"w": width, "h": height, "v": config.MODEL_VOXEL}
        if term[-1] in units:
            total += float(term[:-1]) * units[term[-1]]
        else:
            total += float(term)
    return total
