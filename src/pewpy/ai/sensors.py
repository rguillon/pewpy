"""What the AI sees of the world: a fixed list of numbers, mostly from -1 to 1, around its ship.

- A danger radar that plans ahead: for each of MOVES (8 directions and staying put), the ship flies it for FIRST
  seconds then the best of MOVES until HORIZON (with its inertia, everything else going on at its speed, the threats
  within NEAR): how long before a hit (closer than MARGIN; from 0 to 1, the whole HORIZON: none) and the room left on
  the way (from 0 to 1, CLEAR or more); the safest of the moves (its direction); and the move to aim, the safe move
  (within TOLERANCE of the safest) that best brings the ship under its target (the boss, else the nearest enemy
  above it).
- The NEAREST_SHOTS nearest enemy shots: where they are from the ship and how fast they go.
- Lanes across the whole screen (LANES columns): how many enemy shots and how many enemies are in each, above the
  ship, so it can pick a lane to fly in and to shoot up.
- The ship: where it is on the screen, its speed, health, whether it is invulnerable, its kind (its top speed and
  size, and which of REGULAR_SHIPS it is: one brain flies them all); the weapon selected and the weapons' levels.
- Targets: the nearest TARGETS enemies and the nearest pickup (where they are from the ship), the boss.
- Repairs: whether any enemy can be hurt (firing at nothing only puts the repairs off), how long since the
  ship last fired (as a share of the wait before its repairs start, 1 once they have) and how fast it repairs.
"""

import math
from typing import Protocol

import numpy as np

from pewpy import config
from pewpy.game.player import REGULAR_SHIPS
from pewpy.game.weapons.player.arsenal import MAX_LEVEL, WEAPONS
from pewpy.game.world import World


class Placed(Protocol):
    """Something with a place on the play plane: what the AI looks at (a pickup, an enemy)."""

    x: float
    y: float


MOVES = ((0.0, 0.0), *((math.cos(a * math.pi / 4), math.sin(a * math.pi / 4)) for a in range(8)))
FIRST = 0.25  # seconds of the first move of a plan, then the second until HORIZON
HORIZON = 0.8  # seconds
STEPS = 10  # positions checked along a plan
NEAR = 0.9  # world units: farther threats can't reach the ship within HORIZON
CLEAR = 0.2  # world units of room: safe enough
MARGIN = 0.02  # world units: closer than this counts as a hit (the threats don't fly quite straight)
UNHIT = 1.5  # a plan's score without a hit (one with a hit scores its time before it, as a share of HORIZON)
TOLERANCE = 0.1  # how much less than the safest a move can score and still be safe to aim with
HOME = 0.0  # the height the ship aims from (the middle of the screen: room to dodge all around)...
HOME_WEIGHT = 0.3  # ...minding it this much less than being under its target
ABOVE_WEIGHT = 0.3  # how much a target's height above the ship counts beside its distance across
CEILING = 0.0  # the highest it goes for a pickup: above, it waits under the pickup for it to drift down
NEAREST_SHOTS = 6
SHOT_RANGE = 0.6  # where the shots are, in this unit
LANES = 8
TARGETS = 3
REACH = 1.0  # targets are seen this far away (world units) at most
FAST_REPAIR = 0.5  # health a second: a repair rate seen as 1
LANE_FULL = 4  # how many things fill a lane, at most (one crowded lane must not drown the others)
SHIP_SIZE = 0.12  # a regular ship's size: the unit ship sizes are seen in, like their speed is their own
NO_THINGS = [0.0, 0.0, 0.0]  # where nothing is: seen as three zeros (no x, no y, and not there)

# Where each block of the view starts, so the network's inputs can be reached by name (see `sense` and brain.py).
SAFEST = 2 * len(MOVES)  # the safest move's direction (x, y), after the times and the rooms
AIM = SAFEST + 2  # the move to aim's direction (x, y)
SHOTS = AIM + 2  # the NEAREST_SHOTS nearest shots, four numbers each
LANE_SHOTS = SHOTS + 4 * NEAREST_SHOTS  # the lanes' shots, then their enemies
LANE_ENEMIES = LANE_SHOTS + LANES
SHIP = LANE_ENEMIES + LANES  # the ship itself, then which ship it is
WHICH_SHIP = SHIP + 8
WEAPONS_SEEN = WHICH_SHIP + len(REGULAR_SHIPS)  # the selected weapon, then every weapon's level
LEVELS = WEAPONS_SEEN + len(WEAPONS)
TARGETS_SEEN = LEVELS + len(WEAPONS)  # the nearest enemies, the pickup and the boss
PICKUP = TARGETS_SEEN + 3 * TARGETS
BOSS = PICKUP + 3
REPAIRS = BOSS + 3  # whether something can be hurt, how long since it fired, how fast it repairs
SHOOTABLE = REPAIRS  # "something on screen can be hurt" is the first of the three (1, else 0)
SIZE = REPAIRS + 3  # the view is this many numbers

HALF_WIDTH = config.PLAY_WIDTH / 2
HALF_HEIGHT = config.PLAY_HEIGHT / 2
NO_THREATS = np.zeros((0, 6))  # nothing threatens: the shape _rows returns when nothing is alive

# A threat as _rows sees it: its position, its velocity and its size, so the radar can foresee a meeting.
X, Y, VX, VY, WIDTH, HEIGHT = range(6)
TIMES = np.linspace(HORIZON / STEPS, HORIZON, STEPS)  # when the radar looks
_FIRSTS = np.repeat(np.arange(len(MOVES)), len(MOVES))  # every plan: its first move...
_SECONDS = np.tile(np.arange(len(MOVES)), len(MOVES))  # ...and its second
_AIM_STEP = int(np.searchsorted(TIMES, FIRST))  # where the ship is told to be when aiming: after the first move


def _rows(entities: list) -> np.ndarray:
    """Return living entities as rows of (X, Y, VX, VY, WIDTH, HEIGHT).

    A shot snaking across its line of flight (an `amplitude`) is as wide as its snaking, so flying straight is all the
    radar needs to foresee.
    """
    rows = []
    for e in entities:
        if e.alive:
            sway = 2 * getattr(e, "amplitude", 0.0)
            rows.append((e.x, e.y, e.vx, e.vy, e.width + sway, e.height + sway))
    return np.array(rows, dtype=float) if rows else NO_THREATS


def nearest[T: Placed](entities: list[T], x: float, y: float, count: int = 1) -> list[T]:
    """Return the `count` entities nearest to (x, y), nearest first (fewer when there are fewer)."""
    return sorted(entities, key=lambda entity: math.hypot(entity.x - x, entity.y - y))[:count]


def nearest_one[T: Placed](entities: list[T], x: float, y: float) -> T | None:
    """Return the entity nearest to (x, y), or None when there is none."""
    return next(iter(nearest(entities, x, y)), None)


def _glide(position: np.ndarray, velocity: np.ndarray, target: np.ndarray, times: np.ndarray) -> np.ndarray:
    """Return where the ship is after `times`: (plans, 2, times).

    Positions, velocities and targets are (plans, 2); the velocity eases towards the target velocity as Player.update
    does it.
    """
    ease = config.PLAYER_RESPONSIVENESS
    lag = (velocity - target)[..., None] * (1 - np.exp(-ease * times)) / ease
    return position[..., None] + target[..., None] * times + lag


def plans(world: World) -> tuple[np.ndarray, np.ndarray]:
    """Return where the ship is along every plan, at TIMES, kept in the play area: x and y, (plans, steps).

    A plan is a first move for FIRST seconds, then a second one: plan i is MOVES[i // len(MOVES)] then
    MOVES[i % len(MOVES)].
    """
    player = world.player
    moves = np.array(MOVES) * player.ship.speed
    first, second = moves[_FIRSTS], moves[_SECONDS]
    start = np.array([[player.x, player.y]])
    velocity = np.array([[player.vx, player.vy]])
    before = _glide(start, velocity, first, np.minimum(TIMES, FIRST))
    ease = config.PLAYER_RESPONSIVENESS
    turn = _glide(start, velocity, first, np.array([FIRST]))[..., 0]
    turn_velocity = first + (velocity - first) * np.exp(-ease * FIRST)
    after = _glide(turn, turn_velocity, second, np.maximum(TIMES - FIRST, 0.0))
    path = np.where(TIMES <= FIRST, before, after)
    max_x = (config.PLAY_WIDTH - player.width) / 2
    max_y = (config.PLAY_HEIGHT - player.height) / 2
    return np.clip(path[:, 0], -max_x, max_x), np.clip(path[:, 1], -max_y, max_y)


def radar(world: World, threats: np.ndarray) -> tuple[np.ndarray, ...]:
    """Sweep the radar over the moves.

    For each move: its best plan's time before a hit (share of HORIZON, 1: none) and room left (share of CLEAR), and the
    score that ranks the moves (see UNHIT); and where each move takes the ship (x and y after FIRST).
    """
    player = world.player
    ship_x, ship_y = plans(world)
    if len(threats):
        near = (np.abs(threats[:, X] - player.x) < NEAR + threats[:, WIDTH] / 2) & (
            np.abs(threats[:, Y] - player.y) < NEAR + threats[:, HEIGHT] / 2
        )
        threats = threats[near]
    count = len(MOVES)
    if len(threats):
        threat_x = threats[:, X] + threats[:, VX] * TIMES[:, None]  # (steps, threats)
        threat_y = threats[:, Y] + threats[:, VY] * TIMES[:, None]
        gap_x = np.abs(threat_x[None] - ship_x[:, :, None]) - (threats[:, WIDTH] + player.width) / 2  # (plans, ...)
        gap_y = np.abs(threat_y[None] - ship_y[:, :, None]) - (threats[:, HEIGHT] + player.height) / 2
        gap = np.maximum(gap_x, gap_y).min(axis=2)  # (plans, steps)
        hit = gap < MARGIN
        first_hit = np.where(hit.any(axis=1), hit.argmax(axis=1), STEPS)
        time = np.where(first_hit < STEPS, TIMES[np.minimum(first_hit, STEPS - 1)] / HORIZON, 1.0)
        room = np.clip(gap.min(axis=1) / CLEAR, 0.0, 1.0)
    else:
        time = room = np.ones(len(_FIRSTS))
    score = np.where(time < 1.0, time, UNHIT) + CLEAR * room
    best = score.reshape(count, count).argmax(axis=1)  # each move's best second move
    pick = np.arange(count) * count + best
    after_first = np.arange(count) * count
    return time[pick], room[pick], score[pick], ship_x[after_first, _AIM_STEP], ship_y[after_first, _AIM_STEP]


def target(world: World) -> tuple[float, float | None] | None:
    """Where the ship should go: (x, y), or (x, None) for anywhere at that x (to shoot up from HOME height).

    Onto the nearest pickup (where it will be after FIRST: they drift down; waiting under it, not above CEILING),
    else under the boss (under its part nearest across while its core is armored: its parts must go first), else
    under the nearest enemy above it.
    """
    player = world.player
    pickup = nearest_one(world.pickups, player.x, player.y)
    if pickup is not None:
        return pickup.x, min(pickup.y + pickup.vy * FIRST, CEILING)
    boss = world.boss
    if boss is not None:
        parts = [part for part in boss.parts if part.alive]
        if parts and not boss.state.vulnerable:
            return min(parts, key=lambda part: abs(part.x - player.x)).x, None
        return boss.x, None
    above = [
        enemy
        for enemy in world.enemies
        if enemy.alive and player.y < enemy.y < world.view_top and abs(enemy.x) < world.view_side
    ]
    if not above:
        return None
    return min(above, key=lambda enemy: abs(enemy.x - player.x) + ABOVE_WEIGHT * (enemy.y - player.y)).x, None


def shootable(world: World) -> bool:
    """Tell whether an enemy can be hurt (not an armored core nor an arriving boss), on screen or coming onto it."""
    return any(enemy.alive and enemy.vulnerable for enemy in world.enemies)


def repairs(world: World) -> list[float]:
    """Return the repairs' inputs: something to shoot, the time since the ship fired (1: repairing), its repair rate."""
    player = world.player
    ship = player.ship
    waited = min(player.since_fired / ship.regeneration_delay, 1.0) if ship.regeneration_delay else 1.0
    return [1.0 if shootable(world) else 0.0, waited, ship.regeneration / FAST_REPAIR]


def safest(score: np.ndarray) -> tuple[float, float]:
    """Return the direction of the move with the best score (staying put when tied)."""
    return MOVES[int(np.argmax(score))]


def aim(
    score: np.ndarray, reach_x: np.ndarray, reach_y: np.ndarray, goal: tuple[float, float | None] | None
) -> tuple[float, float]:
    """Return the direction of the safe move that takes the ship nearest to `goal` (at HOME height if it has no y).

    The safe moves are within TOLERANCE of the safest; without a goal, the safest move.
    """
    if goal is None:
        return safest(score)
    goal_x, goal_y = goal
    safe = score >= score.max() - TOLERANCE
    if goal_y is None:
        cost = np.abs(reach_x - goal_x) + HOME_WEIGHT * np.abs(reach_y - HOME)
    else:
        cost = np.hypot(reach_x - goal_x, reach_y - goal_y)
    return MOVES[int(np.argmin(np.where(safe, cost, np.inf)))]


def _nearest_shots(shots: np.ndarray, x: float, y: float) -> np.ndarray:
    """Return the NEAREST_SHOTS shots nearest to (x, y): where they are from the ship and how fast they go."""
    out = np.zeros((NEAREST_SHOTS, 4))
    if len(shots):
        close = shots[np.argsort(np.hypot(shots[:, X] - x, shots[:, Y] - y))[:NEAREST_SHOTS]]
        out[: len(close), X] = np.clip((close[:, X] - x) / SHOT_RANGE, -1.0, 1.0)
        out[: len(close), Y] = np.clip((close[:, Y] - y) / SHOT_RANGE, -1.0, 1.0)
        out[: len(close), VX:] = np.clip(close[:, VX : VX + 2], -1.0, 1.0)
    return out.ravel()


def _lanes(things: np.ndarray, above: float) -> np.ndarray:
    """How many of the things are in each lane of the screen, above `above`, as a share of LANE_FULL."""
    lanes = np.zeros(LANES)
    if len(things):
        up = things[things[:, Y] > above]
        index = np.clip(((up[:, X] + HALF_WIDTH) / config.PLAY_WIDTH * LANES).astype(int), 0, LANES - 1)
        np.add.at(lanes, index, 1.0)
    return np.minimum(lanes, LANE_FULL) / LANE_FULL


def _towards(dx: float, dy: float) -> tuple[float, float]:
    """Return a direction, each way from -1 to 1: how far off something is, as a share of REACH."""
    return max(-1.0, min(1.0, dx / REACH)), max(-1.0, min(1.0, dy / REACH))


def _seen_thing(entity: Placed | None, x: float, y: float) -> list[float]:
    """Return a thing as the AI sees it: where from the ship, and 1 (it is there) or 0 (no thing)."""
    if entity is None:
        return list(NO_THINGS)
    return [*_towards(entity.x - x, entity.y - y), 1.0]


def _radar(world: World, threats: np.ndarray) -> np.ndarray:
    """Return the radar's answer: each move's time before a hit and the room left, the safest move, the move to aim."""
    time, room, score, reach_x, reach_y = radar(world, threats)
    return np.concatenate([time, room, safest(score), aim(score, reach_x, reach_y, target(world))])


def _lanes_seen(shots: np.ndarray, enemies: np.ndarray, above: float) -> np.ndarray:
    """Return the lanes across the whole screen: the shots' above the ship, and the enemies'."""
    return np.concatenate([_lanes(shots, above), _lanes(enemies, above)])


def _the_ship(world: World) -> list[float]:
    """Return the player's ship: where it is on the screen, how it's moving and how it is."""
    player, ship = world.player, world.player.ship
    return [
        player.x / HALF_WIDTH,
        player.y / HALF_HEIGHT,
        player.vx / ship.speed,
        player.vy / ship.speed,
        max(player.health, 0.0) / ship.health,
        1.0 if player.invulnerable else 0.0,
        ship.speed - 1.0,
        ship.size / SHIP_SIZE - 1.0,
    ]


def _its_ship(world: World) -> list[float]:
    """Return which of REGULAR_SHIPS the player's ship is (one brain flies them all)."""
    return [1.0 if spec is world.player.ship else 0.0 for spec in REGULAR_SHIPS.values()]


def _the_weapons(world: World) -> list[float]:
    """Return the arsenal: which weapon is selected, then every weapon's level."""
    arsenal = world.arsenal
    return [
        *[1.0 if weapon == arsenal.selected else 0.0 for weapon in WEAPONS],
        *[arsenal.levels[weapon] / MAX_LEVEL for weapon in WEAPONS],
    ]


def _the_targets(world: World) -> list[float]:
    """Return the TARGETS enemies nearest the ship, each as where from it and that it's there."""
    player = world.player
    close = nearest([enemy for enemy in world.enemies if enemy.alive], player.x, player.y, TARGETS)
    seen = [number for enemy in close for number in _seen_thing(enemy, player.x, player.y)]
    return [*seen, *NO_THINGS * (TARGETS - len(close))]


def _the_pickup(world: World) -> list[float]:
    """Return the nearest pickup: where it is from the ship, and 1 that it's there (no pickup: three zeros)."""
    player = world.player
    return _seen_thing(nearest_one(world.pickups, player.x, player.y), player.x, player.y)


def _the_boss(world: World) -> list[float]:
    """Return the boss: where it is from the ship, and how much of its health is left (no boss: three zeros)."""
    player, boss = world.player, world.boss
    if boss is None:
        return list(NO_THINGS)
    x, y, _there = _seen_thing(boss, player.x, player.y)
    return [x, y, boss.health_fraction]


def sense(world: World) -> np.ndarray:
    """Return the AI's view of `world`, one block per thing the module docstring lists, in that order.

    The blocks are named, so their offsets in the view are named too (AIM, SHOOTABLE...); a block's size follows from
    what it describes, and SIZE is their sum.
    """
    player = world.player
    shots = _rows([shot for shot in world.enemy_bullets if not shot.harmless])
    enemies = _rows(world.enemies)
    return np.concatenate([
        _radar(world, np.concatenate([shots, enemies])),  # time and room per move, then the safest and the aim
        _nearest_shots(shots, player.x, player.y),
        _lanes_seen(shots, enemies, player.y),
        _the_ship(world),
        _its_ship(world),
        _the_weapons(world),
        _the_targets(world),
        _the_pickup(world),
        _the_boss(world),
        repairs(world),
    ])
