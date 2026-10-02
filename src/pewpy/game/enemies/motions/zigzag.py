"""The "zigzag" motion."""

from dataclasses import dataclass

from pewpy.game.enemies.body import Body
from pewpy.game.enemies.motions.bounce import Bounce
from pewpy.game.enemies.motions.motion import Motion
from pewpy.game.entities import Entity

EDGES = Bounce()


@dataclass(frozen=True)
class Zigzag(Motion):
    """Sideways at `speed`, first towards the player, turning back every `every` seconds and at the edges."""

    speed: float = 0.0
    every: float = 0.0

    def apply(self, body: Body, dt: float, target: Entity, scroll_speed: float) -> None:
        """Move sideways, turning at the edges and every `every` seconds."""
        body.turn_timer -= dt
        if body.vx == 0:
            body.vx = self.speed if target.x > body.x else -self.speed
        EDGES.apply(body, dt, target, scroll_speed)
        if body.turn_timer > 0:
            return
        body.turn_timer = self.every
        body.vx = -body.vx
