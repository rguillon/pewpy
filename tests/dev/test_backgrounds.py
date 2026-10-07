import random

from pewpy.dev.backgrounds import SCROLL_SPEED, BackgroundBrowser
from pewpy.makers.backgrounds.candidate import candidate
from pewpy.makers.backgrounds.themes import THEMES


def test_the_browser_goes_round_the_themes_with_a_candidate_each() -> None:
    browser = BackgroundBrowser(random.Random(1))
    assert browser.theme == next(iter(THEMES))
    assert browser.made == candidate(browser.theme, browser.seed)
    browser.move(-1)
    assert browser.theme == list(THEMES)[-1]
    browser.move(1)
    assert browser.index == 0
    seed = browser.seed
    browser.generate()
    assert browser.seed != seed


def test_a_candidate_shows_as_a_level_without_waves() -> None:
    browser = BackgroundBrowser(random.Random(2))
    level = browser.level()
    assert level.waves == ()
    assert level.scroll_speed == SCROLL_SPEED
    assert level.name == browser.made["name"]
    assert (level.background, level.scenery, level.time_of_day, level.clouds, level.background_seed) == tuple(
        browser.made[key] for key in ("background", "scenery", "time_of_day", "clouds", "background_seed")
    )
    level.scenery_params()  # it reads
    assert browser.title() == f"{browser.made['name']}: {browser.theme}  (1/{len(THEMES)})"
    assert f"seed {browser.seed}" in browser.details()
