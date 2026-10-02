import pytest

from pewpy import config
from pewpy.game.enemies.enemy import Enemy, make
from pewpy.game.entities import Bullet, Pickup
from pewpy.game.level import Level, Wave
from pewpy.game.player import Player
from pewpy.game.weapons.player.arsenal import Arsenal
from pewpy.game.weapons.player.secondary import SECONDARY_GUNS, SECONDARY_LETTERS, SECONDARY_WEAPONS, SecondaryWeapon
from pewpy.game.world import Controls, World

TURRET = SECONDARY_GUNS["turret"]
LIGHTNING = SECONDARY_GUNS["lightning"]
DT = 1 / 60
QUIET_LEVEL = Level(name="quiet", scroll_speed=0.2, waves=(Wave(time=1000.0),))


def armed_world(kind: str | None) -> World:
    arsenal = Arsenal(secondary=SecondaryWeapon(kind) if kind else None)
    return World(QUIET_LEVEL, seed=0, arsenal=arsenal)


def still_drone(x: float, y: float, health: float = 100.0) -> Enemy:
    drone = make("drone", x, y)
    drone.vy, drone.fire_cooldown, drone.health = 0.0, 1000.0, health
    return drone


def run(world: World, seconds: float) -> None:
    for _ in range(round(seconds / DT)):
        world.update(DT, Controls())


def test_the_secondary_weapons_are_read():
    assert SECONDARY_WEAPONS == ("turret", "lightning")
    assert set(SECONDARY_LETTERS) == set(SECONDARY_WEAPONS)


def test_turret_shoots_the_nearest_enemy_on_its_own():
    turret = SecondaryWeapon("turret")
    ship = Player()
    near, far = still_drone(ship.x + 0.3, ship.y + 0.4), still_drone(ship.x, ship.y + 1.2)
    shots, struck = turret.fire(DT, ship, [far, near])
    assert struck == []
    assert len(shots) == 1
    shot = shots[0]
    assert shot.damage == TURRET.damage
    assert not shot.hostile
    assert (shot.vx, shot.vy) == pytest.approx((0.6 * 2.5, 0.8 * 2.5))  # toward `near`: (0.3, 0.4) / 0.5
    assert (turret.aim_x, turret.aim_y) == pytest.approx((0.6, 0.8))


def test_turret_fire_rate_and_no_target_no_shot():
    turret = SecondaryWeapon("turret")
    ship = Player()
    assert turret.fire(DT, ship, []) == ([], [])
    target = still_drone(0.0, 0.5)
    shots = sum(len(turret.fire(DT, ship, [target])[0]) for _ in range(round(2.0 / DT)))
    assert abs(shots - 2 * (1 / TURRET.interval)) <= 1


def test_turret_kills_enemies_in_the_world():
    world = armed_world("turret")
    drone = still_drone(world.player.x - 0.4, world.player.y + 0.6, health=1.0)
    world.enemies.append(drone)
    run(world, 1.0)  # no Fire: it shoots on its own
    assert not drone.alive
    assert world.score == drone.points


def test_lightning_chains_from_enemy_to_enemy():
    lightning = SecondaryWeapon("lightning")
    ship = Player(x=0.0, y=0.0)
    step = LIGHTNING.chain_jump * 0.9
    line = [still_drone(LIGHTNING.chain_range * 0.9 + i * step, 0.0) for i in range(LIGHTNING.chain_count + 1)]
    out_of_reach = still_drone(-LIGHTNING.chain_range * 1.1, 0.0)
    shots, struck = lightning.fire(DT, ship, [*reversed(line), out_of_reach])
    assert shots == []
    assert struck == line[: LIGHTNING.chain_count]  # nearest first, then jumping, up to the chain's length
    assert lightning.state.cooldown == pytest.approx(LIGHTNING.interval)
    assert lightning.fire(DT, ship, line) == ([], [])  # recharging


def test_lightning_needs_an_enemy_in_range():
    lightning = SecondaryWeapon("lightning")
    ship = Player(x=0.0, y=0.0)
    assert lightning.fire(DT, ship, [still_drone(LIGHTNING.chain_range * 1.1, 0.0)]) == ([], [])
    assert lightning.state.cooldown == 0.0


def test_lightning_damages_enemies_and_shows_a_bolt():
    world = armed_world("lightning")
    drone = still_drone(world.player.x, world.player.y + 0.4)
    world.enemies.append(drone)
    world.update(DT, Controls())
    assert drone.health == pytest.approx(100.0 - (LIGHTNING.damage or 0))
    assert "zap" in [event.kind for event in world.events]
    assert world.bolt[-1] == (drone.x, drone.y)
    run(world, LIGHTNING.flash + DT)
    assert world.bolt == []


def test_picking_up_a_secondary_weapon_replaces_the_one_carried():
    world = armed_world("turret")
    world.pickups.append(Pickup(x=world.player.x, y=world.player.y, kind="lightning"))
    world.update(DT, Controls())
    assert world.arsenal.secondary is not None
    assert world.arsenal.secondary.kind == "lightning"
    assert [event.source for event in world.events if event.kind == "pickup"] == ["lightning"]


@pytest.mark.parametrize("kind", ["turret", "lightning"])
def test_a_shot_takes_the_secondary_weapon_instead_of_health(kind):
    world = armed_world(kind)
    player = world.player
    world.enemy_bullets.append(Bullet(x=player.x, y=player.y, vy=0.0, damage=1.0, hostile=True))
    world.update(DT, Controls())
    assert player.health == world.ship.health
    assert world.arsenal.secondary is None
    assert player.invulnerable
    events = [(event.kind, event.source) for event in world.events]
    assert ("disarmed", kind) in events
    assert ("hurt", "") not in events

    run(world, config.PLAYER_INVULNERABILITY_TIME + DT)
    world.enemy_bullets.append(Bullet(x=player.x, y=player.y, vy=0.0, damage=1.0, hostile=True))
    world.update(DT, Controls())
    assert player.health == world.ship.health - 1.0  # nothing left to lose: now it hurts


def test_ramming_takes_the_secondary_weapon_instead_of_health():
    world = armed_world("turret")
    world.enemies.append(still_drone(world.player.x, world.player.y, health=1000.0))
    world.update(DT, Controls())
    assert world.player.health == world.ship.health
    assert world.arsenal.secondary is None


def test_losing_a_life_loses_the_secondary_weapon():
    world = armed_world("lightning")
    world.player.health = 0.0
    world.update(DT, Controls())
    assert world.lives == config.PLAYER_LIVES - 1
    assert world.arsenal.secondary is None


def test_the_secondary_weapon_goes_on_to_the_next_level():
    world = armed_world("turret")
    next_level = World(QUIET_LEVEL, seed=0, arsenal=world.arsenal)
    assert next_level.arsenal.secondary is not None
    assert next_level.arsenal.secondary.kind == "turret"
