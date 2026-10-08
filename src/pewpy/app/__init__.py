"""Panda3D application: window, camera, input and rendering.

PewPewApp is built in layers, each adding one concern in its own module, each layer on top of the one before:
window.py (the window, camera and lights), entity_models.py (the models of what's in play), hud.py, drawing.py
(what's in play, each frame; bullets.py: how bullets look), screens.py (the menus and screens), keys.py, sound.py,
dev.py (the Dev menu's model and music browsers), backgrounds.py (its backgrounds browser), ai_playing.py (the AI
playing screen), screenshots.py (the Dev menu's screenshots) and parts.py (its parts browser). This module puts them
together and runs the frames.
"""

import random
from enum import Enum
from typing import TYPE_CHECKING

from direct.task.Task import Task
from panda3d.core import NodePath, loadPrcFileData

from pewpy import config
from pewpy.app.entity_models import fitted_model
from pewpy.app.parts import Parts
from pewpy.app.window import GAME_ASPECT, letterbox
from pewpy.audio.cues import event_sounds
from pewpy.game.controls import Controls
from pewpy.game.level import load_worlds
from pewpy.game.player import DEFAULT_SHIP
from pewpy.game.states import State, StateMachine
from pewpy.game.world import World
from pewpy.graphics.effects.system import ParticleSystem
from pewpy.graphics.effects.view import EffectsView
from pewpy.scenery.background import Scenery
from pewpy.scenery.background.view import BackgroundView, CameraView
from pewpy.ui.ai_panel import AIPanel
from pewpy.ui.level_preview import LevelPreview
from pewpy.ui.menu_view import MenuView

if TYPE_CHECKING:
    from pewpy.game.entities import Entity
    from pewpy.ui.ship_select_view import ShipSelectView

# Particles keep moving after the last explosion of a level or a life (not in pause or the menus).
EFFECTS_RUN_IN: frozenset[Enum] = frozenset({State.PLAYING, State.GAME_OVER, State.LEVEL_COMPLETE, State.AI_PLAYING})


class PewPewApp(Parts):
    """The game."""

    def __init__(self) -> None:
        """Set the window up, then build the camera, the lights, the drawings, the models and the levels."""
        loadPrcFileData(
            "",
            f"""
            window-title {config.WINDOW_TITLE}
            win-size {config.WINDOW_WIDTH} {config.WINDOW_HEIGHT}
            sync-video true
            textures-power-2 none
            """,
        )
        super().__init__()
        self.disableMouse()
        self._setup_letterbox()
        # Set up the 2D overlay (menus, HUD) the way a window does when it opens or resizes, so it's the same
        # without a window (tests, screenshots): the game area is 2 units wide, its anchors on its edges.
        self.adjustWindowAspectRatio(self.getAspectRatio())
        self._setup_camera()
        self._setup_lights()
        self._setup_font()
        self._setup_drawing()
        self._build_models()
        self.ship_key = DEFAULT_SHIP  # the player's ship (picked on the ship selection screen)
        self.ship_select: ShipSelectView | None = None

        self.worlds = load_worlds()
        self.levels = [level for world in self.worlds for level in world.levels]  # in playing order
        # For each level: (its world's index, its number in the world, from 1).
        self.places = [(w, n + 1) for w, world in enumerate(self.worlds) for n in range(len(world.levels))]
        self.level_index = 0
        self.world_index = 0  # the world picked in the world select
        self.world: World | None = None
        self.nodes: dict[Entity, NodePath] = {}
        self.flames: dict[Entity, list[tuple[NodePath, float]]] = {}  # engine flames and their steady length
        self.camera_view = CameraView(self.cam, self.cam.node().getLens(), self.render)
        self.background = BackgroundView(Scenery("space", self.camera_view), self.render)  # until the menus' ground
        self.menu_level = None
        self.menu_rng = random.Random()
        self.effects = ParticleSystem()
        self.effects_view = EffectsView(self.effects, self.render, self.cam.node().getLens())

        self._setup_keys()
        self._setup_audio()

        self.menu_view = MenuView(self.aspect2d)
        self._setup_hud()
        # The level select's window on the highlighted level.
        self.level_preview = LevelPreview(self.scene_buffer, self.cam, self.render, self.aspect2d)
        self.ai_panel = AIPanel(self.aspect2d)

        self.states = StateMachine(on_change=self._on_state_change)
        self._on_state_change(self.states.state, self.states.state)
        self.taskMgr.add(self._update, "update")

    def _frame_time(self) -> float:
        """Seconds since the last frame (at most 0.1: no huge steps after a stall)."""
        return min(self.clock.getDt(), 0.1)

    def _update(self, task: Task) -> int:  # noqa: ARG002 - a Panda3D task
        dt = self._frame_time()
        world = self.world
        if world is not None and self.states.state is State.PLAYING:
            self._play(world, self._controls(), dt)
            if world.game_over:
                self.states.transition(State.GAME_OVER)
            elif world.completed:
                self.states.transition(State.LEVEL_COMPLETE)
        elif world is not None and self.states.state is State.AI_PLAYING:
            self._play(world, self.pilot.fly(world), dt)
            self._follow_ai(world)
        if self.states.state in EFFECTS_RUN_IN:
            self.effects.update(dt)
        if self.ship_select:
            self.ship_select.update(dt)
        if self.browser_view:
            self.browser_view.update(dt)
        if world is None and self.menu_level is not None:  # the menus' ground scrolls by
            self.background.scenery.update(dt, self.menu_level.scroll_speed)
        self._update_music_view()
        self.level_preview.update(dt)
        self._update_audio(dt)
        self._sync_nodes()
        self._update_hud()
        self._update_fps()
        return Task.cont

    def _play(self, world: World, controls: Controls, dt: float) -> None:
        """One step of a level: the world, its effects, sounds and scenery."""
        world.update(dt, controls)
        self._show_events(world.events, dt)
        self.audio.play_all(event_sounds(world.events))
        self.effects.set_lasers(self._laser_glows(world), dt)
        self.background.scenery.update(dt, world.level.scroll_speed)


def main() -> None:
    """Run the game."""
    PewPewApp().run()


__all__ = ["EFFECTS_RUN_IN", "GAME_ASPECT", "PewPewApp", "fitted_model", "letterbox", "main"]
