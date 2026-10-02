"""Make the final bosses (data/bosses/final_bosses.json) from their plans (final_boss_plans.json, next to this
file), 02-enemies-bosses.md:

    make final-bosses

(or `uv run python -m pewpewdev.tools.make_final_bosses`).

A plan gives a final boss's drawing, size, difficulty (1 to 20), four attacks and parts. Each is a big core with its
parts, and four attacks. Its phases come from them (see `final_boss`): the front parts first, then the back ones,
while the core is armored; then the core, then the core in a rage. Everything gets harder with the difficulty.

A boss is written like any enemy (see pewpy.game.enemies.spec): it comes down to HOLD_Y, then goes through its
phases as states, each starting with PHASE_PAUSE seconds without shooting, blinking; its parts are enemies of their
own. `boss_json` writes a boss described shortly (BossSpec: its parts and phases) that way.
"""

import argparse
import dataclasses
import json
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any

from pewpewdev.paths import DATA
from pewpy.game.weapons.guns import Gun

PLANS = Path(__file__).with_name("final_boss_plans.json")
OUT = DATA / "bosses" / "final_bosses.json"
CORE = "core"  # the gun source that is the boss itself
HOLD_Y = 0.55  # where a boss stops coming down (the top of the screen is at 1)
ENTRY_SPEED = 0.25
PHASE_PAUSE = 1.2  # seconds without shooting when a phase starts, while the core flashes
EXPLOSIONS = ((0.0, 0.0, 1.3), (-0.45, 0.25, 0.7), (0.45, -0.2, 0.7), (0.2, 0.4, 0.6), (-0.3, -0.35, 0.6))
PART_DROP_CHANCE = 0.3


@dataclass(frozen=True)
class PartSpec:
    """A destructible part, at (x, y) from the core's middle."""

    name: str
    drawing: str  # its model: models/<drawing>.json
    x: float
    y: float
    width: float
    height: float
    health: float
    points: int


@dataclass(frozen=True)
class Phase:
    """Guns as (source, gun): the source is CORE or a part's name. `sway`: side to side speed.

    It ends once every part in `until_destroyed` is destroyed, or once the core's health is below `until_below`
    (a fraction of its full health); the last phase lasts until the end.
    """

    guns: tuple[tuple[str, Gun], ...]
    sway: float
    armored: bool = False
    until_destroyed: tuple[str, ...] = ()
    until_below: float = 0.0


@dataclass(frozen=True)
class BossSpec:
    name: str  # shown over its health bar
    drawing: str
    width: float
    height: float
    health: float
    points: int
    phases: tuple[Phase, ...]
    parts: tuple[PartSpec, ...] = ()

    @property
    def half_span(self) -> float:
        """Half the width of the whole boss, parts included."""
        return max([self.width / 2] + [abs(part.x) + part.width / 2 for part in self.parts])

    @property
    def top_reach(self) -> float:
        """How far the boss reaches above its middle, parts included."""
        return max([self.height / 2] + [part.y + part.height / 2 for part in self.parts])


PartPlan = tuple[str, float, float, float, float]  # drawing, x, y, width, height (from the core's middle)


def attack_guns(p: float) -> dict[str, Gun]:
    """Each attack's gun, at `p` from 0 (difficulty 1) to 1 (difficulty 20)."""
    return {
        "aimed": Gun("aimed", 1.6 - 0.5 * p, 0.6 + 0.15 * p, volley=3 + round(2 * p), gap=0.12, style="heavy"),
        "sniper": Gun("aimed", 1.5 - 0.4 * p, 0.85 + 0.1 * p, volley=2 + round(2 * p), gap=0.2, style="sniper"),
        "fan": Gun("fan", 1.8 - 0.5 * p, 0.45 + 0.1 * p, count=5 + round(4 * p), spread=12, sweep=25),
        "ring": Gun("ring", 2.0 - 0.6 * p, 0.38 + 0.08 * p, count=12 + round(8 * p), turn=9),
        "spiral": Gun("ring", 0.16 - 0.04 * p, 0.42 + 0.06 * p, count=2 + round(2 * p), turn=13),
        "wave": Gun("fan", 1.6 - 0.4 * p, 0.45 + 0.1 * p, count=3 + round(2 * p), spread=20, style="wave"),
        "accel": Gun("aimed", 1.8 - 0.5 * p, 0.55 + 0.15 * p, count=5, spread=8, style="accel"),
        "curve": Gun("ring", 1.8 - 0.5 * p, 0.35 + 0.05 * p, count=8 + round(4 * p), curve=35, style="curve"),
        "pellets": Gun("aimed", 1.6 - 0.4 * p, 0.6 + 0.1 * p, count=7 + round(4 * p), spread=6, style="pellet"),
        "laser": Gun("laser", 4.5 - 1.5 * p, 0.0, width=0.07, duration=1.0 + 0.4 * p),
        "missiles": Gun("aimed", 3.5 - 1.0 * p, 0.0, count=2, spread=40, projectile="missile"),
        "rockets": Gun("fan", 2.6 - 0.8 * p, 0.0, count=3, spread=25, projectile="rocket"),
        "cluster": Gun("fan", 3.0 - 0.8 * p, 0.0, count=2 + round(p), spread=30, projectile="cluster"),
    }


ATTACKS = tuple(attack_guns(0.0))


def final_boss(
    name: str,
    drawing: str,
    width: float,
    height: float,
    difficulty: int,
    attacks: tuple[str, ...],
    parts: tuple[PartPlan, ...],
) -> BossSpec:
    """A final boss of a level of `difficulty`: its health, points and phases from it and its four attacks.

    attacks: the front parts', the back parts', the core's, and the one it adds in its rage (the last phase). The
    front parts are the drawings nearest the bottom of the screen (half of the kinds of parts), the back ones the
    others. A "laser" on the core fires two beams apart.
    """
    p = (difficulty - 1) / 19
    guns = attack_guns(p)
    front_attack, back_attack, core_attack, rage_attack = attacks
    kinds = sorted(  # ties by name, so the same parts are in front every time
        {plan[0] for plan in parts}, key=lambda kind: (sum(plan[2] for plan in parts if plan[0] == kind), kind)
    )
    front_kinds = set(kinds[: (len(kinds) + 1) // 2])
    specs = tuple(
        PartSpec(
            f"{part_drawing.rsplit('_', 1)[-1]} {index + 1}",
            part_drawing,
            x,
            y,
            part_width,
            part_height,
            round(16 + 1.6 * (difficulty - 1)),
            300 + 30 * difficulty,
        )
        for index, (part_drawing, x, y, part_width, part_height) in enumerate(parts)
    )
    front = tuple(spec.name for spec in specs if spec.drawing in front_kinds)
    back = tuple(spec.name for spec in specs if spec.drawing not in front_kinds)

    def from_parts(names: tuple[str, ...], attack: str) -> tuple[tuple[str, Gun], ...]:
        """Every part of `names` firing `attack` in turn (as often in all as about two parts would)."""
        interval = guns[attack].interval * max(1.0, len(names) / 2) ** 0.5
        return tuple(
            (part, replace(guns[attack], interval=interval, delay=interval * index / len(names)))
            for index, part in enumerate(names)
        )

    def from_core(attack: str, delay: float = 0.0) -> tuple[str, Gun]:
        offsets = (-width / 4, width / 4) if attack == "laser" else (0.0,)
        return CORE, replace(guns[attack], delay=delay, offsets=offsets)

    sway = 0.08 + 0.004 * difficulty
    phases = []
    if front:
        core_guns = (from_core("aimed", 0.8),) if difficulty >= 8 else ()
        phases.append(Phase(from_parts(front, front_attack) + core_guns, sway, armored=True, until_destroyed=front))
    if back:
        phases.append(
            Phase(
                (*from_parts(back, back_attack), from_core(core_attack, 0.6)), sway, armored=True, until_destroyed=back
            )
        )
    phases.append(Phase((from_core(core_attack), from_core(rage_attack, 0.9)), sway + 0.03, until_below=0.5))
    rage = (
        from_core(rage_attack),
        from_core(front_attack, 0.5),
        from_core("spiral" if difficulty >= 6 else "ring", 1.0),
    )
    phases.append(Phase(rage, sway + 0.06))
    return BossSpec(
        name=name,
        drawing=drawing,
        width=width,
        height=height,
        health=float(110 + 14 * (difficulty - 1)),
        points=4000 + 400 * difficulty,
        phases=tuple(phases),
        parts=specs,
    )


def boss_json(spec: BossSpec, note: str = "") -> dict[str, Any]:
    """The boss written like any enemy: its body, its parts, and states: coming down, then its phases."""
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
    """The gun's fields that aren't the defaults (its pattern, interval and speed always)."""
    written: dict[str, Any] = {}
    for f in dataclasses.fields(gun):
        value = getattr(gun, f.name)
        if f.default is dataclasses.MISSING or value != f.default:
            written[f.name] = _plain(value)
    return written


def _plain(value: Any) -> Any:
    """Tuples as lists, guns as dicts: as JSON writes them."""
    if isinstance(value, Gun):
        return gun_json(value)
    if isinstance(value, tuple):
        return [_plain(item) for item in value]
    return value


def plan_boss(plan: dict[str, Any]) -> BossSpec:
    attacks = plan["attacks"]
    return final_boss(
        plan["name"],
        plan["drawing"],
        plan["width"],
        plan["height"],
        plan["difficulty"],
        (attacks["front"], attacks["back"], attacks["core"], attacks["rage"]),
        tuple((part["drawing"], part["x"], part["y"], part["width"], part["height"]) for part in plan["parts"]),
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--out", type=Path, default=OUT, help="where (default: the game's final bosses)")
    args = parser.parse_args()
    plans = json.loads(PLANS.read_text())
    bosses = {name: boss_json(plan_boss(plan), plan.get("note", "")) for name, plan in plans.items()}
    args.out.write_text(json.dumps(bosses, indent=2) + "\n")
    print(f"{len(bosses)} final bosses written to {args.out}")


if __name__ == "__main__":
    main()
