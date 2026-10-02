"""The exit condition on `volleys`: this many volleys fired in the state (checked after the guns)."""

from typing import TYPE_CHECKING

from pewpy.game.entities import Entity

if TYPE_CHECKING:
    from pewpy.game.enemies.enemy import Enemy
    from pewpy.game.enemies.spec import Exit


def volleys(enemy: "Enemy", way_out: "Exit", target: Entity) -> bool:
    return sum(gun.volleys for gun in enemy.guns) >= way_out.volleys
