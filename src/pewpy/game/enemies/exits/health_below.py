"""The exit condition on `health_below`: health below this share of the full health."""

from typing import TYPE_CHECKING

from pewpy.game.entities import Entity

if TYPE_CHECKING:
    from pewpy.game.enemies.enemy import Enemy
    from pewpy.game.enemies.spec import Exit


def health_below(enemy: "Enemy", way_out: "Exit", target: Entity) -> bool:
    return not way_out.health_below or enemy.health < way_out.health_below * enemy.spec.health
