import pytest

from pewpy import config
from pewpy.enemies import ClusterBomb, Drone, FlakCannon, HomingMissile, ShieldCarrier, Splitter, Swarmer
from pewpy.entities import Bullet
from pewpy.level import Level, Wave
from pewpy.player import DEFAULT_SHIP, SHIPS
from pewpy.terrain import GROUND_SPEED
from pewpy.weapons import BULLET_FIRE_RATE
from pewpy.world import Controls, World

DT = 1 / 60
EMPTY_LEVEL = Level(name="empty", scroll_speed=0.2, waves=())
# One far away wave, so the level is not complete while a test adds its own enemies.
QUIET_LEVEL = Level(name="quiet", scroll_speed=0.2, waves=(Wave(time=1000.0),))


def make_world(level: Level = QUIET_LEVEL) -> World:
    return World(level, seed=0)


def run(world: World, seconds: float, controls: Controls | None = None) -> None:
    for _ in range(round(seconds / DT)):
        world.update(DT, controls or Controls())


def test_fire_rate():
    world = make_world()
    shots = 0
    for _ in range(round(2.0 / DT)):
        before = len(world.player_bullets)
        world.update(DT, Controls(fire=True))
        shots += len(world.player_bullets) > before
    assert abs(shots - 2 * BULLET_FIRE_RATE) <= 1


def test_no_shots_without_fire():
    world = make_world()
    run(world, 1.0)
    assert world.player_bullets == []


def test_bullets_kill_enemy_and_score():
    world = make_world()
    enemy = Drone(x=world.player.x, y=world.player.y + 0.6, vy=0.0, fire_cooldown=1000.0)
    world.enemies.append(enemy)
    run(world, 1.0, Controls(fire=True))
    assert not enemy.alive
    assert enemy not in world.enemies
    assert world.score == 100


def test_waves_spawn_on_time_at_top_and_move_down():
    level = Level(name="test", scroll_speed=0.2, waves=(Wave(time=1.0, count=3, formation="line"),))
    world = make_world(level)
    run(world, 0.9)
    assert world.enemies == []
    run(world, 0.2)
    assert len(world.enemies) == 3
    enemy = world.enemies[0]
    start_y = enemy.y
    assert start_y > config.PLAY_HEIGHT / 2
    run(world, 1.0)
    assert enemy.y < start_y


def test_destroyed_splitter_adds_swarmers_and_score():
    world = make_world()
    splitter = Splitter(x=world.player.x, y=world.player.y + 0.6, vy=0.0, health=1.0, fire_cooldown=1000.0)
    world.enemies.append(splitter)
    world.player_bullets.append(Bullet(x=splitter.x, y=splitter.y))
    world.update(DT, Controls())
    assert not splitter.alive
    assert world.score == 200
    assert sum(isinstance(enemy, Swarmer) for enemy in world.enemies) == 3


def test_shield_absorbs_bullets():
    world = make_world()
    carrier = ShieldCarrier(x=0.0, y=0.3, vy=0.0)
    world.enemies.append(carrier)
    bullet = Bullet(x=carrier.x, y=carrier.y)
    world.player_bullets.append(bullet)
    world.update(DT, Controls())
    assert not bullet.alive
    assert carrier.health == 10.0


def test_enemy_leaving_bottom_is_removed():
    world = make_world()
    world.enemies.append(Drone(x=0.7, y=-config.PLAY_HEIGHT / 2, fire_cooldown=1000.0))
    run(world, 2.0)
    assert world.enemies == []


def test_enemy_fires_at_player():
    world = make_world()
    world.enemies.append(Drone(x=0.5, y=0.5, vy=0.0, fire_cooldown=0.0))
    world.update(DT, Controls())
    bullet = world.enemy_bullets[0]
    assert bullet.hostile
    assert bullet.vy < 0  # player is below
    assert bullet.vx < 0  # player is to the left


def hit_player(world: World) -> None:
    player = world.player
    world.enemy_bullets.append(Bullet(x=player.x, y=player.y, damage=1.0, hostile=True))
    world.update(DT, Controls())


def test_hit_damages_player_then_invulnerable():
    world = make_world()
    hit_player(world)
    assert world.player.health == SHIPS[DEFAULT_SHIP].health - 1
    assert world.player.invulnerable
    hit_player(world)
    assert world.player.health == SHIPS[DEFAULT_SHIP].health - 1


def test_invulnerability_wears_off():
    world = make_world()
    hit_player(world)
    run(world, config.PLAYER_INVULNERABILITY_TIME + 0.1)
    hit_player(world)
    assert world.player.health == SHIPS[DEFAULT_SHIP].health - 2


def test_ramming_enemy_damages_player_and_dies():
    world = make_world()
    enemy = Drone(x=world.player.x, y=world.player.y, vy=0.0, fire_cooldown=1000.0)
    world.enemies.append(enemy)
    world.update(DT, Controls())
    assert world.player.health == SHIPS[DEFAULT_SHIP].health - config.ENEMY_RAM_DAMAGE
    assert not enemy.alive
    assert world.score == 0


def test_empty_health_loses_life_and_restarts_level():
    level = Level(name="test", scroll_speed=0.2, waves=(Wave(time=0.5), Wave(time=1000.0)))
    world = World(level, score=300, seed=0)
    run(world, 1.0)
    assert len(world.enemies) == 1
    world.score += 100
    world.player.health = 0.5
    old_player = world.player
    hit_player(world)
    assert world.lives == config.PLAYER_LIVES - 1
    assert world.player is not old_player
    assert world.player.health == SHIPS[DEFAULT_SHIP].health
    assert world.enemies == []
    assert world.time == 0.0
    assert len(world.pending_spawns) == 2  # waves replay from the start
    assert world.score == 300  # back to the score the level started with
    assert not world.game_over


def test_game_over_when_no_lives_left():
    world = make_world()
    world.lives = 1
    world.player.health = 0.5
    hit_player(world)
    assert world.lives == 0
    assert world.game_over
    score = world.score
    run(world, 1.0, Controls(fire=True))  # nothing moves any more
    assert world.player_bullets == []
    assert world.score == score


def test_level_completes_when_all_waves_are_gone():
    level = Level(name="test", scroll_speed=0.2, waves=(Wave(time=0.5),))
    world = make_world(level)
    assert not world.completed
    run(world, 1.0)
    assert not world.completed  # the enemy is still on screen
    world.enemies[0].alive = False
    world.update(DT, Controls())
    assert world.completed


def test_empty_level_is_complete_immediately():
    assert make_world(EMPTY_LEVEL).completed


def test_score_and_lives_carry_into_next_level():
    world = World(QUIET_LEVEL, score=1200, lives=2)
    assert (world.score, world.lives) == (1200, 2)


# --- events for the effects ---


def kinds(world: World) -> list[str]:
    return [event.kind for event in world.events]


def test_shots_hitting_and_destroying_enemies_are_reported():
    world = make_world()
    drone = Drone(x=0.0, y=0.0, vy=0.0, fire_cooldown=1000.0, health=1.0)
    world.enemies.append(drone)
    world.player_bullets.append(Bullet(x=0.0, y=0.0, vy=0.0, damage=1.0))
    world.update(DT, Controls())
    assert kinds(world) == ["impact", "explosion"]
    impact, explosion = world.events
    assert impact.source == "enemy"
    assert (explosion.source, explosion.x, explosion.y) == ("Drone", 0.0, 0.0)
    assert explosion.size == max(drone.width, drone.height)
    world.update(DT, Controls())
    assert world.events == []  # only what happened during the last update


def test_the_player_getting_hit_and_losing_a_life_is_reported():
    world = make_world()
    world.player.health = 1.0
    world.enemy_bullets.append(Bullet(x=world.player.x, y=world.player.y, vy=0.0, damage=1.0, hostile=True))
    x, y = world.player.x, world.player.y
    world.update(DT, Controls())
    assert kinds(world) == ["impact", "explosion"]
    assert world.events[0].source == "player"
    assert (world.events[1].source, world.events[1].x, world.events[1].y) == ("Player", x, y)


def test_ramming_an_enemy_blows_it_up_too():
    world = make_world()
    world.enemies.append(Drone(x=world.player.x, y=world.player.y, vy=0.0, fire_cooldown=1000.0))
    world.update(DT, Controls())
    assert kinds(world) == ["explosion"]
    assert world.score == 0  # still no points for ramming


def test_shots_fly_until_they_are_off_the_screen():
    # The tilted camera shows more than the play area at the top: shots stay until they pass the screen's edges.
    world = World(QUIET_LEVEL, seed=0, view_top=1.6, view_side=1.1)
    in_the_band = Bullet(x=0.0, y=1.4, vy=0.0)
    in_a_top_corner = Bullet(x=1.0, y=1.5, vy=0.0)
    gone_up, gone_sideways = Bullet(x=0.0, y=1.7, vy=0.0), Bullet(x=1.2, y=1.0, vy=0.0)
    world.player_bullets += [in_the_band, in_a_top_corner, gone_up, gone_sideways]
    world.update(DT, Controls())
    assert world.player_bullets == [in_the_band, in_a_top_corner]


def test_enemies_appear_off_screen_and_fly_in():
    # The tilted camera shows more than the play area: enemies must appear beyond the screen's real edges.
    level = Level(
        name="entries",
        scroll_speed=0.2,
        waves=(Wave(time=0.0, enemy="drone"), Wave(time=0.0, enemy="swarmer", side="left", y=0.5), Wave(time=1000.0)),
    )
    world = World(level, seed=0, view_top=1.6, view_side=1.1)
    world.update(DT, Controls())
    drone, swarmer = sorted(world.enemies, key=lambda enemy: enemy.y, reverse=True)
    assert drone.y - drone.height / 2 > 1.6 - 0.01  # just above the top of the screen (one frame in), not removed
    assert swarmer.x + swarmer.width / 2 < -1.1 + 0.02  # just left of the screen (one frame in)
    run(world, 3.0)
    assert any(abs(enemy.x) < 0.75 and enemy.y < 1.0 for enemy in world.enemies)  # they came in


def test_a_bursting_cluster_bomb_blows_up_and_leaves_its_shards():
    world = make_world()
    world.enemies.append(ClusterBomb(x=0.0, y=0.5, fuse=DT / 2))
    world.update(DT, Controls())
    assert world.enemies == []
    assert len(world.enemy_bullets) == ClusterBomb.shards
    assert [event.source for event in world.events if event.kind == "explosion"] == ["ClusterBomb"]


def test_enemy_missiles_can_be_shot_down():
    world = make_world()
    missile = HomingMissile(x=world.player.x, y=world.player.y + 0.4)
    world.enemies.append(missile)
    world.player_bullets.append(Bullet(x=missile.x, y=missile.y, damage=5.0))
    world.update(DT, Controls())
    assert not missile.alive


def test_a_beam_hurts_the_player_and_goes_on():
    world = make_world()
    beam = Bullet(x=world.player.x, y=0.0, width=0.03, height=2.0, hostile=True, life=0.5, pierces=True)
    world.enemy_bullets.append(beam)
    health = world.player.health
    world.update(DT, Controls())
    assert world.player.health == health - beam.damage
    assert beam.alive


def test_the_chosen_ship_is_kept_for_every_life():
    world = World(QUIET_LEVEL, seed=0, ship=SHIPS["juggernaut"])
    assert world.player.ship is SHIPS["juggernaut"]
    world.player.health = 0.5
    hit_player(world)
    assert world.player.ship is SHIPS["juggernaut"]
    assert world.player.health == SHIPS["juggernaut"].health


def test_ground_units_scroll_with_the_ground_and_flyers_with_the_level():
    world = make_world()
    turret = FlakCannon(x=0.0, y=0.5)
    drone = Drone(x=0.3, y=0.5)
    world.enemies += [turret, drone]
    world.update(DT, Controls())
    assert turret.vy == pytest.approx(-QUIET_LEVEL.scroll_speed * GROUND_SPEED)
    assert world.scroll_speed(drone) == QUIET_LEVEL.scroll_speed
