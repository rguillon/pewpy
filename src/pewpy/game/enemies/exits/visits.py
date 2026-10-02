"""The exit condition on `visits`: the state has been entered this many times (this time included)."""

from typing import TYPE_CHECKING

from pewpy.game.entities import Entity

if TYPE_CHECKING:
    from pewpy.game.enemies.enemy import Enemy
    from pewpy.game.enemies.spec import Exit


def visits(enemy: "Enemy", way_out: "Exit", target: Entity) -> bool:
    return enemy.visits[enemy.state_index] >= way_out.visits
