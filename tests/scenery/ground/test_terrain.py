from itertools import pairwise

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
    terrain = Terrain(AREA, 1.0, params.resolve("savanna"), seed=0)
    assert terrain.width >= AREA.width
    assert terrain.left == pytest.approx(-terrain.width / 2)


def test_a_scenery_without_a_ground_has_no_terrain() -> None:
    with pytest.raises(ValueError, match="no ground"):
        Terrain(AREA, 1.0, params.resolve("space"))


def test_ground_loop_grows_to_stay_longer_than_the_screen() -> None:
    tall = Area(-1, 1, -10, 10)
    terrain = Terrain(tall, 1.0, params.resolve("savanna"))
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


def test_a_ground_can_go_bare_without_outposts_or_flora() -> None:
    bare = params.resolve("savanna", {"outposts": None, "flora": None})
    terrain = Terrain(AREA, 1.0, bare, seed=0)
    assert terrain.props == []
    assert terrain.relief.rows == terrain.relief_rows * terrain.chunks


def savanna() -> Terrain:
    return Terrain(AREA, 1.0, params.resolve("savanna"), seed=0)


def test_ground_chunks_follow_each_other_down_and_loop() -> None:
    terrain = savanna()
    tops = [terrain.chunk_top(chunk) for chunk in range(CHUNKS)]
    for upper, lower in pairwise(tops):
        assert upper - lower == pytest.approx(terrain.chunk_height)
    terrain.update(1.0, scroll_speed=0.1)
    assert terrain.chunk_top(0) == pytest.approx(tops[0] - 0.1)
    terrain.update(terrain.loop_length / 0.1 - 1.0, scroll_speed=0.1)  # one full loop in total
    assert terrain.chunk_top(0) == pytest.approx(tops[0])


def test_ground_always_covers_the_screen() -> None:
    terrain = savanna()
    for _ in range(50):
        terrain.update(0.37, scroll_speed=0.5)
        spans = sorted((top - terrain.chunk_height, top) for top in map(terrain.chunk_top, range(CHUNKS)))
        covered_to = AREA.bottom
        for bottom, top in spans:
            if bottom <= covered_to + 1e-9:
                covered_to = max(covered_to, top)
        assert covered_to >= AREA.top
