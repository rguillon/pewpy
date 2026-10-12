from pewpy.graphics.models.built.cube import make_cube
from tests.graphics.models.meshes import triangles_of


def test_cube_faces_outward() -> None:
    cube = make_cube()
    triangles = triangles_of(cube)
    assert len(triangles) == 12
    for corners, normal in triangles:
        winding = (corners[1] - corners[0]).cross(corners[2] - corners[0])
        assert winding.dot(normal) > 0  # counter-clockwise seen from outside
        center = (corners[0] + corners[1] + corners[2]) / 3
        assert normal.dot(center) > 0  # and pointing away from the cube's center


def test_a_cube_fits_the_unit_box_and_can_be_named() -> None:
    cube = make_cube("bullet")
    assert cube.getName() == "bullet"
    points = [corner for corners, _ in triangles_of(cube) for corner in corners]
    assert {round(abs(value), 6) for point in points for value in point} == {0.5}
    assert cube.getGeom(0).getVertexData().hasColumn("texcoord")
