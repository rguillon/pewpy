from panda3d.core import NodePath

from pewpy.ui.screenshot_view import BACKGROUND_KEYS, KEYS, ScreenshotView


def test_the_screenshots_texts_say_which_world_which_shot_and_whats_going_on() -> None:
    view = ScreenshotView(NodePath("aspect2d"))
    assert view.keys.getText() == KEYS
    view.describe("WORLD 2", "level 2-3", "saved")
    assert (view.title.getText(), view.details.getText(), view.status.getText()) == ("WORLD 2", "level 2-3", "saved")


def test_the_backgrounds_browser_shows_its_own_keys() -> None:
    assert ScreenshotView(NodePath("aspect2d"), BACKGROUND_KEYS).keys.getText() == BACKGROUND_KEYS
