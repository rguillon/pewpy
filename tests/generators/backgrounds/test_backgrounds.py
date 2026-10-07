import pytest

from pewpy.generators.backgrounds.candidate import candidate
from pewpy.generators.backgrounds.themes import THEMES
from pewpy.scenery import params


@pytest.mark.parametrize("theme", list(THEMES))
def test_every_theme_makes_backgrounds_the_game_reads(theme: str) -> None:
    for seed in range(5):
        made = candidate(theme, seed)
        assert made["note"] == f"theme: {theme}"
        assert made["background"] == THEMES[theme].preset
        assert made["time_of_day"] in THEMES[theme].times
        low, high = THEMES[theme].clouds
        assert low <= made["clouds"] <= high
        params.resolve(made["background"], made["scenery"])


def test_a_candidate_is_made_again_from_its_theme_and_seed() -> None:
    assert candidate("kalahari", 7) == candidate("kalahari", 7)
    assert candidate("kalahari", 7) != candidate("kalahari", 8)
