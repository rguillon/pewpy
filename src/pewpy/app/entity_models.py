"""The models of everything in play, built once (an enemy's when first needed), copied for each entity."""

from panda3d.core import NodePath

from pewpy.app.window import Color, Window
from pewpy.game.enemies.enemy import Enemy
from pewpy.game.enemies.kinds import drawings
from pewpy.game.entities import Entity, Pickup
from pewpy.game.level import Level
from pewpy.game.player import DEFAULT_SHIP, SHIPS, Player
from pewpy.game.weapons.bullets import Missile
from pewpy.game.weapons.player.arsenal import LETTERS, WEAPONS
from pewpy.game.weapons.player.secondary import SECONDARY_LETTERS, SECONDARY_WEAPONS
from pewpy.graphics import models

WEAPON_COLORS: dict[str, Color] = {
    "bullets": (1.0, 0.9, 0.2, 1),
    "laser": (0.3, 0.9, 1.0, 1),
    "missiles": (1.0, 0.6, 0.15, 1),
}
SECONDARY_COLORS: dict[str, Color] = {
    "turret": (0.45, 1.0, 0.4, 1),
    "lightning": (0.8, 0.55, 1.0, 1),
}


class EntityModels(Window):
    """The models of the ships, enemies, bosses, pickups and secondary weapons."""

    def _build_models(self) -> None:
        """Build the models from pewpy.graphics.models (looked up by name, so reloaded models are used).

        The enemies' (and their parts') are built when first needed (see _ship_model): there are many, the bosses big.
        """
        # The enemies', their parts' and the player's missiles, by drawing (see EnemySpec.drawing, Missile.drawing).
        self.ship_models: dict[str, NodePath] = {}
        self.player_models = {spec.drawing: models.model(spec.drawing) for spec in SHIPS.values()}
        # Explosions throw debris in the colors of what blew up (see Enemy.kind_name), the player's ship included.
        self.debris_colors = {"Player": models.main_colors(self.player_models[SHIPS[DEFAULT_SHIP].drawing])}
        self._ship_model(Missile.drawing)
        self.shield_bubble = models.shield_bubble_model()
        self.pickup_models = {weapon: models.pickup_model(LETTERS[weapon], WEAPON_COLORS[weapon]) for weapon in WEAPONS}
        self.pickup_models["repair"] = models.repair_model()
        self.pickup_models["life"] = models.extra_life_model()
        for kind in SECONDARY_WEAPONS:
            self.pickup_models[kind] = models.pickup_model(SECONDARY_LETTERS[kind], SECONDARY_COLORS[kind])
        self.secondary_models = {"turret": models.gun_turret_model(), "lightning": models.lightning_coil_model()}

    def _ship_model(self, drawing: str) -> NodePath:
        """Return the model of an enemy, a part or a missile, built the first time."""
        if drawing not in self.ship_models:
            model = self.ship_models[drawing] = models.model(drawing)
            self.debris_colors[drawing] = models.main_colors(model)
        return self.ship_models[drawing]

    def _prepare_level(self, level: Level) -> None:
        """Build the models of the level's enemies now (and what they launch), so the game doesn't stall on them."""
        for kind in {wave.enemy for wave in level.waves}:
            for drawing in drawings(kind):
                self._ship_model(drawing)

    def _make_block(self, entity: Entity) -> NodePath:
        """Make the entity's model in the scene (bullets are sprites, see _sync_nodes)."""
        node = self._make_model(entity)
        node.reparentTo(self.render)
        return node

    def _make_model(self, entity: Entity) -> NodePath:
        """Make a copy of the entity's model.

        Models are in world units, all with the same cubes, their size from their drawing (about their hitbox). Copied,
        not instanced, so each Turret can aim its own barrel.
        """
        node = NodePath("entity")
        if isinstance(entity, Player):
            self.player_models[entity.ship.drawing].copyTo(node)
            bounds = node.getTightBounds()
            front = bounds[0].y if bounds else 0.0  # the secondary weapons sit on top of the ship, hidden until carried
            for kind, model in self.secondary_models.items():
                mount = node.attachNewNode(f"secondary_{kind}")
                mount.setY(front)
                model.copyTo(mount)
                mount.hide()
            return node
        model = self.pickup_models[entity.kind] if isinstance(entity, Pickup) else self._ship_model(drawing_of(entity))
        model.copyTo(node)
        if isinstance(entity, Enemy) and shielded(entity):
            bubble = node.attachNewNode("bubble")  # the bubble fits a 1 x 1 x 1 box: stretched around the ship
            bubble.setScale(entity.width)
            self.shield_bubble.copyTo(bubble)
        return node


def fitted_model(model: NodePath, size: float) -> NodePath:
    """Make a copy of a world-sized model, `size` across, fitted in a 1 x 1 x 1 box.

    For the ship select, and the dev tools' Models screen.
    """
    box = NodePath("fitted")
    inner = box.attachNewNode("scaled")
    inner.setScale(1 / size)
    model.copyTo(inner)
    return box


def shielded(enemy: Enemy) -> bool:
    """Whether it has a shield (a state looking "shield"): its model has a bubble, shown while it's up."""
    return any(state.look == "shield" for state in enemy.spec.states)


def drawing_of(entity: Entity) -> str:
    """Return the drawing of an enemy or a missile: its model."""
    return entity.drawing if isinstance(entity, Enemy | Missile) else ""
