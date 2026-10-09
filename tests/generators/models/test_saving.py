"""Saving a new model in place of one of the game's."""

import json
import random
from pathlib import Path
from typing import Any

from pewpy import config
from pewpy.data import read_model
from pewpy.game.enemies.kinds import ENEMIES, MINI_BOSSES, reload_kinds
from pewpy.generators.models.catalog import BossPart, entries, read_data
from pewpy.generators.models.final_bosses.plans import plan_boss
from pewpy.generators.models.final_bosses.writing import boss_json
from pewpy.generators.models.saving import (
    DEFAULT_PART,
    drawn_size,
    front_to_back,
    lopsided,
    new_parts,
    remap_phases,
    save_boss,
    save_ship,
)
from pewpy.generators.models.sized import parts_for, sized_boss, sized_ship


def entry(category: str, key: str):  # noqa: ANN201 - an Entry
    return next(found for found in entries(category) if found.key == key)


def test_a_boss_is_lopsided_when_a_part_has_no_mirror_image() -> None:
    pair = (BossPart("l", "x_gun", -0.1, 0.0), BossPart("r", "x_gun", 0.1, 0.0))
    assert not lopsided(pair)
    assert not lopsided((*pair, BossPart("bow", "x_dish", 0.0, -0.1)))
    assert lopsided((*pair, BossPart("odd", "x_dish", 0.2, 0.0)))


def test_new_parts_are_named_after_their_kind() -> None:
    made = {
        "parts": [({"layers": [["aa"]]}, -3, 1), ({"layers": [["aa"]]}, 3, 1), ({"layers": [["a"]]}, 0, -2)],
        "groups": [0, 0, 1],
        "kinds": ["launcher", "launcher", "launcher"],
    }
    parts = new_parts("boss", made)
    assert [part["name"] for part, _ in parts] == ["launcher 1", "launcher 2", "launcher 3"]
    assert [part["drawing"] for part, _ in parts] == ["boss:launcher", "boss:launcher", "boss:launcher2"]
    assert parts[0][0]["x"] == round(-3 * config.MODEL_VOXEL, 3)


def test_parts_are_split_front_to_back_groups_together_when_they_can() -> None:
    parts = [
        {"name": "a", "drawing": "back", "y": 0.1},
        {"name": "b", "drawing": "front", "y": -0.1},
        {"name": "c", "drawing": "back", "y": 0.1},
        {"name": "d", "drawing": "front", "y": -0.1},
    ]
    assert [[part["name"] for part in lot] for lot in front_to_back(parts, 2)] == [["b", "d"], ["a", "c"]]
    assert [[part["name"] for part in lot] for lot in front_to_back(parts, 3)] == [["b"], ["d", "a"], ["c"]]


def test_a_mini_bosss_phases_name_its_new_parts() -> None:
    phases: list[dict[str, Any]] = [
        {"until": {"parts": ["left gun", "right gun"]}, "guns": [{"from": "left gun"}, {"pattern": "ring"}]},
        {"until": {"parts": ["dish"]}, "guns": [{"from": ["dish", "spare"]}]},
        {"guns": [{"from": "spare"}]},
    ]
    body: dict[str, Any] = {
        "parts": [
            {"name": "left gun", "health": 30.0, "points": 500},
            {"name": "right gun", "health": 30.0, "points": 500},
            {"name": "dish", "health": 10.0, "points": 100},
            {"name": "spare", "health": 5.0, "points": 50},
        ],
        "phases": phases,
    }
    parts = [
        {"name": "drill 1", "drawing": "front", "y": -0.1},
        {"name": "drill 2", "drawing": "front", "y": -0.1},
        {"name": "radar 3", "drawing": "back", "y": 0.1},
    ]
    remap_phases(body, parts)
    first, second, rage = phases
    assert first["until"]["parts"] == ["drill 1", "drill 2"]
    assert first["guns"] == [{"from": ["drill 1", "drill 2"]}, {"pattern": "ring"}]
    assert second["until"]["parts"] == ["radar 3"]
    assert second["guns"][0]["from"] == ["radar 3", "drill 1", "drill 2"]  # "spare" was waited for by no phase
    assert rage["guns"][0]["from"] == ["drill 1", "drill 2", "radar 3"]
    health = {part["name"]: (part["health"], part["points"]) for part in body["parts"]}
    assert health == {"drill 1": (30.0, 500), "drill 2": (30.0, 500), "radar 3": (10.0, 100)}


def test_a_mini_boss_without_parts_gets_some() -> None:
    body = {"phases": [{"until": {"health_below": 0.5}, "guns": [{"pattern": "fan"}]}]}
    remap_phases(body, [{"name": "drill 1", "drawing": "d", "y": 0.0}])
    assert body["parts"] == [{"name": "drill 1", "drawing": "d", "y": 0.0, **DEFAULT_PART}]
    assert body["phases"] == [{"until": {"health_below": 0.5}, "guns": [{"pattern": "fan"}]}]


def test_a_new_ship_replaces_its_model_its_hitbox_following_its_size(data_copy: Path) -> None:
    vanguard = entry("players", "vanguard")
    hitbox = read_data("ships.json")["vanguard"]["size"]
    drawing = sized_ship(random.Random(1), (0.15, 0.15), player=True)
    save_ship(vanguard, drawing, (0.1, 0.1))  # half as big again
    assert json.loads((data_copy / "models/player/player.json").read_text()) == drawing
    assert read_data("ships.json")["vanguard"]["size"] == round(hitbox * 1.5, 3)


def test_an_enemys_hitbox_follows_its_size(data_copy: Path) -> None:  # noqa: ARG001 - its data
    gunship = entry("enemies", "gunship")
    width, height = ENEMIES["gunship"].width, ENEMIES["gunship"].height
    save_ship(gunship, sized_ship(random.Random(1), (0.3, 0.2)), (0.15, 0.2))
    assert read_data("enemies/catalog.json")["gunship"]["size"] == [round(2 * width, 3), round(height, 3)]


def test_an_enemy_sized_by_its_cubes_gets_its_new_ones(data_copy: Path) -> None:  # noqa: ARG001 - its data
    dart = entry("enemies", "dart")
    drawing = sized_ship(random.Random(1), (0.1, 0.12))
    save_ship(dart, drawing, (0.1, 0.12))
    assert read_data("enemies/fleet.json")["dart"]["voxels"] == [
        len(drawing["layers"][0][0]),
        len(drawing["layers"][0]),
    ]


def test_a_new_mini_boss_gets_new_parts_and_loses_the_old_ones(data_copy: Path) -> None:
    rockbreaker = entry("bosses", "rockbreaker")
    made = sized_boss(random.Random(1), (0.4, 0.3))
    save_boss(rockbreaker, made)
    body = json.loads((data_copy / "bosses/mini_bosses.json").read_text())["rockbreaker"]
    assert body["size"] == drawn_size(made["core"])
    assert len(body["parts"]) == parts_for((0.4, 0.3)) == len(made["parts"])
    names = [part["name"] for part in body["parts"]]
    assert set(body["phases"][0]["until"]["parts"]) <= set(names)
    core = json.loads((data_copy / "models/bosses/rockbreaker.json").read_text())
    for part in body["parts"]:
        drawing, _ = read_model(part["drawing"])  # in the boss's file
        assert part["drawing"].startswith("rockbreaker:")
        assert part["size"] == drawn_size(drawing) == drawing["size"]
    assert set(core["parts"]) == {part["drawing"].removeprefix("rockbreaker:") for part in body["parts"]}  # only new
    assert core["size"] == [0.4, 0.3]
    reload_kinds()  # the game reads it
    assert len(MINI_BOSSES["rockbreaker"].parts) == len(names)


def test_a_new_final_boss_is_made_again_from_its_changed_plan(data_copy: Path) -> None:
    avalanche = entry("bosses", "avalanche")
    made = sized_boss(random.Random(2), (0.5, 0.287))
    save_boss(avalanche, made)
    plan = json.loads((data_copy / "bosses/final_plans.json").read_text())["avalanche"]
    body = json.loads((data_copy / "bosses/final_bosses.json").read_text())["avalanche"]
    assert body == json.loads(json.dumps(boss_json(plan_boss(plan), plan["note"])))
    assert [plan["width"], plan["height"]] == body["size"] == drawn_size(made["core"])
    assert len(plan["parts"]) == len(body["parts"]) == parts_for((0.5, 0.287))
    assert [part["x"] for part in plan["parts"]] == [part["x"] for part in body["parts"]]


def test_a_flat_drawing_covers_its_rows() -> None:
    assert drawn_size({"rows": ["aaa", "aaa"]}) == [round(3 * config.MODEL_VOXEL, 3), round(2 * config.MODEL_VOXEL, 3)]
