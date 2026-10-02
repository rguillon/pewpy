"""The final bosses: one at the end of each level, after its mini boss (02-enemies-bosses.md). Placeholders.

Each (in `bosses/final_bosses.json`, loaded by catalog.py) is a big core (a boss candidate, see pewpewdev/tools/make_boss_candidates.py) with its parts, and four attacks. Its
phases come from them (see `final_boss`): the front parts first, then the back ones, while the core is armored;
then the core, then the core in a rage. Everything gets harder with the level's difficulty (1 to 20).
"""

from dataclasses import replace

from pewpy.game.bosses.boss import CORE, BossSpec, PartSpec, Phase
from pewpy.game.weapons.enemy.boss_guns import Gun

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
