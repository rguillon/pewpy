"""The "parts" exit condition."""

from dataclasses import dataclass

from pewpy.game.enemies.body import Body
from pewpy.game.enemies.exits.condition import Condition
from pewpy.game.entities import Entity


@dataclass(frozen=True)
class Parts(Condition):
    """These parts are destroyed."""

    names: tuple[str, ...]

    def holds(self, body: Body, target: Entity) -> bool:
        """Tell whether the parts named are all destroyed."""
        return all(body.destroyed(name) for name in self.names)
