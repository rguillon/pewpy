"""Guns (01-gameplay.md "Weapons", 02-enemies.md "Enemy weapons", 02-enemies-bosses.md): how the player's weapons
and every enemy and boss fire their bullets, launch their projectiles or fire their beams. Independent from rendering.

A gun (Gun) is data, read from the JSON files (the player's weapons in `src/pewpy/weapons/`, the enemies' with
them, see pewpy.game.enemies.spec); its GunState counts down to its next shot. `step` runs a gun for a frame and
returns what it fired: bullets of several kinds (see bullets.py and Gun.style), enemies (projectiles like rockets and
homing missiles, mines, Sparks...) or beams. Two patterns aren't fired by `step`: "ray" (the player's laser, which
the world plays out against the enemies) and "chain" (the lightning gun, see `chain`).
"""

import math
import re
from collections.abc import Callable, Sequence
from dataclasses import dataclass, field, fields
from typing import Any, TypeVar

from pewpy import config
from pewpy.game.entities import Bullet, Entity
from pewpy.game.weapons.bullets import AccelBullet, BossBeam, CurveBullet, Missile, WaveBullet, beam

HEAVY_BULLET_SIZE = 0.05  # "heavy" shots: bigger and orange (the hitbox too)
SWEEP_PERIOD = 2.0  # seconds for a sweeping gun to go from one side to the other and back
BULLET_SIZES = {"heavy": HEAVY_BULLET_SIZE, "pellet": 0.022}  # the others are config.ENEMY_BULLET_SIZE
ACCEL_START = 0.35  # "accel" shots start at this share of their speed...
ACCEL_RATE = 0.9  # ...and speed up by this much per second...
ACCEL_TOP = 1.8  # ...up to this many times their speed
LASER_WARNING = 1.0  # seconds of thin harmless beam before a laser fires: time to move away
WARNING_WIDTH = 0.008
# A boss gun's `projectile`: the enemy it launches, and how fast (a homing missile sets its own speed).
PROJECTILES = {"rocket": ("rocket", 0.25), "missile": ("homing_missile", 0.0), "cluster": ("cluster_bomb", 0.3)}

# Makes an enemy of a kind at (x, y), heading that way (radians, None: its own) with its first timer (None: its own).
Maker = Callable[[str, float, float, float | None, float | None], Entity]
Distance = float | str  # see `distance`
T = TypeVar("T", bound=Entity)


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

    `style`: "normal", "sniper" (blue), "heavy" (bigger, orange), "pellet" (small), "wave" (violet, snaking across
    its line of flight), "accel" (cyan, starts slow and speeds up) or "curve" (yellow, its path bends by `curve`
    degrees per second for CURVE_TIME seconds). Its shots do `damage` (None: config.ENEMY_BULLET_DAMAGE) and are
    `size` (width, height; None: by style). `bullet`: "missile" for the player's missiles, homing at `homing` degrees
    per second (0: not homing), blowing up enemies within `splash_radius` too (`splash` damage each).

    Instead of bullets it can launch enemies: `projectile` ("rocket", "missile" (homing) or "cluster", see
    PROJECTILES, flying the shot's way) or `spawn` (any kind of enemy). A spawned enemy flies the shot's way at
    `spawn_speed`, or at `spawn_velocity` (its x turned round on the left of the middle), or as it would on its own;
    `spawn_heading` turns it (degrees, counterclockwise from the right); with `spawn_fuse`, its first timer is set so
    it gets where the player is now.

    A laser fires one beam per `offsets` (x from the gun's middle), `width` wide, for `duration` seconds, each
    announced by a thin harmless beam LASER_WARNING seconds before; the beams follow the gun as the boss sways.

    When to fire: while its trigger is held (always, for enemies), when `interval` has gone by ("reset": counted
    again from then; "carry": what it was late by is taken off the next wait; "clamp": the wait never goes below 0,
    so it doesn't make up for the time it had nothing to fire at). `needs_target`: it only fires at a target (the
    nearest enemy, for the player's guns). `off_screen`: "hold" (the shot waits until it's on screen), "skip" (that shot is
    skipped) or "fire". `aligned`: it fires only within that of the player's column. `staggered`: the first wait is
    the enemy's own (set when it's placed). `charge`: seconds of glowing before it fires (the wait starts again
    after); `hold`: the enemy stands still while charging and while its beam lasts. `wait_volley`: no reloading
    during a volley, which starts on the next frame (a volley of one fires at once). `at`: fires once, when the
    state has that many seconds left. `window`: fires every `gap` seconds during the first `window` seconds of each
    `interval` of the state, sweeping from `-reach` to `reach` degrees (the other way round every other time).
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


@dataclass
class GunState:
    cooldown: float
    volley_left: int = 0
    volley_timer: float = 0.0
    volley_index: int = 0  # the next shot's place in its volley
    turned: float = 0.0
    charge: float = 0.0  # a laser: seconds until its beams fire (its warning beams show meanwhile)
    charging: float = 0.0  # a gun with `charge`: seconds until it fires
    beaming: float = 0.0  # a "beam" gun: seconds until its beam ends
    shots: int = 0  # volleys started: the sequence goes round with it
    volleys: int = 0  # volleys fired in full
    fired: bool = False  # an `at` gun
    item: Gun | None = None  # the pattern of the volley under way

    @property
    def busy(self) -> bool:
        """Charging, beaming or in the middle of a volley."""
        return self.volley_left > 0 or self.charging > 0 or self.beaming > 0


def _no_maker(kind: str, x: float, y: float, heading: float | None, timer: float | None) -> Entity:
    raise NoMakerError(kind)


class NoMakerError(Exception):
    def __init__(self, kind: str) -> None:
        super().__init__(f"this gun can't launch a {kind!r}: nothing to make it")


@dataclass
class Shooter:
    """What a gun needs to know about what carries it, this frame."""

    piece: Entity  # where it fires from (an enemy, a boss's part, the player's ship)
    target: Entity | None  # what it aims at (the player, for enemies), if anything
    age: float = 0.0  # of the enemy, for sweeping guns
    clock: float = 0.0  # seconds in the enemy's state
    remaining: float = 0.0  # seconds left in the enemy's state (its timer)
    on_screen: bool = True
    make: Maker = _no_maker
    stop: Callable[[], None] = field(default=lambda: None)  # stand still (a gun that holds)
    hostile: bool = True  # its shots hurt the player (else the enemies)
    forward: int = -1  # straight ahead: -1 down the screen (enemies), 1 up (the player)
    trigger: bool = True  # fire held (enemies always fire)


def step(gun: Gun, state: GunState, shooter: Shooter, dt: float) -> list[Entity]:
    """Run `gun` for a frame: what it fired."""
    created: list[Entity] = []
    if state.charge > 0:
        state.charge -= dt
        if state.charge <= 0:
            created += laser_beams(state.item or gun, shooter.piece, warning=False)
    if state.beaming > 0 or state.charging > 0:
        return created + _charging(gun, state, shooter, dt)
    if gun.window:
        return created + _window(gun, state, shooter, dt)
    if gun.at is not None:
        return created + _at(gun, state, shooter)
    if gun.wait_volley:
        return created + _waiting_volley(gun, state, shooter, dt)
    if _reloaded(gun, state, shooter, dt):
        if gun.charge:
            state.charging = gun.charge
            if gun.hold:
                shooter.stop()
            return created
        _start_volley(gun, state)
    return created + _volley(state, shooter, dt)


def _charging(gun: Gun, state: GunState, shooter: Shooter, dt: float) -> list[Entity]:
    """Glowing before it fires, or firing its beam."""
    if state.beaming > 0:
        state.beaming -= dt
        return []
    state.charging -= dt
    if state.charging > 0:
        return []
    if gun.pattern == "beam":
        state.beaming = gun.duration
    return fire(gun, shooter, state)


def _at(gun: Gun, state: GunState, shooter: Shooter) -> list[Entity]:
    if state.fired or shooter.remaining > (gun.at or 0.0):
        return []
    state.fired = True
    return fire(gun, shooter, state)


def _waiting_volley(gun: Gun, state: GunState, shooter: Shooter, dt: float) -> list[Entity]:
    """No reloading during a volley, which starts on the next frame (a volley of one fires at once)."""
    if state.volley_left > 0:
        return _volley(state, shooter, dt)
    if not _reloaded(gun, state, shooter, dt):
        return []
    item = _start_volley(gun, state)
    if item.volley > 1:
        return []
    state.volley_left = 0
    return _shoot(item, state, shooter)


def _reloaded(gun: Gun, state: GunState, shooter: Shooter, dt: float) -> bool:
    """Count down to the next shot; True when it's time to fire."""
    state.cooldown -= dt
    if gun.reload == "clamp" or not shooter.trigger:
        state.cooldown = max(state.cooldown, 0.0)
    if not shooter.trigger or state.cooldown > 0:
        return False
    if gun.off_screen == "skip" and not shooter.on_screen:
        state.cooldown = gun.interval
        return False
    if gun.off_screen == "hold" and not shooter.on_screen:
        return False
    target = shooter.target
    if (gun.needs_target and target is None) or (
        gun.aligned and target and abs(target.x - shooter.piece.x) > gun.aligned
    ):
        return False
    state.cooldown = gun.interval if gun.reload == "reset" else state.cooldown + gun.interval
    return True


def _start_volley(gun: Gun, state: GunState) -> Gun:
    """The next volley (of the next gun of the sequence, if it has one): its pattern."""
    item = gun.sequence[state.shots % len(gun.sequence)] if gun.sequence else gun
    state.item = item
    state.shots += 1
    state.volley_left, state.volley_timer, state.volley_index = item.volley, 0.0, 0
    return item


def _volley(state: GunState, shooter: Shooter, dt: float) -> list[Entity]:
    item = state.item
    if item is None or state.volley_left == 0:
        return []
    state.volley_timer -= dt
    if state.volley_timer > 0:
        return []
    state.volley_left -= 1
    state.volley_timer = item.gap
    return _shoot(item, state, shooter)


def _shoot(item: Gun, state: GunState, shooter: Shooter) -> list[Entity]:
    """The next shot of the volley under way."""
    if state.volley_left == 0:
        state.volleys += 1
    if item.pattern == "laser":
        state.charge = LASER_WARNING
        return list(laser_beams(item, shooter.piece, warning=True))
    shots = fire(item, shooter, state)
    state.volley_index += 1
    state.turned += item.turn
    return shots


def _window(gun: Gun, state: GunState, shooter: Shooter, dt: float) -> list[Entity]:
    into = shooter.clock % gun.interval
    if into >= gun.window:
        return []
    state.volley_timer -= dt
    if state.volley_timer > 0:
        return []
    state.volley_timer = gun.gap
    forward = int(shooter.clock // gun.interval) % 2 == 0
    angle = (into / gun.window * 2 - 1) * gun.reach * (1 if forward else -1)
    return fire(gun, shooter, state, angle)


def fire(gun: Gun, shooter: Shooter, state: GunState | None = None, angle: float | None = None) -> list[Entity]:
    """One shot of `gun` from each of its origins: its bullets (or enemies, or beam), all at the same time."""
    turned = state.turned if state else 0.0
    index = state.volley_index if state else 0
    piece = shooter.piece
    created: list[Entity] = []
    if gun.pattern in ("ray", "chain"):
        return created  # played out by what carries it (see the module's docstring)
    for x, y in gun.origins:
        ox, oy = distance(x, piece.width, piece.height), distance(y, piece.width, piece.height)
        muzzle = piece if ox == 0 and oy == 0 else Entity(x=piece.x + ox, y=piece.y + oy)
        if gun.pattern == "beam":
            created.append(beam(muzzle.x, muzzle.y, gun.width, gun.duration))
            continue
        if gun.velocities:
            created += [styled_bullet(gun, muzzle, vx, vy, shooter.hostile) for vx, vy in gun.velocities]
            continue
        target = shooter.target or muzzle
        if angle is not None:
            angles = [angle]
        else:
            angles = pattern_angles(gun, muzzle, target, turned, shooter.age, shooter.forward)
        extra = gun.volley_angles[index % len(gun.volley_angles)] if gun.volley_angles else 0.0
        for number, direction in enumerate(angles):
            direction += extra
            speed = gun.speeds[number % len(gun.speeds)] if gun.speeds else gun.speed
            if gun.spawn or gun.projectile:
                created.append(_launch(gun, muzzle, direction, ox, shooter))
            else:
                radians = math.radians(direction)
                vx, vy = math.sin(radians) * speed, shooter.forward * math.cos(radians) * speed
                created.append(styled_bullet(gun, muzzle, vx, vy, shooter.hostile))
    return created


def _launch(gun: Gun, muzzle: Entity, direction: float, ox: float, shooter: Shooter) -> Entity:
    kind, speed = PROJECTILES[gun.projectile] if gun.projectile else (gun.spawn, gun.spawn_speed)
    heading = math.radians(gun.spawn_heading) if gun.spawn_heading is not None else None
    vx = vy = fuse = None
    if speed is not None:
        radians = math.radians(direction)
        dx, dy = math.sin(radians), shooter.forward * math.cos(radians)
        vx, vy = dx * speed, dy * speed
        heading = math.atan2(dy, dx) if heading is None else heading
        if gun.spawn_fuse and speed and shooter.target:
            fuse = math.hypot(shooter.target.x - muzzle.x, shooter.target.y - muzzle.y) / speed
    elif gun.spawn_velocity is not None:
        vx, vy = gun.spawn_velocity
        vx = math.copysign(vx, ox) if ox else vx
    enemy = shooter.make(kind, muzzle.x, muzzle.y, heading, fuse)
    if vx is not None and vy is not None:
        enemy.vx, enemy.vy = vx, vy
    return enemy


def laser_beams(gun: Gun, source: Entity, warning: bool) -> list[Bullet]:
    """A laser gun's beams from `source`, or their thin harmless warnings."""
    beams: list[Bullet] = []
    for offset in gun.offsets:
        laser = BossBeam(
            width=WARNING_WIDTH if warning else gun.width,
            damage=0.0 if warning else config.ENEMY_BULLET_DAMAGE,
            hostile=True,
            style="warning" if warning else "beam",
            life=LASER_WARNING if warning else gun.duration,
            pierces=True,
            harmless=warning,
            source=source,
            offset_x=offset,
        )
        laser.move(0.0)  # in place under its source
        beams.append(laser)
    return beams


def pattern_angles(
    gun: Gun, source: Entity, target: Entity, turned: float, age: float, forward: int = -1
) -> list[float]:
    """The directions of one shot's bullets, in degrees from straight ahead (`forward`: -1 down, 1 up)."""
    if gun.pattern == "aimed":
        middle = math.degrees(math.atan2(target.x - source.x, forward * (target.y - source.y)))
    else:
        middle = gun.sweep * math.sin(2 * math.pi * age / SWEEP_PERIOD)
    if gun.angles:
        return [middle + turned + gun.angle + angle for angle in gun.angles]
    if gun.pattern == "ring":
        return [middle + turned + gun.angle + index * 360 / gun.count for index in range(gun.count)]
    return [middle + turned + gun.angle + (index - (gun.count - 1) / 2) * gun.spread for index in range(gun.count)]


def styled_bullet(gun: Gun, source: Entity, vx: float, vy: float, hostile: bool = True) -> Bullet:
    """A bullet of the gun's style (or kind) from `source`, flying at (vx, vy) (an "accel" one starts slower)."""
    if gun.bullet == "missile":
        bullet: Bullet = Missile(
            homing=gun.homing > 0,
            turn_rate=math.radians(gun.homing),
            splash_damage=gun.splash,
            splash_radius=gun.splash_radius,
        )
    elif gun.style == "wave":
        bullet = WaveBullet()
    elif gun.style == "accel":
        bullet = AccelBullet(rate=ACCEL_RATE * gun.speed, top_speed=ACCEL_TOP * gun.speed)
        vx, vy = vx * ACCEL_START, vy * ACCEL_START
    elif gun.style == "curve":
        bullet = CurveBullet(turn_rate=gun.curve)
    else:
        bullet = Bullet()
    bullet.x, bullet.y, bullet.vx, bullet.vy = source.x, source.y, vx, vy
    if gun.size is None:
        bullet.width = bullet.height = BULLET_SIZES.get(gun.style, config.ENEMY_BULLET_SIZE)
    else:
        bullet.width, bullet.height = gun.size
    bullet.damage = config.ENEMY_BULLET_DAMAGE if gun.damage is None else gun.damage
    bullet.hostile, bullet.style = hostile, gun.style
    return bullet


def nearest(origin: Entity, targets: Sequence[T], reach: float = math.inf) -> T | None:
    """The target nearest to `origin`, within `reach`."""
    distances = {id(target): math.hypot(target.x - origin.x, target.y - origin.y) for target in targets}
    near = [target for target in targets if distances[id(target)] <= reach]
    return min(near, key=lambda target: distances[id(target)], default=None)


def chain(gun: Gun, origin: Entity, targets: Sequence[T]) -> list[T]:
    """What a "chain" gun strikes: the nearest target in range of `origin`, then each time the nearest one not
    struck yet within a jump of the last.
    """
    struck: list[T] = []
    here, reach = origin, gun.chain_range
    while len(struck) < gun.chain_count:
        target = nearest(here, [target for target in targets if target not in struck], reach)
        if target is None:
            break
        struck.append(target)
        here, reach = target, gun.chain_jump
    return struck


GUN_FIELDS = frozenset(f.name for f in fields(Gun))


def parse_gun(data: dict[str, Any]) -> Gun:
    """A gun as written in the JSON files: like Gun, with lists for tuples, `rate` (shots per second) instead of
    `interval`, and `from` (what fires it: see pewpy.game.enemies.spec) left out.
    """
    values: dict[str, Any] = {}
    for key, value in data.items():
        if key == "from":
            continue
        if key == "rate":
            key, value = "interval", 1.0 / value
        elif key == "sequence":
            value = tuple(parse_gun({"interval": 0.0, "speed": 0.0, **item}) for item in value)
        elif key in ("origins", "velocities"):
            value = tuple(tuple(pair) for pair in value)
        elif isinstance(value, list):
            value = tuple(value)
        values[key] = value
    return Gun(**values)


TERM = re.compile(r"[+-]?[^+-]+")


def distance(value: Distance, width: float, height: float) -> float:
    """A distance: a number (world units), or a string adding up terms like "0.45w" (that share of the width),
    "-0.5h" (of the height), "3v" (model cubes, config.MODEL_VOXEL each) or "0.05": "0.5w-0.05".
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
