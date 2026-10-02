"""The exit condition on `aligned`: within this of the player's column."""

from typing import TYPE_CHECKING

from pewpy.game.entities import Entity

if TYPE_CHECKING:
    from pewpy.game.enemies.enemy import Enemy
    from pewpy.game.enemies.spec import Exit


def aligned(enemy: "Enemy", way_out: "Exit", target: Entity) -> bool:
    return way_out.aligned is None or abs(target.x - enemy.x) <= way_out.aligned
