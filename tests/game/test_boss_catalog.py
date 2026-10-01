import pytest

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
        assert models.load_voxels(drawing).cells


@pytest.mark.parametrize("kind", BOSSES)
def test_every_hitbox_has_the_size_of_its_drawing(kind):
    """Models are built with cubes of config.MODEL_VOXEL (or finer): each drawing is about as big as its hitbox."""
    spec = BOSSES[kind]
    for drawing, width, height in [(spec.drawing, spec.width, spec.height)] + [
        (part.drawing, part.width, part.height) for part in spec.parts
    ]:
        voxels = models.load_voxels(drawing)
        assert voxels.width * voxels.size == pytest.approx(width, rel=0.12), drawing
        assert voxels.height * voxels.size == pytest.approx(height, rel=0.12), drawing


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
