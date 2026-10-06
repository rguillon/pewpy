"""The candidates' colors: greys for the hull, tinted; a cockpit; an accent for markings and sensors; a livery.

Each character of a drawing is one color: the enemies' GREYS, the boss cores' CORE_GREYS or their parts' PART_GREYS,
and the same colors on top of them for everyone (see `palette`).
"""

from dataclasses import dataclass

from pewpy.tools.common.geometry import Rng

Color = tuple[float, float, float]

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
GREYS: dict[str, Color] = {  # the enemies'
    "N": (0.26, 0.27, 0.29),  # heavy plates
    "h": (0.37, 0.38, 0.41),  # hull
    "H": (0.5, 0.51, 0.54),  # lighter hull bands
    "S": (0.6, 0.61, 0.63),  # spine, fins, raised parts
    "k": (0.17, 0.18, 0.2),  # dark panel lines, flaps
    "r": (0.13, 0.13, 0.15),  # gun barrels
    "w": (0.32, 0.33, 0.36),  # wings
    "W": (0.45, 0.46, 0.49),  # lighter wing panels, leading edges
    "o": (0.08, 0.08, 0.09),  # engine nozzles
    "t": (0.3, 0.31, 0.33),  # turrets, containers
}
CORE_GREYS: dict[str, Color] = {  # a boss's core
    "N": (0.26, 0.27, 0.29),  # armor bands
    "h": (0.37, 0.38, 0.41),  # hull
    "H": (0.5, 0.51, 0.54),  # lighter hull bands
    "S": (0.6, 0.61, 0.63),  # superstructure
    "T": (0.55, 0.56, 0.59),  # superstructure, lower decks
    "k": (0.17, 0.18, 0.2),  # dark panel lines, hangar bays
    "r": (0.13, 0.13, 0.15),  # recesses, gun barrels
    "w": (0.32, 0.33, 0.36),  # wings, sponsons
    "W": (0.45, 0.46, 0.49),
    "o": (0.08, 0.08, 0.09),  # engine nozzles
    "x": (0.22, 0.23, 0.25),  # sockets under the parts
}
PART_GREYS: dict[str, Color] = {  # a boss's parts
    "N": (0.26, 0.27, 0.29),
    "t": (0.3, 0.31, 0.33),  # housing
    "S": (0.6, 0.61, 0.63),  # dome, raised top
    "h": (0.37, 0.38, 0.41),
    "H": (0.5, 0.51, 0.54),
    "k": (0.17, 0.18, 0.2),
    "r": (0.13, 0.13, 0.15),  # barrels, tubes
    "W": (0.45, 0.46, 0.49),
}
COCKPIT: Color = (0.08, 0.2, 0.28)  # a cockpit's glass, a bridge's windows
PLAYER_TINT = HULL_TINTS["blue"]  # every player's ship is a bluish grey, like the game's ships *(the user's choice)*
UNDERSIDE = 0.72  # the hull's underside, this much as bright as its plating


@dataclass(frozen=True)
class Colors:
    """What makes a candidate's colors its own: the tint of its greys, its accent, its livery."""

    tint: Color
    accent: str
    livery: Color


def pick_colors(rng: Rng) -> Colors:
    """Pick a tint, an accent and a livery."""
    tint = HULL_TINTS[rng.choice(list(HULL_TINTS))]
    accent = rng.choice(list(ACCENTS))
    return Colors(tint, accent, rng.choice(LIVERIES))


def pick_player_colors(rng: Rng) -> Colors:
    """Pick an accent and a livery for a player's ship: its greys always bluish (PLAYER_TINT), only its bits colored."""
    accent = rng.choice(list(ACCENTS))
    return Colors(PLAYER_TINT, accent, rng.choice(LIVERIES))


def palette(greys: dict[str, Color], colors: Colors) -> dict:
    """Make a palette: the greys tinted, then the same colors for everyone.

    The cockpit (c), the markings (p, and q on wings), the glowing sensor color (glowing seams g, a part's glowing core
    G, sensors R), the livery (L) and the underside (D: the hull darker). A drawing keeps only the characters it uses
    (see drawing.layered_drawing).
    """
    marking, sensor = ACCENTS[colors.accent]
    entries = {char: _scaled(color, colors.tint) for char, color in greys.items()}
    entries |= {"c": COCKPIT, "p": marking, "q": marking, "g": sensor, "G": sensor, "R": sensor, "L": colors.livery}
    entries["D"] = _scaled(entries["h"], (UNDERSIDE, UNDERSIDE, UNDERSIDE))
    return {char: {"color": list(color)} for char, color in entries.items()}


def _scaled(color: Color, factors: Color) -> Color:
    """Return a color, each channel times its factor (at most 1), rounded."""
    red, green, blue = (round(min(1.0, channel * factor), 3) for channel, factor in zip(color, factors, strict=True))
    return red, green, blue
