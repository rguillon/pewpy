import pytest

from pewpy.app import PewPewApp
from pewpy.app.entity_models import drawing_of, fitted_model, shielded
from pewpy.game.enemies.enemy import Enemy
from pewpy.game.enemies.kinds import ENEMIES
from pewpy.game.entities import Entity
from pewpy.game.weapons.bullets import Missile
from pewpy.graphics import models
from tests.app.driving import play


def test_every_kind_of_ship_gets_its_model(app: PewPewApp) -> None:
    world = play(app)
    world.enemies = [Enemy.of_kind(kind, 0.0, 0.5) for kind in ENEMIES]
    app._sync_nodes()
    assert all(enemy in app.nodes for enemy in world.enemies)
    world.enemies = []
    app._sync_nodes()  # gone from the world: gone from the screen
    assert set(app.nodes) == {world.player}


def test_a_fitted_model_fits_the_unit_box() -> None:
    model = models.model("drone")
    bounds = model.getTightBounds()
    assert bounds is not None
    low, high = bounds
    size = max(high.x - low.x, high.z - low.z)
    fitted = fitted_model(model, size)
    bounds = fitted.getTightBounds()
    assert bounds is not None
    low, high = bounds
    assert max(high.x - low.x, high.z - low.z) == pytest.approx(1.0)
    assert model.getParent().isEmpty()  # a copy: the model itself stays where it was


def test_only_an_enemy_with_a_shield_state_is_shielded() -> None:
    assert shielded(Enemy.of_kind("shield_carrier"))
    assert not shielded(Enemy.of_kind("drone"))


def test_enemies_and_missiles_are_drawn_as_their_drawings() -> None:
    assert drawing_of(Enemy.of_kind("drone")) == Enemy.of_kind("drone").drawing
    assert drawing_of(Missile()) == "missile"
    assert drawing_of(Entity()) == ""
