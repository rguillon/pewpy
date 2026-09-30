import math
import random

import pytest

from pewpy import config
from pewpy.enemies import (
    ENEMY_TYPES,
    HALF_WIDTH,
    HEAVY_BULLET_SIZE,
    TOP,
    Diver,
    Enemy,
    FlakCannon,
    Gunship,
    Mine,
    MineLayer,
    RocketTruck,
    ShieldCarrier,
    Sniper,
    Splitter,
    Swarmer,
    Tank,
    Turret,
    Weaver,
    make_enemy,
)
from pewpy.entities import Bullet, Entity

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


@pytest.mark.parametrize("kind", sorted(ENEMY_TYPES))
def test_every_enemy_type_enters_and_runs(kind):
    rng = random.Random(0)  # noqa: S311
    enemy = make_enemy(kind, x=5.0, y=0.5, side="right", rng=rng)
    if enemy.side_entry:
        assert enemy.x > HALF_WIDTH
    else:
        assert enemy.y > TOP
        assert abs(enemy.x) <= HALF_WIDTH - enemy.width / 2  # x=5.0 was clamped
    start = (enemy.x, enemy.y)
    run(enemy, 20.0)
    assert (enemy.x, enemy.y) != start


def test_side_entry_from_the_left_moves_right():
    enemy = make_enemy("mine_layer", x=0, y=0.3, side="left", rng=random.Random(0))  # noqa: S311
    assert enemy.x < -HALF_WIDTH
    assert enemy.y == 0.3
    run(enemy, 1.0)
    assert enemy.vx > 0


def test_weaver_snakes_around_its_column():
    weaver = Weaver(x=0.2, y=0.9)
    xs = [weaver.x]
    for _ in range(120):
        weaver.update(DT, TARGET, SCROLL)
        xs.append(weaver.x)
    assert max(xs) == pytest.approx(0.45, abs=0.01)
    assert min(xs) == pytest.approx(-0.05, abs=0.01)
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


def test_only_ground_enemies_are_marked_as_on_the_ground():
    assert {kind for kind, enemy in ENEMY_TYPES.items() if enemy.ground} == {
        "turret",
        "flak_cannon",
        "tank",
        "rocket_truck",
    }


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

    edge = -(0.75 + Swarmer.width / 2)
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
