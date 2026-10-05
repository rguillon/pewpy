"""A boss written shortly (02-enemies-bosses.md): its body, its parts and its phases, made into an enemy's description.

Every boss comes down at ENTRY_SPEED to HOLD_Y, then goes through its phases, swaying between the screen edges. Each
phase is a state starting with PHASE_PAUSE seconds without shooting; it is written as its `sway` speed, its `guns`,
`armored` (shots bounce off the core) and `until`: the exit conditions ending it (like `{"parts": [...]}` or
`{"health_below": 0.5}`, see exits/), the last phase has none. The boss's body and its parts get the bosses' usual
fields (BODY, PART) and its guns GUN, unless they give their own; any other field of a phase goes to its state.

A gun can come `from` several parts (a list): each of them fires it in turn, their first shots spread over its
interval.
"""

from typing import Any

HOLD_Y = 0.55  # where a boss stops coming down (the top of the screen is at 1)
ENTRY_SPEED = 0.25
PHASE_PAUSE = 1.2  # seconds without shooting when a phase starts, while the core flashes
EXPLOSIONS = ((0.0, 0.0, 1.3), (-0.45, 0.25, 0.7), (0.45, -0.2, 0.7), (0.2, 0.4, 0.6), (-0.3, -0.35, 0.6))
PART_DROP_CHANCE = 0.3

BODY: dict[str, Any] = {
    "drop_chance": 1.0, "velocity": [0.0, -ENTRY_SPEED], "rammable": False, "leaves_screen": False,
    "placeable": False, "boss": True, "hit_look": "hit", "entry_gap": "0.5h",
    "explosions": [list(explosion) for explosion in EXPLOSIONS],
}  # fmt: skip
PART: dict[str, Any] = {
    "drop_chance": PART_DROP_CHANCE, "rammable": False, "leaves_screen": False, "placeable": False, "hit_look": "hit"
}  # fmt: skip
GUN: dict[str, Any] = {"reload": "carry", "off_screen": "fire"}
ARMORED: dict[str, Any] = {"look": "armored", "vulnerable": False}


def expand_boss(data: dict[str, Any]) -> dict[str, Any]:
    """Make a boss written shortly (with `phases`) into an enemy's description (with `states`)."""
    body = dict(data)
    phases = body.pop("phases")
    parts = [PART | part for part in body.pop("parts", [])]
    return BODY | body | {"parts": parts, "states": _states(phases)}


def _states(phases: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Coming down, then a state per phase."""
    first = phases[0]
    arrive = {
        "to": "phase 1", "below_y": HOLD_Y, "go_on": True, "recheck": True,
        "then": [{"type": "velocity", "vy": 0.0}, {"type": "sway", "speed": first["sway"]}],
    }  # fmt: skip
    states = [{"name": "enter", **(ARMORED if first.get("armored") else {}), "exits": [arrive]}]
    for number, phase in enumerate(phases, start=1):
        fields = dict(phase)
        fields.pop("sway")
        armored, until = fields.pop("armored", False), fields.pop("until", None)
        guns = [written for gun in fields.pop("guns", []) for written in _guns(gun)]
        exits = []
        if until is not None:
            then = [{"type": "sway", "speed": phases[number]["sway"]}]
            exits.append({"to": f"phase {number + 1}", **until, "go_on": True, "then": then})
        state = {"name": f"phase {number}", "motions": [{"type": "bounce", "clamp": True}], "guns": guns}
        states.append(state | (ARMORED if armored else {}) | {"warmup": PHASE_PAUSE, "exits": exits} | fields)
    return states


def _guns(gun: dict[str, Any]) -> list[dict[str, Any]]:
    """Write the gun as it is, or once per part when it comes from several, in turn."""
    sources = gun.get("from", "")
    if not isinstance(sources, list):
        return [GUN | gun]
    delay, step = gun.get("delay", 0.0), gun["interval"] / len(sources)
    return [GUN | gun | {"from": source, "delay": delay + step * index} for index, source in enumerate(sources)]
