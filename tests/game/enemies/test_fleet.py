import json
import math
from importlib import resources

import pytest

from pewpy import config
from pewpy.game.enemies import fleet
from pewpy.game.enemies.catalog import Mine
from pewpy.game.enemies.enemy import Enemy
from pewpy.game.enemies.fleet import (
    FLEET,
    Albatross,
    Behemoth,
    Brawler,
    Broadside,
    Brood,
    Catamaran,
    Condor,
    Dart,
    Freighter,
    Harrier,
    Hornet,
    Howitzer,
    Imp,
    Javelin,
    Kestrel,
    Manta,
    Mite,
    Needle,
    Outrider,
    Pincer,
    Rampart,
    Rapier,
    Scrapper,
    Spark,
    Stalker,
    Stormcrow,
    Tick,
    Warhawk,
    Wisp,
)
from pewpy.game.entities import Bullet, Entity
from pewpy.game.weapons.enemy.projectiles import ClusterBomb, HomingMissile
from pewpy.game.weapons.enemy.shots import WaveBullet

DT = 1 / 60
TARGET = Entity(x=0.0, y=-0.75)  # where the player starts
SCROLL = 0.2


def run(enemy: Enemy, seconds: float, target: Entity = TARGET) -> list[Entity]:
    created = []
    for _ in range(round(seconds / DT)):
        created += enemy.update(DT, target, SCROLL)
    return created


def shots(created: list[Entity]) -> list[Bullet]:
    return [entity for entity in created if isinstance(entity, Bullet)]


def of_type(created: list[Entity], kind: type) -> list:
    return [entity for entity in created if isinstance(entity, kind)]


@pytest.mark.parametrize("kind", FLEET.values())
def test_every_hitbox_is_its_drawing_and_every_drawing_has_engines(kind):
    drawing = json.loads((resources.files("pewpy") / "models" / f"{kind.drawing}.json").read_text())
    rows = drawing["rows"]
    enemy = kind()
    assert enemy.width == pytest.approx(len(rows[0]) * config.MODEL_VOXEL)
    assert enemy.height == pytest.approx(len(rows) * config.MODEL_VOXEL)
    assert drawing["engines"]


def test_darts_dive_then_swerve_at_the_player_once():
    dart = Dart(x=0.4, y=0.5)
    run(dart, 0.5, Entity(x=-0.3, y=-0.75))
    assert dart.swerved and dart.vx < 0
    speed = dart.vx
    run(dart, 0.5, Entity(x=0.6, y=-0.75))
    assert dart.vx == speed  # only once


def test_mites_spiral_down_and_shoot():
    mite = Mite(x=0.0, y=0.5, fire_cooldown=0.0)
    xs = []
    created = []
    for _ in range(120):
        created += mite.update(DT, TARGET, SCROLL)
        xs.append(mite.x)
    assert max(xs) - min(xs) > 0.15  # circles
    assert mite.y < 0.5
    assert shots(created)


def test_ticks_come_up_from_the_bottom_and_fire_once():
    tick = Tick(x=0.2, y=1.2)
    created = run(tick, 5.0)
    assert tick.vy > 0
    assert len(shots(created)) == 1
    assert tick.y > 0.5


def test_sparks_home_in_on_the_player():
    spark = Spark(x=0.5, y=0.5)
    run(spark, 1.0, Entity(x=-0.5, y=0.5))
    assert spark.vx < 0


def test_imps_fire_a_cross_that_turns():
    imp = Imp(x=0.0, y=0.5, fire_cooldown=0.0)
    first = shots(run(imp, DT))
    second = shots(run(imp, Imp.fire_interval))
    assert len(first) == len(second) == 4
    assert (first[0].vx, first[0].vy) != pytest.approx((second[0].vx, second[0].vy))


def test_wisps_blink_out_and_cant_be_hit_while_hidden():
    wisp = Wisp(x=0.0, y=0.7, phase="shown", timer=Wisp.shown_duration)
    fired = shots(run(wisp, Wisp.shown_duration + 0.05))
    assert len(fired) == 1
    assert wisp.phase == "hidden" and wisp.appearance() == "hidden"
    wisp.hit(10.0)
    assert wisp.alive
    x = wisp.x
    run(wisp, Wisp.hidden_duration)
    assert wisp.phase == "shown" and wisp.x != x and wisp.y < 0.7


def test_hornets_zigzag_and_fire_at_each_turn():
    hornet = Hornet(x=0.0, y=0.5)
    directions = set()
    created = []
    for _ in range(90):
        created += hornet.update(DT, TARGET, SCROLL)
        directions.add(hornet.vx > 0)
    assert directions == {True, False}
    assert len(shots(created)) >= 2


def test_albatrosses_weave_and_fire_fans_of_five():
    albatross = Albatross(x=0.0, y=0.5, fire_cooldown=0.0)
    fan = shots(run(albatross, 0.5))
    assert len(fan) == 5
    run(albatross, 1.0)
    assert albatross.x != 0.0


def test_kestrels_swoop_down_then_climb_back_firing_triples():
    kestrel = Kestrel(x=-0.8, y=0.6, vx=0.45, fire_cooldown=0.0)
    created = run(kestrel, 0.5)
    assert kestrel.vy < 0
    assert len(shots(created)) == 3
    run(kestrel, 2.5)
    assert kestrel.vy > 0


def test_javelins_line_up_with_the_player_then_dive():
    javelin = Javelin(x=0.4, y=0.7, phase="aim", timer=Javelin.aim_time)
    run(javelin, 0.2, Entity(x=0.0, y=-0.75))
    assert javelin.vx < 0 and javelin.appearance() == "flash"
    run(javelin, Javelin.aim_time)
    assert javelin.phase == "dive" and javelin.vy == -Javelin.dive_speed


def test_rapiers_streak_down_firing_to_both_sides():
    rapier = Rapier(x=0.0, y=0.5, fire_cooldown=0.0)
    pair = shots(run(rapier, DT))
    assert sorted(shot.vx > 0 for shot in pair) == [False, True]
    assert rapier.vy < -0.8


def test_stalkers_chase_and_fire_only_when_lined_up():
    stalker = Stalker(x=0.4, y=0.5, fire_cooldown=0.0)
    assert not shots(run(stalker, DT, Entity(x=-0.4, y=-0.75)))
    assert stalker.vx < 0
    assert len(shots(run(stalker, DT, Entity(x=0.4, y=-0.75)))) == 2


def test_scrappers_drift_erratically_and_shoot_from_their_turret():
    scrapper = Scrapper(x=0.0, y=0.5, fire_cooldown=0.0)
    created = run(scrapper, 1.6)
    assert shots(created)[0].x == pytest.approx(Scrapper.turret[0])  # off-centre: from the turret
    assert scrapper.x != 0.0


def test_brawlers_fire_heavy_shots_from_their_side_cannon():
    brawler = Brawler(x=0.0, y=0.5, fire_cooldown=0.0)
    (shot,) = shots(run(brawler, DT))
    assert shot.style == "heavy"
    assert shot.x == pytest.approx(Brawler.cannon[0], abs=0.01)


def test_mantas_cross_dropping_shots_from_one_wingtip_then_the_other():
    manta = Manta(x=-0.5, y=0.6, fire_cooldown=0.0)  # holding still, to compare the shots
    first, second = shots(run(manta, 2 * DT + Manta.fire_interval))
    assert abs(first.x - second.x) > manta.width * 0.7  # one wingtip, then the other
    assert first.vx == 0 and first.vy < 0


def test_broadsides_fire_fans_to_both_flanks():
    fan = shots(run(Broadside(x=0.0, y=0.5, vx=0.22, fire_cooldown=0.0), DT))
    assert len(fan) == 6
    assert sum(shot.vx < 0 for shot in fan) == 3


def test_catamarans_hulls_take_turns_firing_snaking_shots():
    catamaran = Catamaran(x=0.0, y=0.5, fire_cooldown=0.0)
    created = run(catamaran, DT + Catamaran.fire_interval)
    first, second = of_type(created, WaveBullet)
    assert first.x == -second.x != 0


def test_outriders_stop_fire_bursts_of_pairs_then_dive_away():
    outrider = Outrider(x=0.0, y=0.55, phase="stay", fire_cooldown=0.0)
    burst = shots(run(outrider, 0.5))
    assert len(burst) == 2 * Outrider.pairs
    run(outrider, Outrider.stay_duration)
    assert outrider.phase == "leave" and outrider.vy < 0


def test_needles_fire_fast_streams_straight_down():
    needle = Needle(x=0.0, y=0.7, phase="stay", fire_cooldown=0.0)
    stream = shots(run(needle, 0.5))
    assert len(stream) == Needle.stream
    assert all(shot.vx == 0 for shot in stream)


def test_harriers_fire_scattered_bursts_at_the_player():
    harrier = Harrier(x=0.0, y=0.6, phase="stay", fire_cooldown=0.0)
    burst = shots(run(harrier, 0.6))
    assert len(burst) == Harrier.burst
    assert len({round(shot.vx, 3) for shot in burst}) > 1


def test_howitzers_lob_shells_that_burst_where_the_player_was():
    howitzer = Howitzer(x=0.0, y=0.75, phase="stay", fire_cooldown=0.0)
    (shell,) = of_type(run(howitzer, DT), ClusterBomb)
    shell.x, shell.y = howitzer.x, howitzer.y  # from where it was fired
    while shell.alive:
        shell.update(DT, TARGET, SCROLL)  # it moves itself
    assert math.hypot(shell.x - TARGET.x, shell.y - TARGET.y) < 0.1


def test_freighters_lay_mines_and_always_drop_a_pickup():
    freighter = Freighter(x=0.0, y=0.5, fire_cooldown=0.0)
    assert of_type(run(freighter, DT), Mine)
    assert Freighter.drop_chance == 1.0


def test_broods_release_pairs_of_sparks():
    sparks = of_type(run(Brood(x=0.0, y=0.5, fire_cooldown=0.0), DT), Spark)
    assert len(sparks) == 2


def test_ramparts_can_only_be_hurt_while_open_and_then_fire_a_wall():
    rampart = Rampart(x=0.0, y=0.5)
    rampart.hit(5.0)
    assert rampart.health == Rampart.health and rampart.appearance() == "armored"
    wall = shots(run(rampart, Rampart.closed_duration + 0.05))
    assert len(wall) == Rampart.wall
    rampart.hit(5.0)
    assert rampart.health == Rampart.health - 5.0


def test_condors_alternate_homing_missiles_and_spreads():
    condor = Condor(x=0.0, y=0.5, fire_cooldown=0.0)
    missiles = of_type(run(condor, DT), HomingMissile)
    assert len(missiles) == 2
    spread = shots(run(condor, Condor.fire_interval + DT))
    assert len(spread) == 7


def test_behemoths_launch_darts_then_fire_rings():
    behemoth = Behemoth(x=0.0, y=0.5, fire_cooldown=0.0)
    assert len(of_type(run(behemoth, DT), Dart)) == 2
    assert len(shots(run(behemoth, Behemoth.fire_interval + DT))) == Behemoth.ring


def test_warhawks_alternate_a_spiral_and_heavy_triples():
    warhawk = Warhawk(x=0.0, y=0.55, phase="stay", fire_cooldown=0.0)
    spiral = shots(run(warhawk, 1.5))
    assert len(spiral) == Warhawk.spiral
    heavy = shots(run(warhawk, Warhawk.fire_interval))
    assert [shot.style for shot in heavy] == ["heavy"] * 3


def test_stormcrows_sweep_streams_of_shots_then_pause():
    stormcrow = Stormcrow(x=0.0, y=0.6, phase="stay")
    sweep = shots(run(stormcrow, Stormcrow.sweep_duration))
    assert len(sweep) > 10
    assert min(shot.vx for shot in sweep) < 0 < max(shot.vx for shot in sweep)
    assert not shots(run(stormcrow, Stormcrow.pause_duration - 0.1))


def test_pincers_charge_then_fire_two_beams_with_a_safe_gap():
    pincer = Pincer(x=0.0, y=0.55, phase="stay", fire_cooldown=0.0)
    run(pincer, DT)
    assert pincer.appearance() == "flash"
    beams = shots(run(pincer, Pincer.charge_duration))
    assert len(beams) == 2 and all(beam.style == "beam" and beam.pierces for beam in beams)
    assert beams[0].x - pincer.x == -(beams[1].x - pincer.x) != 0  # one from each prong


def test_hoverers_leave_after_their_stay():
    needle = Needle(x=0.0, y=0.7, phase="stay", fire_cooldown=99.0)
    run(needle, Needle.stay_duration + 0.1)
    assert needle.phase == "leave" and needle.vy > 0


def test_every_fleet_enemy_is_in_the_models_and_nothing_is_left_out():
    assert set(FLEET) == {kind.drawing for kind in FLEET.values()}
    assert all(issubclass(kind, Enemy) and not kind.ground for kind in FLEET.values())
    assert fleet.VOXEL == config.MODEL_VOXEL


def test_a_hoverer_does_nothing_while_it_stays_unless_told_to():
    hoverer = fleet.Hoverer(x=0.0, y=0.5, phase="stay")
    assert hoverer.behave(0.1, Entity(), 0.0) == []
    assert hoverer.phase == "stay"
