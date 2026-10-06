"""The game with the dev tools' screens (`make dev`).

The main menu also opens the Models, Bosses, Enemy candidates, Player candidates, Boss candidates and Prop candidates
screens (models on
show, to work on them, model_screens.py) and the AI learning, AI rating and AI playing screens (ai_screens.py).
"""

from enum import Enum
from typing import TYPE_CHECKING

from direct.task.Task import Task

from pewpy.app import EFFECTS_RUN_IN
from pewpy.game.states import State
from pewpy.tools.dev.app.ai_screens import AI_STATES, AIGame, AIScreens
from pewpy.tools.dev.app.model_screens import SHOWCASE_STATES
from pewpy.tools.dev.states import DEV_TRANSITIONS, DevState
from pewpy.tools.dev.ui.ai_panel import AIPanel
from pewpy.ui.menu import Menu, MenuItem

if TYPE_CHECKING:
    from pewpy.tools.ai.pilot import Pilot
    from pewpy.tools.ai.sessions import Session
    from pewpy.ui.showcase import ModelShowcase


class DevApp(AIScreens):
    """The game with the dev tools' screens."""

    state_transitions = DEV_TRANSITIONS
    effects_run_in = EFFECTS_RUN_IN | {DevState.AI_LEARNING, DevState.AI_PLAYING}

    def _setup_screens(self) -> None:
        self.showcase: ModelShowcase | None = None
        self.showcase_page = 0  # the page shown on the Models or Bosses screen
        self.blinking = []  # the bosses' parts on show, blinking
        self.ai_session: Session | None = None  # learning or rating in the background, on the AI screens
        self.stopped_ai: list[Session] = []  # stopped, still finishing what they were doing
        self.pilot: Pilot | None = None  # the AI flying the ship on screen
        self.ai_watching = ""  # what the AI on screen plays
        self.ai_game = AIGame()  # the AI playing the game, on the AI playing screen
        self.ai_panel = AIPanel(self.aspect2d)

    def _main_menu_items(self) -> list[MenuItem]:
        go = self._go
        return [
            *super()._main_menu_items(),
            MenuItem("Models", go(DevState.MODELS)),
            MenuItem("Bosses", go(DevState.BOSSES)),
            MenuItem("Enemy candidates", go(DevState.CANDIDATES)),
            MenuItem("Player candidates", go(DevState.PLAYER_CANDIDATES)),
            MenuItem("Boss candidates", go(DevState.BOSS_CANDIDATES)),
            MenuItem("Prop candidates", go(DevState.PROP_CANDIDATES)),
            MenuItem("AI learning", go(DevState.AI_LEARNING)),
            MenuItem("AI rating", go(DevState.AI_RATING)),
            MenuItem("AI playing", go(DevState.AI_PLAYING)),
        ]

    def _menu(self, state: Enum) -> Menu | None:
        if state in SHOWCASE_STATES:
            return self._models_menu()
        return super()._menu(state)

    def _on_state_change(self, previous: Enum, current: Enum) -> None:
        if current in SHOWCASE_STATES:
            self.showcase_page = 0  # before the menu: its title shows the page
        super()._on_state_change(previous, current)
        if current in SHOWCASE_STATES:
            self._show_showcase()
            self.background.root.hide()  # a plain dark background, to look at the models
        elif self.showcase:
            self.showcase.destroy()
            self.showcase = None
            self.background.root.show()
        self._switch_ai(previous, current)

    def _update(self, task: Task) -> int:
        dt = self._frame_time()
        if self.states.state in AI_STATES:
            self._update_ai(dt)
        if self.showcase:
            self.showcase.update(dt)
            self.blink_parts()
        return super()._update(task)

    def _on_back(self) -> None:
        if self.menu_view.menu is None and self.states.state in AI_STATES:
            self.audio.play("menu_back")
            self.states.transition(State.MAIN_MENU)
            return
        super()._on_back()

    def finalizeExit(self) -> None:  # noqa: N802 - overrides ShowBase
        """Stop the AI (its brains are saved as it stops) before the window goes."""
        self._stop_ai()
        self._finish_stopped_ai(wait=30.0)  # the brains are saved as it stops
        super().finalizeExit()


def main() -> None:
    """Run the game with the dev tools' screens."""
    DevApp().run()
