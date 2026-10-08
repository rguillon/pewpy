from array import array

import pytest
from panda3d.core import NodePath, PerspectiveLens

from pewpy.graphics.sprites import Sprite, SpriteBatch, pack

RED = (1.0, 0.2, 0.1, 1.0)


def lens() -> PerspectiveLens:
    result = PerspectiveLens()
    result.setFov(30, 40)
    return result


def test_sprites_are_packed_as_positions_then_colors_then_energies_in_texture_order() -> None:
    capacity = 2
    buffer = array("f", bytes(4 * 4 * 3 * capacity))  # what SpriteBatch keeps between frames
    pack(buffer, 4 * capacity, [Sprite(0.1, 0.2, 0.03, 0.05, RED, depth=0.3, energy=1.0, phase=2.0)], 1)
    data = buffer
    assert len(data) == 3 * 2 * 4  # three rows of two texels of four floats
    # Texels are blue, green, red, alpha in memory: the shader reads (x, depth, y, width), (r, g, b, height),
    # (energy, phase, 0, 0).
    assert list(data[:4]) == pytest.approx([0.2, 0.3, 0.1, 0.03])
    assert list(data[8:12]) == pytest.approx([0.1, 0.2, 1.0, 0.05])
    assert list(data[16:20]) == pytest.approx([0.0, 2.0, 1.0, 0.0])
    assert list(data[4:8]) == [0.0] * 4  # the unused slot, left at zero

    # A sprite shown again overwrites its column whole: nothing of the last frame's sprites is left behind.
    pack(buffer, 4 * capacity, [Sprite(0.5, 0.6, 0.07, 0.08, RED, depth=0.9, energy=0.5, phase=1.0)], 1)
    assert list(buffer[:4]) == pytest.approx([0.6, 0.9, 0.5, 0.07])
    assert list(buffer[8:12]) == pytest.approx([0.1, 0.2, 1.0, 0.08])
    assert list(buffer[16:20]) == pytest.approx([0.0, 1.0, 0.5, 0.0])


def test_a_batch_draws_one_square_per_sprite_and_hides_when_empty() -> None:
    batch = SpriteBatch(NodePath("render"), lens(), capacity=3, glow=False, core=0.4, hot=0.3)
    assert batch.node.isHidden()
    batch.show([Sprite(0, 0, 0.1, 0.1, RED)] * 5)
    assert batch.node.getInstanceCount() == 3  # no more than its capacity
    assert not batch.node.isHidden()
    batch.show([])
    assert batch.node.isHidden()
