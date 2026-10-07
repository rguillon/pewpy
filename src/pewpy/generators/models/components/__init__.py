"""Built-in parts: small 3D pieces of machinery, stamped on ships and bosses, each in its own module.

Weapons (a turret, a twin cannon, a gatling, a missile rack, a flak gun, a beam emitter), an engine, and details (a
reactor, a radar, an antenna, a sensor dome, a vent, a radiator, exhaust stacks, a fuel tank). Each is a function
(rng, size) -> Piece (piece.py): `size` 1 for a ship's, more on a boss or as a boss's destroyable part; its weapons'
barrel tips and its engine's nozzle come with it. A boss's destroyable parts are built from PART_COMPONENTS, a boss's
core and the enemies' hulls get DETAILS and WEAPONS (see
pewpy.generators.models.bosses.greebles, pewpy.generators.models.ships.kit.extras).
"""

from collections.abc import Callable

from pewpy.generators.models.common.geometry import Rng
from pewpy.generators.models.components.antenna import antenna
from pewpy.generators.models.components.beam import beam
from pewpy.generators.models.components.dome import dome
from pewpy.generators.models.components.engine import engine
from pewpy.generators.models.components.flak import flak
from pewpy.generators.models.components.gatling import gatling
from pewpy.generators.models.components.missile_rack import missile_rack
from pewpy.generators.models.components.piece import Piece
from pewpy.generators.models.components.radar import radar
from pewpy.generators.models.components.radiator import radiator
from pewpy.generators.models.components.reactor import reactor
from pewpy.generators.models.components.stack import stack
from pewpy.generators.models.components.tank import tank
from pewpy.generators.models.components.turret import turret
from pewpy.generators.models.components.twin_cannon import twin_cannon
from pewpy.generators.models.components.vent import vent

Component = Callable[[Rng, int], Piece]
WEAPONS: dict[str, Component] = {
    "turret": turret,
    "twin_cannon": twin_cannon,
    "gatling": gatling,
    "missile_rack": missile_rack,
    "flak": flak,
    "beam": beam,
}
DETAILS: dict[str, Component] = {
    "reactor": reactor,
    "radar": radar,
    "antenna": antenna,
    "dome": dome,
    "vent": vent,
    "radiator": radiator,
    "stack": stack,
    "tank": tank,
}
COMPONENTS: dict[str, Component] = {**WEAPONS, "engine": engine, **DETAILS}
PART_COMPONENTS = (*WEAPONS, "reactor", "radar")  # what a boss's destroyable parts can be

__all__ = ["COMPONENTS", "DETAILS", "PART_COMPONENTS", "WEAPONS", "Component", "Piece"]
