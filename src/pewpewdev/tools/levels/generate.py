"""Making every level of every world."""

import random
from typing import Any

from pewpewdev.tools.levels.difficulty import (
    SCROLL_SPEED,
    between,
    difficulty,
)
from pewpewdev.tools.levels.enemies import GROUND, UNLOCK
from pewpewdev.tools.levels.plan import LevelPlan, WorldPlan
from pewpewdev.tools.levels.waves import (
    AFTER_MINI_BOSS,
    BOSS_DELAY,
    FIRST_WAVE,
    SECOND_HALF_HARDER,
    make_half,
)
from pewpewdev.tools.levels.worlds import WORLDS


def make_level(rng: random.Random, world: WorldPlan, plan: LevelPlan, d: int) -> dict[str, Any]:
    """The first half at the level's difficulty, its mini boss, the second half harder, its final boss."""
    pool = sorted(
        enemy for enemy, unlock in UNLOCK.items() if unlock <= d and (world.ground_units or enemy not in GROUND)
    )
    first = make_half(rng, pool, d, FIRST_WAVE)
    mini_boss = first[-1]["time"] + BOSS_DELAY
    second = make_half(rng, pool, d, mini_boss + AFTER_MINI_BOSS, SECOND_HALF_HARDER)
    waves = [
        *first,
        {"time": round(mini_boss, 1), "enemy": plan.mini_boss},
        *second,
        {"time": round(second[-1]["time"] + BOSS_DELAY, 1), "enemy": plan.final_boss},
    ]
    level: dict[str, Any] = {
        "name": plan.name,
        "scroll_speed": round(between(SCROLL_SPEED, d), 3),
        "background": world.background,
        "background_seed": plan.seed or rng.randint(100, 9999),
    }
    if plan.time_of_day != "day":
        level["time_of_day"] = plan.time_of_day
    if plan.clouds:
        level["clouds"] = plan.clouds
    if plan.scenery:
        level["scenery"] = plan.scenery
    return {**level, "waves": waves}


def generate(seed: int) -> dict[tuple[int, int], dict[str, Any]]:
    """Every level, by (world, level) from 1."""
    rng = random.Random(seed)  # noqa: S311 - level layouts, not cryptography
    return {
        (w, n): make_level(rng, world, plan, difficulty(w, n))
        for w, world in enumerate(WORLDS, start=1)
        for n, plan in enumerate(world.levels, start=1)
    }
