"""What enemies do once (02-enemies.md), each action in its own module: when an enemy appears (EnemySpec.start) or
goes from a state to another (Exit.then). An action is `action(enemy, action, target)`: the enemy, its Action (see
pewpy.game.enemies.spec) and the player; it returns what it created (bullets, enemies). The enemies' descriptions
name them (Action.type); ACTIONS gives each name its function. Independent from rendering.
"""

from collections.abc import Callable
from typing import TYPE_CHECKING

from pewpy.game.enemies.actions.aim import aim
from pewpy.game.enemies.actions.die import die
from pewpy.game.enemies.actions.fire import fire
from pewpy.game.enemies.actions.relocate import relocate
from pewpy.game.enemies.actions.sway import sway
from pewpy.game.enemies.actions.swerve import swerve
from pewpy.game.enemies.actions.to_bottom import to_bottom
from pewpy.game.enemies.actions.toward_middle import toward_middle
from pewpy.game.enemies.actions.velocity import velocity
from pewpy.game.entities import Entity

if TYPE_CHECKING:
    from pewpy.game.enemies.enemy import Enemy
    from pewpy.game.enemies.spec import Action

__all__ = ["ACTIONS", "ActionFunction"]
ActionFunction = Callable[["Enemy", "Action", Entity], list[Entity]]
ACTIONS: dict[str, ActionFunction] = {
    "velocity": velocity,
    "toward_middle": toward_middle,
    "aim": aim,
    "swerve": swerve,
    "sway": sway,
    "relocate": relocate,
    "to_bottom": to_bottom,
    "fire": fire,
    "die": die,
}
