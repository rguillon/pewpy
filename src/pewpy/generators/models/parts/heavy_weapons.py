"""The heavy weapons: gigantic guns and missile batteries for the biggest ships and the bosses.

Cannons as thick as a hull on the nose, a siege railgun, a mega gatling; battleship and dreadnought turrets and a
missile battery on top; cruise missiles under a wing. Their barrels' tips are the model's weapons.
"""

from pewpy.generators.models.parts.part import Part, Sketch


def big_cannon(name: str, radius: float, long: int) -> Part:
    """Build a cannon on the nose: an armored breech, a round barrel `radius` thick, bands, a muzzle brake."""
    sketch = Sketch()
    reach = round(radius) + 1
    breech = 2 * reach + 1
    sketch.box(-reach, reach, 0, breech, -reach, reach, "N")
    sketch.box(-reach, reach, 0, breech, reach, reach, "H")
    sketch.box(-reach + 1, reach - 1, 1, breech - 1, reach, reach, "h")
    sketch.box(-reach, reach, breech, breech, reach, reach, "p")  # a light on the breech's front edge
    tip = breech + long
    sketch.rod(breech + 1, tip, radius, "r")
    for y in range(breech + 3, tip - 2, 4):
        sketch.rod(y, y, radius + 0.5, "N")  # bands round the barrel
    sketch.rod(tip - 1, tip, radius + 0.8, "N")  # the muzzle brake
    sketch.rod(tip, tip, max(0.5, radius - 1), "k")  # the bore
    sketch.weapon("cannon", 0, tip, 0)
    return sketch.part(name, "gun", "nose", f"A cannon as thick as a hull, {long} cubes long, on the nose.")


def siege_railgun(name: str, long: int) -> Part:
    """Build a siege railgun: two heavy rails out of a capacitor bank, coils across them, a glow between their tips."""
    sketch = Sketch()
    sketch.box(-3, 3, 0, 4, -2, 2, "N")
    sketch.box(-3, 3, 0, 4, 2, 2, "H")
    sketch.box(-2, 2, 1, 3, 2, 2, "G")  # the capacitors, charged
    sketch.box(2, 2, 5, long + 4, -1, 1, "r")
    for y in range(6, long + 4, 2):
        sketch.box(-2, 2, y, y, 2, 2, "p")  # the coils
    sketch.box(-1, 1, long + 4, long + 4, 0, 0, "G")  # the glow between their tips
    sketch.weapon("cannon", 0, long + 4, 0)
    return sketch.part(name, "gun", "nose", f"A siege railgun, two heavy rails {long} cubes long.")


def mega_gatling(name: str, long: int) -> Part:
    """Build a mega gatling: a drum, six barrels round a thick spindle."""
    sketch = Sketch()
    sketch.box(-3, 3, 0, 3, -3, 3, "N")
    sketch.box(-3, 3, 0, 3, 3, 3, "H")
    sketch.rod(4, 5, 3, "k")  # the drum
    sketch.rod(6, long + 5, 1, "k")  # the spindle
    for x, z in ((0, 2), (2, 1), (2, -1), (0, -2)):
        sketch.box(x, x, 6, long + 5, z, z, "r")
    for y in range(8, long + 5, 4):
        sketch.rod(y, y, 2.6, "N")  # clamps round the barrels
    sketch.weapon("gatling", 0, long + 5, 0)
    return sketch.part(name, "gun", "nose", f"A mega gatling, six barrels {long} cubes long.")


def battleship_turret(name: str, half: int, barrels: list[int], long: int) -> Part:
    """Build a battleship turret on top: an armored house, sloped in front, long barrels at each x of `barrels`."""
    sketch = Sketch()
    deep = 2 * half + 2
    sketch.box(-half - 1, half + 1, 0, deep, 0, 0, "N")  # the barbette
    sketch.housing(half, 0, deep - 1, 1, 3)
    sketch.box(-half + 1, half - 1, deep, deep, 1, 2, "N")  # the sloped face
    sketch.box(-half + 1, half - 1, 1, 2, 4, 4, "S")  # the rangefinder
    sketch.put(half - 1, 1, 5, "R")
    tip = deep + long
    for x in barrels:
        sketch.box(x, x, deep, tip, 2, 2, "r")
        sketch.box(x, x, deep + 1, deep + 2, 2, 3, "N")  # the mantlet
        sketch.weapon("turret", x, tip, 2)
    count = len(set(barrels) | {-x for x in barrels})
    return sketch.part(name, "gun", "top", f"A battleship turret on top, {count} barrels {long} cubes long.")


def missile_battery(name: str, half: int, rows: int) -> Part:
    """Build a missile battery on top: an armored box, a grid of warheads on its front, blast vents on top."""
    sketch = Sketch()
    front = 4 + 2 * rows
    sketch.housing(half, 0, front, 0, rows + 1)
    for x in range(0, half + 1, 2):
        for z in range(0, rows + 1, 2):
            sketch.put(x, front + 1, z, "p")
    for y in range(2, front - 1, 2):
        sketch.box(-half + 1, half - 1, y, y, rows + 2, rows + 2, "k")
    sketch.weapon("missile", 0, front + 1, 0)
    return sketch.part(
        name, "missile", "top", f"A missile battery on top, {(half + 1) * (rows // 2 + 1)} tubes a side."
    )


def cruise_missile(name: str, long: int) -> Part:
    """Build a cruise missile under a wing: a long body, wings and fins, its warhead lit."""
    sketch = Sketch()
    sketch.box(0, 0, 3, long - 4, 0, 0, "k")  # the pylon
    sketch.rod(0, long - 1, 1, "H", z=-2)
    sketch.box(-2, 2, long // 2, long // 2 + 1, -2, -2, "W")  # its wings
    sketch.box(-1, 1, 0, 0, -2, -2, "W")
    sketch.box(0, 0, 0, 0, -4, 0, "W")
    sketch.rod(long, long, 0.5, "p", z=-2)
    sketch.weapon("missile", 0, long, -2)
    return sketch.part(name, "missile", "under", f"A cruise missile under a wing, {long + 1} cubes long.")


def heavy_guns() -> list[Part]:
    """Return every heavy gun."""
    return [
        big_cannon("heavy cannon", 1.5, 9),
        big_cannon("gigantic cannon", 2.0, 13),
        big_cannon("colossal cannon", 3.0, 18),
        siege_railgun("siege railgun", 14),
        mega_gatling("mega gatling", 9),
        battleship_turret("battleship turret", 3, [0, 2], 10),
        battleship_turret("dreadnought turret", 4, [1, 3], 14),
    ]


def heavy_missiles() -> list[Part]:
    """Return every heavy missile weapon."""
    return [
        missile_battery("missile battery", 4, 3),
        missile_battery("missile battery, huge", 6, 4),
        cruise_missile("cruise missile", 12),
    ]
