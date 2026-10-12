import math

import numpy as np
import pytest

from pewpy.graphics.models.mesh.builder import MeshBuilder
from pewpy.graphics.models.mesh.slopes import CUTS, SLANT_NORMALS, clip, cuts, face_quarters, quarter_edges, slant
from pewpy.graphics.models.mesh.voxel_faces import Occupancy
from tests.graphics.models.meshes import WHITE, surface, volume


def test_a_cube_can_be_cut_across_each_of_its_12_edges() -> None:
    assert len(CUTS) == 12
    assert np.allclose(np.linalg.norm(SLANT_NORMALS, axis=1), 1.0)


def test_a_faces_quarters_go_round_it() -> None:
    edges = quarter_edges((0, 0, 1))
    assert len({tuple(edge) for edge in edges}) == 4
    assert (edges.sum(axis=0) == 0).all()


def test_only_a_stairs_outer_corner_is_cut() -> None:
    # Positions (x, depth, up): a step of two cubes on three. The top-left cube is an outer corner the stair goes on
    # past (down to the bottom-left one); the bottom-left one has nothing above to be a corner with.
    drawn = np.array([(0, 0, 0), (1, 0, 0), (2, 0, 0), (1, 0, 1), (2, 0, 1)])
    occupancy = Occupancy(drawn, np.zeros((0, 3), np.int64))
    cut = cuts(drawn, occupancy, np.ones(len(drawn), dtype=bool))
    assert cut.sum(axis=1).tolist() == [0, 0, 0, 1, 0]
    assert not cuts(drawn, occupancy, np.zeros(len(drawn), dtype=bool)).any()  # cubes that can't be cut aren't


def test_a_cut_takes_away_its_two_open_faces_and_half_of_each_end() -> None:
    cut = np.zeros((1, 12), dtype=bool)
    assert face_quarters(cut).all()
    cut[0, 0] = True  # across the edge between +x and +y (FACE_DIRECTIONS: +x, -x, +y, -y, +z, -z)
    left = face_quarters(cut)[0]
    assert left.sum(axis=1).tolist() == [0, 4, 0, 4, 2, 2]


def test_a_slanted_face_is_a_rectangle_unless_another_cut_trims_it() -> None:
    cut = np.zeros(12, dtype=bool)
    cut[0] = True  # across the edge between +x and +y: from the -x+y edge to the +x-y one
    assert slant(cut, 0).tolist() == [[-0.5, 0.5, -0.5], [-0.5, 0.5, 0.5], [0.5, -0.5, 0.5], [0.5, -0.5, -0.5]]
    cut[4] = True  # across the edge between +x and +z: a corner cut off twice, the slant is a triangle
    assert slant(cut, 0).tolist() == [[-0.5, 0.5, -0.5], [-0.5, 0.5, 0.5], [0.5, -0.5, -0.5]]


def test_clipping_keeps_the_half_on_the_inside() -> None:
    square = np.array([(-1, 0, -1), (1, 0, -1), (1, 0, 1), (-1, 0, 1)], dtype=float)
    half = clip(square, np.array([1, 0, 0]))
    assert half[:, 0].max() == pytest.approx(0.0)
    assert len(half) == 4


def test_staircases_become_45_degree_slopes() -> None:
    mesh = MeshBuilder()
    mesh.voxels(["..##", ".###", "####"], {"#": (WHITE, 1)}, 1.0)
    _, normals, _ = surface(mesh)
    slanted = normals[np.abs(normals).max(axis=1) < 0.9]
    assert len(slanted)
    assert np.allclose(slanted, [-math.sqrt(0.5), 0, math.sqrt(0.5)])  # up and left: the stair goes up to the right
    assert volume(mesh) == pytest.approx(9 - 2 * 0.5)  # the outer corner of each of the 2 steps is cut in half


def test_a_thicker_part_slopes_down_to_a_thinner_one() -> None:
    mesh = MeshBuilder()
    mesh.voxels(["xxxxx", "xcccx", "xcccx", "xxxxx"], {"x": (WHITE, 1), "c": (WHITE, 3)}, 1.0)
    _, normals, _ = surface(mesh)
    assert np.isclose(np.abs(normals[:, 1]), math.sqrt(0.5)).any()  # sloped towards the camera and away
