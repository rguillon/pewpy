"""What the AI sees of the world: a fixed list of numbers, mostly from -1 to 1, around its ship.

- A danger radar: for each of MOVES (8 directions and staying put), how close the enemy shots and the enemies come to
  the ship if it flew that way for each of HORIZONS (everything going on at its speed): the room left, from 0
  (a hit) to 1 (CLEAR or more); and the safest of the moves (its direction, the long horizon counting double).
- The NEAREST_SHOTS nearest enemy shots: where they are from the ship and how fast they go.
- Lanes across the whole screen (LANES columns): how many enemy shots and how many enemies are in each, above the
  ship, so it can pick a lane to fly in and to shoot up.
- The ship: where it is on the screen, its speed, health, whether it is invulnerable, its kind; the weapon selected
  and the weapons' levels.
- Targets: the nearest TARGETS enemies and the nearest pickup (where they are from the ship), the boss.
"""

import math

import numpy as np

from pewpy import config
from pewpy.game.weapons import MAX_LEVEL, WEAPONS
from pewpy.game.world import World

MOVES = ((0.0, 0.0), *((math.cos(a * math.pi / 4), math.sin(a * math.pi / 4)) for a in range(8)))
HORIZONS = (0.3, 0.7)  # seconds
STEPS = 4  # positions checked along each horizon
CLEAR = 0.2  # world units of room: safe enough
NEAREST_SHOTS = 6
SHOT_RANGE = 0.6  # where the shots are, in this unit
LANES = 8
TARGETS = 3
REACH = 1.0  # targets are seen this far away (world units) at most

HALF_WIDTH = config.PLAY_WIDTH / 2
HALF_HEIGHT = config.PLAY_HEIGHT / 2
SIZE = len(MOVES) * len(HORIZONS) + 2 + 4 * NEAREST_SHOTS + 2 * LANES + 8 + 2 * len(WEAPONS) + 3 * TARGETS + 3 + 3
SAFEST = len(MOVES) * len(HORIZONS)  # where the safest move's direction (x, y) is in the view
NO_THREATS = np.zeros((0, 6))
TIMES = [np.linspace(horizon / STEPS, horizon, STEPS) for horizon in HORIZONS]  # when the radar looks


def _rows(entities: list) -> np.ndarray:
    """Living entities as rows of (x, y, vx, vy, width, height)."""
    rows = [(e.x, e.y, e.vx, e.vy, e.width, e.height) for e in entities if e.alive]
    return np.array(rows, dtype=float) if rows else NO_THREATS


def radar(world: World, threats: np.ndarray) -> np.ndarray:
    """For each move and horizon, the room left between the ship and the nearest threat (at worst along the way)."""
    player = world.player
    if not len(threats):
        return np.ones(len(MOVES) * len(HORIZONS))
    moves = np.array(MOVES) * player.ship.speed  # (moves, 2)
    reach_x = (threats[:, 4] + player.width) / 2  # (threats,)
    reach_y = (threats[:, 5] + player.height) / 2
    max_x = (config.PLAY_WIDTH - player.width) / 2
    max_y = (config.PLAY_HEIGHT - player.height) / 2
    rooms = []
    for times in TIMES:  # (steps,)
        ship_x = np.clip(player.x + moves[:, 0, None] * times, -max_x, max_x)  # (moves, steps)
        ship_y = np.clip(player.y + moves[:, 1, None] * times, -max_y, max_y)
        threat_x = threats[:, 0] + threats[:, 2] * times[:, None]  # (steps, threats)
        threat_y = threats[:, 1] + threats[:, 3] * times[:, None]
        gap_x = np.abs(threat_x[None] - ship_x[:, :, None]) - reach_x  # (moves, steps, threats)
        gap_y = np.abs(threat_y[None] - ship_y[:, :, None]) - reach_y
        room = np.maximum(gap_x, gap_y).min(axis=(1, 2))
        rooms.append(np.clip(room / CLEAR, 0.0, 1.0))
    return np.concatenate(rooms)


def safest(rooms: np.ndarray) -> tuple[float, float]:
    """The direction of the move with the most room (the long horizon counting double; staying put when tied)."""
    count = len(MOVES)
    score = sum((index + 1) * rooms[index * count : (index + 1) * count] for index in range(len(HORIZONS)))
    return MOVES[int(np.argmax(score))]


def _nearest_shots(shots: np.ndarray, x: float, y: float) -> np.ndarray:
    out = np.zeros((NEAREST_SHOTS, 4))
    if len(shots):
        nearest = shots[np.argsort(np.hypot(shots[:, 0] - x, shots[:, 1] - y))[:NEAREST_SHOTS]]
        out[: len(nearest), 0] = np.clip((nearest[:, 0] - x) / SHOT_RANGE, -1.0, 1.0)
        out[: len(nearest), 1] = np.clip((nearest[:, 1] - y) / SHOT_RANGE, -1.0, 1.0)
        out[: len(nearest), 2:] = np.clip(nearest[:, 2:4], -1.0, 1.0)
    return out.ravel()


def _lanes(things: np.ndarray, above: float) -> np.ndarray:
    """How many of the things are in each lane of the screen, above `above` (each lane's count, at most 4)."""
    lanes = np.zeros(LANES)
    if len(things):
        up = things[things[:, 1] > above]
        index = np.clip(((up[:, 0] + HALF_WIDTH) / config.PLAY_WIDTH * LANES).astype(int), 0, LANES - 1)
        np.add.at(lanes, index, 1.0)
    return np.minimum(lanes, 4.0) / 4.0


def _towards(dx: float, dy: float) -> tuple[float, float]:
    return max(-1.0, min(1.0, dx / REACH)), max(-1.0, min(1.0, dy / REACH))


def sense(world: World) -> np.ndarray:
    """The AI's view of `world`, SIZE numbers."""
    player = world.player
    shots = _rows([shot for shot in world.enemy_bullets if not shot.harmless])
    enemies = _rows(world.enemies)
    arsenal = world.arsenal
    ship = player.ship
    nearest = sorted(
        (enemy for enemy in world.enemies if enemy.alive),
        key=lambda enemy: math.hypot(enemy.x - player.x, enemy.y - player.y),
    )[:TARGETS]
    targets = []
    for index in range(TARGETS):
        if index < len(nearest):
            targets += [*_towards(nearest[index].x - player.x, nearest[index].y - player.y), 1.0]
        else:
            targets += [0.0, 0.0, 0.0]
    pickup = min(world.pickups, key=lambda p: math.hypot(p.x - player.x, p.y - player.y), default=None)
    boss = world.boss
    rooms = radar(world, np.concatenate([shots, enemies]))
    return np.concatenate([
        rooms,
        safest(rooms),
        _nearest_shots(shots, player.x, player.y),
        _lanes(shots, player.y),
        _lanes(enemies, player.y),
        [
            player.x / HALF_WIDTH,
            player.y / HALF_HEIGHT,
            player.vx / ship.speed,
            player.vy / ship.speed,
            max(player.health, 0.0) / ship.health,
            1.0 if player.invulnerable else 0.0,
            ship.speed - 1.0,
            ship.size / 0.12 - 1.0,
        ],
        [1.0 if weapon == arsenal.selected else 0.0 for weapon in WEAPONS],
        [arsenal.levels[weapon] / MAX_LEVEL for weapon in WEAPONS],
        targets,
        [*_towards(pickup.x - player.x, pickup.y - player.y), 1.0] if pickup else [0.0, 0.0, 0.0],
        [*_towards(boss.x - player.x, boss.y - player.y), boss.health_fraction] if boss else [0.0, 0.0, 0.0],
    ])
