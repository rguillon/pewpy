from pewpy.scenery import ground_shader, params


def test_a_scenery_without_ground_paints_nothing():
    assert set(ground_shader.palette(params.resolve("space"))) == {(0.0, 0.0, 0.0)}


def test_a_ground_has_its_colors():
    assert len(set(ground_shader.palette(params.resolve("forest")))) > 1
