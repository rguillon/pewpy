"""The "chain" pattern (the lightning gun), which the gun doesn't fire itself: what it strikes."""

import math
from collections.abc import Sequence
from typing import TypeVar

from pewpy.game.entities import Entity
from pewpy.game.weapons.guns.gun import Gun

T = TypeVar("T", bound=Entity)


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
