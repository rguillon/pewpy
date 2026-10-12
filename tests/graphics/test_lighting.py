from panda3d.core import AmbientLight, DirectionalLight, LightAttrib, NodePath

from pewpy.app import PewPewApp
from pewpy.graphics.lighting import FRAGMENT_SHADER, VERTEX_SHADER, light, setup


def test_a_scene_is_lit_by_an_ambient_light_and_a_sun() -> None:
    root = NodePath("scene")
    light(root)
    lights = root.getAttrib(LightAttrib)
    assert isinstance(lights, LightAttrib)
    kinds = sorted(type(lights.getOnLight(index).node()).__name__ for index in range(lights.getNumOnLights()))
    assert kinds == sorted([AmbientLight.__name__, DirectionalLight.__name__])


def test_a_scene_is_drawn_with_the_shiny_shader_and_its_settings() -> None:
    root = NodePath("scene")
    light(root)
    assert root.getShader() is not None
    names = ("shininess", "specular", "reflectivity", "bevel_width", "bevel_strength", "water_offset", "water_loop")
    for name in (*names, "haze", "tint"):
        assert str(root.getShaderInput(name).getName()) == name


def test_the_shader_is_glsl_reading_the_models_colors_normals_and_face_kinds() -> None:
    assert VERTEX_SHADER.lstrip().startswith("#version 150")
    assert all(name in VERTEX_SHADER for name in ("p3d_Normal", "p3d_Color", "p3d_MultiTexCoord0"))
    assert all(name in FRAGMENT_SHADER for name in ("bevel(", "waves(", "environment(", "haze"))


def test_the_game_lights_its_whole_scene(app: PewPewApp) -> None:
    assert app.render.getShader() is not None
    before = app.render.getAttrib(LightAttrib)
    assert isinstance(before, LightAttrib)
    setup(app)
    after = app.render.getAttrib(LightAttrib)
    assert isinstance(after, LightAttrib)
    assert after.getNumOnLights() == before.getNumOnLights() + 2
