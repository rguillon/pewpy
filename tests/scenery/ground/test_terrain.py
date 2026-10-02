import pytest

from pewpy.scenery import params
from pewpy.scenery.ground.terrain import CHUNKS, Area, Terrain

AREA = Area(-1.0, 1.0, -1.2, 1.8)
GROUNDS = [name for name in params.backgrounds() if params.resolve(name).ground is not None]


@pytest.mark.parametrize("name", GROUNDS)
def test_every_ground_builds_whatever_its_layout(name: str) -> None:
    """Features placed near the ground's edges (a refinery's stacks in small yards) stay inside it."""
    for seed in range(10):
        terrain = Terrain(AREA, 1.0, params.resolve(name), seed=seed)
        assert terrain.relief.rows == terrain.relief_rows * terrain.chunks


def test_a_ground_is_wider_than_its_area_and_centered() -> None:
    terrain = Terrain(AREA, 1.0, params.resolve("planet"), seed=0)
    assert terrain.width >= AREA.width
    assert terrain.left == pytest.approx(-terrain.width / 2)


def test_a_scenery_without_a_ground_has_no_terrain() -> None:
    with pytest.raises(ValueError, match="no ground"):
        Terrain(AREA, 1.0, params.resolve("space"))


def test_ground_loop_grows_to_stay_longer_than_the_screen() -> None:
    tall = Area(-1, 1, -10, 10)
    terrain = Terrain(tall, 1.0, params.resolve("planet"))
    assert terrain.chunks > CHUNKS
    assert terrain.loop_length >= tall.height + terrain.chunk_height


def test_a_ground_gets_a_relief_the_size_of_its_loop() -> None:
    area = Area(-1.0, 1.0, -1.3, 1.3)
    terrain = Terrain(area, 1.0, params.resolve("mountains"), seed=1)
    assert terrain.relief.rows == terrain.relief_rows * terrain.chunks
    assert terrain.relief.step_y * terrain.relief.rows == pytest.approx(terrain.loop_length)
    assert terrain.relief.step_x * (terrain.relief.columns - 1) >= area.width


def test_a_built_up_terrain_splits_its_props_between_its_chunks() -> None:
    terrain = Terrain(Area(-1.0, 1.0, -1.3, 1.3), 1.0, params.resolve("city"), seed=5)
    assert terrain.layout is not None
    assert terrain.props
    shares = [terrain.chunk_props(chunk) for chunk in range(terrain.chunks)]
    assert sum(len(share) for share in shares) == len(terrain.props)
