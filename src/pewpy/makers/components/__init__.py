"""Built-in parts: small 3D pieces of machinery, stamped on ships and bosses, each in its own module.

Weapons (a turret, a twin cannon, a gatling, a missile rack, a flak gun, a beam emitter), an engine, and details (a
reactor, a radar, an antenna, a sensor dome, a vent, a radiator, exhaust stacks, a fuel tank). Each is a function
(rng, size) -> Piece (piece.py): `size` 1 for a ship's, more on a boss or as a boss's destroyable part; its weapons'
barrel tips and its engine's nozzle come with it. A boss's destroyable parts are built from PART_COMPONENTS, a boss's
core and the enemies' hulls get DETAILS and WEAPONS (see pewpy.makers.bosses.greebles, pewpy.makers.ships.kit.extras).
"""

from collections.abc import Callable

from pewpy.makers.common.geometry import Rng
from pewpy.makers.components.antenna import antenna
from pewpy.makers.components.beam import beam
from pewpy.makers.components.dome import dome
from pewpy.makers.components.engine import engine
from pewpy.makers.components.flak import flak
from pewpy.makers.components.gatling import gatling
from pewpy.makers.components.missile_rack import missile_rack
from pewpy.makers.components.piece import Piece
from pewpy.makers.components.radar import radar
from pewpy.makers.components.radiator import radiator
from pewpy.makers.components.reactor import reactor
from pewpy.makers.components.stack import stack
from pewpy.makers.components.tank import tank
from pewpy.makers.components.turret import turret
from pewpy.makers.components.twin_cannon import twin_cannon
from pewpy.makers.components.vent import vent

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
