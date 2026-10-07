"""The Dev menu's model browser, without a window."""

import json
import random
from pathlib import Path

import pytest

from pewpy.generators.models.browser import SIZE_STEP, ModelBrowser, model_size, read_model
from pewpy.generators.models.catalog import read_data
from pewpy.generators.models.sized import parts_for


def test_it_starts_on_the_first_model_at_its_size(data_copy: Path) -> None:  # noqa: ARG001 - its data
    browser = ModelBrowser("players", random.Random(1))
    assert browser.entry.key == "vanguard"
    assert browser.size == pytest.approx(tuple(read_model("player")["size"]))
    assert browser.new is None
    assert [piece.name for piece in browser.pieces()] == ["player"]


def test_left_and_right_go_round_the_models(data_copy: Path) -> None:  # noqa: ARG001 - its data
    browser = ModelBrowser("players", random.Random(1))
    browser.move(-1)
    assert browser.entry.key == browser.models[-1].key  # the last ship
    browser.move(1)
    assert browser.entry.key == "vanguard"


def test_the_width_and_the_height_change_on_their_own_for_another_shape(data_copy: Path) -> None:  # noqa: ARG001
    browser = ModelBrowser("enemies", random.Random(1))
    width, height = browser.size
    browser.stretch(1, 0)
    assert browser.size == pytest.approx((width * SIZE_STEP, height))
    browser.stretch(0, -2)
    assert browser.size == pytest.approx((width * SIZE_STEP, height / SIZE_STEP**2))


def test_a_new_ship_shows_until_it_is_saved_or_dropped(data_copy: Path) -> None:
    browser = ModelBrowser("enemies", random.Random(1))
    before = read_model("drone")
    browser.generate()
    assert browser.new is not None
    assert browser.pieces()[0].data is browser.new
    browser.move(1)
    browser.move(-1)
    assert browser.new is None  # dropped
    browser.stretch(1, 1)
    browser.generate()
    new = browser.new
    browser.save()
    assert browser.saved
    assert browser.new is None
    assert json.loads((data_copy / "models/enemies/drone.json").read_text()) == new != before


def test_enter_without_a_new_model_saves_the_size(data_copy: Path) -> None:  # noqa: ARG001 - its data
    browser = ModelBrowser("players", random.Random(1))
    hitbox = read_data("ships.json")["vanguard"]["size"]
    browser.stretch(1, 1)
    size = browser.size
    browser.save()
    assert model_size(read_model("player")) == pytest.approx(size, abs=1e-4)
    assert read_data("ships.json")["vanguard"]["size"] == pytest.approx(hitbox * SIZE_STEP, abs=1e-3)
    assert browser.saved
    browser.stretch(0, 1)
    assert not browser.saved


def test_a_new_boss_shows_with_its_parts_and_saves_them(data_copy: Path) -> None:  # noqa: ARG001 - its data
    browser = ModelBrowser("bosses", random.Random(3))
    browser.index = next(index for index, entry in enumerate(browser.models) if entry.key == "rockbreaker")
    browser.move(0)
    assert len(browser.pieces()) == 1 + len(browser.entry.parts)  # the core and its parts
    browser.generate()
    core, *parts = browser.pieces()
    assert core.data is browser.new["core"]  # ty: ignore[not-subscriptable] - made
    assert len(parts) == parts_for(browser.size)
    browser.save()
    assert [round(part.x, 3) for part in parts] == [part.x for part in browser.entry.parts]


def test_enter_on_a_boss_without_a_new_one_saves_its_size(data_copy: Path) -> None:  # noqa: ARG001 - its data
    browser = ModelBrowser("bosses", random.Random(1))
    browser.stretch(-1, 0)
    size = browser.size
    browser.save()
    assert model_size(read_model(browser.entry.drawing)) == pytest.approx(size, abs=1e-4)
