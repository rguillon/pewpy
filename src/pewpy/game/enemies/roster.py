"""Every kind of enemy the levels can place (see kinds.py), by name, and making one (or a boss) ready to enter."""

import random

from pewpy.game.enemies.enemy import HALF_WIDTH, TOP, Enemy, make
from pewpy.game.enemies.kinds import ENEMIES
from pewpy.game.enemies.spec import EnemySpec
from pewpy.game.weapons.guns import distance

ENEMY_TYPES: dict[str, EnemySpec] = {kind: spec for kind, spec in ENEMIES.items() if spec.placeable}


def make_enemy(
    kind: str,
    x: float,
    y: float,
    side: str,
    rng: random.Random | None,
    top: float = TOP,
    edge: float = HALF_WIDTH,
) -> Enemy:
    """Create an enemy (or a boss) of `kind` just outside the screen, ready to enter.

    Top entries use `x` (kept on the screen, parts included) and come in `entry_gap` above the screen; side entries
    use `side` ("left" or "right") and `y`. `top` and `edge` are where the screen really ends above and on the sides
    (the tilted camera shows more than the play area), so enemies appear off screen and fly in. `rng` staggers its
    first shot, so a group doesn't fire all at once (None: not staggered).
    """
    enemy = make(kind)
    spec = enemy.spec
    if enemy.side_entry:
        direction = 1 if side == "left" else -1
        enemy.place(-direction * (edge + enemy.width / 2), y)
        enemy.enter_from_side(direction)
    else:
        limit = HALF_WIDTH - spec.half_span
        gap = distance(spec.entry_gap, spec.width, spec.height)
        enemy.place(max(-limit, min(limit, x)), top + spec.top_reach + gap)
    if rng is not None:
        enemy.fire_cooldown = rng.uniform(0.3, enemy.fire_interval)
    return enemy
