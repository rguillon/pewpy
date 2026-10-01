"""Remodel the game's ships in real 3D voxels (src/pewpy/models/<name>.json), from recipes written with tools/sculpt.py.

    make models                       # every model that has a recipe
    make models ARGS="player drone"   # just these

(or `uv run python -m tools.make_models ...`). Each recipe builds the ship in the same footprint as before (its
hitbox), with its engines where they were (their flames), and its own paint color so ships stay easy to tell
apart. The files it writes are ordinary 3D drawings: they can be edited by hand or in MagicaVoxel (`make voxels`),
but running a recipe again overwrites them.
"""

import argparse
import json
import os
from collections.abc import Callable
from pathlib import Path

from tools.sculpt import Model

MODELS = Path(__file__).resolve().parent.parent / "src" / "pewpy" / "models"

Recipe = Callable[[], tuple[Model, list[dict] | None]]
RECIPES: dict[str, Recipe] = {}


def recipe(name: str) -> Callable[[Recipe], Recipe]:
    def register(build: Recipe) -> Recipe:
        RECIPES[name] = build
        return build

    return register


def engines_of(name: str, z: float | None = None) -> list[dict]:
    """The model's engines as they are in its file now (their flames stay where they were), maybe raised to `z`."""
    data = json.loads((MODELS / f"{name}.json").read_text())
    engines = [dict(engine) for engine in data.get("engines", [])]
    if z is not None:
        for engine in engines:
            engine["z"] = z
    return engines


def ramp(t: float, start: float, end: float, until: float = 1.0) -> float:
    """From `start` at t = 0 to `end` at t = `until`, then `end`."""
    return start + (end - start) * min(t / until, 1.0) if until > 0 else end


# -- the player's ships (nose up: y = 0 is the nose)


SCALE = int(os.environ.get("MODELS_SCALE", "2"))  # cubes per unit (config.MODEL_VOXEL)


@recipe("player")
def vanguard() -> tuple[Model, list[dict] | None]:
    """Balanced: a pointed fuselage with a bubble canopy, swept wings, two ribbed engine nacelles."""
    m = Model(17, 18, SCALE)
    m.materials["paint"] = (0.25, 0.55, 1.0)
    # Fuselage: a pointed nose widening into the body; a raised back that slopes down to the tail.
    m.loft(
        (0, 16.5),
        lambda t: (
            ramp(t, 0.3, 2.3, 0.45),
            ramp(t, 0.5, 2.0, 0.35) - max(0.0, t - 0.8) * 2.5,
            ramp(t, -0.2, -1.5, 0.45),
            1.2,
        ),
        "hull",
    )
    # Canopy: a bubble of dark glass, its glint, a frame behind it.
    m.loft((4.0, 9.5), lambda t: (1.4 * (1 - abs(2 * t - 1) ** 4), 3.2 - abs(2 * t - 1) ** 2 * 1.2, 1.0, 0.7), "glass")
    m.paint(lambda x, y, z: abs(x - 8.5) < 0.5 and 5.0 <= y < 6.0 and z > 2.5, "glint")
    m.loft((9.5, 10.0), lambda t: (1.3, 2.7, 1.0, 0.5), "frame")
    # Spine along the back, a dorsal sensor behind it.
    m.loft((10, 15.5), lambda t: (0.5, 2.6 - t * 0.6, 1.5, 0.0), "hull_light")
    # Side intakes, dark, along the cockpit.
    m.box((6, 6), (8, 10), (0, 1), "vent")
    # Swept wings: thin, the tips rising a little, a lighter leading edge, a paint stripe, lights at the tips.
    wing = [(6.5, 7.0), (6.5, 15.0), (0.5, 14.0), (0.5, 11.5)]
    m.plate(wing, lambda x, y: (0, 0 if x > 3 else 0.5), "hull")
    m.plate([(6.5, 7.0), (6.5, 8.0), (0.5, 12.5), (0.5, 11.5)], lambda x, y: (0, 0 if x > 3 else 0.5), "hull_light")
    m.plate([(5.5, 11.0), (5.5, 12.0), (1.5, 13.0), (1.5, 12.0)], (0.5, 0.5), "paint")
    m.fill(lambda x, y, z: x < 0.5 and 12.0 <= y < 13.0 and 0 <= z < 1, (0, 1, 11, 14, 0, 1), "light")
    # Engine nacelles under the wing roots: ribbed, with dark nozzles.
    m.nacelle(5.5, (9, 17.5), -0.75, 1.6, "hull")
    for row in (11, 12.5, 14, 15.5):
        m.nacelle(5.5, (row, row + 0.5), -0.75, 1.75, "frame")
    m.nacelle(5.5, (17.5, 18), -0.75, 1.2, "vent")
    m.nacelle(5.5, (8.5, 9.5), -0.75, 1.1, "vent")  # intake at the front
    # Guns: short barrels at the wing roots.
    m.fill(lambda x, y, z: 6.0 <= x < 6.5 and 5.0 <= y < 8.0 and -0.5 <= z < 0, (6, 7, 5, 8, -1, 0), "metal")
    m.finish(seams=(10, 13), keep=frozenset({"glass", "glint", "paint", "light", "vent", "metal"}))
    return m, [
        {"x": 5, "y": 17, "width": 3.2, "length": 9, "towards": "bottom", "z": -0.75},
        {"x": 11, "y": 17, "width": 3.2, "length": 9, "towards": "bottom", "z": -0.75},
    ]


KEEP = frozenset({"glass", "glint", "paint", "light", "vent", "metal"})


def engine(x: float, y: float, width: float, length: float, towards: str, z: float = 0.0) -> dict:
    return {"x": x, "y": y, "width": width, "length": length, "towards": towards, "z": z}


def lights(m: Model, x: float, y: tuple[float, float], z: float = 0.0) -> None:
    """Running lights: small orange marks at x (and its mirror)."""
    m.fill(
        lambda px, py, pz: abs(px - x) < 0.3 and y[0] <= py < y[1] and z <= pz < z + 0.5,
        (x - 1, x + 1, *y, z - 1, z + 1),
        "light",
    )


def ribbed(m: Model, x: float, y: tuple[float, float], z: float, radius: float, step: float = 1.5) -> None:
    """A nacelle in hull grey, with dark ribs every `step`."""
    m.nacelle(x, y, z, radius, "hull")
    row = y[0] + step
    while row < y[1] - 0.5:
        m.nacelle(x, (row, row + 0.5), z, radius + 0.15, "frame")
        row += step


@recipe("player_heavy")
def juggernaut() -> tuple[Model, list[dict] | None]:
    """Heavy armor: a broad armored hull with a raised ridge, two big side pods, three engines."""
    m = Model(21, 21, SCALE)
    m.materials["paint"] = (0.212, 0.468, 0.85)
    # Main hull: a blunt prow, then broad and flat.
    m.loft((0, 19.5), lambda t: (ramp(t, 1.5, 4.5, 0.3), ramp(t, 1.0, 2.5, 0.25), -2.0, 1.5), "hull")
    # The armored ridge down the middle, the cockpit set into it.
    m.loft((1, 17), lambda t: (ramp(t, 0.6, 1.2, 0.2), ramp(t, 2.0, 4.0, 0.25), 1.0, 0.5), "hull_light")
    m.loft((4, 8), lambda t: (1.3, 3.6, 2.0, 0.6), "glass")
    m.paint(lambda x, y, z: abs(x - 10.5) < 0.5 and 5 <= y < 6 and z > 3, "glint")
    # Side pods: heavy armored blocks, ribbed, paint on their tops.
    m.loft((5, 19.5), lambda t: (1.8, 1.8, -1.8, 0.8), "hull", center=4.0)
    for row in range(7, 19, 2):
        m.loft((row, row + 0.5), lambda t: (1.95, 1.95, -1.95, 0.8), "frame", center=4.0)
    m.paint(lambda x, y, z: abs(x - 4.0) < 0.6 and 6 <= y < 17 and z > 1.4, "paint")
    # Stub wings with guns, lights at the tips.
    m.plate([(2.2, 10.0), (2.2, 16.0), (0.0, 15.0), (0.0, 11.0)], (0, 0), "hull")
    m.fill(lambda x, y, z: x < 1.0 and 8.0 <= y < 12 and 0 <= z < 0.5, (0, 1, 8, 12, -1, 1), "metal")
    lights(m, 0.25, (11.0, 11.5), 0.5)
    # Engines: three nozzles at the back.
    for x in (4.5, 10.5):
        m.nacelle(x, (19.5, 21), -0.25, 1.3, "frame")
        m.nacelle(x, (20.5, 21), -0.25, 0.9, "vent")
    m.finish(seams=(9, 13, 16), keep=KEEP)
    return m, [
        engine(10, 20, 3.2, 10, "bottom", -0.25),
        engine(4, 20, 3.2, 9, "bottom", -0.25),
        engine(16, 20, 3.2, 9, "bottom", -0.25),
    ]


@recipe("player_light")
def phantom() -> tuple[Model, list[dict] | None]:
    """Fast: a needle fuselage, a long canopy, a wide thin delta wing, one engine."""
    m = Model(15, 15, SCALE)
    m.materials["paint"] = (0.21, 0.56, 0.7)
    m.loft(
        (0, 14.5), lambda t: (ramp(t, 0.25, 1.6, 0.4), ramp(t, 0.25, 1.8, 0.4), ramp(t, -0.25, -1.0, 0.4), 0.8), "hull"
    )
    m.loft((3.0, 8.0), lambda t: (0.9 * (1 - abs(2 * t - 1) ** 4), 2.5 - abs(2 * t - 1) ** 2, 1.0, 0.5), "glass")
    m.paint(lambda x, y, z: abs(x - 7.5) < 0.5 and 4 <= y < 5 and z > 2.0, "glint")
    m.loft((8, 13), lambda t: (0.5, 2.0, 1.0, 0.0), "hull_light")
    # The delta: thin, swept, lighter leading edge, paint panels near the tips.
    m.plate([(6.0, 6.0), (6.0, 13.0), (0.0, 13.0), (0.0, 11.5)], (0, 0), "hull")
    m.plate([(6.0, 6.0), (6.0, 7.0), (0.0, 12.5), (0.0, 11.5)], (0, 0), "hull_light")
    m.plate([(4.0, 9.5), (4.0, 12.0), (2.0, 12.0), (2.0, 11.0)], (0.5, 0.5), "paint")
    lights(m, 0.25, (12.0, 12.5), 0.5)
    # Small canted fins at the tail.
    m.fin(5.75, [(10.5, 0.5), (13.5, 0.5), (13.5, 2.5), (12.0, 2.5)], "hull", thickness=0.5)
    # The engine.
    m.nacelle(7.5, (12.5, 15), -0.25, 1.1, "frame")
    m.nacelle(7.5, (14.5, 15), -0.25, 0.7, "vent")
    m.finish(seams=(10,), keep=KEEP)
    return m, [engine(7, 14, 3.0, 11, "bottom", -0.25)]


# -- enemies (they fly down: y = 0 is the tail, their nose at the bottom)


@recipe("drone")
def drone() -> tuple[Model, list[dict] | None]:
    """A small attack drone: an armored octagonal body, a red sensor eye, four weapon pods, one engine."""
    m = Model(15, 15, SCALE)
    m.materials["paint"] = (0.8, 0.16, 0.12)
    m.materials["eye"] = (1.0, 0.2, 0.1)
    octagon = [(4.5, 1.0), (10.5, 1.0), (14.0, 4.5), (14.0, 10.5), (10.5, 14.0), (4.5, 14.0), (1.0, 10.5), (1.0, 4.5)]
    m.plate(octagon, (-1, 0), "hull", mirror=False)
    # The raised core, chamfered, with the eye at its front.
    m.loft((3.5, 12.5), lambda t: (3.0, 2.0, 0.5, 1.2), "hull_light")
    m.loft((5.5, 10.5), lambda t: (1.6, 2.6, 1.0, 0.8), "hull")
    m.fill(lambda x, y, z: abs(x - 7.5) < 1.2 and 10.0 <= y < 11.5 and 1.0 <= z < 2.5, (6, 9, 10, 12, 0, 3), "eye")
    # A red band around the core.
    m.paint(lambda x, y, z: z > 0.6 and (4.0 <= y < 4.6 or 11.4 <= y < 12.0) and abs(x - 7.5) < 3, "paint")
    # Weapon pods on the sides, their muzzles forward.
    for x in (1.8,):
        m.nacelle(x, (4.5, 11.5), -0.5, 1.2, "frame")
        m.nacelle(x, (11.5, 13.5), -0.5, 0.5, "metal")
    m.paint(lambda x, y, z: x < 3.0 and 6 <= y < 9 and z > 0.4, "paint")
    lights(m, 1.0, (7.0, 8.0), 0.5)
    # The engine at the back.
    m.nacelle(7.5, (0, 3.5), 0.0, 1.3, "frame")
    m.nacelle(7.5, (0, 0.5), 0.0, 0.9, "vent")
    m.finish(seams=(7.5,), keep=KEEP | {"eye"})
    return m, [engine(7, 0, 3.2, 6, "top")]


@recipe("gunship")
def gunship() -> tuple[Model, list[dict] | None]:
    """A heavy gunship: a broad armored hull, a bridge, engine pods on outriggers, a big cannon at the front."""
    m = Model(29, 21, SCALE)
    m.materials["paint"] = (0.62, 0.13, 0.1)
    # The hull: wide, its front corners cut.
    m.loft((2, 16), lambda t: (ramp(t, 9.5, 9.5), 2.0, -2.0, 1.5), "hull")
    m.plate([(5.0, 14.0), (14.5, 14.0), (14.5, 16.5), (8.0, 16.5)], (-1, 1), "hull")
    # A raised deck and the bridge.
    m.loft((3, 13), lambda t: (5.5, 3.0, 1.0, 1.0), "hull_light")
    m.loft((6.5, 10.5), lambda t: (2.4, 4.0, 2.0, 0.8), "hull")
    m.box((13, 15), (9.5, 9.5), (3.5, 3.5), "glass", mirror=False)
    m.paint(lambda x, y, z: abs(x - 14.5) < 0.5 and 9.5 <= y < 10.5 and z > 3.2, "glint")
    # Armor plates on the deck's sides, vents between them, red markings.
    for y0 in (3.5, 7.0, 10.5):
        m.box((5.5, 8.5), (y0, y0 + 2.5), (2.5, 3), "hull")
    m.box((6, 8), (6.25, 6.25), (2.5, 2.5), "vent")
    m.box((6, 8), (9.75, 9.75), (2.5, 2.5), "vent")
    m.paint(lambda x, y, z: 5.5 <= x < 8.5 and 13 <= y < 14 and z > 1.6, "paint")
    m.paint(lambda x, y, z: 9.0 <= x < 9.5 and 3 <= y < 13 and z > 2.2, "paint")
    m.paint(lambda x, y, z: x < 5.0 and 2 <= y < 3.5 and z > 0.5, "paint")
    # Outriggers to the engine pods.
    m.box((4, 5), (6, 10), (-0.5, 0), "frame")
    m.box((0, 4), (7, 9), (0, 0), "hull_dark")
    ribbed(m, 2.5, (0, 9), 0.0, 1.7)
    m.nacelle(2.5, (0, 0.5), 0.0, 1.2, "vent")
    lights(m, 0.25, (8.0, 8.5), 0.5)
    # The cannon: a thick barrel forward, a muzzle.
    m.nacelle(14.5, (15, 20), -0.5, 0.9, "frame", mirror=False)
    m.nacelle(14.5, (20, 21), -0.5, 0.5, "metal", mirror=False)
    # Side guns.
    m.nacelle(8.0, (16.5, 19), -0.5, 0.45, "metal")
    m.finish(seams=(6, 12), keep=KEEP)
    return m, [engine(2, 0, 3.6, 7, "top"), engine(26, 0, 3.6, 7, "top")]


@recipe("bomber")
def bomber() -> tuple[Model, list[dict] | None]:
    """A bomber: a broad flying wing, four engine pods at the back, a bomb bay under a raised hull."""
    m = Model(33, 18, SCALE)
    m.materials["paint"] = (0.34, 0.51, 0.255)
    # The wing: swept back from the nose (enemies fly down: the nose is at the bottom).
    m.plate(
        [(16.5, 17.0), (16.5, 3.0), (0.0, 3.0), (0.0, 4.5), (9.0, 16.5)], lambda x, y: (0, 0 if x < 10 else 0.5), "hull"
    )
    m.plate([(16.5, 17.0), (9.0, 16.5), (0.0, 4.5), (0.0, 4.0), (9.0, 15.8), (16.5, 16.4)], (0, 0.5), "hull_light")
    # The central hull, raised, with the bay.
    m.loft((2.5, 17.0), lambda t: (ramp(t, 6.0, 1.5, 1.0), ramp(t, 2.5, 1.5, 1.0), -1.5, 1.2), "hull")
    m.loft((7, 12), lambda t: (2.0, 2.8, 2.0, 0.6), "vent")
    m.paint(lambda x, y, z: 11.0 <= x < 12.0 and 4 <= y < 15 and z > 1.5, "paint")
    # Chevrons on the wings, the color of the old bomber.
    m.paint(
        lambda x, y, z: 3.0 <= x < 10.0 and 5.0 + (10.0 - x) * 0.55 <= y < 6.0 + (10.0 - x) * 0.55 and z > -0.1, "paint"
    )
    m.paint(
        lambda x, y, z: 3.0 <= x < 10.0 and 7.0 + (10.0 - x) * 0.55 <= y < 7.5 + (10.0 - x) * 0.55 and z > -0.1, "paint"
    )
    lights(m, 0.25, (3.5, 4.5), 0.5)
    # Four engine pods at the back.
    for x in (6.5, 13.5):
        ribbed(m, x, (0, 5), 0.0, 1.5)
        m.nacelle(x, (0, 0.5), 0.0, 1.0, "vent")
    m.finish(seams=(9, 13), keep=KEEP)
    return m, [
        engine(6, 0, 3, 7, "top"),
        engine(13, 0, 3, 7, "top"),
        engine(19, 0, 3, 7, "top"),
        engine(26, 0, 3, 7, "top"),
    ]


# -- pickups


@recipe("extra_life")
def extra_life() -> tuple[Model, list[dict] | None]:
    """The extra life: a green gem with a little white ship standing on it."""
    m = Model(12, 12, SCALE)
    m.materials["paint"] = (0.2, 0.8, 0.35)
    m.materials["paint_light"] = (0.45, 0.95, 0.55)
    m.materials["white"] = (0.95, 0.96, 0.97)
    octagon = [(3.5, 0.5), (8.5, 0.5), (11.5, 3.5), (11.5, 8.5), (8.5, 11.5), (3.5, 11.5), (0.5, 8.5), (0.5, 3.5)]
    inner = [(4.0, 2.0), (8.0, 2.0), (10.0, 4.0), (10.0, 8.0), (8.0, 10.0), (4.0, 10.0), (2.0, 8.0), (2.0, 4.0)]
    m.plate(octagon, (-1, 1), "paint", mirror=False)
    m.plate(inner, (2, 2), "paint_light", mirror=False)  # a raised facet
    # The ship: a fuselage, swept wings, on the facet.
    m.loft((2.5, 9.5), lambda t: (ramp(t, 0.3, 1.0, 0.4), 3.6, 2.5, 0.3), "white")
    m.plate([(5.5, 5.5), (5.5, 9.0), (2.5, 9.5), (2.5, 8.0)], (3, 3), "white")
    m.paint(lambda x, y, z: abs(x - 6.0) < 0.6 and 4 <= y < 5 and z > 3.2, "glint")
    return m, None


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("names", nargs="*", help="models to remodel (default: all with a recipe)")
    args = parser.parse_args()
    for name in args.names or RECIPES:
        model, engines = RECIPES[name]()
        model.save(MODELS / f"{name}.json", engines)
        print(f"{name}: {len(model.cells)} cubes")


if __name__ == "__main__":
    main()
