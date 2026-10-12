from pewpy.scenery.params.colors import FLUID_COLORS, STYLE_COLORS, SURFACE_COLORS
from pewpy.scenery.params.presets import backgrounds, resolve


def test_built_up_grounds_paint_with_their_settlements_colors() -> None:
    for style in SURFACE_COLORS:
        assert STYLE_COLORS[style] == ()
    assert all(SURFACE_COLORS.values())


def test_every_preset_gives_its_painters_the_colors_they_name() -> None:
    for name in backgrounds():
        scenery = resolve(name)
        if scenery.ground is not None:
            assert set(scenery.ground.colors) == set(STYLE_COLORS[scenery.ground.style])
        if scenery.fluid is not None:
            assert set(scenery.fluid.colors) == set(FLUID_COLORS[scenery.fluid.kind])
        if scenery.settlement is not None:
            assert set(scenery.settlement.colors) == set(SURFACE_COLORS[scenery.settlement.kind])


def test_no_painter_names_a_color_twice() -> None:
    for names in (*STYLE_COLORS.values(), *SURFACE_COLORS.values(), *FLUID_COLORS.values()):
        assert len(names) == len(set(names))
