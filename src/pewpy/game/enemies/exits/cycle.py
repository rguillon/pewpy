"""The exit condition on `cycle`: (period, start, end): start <= age % period < end."""

from typing import TYPE_CHECKING

from pewpy.game.entities import Entity

if TYPE_CHECKING:
    from pewpy.game.enemies.enemy import Enemy
    from pewpy.game.enemies.spec import Exit


def cycle(enemy: "Enemy", way_out: "Exit", target: Entity) -> bool:
    if way_out.cycle is None:
        return True
    period, start, end = way_out.cycle
    return start <= enemy.age % period < end
