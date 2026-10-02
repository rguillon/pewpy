"""The enemy files as a whole (not each enemy: they're data)."""

import json

import pytest

from pewpy import config
from pewpy.data import data_folder
from pewpy.game.enemies.kinds import BOSSES, ENEMIES
from pewpy.game.enemies.roster import ENEMY_TYPES
from pewpy.game.enemies.spec import EnemySpec, load_enemy_specs
from pewpy.game.weapons.guns import PROJECTILES, Gun


def guns_of(spec: EnemySpec) -> list[Gun]:
    found = [gun for state in spec.states for _, gun in state.guns]
    found += [action.gun for state in spec.states for exit_ in state.exits for action in exit_.then if action.gun]
    return found + [item for gun in found for item in gun.sequence]


@pytest.mark.parametrize("spec", [*ENEMIES.values(), *BOSSES.values()], ids=lambda spec: spec.kind)
def test_every_enemy_launched_or_released_exists(spec):
    for gun in guns_of(spec):
        assert not gun.spawn or gun.spawn in ENEMIES
        assert not gun.projectile or PROJECTILES[gun.projectile][0] in ENEMIES
    assert all(spawn.kind in ENEMIES for spawn in spec.on_destroyed)


@pytest.mark.parametrize("spec", load_enemy_specs("enemies/fleet.json").values(), ids=lambda spec: spec.kind)
def test_every_fleet_hitbox_is_its_drawing_and_every_drawing_has_engines(spec):
    drawing = json.loads((data_folder() / "models" / f"{spec.drawing}.json").read_text())
    rows = drawing["rows"]
    assert spec.width == pytest.approx(len(rows[0]) * config.MODEL_VOXEL)
    assert spec.height == pytest.approx(len(rows) * config.MODEL_VOXEL)
    assert drawing["engines"]


def test_the_levels_place_enemies_not_what_they_launch():
    assert set(ENEMIES) - set(ENEMY_TYPES) == {"rocket", "homing_missile", "cluster_bomb", "mine"}
