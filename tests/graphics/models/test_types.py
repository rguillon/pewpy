from typing import get_args

from panda3d.core import Vec3

from pewpy.graphics.models.types import UV, Cell, Color, Palette, Vertex


def test_a_color_has_red_green_blue_and_alpha() -> None:
    assert get_args(Color) == (float, float, float, float)


def test_a_palette_gives_each_character_a_color_and_a_thickness() -> None:
    assert get_args(Palette) == (str, tuple[Color, int])


def test_a_vertex_is_a_point_its_color_and_its_texture_coordinates() -> None:
    assert get_args(Vertex) == (Vec3, Color, UV)
    assert get_args(Cell) == (int, int, int)
