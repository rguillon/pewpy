import numpy as np
from panda3d.core import NodePath, SamplerState

from pewpy.scenery import params
from pewpy.scenery.ground import kinds
from pewpy.scenery.ground.shader.inputs import (
    FLUIDS,
    PALETTE_SIZE,
    STYLES,
    SURFACE_SLOTS,
    ground_inputs,
    maps,
    palette,
)
from pewpy.scenery.ground.terrain import Area, Terrain

AREA = Area(-1.0, 1.0, -1.2, 1.8)


def terrain(name: str) -> Terrain:
    return Terrain(AREA, 1.0, params.resolve(name), seed=0)


def test_a_scenery_without_ground_paints_nothing() -> None:
    assert set(palette(params.resolve("space"))) == {(0.0, 0.0, 0.0)}
    assert len(palette(params.resolve("space"))) == PALETTE_SIZE


def test_a_ground_has_its_colors() -> None:
    assert len(set(palette(params.resolve("forest")))) > 1


def test_a_built_up_ground_has_its_settlements_colors_by_surface() -> None:
    city = params.resolve("city")
    assert city.settlement is not None
    colors = palette(city)
    for name, color in city.settlement.colors.items():
        assert colors[SURFACE_SLOTS.index(name)] == color


def test_every_style_and_settlement_lists_its_colors() -> None:
    assert set(params.STYLE_COLORS) >= set(STYLES)
    assert set(params.SURFACE_COLORS) == set(kinds.SETTLEMENTS)
    for names in params.SURFACE_COLORS.values():
        assert set(names) <= set(SURFACE_SLOTS)
    assert all(len(names) <= PALETTE_SIZE for names in params.STYLE_COLORS.values())
    assert set(FLUIDS) == set(params.FLUID_COLORS)


def test_the_shadows_loop_down_the_ground_and_a_built_up_one_has_its_surface_map() -> None:
    natural = terrain("savanna")
    textures = maps(natural.relief, natural.layout)
    shadow = textures["shadow_map"]
    assert (shadow.getXSize(), shadow.getYSize()) == (natural.relief.columns, natural.relief.rows)
    assert shadow.getWrapV() == SamplerState.WM_repeat
    assert "surface_map" not in textures
    city = terrain("city")
    assert city.layout is not None
    surface = maps(city.relief, city.layout)["surface_map"]
    assert (surface.getYSize(), surface.getXSize()) == city.layout.surface.shape
    texels = np.frombuffer(bytes(surface.getRamImage()), dtype=np.uint8).reshape(*city.layout.surface.shape, 4)
    assert np.array_equal(texels[..., 2], city.layout.surface)  # red: the surface


def test_both_shaders_get_what_they_read() -> None:
    ground = terrain("salt_pan")
    root = NodePath("ground")
    ground_inputs(root, ground.scenery, maps(ground.relief, ground.layout), ground.loop_length, 2.0)
    names = ("sun", "sun_color", "sky_color", "haze_near", "haze_range", "ground_loop", "ground_width", "style")
    names += ("palette", "fluid", "fluid_colors", "window_lights", "glass_color", "furnace_color", "shadow_map")
    for name in (*names, "surface_map"):
        assert str(root.getShaderInput(name).getName()) == name
    assert root.getShaderInput("surface_map").getTexture().getName() == "shadow_heights"  # none of its own
