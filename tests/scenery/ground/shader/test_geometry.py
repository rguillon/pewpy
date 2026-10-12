import numpy as np
import pytest
from panda3d.core import GeomNode

from pewpy.scenery import params
from pewpy.scenery.ground import props
from pewpy.scenery.ground.settlement import Prop
from pewpy.scenery.ground.shader.geometry import mesh_node, props_model, relief_chunk_model
from pewpy.scenery.ground.shader.programs import shader
from pewpy.scenery.ground.terrain import Area, Terrain

AREA = Area(-1.0, 1.0, -1.2, 1.8)


def test_a_mesh_holds_its_vertices_and_triangles() -> None:
    vertices = np.zeros((3, 14), dtype=np.float32)
    vertices[:, :3] = [(0, 0, 0), (1, 0, 0), (0, 0, 1)]
    node = mesh_node("triangle", vertices, np.array([0, 1, 2]))
    mesh = node.node()
    assert isinstance(mesh, GeomNode)
    geom = mesh.getGeom(0)
    assert geom.getVertexData().getNumRows() == 3
    assert geom.getPrimitive(0).getNumVertices() == 3
    assert geom.getVertexData().getFormat().hasColumn("texcoord")


def test_a_relief_strip_has_its_rows_and_one_more_and_the_ground_shader() -> None:
    terrain = Terrain(AREA, 1.0, params.resolve("savanna"), seed=0)
    relief = terrain.relief
    strip = relief_chunk_model(relief, 0, terrain.relief_rows, 0.12)
    mesh = strip.node()
    assert isinstance(mesh, GeomNode)
    data = mesh.getGeom(0).getVertexData()
    assert data.getNumRows() == (terrain.relief_rows + 1) * relief.columns
    assert strip.getShader() == shader("ground")
    bounds = strip.getTightBounds()
    assert bounds is not None
    assert bounds[1].x == pytest.approx((relief.columns - 1) * relief.step_x)
    assert bounds[0].z == pytest.approx(-terrain.relief_rows * relief.step_y)


def test_the_props_are_drawn_two_sided_with_the_prop_shader() -> None:
    vertices, triangles = props.strip_arrays([Prop("barn", 0.5, 0.3, 0.08, 0.05, 0.04, 0)], 0.2)
    model = props_model(vertices, triangles)
    assert model.getShader() == shader("props")
    assert model.getTwoSided()
