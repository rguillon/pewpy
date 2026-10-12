"""Looking into built meshes: their triangles, corners, surface and volume."""

import numpy as np
from panda3d.core import GeomNode, GeomVertexReader, NodePath, Vec3

from pewpy.graphics.models.mesh.builder import MeshBuilder

WHITE = (1.0, 1.0, 1.0, 1.0)
RED = [1.0, 0.0, 0.0]
BLUE = [0.0, 0.0, 1.0]


def triangles_of(node: GeomNode) -> list[tuple[list[Vec3], Vec3]]:
    """(corners, stored normal) for every triangle of a GeomNode."""
    result = []
    for geom_index in range(node.getNumGeoms()):
        geom = node.getGeom(geom_index)
        vertices = GeomVertexReader(geom.getVertexData(), "vertex")
        normals = GeomVertexReader(geom.getVertexData(), "normal")
        triangles = geom.getPrimitive(0).decompose()
        for index in range(triangles.getNumPrimitives()):
            start = triangles.getPrimitiveStart(index)
            corners = []
            for corner in range(3):
                vertices.setRow(triangles.getVertex(start + corner))
                corners.append(Vec3(vertices.getData3()))
            normals.setRow(triangles.getVertex(start))
            result.append((corners, Vec3(normals.getData3())))
    return result


def all_points(model: NodePath) -> list[Vec3]:
    """Every corner of the model's meshes, in their own space: engine flames left out (they stick out)."""
    points = []
    for path in [model, *model.findAllMatches("**/+GeomNode")]:
        if not isinstance(path.node(), GeomNode) or "flame" in str(path).split("/"):
            continue
        node = path.node()
        assert isinstance(node, GeomNode)
        for corners, _ in triangles_of(node):
            points += corners
    return points


def assert_closed_and_facing_out(node: GeomNode) -> None:
    """Slopes leave no hole: the faces add up to nothing (closed), every triangle wound the way its normal says."""
    triangles = triangles_of(node)
    areas = [(b - a).cross(c - a) for (a, b, c), _ in triangles]
    assert sum(areas, Vec3()).length() < 1e-5 * sum(area.length() for area in areas)  # corners are stored as float32
    for (a, b, c), normal in triangles:
        assert (b - a).cross(c - a).dot(normal) > 0


def surface(mesh: MeshBuilder) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Every triangle's corners (n, 3, 3), stored normal (n, 3) and area times its winding's direction (n, 3)."""
    corners, normals, _, _ = mesh._arrays()
    return corners, normals, np.cross(corners[:, 1] - corners[:, 0], corners[:, 2] - corners[:, 0]) / 2


def volume(mesh: MeshBuilder) -> float:
    """Return the volume a closed mesh holds (divergence theorem)."""
    corners, _, areas = surface(mesh)
    return float(np.einsum("ij,ij->", corners.mean(axis=1), areas) / 3)
