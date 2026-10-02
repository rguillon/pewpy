"""The ways out of an enemy's states (02-enemies.md): an Exit (exit.py) is taken once all its conditions hold, each
condition in its own module (see Condition.holds in condition.py). Independent from rendering.

The enemies' descriptions write an exit as its state (`to`), what's done on the way (`then`, actions), `go_on` and
`recheck`, and its conditions, each by its name: CONDITIONS reads each one, and `parse_exit` a whole exit.
"""

from collections.abc import Callable
from typing import Any

from pewpy.game.enemies.actions import parse_action
from pewpy.game.enemies.errors import FlagError, UnknownConditionError
from pewpy.game.enemies.exits.above_y import AboveY
from pewpy.game.enemies.exits.aligned import Aligned
from pewpy.game.enemies.exits.below_y import BelowY
from pewpy.game.enemies.exits.clock import Clock
from pewpy.game.enemies.exits.condition import Condition
from pewpy.game.enemies.exits.cycle import Cycle
from pewpy.game.enemies.exits.exit import Exit
from pewpy.game.enemies.exits.health_below import HealthBelow
from pewpy.game.enemies.exits.idle import Idle
from pewpy.game.enemies.exits.parts import Parts
from pewpy.game.enemies.exits.timer import Timer
from pewpy.game.enemies.exits.visits import Visits
from pewpy.game.enemies.exits.volleys import Volleys

__all__ = [
    "CONDITIONS",
    "AboveY",
    "Aligned",
    "BelowY",
    "Clock",
    "Condition",
    "Cycle",
    "Exit",
    "HealthBelow",
    "Idle",
    "Parts",
    "Timer",
    "Visits",
    "Volleys",
    "parse_exit",
]


def flag(name: str, condition: Condition) -> Callable[[Any], Condition]:
    """Reads a condition written `name: true`."""

    def read(value: Any) -> Condition:
        if value is not True:
            raise FlagError(name)
        return condition

    return read


CONDITIONS: dict[str, Callable[[Any], Condition]] = {
    "timer": flag("timer", Timer()),  # the state's timer has run out
    "clock": Clock,  # this many seconds in the state
    "below_y": BelowY,
    "above_y": AboveY,
    "aligned": Aligned,  # within this of the player's column
    "cycle": lambda value: Cycle(*value),  # (period, start, end): start <= age % period < end
    "visits": Visits,  # the state has been entered this many times (this time included)
    "parts": lambda value: Parts(tuple(value)),  # these parts are destroyed
    "health_below": HealthBelow,  # health below this share of the full health
    "idle": flag("idle", Idle()),  # no gun is charging, firing a beam or in the middle of a volley
    "volleys": Volleys,  # checked after the guns: this many volleys fired in the state
}


def parse_exit(data: dict[str, Any]) -> Exit:
    fields = dict(data)
    to = fields.pop("to")
    then = tuple(parse_action(action) for action in fields.pop("then", []))
    go_on, recheck = fields.pop("go_on", False), fields.pop("recheck", False)
    for name in fields:
        if name not in CONDITIONS:
            raise UnknownConditionError(name)
    conditions = tuple(CONDITIONS[name](value) for name, value in fields.items())
    return Exit(to, conditions, then, go_on, recheck)
