"""The "scroll" motion."""

from dataclasses import dataclass

from pewpy.game.enemies.body import Body
from pewpy.game.enemies.motions.motion import Motion
from pewpy.game.entities import Entity


@dataclass(frozen=True)
class Scroll(Motion):
    """Fixed to the ground (or driving on it, `plus` faster); `stop_x`: no sideways speed either."""

    plus: float = 0.0
    stop_x: bool = False

    def apply(self, body: Body, dt: float, target: Entity, scroll_speed: float) -> None:
        if self.stop_x:
            body.vx = 0.0
        body.vy = -scroll_speed + self.plus
