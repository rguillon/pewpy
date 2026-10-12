from pewpy.graphics.models.built.lightning_coil import lightning_coil_model
from tests.graphics.models.meshes import all_points


def test_the_lightning_coil_is_an_unlit_orb() -> None:
    orb = lightning_coil_model()
    assert orb.getName() == "lightning_coil"
    assert orb.hasLightOff()
    points = all_points(orb)
    assert max(point.x for point in points) == -min(point.x for point in points)
