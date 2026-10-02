"""The "fire" action."""

from dataclasses import dataclass

from pewpy.game.enemies.actions.action import Action
from pewpy.game.enemies.body import Body
from pewpy.game.entities import Entity
from pewpy.game.weapons.guns import Gun, fire


@dataclass(frozen=True)
class Fire(Action):
    """One shot of its `gun` (while on screen, unless the gun fires off screen too)."""

    gun: Gun

    def do(self, body: Body, target: Entity) -> list[Entity]:
        """Fire the gun once (unless the enemy is off the screen and the gun waits for it)."""
        if self.gun.off_screen == "fire" or body.on_screen:
            return fire(self.gun, body.shooter(target))
        return []
