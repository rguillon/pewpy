import pytest

from pewpy import config
from pewpy.game import bosses
from pewpy.game.boss_catalog import BOSSES
from pewpy.game.bosses import make_boss
from pewpy.game.enemies import (
    ClusterBomb,
    Drone,
    Enemy,
    FlakCannon,
    HomingMissile,
    Rocket,
    ShieldCarrier,
    Splitter,
    Swarmer,
)
from pewpy.game.entities import Bullet, Pickup
from pewpy.game.level import Level, Wave
from pewpy.game.player import DEFAULT_SHIP, SHIPS
from pewpy.game.weapons import BULLET_FIRE_RATE, MAX_LEVEL, Arsenal, Missile
from pewpy.game.world import Controls, World
from pewpy.scenery.terrain import GROUND_SPEED

DT = 1 / 60
EMPTY_LEVEL = Level(name="empty", scroll_speed=0.2, waves=())
# One far away wave, so the level is not complete while a test adds its own enemies.
QUIET_LEVEL = Level(name="quiet", scroll_speed=0.2, waves=(Wave(time=1000.0),))
BOSS_LEVEL = Level(name="boss", scroll_speed=0.2, waves=(Wave(time=0.0, enemy="harvester"),))


def make_world(level: Level = QUIET_LEVEL) -> World:
    return World(level, seed=0)


def run(world: World, seconds: float, controls: Controls | None = None) -> None:
    for _ in range(round(seconds / DT)):
        world.update(DT, controls or Controls())


def boss_world() -> World:
    return World(BOSS_LEVEL, seed=0)


def arsenal_with(weapon: str, level: int) -> Arsenal:
    arsenal = Arsenal(selected=weapon)
    arsenal.levels[weapon] = level
    return arsenal


def armed_world(weapon: str = "bullets", level: int = 1) -> World:
    return World(QUIET_LEVEL, seed=0, arsenal=arsenal_with(weapon, level))


def still_enemy(kind: type[Enemy] = Drone, **fields) -> Enemy:
    return kind(vy=0.0, fire_cooldown=1000.0, **fields)


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
    assert kinds(world) == ["impact", "hurt", "explosion"]
    assert world.events[0].source == "player"
    assert (world.events[2].source, world.events[2].x, world.events[2].y) == ("Player", x, y)


def test_ramming_an_enemy_blows_it_up_too():
    world = make_world()
    world.enemies.append(Drone(x=world.player.x, y=world.player.y, vy=0.0, fire_cooldown=1000.0))
    world.update(DT, Controls())
    assert kinds(world) == ["explosion", "hurt"]
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


def test_shots_fired_are_reported_with_the_weapon():
    world = make_world()
    world.update(DT, Controls(fire=True))
    assert kinds(world) == ["shot"]
    assert world.events[0].source == "bullets"
    world.update(DT, Controls(fire=True))
    assert "shot" not in kinds(world)  # not until the next shot


def test_pickups_collected_are_reported():
    world = make_world()
    world.pickups.append(Pickup(x=world.player.x, y=world.player.y, kind="repair"))
    world.update(DT, Controls())
    assert kinds(world) == ["pickup"]
    assert world.events[0].source == "repair"


def test_a_boss_coming_is_reported():
    world = make_world(Level(name="boss", scroll_speed=0.2, waves=(Wave(time=0.0, enemy="warden"),)))
    world.update(DT, Controls())
    assert "boss" in kinds(world)


def test_a_boss_and_its_parts_stay_in_the_world_and_hold_the_level():
    world = boss_world()
    run(world, 0.1)
    assert world.boss is not None
    assert len(world.enemies) == 1 + len(BOSSES["harvester"].parts)
    run(world, 30)
    assert not world.completed
    assert world.boss is not None


def test_destroying_the_boss_takes_its_parts_down_and_completes_the_level():
    world = boss_world()
    run(world, 0.1)
    boss = world.boss
    assert boss is not None
    boss.parts[1].alive = False
    boss.phase_index = 1
    score = world.score
    world._damage(boss, boss.health)
    assert not boss.parts[0].alive
    assert world.score == score + boss.points  # the parts give no points when wrecked
    explosions = [event for event in world.events if event.kind == "explosion"]
    assert len(explosions) == len(bosses.EXPLOSIONS) + 1
    run(world, DT)
    assert not world.completed  # a moment to pick up what it dropped
    run(world, config.BOSS_BEATEN_TIME)
    assert world.completed


def test_once_the_boss_is_beaten_enemies_and_their_shots_are_gone_and_the_player_plays_on():
    world = boss_world()
    run(world, 0.1)
    boss = world.boss
    assert boss is not None
    world.enemies.append(Rocket(x=0.3, y=0.2))
    world.enemy_bullets.append(Bullet(x=0.0, y=0.0, vy=-0.5))
    for part in boss.parts:
        part.alive = False
    boss.phase_index = 1
    world._damage(boss, boss.health)
    assert not boss.alive
    score = world.score
    run(world, DT)
    assert world.enemies == []
    assert world.enemy_bullets == []
    assert world.score == score  # wrecked, not shot down: no points
    assert any(event.kind == "explosion" and event.source == "Rocket" for event in world.events)
    x = world.player.x
    run(world, 0.5, Controls(move_x=1.0))
    assert world.player.x > x  # still playing
    world.enemy_bullets.append(Bullet(x=0.0, y=0.0, vy=-0.5))  # anything fired late vanishes too
    run(world, DT)
    assert world.enemy_bullets == []


def test_ramming_a_boss_hurts_the_player_but_not_the_boss():
    world = boss_world()
    run(world, 0.1)
    boss = world.boss
    assert boss is not None
    boss.x, boss.y = world.player.x, world.player.y
    health = world.player.health
    world.update(DT, Controls())
    assert world.player.health < health
    assert boss.alive


def test_laser_hits_only_the_first_enemy_until_level_3():
    world = armed_world("laser", 1)
    near, far = still_enemy(x=0.0, y=0.0), still_enemy(x=0.0, y=0.5)
    world.enemies += [near, far]
    world.update(0.25, Controls(fire=True))
    assert near.health == pytest.approx(3.0 - 8.0 * 0.25)
    assert far.health == 3.0
    assert world.laser is not None
    assert world.laser.top == pytest.approx(near.y - near.height / 2)


def test_piercing_laser_hits_every_enemy_in_the_beam():
    world = armed_world("laser", 3)
    enemies = [still_enemy(x=0.03, y=0.0), still_enemy(x=0.0, y=0.5), still_enemy(x=0.5, y=0.5)]
    world.enemies += enemies
    world.update(0.1, Controls(fire=True))
    assert [enemy.health for enemy in enemies] == pytest.approx([3.0 - 1.8, 3.0 - 1.8, 3.0])
    assert world.laser is not None
    assert world.laser.top == config.PLAY_HEIGHT / 2


def test_laser_reaches_the_top_of_the_screen_but_not_beyond():
    # The tilted camera shows more than the play area at the top: the beam goes up to the screen's edge.
    world = World(QUIET_LEVEL, seed=0, arsenal=arsenal_with("laser", 3), view_top=1.6)
    in_the_band, above_the_screen = still_enemy(x=0.0, y=1.3), still_enemy(x=0.0, y=1.8)
    world.enemies += [in_the_band, above_the_screen]
    world.update(0.1, Controls(fire=True))
    assert world.laser is not None
    assert world.laser.top == 1.6
    assert in_the_band.health < 3.0
    assert above_the_screen.health == 3.0


def test_laser_kill_scores_and_beam_goes_away_when_not_firing():
    world = armed_world("laser", 3)
    enemy = still_enemy(x=0.0, y=0.0)
    world.enemies.append(enemy)
    for _ in range(round(0.2 / DT)):
        world.update(DT, Controls(fire=True))
    assert not enemy.alive
    assert world.score == 100
    world.update(DT, Controls())
    assert world.laser is None


def test_shielded_enemy_stops_the_laser_without_damage():
    world = armed_world("laser", 1)
    carrier = still_enemy(ShieldCarrier, x=0.0, y=0.0)
    world.enemies.append(carrier)
    world.update(0.1, Controls(fire=True))
    assert carrier.health == 10.0


def test_missile_explosion_damages_neighbors():
    world = armed_world()
    target, neighbor, bystander = still_enemy(x=0.0, y=0.3), still_enemy(x=0.08, y=0.3), still_enemy(x=0.5, y=0.3)
    world.enemies += [target, neighbor, bystander]
    world.player_bullets.append(Missile(x=0.0, y=0.3, damage=3.0, splash_damage=1.5))
    world.update(DT, Controls())
    assert target.health == 0.0
    assert neighbor.health == 1.5
    assert bystander.health == 3.0


def test_destroyed_enemies_can_drop_pickups(monkeypatch):
    monkeypatch.setattr(Drone, "drop_chance", 1.0)
    world = armed_world("laser", 3)
    enemy = still_enemy(x=0.0, y=0.0, health=0.1)
    world.enemies.append(enemy)
    world.update(DT, Controls(fire=True))
    assert len(world.pickups) == 1
    assert world.pickups[0].kind in {"bullets", "laser", "missiles", "repair", "life", "turret", "lightning"}
    assert (world.pickups[0].x, world.pickups[0].y) == pytest.approx((0.0, 0.0), abs=0.01)


def test_enemies_without_drops_never_drop():
    world = armed_world("laser", 3)
    for y in (0.0, 0.2, 0.4, 0.6):
        world.enemies.append(still_enemy(Swarmer, x=0.0, y=y, health=0.1))  # Swarmers have no drops
    world.update(DT, Controls(fire=True))
    assert world.score == 4 * 50
    assert world.pickups == []


def test_upgrade_capsule_raises_that_weapon_and_keeps_the_selection():
    world = armed_world("bullets", 1)
    world.pickups.append(Pickup(x=world.player.x, y=world.player.y, kind="missiles"))
    world.update(DT, Controls())
    assert world.arsenal.levels["missiles"] == 2
    assert world.arsenal.selected == "bullets"
    assert world.pickups == []


def test_upgrade_at_max_level_gives_points():
    world = armed_world("laser", MAX_LEVEL)
    world.pickups.append(Pickup(x=world.player.x, y=world.player.y, kind="laser"))
    world.update(DT, Controls())
    assert world.score == config.MAX_LEVEL_UPGRADE_POINTS


def test_repair_restores_health_up_to_the_maximum():
    world = armed_world()
    world.player.health = 2.0
    world.pickups.append(Pickup(x=world.player.x, y=world.player.y, kind="repair"))
    world.update(DT, Controls())
    assert world.player.health == 4.0
    world.pickups.append(Pickup(x=world.player.x, y=world.player.y, kind="repair"))
    world.update(DT, Controls())
    assert world.player.health == SHIPS[DEFAULT_SHIP].health


def test_an_extra_life_adds_a_life_up_to_the_most():
    world = armed_world()
    world.pickups.append(Pickup(x=world.player.x, y=world.player.y, kind="life"))
    world.update(DT, Controls())
    assert world.lives == config.PLAYER_LIVES + 1
    assert [event.source for event in world.events if event.kind == "pickup"] == ["life"]
    world.lives = config.MAX_LIVES
    world.pickups.append(Pickup(x=world.player.x, y=world.player.y, kind="life"))
    world.update(DT, Controls())
    assert world.lives == config.MAX_LIVES
    assert world.score == config.EXTRA_LIFE_POINTS


def test_drops_are_mostly_upgrades_sometimes_a_repair_or_secondary_weapon_rarely_a_life(monkeypatch):
    monkeypatch.setattr(Drone, "drop_chance", 1.0)
    world = armed_world()
    kinds = []
    for _ in range(3000):
        world.pickups = []
        world._maybe_drop(still_enemy(x=0.0, y=0.0))
        kinds.append(world.pickups[0].kind)
    shares = {kind: kinds.count(kind) / len(kinds) for kind in set(kinds)}
    upgrades = sum(shares.get(weapon, 0.0) for weapon in ("bullets", "laser", "missiles"))
    assert upgrades == pytest.approx(config.PICKUP_UPGRADE_SHARE, abs=0.03)
    assert shares["life"] == pytest.approx(config.PICKUP_LIFE_SHARE, abs=0.015)
    secondaries = shares.get("turret", 0.0) + shares.get("lightning", 0.0)
    assert secondaries == pytest.approx(config.PICKUP_SECONDARY_SHARE, abs=0.02)
    others = config.PICKUP_UPGRADE_SHARE + config.PICKUP_LIFE_SHARE + config.PICKUP_SECONDARY_SHARE
    assert shares["repair"] == pytest.approx(1 - others, abs=0.03)


def test_pickups_drift_down_and_leave_the_screen():
    world = armed_world()
    pickup = Pickup(x=0.6, y=-0.9)
    world.pickups.append(pickup)
    run_seconds = 2.0
    for _ in range(round(run_seconds / DT)):
        world.update(DT, Controls())
    assert world.pickups == []


def test_weapon_levels_survive_losing_a_life():
    world = armed_world("missiles", 3)
    world.player.health = 0.0
    world.update(DT, Controls())
    assert world.lives == config.PLAYER_LIVES - 1
    assert world.arsenal.selected == "missiles"
    assert world.arsenal.levels["missiles"] == 3


@pytest.mark.parametrize("kind", BOSSES)
def test_every_part_of_every_boss_can_be_shot_from_below(kind):
    """Shots fly up: under a part they go over the core up to it (the parts in front of it destroyed)."""
    for target in BOSSES[kind].parts:
        world = make_world()
        boss = make_boss(BOSSES[kind], 0.0, top=0.2)
        boss.parts_released = True
        world.enemies += [boss, *boss.parts]
        world.update(DT, Controls())  # the parts take their places
        part = next(part for part in boss.parts if part.name == target.name)
        for other in boss.parts:
            other.alive = other is part
        world.player_bullets.append(Bullet(x=part.x, y=part.y - part.height / 2 - 0.03, vy=3.0, width=0.02))
        run(world, 0.1)
        assert part.health < target.health, target.name
        assert boss.health == BOSSES[kind].health


def test_the_laser_goes_over_a_boss_core_up_to_the_part_above_it():
    world = armed_world("laser", 1)
    boss = make_boss(BOSSES["reaper"], 0.0, top=0.2)
    boss.parts_released = True
    world.enemies += [boss, *boss.parts]
    world.update(DT, Controls())
    cutter = next(part for part in boss.parts if part.name == "cutter")
    world.player.x = cutter.x
    run(world, 0.5, Controls(fire=True))
    assert cutter.health < BOSSES["reaper"].parts[2].health
    assert boss.health == BOSSES["reaper"].health
