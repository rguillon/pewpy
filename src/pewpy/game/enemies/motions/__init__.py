"""How enemies move (02-enemies.md), each motion in its own module: each motion of an enemy's state sets its speed
(or its place) every frame; Enemy.move then moves it. Independent from rendering.

A motion is `motion(enemy, motion, dt, target, scroll_speed)`: the enemy, its Motion (see pewpy.game.enemies.spec),
the frame's time, the player and how fast the scenery under the enemy scrolls. The enemies' descriptions name them
(Motion.type); MOTIONS gives each name its function.
"""

from collections.abc import Callable
from typing import TYPE_CHECKING

from pewpy.game.enemies.motions.accelerate import accelerate
from pewpy.game.enemies.motions.bounce import bounce
from pewpy.game.enemies.motions.circle import circle
from pewpy.game.enemies.motions.erratic import erratic
from pewpy.game.enemies.motions.forward import forward
from pewpy.game.enemies.motions.patrol import patrol
from pewpy.game.enemies.motions.scroll import scroll
from pewpy.game.enemies.motions.steer import steer
from pewpy.game.enemies.motions.swoop import swoop
from pewpy.game.enemies.motions.track_x import track_x
from pewpy.game.enemies.motions.weave import weave
from pewpy.game.enemies.motions.zigzag import zigzag
from pewpy.game.entities import Entity

if TYPE_CHECKING:
    from pewpy.game.enemies.enemy import Enemy
    from pewpy.game.enemies.spec import Motion

__all__ = ["MOTIONS", "MotionFunction"]
MotionFunction = Callable[["Enemy", "Motion", float, Entity, float], None]
MOTIONS: dict[str, MotionFunction] = {
    "scroll": scroll,
    "patrol": patrol,
    "bounce": bounce,
    "weave": weave,
    "swoop": swoop,
    "circle": circle,
    "steer": steer,
    "forward": forward,
    "accelerate": accelerate,
    "track_x": track_x,
    "zigzag": zigzag,
    "erratic": erratic,
}
