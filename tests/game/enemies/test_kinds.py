"""The enemy files as a whole (not each enemy: they're data)."""

import json

import pytest

from pewpy import config
from pewpy.data import model_path
from pewpy.game.enemies.actions import Fire
from pewpy.game.enemies.kinds import BOSSES, ENEMIES, drawings
from pewpy.game.enemies.roster import ENEMY_TYPES
from pewpy.game.enemies.spec import EnemySpec, load_enemy_specs
from pewpy.game.weapons.guns import PROJECTILES, Gun


def guns_of(spec: EnemySpec) -> list[Gun]:
    found = [gun for state in spec.states for _, gun in state.guns]
    actions = [action for state in spec.states for exit_ in state.exits for action in exit_.then]
    found += [action.gun for action in actions if isinstance(action, Fire)]
    return found + [item for gun in found for item in gun.sequence]


@pytest.mark.parametrize("spec", [*ENEMIES.values(), *BOSSES.values()], ids=lambda spec: spec.kind)
def test_every_enemy_launched_or_released_exists(spec: EnemySpec) -> None:
    for gun in guns_of(spec):
        assert not gun.spawn or gun.spawn in ENEMIES
        assert not gun.projectile or PROJECTILES[gun.projectile][0] in ENEMIES
    assert all(spawn.kind in ENEMIES for spawn in spec.on_destroyed)


@pytest.mark.parametrize("spec", load_enemy_specs("enemies/fleet.json").values(), ids=lambda spec: spec.kind)
def test_every_fleet_hitbox_is_its_drawing_and_every_drawing_has_engines(spec: EnemySpec) -> None:
    drawing = json.loads(model_path(spec.drawing).read_text())
    rows = drawing["rows"]
    assert spec.width == pytest.approx(len(rows[0]) * config.MODEL_VOXEL)
    assert spec.height == pytest.approx(len(rows) * config.MODEL_VOXEL)
    assert drawing["engines"]


def test_the_levels_place_enemies_not_what_they_launch() -> None:
    assert set(ENEMIES) - set(ENEMY_TYPES) == {"rocket", "homing_missile", "cluster_bomb", "mine"}


def test_an_enemy_needs_its_models_its_parts_and_those_of_what_it_launches() -> None:
    assert drawings("rockbreaker") == {"rockbreaker", "rockbreaker:drill"}
    assert drawings("splitter") == {"splitter", "swarmer"}  # what it releases when shot down
    assert drawings("missile_silo") == {"missile_silo", "homing_missile"}  # what its guns launch
