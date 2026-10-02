"""The bosses' colors: thicker greys than the enemies'."""

from pewpewdev.tools.candidates.palette import ACCENTS, UNDERSIDE

# Thicker than the enemies (the game's bosses go up to 19 cubes).
CORE_GREYS = {  # char: (color, height in cubes)
    "N": ((0.26, 0.27, 0.29), 11),  # armor bands
    "h": ((0.37, 0.38, 0.41), 9),  # hull
    "H": ((0.5, 0.51, 0.54), 9),  # lighter hull bands
    "S": ((0.6, 0.61, 0.63), 15),  # superstructure
    "T": ((0.55, 0.56, 0.59), 13),  # superstructure, lower decks
    "k": ((0.17, 0.18, 0.2), 7),  # dark panel lines, hangar bays
    "r": ((0.13, 0.13, 0.15), 5),  # recesses
    "w": ((0.32, 0.33, 0.36), 3),  # wings, sponsons
    "W": ((0.45, 0.46, 0.49), 3),
    "o": ((0.08, 0.08, 0.09), 9),  # engine nozzles
    "x": ((0.22, 0.23, 0.25), 3),  # sockets under the parts (thin: the part stands out over them)
}
PART_GREYS = {
    "N": ((0.26, 0.27, 0.29), 9),
    "t": ((0.3, 0.31, 0.33), 9),  # housing
    "S": ((0.6, 0.61, 0.63), 13),  # dome, raised top
    "h": ((0.37, 0.38, 0.41), 7),
    "H": ((0.5, 0.51, 0.54), 7),
    "k": ((0.17, 0.18, 0.2), 5),
    "r": ((0.13, 0.13, 0.15), 5),  # barrels, tubes
    "W": ((0.45, 0.46, 0.49), 5),
}
BRIDGE = ((0.08, 0.2, 0.28), 15)


def palette(greys: dict, tint: tuple[float, float, float], accent: str, livery: tuple) -> dict:
    marking, sensor = ACCENTS[accent]
    entries: dict[str, tuple[tuple[float, ...], int]] = {
        char: (tuple(round(min(1.0, c * t), 3) for c, t in zip(color, tint, strict=True)), height)
        for char, (color, height) in greys.items()
    }
    entries["c"] = BRIDGE
    entries["p"] = (marking, 11)
    entries["q"] = (marking, 3)  # markings on wings: as thin as them
    entries["g"] = (sensor, 7)  # glowing seams
    entries["G"] = (sensor, 11)  # a part's glowing core
    entries["R"] = (sensor, 17)
    entries["L"] = (livery, 9)
    entries["D"] = (tuple(round(c * UNDERSIDE, 3) for c in entries["h"][0]), 1)  # the underside
    return {char: {"color": list(color), "height": height} for char, (color, height) in entries.items()}
