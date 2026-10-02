import numpy as np

from pewpy.scenery.ground import relief


def rng() -> np.random.Generator:
    return np.random.default_rng(0)


def test_noise_is_smooth_between_0_and_1_and_loops_along_the_rows() -> None:
    noise = relief.periodic_noise(rng(), 120, 50, cell=17.3)
    assert noise.shape == (120, 50)
    assert float(np.min(noise)) >= 0.0
    assert float(np.max(noise)) <= 1.0
    steps = float(np.max(np.abs(np.diff(noise, axis=0))))
    assert float(np.max(np.abs(noise[-1] - noise[0]))) <= steps * 1.01  # the last row runs on into the first


def test_a_peak_casts_its_shadow_away_from_the_sun_and_rises_above_a_hollow() -> None:
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
