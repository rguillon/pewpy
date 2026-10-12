from pewpy.graphics.models.built.turret import turret_model
from tests.graphics.models.meshes import all_points


def test_turret_has_a_barrel_to_aim_pointing_down_the_screen() -> None:
    turret = turret_model()
    barrel = turret.find("**/barrel")
    assert not barrel.isEmpty()
    assert max(point.z for point in all_points(barrel)) <= 0.0 + 1e-6  # from the dome's middle down
    assert len(all_points(turret)) > 3 * 12


def test_a_turret_is_fixed_to_the_ground_no_flames() -> None:
    assert turret_model().findAllMatches("**/flame").getNumPaths() == 0
