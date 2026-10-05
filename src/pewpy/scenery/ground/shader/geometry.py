"""The meshes the shaders paint: the relief's strips and the props."""

import numpy as np
from panda3d.core import (
    Geom,
    GeomEnums,
    GeomNode,
    GeomTriangles,
    GeomVertexArrayFormat,
    GeomVertexData,
    GeomVertexFormat,
    NodePath,
)

from pewpy.scenery.ground.relief import Relief
from pewpy.scenery.ground.shader.programs import shader


def _vertex_format() -> GeomVertexFormat:
    array = GeomVertexArrayFormat()
    array.addColumn("vertex", 3, GeomEnums.NT_float32, GeomEnums.C_point)
    array.addColumn("normal", 3, GeomEnums.NT_float32, GeomEnums.C_normal)
    array.addColumn("color", 4, GeomEnums.NT_float32, GeomEnums.C_color)
    array.addColumn("texcoord", 4, GeomEnums.NT_float32, GeomEnums.C_texcoord)
    return GeomVertexFormat.registerFormat(GeomVertexFormat(array))


def mesh_node(name: str, vertices: np.ndarray, triangles: np.ndarray) -> NodePath:
    """Make a mesh from vertices of 14 floats (position, normal, color, texture data) and triangle corner indices."""
    data = GeomVertexData(name, _vertex_format(), Geom.UH_static)
    data.uncleanSetNumRows(len(vertices))
    data.modifyArrayHandle(0).copyDataFrom(
        memoryview(np.ascontiguousarray(vertices, dtype=np.float32).reshape(-1)).cast("B")
    )
    primitive = GeomTriangles(Geom.UH_static)
    primitive.setIndexType(GeomEnums.NT_uint32)
    handle = primitive.modifyVertices()
    handle.uncleanSetNumRows(len(triangles))
    handle.modifyHandle().copyDataFrom(memoryview(np.ascontiguousarray(triangles, dtype=np.uint32)).cast("B"))
    geom = Geom(data)
    geom.addPrimitive(primitive)
    node = GeomNode(name)
    node.addGeom(geom)
    return NodePath(node)


def relief_chunk_model(relief: Relief, first_row: int, rows: int, max_height: float) -> NodePath:
    """Make rows `first_row` to `first_row + rows` of a relief into a mesh.

    One more row, from the next strip, closes the gap. The node's origin is the top-left corner, on the base layer: x
    right, z up the screen, heights towards the camera (-y).
    """
    picked = np.arange(first_row, first_row + rows + 1) % relief.rows
    heights = relief.heights[picked]
    normals = relief.normals[picked]
    lines, columns = heights.shape
    vertices = np.zeros((lines, columns, 14), dtype=np.float32)
    vertices[..., 0] = (np.arange(columns) * relief.step_x)[None, :]
    vertices[..., 1] = -heights
    vertices[..., 2] = (-np.arange(lines) * relief.step_y)[:, None]
    # Relief normals: x right, y down the rows, z towards the camera -> model: x, -z (towards the camera is -y), -y.
    vertices[..., 3] = normals[..., 0]
    vertices[..., 4] = -normals[..., 2]
    vertices[..., 5] = -normals[..., 1]
    vertices[..., 6] = relief.cavity[picked]
    vertices[..., 7] = heights / max_height
    vertices[..., 8] = relief.depth[picked]
    vertices[..., 9] = relief.marks[picked]
    index = np.arange(lines * columns, dtype=np.uint32).reshape(lines, columns)
    a, b = index[:-1, :-1], index[:-1, 1:]
    c, d = index[1:, :-1], index[1:, 1:]
    triangles = np.stack([a, c, b, b, c, d], axis=-1).reshape(-1)  # two per square, facing the camera
    path = mesh_node("relief", vertices.reshape(-1, 14), triangles)
    path.setShader(shader("ground"), 20)
    return path


def props_model(vertices: np.ndarray, triangles: np.ndarray) -> NodePath:
    """Make a strip's props into a mesh (see props.strip_arrays)."""
    path = mesh_node("props", vertices, triangles)
    path.setShader(shader("props"), 20)
    path.setTwoSided(True)
    return path
