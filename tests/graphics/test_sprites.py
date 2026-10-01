from array import array

import pytest
from panda3d.core import NodePath, PerspectiveLens

from pewpy.graphics.effects import Effects, LaserGlow, Particle
from pewpy.graphics.effects_view import EffectsView
from pewpy.graphics.sprites import Sprite, SpriteBatch, pack

RED = (1.0, 0.2, 0.1, 1.0)


def lens() -> PerspectiveLens:
    result = PerspectiveLens()
    result.setFov(30, 40)
    return result


def test_sprites_are_packed_as_positions_then_colors_in_texture_order():
    data = array("f")
    data.frombytes(pack([Sprite(0.1, 0.2, 0.03, 0.05, RED, depth=0.3)], capacity=2))
    assert len(data) == 2 * 2 * 4  # two rows of two texels of four floats
    # Texels are blue, green, red, alpha in memory: the shader reads (x, depth, y, width), (r, g, b, height).
    assert list(data[:4]) == pytest.approx([0.2, 0.3, 0.1, 0.03])
    assert list(data[8:12]) == pytest.approx([0.1, 0.2, 1.0, 0.05])
    assert list(data[4:8]) == [0.0] * 4  # the unused slot


def test_a_batch_draws_one_square_per_sprite_and_hides_when_empty():
    batch = SpriteBatch(NodePath("render"), lens(), capacity=3, glow=False, core=0.4, hot=0.3)
    assert batch.node.isHidden()
    batch.show([Sprite(0, 0, 0.1, 0.1, RED)] * 5)
    assert batch.node.getInstanceCount() == 3  # no more than its capacity
    assert not batch.node.isHidden()
    batch.show([])
    assert batch.node.isHidden()


def test_glowing_particles_are_soft_circles_and_debris_stay_cubes():
    effects = Effects(seed=0)
    effects.particles += [
        Particle(0, 0, 0, 0, 0, 0, size=0.02, color=RED, life=1.0, glow=True),
        Particle(0, 0, 0, 0, 0, 0, size=0.02, color=RED, life=1.0, glow=True),
        Particle(0, 0, 0, 0, 0, 0, size=0.02, color=RED, life=1.0),
    ]
    view = EffectsView(effects, NodePath("render"), lens())
    view.sync()
    assert view.glows.node.getInstanceCount() == 2
    assert view.node.getInstanceCount() == 1


def test_the_laser_draws_its_streaks_a_halo_and_glows_at_the_nose_and_where_it_burns():
    effects = Effects(seed=0)
    effects.set_laser(LaserGlow(x=0.0, bottom=-0.5, top=0.1, width=0.03, hits=(0.1,)), 1 / 60)
    view = EffectsView(effects, NodePath("render"), lens())
    view.sync()
    halo = round(0.6 / 0.03) + 1
    assert view.glows.node.getInstanceCount() == len(effects.photons) + halo + 2
    effects.set_laser(None, 1 / 60)
    effects.clear()
    view.sync()
    assert view.glows.node.isHidden()
