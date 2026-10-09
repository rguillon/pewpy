"""The guns and the missiles, their barrels pointing forward (towards the nose): their tips are the ship's weapons.

Guns: barrels, cannons, gatlings, lasers and a railgun on the nose; turrets and flak guns on top; pods under a wing;
guns on its tips; a cannon or a sponson on one side (lopsided ships). Missiles: under a wing, on its tip, in racks on
top, a launcher on one side.
"""

from pewpy.generators.models.parts.part import Part, Sketch


def barrels(name: str, xs: list[int], long: int) -> Part:
    """Build barrels `long` cubes at each x of `xs` (mirrored), out of a dark mount on the nose."""
    sketch = Sketch()
    reach = max(xs)
    sketch.box(-reach, reach, 0, 1, 0, 0, "N")
    for x in xs:
        sketch.box(x, x, 2, long + 1, 0, 0, "r")
        sketch.weapon("gun", x, long + 1, 0)
    count = {1: "One barrel", 2: "Two barrels", 3: "Three barrels"}[len({*xs, *(-x for x in xs)})]
    return sketch.part(name, "gun", "nose", f"{count}, {long} cubes long, on the nose.")


def cannon(name: str, long: int) -> Part:
    """Build a thick cannon on the nose: a breech, a barrel as thick as a cross, a muzzle brake."""
    sketch = Sketch()
    sketch.box(-1, 1, 0, 2, -1, 1, "N")
    sketch.box(-1, 1, 2, 2, 1, 1, "H")
    sketch.rod(3, long + 2, 1, "r")
    sketch.box(-1, 1, long + 2, long + 2, 0, 0, "N")
    sketch.weapon("cannon", 0, long + 2, 0)
    return sketch.part(name, "gun", "nose", f"A heavy cannon, {long} cubes long, on the nose.")


def gatling(name: str, long: int, *, under: bool = False) -> Part:
    """Build a gatling: a drum, three barrels round a spindle (on the nose, or in a pod under a wing)."""
    sketch = Sketch()
    z = -1 if under else 0
    if under:
        sketch.box(0, 0, 1, 2, 0, 0, "k")  # the pylon
    sketch.box(-1, 1, 0, 1, z - 1, z + 1, "N")
    sketch.box(0, 0, 2, long + 1, z, z, "k")  # the spindle
    sketch.box(0, 0, 2, long + 1, z + 1, z + 1, "r")
    sketch.box(-1, 1, 2, long + 1, z - 1, z - 1, "r")
    sketch.weapon("gatling", 0, long + 1, z)
    where = "in a pod under a wing" if under else "on the nose"
    return sketch.part(name, "gun", "under" if under else "nose", f"A gatling, three barrels {where}.")


def laser(name: str, long: int, mount: str = "nose") -> Part:
    """Build a beam emitter: a housing, a thin focusing barrel, a glowing lens at its tip."""
    sketch = Sketch()
    sketch.box(-1, 1, 0, 1, 0, 0, "N")
    sketch.box(0, 0, 0, 1, -1, 1, "N")
    sketch.box(0, 0, 2, long + 1, 0, 0, "W")
    sketch.box(-1, 1, long, long, 0, 0, "k")
    sketch.put(0, long + 2, 0, "G")
    sketch.weapon("laser", 0, long + 2, 0)
    where = {"nose": "on the nose", "tip": "on a wing's tip"}[mount]
    return sketch.part(name, "gun", mount, f"A beam emitter {where}, its lens glowing.")


def railgun(name: str, long: int) -> Part:
    """Build a railgun: two rails out of a breech, coils across them, a glow between their tips."""
    sketch = Sketch()
    sketch.box(-1, 1, 0, 1, -1, 1, "N")
    sketch.box(1, 1, 2, long + 1, 0, 0, "r")
    for y in range(3, long + 1, 2):
        sketch.box(-1, 1, y, y, 1, 1, "p")
    sketch.put(0, long + 1, 0, "G")
    sketch.weapon("cannon", 0, long + 1, 0)
    return sketch.part(name, "gun", "nose", f"A railgun, two rails {long} cubes long.")


def turret(name: str, size: int, xs: list[int]) -> Part:
    """Build a turret on top: a round base, a housing with a dome, barrels at each x of `xs` pointing forward."""
    sketch = Sketch()
    r = size + 1
    sketch.disc(r, r, 0, 0, "N")
    sketch.disc(r, r - 0.5, 1, size, "h")
    sketch.disc(r, max(0.5, r / 2), size + 1, size + 1, "S")
    tip = 2 * r + size + 1
    for x in xs:
        sketch.box(x, x, r, tip, size, size, "r")
        sketch.weapon("turret", x, tip, size)
    return sketch.part(name, "gun", "top", f"A turret on top, {len(set(xs) | {-x for x in xs})} barrels.")


def ball_turret(name: str) -> Part:
    """Build a ball turret hanging under the hull or a wing, a barrel pointing forward."""
    sketch = Sketch()
    sketch.box(-1, 1, 0, 2, 0, 0, "N")
    sketch.box(-1, 1, 0, 2, -1, -1, "t")
    sketch.box(0, 0, 0, 2, -2, -2, "t")
    sketch.box(0, 0, 3, 5, -1, -1, "r")
    sketch.weapon("turret", 0, 5, -1)
    return sketch.part(name, "gun", "under", "A ball turret hanging underneath.")


def flak(name: str, size: int) -> Part:
    """Build a flak gun on top: a box, two short thick barrels."""
    sketch = Sketch()
    sketch.housing(size + 1, 0, 2 + size, 0, size)
    sketch.box(size, size, 3 + size, 4 + 2 * size, size, size, "r")
    sketch.weapon("flak", size, 4 + 2 * size, size)
    return sketch.part(name, "gun", "top", "A flak gun on top, two short barrels.")


def gun_pod(name: str, long: int, kind: str) -> Part:
    """Build a pod hanging under a wing, a pylon above it, a barrel (or a lens) out of its front."""
    sketch = Sketch()
    sketch.box(0, 0, 1, 3, 0, 0, "k")
    sketch.rod(0, 4, 1, "N", z=-2)
    sketch.box(0, 0, 0, 4, -1, -1, "h")
    tip = 5 + long - 1
    if kind == "laser":
        sketch.box(0, 0, 5, tip - 1, -2, -2, "W")
        sketch.put(0, tip, -2, "G")
    else:
        sketch.box(0, 0, 5, tip, -2, -2, "r")
    sketch.weapon(kind, 0, tip, -2)
    return sketch.part(name, "gun", "under", f"A {kind} pod hanging under a wing.")


def tip_gun(name: str, long: int) -> Part:
    """Build a gun on a wing's tip: a slim fairing, a long barrel."""
    sketch = Sketch()
    sketch.box(0, 0, 0, 2, -1, 1, "N")
    sketch.box(0, 0, 3, long + 2, 0, 0, "r")
    sketch.weapon("gun", 0, long + 2, 0)
    return sketch.part(name, "gun", "tip", f"A gun on a wing's tip, {long} cubes long.")


def side_cannon(name: str, long: int) -> Part:
    """Build a big cannon on the hull's left side: a casemate, a thick barrel (lopsided ships)."""
    sketch = Sketch()
    sketch.box(-2, 0, 0, 4, -1, 1, "N", mirror=False)
    sketch.box(-2, 0, 0, 4, 1, 1, "H", mirror=False)
    sketch.box(-1, -1, 5, long + 4, 0, 0, "r", mirror=False)
    sketch.box(-1, -1, 5, 6, -1, -1, "r", mirror=False)
    sketch.weapon("cannon", -1, long + 4, 0, mirror=False)
    return sketch.part(name, "gun", "side", "A big cannon on one side (lopsided ships).")


def sponson(name: str) -> Part:
    """Build a sponson on the hull's left side: a gun deck, two barrels."""
    sketch = Sketch()
    sketch.box(-3, 0, 0, 3, 0, 0, "H", mirror=False)
    sketch.box(-3, 0, 0, 3, -1, -1, "N", mirror=False)
    for x in (-3, -1):
        sketch.box(x, x, 4, 6, 0, 0, "r", mirror=False)
        sketch.weapon("gun", x, 6, 0, mirror=False)
    return sketch.part(name, "gun", "side", "A sponson on one side, two barrels (lopsided ships).")


def missile(name: str, xs: list[int], long: int) -> Part:
    """Build missiles `long` cubes under a wing, at each x of `xs` (mirrored), on a rail, their warheads lit."""
    sketch = Sketch()
    reach = max(xs)
    sketch.box(-reach, reach, 1, 2, 0, 0, "k")
    for x in xs:
        sketch.box(x, x, 0, long - 1, -1, -1, "H")
        sketch.put(x, long, -1, "p")
        sketch.put(x, 0, -2, "W")
        sketch.weapon("missile", x, long, -1)
    many = "Two missiles" if reach else "A missile"
    return sketch.part(name, "missile", "under", f"{many} under a wing, {long + 1} cubes long.")


def rocket_pod(name: str, long: int) -> Part:
    """Build a round rocket pod under a wing, the rockets' heads showing on its front."""
    sketch = Sketch()
    sketch.box(0, 0, 1, 2, 0, 0, "k")
    sketch.rod(0, long - 1, 1.5, "N", z=-2)
    sketch.box(-1, 1, long - 1, long - 1, -2, -2, "p")
    sketch.box(0, 0, long - 1, long - 1, -3, -1, "p")
    sketch.weapon("missile", 0, long - 1, -2)
    return sketch.part(name, "missile", "under", "A rocket pod under a wing.")


def tip_missile(name: str, long: int) -> Part:
    """Build a missile on a wing's tip, its fins at the back."""
    sketch = Sketch()
    sketch.box(0, 0, 0, long - 1, 0, 0, "H")
    sketch.box(-1, 1, 0, 0, 0, 0, "W")
    sketch.box(0, 0, 0, 0, -1, 1, "W")
    sketch.put(0, long, 0, "p")
    sketch.weapon("missile", 0, long, 0)
    return sketch.part(name, "missile", "tip", "A missile on a wing's tip.")


def rack(name: str, half: int, rows: int) -> Part:
    """Build a missile rack on top: a box, the warheads of its tubes showing on its front."""
    sketch = Sketch()
    front = 2 + 2 * rows
    sketch.housing(half, 0, front, 0, rows)
    for x in range(0, half + 1, 2):
        for z in range(0, rows + 1, 2):
            sketch.put(x, front + 1, z, "p")
    sketch.weapon("missile", 0, front + 1, 0)
    return sketch.part(name, "missile", "top", "A missile rack on top, its warheads showing.")


def launcher(name: str) -> Part:
    """Build a missile launcher on the hull's left side: a box of tubes (lopsided ships)."""
    sketch = Sketch()
    sketch.box(-3, 0, 0, 4, -1, 1, "N", mirror=False)
    sketch.box(-3, 0, 0, 4, 1, 1, "h", mirror=False)
    for x in (-3, -1):
        for z in (-1, 1):
            sketch.put(x, 5, z, "p", mirror=False)
            sketch.weapon("missile", x, 5, z, mirror=False)
    return sketch.part(name, "missile", "side", "A box of missiles on one side (lopsided ships).")


def guns() -> list[Part]:
    """Return every gun."""
    return [
        barrels("barrel, short", [0], 2),
        barrels("barrel", [0], 4),
        barrels("barrel, long", [0], 6),
        barrels("twin barrels, short", [1], 2),
        barrels("twin barrels", [1], 4),
        barrels("twin barrels, wide", [2], 3),
        barrels("triple barrels", [0, 2], 3),
        cannon("cannon, short", 3),
        cannon("cannon", 6),
        gatling("gatling", 3),
        gatling("gatling, long", 5),
        gatling("gatling pod", 3, under=True),
        laser("beam emitter", 2),
        laser("beam emitter, long", 5),
        laser("tip emitter", 2, "tip"),
        railgun("railgun", 6),
        railgun("railgun, long", 9),
        turret("turret", 1, [0]),
        turret("twin turret", 1, [1]),
        turret("turret, big", 2, [0, 2]),
        ball_turret("ball turret"),
        flak("flak gun", 1),
        flak("flak gun, big", 2),
        gun_pod("gun pod", 2, "gun"),
        gun_pod("cannon pod", 4, "cannon"),
        gun_pod("laser pod", 3, "laser"),
        tip_gun("tip gun", 3),
        tip_gun("tip gun, long", 6),
        side_cannon("side cannon", 4),
        side_cannon("side cannon, long", 7),
        sponson("sponson"),
    ]


def missiles() -> list[Part]:
    """Return every missile."""
    return [
        missile("missile", [0], 4),
        missile("missile, long", [0], 7),
        missile("twin missiles", [1], 4),
        missile("twin missiles, wide", [2], 5),
        rocket_pod("rocket pod", 4),
        rocket_pod("rocket pod, long", 7),
        tip_missile("tip missile", 4),
        tip_missile("tip missile, long", 6),
        rack("missile rack", 1, 1),
        rack("missile rack, big", 2, 2),
        rack("missile rack, wide", 3, 1),
        launcher("side launcher"),
    ]
