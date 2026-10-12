"""Driving the game app like a player does: keys, menus, frames."""

from panda3d.core import NodePath

from pewpy.app import PewPewApp, keys
from pewpy.game.entities import Entity
from pewpy.game.player import SHIPS
from pewpy.game.states import State
from pewpy.game.world import World
from pewpy.ui.menu import Menu


def frames(app: PewPewApp, count: int = 1) -> None:
    for _ in range(count):
        app.taskMgr.step()


def menu(app: PewPewApp) -> Menu:
    assert app.menu_view.menu is not None
    return app.menu_view.menu


def world(app: PewPewApp) -> World:
    assert app.world is not None
    return app.world


def labels(app: PewPewApp) -> list[str]:
    return [item.label for item in menu(app).items]


def press(app: PewPewApp, key: str) -> None:
    app.messenger.send(key)


def choose(app: PewPewApp, label: str) -> None:
    menu(app).selected = labels(app).index(label)
    press(app, keys.MENU_CHOOSE_KEY)


def start_level(app: PewPewApp, index: int = 0) -> None:
    choose(app, "Start")
    choose(app, SHIPS[app.ship_key].name.title())
    world_index, number = app.places[index]
    choose(app, f"{world_index + 1}. {app.worlds[world_index].name}")
    menu(app).selected = number - 1
    press(app, keys.MENU_CHOOSE_KEY)
    world(app).arrival_time = 0.0  # skip the ship flying in


def complete(app: PewPewApp) -> None:
    world(app).pending_spawns = []
    world(app).enemies = []
    frames(app)
    assert app.states.state is State.PLAYING  # the ship flies away first
    world(app).player.y = world(app).view_top + 1.0
    frames(app)


def play(app: PewPewApp, index: int = 0) -> World:
    app.states.transition(State.SHIP_SELECT)
    app.states.transition(State.WORLD_SELECT)
    app.states.transition(State.LEVEL_SELECT)
    app._start_level(index)
    assert app.world is not None
    app.world.pending_spawns = []  # only what the test puts in
    return app.world


def node(app: PewPewApp, entity: Entity) -> NodePath:
    app._sync_nodes()
    return app.nodes[entity]
