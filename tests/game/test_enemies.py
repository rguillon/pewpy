import itertools
import math
import random

import pytest

from pewpy import config
from pewpy.game.enemies import (
    HALF_WIDTH,
    HEAVY_BULLET_SIZE,
    TOP,
    Bomber,
    Buckshot,
    ClusterBomb,
    Diver,
    Enemy,
    FlakCannon,
    Gunship,
    HomingMissile,
    Hunter,
    Lancer,
    Mine,
    MineLayer,
    MissileSilo,
    Rocket,
    Rocketeer,
    RocketTruck,
    Serpent,
    ShieldCarrier,
    Sniper,
    Splitter,
    Swarmer,
    Tank,
    Turret,
    WaveBullet,
    Weaver,
)
from pewpy.game.entities import Bullet, Entity
from pewpy.game.roster import make_enemy

DT = 1 / 60
TARGET = Entity(x=0.0, y=-0.75)  # where the player starts
SCROLL = 0.2


def run(enemy: Enemy, seconds: float, target: Entity = TARGET) -> list[Entity]:
    created = []
    for _ in range(round(seconds / DT)):
        created += enemy.update(DT, target, SCROLL)
    return created


def bullets(created: list[Entity]) -> list[Bullet]:
    return [entity for entity in created if isinstance(entity, Bullet)]


def test_weaver_snakes_around_its_column():
    weaver = Weaver(x=0.2, y=0.9)
    xs = [weaver.x]
    for _ in range(120):
        weaver.update(DT, TARGET, SCROLL)
        xs.append(weaver.x)
    reach = 0.25 * config.WIDTH_SCALE  # wider with the screen
    assert max(xs) == pytest.approx(0.2 + reach, abs=0.01)
    assert min(xs) == pytest.approx(0.2 - reach, abs=0.01)
    assert bullets(run(weaver, 5.0)) == []


def test_diver_waits_then_dives_at_the_player():
    diver = Diver(x=0.3, y=1.0)
    run(diver, 1.1)
    assert diver.phase == "wait"
    assert (diver.vx, diver.vy) == (0.0, 0.0)
    run(diver, 0.8)
    assert diver.phase == "dive"
    assert math.hypot(diver.vx, diver.vy) == pytest.approx(1.2)
    assert diver.vx < 0  # toward the player at x=0
    assert diver.vy < 0


def test_gunship_fires_a_three_shot_spread():
    gunship = Gunship(x=0.0, y=0.5, vy=0.0, fire_cooldown=0.0)
    shots = bullets(gunship.update(DT, TARGET, SCROLL))
    assert len(shots) == 3
    assert sorted(round(shot.vx, 3) for shot in shots) == [
        round(-0.5 * math.sin(math.radians(20)), 3),
        0.0,
        round(0.5 * math.sin(math.radians(20)), 3),
    ]
    assert all(shot.vy < 0 for shot in shots)


def test_flak_cannon_sits_on_the_ground_and_fires_pairs_straight_down():
    flak = FlakCannon(x=0.3, y=0.5, fire_cooldown=0.0)
    shots = bullets(run(flak, 1.0))
    assert flak.vy == -SCROLL
    assert len(shots) == 2 * FlakCannon.volley  # two pairs in a row
    assert all(shot.vx == 0 and shot.vy < 0 for shot in shots)  # straight down, whatever the player does
    assert {round(shot.x - shots[0].x, 6) for shot in shots[:2]} == {0.0, round(FlakCannon.barrel_spacing, 6)}


def test_tank_crawls_sideways_on_the_ground_turns_back_at_the_edge_and_aims():
    tank = Tank(x=-0.2, y=0.5, fire_cooldown=0.0)
    shots = bullets(run(tank, 0.5, target=Entity(x=0.4, y=-0.75)))
    assert tank.vy == -SCROLL
    assert tank.vx == Tank.crawl_speed  # towards the middle
    assert shots and shots[0].vx > 0  # aimed at the player, down and to the right
    tank = Tank(x=HALF_WIDTH - Tank().width / 2 + 0.01, y=0.5, vx=Tank.crawl_speed)
    run(tank, DT)
    assert tank.vx == -Tank.crawl_speed


def test_rocket_truck_drives_down_faster_than_the_ground_and_fires_heavy_rockets_straight_down():
    truck = RocketTruck(x=0.0, y=0.5, fire_cooldown=0.0)
    shots = bullets(run(truck, 0.5))
    assert truck.vy == -SCROLL - RocketTruck.drive_speed
    assert shots
    assert all(shot.vx == 0 and shot.vy < 0 and shot.style == "heavy" for shot in shots)
    assert shots[0].width == HEAVY_BULLET_SIZE


def test_turret_scrolls_with_the_ground_and_fires_bursts_of_three():
    turret = Turret(x=0.3, y=0.5, fire_cooldown=0.0)
    shots = bullets(run(turret, 1.0))
    assert turret.vy == -SCROLL
    assert len(shots) == 3
    assert bullets(run(turret, 1.0)) == []  # waiting for the next burst


def test_swarmer_curves_down():
    swarmer = Swarmer(x=-0.8, y=0.5)
    swarmer.enter_from_side(1)
    run(swarmer, 0.1)
    assert swarmer.vx > 0.5
    run(swarmer, 3.0)
    assert swarmer.vx == pytest.approx(0.0, abs=0.01)
    assert swarmer.vy == pytest.approx(-0.6, abs=0.01)


def test_swarmer_entering_from_farther_out_curves_the_same_way():
    # Enemies enter off screen, farther out than the play area: the curve only starts at the play area's edge.
    def path_end(start_x: float) -> float:
        swarmer = Swarmer(x=start_x, y=0.5)
        swarmer.enter_from_side(1)
        while swarmer.vy > -0.59:
            run(swarmer, 0.05)
        return swarmer.x

    edge = -(config.PLAY_WIDTH / 2 + Swarmer.width / 2)
    assert path_end(edge - 0.4) == pytest.approx(path_end(edge), abs=0.03)


def test_sniper_stops_charges_fires_and_leaves():
    sniper = Sniper(x=0.0, y=1.0, fire_cooldown=0.0)
    run(sniper, 1.2)
    assert sniper.phase == "stay"
    assert sniper.vy == 0.0
    sniper.update(DT, TARGET, SCROLL)
    assert sniper.appearance() == "flash"  # warning glow before the shot
    shots = bullets(run(sniper, 0.6))
    assert len(shots) == 1
    assert shots[0].style == "sniper"
    assert math.hypot(shots[0].vx, shots[0].vy) == pytest.approx(0.9)
    run(sniper, 12.0)
    assert sniper.phase == "leave"
    assert sniper.vy > 0


def test_mine_layer_drops_mines_that_scroll():
    layer = MineLayer(x=-0.5, y=0.4, vx=0.35, fire_cooldown=0.0)
    mines = [entity for entity in run(layer, 2.05) if isinstance(entity, Mine)]
    assert len(mines) == 3
    run(mines[0], 0.1)
    assert mines[0].vy == -SCROLL


def test_shield_carrier_is_immune_while_shielded_then_fires_a_ring():
    carrier = ShieldCarrier(x=0.0, y=0.5, vy=0.0)
    carrier.hit(5.0)
    assert carrier.health == 10.0
    assert carrier.appearance() == "shield"
    shots = bullets(run(carrier, 2.05))
    assert len(shots) == 8
    carrier.hit(5.0)
    assert carrier.health == 5.0


def test_splitter_splits_into_three_swarmers():
    splitter = Splitter(x=0.1, y=0.2)
    splitter.hit(6.0)
    assert not splitter.alive
    children = splitter.on_destroyed()
    assert len(children) == 3
    assert all(isinstance(child, Swarmer) and (child.x, child.y) == (0.1, 0.2) for child in children)


def test_enemies_do_not_shoot_before_entering_the_screen():
    turret = Turret(x=0.0, y=TOP + 0.5, fire_cooldown=0.0)
    turret.update(DT, TARGET, 0.0)
    assert turret.burst_left == 0


def test_hit_flash():
    enemy = Gunship()
    enemy.hit(1.0)
    assert enemy.appearance() == "flash"
    enemy.update(0.1, TARGET, SCROLL)
    assert enemy.appearance() == "normal"


def test_enemy_bullets_use_config_damage():
    shots = bullets(Gunship(x=0.0, y=0.5, fire_cooldown=0.0).update(DT, TARGET, SCROLL))
    assert all(shot.hostile and shot.damage == config.ENEMY_BULLET_DAMAGE for shot in shots)


def of_type(created: list[Entity], kind: type) -> list:
    return [entity for entity in created if isinstance(entity, kind)]


def test_rockets_fly_straight_and_speed_up_to_their_top_speed():
    rocket = Rocket(x=0.0, y=0.5)
    run(rocket, 0.1)
    assert rocket.vx == 0 and -Rocket.top_speed < rocket.vy < -0.25
    run(rocket, 3.0)
    assert rocket.vy == pytest.approx(-Rocket.top_speed)


def test_homing_missiles_turn_towards_the_player_until_their_fuel_runs_out():
    missile = HomingMissile(x=0.0, y=0.5, heading=math.pi / 2)  # launched upwards
    run(missile, 3.0, target=Entity(x=0.3, y=-0.75))
    assert missile.vy < 0  # turned round, towards the player below
    heading = missile.heading
    run(missile, 1.0, target=Entity(x=-0.5, y=0.9))  # out of fuel: no more turning
    assert missile.heading == pytest.approx(heading)
    assert math.hypot(missile.vx, missile.vy) == pytest.approx(HomingMissile.speed)


def test_cluster_bombs_burst_into_a_ring_of_shots_when_their_fuse_runs_out():
    bomb = ClusterBomb(x=0.0, y=0.5)
    assert bullets(run(bomb, 1.0)) == []
    shards = bullets(run(bomb, 0.3))
    assert len(shards) == ClusterBomb.shards
    assert not bomb.alive
    angles = sorted(math.degrees(math.atan2(shard.vy, shard.vx)) % 360 for shard in shards)
    assert [b - a for a, b in itertools.pairwise(angles)] == pytest.approx([45.0] * 7)  # evenly around


def test_wave_bullets_snake_across_their_line_of_flight():
    bullet = WaveBullet(x=0.0, y=0.5, vx=0.0, vy=-0.45, hostile=True)
    sideways = []
    for _ in range(round(0.7 / DT)):
        bullet.move(DT)
        sideways.append(bullet.x)
    assert min(sideways) < -0.05 < 0.05 < max(sideways)
    assert bullet.y == pytest.approx(0.5 - 0.45 * 0.7, abs=1e-6)


def test_rocketeers_fire_pairs_of_rockets():
    rocketeer = Rocketeer(x=0.0, y=0.5, fire_cooldown=0.0)
    rockets = of_type(run(rocketeer, 0.1), Rocket)
    assert len(rockets) == 2
    assert rockets[1].x - rockets[0].x == pytest.approx(Rocketeer.pod_spacing)


def test_hunters_stop_near_the_top_strafe_and_launch_homing_missiles():
    hunter = Hunter(x=-0.2, y=0.8, fire_cooldown=0.0)
    launched = of_type(run(hunter, 1.5), HomingMissile)
    assert hunter.phase == "stay" and hunter.vy == 0 and hunter.vx > 0
    assert launched


def test_missile_silos_sit_on_the_ground_and_launch_missiles_upwards():
    silo = MissileSilo(x=0.2, y=0.5, fire_cooldown=0.0)
    missiles = of_type(run(silo, 0.1), HomingMissile)
    assert silo.vy == -SCROLL
    assert len(missiles) == 1 and missiles[0].heading == pytest.approx(math.pi / 2)


def test_bombers_cross_the_screen_dropping_cluster_bombs():
    rng = random.Random(0)  # noqa: S311
    bomber = make_enemy("bomber", x=0.0, y=0.6, side="left", rng=rng)
    assert bomber.vx > 0 and bomber.x < -HALF_WIDTH
    bomber.x, bomber.fire_cooldown = 0.0, 0.0
    assert of_type(run(bomber, 0.1), ClusterBomb)
    assert isinstance(bomber, Bomber)


def test_lancers_charge_then_fire_a_beam_straight_down_holding_still():
    lancer = Lancer(x=0.0, y=0.5, vy=0.0, phase="stay", fire_cooldown=0.0)
    run(lancer, DT)
    assert lancer.appearance() == "flash"  # charging: a warning
    beams = bullets(run(lancer, Lancer.charge_duration))
    assert len(beams) == 1
    beam = beams[0]
    assert beam.style == "beam" and beam.x == lancer.x
    assert beam.y + beam.height / 2 == pytest.approx(lancer.y - lancer.height / 2)  # from the Lancer's lance
    assert beam.y - beam.height / 2 < -config.PLAY_HEIGHT / 2  # down past the bottom of the screen
    run(lancer, 0.2)
    assert lancer.vx == 0  # holds still while firing
    beam.move(Lancer.beam_duration)
    assert not beam.alive  # the beam lasts a moment only


def test_lancers_slide_towards_the_players_side_between_shots():
    lancer = Lancer(x=0.0, y=0.5, vy=0.0, phase="stay", fire_cooldown=5.0)
    run(lancer, 0.1, target=Entity(x=0.5, y=-0.75))
    assert lancer.vx == Lancer.slide_speed


def test_serpents_fire_three_snaking_shots_at_the_player():
    serpent = Serpent(x=0.0, y=0.5, fire_cooldown=0.0)
    shots = of_type(run(serpent, 0.1), WaveBullet)
    assert len(shots) == 3
    assert all(shot.style == "wave" and shot.hostile for shot in shots)


def test_buckshots_fire_two_blasts_of_small_pellets_then_dive_away():
    buckshot = Buckshot(x=0.0, y=0.5)
    pellets = bullets(run(buckshot, 2.0))
    assert len(pellets) == Buckshot.blasts * Buckshot.pellets
    assert all(pellet.width == Buckshot.pellet_size for pellet in pellets)
    assert len({round(math.hypot(p.vx, p.vy), 3) for p in pellets[: Buckshot.pellets]}) > 1  # a spray, not a line
    assert buckshot.phase == "leave" and buckshot.vy < 0


def test_a_waiting_diver_blinks():
    diver = Diver(phase="wait", wait_time=0.15)
    assert diver.appearance() == "hidden"
    diver.wait_time = 0.25
    assert diver.appearance() == "normal"


def test_a_hunter_turns_back_at_the_edge_of_the_screen():
    hunter = Hunter(x=HALF_WIDTH, y=0.6, vx=0.12, phase="stay")
    hunter.behave(0.01, TARGET, 0.0)
    assert hunter.vx == -0.12
