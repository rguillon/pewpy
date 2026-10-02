"""A final boss from its plan (plans.json)."""

from typing import Any

from pewpewdev.tools.final_bosses.boss import BossSpec, final_boss


def plan_boss(plan: dict[str, Any]) -> BossSpec:
    """Make the boss a plan describes."""
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
