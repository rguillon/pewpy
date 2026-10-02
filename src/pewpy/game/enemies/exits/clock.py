"""The exit condition on `clock`: this many seconds in the state."""

from typing import TYPE_CHECKING

from pewpy.game.entities import Entity

if TYPE_CHECKING:
    from pewpy.game.enemies.enemy import Enemy
    from pewpy.game.enemies.spec import Exit


def clock(enemy: "Enemy", way_out: "Exit", target: Entity) -> bool:
    return way_out.clock is None or enemy.clock >= way_out.clock
