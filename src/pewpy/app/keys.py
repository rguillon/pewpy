"""The keyboard: flying and firing, switching weapons, and the menus."""

from typing import cast

from panda3d.core import ButtonThrower, ModifierButtons

from pewpy.app.screens import Screens
from pewpy.audio.sound import Audio
from pewpy.game.controls import Controls
from pewpy.game.states import State

MOVE_KEYS = {
    "arrow_left": (-1, 0),
    "arrow_right": (1, 0),
    "arrow_up": (0, 1),
    "arrow_down": (0, -1),
}
FIRE_KEY = "space"
SWITCH_WEAPON_KEY = "shift"
# Menus: Up/Down move the highlight, Enter chooses, Escape goes back (and pauses while playing).
MENU_MOVES = {"arrow_up": -1, "arrow_down": 1}
MENU_CHOOSE_KEY = "enter"
BACK_KEY = "escape"
MUSIC_KEY = "m"  # music on and off


class Keys(Screens):
    """The keys and what they do."""

    audio: Audio  # set up by Sound._setup_audio

    def _setup_keys(self) -> None:
        self.keys_down: set[str] = set()
        for key in (*MOVE_KEYS, FIRE_KEY):
            # One handler per key (Panda3D keeps only the last one): the arrows also move menu highlights.
            self.accept(key, self._on_key, [key])
            self.accept(f"{key}-up", self.keys_down.discard, [key])
        self.accept(SWITCH_WEAPON_KEY, self._switch_weapon)
        self.accept(MENU_CHOOSE_KEY, self._on_choose)
        self.accept(BACK_KEY, self._on_back)
        self._disable_modifier_keys()

    def _disable_modifier_keys(self) -> None:
        # By default Panda3D sends "shift-space" instead of "space" while Shift is held, which would stop
        # firing when switching weapons. Treat Shift like any other key.
        if self.mouseWatcher is None:  # no window, e.g. offscreen
            return
        for path in self.mouseWatcher.findAllMatches("**/+ButtonThrower"):
            cast("ButtonThrower", path.node()).setModifierButtons(ModifierButtons())
        self.mouseWatcherNode.setModifierButtons(ModifierButtons())

    def _switch_weapon(self) -> None:
        if self.world is not None and self.states.state is State.PLAYING:
            self.world.arsenal.switch()
            self.audio.play("switch")

    def _on_key(self, key: str) -> None:
        self.keys_down.add(key)
        menu = self.menu_view.menu
        if menu is not None and key in MENU_MOVES:
            menu.move(MENU_MOVES[key])
            self.audio.play("menu_move")
            self.menu_view.refresh()
            self._highlight_ship()
            if self.states.state is State.LEVEL_SELECT:
                self._preview_level(menu)

    def _on_choose(self) -> None:
        if self.menu_view.menu is not None:
            self.audio.play("menu_choose")
            self.menu_view.menu.choose()

    def _on_back(self) -> None:
        if self.menu_view.menu is not None:
            self.audio.play("menu_back")
            self.menu_view.menu.go_back()
        elif self.states.state is State.PLAYING:
            self.audio.play("menu_back")
            self.states.transition(State.PAUSED)

    def _controls(self) -> Controls:
        return Controls(
            move_x=sum(MOVE_KEYS[key][0] for key in self.keys_down if key in MOVE_KEYS),
            move_y=sum(MOVE_KEYS[key][1] for key in self.keys_down if key in MOVE_KEYS),
            fire=FIRE_KEY in self.keys_down,
        )
