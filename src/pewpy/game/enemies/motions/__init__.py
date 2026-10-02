"""How enemies move (02-enemies.md), each motion in its own module: each motion of an enemy's state sets its speed
(or its place) every frame (Motion.apply, see motion.py); the enemy then moves with its speed. Independent from
rendering.

The enemies' descriptions name them (`type`, with the motion's fields next to it); MOTIONS gives each name its class
and `parse_motion` reads one.
"""

from typing import Any

from pewpy.game.enemies.errors import UnknownNameError
from pewpy.game.enemies.motions.accelerate import Accelerate
from pewpy.game.enemies.motions.bounce import Bounce
from pewpy.game.enemies.motions.circle import Circle
from pewpy.game.enemies.motions.erratic import Erratic
from pewpy.game.enemies.motions.forward import Forward
from pewpy.game.enemies.motions.motion import Motion
from pewpy.game.enemies.motions.patrol import Patrol
from pewpy.game.enemies.motions.scroll import Scroll
from pewpy.game.enemies.motions.steer import Steer
from pewpy.game.enemies.motions.swoop import Swoop
from pewpy.game.enemies.motions.track_x import TrackX
from pewpy.game.enemies.motions.weave import Weave
from pewpy.game.enemies.motions.zigzag import Zigzag

__all__ = [
    "MOTIONS",
    "Accelerate",
    "Bounce",
    "Circle",
    "Erratic",
    "Forward",
    "Motion",
    "Patrol",
    "Scroll",
    "Steer",
    "Swoop",
    "TrackX",
    "Weave",
    "Zigzag",
    "parse_motion",
]
MOTIONS: dict[str, type[Motion]] = {
    "scroll": Scroll,
    "patrol": Patrol,
    "bounce": Bounce,
    "weave": Weave,
    "swoop": Swoop,
    "circle": Circle,
    "steer": Steer,
    "forward": Forward,
    "accelerate": Accelerate,
    "track_x": TrackX,
    "zigzag": Zigzag,
    "erratic": Erratic,
}


def parse_motion(data: dict[str, Any]) -> Motion:
    """A motion: its `type` and its fields."""
    fields = dict(data)
    kind = fields.pop("type")
    if kind not in MOTIONS:
        raise UnknownNameError("motion", kind)
    return MOTIONS[kind](**fields)
