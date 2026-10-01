"""The game world during play: player, enemies, bullets, pickups, score and lives. Independent from rendering."""

import math
import random
from dataclasses import dataclass

from pewpy import config
from pewpy.game.boss_catalog import BOSSES
from pewpy.game.bosses import Boss, make_boss
from pewpy.game.enemies import Enemy
from pewpy.game.entities import Bullet, Entity, Pickup
from pewpy.game.level import Level
from pewpy.game.player import DEFAULT_SHIP, SHIPS, Player, ShipSpec
from pewpy.game.roster import make_enemy
from pewpy.game.weapons import MISSILE_SPLASH_RADIUS, WEAPONS, Arsenal, Beam, LaserStats, Missile
from pewpy.scenery.terrain import GROUND_SPEED


@dataclass
class Controls:
    move_x: float = 0.0
    move_y: float = 0.0
    fire: bool = False


@dataclass(frozen=True)
class Event:
    """Something the effects show (see effects.py) or the sounds play (see audio/cues.py), collected during one
    update.

    kind: "impact" (a shot hit `source`: "enemy" or "player"), "explosion" (`source` blew up: an enemy class
    name like "Drone", a boss's drawing like "warden", or "Player"), "blast" (a missile exploded, `size` = its splash
    radius), "burn" (the laser is burning an enemy at x, y), "shot" (the player fired `source`: "bullets" or
    "missiles"), "hurt" (the player was hit), "pickup" (the player picked up `source`: "repair" or a weapon) or
    "boss" (a boss came).
    """

    kind: str
    x: float
    y: float
    size: float = 0.0
    source: str = ""


SHOT_MARGIN = 0.05  # shots are removed once this far past the edge of the screen (they're smaller than this)
PLAYER_EXPLOSION_SIZE = 0.2
MISSILE_BLAST_SIZE = 0.05  # a missile without splash damage still explodes, smaller


class World:
    """One level being played."""

    def __init__(
        self,
        level: Level,
        score: int = 0,
        lives: int = config.PLAYER_LIVES,
        seed: int | None = None,
        arsenal: Arsenal | None = None,
        view_top: float = config.PLAY_HEIGHT / 2,
        ship: ShipSpec | None = None,
        view_side: float = config.PLAY_WIDTH / 2,
    ) -> None:
        self.ship = ship or SHIPS[DEFAULT_SHIP]  # the player's ship, for every life
        self.rng = random.Random(seed)  # noqa: S311 - gameplay randomness, not cryptography
        # Top and sides of the screen on the play plane. The tilted camera shows more than the play area at the
        # top (higher and wider), so the app passes where the screen really ends: the laser goes up to there,
        # shots fly until they are off screen, and enemies appear off screen.
        self.view_top = view_top
        self.view_side = view_side
        self.level = level
        self.level_start_score = score
        self.lives = lives
        self.arsenal = arsenal or Arsenal()  # kept when a life is lost
        self.events: list[Event] = []  # what happened during the last update, for the effects
        self.start_life()

    def start_life(self) -> None:
        """(Re)start the level from the beginning with full health and the score it started with."""
        self.score = self.level_start_score
        self.time = 0.0
        self.pending_spawns = self.level.spawns()
        self.player = Player(ship=self.ship)
        self.player_bullets: list[Bullet] = []
        self.enemies: list[Enemy] = []
        self.enemy_bullets: list[Bullet] = []
        self.pickups: list[Pickup] = []
        self.laser: Beam | None = None
        self.boss_beaten_time = 0.0  # counts down once the boss is destroyed: the level ends at 0
        self.boss_beaten = False
        self._created: list[Entity] = []  # enemies created while iterating, added after collisions

    @property
    def game_over(self) -> bool:
        return self.lives <= 0

    @property
    def completed(self) -> bool:
        """Every wave has entered and no enemy is left."""
        waiting = self.boss_beaten and self.boss_beaten_time > 0  # still picking up what the boss dropped
        return not self.game_over and not self.pending_spawns and not self.enemies and not waiting

    @property
    def boss(self) -> Boss | None:
        """The boss being fought, if there is one."""
        return next((enemy for enemy in self.enemies if isinstance(enemy, Boss) and enemy.alive), None)

    def entities(self) -> list[Entity]:
        return [self.player, *self.player_bullets, *self.enemies, *self.enemy_bullets, *self.pickups]

    def update(self, dt: float, controls: Controls) -> None:
        self.events = []
        if self.game_over or self.completed:
            return
        self.time += dt
        self.player.update(dt, controls.move_x, controls.move_y, controls.fire)
        shots = self.arsenal.fire(dt, controls.fire, self.player)
        if shots:
            self.events.append(Event("shot", self.player.x, self.player.y, source=self.arsenal.selected))
        self.player_bullets += shots
        self._spawn_enemies()
        self._update_enemies(dt)
        self._move_shots(dt)
        self._fire_laser(dt, self.arsenal.laser(controls.fire))
        self._collide()
        self._add(self._created)
        self._created = []
        if self.boss_beaten:
            self.boss_beaten_time -= dt
            self._clear_field()
        self._collect_pickups(dt)
        self._remove_dead()

        if self.player.health <= 0:
            player = self.player
            self.events.append(Event("explosion", player.x, player.y, PLAYER_EXPLOSION_SIZE, "Player"))
            self.lives -= 1
            if not self.game_over:
                self.start_life()

    def _spawn_enemies(self) -> None:
        while self.pending_spawns and self.pending_spawns[0].time <= self.time:
            spawn = self.pending_spawns.pop(0)
            if spawn.enemy in BOSSES:
                self.enemies.append(make_boss(BOSSES[spawn.enemy], spawn.x, self.view_top))
                self.events.append(Event("boss", spawn.x, self.view_top, source=spawn.enemy))
                continue
            enemy = make_enemy(spawn.enemy, spawn.x, spawn.y, spawn.side, self.rng, self.view_top, self.view_side)
            self.enemies.append(enemy)

    def _update_enemies(self, dt: float) -> None:
        for enemy in list(self.enemies):
            self._add(enemy.update(dt, self.player, self.scroll_speed(enemy)))
            if not enemy.alive:  # it used itself up (a cluster bomb bursting): it blows up, without points
                self._explode(enemy)

    def scroll_speed(self, enemy: Enemy) -> float:
        """How fast the scenery under `enemy` scrolls down the play plane: the ground scrolls slower on screen than
        the level (it's far below, see GROUND_SPEED), so units on the ground go with it, not with the level."""
        return self.level.scroll_speed * (GROUND_SPEED if enemy.ground else 1.0)

    def _add(self, created: list[Entity]) -> None:
        for entity in created:
            if isinstance(entity, Enemy):
                self.enemies.append(entity)
            elif isinstance(entity, Bullet):
                self.enemy_bullets.append(entity)

    def _move_shots(self, dt: float) -> None:
        targets = [enemy for enemy in self.enemies if enemy.alive and enemy.on_screen]
        for bullet in self.player_bullets:
            if isinstance(bullet, Missile):
                bullet.steer(dt, targets)
            bullet.move(dt)
        for bullet in self.enemy_bullets:
            bullet.move(dt)

    def _fire_laser(self, dt: float, stats: LaserStats | None) -> None:
        if stats is None:
            self.laser = None
            return
        player = self.player
        bottom = player.y + player.height / 2
        in_beam = sorted(
            (
                enemy
                for enemy in self.enemies
                if enemy.alive
                and enemy.y + enemy.height / 2 > bottom
                and enemy.y - enemy.height / 2 < self.view_top  # not above the screen
                and abs(enemy.x - player.x) < (stats.width + enemy.width) / 2
            ),
            key=lambda enemy: enemy.y,
        )
        top = self.view_top
        if not stats.pierces and in_beam:
            in_beam = in_beam[:1]
            top = max(bottom, in_beam[0].y - in_beam[0].height / 2)  # the beam stops at the first enemy
        self.laser = Beam(x=player.x, bottom=bottom, top=top, width=stats.width)
        for enemy in in_beam:
            self.events.append(Event("burn", player.x, enemy.y - enemy.height / 2))
            self._damage(enemy, stats.damage_per_second * dt)

    def _damage(self, enemy: Enemy, amount: float) -> None:
        """Damage from the player's weapons: scores, splits and drops when the enemy is destroyed."""
        if not enemy.alive:
            return
        enemy.hit(amount)
        if enemy.alive:
            return
        self._explode(enemy)
        self.score += enemy.points
        self._created += enemy.on_destroyed()
        self._maybe_drop(enemy)
        for piece in enemy.wreckage():  # a boss's parts go down with it, without points
            piece.alive = False
            self._explode(piece)
        if isinstance(enemy, Boss):
            self.boss_beaten = True
            self.boss_beaten_time = config.BOSS_BEATEN_TIME

    def _clear_field(self) -> None:
        """Once the boss is beaten: every enemy left (missiles, mines...) blows up, without points, and enemy
        bullets vanish, so the player can safely pick up what the boss dropped."""
        for enemy in self.enemies:
            if enemy.alive:
                enemy.alive = False
                self._explode(enemy)
        for bullet in self.enemy_bullets:
            bullet.alive = False
            self.events.append(Event("impact", bullet.x, bullet.y, source="player"))

    def _maybe_drop(self, enemy: Enemy) -> None:
        if self.rng.random() >= enemy.drop_chance:
            return
        kind = self.rng.choice(WEAPONS) if self.rng.random() < config.PICKUP_UPGRADE_SHARE else "repair"
        self.pickups.append(Pickup(x=enemy.x, y=enemy.y, kind=kind))

    def _collide(self) -> None:
        for bullet in self.player_bullets:
            for enemy in self.enemies:
                if enemy.alive and bullet.overlaps(enemy):
                    self._shot_hits(bullet, enemy)
                    break

        player = self.player
        if player.invulnerable:
            return
        for bullet in self.enemy_bullets:
            if bullet.overlaps(player):
                bullet.alive = bullet.pierces  # a beam goes on (the player is briefly invulnerable after a hit)
                self.events.append(Event("impact", player.x, player.y if bullet.pierces else bullet.y, source="player"))
                player.take_hit(bullet.damage)
                self.events.append(Event("hurt", player.x, player.y))
                return
        for enemy in self.enemies:
            if enemy.alive and enemy.overlaps(player):
                if enemy.rammable:
                    enemy.alive = False
                    self._explode(enemy)  # rammed: no points
                player.take_hit(config.ENEMY_RAM_DAMAGE)
                self.events.append(Event("hurt", player.x, player.y))
                return

    def _shot_hits(self, bullet: Bullet, enemy: Enemy) -> None:
        bullet.alive = False  # a shielded enemy absorbs the shot without damage
        if isinstance(bullet, Missile):
            radius = MISSILE_SPLASH_RADIUS if bullet.splash_damage else MISSILE_BLAST_SIZE
            self.events.append(Event("blast", bullet.x, bullet.y, radius))
        else:
            self.events.append(Event("impact", bullet.x, bullet.y + bullet.height / 2, source="enemy"))
        self._damage(enemy, bullet.damage)
        if isinstance(bullet, Missile) and bullet.splash_damage:
            self._splash(bullet, enemy)

    def _explode(self, enemy: Enemy) -> None:
        for x, y, size in enemy.explosions():
            self.events.append(Event("explosion", x, y, size, enemy.kind_name))

    def _splash(self, missile: Missile, direct_hit: Enemy) -> None:
        for enemy in self.enemies:
            near = math.hypot(enemy.x - missile.x, enemy.y - missile.y) <= MISSILE_SPLASH_RADIUS
            if enemy is not direct_hit and near:
                self._damage(enemy, missile.splash_damage)

    def _collect_pickups(self, dt: float) -> None:
        for pickup in self.pickups:
            pickup.move(dt)
            if not pickup.overlaps(self.player):
                continue
            pickup.alive = False
            self.events.append(Event("pickup", pickup.x, pickup.y, source=pickup.kind))
            if pickup.kind == "repair":
                self.player.health = min(self.ship.health, self.player.health + config.REPAIR_AMOUNT)
            elif not self.arsenal.upgrade(pickup.kind):
                self.score += config.MAX_LEVEL_UPGRADE_POINTS

    def _remove_dead(self) -> None:
        on_screen = {"margin": SHOT_MARGIN, "top": self.view_top, "side": self.view_side}
        self.player_bullets = [b for b in self.player_bullets if b.alive and b.in_play_area(**on_screen)]
        self.enemy_bullets = [b for b in self.enemy_bullets if b.alive and b.in_play_area(**on_screen)]
        # Enemies go once they're off screen (they enter from off screen, so this is also after they came in);
        # bosses stay until destroyed.
        self.enemies = [
            e
            for e in self.enemies
            if e.alive and (not e.leaves_screen or e.in_play_area(top=self.view_top, side=self.view_side))
        ]
        self.pickups = [p for p in self.pickups if p.alive and p.in_play_area()]
