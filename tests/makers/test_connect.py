"""Keeping models in one piece."""

from pewpy.makers.common.connect import bridges, pieces


def test_cells_touching_through_their_faces_are_one_piece() -> None:
    found = pieces({(0, 0), (0, 1), (1, 1), (3, 3), (4, 4)})  # the last two touch only at a corner
    assert [len(piece) for piece in found] == [3, 1, 1]


def test_bridges_join_every_piece_by_the_shortest_way() -> None:
    cells = {(0, 0), (0, 1), (3, 0), (3, 1), (9, 9)}
    added = bridges(cells)
    assert len(pieces(cells | added)) == 1
    assert {(1, 0), (2, 0)} <= added or {(1, 1), (2, 1)} <= added  # the two posts, three apart
    assert bridges({(0, 0, 0), (0, 0, 1)}) == set()  # already one piece


def test_bridges_on_a_symmetric_model_are_mirrored() -> None:
    cells = {(-3, 0), (3, 0), (0, 4)}
    added = bridges(cells, mirror=lambda cell: (-cell[0], *cell[1:]))
    assert len(pieces(cells | added)) == 1
    assert added == {(-x, y) for x, y in added}


def test_models_join_in_3d() -> None:
    cells = {(0, 0, 0), (0, 0, 3)}  # a missile hanging under a wing, a gap between
    assert bridges(cells) == {(0, 0, 1), (0, 0, 2)}
