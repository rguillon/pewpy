"""The details: vents, intakes, fins, antennas, sensors, tanks, armor, lights, machinery.

Most sit on top of a surface; intakes and armor on the hull's sides, drop tanks and ventral fins underneath.
"""

from pewpy.generators.models.parts.part import Part, Sketch


def slats(name: str, half: int, long: int) -> Part:
    """Build a vent: a dark frame, slats across it."""
    sketch = Sketch()
    sketch.box(-half - 1, half + 1, 0, long + 1, 0, 0, "N")
    for y in range(1, long + 1):
        sketch.box(-half, half, y, y, 0, 0, "k" if y % 2 else "r")
    return sketch.part(name, "vent", "top", f"A vent, {long} slats across.")


def round_vent(name: str, radius: int) -> Part:
    """Build a round vent: a dark ring, a grille in a cross."""
    sketch = Sketch()
    sketch.disc(radius, radius, 0, 0, "N")
    sketch.box(-radius + 1, radius - 1, radius, radius, 0, 0, "k")
    sketch.box(0, 0, 1, 2 * radius - 1, 0, 0, "k")
    return sketch.part(name, "vent", "top", "A round vent, a grille in a cross.")


def grille(name: str, long: int) -> Part:
    """Build a grille along the hull: a strip of dark and light cubes, one wide."""
    sketch = Sketch()
    for y in range(long):
        sketch.put(0, y, 0, "k" if y % 2 else "N")
    return sketch.part(name, "vent", "top", f"A grille strip, {long} cubes long.")


def louvres(name: str, gap: int) -> Part:
    """Build two small vents side by side, a bar between them."""
    sketch = Sketch()
    sketch.box(-gap, gap, 0, 0, 0, 0, "N")
    sketch.box(gap, gap + 1, 0, 3, 0, 0, "N")
    sketch.box(gap, gap + 1, 1, 1, 0, 0, "k")
    sketch.box(gap, gap + 1, 3, 3, 0, 0, "k")
    return sketch.part(name, "vent", "top", "Two small vents side by side.")


def exhausts(name: str, count: int) -> Part:
    """Build exhaust ports in a row across, each a short dark pipe."""
    sketch = Sketch()
    reach = count - 1
    sketch.box(-reach, reach, 0, 1, 0, 0, "N")
    for x in range(-reach, reach + 1, 2):
        sketch.put(x, 0, 1, "o", mirror=False)
    return sketch.part(name, "vent", "top", f"{count} exhaust ports in a row.")


def scoop(name: str, long: int, tall: int, mount: str) -> Part:
    """Build an air intake: a box, its dark mouth on its front."""
    sketch = Sketch()
    if mount == "side":
        sketch.box(-1, 0, 0, long - 1, 0, tall - 1, "N", mirror=False)
        sketch.box(-1, -1, long - 1, long - 1, 0, tall - 1, "k", mirror=False)
        sketch.box(-1, -1, 0, long - 2, tall - 1, tall - 1, "H", mirror=False)
    elif mount == "top":
        sketch.box(-1, 1, 0, long - 1, 0, tall - 1, "N")
        sketch.box(-1, 1, 0, long - 2, tall - 1, tall - 1, "H")
        sketch.box(0, 0, long - 1, long - 1, 0, tall - 1, "k")
    else:  # under
        sketch.box(-1, 1, 0, long - 1, -tall + 1, 0, "N")
        sketch.box(0, 0, long - 1, long - 1, -tall + 1, 0, "k")
    where = {"side": "on a side", "top": "on top", "under": "underneath"}[mount]
    return sketch.part(name, "intake", mount, f"An air intake {where}, {long} cubes long.")


def fin(name: str, long: int, tall: int, *, x: int = 0, swept: bool = True, under: bool = False) -> Part:
    """Build an upright fin (a pair `x` cubes each side of the middle), tallest at its back; a light on its top."""
    sketch = Sketch()
    sign = -1 if under else 1
    for y in range(long):
        height = max(1, round(tall * (1 - y / long) + 0.5)) if swept else tall
        for z in range(height):
            sketch.put(x, y, sign * z, "S" if y else "k")
    sketch.put(x, 0, sign * tall, "R")
    if x:
        sketch.box(-x + 1, x - 1, 1, 1, 0, 0, "N")  # a bar joining the pair
    pair = "Two fins" if x else ("A ventral fin" if under else "A fin")
    return sketch.part(name, "fin", "under" if under else "top", f"{pair}, {tall} cubes high.")


def shark_fin(name: str, long: int, tall: int) -> Part:
    """Build a fin leaning back: its top runs behind its root."""
    sketch = Sketch()
    for z in range(tall):
        for y in range(long - z):
            sketch.put(0, y - z // 2 + tall // 2, z, "S" if y else "k")
    return sketch.part(name, "fin", "top", f"A fin leaning back, {tall} cubes high.")


def whip(name: str, tall: int, x: int = 0) -> Part:
    """Build a thin mast (a pair `x` cubes each side of the middle), its tip glowing."""
    sketch = Sketch()
    sketch.box(-x, x, 0, 0, 0, 0, "N")
    sketch.box(x, x, 0, 0, 1, tall, "k")
    sketch.put(x, 0, tall + 1, "R")
    return sketch.part(name, "antenna", "top", f"{'Two masts' if x else 'A mast'}, {tall + 1} cubes high.")


def mast(name: str, tall: int) -> Part:
    """Build a mast with a crossbar, lights on its ends."""
    sketch = Sketch()
    sketch.box(0, 0, 0, 0, 0, tall, "k")
    sketch.box(-1, 1, 0, 0, tall - 1, tall - 1, "W")
    sketch.box(2, 2, 0, 0, tall - 1, tall - 1, "R")
    return sketch.part(name, "antenna", "top", "A mast with a crossbar.")


def spikes(name: str, count: int) -> Part:
    """Build a row of short spikes along the hull."""
    sketch = Sketch()
    sketch.box(0, 0, 0, 2 * count - 2, 0, 0, "N")
    for y in range(0, 2 * count - 1, 2):
        sketch.box(0, 0, y, y, 1, 2, "k")
    return sketch.part(name, "antenna", "top", f"{count} short spikes in a row.")


def aerial(name: str, long: int) -> Part:
    """Build a wire aerial along the hull on two posts."""
    sketch = Sketch()
    sketch.box(0, 0, 0, 0, 0, 1, "k")
    sketch.box(0, 0, long - 1, long - 1, 0, 1, "k")
    sketch.box(0, 0, 0, long - 1, 2, 2, "k")
    sketch.put(0, long - 1, 3, "R")
    return sketch.part(name, "antenna", "top", "A wire aerial on two posts.")


def sensor_dome(name: str, radius: int) -> Part:
    """Build a radar dome: a round base, a dome, a light on top."""
    sketch = Sketch()
    sketch.disc(radius, radius, 0, 0, "t")
    for z in range(1, radius + 1):
        sketch.disc(radius, max(0.5, radius * (1 - (z / (radius + 1)) ** 2) ** 0.5), z, z, "t")
    sketch.put(0, radius, radius + 1, "R")
    return sketch.part(name, "sensor", "top", f"A radar dome, {2 * radius + 1} cubes across.")


def rotodome(name: str) -> Part:
    """Build a rotating radar disc on a pylon."""
    sketch = Sketch()
    sketch.box(0, 0, 2, 2, 0, 1, "k")
    sketch.disc(2, 2, 2, 2, "t")
    sketch.box(-2, 2, 2, 2, 2, 2, "p")
    return sketch.part(name, "sensor", "top", "A radar disc on a pylon.")


def sensor_ball(name: str) -> Part:
    """Build a glowing sensor ball on a dark base."""
    sketch = Sketch()
    sketch.box(-1, 1, 0, 2, 0, 0, "N")
    sketch.box(0, 0, 1, 1, 1, 1, "R")
    return sketch.part(name, "sensor", "top", "A glowing sensor on a base.")


def blister(name: str, long: int) -> Part:
    """Build a long low sensor blister."""
    sketch = Sketch()
    sketch.box(-1, 1, 0, long - 1, 0, 0, "S")
    sketch.box(0, 0, 1, long - 2, 1, 1, "S")
    sketch.put(0, long - 1, 1, "R")
    return sketch.part(name, "sensor", "top", f"A sensor blister, {long} cubes long.")


def sensor_bar(name: str, half: int) -> Part:
    """Build a bar of sensors across, alternately lit."""
    sketch = Sketch()
    sketch.box(-half, half, 0, 0, 0, 0, "N")
    for x in range(0, half + 1, 2):
        sketch.put(x, 0, 1, "R")
    return sketch.part(name, "sensor", "top", "A bar of sensors across.")


def tank(name: str, long: int, radius: float, x: int = 0) -> Part:
    """Build a fuel tank lying along the hull (a pair `x` cubes each side of the middle), banded."""
    sketch = Sketch()
    z = round(radius)
    sketch.rod(0, long - 1, radius, "H", z=z, x=x)
    for y in range(1, long - 1, 3):
        sketch.rod(y, y, radius, "N", z=z, x=x)
    sketch.rod(long - 1, long - 1, max(0.5, radius - 1), "p", z=z, x=x)
    if x:
        sketch.box(-x, x, 1, 1, 0, 0, "k")
    return sketch.part(name, "tank", "top", f"{'Two fuel tanks' if x else 'A fuel tank'}, {long} cubes long.")


def sphere_tank(name: str, radius: int) -> Part:
    """Build a round tank on a saddle."""
    sketch = Sketch()
    for z in range(2 * radius + 1):
        dz = z - radius
        sketch.disc(radius, max(0.5, (radius * radius - dz * dz) ** 0.5), z, z, "H")
    sketch.box(-1, 1, radius, radius, 0, 0, "N")
    return sketch.part(name, "tank", "top", "A round tank.")


def drop_tank(name: str, long: int) -> Part:
    """Build a drop tank hanging under a wing, pointed at both ends."""
    sketch = Sketch()
    sketch.box(0, 0, 2, long - 3, 0, 0, "k")
    sketch.box(0, 0, 0, long - 1, -2, -2, "H")
    sketch.rod(1, long - 2, 1, "H", z=-2)
    sketch.put(0, long - 1, -2, "p")
    return sketch.part(name, "tank", "under", f"A drop tank under a wing, {long} cubes long.")


def plate(name: str, long: int, tall: int) -> Part:
    """Build an armor plate on the hull's side, its ends darker."""
    sketch = Sketch()
    sketch.box(-1, 0, 0, long - 1, -tall, tall, "N", mirror=False)
    sketch.box(-1, -1, 0, 0, -tall, tall, "k", mirror=False)
    sketch.box(-1, -1, long - 1, long - 1, -tall, tall, "k", mirror=False)
    return sketch.part(name, "armor", "side", f"An armor plate on a side, {long} cubes long.")


def spaced(name: str, long: int) -> Part:
    """Build spaced armor on the hull's side: plates on braces, a gap behind them."""
    sketch = Sketch()
    for y in range(0, long, 3):
        sketch.box(-1, 0, y, y, 0, 0, "k", mirror=False)
    sketch.box(-2, -2, 0, long - 1, -1, 1, "N", mirror=False)
    return sketch.part(name, "armor", "side", "Spaced armor plates on braces.")


def deck_plate(name: str, half: int, long: int) -> Part:
    """Build a raised armor plate on top, its rim lighter."""
    sketch = Sketch()
    sketch.housing(half, 0, long - 1, 0, 0)
    return sketch.part(name, "armor", "top", f"A raised plate on top, {long} cubes long.")


def lamp(name: str, char: str) -> Part:
    """Build a small light on a dark base."""
    sketch = Sketch()
    sketch.put(0, 0, 0, "N")
    sketch.put(0, 0, 1, char)
    return sketch.part(name, "light", "top", "A small light.")


def beacon(name: str, tall: int) -> Part:
    """Build a beacon: a post, a glowing light on it."""
    sketch = Sketch()
    sketch.box(0, 0, 0, 0, 0, tall - 1, "k")
    sketch.put(0, 0, tall, "R")
    return sketch.part(name, "light", "top", "A beacon on a post.")


def light_strip(name: str, long: int) -> Part:
    """Build a strip of lights along the hull."""
    sketch = Sketch()
    for y in range(long):
        sketch.put(0, y, 0, "p" if y % 2 else "N")
    return sketch.part(name, "light", "top", f"A strip of lights, {long} cubes long.")


def panel(name: str, half: int, long: int) -> Part:
    """Build a box of machinery: a housing, a seam across it."""
    sketch = Sketch()
    sketch.box(-half, half, 0, long - 1, 0, 1, "t")
    sketch.box(-half, half, long // 2, long // 2, 1, 1, "k")
    sketch.put(half, long - 1, 1, "p")
    return sketch.part(name, "greeble", "top", "A box of machinery.")


def pipes(name: str, long: int, x: int) -> Part:
    """Build a pipe along the hull on low supports (a pair `x` cubes each side of the middle)."""
    sketch = Sketch()
    sketch.box(x, x, 0, long - 1, 1, 1, "r")
    for y in range(0, long, 3):
        sketch.put(x, y, 0, "N")
    if x:
        sketch.box(-x, x, 0, 0, 0, 0, "N")
    return sketch.part(name, "greeble", "top", f"{'Two pipes' if x else 'A pipe'} along the hull.")


def details() -> list[Part]:
    """Return every detail."""
    return [
        slats("vent, small", 1, 3),
        slats("vent", 1, 5),
        slats("vent, wide", 2, 4),
        slats("vent, long", 1, 8),
        slats("vent, big", 3, 6),
        round_vent("round vent", 2),
        round_vent("round vent, big", 3),
        grille("grille strip", 6),
        grille("grille strip, long", 10),
        louvres("louvres", 1),
        louvres("louvres, wide", 3),
        exhausts("exhaust ports", 2),
        exhausts("exhaust ports, row", 3),
        scoop("side intake, small", 3, 1, "side"),
        scoop("side intake", 4, 2, "side"),
        scoop("side intake, long", 7, 2, "side"),
        scoop("side intake, big", 5, 3, "side"),
        scoop("dorsal intake", 4, 2, "top"),
        scoop("dorsal intake, long", 6, 2, "top"),
        scoop("chin intake", 4, 2, "under"),
        fin("fin, tiny", 3, 1),
        fin("fin, small", 3, 2),
        fin("fin", 4, 3),
        fin("fin, tall", 5, 5),
        fin("fin, long", 8, 3),
        fin("square fin", 3, 3, swept=False),
        fin("twin fins", 4, 3, x=2),
        fin("twin fins, wide", 4, 3, x=4),
        fin("twin fins, tall", 5, 4, x=2),
        shark_fin("shark fin", 5, 4),
        fin("ventral fin", 4, 2, under=True),
        whip("stub antenna", 0),
        whip("whip antenna", 2),
        whip("whip antenna, tall", 4),
        whip("twin whips", 3, x=2),
        mast("mast", 3),
        spikes("spike array", 3),
        spikes("spike array, long", 5),
        aerial("wire aerial", 6),
        sensor_dome("radar dome, small", 1),
        sensor_dome("radar dome", 2),
        sensor_dome("radar dome, big", 3),
        rotodome("rotodome"),
        sensor_ball("sensor ball"),
        blister("sensor blister", 4),
        blister("sensor blister, long", 7),
        sensor_bar("sensor bar", 2),
        sensor_bar("sensor bar, wide", 4),
        tank("fuel tank, small", 4, 1),
        tank("fuel tank", 6, 1),
        tank("fuel tank, big", 8, 1.5),
        tank("twin tanks", 5, 1, x=2),
        tank("twin tanks, long", 8, 1, x=3),
        sphere_tank("round tank", 1),
        sphere_tank("round tank, big", 2),
        drop_tank("drop tank", 6),
        drop_tank("drop tank, long", 9),
        plate("armor plate, short", 4, 1),
        plate("armor plate", 7, 1),
        plate("armor plate, long", 10, 1),
        plate("armor plate, tall", 6, 2),
        spaced("spaced armor", 7),
        deck_plate("deck plate", 1, 4),
        deck_plate("deck plate, wide", 2, 6),
        lamp("running light", "p"),
        lamp("sensor light", "R"),
        beacon("beacon", 2),
        beacon("beacon, tall", 4),
        light_strip("light strip", 5),
        light_strip("light strip, long", 9),
        panel("machinery box", 1, 3),
        panel("machinery box, big", 2, 5),
        pipes("pipe", 6, 0),
        pipes("twin pipes", 8, 2),
    ]
