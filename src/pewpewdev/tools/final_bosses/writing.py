"""Writing a boss like any enemy (see pewpy.game.enemies.spec)."""

import dataclasses
from dataclasses import replace
from typing import Any

from pewpewdev.tools.final_bosses.boss import (
    CORE,
    ENTRY_SPEED,
    EXPLOSIONS,
    HOLD_Y,
    PART_DROP_CHANCE,
    PHASE_PAUSE,
    BossSpec,
)
from pewpy.game.weapons.guns import Gun


def boss_json(spec: BossSpec, note: str = "") -> dict[str, Any]:
    """Write the boss like any enemy: its body, its parts, and states: coming down, then its phases."""
    parts = [
        {
            "name": part.name, "x": part.x, "y": part.y, "drawing": part.drawing, "size": [part.width, part.height],
            "health": part.health, "points": part.points, "drop_chance": PART_DROP_CHANCE, "rammable": False,
            "leaves_screen": False, "placeable": False, "hit_look": "hit",
        }
        for part in spec.parts
    ]  # fmt: skip
    armored = {"look": "armored", "vulnerable": False}
    arrive = {
        "to": "phase 1", "below_y": HOLD_Y, "go_on": True, "recheck": True,
        "then": [{"type": "velocity", "vy": 0.0}, {"type": "sway", "speed": spec.phases[0].sway}],
    }  # fmt: skip
    states = [{"name": "enter", **(armored if spec.phases[0].armored else {}), "exits": [arrive]}]
    for number, phase in enumerate(spec.phases, start=1):
        exits = []
        if number < len(spec.phases):
            then = [{"type": "sway", "speed": spec.phases[number].sway}]
            if phase.until_destroyed:
                exits.append({
                    "to": f"phase {number + 1}",
                    "parts": list(phase.until_destroyed),
                    "go_on": True,
                    "then": then,
                })
            if phase.until_below > 0:
                exits.append({
                    "to": f"phase {number + 1}",
                    "health_below": phase.until_below,
                    "go_on": True,
                    "then": then,
                })
        guns = [
            {
                **({} if source == CORE else {"from": source}),
                **gun_json(replace(gun, reload="carry", off_screen="fire")),
            }
            for source, gun in phase.guns
        ]
        state = {"name": f"phase {number}", "motions": [{"type": "bounce", "clamp": True}], "guns": guns}
        states.append({**state, **(armored if phase.armored else {}), "warmup": PHASE_PAUSE, "exits": exits})
    body = {"note": note} if note else {}
    return body | {
        "name": spec.name, "drawing": spec.drawing, "size": [spec.width, spec.height], "health": spec.health,
        "points": spec.points, "drop_chance": 1.0, "velocity": [0.0, -ENTRY_SPEED], "rammable": False,
        "leaves_screen": False, "placeable": False, "boss": True, "hit_look": "hit", "entry_gap": "0.5h",
        "explosions": [list(explosion) for explosion in EXPLOSIONS], "parts": parts, "states": states,
    }  # fmt: skip


def gun_json(gun: Gun) -> dict[str, Any]:
    """Write the gun's fields that aren't the defaults (its pattern, interval and speed always)."""
    written: dict[str, Any] = {}
    for f in dataclasses.fields(gun):
        value = getattr(gun, f.name)
        if f.default is dataclasses.MISSING or value != f.default:
            written[f.name] = _plain(value)
    return written


def _plain(value: object) -> object:
    """Tuples as lists, guns as dicts: as JSON writes them."""
    if isinstance(value, Gun):
        return gun_json(value)
    if isinstance(value, tuple):
        return [_plain(item) for item in value]
    return value
