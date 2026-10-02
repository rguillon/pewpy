"""The exit condition on `timer`: the state's timer has run out."""

from typing import TYPE_CHECKING

from pewpy.game.entities import Entity

if TYPE_CHECKING:
    from pewpy.game.enemies.enemy import Enemy
    from pewpy.game.enemies.spec import Exit


def timer(enemy: "Enemy", way_out: "Exit", target: Entity) -> bool:
    return not way_out.timer or enemy.timer <= 0
