"""The kinds of parts, each in its own module."""

from collections.abc import Callable

from pewpy.tools.boss_candidates.canvas import Canvas
from pewpy.tools.boss_candidates.part_kinds.cannon import part_cannon
from pewpy.tools.boss_candidates.part_kinds.claw import part_claw
from pewpy.tools.boss_candidates.part_kinds.drill import part_drill
from pewpy.tools.boss_candidates.part_kinds.emitter import part_emitter
from pewpy.tools.boss_candidates.part_kinds.flak import part_flak
from pewpy.tools.boss_candidates.part_kinds.generator import part_generator
from pewpy.tools.boss_candidates.part_kinds.launcher import part_launcher
from pewpy.tools.boss_candidates.part_kinds.missile_pod import part_missile_pod
from pewpy.tools.boss_candidates.part_kinds.radar import part_radar
from pewpy.tools.boss_candidates.part_kinds.shield_node import part_shield_node
from pewpy.tools.boss_candidates.part_kinds.turret import part_turret
from pewpy.tools.common.geometry import Rng

PARTS: dict[str, Callable[[Rng, Canvas], None]] = {
    "turret": part_turret,
    "cannon": part_cannon,
    "generator": part_generator,
    "launcher": part_launcher,
    "drill": part_drill,
    "missile_pod": part_missile_pod,
    "emitter": part_emitter,
    "shield_node": part_shield_node,
    "radar": part_radar,
    "flak": part_flak,
    "claw": part_claw,
}
