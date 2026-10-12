import json

from pewpy.data import data_folder
from pewpy.game.weapons.guns import Gun
from pewpy.generators.models.final_bosses.boss import final_boss
from pewpy.generators.models.final_bosses.plans import plan_boss
from pewpy.generators.models.final_bosses.writing import boss_json, gun_json


def test_a_boss_without_a_note_is_written_without_one() -> None:
    plan = next(iter(json.loads((data_folder() / "bosses" / "final_plans.json").read_text()).values()))
    assert "note" not in boss_json(plan_boss(plan))
    assert boss_json(plan_boss(plan), "a note")["note"] == "a note"


def test_a_guns_sequence_is_written_as_guns() -> None:
    gun = Gun("aimed", 1.0, 0.5, sequence=(Gun("fan", 0.5, 0.4),))
    assert gun_json(gun)["sequence"] == [{"pattern": "fan", "interval": 0.5, "speed": 0.4}]


def test_a_gun_is_written_with_only_what_isnt_usual() -> None:
    assert gun_json(Gun("ring", 2.0, 0.4, count=12, turn=9)) == {
        "pattern": "ring",
        "interval": 2.0,
        "speed": 0.4,
        "count": 12,
        "turn": 9,
    }


def test_a_boss_is_written_as_the_game_reads_bosses_with_phases_and_parts() -> None:
    boss = final_boss("BIG", "big", 0.5, 0.3, 5, ("fan", "aimed", "laser", "ring"), (("big:gun", -0.2, 0.0, 0.1, 0.1),))
    written = boss_json(boss)
    assert written["boss"] is True
    assert (written["name"], written["size"]) == ("BIG", [0.5, 0.3])
    assert [part["name"] for part in written["parts"]] == ["gun 1"]
    assert len(written["phases"]) == len(boss.phases)
