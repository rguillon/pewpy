import numpy as np
import pytest

from pewpy.graphics.models.mesh.voxel_faces import (
    CONTEXT,
    EMPTY,
    FACE_DIRECTIONS,
    OCCLUSION_BRIGHTNESS,
    Occupancy,
    corner_levels,
    face_axes,
    face_corners,
    merged_faces,
    model_axes,
    occlusion_level,
)


@pytest.mark.parametrize(
    ("side_a", "side_b", "corner", "expected"),
    [
        (False, False, False, OCCLUSION_BRIGHTNESS[0]),
        (False, False, True, OCCLUSION_BRIGHTNESS[1]),
        (True, False, True, OCCLUSION_BRIGHTNESS[2]),
        (True, True, False, OCCLUSION_BRIGHTNESS[3]),  # both sides: fully tucked in
    ],
)
def test_occlusion_counts_the_voxels_in_front_of_a_corner(
    side_a: bool, side_b: bool, corner: bool, expected: float
) -> None:
    level = occlusion_level(np.array([side_a]), np.array([side_b]), np.array([corner]))
    assert OCCLUSION_BRIGHTNESS[level[0]] == expected


@pytest.mark.parametrize("direction", FACE_DIRECTIONS)
def test_a_faces_axes_wind_counter_clockwise_around_its_normal(direction: tuple[int, int, int]) -> None:
    normal, u, w = face_axes(direction)
    assert (np.cross(u, w) == normal).all()
    assert normal @ u == normal @ w == u @ w == 0


def test_cells_are_turned_into_the_models_axes() -> None:
    assert model_axes(np.array([(1, 2, 3)])).tolist() == [[1, 3, -2]]  # rows go down the screen, layers away
    assert model_axes(np.zeros((0, 3), np.int64)).shape == (0, 3)


def test_occupancy_tells_drawn_voxels_from_context_and_empty_space() -> None:
    occupancy = Occupancy(np.array([(0, 0, 0), (1, 0, 0)]), np.array([(0, 1, 0)]))
    assert occupancy.at(np.array([(1, 0, 0), (0, 1, 0), (0, 0, 1)])).tolist() == [
        1,
        CONTEXT,
        EMPTY,
    ]
    assert occupancy.filled(np.array([(0, 1, 0), (-1, 0, 0)])).tolist() == [True, False]


def test_a_face_next_to_a_neighbor_has_two_darkened_corners() -> None:
    occupancy = Occupancy(np.array([(0, 0, 0), (1, 0, 1)]), np.zeros((0, 3), np.int64))
    levels = corner_levels(np.array([(0, 0, 0)]), (0, 0, 1), occupancy)  # the top face, the cube up-right of it
    assert sorted(levels[0].tolist()) == [0, 0, 1, 1]


def test_a_faces_corners_are_half_a_cube_out_from_its_middle() -> None:
    corners = face_corners(np.array([(0, 0, 0)]), (1, 0, 0), 2.0, np.array([10.0, 0.0, 0.0]))
    assert corners.shape == (1, 4, 3)
    assert (corners[0, :, 0] == 11.0).all()
    assert {tuple(corner[1:]) for corner in corners[0]} == {(-1.0, -1.0), (-1.0, 1.0), (1.0, -1.0), (1.0, 1.0)}


def test_alike_faces_merge_into_rectangles_and_unlike_ones_dont() -> None:
    depth, u, w = np.zeros(4, np.int64), np.array([0, 1, 0, 1]), np.array([0, 0, 1, 1])
    flat = np.zeros((4, 4), np.int64)
    assert merged_faces(depth, u, w, np.zeros(4, np.int64), flat).tolist() == [[0, 0, 0, 2, 2, 0, 0, 0, 0, 0]]
    two_colors = merged_faces(depth, u, w, np.array([0, 0, 1, 1]), flat)
    assert [row[3:6] for row in two_colors.tolist()] == [[2, 1, 0], [2, 1, 1]]
