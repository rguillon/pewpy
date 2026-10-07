"""The models the Dev menu's browser shows."""

import json
from pathlib import Path

from pewpy.dev.catalog import CATEGORIES, entries, read_data
from pewpy.game.level import load_worlds
from pewpy.game.player import SHIPS
from pewpy.graphics.models import BUILT_MODELS


def test_the_players_ships_are_shown_with_their_descriptions() -> None:
    ships = entries("players")
    assert [ship.drawing for ship in ships] == [spec.drawing for spec in SHIPS.values()]
    assert ships[0].title == "Vanguard"
    assert ships[0].description == "Balanced"


def test_the_enemies_drawn_from_files_are_shown_once_each() -> None:
    enemies = entries("enemies")
    drawings = [enemy.drawing for enemy in enemies]
    assert len(drawings) == len(set(drawings))
    assert not set(drawings) & set(BUILT_MODELS)  # those are built in code
    drone = next(enemy for enemy in enemies if enemy.key == "drone")
    assert drone.description.startswith("Comes straight down")
    assert next(enemy for enemy in enemies if enemy.key == "mine_layer").title == "Mine Layer"


def test_the_bosses_are_shown_with_their_parts() -> None:
    bosses = {boss.key: boss for boss in entries("bosses")}
    assert bosses["avalanche"].file == "bosses/final_bosses.json"
    body = read_data("bosses/mini_bosses.json")["rockbreaker"]
    rockbreaker = bosses["rockbreaker"]
    assert [part.name for part in rockbreaker.parts] == [part["name"] for part in body["parts"]]
    drawing = body["parts"][0]["drawing"]
    count = sum(part["drawing"] == drawing for part in body["parts"])
    assert f"{count} {drawing.removeprefix('rockbreaker:')}" in rockbreaker.description


def test_a_boss_without_parts_says_nothing_of_them(data_copy: Path) -> None:
    bosses = read_data("bosses/mini_bosses.json")
    bosses["sentinel"].pop("parts", None)
    (data_copy / "bosses/mini_bosses.json").write_text(json.dumps(bosses))
    sentinel = next(boss for boss in entries("bosses") if boss.key == "sentinel")
    assert not sentinel.parts
    assert "Parts" not in sentinel.description


def test_every_category_has_a_title() -> None:
    assert list(CATEGORIES) == ["players", "enemies", "bosses"]


def test_the_bosses_come_as_theyre_played_mini_boss_first() -> None:
    bosses = entries("bosses")
    levels = [level for world in load_worlds() for level in world.levels]
    played = [wave.enemy for level in levels for wave in level.waves if wave.enemy in {boss.key for boss in bosses}]
    assert [boss.key for boss in bosses] == list(dict.fromkeys(played))
    assert [boss.file for boss in bosses[:2]] == ["bosses/mini_bosses.json", "bosses/final_bosses.json"]


def test_a_boss_in_no_level_comes_last(data_copy: Path) -> None:
    bosses = read_data("bosses/mini_bosses.json")
    bosses["spare"] = {**bosses["sentinel"], "name": "SPARE"}
    (data_copy / "bosses/mini_bosses.json").write_text(json.dumps(bosses))
    assert entries("bosses")[-1].key == "spare"
