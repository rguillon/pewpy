"""Drawing what's in play each frame.

Models placed, turned and shaded, bullets as sprites, laser beams, the lightning bolt, and the effects of what
happened.
"""

import itertools
import math
import random

from panda3d.core import LineSegs, NodePath

from pewpy.app.bullets import (
    BULLET_BODY,
    MAX_BULLETS,
    WARNING_BEAM_COLOR,
    WARNING_SCALE,
    bullet_sprite,
    is_beam,
    is_round_bullet,
    is_warning,
)
from pewpy.app.entity_models import shielded
from pewpy.app.event_effects import event_effect
from pewpy.app.hud import Hud
from pewpy.app.window import Color
from pewpy.game.enemies.enemy import Enemy
from pewpy.game.entities import Entity
from pewpy.game.events import Event
from pewpy.game.player import Player
from pewpy.game.weapons.bullets import Bullet, Missile
from pewpy.game.weapons.player.secondary import SECONDARY_WEAPONS
from pewpy.game.world import World
from pewpy.graphics import models
from pewpy.graphics.effects.laser import LaserGlow
from pewpy.graphics.effects.system import ParticleSystem
from pewpy.graphics.effects.view import EffectsView
from pewpy.graphics.sprites import SpriteBatch
from pewpy.scenery.background.view import BackgroundView

LASER_FIRE_RATE = 53.0  # radians a second: how fast a laser's width flickers (the player's and the enemies')
BOLT_COLOR: Color = (0.85, 0.75, 1.0, 1)
BOLT_THICKNESS = 3.0  # pixels
BOLT_STEP = 0.05  # a lightning bolt zigzags every this many world units...
BOLT_ZIGZAG = 0.025  # ...this far to each side, differently every frame
PICKUP_SPIN_SPEED = 120.0  # degrees per second
MINE_SPIN_SPEED = 90.0  # degrees per second
FLASH_COLOR: Color = (1.0, 1.0, 1.0, 1)
LASER_FLICKER = 0.12  # the player's laser beam's width flickers by this share
ENEMY_LASER_CORE: Color = (1.0, 0.82, 0.78, 0.95)  # enemies' laser beams: a white-hot core in a red light
ARMORED_SHADE: Color = (0.55, 0.55, 0.62, 1)  # a boss's core, darker while shots bounce off it
HIT_SHADE: Color = (1.6, 1.6, 1.6, 1)  # bosses light up when hit (white would hide them: they're shot all the time)
PLAYER_BANK_ANGLE = 25.0  # degrees of roll at full sideways speed
FLAME_FLICKER = (0.12, 0.08)  # how much engine flames waver in length: a slow wave and a fast one
FLAME_THRUST = 0.35  # the player's flames: this much longer flying up at full speed, shorter flying down
FLAME_PHASES = 97  # the flames' waver phases: one entity's among these, so neighbouring ones don't wave alike
FLAME_PHASE_STEP = 1.7  # ...and this far apart, along an entity's own flames
THINNEST = 0.001  # the least a beam is drawn this wide: Panda3D complains about a zero scale


class Drawing(Hud):
    """What's in play, drawn each frame (`_sync_nodes`)."""

    # Set up by PewPewApp.__init__.
    background: BackgroundView
    effects: ParticleSystem
    effects_view: EffectsView
    nodes: dict[Entity, NodePath]  # the models of what's in play
    flames: dict[Entity, list[tuple[NodePath, float]]]  # engine flames and their steady length

    def _setup_drawing(self) -> None:
        # Bullets are balls of energy (missiles have a model): solid in the middle, in a glowing halo.
        self.bullet_sprites = SpriteBatch(
            self.render, self.cam.node().getLens(), MAX_BULLETS, glow=False, core=BULLET_BODY, hot=0.35
        )
        self.laser_node = models.laser_beam_model()
        self.laser_node.reparentTo(self.render)
        self.laser_node.hide()
        self.enemy_laser_model = models.laser_beam_model(ENEMY_LASER_CORE)
        self.warning_model = models.laser_beam_model(WARNING_BEAM_COLOR)
        self.beam_nodes: dict[Bullet, NodePath] = {}  # the enemies' laser beams and their warnings
        self.bolt_node = self.render.attachNewNode("bolt")
        self.bolt_rng = random.Random()

    def _show_events(self, events: list[Event], dt: float) -> None:
        """Play the effect of each event that has one (see event_effects.py, beside the sounds in audio/cues.py)."""
        for event in events:
            effect = event_effect(event, dt, self.debris_colors)
            if effect is not None:
                self.effects.play(effect)

    def _sync_nodes(self) -> None:
        self.effects_view.sync()
        self.background.sync()

        world = self.world
        entities = world.entities() if world else []
        self.bullet_sprites.show([bullet_sprite(entity) for entity in entities if is_round_bullet(entity)])
        self._show_beams([
            entity for entity in entities if isinstance(entity, Bullet) and (is_beam(entity) or is_warning(entity))
        ])
        entities = [entity for entity in entities if not isinstance(entity, Bullet) or isinstance(entity, Missile)]
        alive = set(entities)
        for entity in [entity for entity in self.nodes if entity not in alive]:
            self.nodes.pop(entity).removeNode()
            self.flames.pop(entity, None)
        if world is not None:
            self._show_entities(world, entities)
        self._show_laser()
        self._show_bolt()

    def _show_entities(self, world: World, entities: list[Entity]) -> None:
        """Place the models of what's on screen (all but the round bullets), each turned and shaded as it is now."""
        for entity in entities:
            node = self.nodes.get(entity)
            if node is None:
                node = self.nodes[entity] = self._make_block(entity)
                self.flames[entity] = [(flame, flame.getSz()) for flame in node.findAllMatches("**/flame")]
            node.setPos(entity.x, entity.depth if isinstance(entity, Bullet) else 0, entity.y)
            self._flicker(entity)
            if isinstance(entity, Player):
                blink_off = entity.invulnerable and int(entity.invulnerable_time * 10) % 2 == 1
                node.hide() if blink_off else node.show()
                node.setH(-entity.vx / entity.ship.speed * PLAYER_BANK_ANGLE)  # roll around the nose axis
                self._show_secondary(node)
            elif isinstance(entity, Enemy):
                self._show_enemy_appearance(entity, node)
                self._orient_enemy(entity, node, world.player)
            elif isinstance(entity, Missile):
                node.setR(models.facing_roll(entity.vx, entity.vy))
            else:  # a pickup
                node.setH(world.time * PICKUP_SPIN_SPEED)

    def _show_secondary(self, ship: NodePath) -> None:
        secondary = self.world.arsenal.secondary if self.world else None
        for kind in SECONDARY_WEAPONS:
            mount = ship.find(f"secondary_{kind}")
            mount.show() if secondary is not None and secondary.kind == kind else mount.hide()
        if secondary is not None and secondary.kind == "turret":
            ship.find("secondary_turret/**/barrel").setR(models.facing_roll(secondary.aim_x, secondary.aim_y))

    def _show_bolt(self) -> None:
        """Show the lightning gun's last strike, while it shows: a zigzag line, redrawn every frame so it crackles."""
        self.bolt_node.getChildren().detach()
        points = self.world.bolt if self.world else []
        if len(points) < 2:
            return
        lines = LineSegs("bolt")
        lines.setThickness(BOLT_THICKNESS)
        lines.setColor(*BOLT_COLOR)
        lines.moveTo(points[0][0], 0, points[0][1])
        for (x0, z0), (x1, z1) in itertools.pairwise(points):
            length = math.hypot(x1 - x0, z1 - z0)
            steps = max(1, round(length / BOLT_STEP))
            side_x, side_z = (-(z1 - z0) / length, (x1 - x0) / length) if length else (0.0, 0.0)
            for step in range(1, steps + 1):
                along = step / steps
                zig = self.bolt_rng.uniform(-BOLT_ZIGZAG, BOLT_ZIGZAG) if step < steps else 0.0
                lines.drawTo(x0 + (x1 - x0) * along + side_x * zig, 0, z0 + (z1 - z0) * along + side_z * zig)
        bolt = self.bolt_node.attachNewNode(lines.create())
        bolt.setLightOff()
        bolt.setShaderOff()
        bolt.setBin("fixed", 0)
        bolt.setDepthTest(False)
        bolt.setDepthWrite(False)

    def _flicker(self, entity: Entity) -> None:
        thrust = entity.vy / entity.ship.speed if isinstance(entity, Player) else 0.0
        time = self.clock.getFrameTime()
        for index, (flame, length) in enumerate(self.flames.get(entity, ())):
            flame.setSz(length * flame_scale(time, id(entity) % FLAME_PHASES + index * FLAME_PHASE_STEP, thrust))

    @staticmethod
    def _laser_glows(world: World) -> list[LaserGlow]:
        """Return the laser beams this frame, for their light: the player's laser, and the enemies' beams."""
        glows = [
            LaserGlow(
                shot.x,
                shot.y - shot.height / 2,
                shot.y + shot.height / 2,
                shot.width,
                hostile=True,
                key=id(shot),
                depth=shot.depth,
            )
            for shot in world.enemy_bullets
            if is_beam(shot)
        ]
        beam = world.laser
        if beam is not None:
            hits = tuple(event.y for event in world.events if event.kind == "burn")
            glows.append(LaserGlow(beam.x, beam.bottom, beam.top, beam.width, hits))
        return glows

    def _show_beams(self, beams: list[Bullet]) -> None:
        """Show the enemies' laser beams' cores, flickering like the player's laser (their light is an effect).

        And their warnings: thin red lines, at their muzzle's depth like the beams, so a beam fires right where its
        warning was (the camera's perspective bends both the same way).
        """
        for gone in [beam for beam in self.beam_nodes if beam not in beams]:
            self.beam_nodes.pop(gone).removeNode()
        flicker = 1.0 + LASER_FLICKER * math.sin(self.clock.getFrameTime() * LASER_FIRE_RATE)
        for beam in beams:
            node = self.beam_nodes.get(beam)
            warning = is_warning(beam)
            if node is None:
                node = self.beam_nodes[beam] = self.render.attachNewNode("beam")
                (self.warning_model if warning else self.enemy_laser_model).copyTo(node)
            width = beam.width * (WARNING_SCALE if warning else flicker)
            node.setPos(beam.x, beam.depth, beam.y)
            node.setScale(width, width, max(beam.height, THINNEST))

    def _show_laser(self) -> None:
        beam = self.world.laser if self.world else None
        if beam is None:
            self.laser_node.hide()
            return
        self.laser_node.show()
        self.laser_node.setPos(beam.x, 0, (beam.bottom + beam.top) / 2)
        width = beam.width * (1.0 + LASER_FLICKER * math.sin(self.clock.getFrameTime() * LASER_FIRE_RATE))
        self.laser_node.setScale(width, width, max(beam.top - beam.bottom, THINNEST))

    def _show_enemy_appearance(self, enemy: Enemy, node: NodePath) -> None:
        appearance = enemy.appearance()
        if appearance == "hidden":
            node.hide()
            return
        node.show()
        if appearance == "flash":
            node.setColor(*FLASH_COLOR)
        else:
            node.clearColor()  # show the model's own colors
        shade = {"armored": ARMORED_SHADE, "hit": HIT_SHADE}.get(appearance)
        if shade:
            node.setColorScale(*shade)
        else:
            node.clearColorScale()
        if shielded(enemy):
            bubble = node.find("**/shield")
            bubble.show() if appearance == "shield" else bubble.hide()

    def _orient_enemy(self, enemy: Enemy, node: NodePath, player: Player) -> None:
        facing = enemy.facing
        if facing == "player":
            node.find("**/barrel").setR(models.facing_roll(player.x - enemy.x, player.y - enemy.y))
        elif facing == "travel" and (enemy.vx or enemy.vy):
            node.setR(models.facing_roll(enemy.vx, enemy.vy))  # point where it's flying
        elif facing == "spin":
            node.setR(enemy.age * MINE_SPIN_SPEED)


def flame_scale(time: float, phase: float, thrust: float = 0.0) -> float:
    """Return an engine flame's length right now, compared with its steady length.

    It wavers, longer with `thrust` (-1 to 1). `phase` keeps flames from wavering together.
    """
    slow, fast = FLAME_FLICKER
    waver = slow * math.sin(time * 23 + phase) + fast * math.sin(time * 61 + phase * 2.3)
    return max(0.1, 1 + waver + FLAME_THRUST * thrust)
