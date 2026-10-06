"""Writing a boss shortly, as the game reads it (see pewpy.game.enemies.boss)."""

import dataclasses
from typing import Any

from pewpy.game.weapons.guns import Gun
from pewpy.tools.final_bosses.boss import CORE, BossSpec


def boss_json(spec: BossSpec, note: str = "") -> dict[str, Any]:
    """Write the boss: its body, its parts and its phases."""
    parts = [
        {
            "name": part.name, "x": part.x, "y": part.y, "drawing": part.drawing, "size": [part.width, part.height],
            "health": part.health, "points": part.points,
        }
        for part in spec.parts
    ]  # fmt: skip
    phases = []
    for phase in spec.phases:
        written: dict[str, Any] = {"sway": phase.sway}
        if phase.armored:
            written["armored"] = True
        if phase.until_destroyed:
            written["until"] = {"parts": list(phase.until_destroyed)}
        if phase.until_below > 0:
            written["until"] = {"health_below": phase.until_below}
        written["guns"] = [
            {**({} if source == CORE else {"from": _plain(source)}), **gun_json(gun)} for source, gun in phase.guns
        ]
        phases.append(written)
    body = {"note": note} if note else {}
    return body | {
        "name": spec.name, "drawing": spec.drawing, "size": [spec.width, spec.height], "health": spec.health,
        "points": spec.points, "parts": parts, "phases": phases,
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
    """Tuples as lists, guns as dicts: as JSON writes them; numbers to 3 decimals."""
    if isinstance(value, float):
        return round(value, 3)
    if isinstance(value, Gun):
        return gun_json(value)
    if isinstance(value, tuple):
        return [_plain(item) for item in value]
    return value
