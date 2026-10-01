import random

from pewpy.graphics.effects.laser import PHOTON_FADE, LaserGlow, LaserLight

DT = 1 / 60
BEAM = LaserGlow(x=0.2, bottom=-0.5, top=0.5, width=0.03, hits=(0.5,))


class Clock:
    """A laser light with its random numbers and its time, run frame by frame."""

    def __init__(self) -> None:
        self.light = LaserLight()
        self.rng = random.Random(0)  # noqa: S311
        self.time = 0.0

    def frame(self, laser: LaserGlow | None) -> None:
        self.light.set(laser, DT, self.rng)
        self.time += DT
        self.light.update(DT, self.time)


def test_the_laser_sends_streaks_of_light_up_the_beam_that_stop_where_it_ends():
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


def test_the_streaks_follow_the_ship_while_the_laser_is_on():
    clock = Clock()
    clock.frame(BEAM)
    moved = LaserGlow(x=-0.3, bottom=-0.4, top=0.5, width=0.03)
    clock.frame(moved)
    assert all(abs(photon.x - moved.x) < moved.width for photon in clock.light.photons)


def test_once_the_laser_is_cut_its_streaks_fly_on_and_fade_out():
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


def test_wider_beams_send_more_streaks():
    thin, wide = Clock(), Clock()
    for _ in range(60):
        thin.frame(BEAM)
        wide.frame(LaserGlow(x=0.2, bottom=-0.5, top=0.5, width=0.12))
    assert len(wide.light.photons) > len(thin.light.photons)
