from dataclasses import replace

import pytest

from pewpy.game.enemies.mounts import Mount
from pewpy.game.entities import Entity
from pewpy.game.weapons.bullets import BossBeam
from pewpy.game.weapons.guns.gun import Gun
from pewpy.game.weapons.guns.laser import LASER_WARNING, WARNING_WIDTH, laser_beams
from pewpy.game.weapons.guns.shooter import Shooter

MOUNTS = {
    1: Mount(1, "gun", -0.1, -0.05),
    2: Mount(2, "cannon", -0.06, -0.04, depth=-0.08),
    3: Mount(3, "cannon", 0.06, -0.04, depth=-0.08),
    4: Mount(4, "missile", 0.0, -0.02),
}
LASER = Gun("laser", 5.0, speed=0.0, offsets=(-0.1, 0.1))
PIECE = Entity(x=0.2, y=0.5, width=0.4, height=0.2)


def test_a_laser_fires_from_the_cannons_nearest_its_offsets() -> None:
    beams = laser_beams(LASER, Shooter(PIECE, None, mounts=MOUNTS), warning=False)
    assert [(beam.x - PIECE.x, beam.y + beam.height / 2 - PIECE.y, beam.depth) for beam in beams] == [
        pytest.approx((-0.06, -0.04, -0.08)),
        pytest.approx((0.06, -0.04, -0.08)),
    ]
    one_cannon = {number: MOUNTS[number] for number in (1, 3, 4)}  # each weapon fires one beam
    assert len(laser_beams(LASER, Shooter(PIECE, None, mounts=one_cannon), warning=True)) == 1
    no_cannon = {number: MOUNTS[number] for number in (1, 4)}  # no laser or cannon: any weapon, the nearest
    anywhere = laser_beams(LASER, Shooter(PIECE, None, mounts=no_cannon), warning=False)
    assert [beam.x - PIECE.x for beam in anywhere] == [pytest.approx(-0.1), pytest.approx(0.0)]
    named = laser_beams(replace(LASER, weapons=(4,)), Shooter(PIECE, None, mounts=MOUNTS), warning=False)
    assert [beam.x - PIECE.x for beam in named] == [pytest.approx(0.0)]
    under = laser_beams(LASER, Shooter(PIECE, None), warning=False)  # no weapons: under its middle
    assert [(beam.x - PIECE.x, beam.y + beam.height / 2, beam.depth) for beam in under] == [
        pytest.approx((-0.1, 0.4, 0.0)),
        pytest.approx((0.1, 0.4, 0.0)),
    ]


def test_a_lasers_warning_is_thin_harmless_and_lasts_until_the_beam() -> None:
    warning, beam = (laser_beams(LASER, Shooter(PIECE, None), warning=each)[0] for each in (True, False))
    assert (warning.harmless, warning.width, warning.life) == (True, WARNING_WIDTH, pytest.approx(LASER_WARNING))
    assert (beam.harmless, beam.width, beam.life) == (False, LASER.width, LASER.duration)
    assert isinstance(beam, BossBeam)
    assert beam.source is PIECE
