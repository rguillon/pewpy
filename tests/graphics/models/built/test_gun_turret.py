from panda3d.core import GeomNode

from pewpy.graphics.models.built.gun_turret import gun_turret_model
from tests.graphics.models.meshes import all_points, triangles_of


def test_the_gun_turret_is_a_dome_with_a_barrel_pointing_down_the_screen() -> None:
    turret = gun_turret_model()
    assert turret.getName() == "gun_turret"
    dome = turret.node()
    assert isinstance(dome, GeomNode)
    lowest_of_dome = min(corner.z for corners, _ in triangles_of(dome) for corner in corners)
    barrel = turret.find("barrel")
    assert min(point.z for point in all_points(barrel)) < lowest_of_dome
