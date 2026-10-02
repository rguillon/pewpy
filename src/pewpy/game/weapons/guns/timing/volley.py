"""Firing every `interval`, `volley` shots in a row: the countdown and the volleys every way of firing shares."""

from pewpy.game.entities import Entity
from pewpy.game.weapons.guns.gun import Gun
from pewpy.game.weapons.guns.laser import LASER_WARNING, laser_beams
from pewpy.game.weapons.guns.patterns import fire
from pewpy.game.weapons.guns.shooter import Shooter
from pewpy.game.weapons.guns.state import GunState


def reloaded(gun: Gun, state: GunState, shooter: Shooter, dt: float) -> bool:
    """Count down to the next shot; True when it's time to fire."""
    state.cooldown -= dt
    if gun.reload == "clamp" or not shooter.trigger:
        state.cooldown = max(state.cooldown, 0.0)
    if not shooter.trigger or state.cooldown > 0:
        return False
    if gun.off_screen == "skip" and not shooter.on_screen:
        state.cooldown = gun.interval
        return False
    if gun.off_screen == "hold" and not shooter.on_screen:
        return False
    target = shooter.target
    if (gun.needs_target and target is None) or (
        gun.aligned and target and abs(target.x - shooter.piece.x) > gun.aligned
    ):
        return False
    state.cooldown = gun.interval if gun.reload == "reset" else state.cooldown + gun.interval
    return True


def start_volley(gun: Gun, state: GunState) -> Gun:
    """Start the next volley (of the next gun of the sequence, if it has one); return its pattern."""
    item = gun.sequence[state.shots % len(gun.sequence)] if gun.sequence else gun
    state.item = item
    state.shots += 1
    state.volley_left, state.volley_timer, state.volley_index = item.volley, 0.0, 0
    return item


def volley(state: GunState, shooter: Shooter, dt: float) -> list[Entity]:
    """Fire the volley under way: its next shot, when it's time."""
    item = state.item
    if item is None or state.volley_left == 0:
        return []
    state.volley_timer -= dt
    if state.volley_timer > 0:
        return []
    state.volley_left -= 1
    state.volley_timer = item.gap
    return shoot(item, state, shooter)


def shoot(item: Gun, state: GunState, shooter: Shooter) -> list[Entity]:
    """Fire the next shot of the volley under way."""
    if state.volley_left == 0:
        state.volleys += 1
    if item.pattern == "laser":
        state.charge = LASER_WARNING
        return list(laser_beams(item, shooter.piece, warning=True))
    shots = fire(item, shooter, state)
    state.volley_index += 1
    state.turned += item.turn
    return shots
