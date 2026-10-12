from pewpy.app import PewPewApp, keys
from pewpy.game.states import State
from pewpy.generators.backgrounds.themes import THEMES
from tests.app.driving import choose, menu, press


def test_the_backgrounds_show_a_candidate_of_each_theme(app: PewPewApp) -> None:
    choose(app, "Dev")
    choose(app, "Backgrounds")
    assert app.states.state is State.BACKGROUND_BROWSER
    assert app.menu_view.menu is None
    browser, view = app.background_browser, app.background_view
    assert browser is not None
    assert view is not None
    assert app.menu_level == browser.level()  # its ground scrolls by
    assert view.title.getText() == browser.title()
    assert view.status.getText() == f"theme: {browser.theme}"
    seed = browser.seed
    press(app, keys.FIRE_KEY)  # another one of the theme
    assert browser.index == 0
    assert browser.seed != seed
    assert view.details.getText() == browser.details()
    press(app, "arrow_left")  # the last theme
    assert browser.index == len(THEMES) - 1
    assert app.menu_level == browser.level()
    press(app, "arrow_up")  # nothing to change
    assert browser.index == len(THEMES) - 1
    press(app, keys.MENU_CHOOSE_KEY)  # nothing to save
    assert app.states.state is State.BACKGROUND_BROWSER
    press(app, keys.BACK_KEY)
    assert app.states.state is State.DEV_MENU
    assert app.background_view is None
    assert app.background_browser is None
    assert menu(app).items[menu(app).selected].label == "Backgrounds"
