"""The exit condition on `idle`: no gun is charging, firing a beam or in the middle of a volley."""

from typing import TYPE_CHECKING

from pewpy.game.entities import Entity

if TYPE_CHECKING:
    from pewpy.game.enemies.enemy import Enemy
    from pewpy.game.enemies.spec import Exit


def idle(enemy: "Enemy", way_out: "Exit", target: Entity) -> bool:
    return not way_out.idle or not any(gun.busy for gun in enemy.guns)
