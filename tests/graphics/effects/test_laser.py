import random

from pewpy.graphics.effects.laser import ENEMY_BURN_COLORS, PHOTON_FADE, LaserGlow, LaserLight

DT = 1 / 60
BEAM = LaserGlow(x=0.2, bottom=-0.5, top=0.5, width=0.03, hits=(0.5,))


class Clock:
    """A laser light with its random numbers and its time, run frame by frame."""

    def __init__(self) -> None:
        self.light = LaserLight()
        self.rng = random.Random(0)
        self.time = 0.0

    def frame(self, laser: LaserGlow | None) -> None:
        self.light.set([] if laser is None else [laser], DT, self.rng)
        self.time += DT
        self.light.update(DT, self.time)


def test_the_laser_sends_streaks_of_light_up_the_beam_that_stop_where_it_ends() -> None:
    clock = Clock()
    for _ in range(30):
        clock.frame(BEAM)
    photons = clock.light.photons
    assert len(photons) > 10
    assert all(BEAM.bottom <= photon.y < BEAM.top for photon in photons)
    assert all(abs(photon.x - BEAM.x) < BEAM.width for photon in photons)
    lower = LaserGlow(x=0.2, bottom=-0.5, top=-0.2, width=0.03)  # an enemy comes into the beam
    clock.frame(lower)
    assert all(photon.y < lower.top for photon in clock.light.photons)


def test_the_streaks_follow_the_ship_while_the_laser_is_on() -> None:
    clock = Clock()
    clock.frame(BEAM)
    moved = LaserGlow(x=-0.3, bottom=-0.4, top=0.5, width=0.03)
    clock.frame(moved)
    assert all(abs(photon.x - moved.x) < moved.width for photon in clock.light.photons)


def test_once_the_laser_is_cut_its_streaks_fly_on_and_fade_out() -> None:
    clock = Clock()
    for _ in range(10):
        clock.frame(BEAM)
    heights = {id(photon): photon.y for photon in clock.light.photons}
    clock.frame(None)
    assert clock.light.photons
    assert all(photon.y > heights[id(photon)] and photon.fade < 1 for photon in clock.light.photons)
    for _ in range(round(PHOTON_FADE / DT) + 1):
        clock.frame(None)
    assert clock.light.photons == []


def test_wider_beams_send_more_streaks() -> None:
    thin, wide = Clock(), Clock()
    for _ in range(60):
        thin.frame(BEAM)
        wide.frame(LaserGlow(x=0.2, bottom=-0.5, top=0.5, width=0.12))
    assert len(wide.light.photons) > len(thin.light.photons)


def test_an_enemy_beam_sends_red_streaks_down_from_its_muzzle() -> None:
    clock = Clock()
    beam = LaserGlow(x=0.1, bottom=-1.1, top=0.4, width=0.035, hostile=True, key=3)
    for _ in range(30):
        clock.frame(beam)
    photons = clock.light.photons
    assert photons
    assert all(beam.bottom < photon.y <= beam.top and photon.direction == -1 for photon in photons)
    assert {photon.color for photon in photons} <= set(ENEMY_BURN_COLORS)
    streak = photons[-1]
    height = streak.y
    clock.frame(beam)
    assert streak.y < height  # flowing down
    clock.frame(None)  # it stopped: its streaks fly on down and fade
    assert all(photon.fade < 1 for photon in clock.light.photons)


def test_several_beams_each_keep_their_own_streaks() -> None:
    clock = Clock()
    left = LaserGlow(x=-0.5, bottom=-1.1, top=0.4, width=0.03, hostile=True, key=1)
    right = LaserGlow(x=0.5, bottom=-1.1, top=0.4, width=0.03, hostile=True, key=2)
    for _ in range(10):
        clock.light.set([left, right, BEAM], DT, clock.rng)
        clock.light.update(DT, 0.0)
    keys = {photon.key for photon in clock.light.photons}
    assert keys == {0, 1, 2}
    assert all(abs(photon.x - {1: -0.5, 2: 0.5, 0: 0.2}[photon.key]) < 0.05 for photon in clock.light.photons)
