"""A final boss described shortly: its parts and phases, made from its attacks and parts."""

from dataclasses import dataclass, replace

from pewpy.game.weapons.guns import Gun
from pewpy.generators.models.final_bosses.attacks import attack_guns

CORE = "core"  # the gun source that is the boss itself
DIFFICULTY_FROM = 19  # the last difficulty, for turning a difficulty into a share from 0 to 1
PART_HEALTH = 16.0  # a part's health at difficulty 1...
PART_HEALTH_STEP = 1.6  # ...and how much more each difficulty adds
PART_POINTS = 300  # a part's points at difficulty 1...
PART_POINTS_STEP = 30  # ...and how many more each difficulty adds
HEALTH = 110.0  # the core's health at difficulty 1...
HEALTH_STEP = 14.0  # ...and how much more each difficulty adds
POINTS = 4000  # the boss's points at difficulty 1...
POINTS_STEP = 400  # ...and how many more each difficulty adds
SWAY = 0.08  # how fast the boss sways at difficulty 1...
SWAY_STEP = 0.004  # ...and how much faster each difficulty sways
RAGE_SWAY = 0.03  # ...plus this in the first phase of its rage
LAST_SWAY = 0.06  # ...and this in the one after that
ARMORED_FROM = 8  # from this difficulty, the core aims while its front parts are up
# How long the core waits before each of its own guns fires, in the phases where it fires beside the parts' and in
# its rage; AIMED_DELAY is the gun it fires while its front parts are up (only from ARMORED_FROM).
AIMED_DELAY = 0.8
CORE_DELAY = 0.6
RAGE_DELAY = 0.9
RAGE_FRONT_DELAY = 0.5
RAGE_WAVE_DELAY = 1.0
SPIRAL_FROM = 6  # from this difficulty its rage spirals, else it rings
RAGE_AT = 0.5  # the share of its health left that the core's rage starts at
LASER_BEAMS = (-0.25, 0.25)  # the core's laser fires two beams this far from its middle, as a share of its width
GUNS_IN_TURN = 2  # a phase's parts fire in turn as often in all as about this many parts would


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


def part_health(difficulty: int) -> float:
    """Return a part's health at `difficulty`."""
    return round(PART_HEALTH + PART_HEALTH_STEP * (difficulty - 1))


def part_points(difficulty: int) -> int:
    """Return a part's points at `difficulty`."""
    return PART_POINTS + PART_POINTS_STEP * difficulty


def _part_specs(parts: tuple[PartPlan, ...], difficulty: int) -> tuple[PartSpec, ...]:
    """Return the specs of every part, numbered by kind and place: "cannon 3", "turret 2"..."""
    health, points = part_health(difficulty), part_points(difficulty)
    return tuple(
        PartSpec(f"{drawing.rsplit(':', 1)[-1]} {index + 1}", drawing, x, y, width, height, health, points)
        for index, (drawing, x, y, width, height) in enumerate(parts)
    )


def _front_kinds(parts: tuple[PartPlan, ...]) -> set[str]:
    """Return the drawings of the front parts: those nearest the bottom of the screen, ties by name.

    The same parts are in front every time, so the player learns where to shoot.
    """
    kinds = sorted(  # ties by name, so the same parts are in front every time
        {plan[0] for plan in parts}, key=lambda kind: (sum(plan[2] for plan in parts if plan[0] == kind), kind)
    )
    return set(kinds[: (len(kinds) + 1) // 2])


def _from_parts(names: tuple[str, ...], attack: str, guns: dict[str, Gun]) -> tuple[tuple[tuple[str, ...], Gun], ...]:
    """Return every part of `names` firing `attack` in turn (as often in all as about two parts would)."""
    interval = guns[attack].interval * max(1.0, len(names) / GUNS_IN_TURN) ** 0.5
    return ((names, replace(guns[attack], interval=interval)),)


def _from_core(attack: str, guns: dict[str, Gun], width: float, delay: float = 0.0) -> tuple[str, Gun]:
    """Return the core firing `attack`: a laser fires two beams apart, everything else from its middle."""
    offsets = (width * LASER_BEAMS[0], width * LASER_BEAMS[1]) if attack == "laser" else (0.0,)
    return CORE, replace(guns[attack], delay=delay, offsets=offsets)


def _front_phase(
    front: tuple[str, ...], guns: dict[str, Gun], width: float, sway: float, difficulty: int, front_attack: str
) -> Phase:
    """Return the first phase: the front parts firing, the core aiming beside them once it's mean enough."""
    core_guns = (_from_core("aimed", guns, width, AIMED_DELAY),) if difficulty >= ARMORED_FROM else ()
    return Phase((*_from_parts(front, front_attack, guns), *core_guns), sway, armored=True, until_destroyed=front)


def _back_phase(
    back: tuple[str, ...], guns: dict[str, Gun], width: float, sway: float, back_attack: str, core_attack: str
) -> Phase:
    """Return the second phase: the back parts firing, the core on its own attack beside them."""
    return Phase(
        (*_from_parts(back, back_attack, guns), _from_core(core_attack, guns, width, CORE_DELAY)),
        sway,
        armored=True,
        until_destroyed=back,
    )


def _phases(
    front: tuple[str, ...],
    back: tuple[str, ...],
    guns: dict[str, Gun],
    width: float,
    sway: float,
    difficulty: int,
    front_attack: str,
    back_attack: str,
    core_attack: str,
    rage_attack: str,
) -> tuple[Phase, ...]:
    """Return the boss's phases: its parts' turn, then the core's, then its rage."""
    phases = []
    if front:
        phases.append(_front_phase(front, guns, width, sway, difficulty, front_attack))
    if back:
        phases.append(_back_phase(back, guns, width, sway, back_attack, core_attack))
    phases.append(
        Phase(
            (_from_core(core_attack, guns, width), _from_core(rage_attack, guns, width, RAGE_DELAY)),
            sway + RAGE_SWAY,
            until_below=RAGE_AT,
        )
    )
    phases.append(
        Phase(
            (
                _from_core(rage_attack, guns, width),
                _from_core(front_attack, guns, width, RAGE_FRONT_DELAY),
                _from_core("spiral" if difficulty >= SPIRAL_FROM else "ring", guns, width, RAGE_WAVE_DELAY),
            ),
            sway + LAST_SWAY,
        )
    )
    return tuple(phases)


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
    p = (difficulty - 1) / DIFFICULTY_FROM
    guns = attack_guns(p)
    front_attack, back_attack, core_attack, rage_attack = attacks
    specs = _part_specs(parts, difficulty)
    front_kinds = _front_kinds(parts)
    front = tuple(spec.name for spec in specs if spec.drawing in front_kinds)
    back = tuple(spec.name for spec in specs if spec.drawing not in front_kinds)
    return BossSpec(
        name=name,
        drawing=drawing,
        width=width,
        height=height,
        health=HEALTH + HEALTH_STEP * (difficulty - 1),
        points=POINTS + POINTS_STEP * difficulty,
        phases=_phases(
            front,
            back,
            guns,
            width,
            SWAY + SWAY_STEP * difficulty,
            difficulty,
            front_attack,
            back_attack,
            core_attack,
            rage_attack,
        ),
        parts=specs,
    )
