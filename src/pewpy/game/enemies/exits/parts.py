"""The exit condition on `parts`: these parts are destroyed."""

from typing import TYPE_CHECKING

from pewpy.game.entities import Entity

if TYPE_CHECKING:
    from pewpy.game.enemies.enemy import Enemy
    from pewpy.game.enemies.spec import Exit


def parts(enemy: "Enemy", way_out: "Exit", target: Entity) -> bool:
    destroyed = {part.part_name for part in enemy.parts if not part.alive}
    return set(way_out.parts) <= destroyed
