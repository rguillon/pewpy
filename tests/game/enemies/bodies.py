"""A stand-in enemy body, to test what works on any Body without a whole Enemy."""

from dataclasses import dataclass

from pewpy.game.enemies.body import Body
from pewpy.game.entities import Entity
from pewpy.game.weapons.guns import Shooter


@dataclass(eq=False)
class StandIn(Body):
    """A body whose full health, span, visits and destroyed parts are set as told."""

    full: float = 3.0
    span: float = 0.05
    entered: int = 1
    lost: tuple[str, ...] = ()

    @property
    def full_health(self) -> float:
        return self.full

    @property
    def half_span(self) -> float:
        return self.span

    @property
    def visits(self) -> int:
        return self.entered

    def destroyed(self, part: str) -> bool:
        return part in self.lost

    def shooter(self, target: Entity) -> Shooter:
        return Shooter(self, target, on_screen=self.on_screen)
