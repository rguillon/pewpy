from collections.abc import Callable

import pytest

from pewpy.audio.sfx.menu import menu_back, menu_choose, menu_move
from pewpy.audio.synth import FloatArray
from tests.audio.sfx.audible import assert_audible


@pytest.mark.parametrize(("make", "seconds"), [(menu_move, 0.045), (menu_choose, 0.18), (menu_back, 0.16)])
def test_every_menu_blip_is_audible(make: Callable[[], FloatArray], seconds: float) -> None:
    assert_audible(make(), seconds)
