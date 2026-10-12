from pewpy.scenery.params.presets import backgrounds, resolve
from pewpy.scenery.params.props import PropColors


def test_every_scenery_lights_its_props_windows_and_furnaces() -> None:
    for name in backgrounds():
        props = resolve(name).props
        assert isinstance(props, PropColors)
        assert len(props.window_lights) == 2
        assert all(0 <= value <= 1 for color in (*props.window_lights, props.glass, props.furnace) for value in color)
