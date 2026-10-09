"""A boss's destroyable parts: modules assembled at random from the catalog's parts (pewpy.generators.models.parts).

A module is a platform (a short, wide hull, cut flat underneath), its main piece standing on it (a part of the module's
kind, see KINDS: a turret, a cannon, a missile battery, a beam emitter, a sensor, a fuel tank), and round it, in
mirrored pairs: guns on the platform's front (on a gun module), armor on its sides, details on its deck (vents, sensors,
antennas, tanks, lights, machinery), sometimes stub wings. It's put together like a ship (see
pewpy.generators.models.ships.ship), each part only where it fits, then joined into one piece. Modules are symmetric: a
boss's mirrored pair of parts shares one drawing.
"""

from collections.abc import Callable

from pewpy.generators.models.common.connect import bridges
from pewpy.generators.models.common.geometry import Rng, miss
from pewpy.generators.models.parts import Part, of_kind
from pewpy.generators.models.ships.ship import Ship, Spot

# The kinds of destroyable parts: what their main piece can be (the catalog's symmetric parts of it).
KINDS: dict[str, Callable[[], list[Part]]] = {
    "turret": lambda: of_kind("gun", "top"),  # turrets, flak guns, battleship turrets
    "cannon": lambda: [part for part in of_kind("gun", "nose") if part.weapons[0][0] != "laser"],
    "launcher": lambda: of_kind("missile", "top"),  # missile racks and batteries
    "emitter": lambda: [part for part in of_kind("gun", "nose") if part.weapons[0][0] == "laser"],
    "sensor": lambda: of_kind("sensor", "top"),
    "tank": lambda: of_kind("tank", "top"),
}
ARMED = ("turret", "cannon", "launcher", "emitter")  # the kinds whose main piece is a weapon
SIZES = {0: "tiny", 1: "small", 2: "medium", 3: "large", 4: "huge", 5: "gigantic", 6: "colossal"}
WIDTH = (3, 2)  # a module of size s wants a main piece about 3 + 2 s cubes wide *(placeholder)*
PLATFORMS = ("brick", "coffin", "lozenge", "hammer", "manta", "wedge")  # hull profiles with room on top
DETAILS = ("vent", "sensor", "antenna", "tank", "light", "greeble")  # the kinds of parts on its top
NOSE_GUNS = 0.6  # the chance of a gun module getting guns on its platform's front *(placeholder)*
ARMOR = 0.5  # of armor on its sides
WINGS = 0.25  # of stub wings
DETAIL_COUNT = (1, 3)  # pairs of details on top (or one in the middle)
TRIES = 10  # places tried for each part before giving up on it


def module(rng: Rng, kind: str, size: int) -> Part:
    """Assemble a destroyable part of a kind (see KINDS) and a size (0 to 6, see SIZES), its parts picked at random."""
    candidates = [part for part in KINDS[kind]() if part.symmetric]
    wide = WIDTH[0] + WIDTH[1] * size
    main = rng.choice(sorted(candidates, key=lambda part: miss((part.extent()[0],), (wide,)))[:3])
    width, length, _ = main.extent()
    if main.mount == "nose":  # a gun out of its front: its barrel reaching past the platform
        length = round(length * 0.6)
    ship = Ship()
    platforms = [part for part in of_kind("hull") if part.name.split()[0] in PLATFORMS]
    want = (width + 2, length * rng.uniform(1.0, 1.3))
    platform = _flat(rng.choice(sorted(platforms, key=lambda part: miss(part.extent()[:2], want))[:3]))
    ship.place(platform, [Spot(0, 0, 0)])
    deck = platform.high[1] + 1  # its length
    back = round(deck * 0.15) if main.mount == "nose" else max(0, (deck - length) // 2)
    ship.place(main, [_on_top(ship, main, 0, back)])
    if kind in ARMED and rng.random() < NOSE_GUNS and main.mount != "nose":
        _nose_guns(rng, ship, platform)
    if rng.random() < ARMOR:
        _sides(rng, ship, platform, [part for part in of_kind("armor", "side") if part.extent()[1] <= deck])
    if rng.random() < WINGS:
        _sides(rng, ship, platform, [part for part in of_kind("wing") if part.extent()[0] <= 4], overlap=0.5)
    for _ in range(rng.randint(*DETAIL_COUNT)):
        _detail(rng, ship, platform)
    return _joined(ship, f"{SIZES[size]} {kind} module", f"A destroyable {kind} on a platform, {SIZES[size]}.")


def _flat(hull: Part) -> Part:
    """Return a hull cut flat at its middle plane: its top half, a platform."""
    cells = {cell: char for cell, char in hull.cells.items() if cell[2] >= 0}
    return Part(hull.name, hull.kind, hull.mount, hull.description, cells)


def _on_top(ship: Ship, part: Part, x: int, y: int, *, flip: bool = False) -> Spot:
    """Return the spot standing a part on what's at (x, y) (its origin there): on the highest cube under it."""
    spot = Spot(x, y, 0, flip)
    columns = {spot.cell((px, py, 0))[:2] for px, py in part.footprint}
    under = [ship.tops[column] for column in columns if column in ship.tops] or [0]
    return Spot(x, y, max(under) + 1 - part.low[2], flip)


def _pair(part: Part, spot: Spot) -> list[Spot]:
    """Return a part's spot and its mirror image's (or the spot alone, on the axis)."""
    if spot.x == 0:
        return [spot] if part.symmetric else []
    return [spot, Spot(-spot.x, spot.y, spot.z, not spot.flip)]


def _put(ship: Ship, part: Part, spot: Spot, overlap: float = 0.0) -> bool:
    """Place a part and its mirror image if they fit; tell whether they did."""
    spots = _pair(part, spot)
    if not spots or not ship.fits(part, spots, overlap):
        return False
    ship.place(part, spots)
    return True


def _nose_guns(rng: Rng, ship: Ship, platform: Part) -> None:
    """Put small guns on the platform's front: one in the middle or a pair on its cheeks."""
    guns = [part for part in of_kind("gun", "nose") if part.extent()[1] <= 8 and part.extent()[0] <= 3]
    front = platform.high[1]
    half, top, bottom = platform.rows[front]
    for _ in range(TRIES):
        gun = rng.choice(guns)
        x = rng.choice([0, -half])
        y = front + 1 if x == 0 else front - rng.randint(1, 3)
        if _put(ship, gun, Spot(x, y, (top + bottom) // 2)):
            return


def _sides(rng: Rng, ship: Ship, platform: Part, parts: list[Part], overlap: float = 0.0) -> None:
    """Put a pair of side parts (armor plates, stub wings) against the platform's sides."""
    for _ in range(TRIES if parts else 0):
        part = rng.choice(parts)
        back = rng.randint(0, max(0, platform.high[1] - part.extent()[1] + 1))
        rows = [platform.rows[y] for y in range(back, back + part.extent()[1]) if y in platform.rows]
        if not rows:
            continue
        reach = max(half for half, _, _ in rows)
        middle = rows[len(rows) // 2]
        x = -reach - (1 if part.mount == "side" else 0)  # a wing's root sinks into the side
        if _put(ship, part, Spot(x, back, (middle[1] + middle[2]) // 2), overlap):
            return


def _detail(rng: Rng, ship: Ship, platform: Part) -> None:
    """Put a detail on the platform's deck (not on its main piece): in the middle, or a pair."""
    parts = [part for kind in DETAILS for part in of_kind(kind, "top") if part.extent()[2] <= 4]
    for _ in range(TRIES):
        part = rng.choice(parts)
        y = rng.randint(0, platform.high[1])
        half = platform.rows[y][0]
        x = 0 if part.symmetric and rng.random() < 0.3 else -rng.randint(part.high[0] + 1, max(part.high[0] + 1, half))
        spot = _on_top(ship, part, x, y)
        on_deck = spot.z + part.low[2] <= platform.high[2] + 1  # on the platform, not on its main piece
        if on_deck and _put(ship, part, spot):
            return


def _joined(ship: Ship, title: str, description: str) -> Part:
    """Return the module as one piece (struts joining what's apart), its back on y = 0, its bottom on z = 0."""
    cells = dict(ship.cells)
    for x, y, z in bridges(cells, lambda cell: (-cell[0], *cell[1:])):
        cells[x, y, z] = "N"
    back = min(y for _, y, _ in cells)
    bottom = min(z for _, _, z in cells)
    return Part(
        title,
        "module",
        "top",
        description,
        {(x, y - back, z - bottom): char for (x, y, z), char in cells.items()},
        tuple((kind, x, y - back, z - bottom) for kind, x, y, z in ship.weapons),
        tuple((x, y - back, z - bottom, width) for x, y, z, width in ship.nozzles),
    )
