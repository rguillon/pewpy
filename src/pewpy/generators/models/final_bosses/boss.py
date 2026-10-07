"""A final boss described shortly: its parts and phases, made from its attacks and parts."""

from dataclasses import dataclass, replace

from pewpy.game.weapons.guns import Gun
from pewpy.generators.models.final_bosses.attacks import attack_guns

CORE = "core"  # the gun source that is the boss itself


@dataclass(frozen=True)
class PartSpec:
    """A destructible part, at (x, y) from the core's middle."""

    name: str
    drawing: str  # its model: models/<group>/<drawing>.json
    x: float
    y: float
    width: float
    height: float
    health: float
    points: int


@dataclass(frozen=True)
class Phase:
    """Guns as (source, gun): the source is CORE, or parts' names firing it in turn. `sway`: side to side speed.

    It ends once every part in `until_destroyed` is destroyed, or once the core's health is below `until_below`
    (a fraction of its full health); the last phase lasts until the end.
    """

    guns: tuple[tuple[str | tuple[str, ...], Gun], ...]
    sway: float
    armored: bool = False
    until_destroyed: tuple[str, ...] = ()
    until_below: float = 0.0


@dataclass(frozen=True)
class BossSpec:
    """A boss described shortly: its body, its parts and its phases."""

    name: str  # shown over its health bar
    drawing: str
    width: float
    height: float
    health: float
    points: int
    phases: tuple[Phase, ...]
    parts: tuple[PartSpec, ...] = ()


PartPlan = tuple[str, float, float, float, float]  # drawing, x, y, width, height (from the core's middle)


def final_boss(
    name: str,
    drawing: str,
    width: float,
    height: float,
    difficulty: int,
    attacks: tuple[str, ...],
    parts: tuple[PartPlan, ...],
) -> BossSpec:
    """Make a final boss of a level of `difficulty`: its health, points and phases from it and its four attacks.

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
            f"{part_drawing.rsplit(':', 1)[-1]} {index + 1}",
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

    def from_parts(names: tuple[str, ...], attack: str) -> tuple[tuple[tuple[str, ...], Gun], ...]:
        """Every part of `names` firing `attack` in turn (as often in all as about two parts would)."""
        interval = guns[attack].interval * max(1.0, len(names) / 2) ** 0.5
        return ((names, replace(guns[attack], interval=interval)),)

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
