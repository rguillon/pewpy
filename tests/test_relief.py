import numpy as np
import pytest

from pewpy import landscapes, relief
from pewpy.background import Area
from pewpy.terrain import BIOMES, Terrain


def rng() -> np.random.Generator:
    return np.random.default_rng(0)


def test_noise_is_smooth_between_0_and_1_and_loops_along_the_rows():
    noise = relief.periodic_noise(rng(), 120, 50, cell=17.3)
    assert noise.shape == (120, 50)
    assert float(np.min(noise)) >= 0.0 and float(np.max(noise)) <= 1.0
    steps = float(np.max(np.abs(np.diff(noise, axis=0))))
    assert float(np.max(np.abs(noise[-1] - noise[0]))) <= steps * 1.01  # the last row runs on into the first


def test_mountains_stay_between_the_base_layer_and_their_highest_point():
    heights = landscapes.mountains(rng(), 200, 80, 0.5, 0.02).heights
    assert float(np.min(heights)) == 0.0  # flat valley floors
    assert float(np.max(heights)) == pytest.approx(0.5)
    assert float(np.max(np.abs(heights[-1] - heights[0]))) < 0.05  # no cliff where the loop starts again


def test_a_peak_casts_its_shadow_away_from_the_sun_and_rises_above_a_hollow():
    heights = np.zeros((60, 60))
    heights[20, 20] = 0.3
    shape = relief.make_relief(relief.Shape(heights), 0.02, 0.02)
    assert shape.shadow[25, 25] == 1.0  # down and right of the peak: the sun is up and left
    assert shape.shadow[15, 15] == 0.0
    assert shape.shadow[20, 20] == 0.0  # the peak itself is in the sun
    assert np.allclose(np.linalg.norm(shape.normals, axis=-1), 1.0)
    pit = np.full((60, 60), 0.2)
    pit[30, 30] = 0.0
    cavity = relief.make_relief(relief.Shape(pit), 0.02, 0.02).cavity
    assert cavity[30, 30] > 0.1
    assert cavity[30, 30] == float(np.max(cavity))


def test_a_smooth_biome_gets_a_relief_the_size_of_its_loop():
    terrain = Terrain(Area(-1.0, 1.0, -1.3, 1.3), 1.0, seed=1, biome="mountains")
    assert BIOMES["mountains"].relief is not None
    assert terrain.relief is not None
    assert terrain.relief.rows == terrain.relief_rows * terrain.chunks
    assert terrain.relief.step_y * terrain.relief.rows == pytest.approx(terrain.loop_length)
    assert terrain.relief.step_x * (terrain.relief.columns - 1) >= terrain.columns * terrain.voxel
    assert all(biome.relief is not None for biome in BIOMES.values())  # no voxel ground left
