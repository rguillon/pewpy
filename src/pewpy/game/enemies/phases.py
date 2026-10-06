"""Enemies written shortly with phases, and the usual fields of each kind of enemy (02-enemies-bosses.md).

Any enemy can be written with `phases` instead of `states` (`expand_phases` makes them states): it comes down at its
speed to `hold_y` (HOLD_Y unless given), then goes through its phases, swaying between the screen edges; until it
stops it doesn't shoot, and neither it nor its parts can be hurt. Each phase is a state starting with `phase_pause`
(PHASE_PAUSE unless given) seconds without shooting; it is written as its `sway` speed, its `guns`, `armored` (shots
bounce off the core) and `until`: the exit conditions ending it (like `{"parts": [...]}` or `{"health_below": 0.5}`,
see exits/), the last phase has none. Any other field of a phase goes to its state.

A preset is the usual fields of a kind of enemy, filled in unless its description gives them: its body's, each of
its parts' and each of its guns'. Every enemy gets ENEMY's, a boss (`"boss": true`) BOSS's: every boss comes down
and fights the same way, so a boss is its body, its parts and its phases.
"""

from dataclasses import dataclass, field
from typing import Any

HOLD_Y = 0.55  # where an enemy written with phases stops coming down (the top of the screen is at 1)
PHASE_PAUSE = 1.2  # seconds without shooting when a phase starts, while the core flashes
BOSS_ENTRY_SPEED = 0.25
BOSS_EXPLOSIONS = ((0.0, 0.0, 1.3), (-0.45, 0.25, 0.7), (0.45, -0.2, 0.7), (0.2, 0.4, 0.6), (-0.3, -0.35, 0.6))
BOSS_PART_DROP_CHANCE = 0.3
ARMORED: dict[str, Any] = {"look": "armored", "vulnerable": False}


@dataclass(frozen=True)
class Preset:
    """The usual fields of a kind of enemy: its body's, its parts' and its guns'."""

    body: dict[str, Any] = field(default_factory=dict)
    part: dict[str, Any] = field(default_factory=dict)
    gun: dict[str, Any] = field(default_factory=dict)


# A part is carried by its enemy: the levels don't place it, and it goes with its enemy, not by leaving the screen.
ENEMY = Preset(part={"placeable": False, "leaves_screen": False})
BOSS = Preset(
    body={
        "drop_chance": 1.0, "velocity": [0.0, -BOSS_ENTRY_SPEED], "rammable": False, "leaves_screen": False,
        "placeable": False, "hit_look": "hit", "entry_gap": "0.5h",
        "explosions": [list(explosion) for explosion in BOSS_EXPLOSIONS],
    },
    part=ENEMY.part | {"drop_chance": BOSS_PART_DROP_CHANCE, "rammable": False, "hit_look": "hit"},
    gun={"reload": "carry", "off_screen": "fire"},
)  # fmt: skip


def preset(data: dict[str, Any]) -> Preset:
    """Return the usual fields of the enemy `data` describes: a boss's, or any enemy's."""
    return BOSS if data.get("boss") else ENEMY


def expand_phases(data: dict[str, Any]) -> dict[str, Any]:
    """Make an enemy written shortly (with `phases`) into an enemy's description (with `states`)."""
    body = dict(data)
    phases = body.pop("phases")
    hold_y, pause = body.pop("hold_y", HOLD_Y), body.pop("phase_pause", PHASE_PAUSE)
    return body | {"states": _states(phases, hold_y, pause)}


def _states(phases: list[dict[str, Any]], hold_y: float, pause: float) -> list[dict[str, Any]]:
    """Coming down, then a state per phase."""
    first = phases[0]
    arrive = {
        "to": "phase 1", "below_y": hold_y, "go_on": True, "recheck": True,
        "then": [{"type": "velocity", "vy": 0.0}, {"type": "sway", "speed": first["sway"]}],
    }  # fmt: skip
    entry = {"name": "enter", "coming_in": True, **(ARMORED if first.get("armored") else {}), "exits": [arrive]}
    states = [entry]
    for number, phase in enumerate(phases, start=1):
        fields = dict(phase)
        fields.pop("sway")
        armored, until = fields.pop("armored", False), fields.pop("until", None)
        exits = []
        if until is not None:
            then = [{"type": "sway", "speed": phases[number]["sway"]}]
            exits.append({"to": f"phase {number + 1}", **until, "go_on": True, "then": then})
        state = {"name": f"phase {number}", "motions": [{"type": "bounce", "clamp": True}], "guns": []}
        states.append(state | (ARMORED if armored else {}) | {"warmup": pause, "exits": exits} | fields)
    return states
