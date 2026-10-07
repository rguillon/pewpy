import pytest

from pewpy.game.enemies.exits import Parts
from pewpy.game.enemies.kinds import BOSSES, FINAL_BOSSES, MINI_BOSSES
from pewpy.game.enemies.screen import HALF_WIDTH
from pewpy.game.enemies.spec import EnemySpec, State
from pewpy.game.level import load_levels
from pewpy.graphics import models
from pewpy.graphics.models.drawings.files import read_drawing


def voxels_of(drawing: str) -> models.Voxels:
    """Read a drawing's cubes from its file."""
    return models.parse_voxels(*read_drawing(drawing))


@pytest.mark.parametrize("kind", BOSSES)
def test_every_boss_fits_the_screen_and_its_parts_and_guns_exist(kind: str) -> None:
    spec = BOSSES[kind]
    assert spec.half_span < HALF_WIDTH
    assert spec.boss
    names = {part.name for part in spec.parts}
    for state in spec.states:
        assert {source for source, _ in state.guns} <= names | {""}
        conditions = [condition for way_out in state.exits for condition in way_out.conditions]
        assert all(set(condition.names) <= names for condition in conditions if isinstance(condition, Parts))
    for drawing in {spec.drawing} | {part.spec.drawing for part in spec.parts}:
        assert voxels_of(drawing).cells


@pytest.mark.parametrize("kind", BOSSES)
def test_every_hitbox_has_the_size_of_its_drawing(kind: str) -> None:
    """Models are built with cubes of config.MODEL_VOXEL (or finer): each drawing is about as big as its hitbox."""
    spec = BOSSES[kind]
    for drawing, width, height in [(spec.drawing, spec.width, spec.height)] + [
        (part.spec.drawing, part.spec.width, part.spec.height) for part in spec.parts
    ]:
        voxels = voxels_of(drawing)
        assert voxels.width * voxels.size == pytest.approx(width, rel=0.12), drawing
        assert voxels.height * voxels.size == pytest.approx(height, rel=0.12), drawing


def test_every_level_has_its_own_mini_boss_halfway_and_final_boss_at_the_end() -> None:
    levels = load_levels()
    bosses_by_level = [[wave for wave in level.waves if wave.enemy in BOSSES] for level in levels]
    assert all(len(waves) == 2 for waves in bosses_by_level)
    assert sorted(waves[0].enemy for waves in bosses_by_level) == sorted(MINI_BOSSES)  # each boss once
    assert sorted(waves[1].enemy for waves in bosses_by_level) == sorted(FINAL_BOSSES)
    for level, (mini, final) in zip(levels, bosses_by_level, strict=True):
        assert final == max(level.waves, key=lambda wave: wave.time)
        assert sum(wave.time < mini.time for wave in level.waves) > 5  # halfway: waves before and after it
        assert sum(mini.time < wave.time < final.time for wave in level.waves) > 5


def test_a_final_boss_is_wider_and_tougher_than_its_levels_mini_boss() -> None:
    for level in load_levels():
        mini, final = (BOSSES[wave.enemy] for wave in level.waves if wave.enemy in BOSSES)

        def toughness(spec: EnemySpec) -> float:
            return spec.health + sum(part.spec.health for part in spec.parts)

        assert final.width > mini.width
        assert toughness(final) > toughness(mini)
        assert len(phases(final)) >= len(phases(mini))


def phases(spec: EnemySpec) -> list[State]:
    return [state for state in spec.states if state.guns]


@pytest.mark.parametrize("kind", BOSSES)
def test_every_phase_but_the_last_can_end(kind: str) -> None:
    fighting = phases(BOSSES[kind])
    assert all(phase.exits for phase in fighting[:-1])
    assert len(fighting) >= 2  # several shooting patterns
