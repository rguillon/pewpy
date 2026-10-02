"""The candidates' colors: greys for the hull, a tint, an accent, a livery."""

from pewpewdev.tools.candidates.canvas import Rng

HULL_TINTS = {
    "grey": (1.0, 1.0, 1.0),
    "warm": (1.08, 1.0, 0.9),
    "blue": (0.9, 0.97, 1.1),
    "olive": (0.95, 1.0, 0.78),
    "dark": (0.68, 0.68, 0.74),
    "sand": (1.15, 1.05, 0.85),
    "rust": (1.1, 0.85, 0.72),
    "white": (1.35, 1.35, 1.35),
}
ACCENTS = {  # (markings, sensor)
    "red": ((0.8, 0.16, 0.12), (1.0, 0.2, 0.1)),
    "orange": ((0.9, 0.45, 0.1), (1.0, 0.6, 0.15)),
    "yellow": ((0.8, 0.65, 0.12), (1.0, 0.85, 0.2)),
    "green": ((0.2, 0.65, 0.25), (0.35, 1.0, 0.4)),
    "cyan": ((0.12, 0.6, 0.72), (0.3, 0.95, 1.0)),
    "purple": ((0.5, 0.2, 0.72), (0.75, 0.35, 1.0)),
    "magenta": ((0.78, 0.18, 0.55), (1.0, 0.3, 0.75)),
}
LIVERIES = [
    (0.55, 0.12, 0.1),
    (0.15, 0.25, 0.5),
    (0.5, 0.42, 0.12),
    (0.2, 0.35, 0.2),
    (0.3, 0.3, 0.33),
    (0.45, 0.2, 0.45),
]
GREYS = {  # char: (color, height in cubes)
    "N": ((0.26, 0.27, 0.29), 5),  # heavy plates
    "h": ((0.37, 0.38, 0.41), 3),  # hull
    "H": ((0.5, 0.51, 0.54), 3),  # lighter hull bands
    "S": ((0.6, 0.61, 0.63), 5),  # spine, fins, raised parts
    "k": ((0.17, 0.18, 0.2), 1),  # dark panel lines, flaps
    "r": ((0.13, 0.13, 0.15), 3),  # gun barrels
    "w": ((0.32, 0.33, 0.36), 1),  # wings
    "W": ((0.45, 0.46, 0.49), 1),  # lighter wing panels, leading edges
    "o": ((0.08, 0.08, 0.09), 3),  # engine nozzles
    "t": ((0.3, 0.31, 0.33), 5),  # turrets, containers
}
COCKPIT = ((0.08, 0.2, 0.28), 5)
UNDERSIDE = 0.72  # the hull's underside, this much as bright as its plating
HULL = "hHNSkt"  # what counts as hull (for engines)


def palette(rng: Rng, used: set[str]) -> dict:
    tint = HULL_TINTS[rng.choice(list(HULL_TINTS))]
    marking, sensor = ACCENTS[rng.choice(list(ACCENTS))]
    entries: dict[str, tuple[tuple[float, ...], int]] = {
        char: (tuple(round(min(1.0, c * t), 3) for c, t in zip(color, tint, strict=True)), height)
        for char, (color, height) in GREYS.items()
    }
    entries["c"] = COCKPIT
    entries["p"] = (marking, 3)
    entries["q"] = (marking, 1)  # on wings: as thin as them
    entries["R"] = (sensor, 5)
    entries["L"] = (rng.choice(LIVERIES), 3)
    entries["D"] = (tuple(round(c * UNDERSIDE, 3) for c in entries["h"][0]), 1)  # the underside (3D ships only)
    return {char: {"color": list(color), "height": height} for char, (color, height) in entries.items() if char in used}
