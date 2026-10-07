"""The final bosses, made from their plans, and how the bosses' files are written."""

import json

from pewpy.data import data_folder
from pewpy.game.weapons.guns import Gun
from pewpy.makers.compact_json import WIDTH, compact_json
from pewpy.makers.final_bosses.boss import final_boss
from pewpy.makers.final_bosses.plans import plan_boss
from pewpy.makers.final_bosses.writing import boss_json, gun_json


def test_the_final_bosses_are_what_their_plans_make() -> None:
    plans = json.loads((data_folder() / "bosses" / "final_plans.json").read_text())
    made = {name: boss_json(plan_boss(plan), plan.get("note", "")) for name, plan in plans.items()}
    assert compact_json(made) == (data_folder() / "bosses" / "final_bosses.json").read_text()


def test_a_boss_without_a_note_is_written_without_one() -> None:
    plan = next(iter(json.loads((data_folder() / "bosses" / "final_plans.json").read_text()).values()))
    assert "note" not in boss_json(plan_boss(plan))


def test_json_is_written_compactly_lines_fitting() -> None:
    value = {"short": [1, 2], "long": ["x" * 60, "y" * 60, {"z": "z" * 50}], "empty": []}
    text = compact_json(value)
    assert json.loads(text) == value
    assert all(len(line) <= WIDTH for line in text.splitlines())
    assert '"short": [1, 2]' in text
    assert compact_json([]) == "[]\n"


def test_a_final_boss_without_parts_fights_with_its_core_only() -> None:
    spec = final_boss("BARE", "bare", 0.3, 0.2, 10, ("fan", "aimed", "laser", "ring"), ())
    assert len(spec.phases) == 2
    assert not any(phase.armored for phase in spec.phases)


def test_a_guns_sequence_is_written_as_guns() -> None:
    gun = Gun("aimed", 1.0, 0.5, sequence=(Gun("fan", 0.5, 0.4),))
    assert gun_json(gun)["sequence"] == [{"pattern": "fan", "interval": 0.5, "speed": 0.4}]
