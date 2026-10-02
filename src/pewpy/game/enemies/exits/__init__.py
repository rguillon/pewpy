"""The ways out of an enemy's states (02-enemies.md), each condition in its own module. A condition is
`condition(enemy, way_out, target)`: the enemy, the Exit (see pewpy.game.enemies.spec) and the player; True when it
holds (or the exit doesn't ask for it). An exit is taken once all its conditions hold. Independent from rendering.
"""

from collections.abc import Callable
from typing import TYPE_CHECKING

from pewpy.game.enemies.exits.above_y import above_y
from pewpy.game.enemies.exits.aligned import aligned
from pewpy.game.enemies.exits.below_y import below_y
from pewpy.game.enemies.exits.clock import clock
from pewpy.game.enemies.exits.cycle import cycle
from pewpy.game.enemies.exits.health_below import health_below
from pewpy.game.enemies.exits.idle import idle
from pewpy.game.enemies.exits.parts import parts
from pewpy.game.enemies.exits.timer import timer
from pewpy.game.enemies.exits.visits import visits
from pewpy.game.enemies.exits.volleys import volleys
from pewpy.game.entities import Entity

if TYPE_CHECKING:
    from pewpy.game.enemies.enemy import Enemy
    from pewpy.game.enemies.spec import Exit

__all__ = ["CONDITIONS", "Condition", "can_leave"]
Condition = Callable[["Enemy", "Exit", Entity], bool]
CONDITIONS: tuple[Condition, ...] = (
    timer,
    clock,
    below_y,
    above_y,
    aligned,
    cycle,
    visits,
    parts,
    health_below,
    idle,
    volleys,
)


def can_leave(enemy: "Enemy", way_out: "Exit", target: Entity) -> bool:
    """Whether every condition of `way_out` holds."""
    return all(condition(enemy, way_out, target) for condition in CONDITIONS)
