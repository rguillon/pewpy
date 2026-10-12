import pytest

from pewpy.game.entities import Entity
from pewpy.game.weapons.bullets.beam import BEAM_BOTTOM
from pewpy.game.weapons.bullets.boss_beam import BossBeam


def test_a_boss_beam_follows_its_source_from_under_it() -> None:
    boss = Entity(x=0.0, y=0.5, height=0.2)
    beam = BossBeam(source=boss, offset_x=0.1, life=1.0)
    boss.x, boss.y = 0.2, 0.6
    beam.move(0.1)
    assert beam.x == pytest.approx(0.3)
    assert beam.y + beam.height / 2 == pytest.approx(0.5)
    assert beam.y - beam.height / 2 == pytest.approx(BEAM_BOTTOM)
    assert beam.alive


def test_a_boss_beam_can_start_higher_on_its_source() -> None:
    beam = BossBeam(source=Entity(x=0.0, y=0.5, height=0.2), offset_y=0.05)
    beam.move(0.0)
    assert beam.y + beam.height / 2 == pytest.approx(0.55)


def test_a_boss_beam_goes_with_its_source_or_its_time() -> None:
    boss = Entity()
    beam = BossBeam(source=boss, life=1.0)
    boss.alive = False
    beam.move(0.1)
    assert not beam.alive
    timed = BossBeam(life=0.1)
    timed.move(0.1)
    assert not timed.alive


def test_a_boss_beam_stays_at_its_depth() -> None:
    beam = BossBeam(depth=-0.1)
    beam.move(0.5)
    assert beam.depth == -0.1
