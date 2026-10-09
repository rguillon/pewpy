"""The catalog of built-in parts every ship is assembled from: the player's, the enemies', the bosses'.

Hulls, wings, cockpits, engines, guns, missiles and details. Every part is drawn once, by hand in code, and named ("dart
hull, large", "twin barrels, short", "radar dome"...); the ship maker (pewpy.generators.models.ships.placing) picks
among them and places them, and assembles a boss's destroyable parts from them (see ships/modules.py). Each family in
its own module: hulls.py, wings.py, cockpits.py, engines.py, weapons.py (guns and missiles), heavy_weapons.py (gigantic
guns and missile batteries), details.py (vents, intakes, fins, antennas, sensors, tanks, armor, lights, machinery).
part.py: what a part is.
"""

from functools import cache

from pewpy.generators.models.parts.cockpits import cockpits
from pewpy.generators.models.parts.details import details
from pewpy.generators.models.parts.engines import engines
from pewpy.generators.models.parts.heavy_weapons import heavy_guns, heavy_missiles
from pewpy.generators.models.parts.hulls import hulls
from pewpy.generators.models.parts.part import MOUNTS, Part
from pewpy.generators.models.parts.weapons import guns, missiles
from pewpy.generators.models.parts.wings import wings

KINDS = {  # the families of parts, in the catalog's order, and their titles
    "hull": "Hulls",
    "wing": "Wings",
    "cockpit": "Cockpits",
    "engine": "Engines",
    "gun": "Guns",
    "missile": "Missiles",
    "vent": "Vents",
    "intake": "Intakes",
    "fin": "Fins",
    "antenna": "Antennas",
    "sensor": "Sensors",
    "tank": "Tanks",
    "armor": "Armor",
    "light": "Lights",
    "greeble": "Machinery",
}


@cache
def catalog() -> dict[str, Part]:
    """Return every built-in part, by name: by kind (see KINDS), in each module's order."""
    every = [
        *hulls(),
        *wings(),
        *cockpits(),
        *engines(),
        *guns(),
        *heavy_guns(),
        *missiles(),
        *heavy_missiles(),
        *details(),
    ]
    ordered = sorted(every, key=lambda part: list(KINDS).index(part.kind))  # stable: each kind keeps its order
    return {part.name: part for part in ordered}


def of_kind(kind: str, mount: str | None = None) -> list[Part]:
    """Return the parts of a kind (see KINDS), only those mounting a way (see MOUNTS) if `mount`."""
    return [part for part in catalog().values() if part.kind == kind and mount in (None, part.mount)]


__all__ = ["KINDS", "MOUNTS", "Part", "catalog", "of_kind"]
