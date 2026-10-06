import json
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pytest

from pewpy import config, data
from pewpy.game.enemies.enemy import Enemy
from pewpy.game.enemies.errors import EnemySpecError
from pewpy.game.enemies.mounts import Mount, model_mounts, parse_mounts
from pewpy.game.enemies.spec import parse_enemy
from pewpy.game.entities import Entity
from pewpy.game.weapons.bullets import Bullet
from pewpy.game.weapons.guns import Shooter, fire, parse_gun

V = config.MODEL_VOXEL
DT = 1 / 60
TARGET = Entity(x=0.0, y=-0.75)
# 5 columns, 4 rows: a gun on the left of its front row, missiles on its right.
GUNNER = {
    "layers": [[".....", ".....", ".....", "....."]],
    "palette": {},
    "weapons": [{"number": 1, "kind": "gun", "x": 0, "y": 3}, {"number": 2, "kind": "missile", "x": 4, "y": 3}],
}
SHOT = {"pattern": "fan", "interval": 1.0, "speed": 0.5, "off_screen": "fire"}


@pytest.fixture
def models(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[Path]:
    """Use a data folder of our own, with the gunner's model in it."""
    folder = tmp_path / "models"
    folder.mkdir()
    (folder / "gunner.json").write_text(json.dumps(GUNNER))
    monkeypatch.setattr(data, "data_folder", lambda: tmp_path)
    model_mounts.cache_clear()
    yield folder
    model_mounts.cache_clear()


def gunner(guns: list[dict[str, Any]], **body: object) -> Enemy:
    spec = parse_enemy("test", {"drawing": "gunner", "states": [{"name": "a", "guns": guns}], **body}, "test")
    return Enemy.from_spec(spec, 0.0, 0.5)


def shots(enemy: Enemy) -> list[tuple[float, float]]:
    """Where the bullets of its first frame are, from its middle (they start moving on the next one)."""
    created = [entity for entity in enemy.update(DT, TARGET, 0.0) if isinstance(entity, Bullet)]
    return [(bullet.x - enemy.x, bullet.y - enemy.y) for bullet in created]


def test_a_weapon_fires_from_its_barrels_tip_facing_down_the_screen() -> None:
    found = parse_mounts(GUNNER, "gunner.json")
    assert found == {1: Mount(1, "gun", -2 * V, -2 * V), 2: Mount(2, "missile", 2 * V, -2 * V)}
    flat = {
        "rows": ["...", "..."],
        "palette": {},
        "scale": 2,
        "weapons": [{"number": 3, "kind": "gun", "x": 1, "y": 1}],
    }
    assert parse_mounts(flat, "flat.json") == {3: Mount(3, "gun", 0.0, -V / 2)}
    assert parse_mounts({"layers": [["."]], "palette": {}}, "none.json") == {}


@pytest.mark.parametrize(
    "weapons",
    [
        {"number": 1},
        [{"number": 1, "kind": "gun", "x": 0}],
        [{"number": 0, "kind": "gun", "x": 0, "y": 0}],
        [{"number": 1, "kind": "gun", "x": 0, "y": 0}, {"number": 1, "kind": "gun", "x": 1, "y": 0}],
        [{"number": 1, "kind": "", "x": 0, "y": 0}],
        [{"number": 1, "kind": "gun", "x": "left", "y": 0}],
        [{"number": 1, "kind": "gun", "x": 5, "y": 0}],
    ],
    ids=["not a list", "missing key", "number 0", "twice the same number", "no kind", "not a number", "off the model"],
)
def test_wrong_weapons_are_refused(weapons: object) -> None:
    with pytest.raises((TypeError, ValueError), match=r"bad\.json"):
        parse_mounts({**GUNNER, "weapons": weapons}, "bad.json")


def test_only_drawings_that_give_their_size_can_have_weapons() -> None:
    with pytest.raises(ValueError, match="only a flat or 3D drawing"):
        parse_mounts({"vox": "ship.vox", "weapons": GUNNER["weapons"]}, "ship.json")


def test_a_models_weapons_are_read_from_its_file(models: Path) -> None:
    assert set(model_mounts("gunner")) == {1, 2}
    assert model_mounts("built_in_code") == {}
    assert model_mounts("") == {}
    assert models.is_dir()


@pytest.mark.usefixtures("models")
def test_an_enemys_guns_fire_from_its_weapons_in_turn() -> None:
    # Three guns, two weapons: the third gun goes back to the first weapon.
    enemy = gunner([SHOT, SHOT, SHOT])
    assert shots(enemy) == [
        pytest.approx((-2 * V, -2 * V)),
        pytest.approx((2 * V, -2 * V)),
        pytest.approx((-2 * V, -2 * V)),
    ]


@pytest.mark.usefixtures("models")
def test_a_gun_can_pick_its_weapons_or_keep_its_own_origins() -> None:
    assert shots(gunner([{**SHOT, "weapon": 2}])) == [pytest.approx((2 * V, -2 * V))]
    assert len(shots(gunner([{**SHOT, "weapons": [1, 2]}]))) == 2
    assert shots(gunner([{**SHOT, "origins": [[0.01, 0.0]]}])) == [pytest.approx((0.01, 0.0))]


def test_without_weapons_a_gun_fires_from_its_origins() -> None:
    piece = Entity(x=0.0, y=0.0, width=0.1, height=0.1)
    gun = parse_gun({**SHOT, "origins": [["0.5w", 0.0]]})
    (bullet,) = fire(gun, Shooter(piece, TARGET))
    assert (bullet.x, bullet.y) == pytest.approx((0.05, 0.0))


def test_a_gun_fires_from_its_origins_or_its_weapons_not_both() -> None:
    with pytest.raises(ValueError, match="not both"):
        parse_gun({**SHOT, "origins": [[0, 0]], "weapon": 1})


@pytest.mark.usefixtures("models")
def test_the_weapons_turn_with_a_model_facing_its_way() -> None:
    still = gunner([SHOT], facing="travel")
    assert still.mounts() == {1: pytest.approx((-2 * V, -2 * V)), 2: pytest.approx((2 * V, -2 * V))}
    flying_right = gunner([SHOT], facing="travel", velocity=[0.5, 0.0])
    # Its nose, down the screen, now points right (a quarter turn counterclockwise): its front on the right.
    assert flying_right.mounts() == {1: pytest.approx((2 * V, -2 * V)), 2: pytest.approx((2 * V, 2 * V))}


@pytest.mark.usefixtures("models")
@pytest.mark.parametrize(
    "body",
    [
        {"drawing": "gunner", "states": [{"name": "a", "guns": [{**SHOT, "weapon": 3}]}]},
        {
            "drawing": "gunner",
            "states": [{"name": "a", "guns": [{**SHOT, "sequence": [{"pattern": "ring", "weapon": 4}]}]}],
        },
        {"drawing": "gunner", "start": [{"type": "fire", "gun": {**SHOT, "weapon": 3}}]},
        {
            "drawing": "gunner",
            "parts": [{"name": "arm", "drawing": "built_in_code", "x": 0.1, "y": 0.0}],
            "states": [{"name": "a", "guns": [{**SHOT, "from": "arm", "weapon": 1}]}],
        },
    ],
    ids=["its own model", "in a sequence", "fired by an action", "a part's model"],
)
def test_a_gun_can_only_fire_from_weapons_its_model_has(body: dict[str, Any]) -> None:
    with pytest.raises(EnemySpecError, match="doesn't have"):
        parse_enemy("test", body, "test")


def test_a_wrong_model_makes_a_wrong_enemy(models: Path) -> None:
    (models / "broken.json").write_text(json.dumps({**GUNNER, "weapons": {"number": 1}}))
    with pytest.raises(EnemySpecError, match="'weapons' must be a list"):
        parse_enemy("test", {"drawing": "broken", "states": [{"name": "a", "guns": [{**SHOT, "weapon": 1}]}]}, "test")
