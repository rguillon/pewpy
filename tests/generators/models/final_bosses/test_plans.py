"""The final bosses, made from their plans."""

import json

from pewpy.data import data_folder
from pewpy.generators.compact_json import compact_json
from pewpy.generators.models.final_bosses.plans import plan_boss
from pewpy.generators.models.final_bosses.writing import boss_json


def plans() -> dict:
    return json.loads((data_folder() / "bosses" / "final_plans.json").read_text())


def test_the_final_bosses_are_what_their_plans_make() -> None:
    made = {name: boss_json(plan_boss(plan), plan.get("note", "")) for name, plan in plans().items()}
    assert compact_json(made) == (data_folder() / "bosses" / "final_bosses.json").read_text()


def test_a_plan_gives_the_boss_its_name_drawing_size_and_parts() -> None:
    plan = next(iter(plans().values()))
    boss = plan_boss(plan)
    assert (boss.name, boss.drawing, boss.width, boss.height) == (
        plan["name"],
        plan["drawing"],
        plan["width"],
        plan["height"],
    )
    assert [part.drawing for part in boss.parts] == [part["drawing"] for part in plan["parts"]]
