import pytest

from pewpy import config
from pewpy.game import bosses
from pewpy.game.boss_catalog import BOSSES
from pewpy.game.enemies import HALF_WIDTH
from pewpy.game.level import load_levels
from pewpy.graphics import models


@pytest.mark.parametrize("kind", BOSSES)
def test_every_boss_fits_the_screen_and_its_parts_and_guns_exist(kind):
    spec = BOSSES[kind]
    assert spec.half_span < HALF_WIDTH
    names = {part.name for part in spec.parts}
    for phase in spec.phases:
        assert {source for source, _ in phase.guns} <= names | {bosses.CORE}
        assert set(phase.until_destroyed) <= names
    for drawing in {spec.drawing} | {part.drawing for part in spec.parts}:
        models.load_drawing(drawing)


@pytest.mark.parametrize("kind", BOSSES)
def test_every_part_can_be_shot_from_below(kind):
    """Shots fly up: some of each part's width must not be behind a piece that reaches lower (core included)."""
    spec = BOSSES[kind]
    pieces = [(0.0, -spec.height / 2, spec.width)] + [(p.x, p.y - p.height / 2, p.width) for p in spec.parts]
    for part in spec.parts:
        bottom, left, right = part.y - part.height / 2, part.x - part.width / 2, part.x + part.width / 2
        shots = [left + (right - left) * step / 100 for step in range(101)]
        open_shots = [
            x
            for x in shots
            if not any(low < bottom and abs(x - middle) < (width + 0.02) / 2 for middle, low, width in pieces)
        ]
        assert len(open_shots) * (right - left) / 100 >= 0.04, part.name


@pytest.mark.parametrize("kind", BOSSES)
def test_every_hitbox_has_the_size_of_its_drawing(kind):
    """Models are built with cubes of config.MODEL_VOXEL: each drawing must be about as big as its hitbox."""
    spec = BOSSES[kind]
    for drawing, width, height in [(spec.drawing, spec.width, spec.height)] + [
        (part.drawing, part.width, part.height) for part in spec.parts
    ]:
        rows, _ = models.load_drawing(drawing)
        assert len(rows[0]) * config.MODEL_VOXEL == pytest.approx(width, rel=0.12), drawing
        assert len(rows) * config.MODEL_VOXEL == pytest.approx(height, rel=0.12), drawing


def test_every_level_ends_with_its_own_boss():
    levels = load_levels()
    last_waves = [max(level.waves, key=lambda wave: wave.time) for level in levels]
    assert all(wave.enemy in BOSSES for wave in last_waves)
    assert sorted(wave.enemy for wave in last_waves) == sorted(BOSSES)  # each boss once
    for level in levels:
        assert sum(wave.enemy in BOSSES for wave in level.waves) == 1


@pytest.mark.parametrize("kind", BOSSES)
def test_every_phase_but_the_last_can_end(kind):
    phases = BOSSES[kind].phases
    assert all(phase.until_destroyed or phase.until_below > 0 for phase in phases[:-1])
    assert len(phases) >= 2  # several shooting patterns
