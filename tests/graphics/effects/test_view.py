from panda3d.core import NodePath, PerspectiveLens

from pewpy.graphics.effects import Particle
from pewpy.graphics.effects.laser import LaserGlow
from pewpy.graphics.effects.system import ParticleSystem
from pewpy.graphics.effects.view import ENEMY_LASER_COLOR, HALO_SPRITES, EffectsView

RED = (1.0, 0.2, 0.1, 1.0)


def lens() -> PerspectiveLens:
    result = PerspectiveLens()
    result.setFov(30, 40)
    return result


def test_glowing_particles_are_soft_circles_and_debris_stay_cubes() -> None:
    effects = ParticleSystem(seed=0)
    effects.particles += [
        Particle(0, 0, 0, 0, 0, 0, size=0.02, color=RED, life=1.0, glow=True),
        Particle(0, 0, 0, 0, 0, 0, size=0.02, color=RED, life=1.0, glow=True),
        Particle(0, 0, 0, 0, 0, 0, size=0.02, color=RED, life=1.0),
    ]
    view = EffectsView(effects, NodePath("render"), lens())
    view.sync()
    assert view.glows.node.getInstanceCount() == 2
    assert view.node.getInstanceCount() == 1


def test_the_laser_draws_its_streaks_a_halo_and_glows_at_the_nose_and_where_it_burns() -> None:
    effects = ParticleSystem(seed=0)
    effects.set_lasers([LaserGlow(x=0.0, bottom=-0.5, top=0.1, width=0.03, hits=(0.1,))], 1 / 60)
    view = EffectsView(effects, NodePath("render"), lens())
    view.sync()
    halo = round(0.6 / 0.03) + 1
    assert view.glows.node.getInstanceCount() == len(effects.light.photons) + halo + 2
    effects.set_lasers([], 1 / 60)
    effects.clear()
    view.sync()
    assert view.glows.node.isHidden()


def test_an_enemy_beam_glows_red_from_its_muzzle_and_a_long_beam_keeps_its_halo_short() -> None:
    effects = ParticleSystem(seed=0)
    beam = LaserGlow(x=0.3, bottom=-1.1, top=0.5, width=0.01, hostile=True, key=7)
    effects.set_lasers([beam], 1 / 60)
    view = EffectsView(effects, NodePath("render"), lens())
    sprites = view._laser_sprites()
    assert len(sprites) == len(effects.light.photons) + HALO_SPRITES + 1 + 1  # its halo is capped
    muzzle = sprites[-1]
    assert (muzzle.y, muzzle.color) == (0.5, ENEMY_LASER_COLOR)
