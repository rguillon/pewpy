"""What enemies do once (02-enemies.md), each action in its own module.

An action is done when an enemy appears (EnemySpec.start) or goes from a state to another (Exit.then), see Action.do
in action.py. Independent from rendering.

The enemies' descriptions name them (`type`, with the action's fields next to it); ACTIONS gives each name its class
and `parse_action` reads one.
"""

from typing import Any

from pewpy.game.enemies.actions.action import Action
from pewpy.game.enemies.actions.aim import Aim
from pewpy.game.enemies.actions.die import Die
from pewpy.game.enemies.actions.fire import Fire
from pewpy.game.enemies.actions.relocate import Relocate
from pewpy.game.enemies.actions.sway import Sway
from pewpy.game.enemies.actions.swerve import Swerve
from pewpy.game.enemies.actions.to_bottom import ToBottom
from pewpy.game.enemies.actions.toward_middle import TowardMiddle
from pewpy.game.enemies.actions.velocity import Velocity
from pewpy.game.enemies.errors import UnknownNameError
from pewpy.game.weapons.guns import parse_gun

__all__ = [
    "ACTIONS",
    "Action",
    "Aim",
    "Die",
    "Fire",
    "Relocate",
    "Sway",
    "Swerve",
    "ToBottom",
    "TowardMiddle",
    "Velocity",
    "parse_action",
]
ACTIONS: dict[str, type[Action]] = {
    "velocity": Velocity,
    "toward_middle": TowardMiddle,
    "aim": Aim,
    "swerve": Swerve,
    "sway": Sway,
    "relocate": Relocate,
    "to_bottom": ToBottom,
    "fire": Fire,
    "die": Die,
}


def parse_action(data: dict[str, Any]) -> Action:
    """Read an action: its `type` and its fields (a gun written as parse_gun reads it)."""
    fields = dict(data)
    kind = fields.pop("type")
    if kind not in ACTIONS:
        raise UnknownNameError("action", kind)  # noqa: EM101 - the error builds its message
    if "gun" in fields:
        fields["gun"] = parse_gun(fields["gun"])
    return ACTIONS[kind](**fields)
