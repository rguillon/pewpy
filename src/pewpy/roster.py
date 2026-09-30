"""Every kind of enemy the levels can place (enemies.py and fleet.py), by name, and making one ready to enter."""

import random

from pewpy.enemies import (
    HALF_WIDTH,
    TOP,
    Bomber,
    Buckshot,
    Diver,
    Drone,
    Enemy,
    FlakCannon,
    Gunship,
    Hunter,
    Lancer,
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
from pewpy.fleet import FLEET

ENEMY_TYPES: dict[str, type[Enemy]] = {
    **FLEET,
    "drone": Drone,
    "weaver": Weaver,
    "diver": Diver,
    "gunship": Gunship,
    "turret": Turret,
    "swarmer": Swarmer,
    "sniper": Sniper,
    "mine_layer": MineLayer,
    "shield_carrier": ShieldCarrier,
    "splitter": Splitter,
    "flak_cannon": FlakCannon,
    "tank": Tank,
    "rocket_truck": RocketTruck,
    "rocketeer": Rocketeer,
    "hunter": Hunter,
    "missile_silo": MissileSilo,
    "bomber": Bomber,
    "lancer": Lancer,
    "serpent": Serpent,
    "buckshot": Buckshot,
}


def make_enemy(
    kind: str, x: float, y: float, side: str, rng: random.Random, top: float = TOP, edge: float = HALF_WIDTH
) -> Enemy:
    """Create an enemy of `kind` just outside the screen, ready to enter.

    Top entries use `x`; side entries use `side` ("left" or "right") and `y`. `top` and `edge` are where the
    screen really ends above and on the sides (the tilted camera shows more than the play area), so enemies
    appear off screen and fly in.
    """
    enemy = ENEMY_TYPES[kind]()
    if enemy.side_entry:
        direction = 1 if side == "left" else -1
        enemy.x = -direction * (edge + enemy.width / 2)
        enemy.y = y
        enemy.enter_from_side(direction)
    else:
        max_x = HALF_WIDTH - enemy.width / 2
        enemy.x = max(-max_x, min(max_x, x))
        enemy.y = top + enemy.height / 2
    # Stagger the first shot so a group doesn't fire all at once.
    enemy.fire_cooldown = rng.uniform(0.3, enemy.fire_interval)
    return enemy
