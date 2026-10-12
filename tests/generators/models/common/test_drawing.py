from pewpy.generators.models.common.drawing import WEAPON_KINDS, layered_drawing, numbered_weapons
from pewpy.graphics.models.drawings.files import parse_voxels

COLORS = {"a": {"color": [1, 0, 0]}, "b": {"color": [0, 0, 1]}, "z": {"color": [0, 1, 0]}}


def test_a_drawing_is_layered_symmetric_round_its_middle_plane_and_the_game_reads_it() -> None:
    cells = {(0, 0, 0): "a", (1, 1, 2): "b"}
    drawing = layered_drawing(cells, 2, 2, COLORS)
    assert len(drawing["layers"]) == 5  # from -2 to 2
    assert drawing["layers"][2] == ["a.", ".."]
    assert drawing["layers"][4] == ["..", ".b"]
    assert set(drawing["palette"]) == {"a", "b"}  # only the colors it uses
    assert parse_voxels(drawing).cells[1, 1, 2] == (0.0, 0.0, 1.0, 1.0)


def test_weapons_are_numbered_by_kind_then_left_to_right() -> None:
    weapons = numbered_weapons([("missile", 0, 5), ("gun", 4, 1), ("gun", 1, 1)])
    assert [(weapon["number"], weapon["kind"], weapon["x"]) for weapon in weapons] == [
        (1, "gun", 1),
        (2, "gun", 4),
        (3, "missile", 0),
    ]
    assert WEAPON_KINDS.index("gun") < WEAPON_KINDS.index("missile")
