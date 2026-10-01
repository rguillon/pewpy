import pytest

from pewpy.game.level import load_levels
from pewpy.game.roster import ENEMY_TYPES
from pewpy.scenery import params
from pewpy.scenery.terrain import Area, Terrain

AREA = Area(-1.0, 1.0, -1.2, 1.8)
GROUNDS = [name for name in params.backgrounds() if params.resolve(name).ground is not None]


@pytest.mark.parametrize("name", GROUNDS)
def test_every_ground_stays_behind_the_ships(name):
    ground = params.resolve(name).ground
    assert ground is not None
    assert ground.depth - ground.max_height > 0.1  # the ships fly at depth 0 and are about 0.1 deep


def test_every_ground_has_levels():
    assert set(GROUNDS) <= {level.background for level in load_levels()}


def test_no_ground_enemies_over_water_or_clouds():
    # Turrets, tanks and the like are on the ground: they would look odd on the sea, the ice floes or the clouds.
    for level in load_levels():
        if level.background in ("pack_ice", "swamp", "clouds", "ocean"):
            ground = [
                wave.enemy for wave in level.waves if wave.enemy in ENEMY_TYPES and ENEMY_TYPES[wave.enemy].ground
            ]
            assert ground == [], level.name


@pytest.mark.parametrize("name", GROUNDS)
def test_every_ground_builds_whatever_its_layout(name):
    """Features placed near the ground's edges (a refinery's stacks in small yards) stay inside it."""
    for seed in range(10):
        terrain = Terrain(AREA, 1.0, params.resolve(name), seed=seed)
        assert terrain.relief.rows == terrain.relief_rows * terrain.chunks


def test_a_ground_is_wider_than_its_area_and_centered():
    terrain = Terrain(AREA, 1.0, params.resolve("planet"), seed=0)
    assert terrain.width >= AREA.width
    assert terrain.left == pytest.approx(-terrain.width / 2)


def test_a_scenery_without_a_ground_has_no_terrain():
    with pytest.raises(ValueError, match="no ground"):
        Terrain(AREA, 1.0, params.resolve("space"))
