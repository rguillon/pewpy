"""The HUD: score, lives, health, weapon levels, the boss's health bar, and the frames per second."""

from typing import Literal

from direct.gui.OnscreenText import OnscreenText
from panda3d.core import CardMaker, NodePath, TextNode

from pewpy import config
from pewpy.app.entity_models import SECONDARY_COLORS, WEAPON_COLORS, EntityModels
from pewpy.app.window import Color
from pewpy.game.weapons.player.arsenal import LETTERS, WEAPONS, Arsenal
from pewpy.game.weapons.player.secondary import SECONDARY_LETTERS
from pewpy.game.world import World

TextAlign = Literal[0, 1, 2, 3, 4, 5]  # TextNode.ALeft, ARight, ACenter...
HUD_DIM_COLOR: Color = (0.5, 0.5, 0.55, 1)
HUD_MARGIN = 0.025  # space between the HUD and the edges of the game area (aspect2d units: the width is 2)
HUD_TEXT = 0.06  # score and lives
HUD_SMALL = 0.055  # weapon levels (the selected one is bigger)
FPS_SCALE = 0.045
FPS_REFRESH = 0.5  # seconds between two updates of the frames per second
WEAPON_SPACING = 0.15
HEALTH_BAR_WIDTH = 0.5
HEALTH_BAR_HEIGHT = 0.025
BOSS_BAR_WIDTH = 1.1  # at the top edge, with the boss's name under it
BOSS_BAR_HEIGHT = 0.025


class Hud(EntityModels):
    """The HUD over the game, and the frames per second over every screen."""

    world: World | None

    def _setup_hud(self) -> None:
        # All along the bottom edge: score bottom-left, the weapon levels over the health bar in the middle, lives
        # bottom-right. Each part hangs on one of Panda3D's anchors (the game area's real edges, whatever the
        # window's shape), a few hundredths from the edge.
        left = self.a2dBottomLeft.attachNewNode("hud_left")
        center = self.a2dBottomCenter.attachNewNode("hud_center")
        right = self.a2dBottomRight.attachNewNode("hud_right")
        self.hud_parts = [left, center, right]
        baseline = HUD_MARGIN + 0.01  # letters sit on it, their bottoms reach down to the margin
        self.score_text = self._hud_text(left, HUD_MARGIN, baseline, TextNode.ALeft)
        self.lives_text = self._hud_text(right, -HUD_MARGIN, baseline, TextNode.ARight)
        # Frames per second, top-right on every screen (not part of the in-game HUD, which menus hide).
        fps_corner = self.a2dTopRight.attachNewNode("fps")
        top_line = -HUD_MARGIN - FPS_SCALE * 0.8  # the letters' tops reach up to the margin
        self.fps_text = self._hud_text(fps_corner, -HUD_MARGIN, top_line, TextNode.ARight, FPS_SCALE, HUD_DIM_COLOR)
        self._fps_shown = -1
        self._fps_next = 1.0  # the clock averages over the last second: nothing to show before
        if not config.SHOW_FPS:
            fps_corner.hide()

        maker = CardMaker("health")
        maker.setFrame(0, HEALTH_BAR_WIDTH, 0, HEALTH_BAR_HEIGHT)
        bar_pos = (-HEALTH_BAR_WIDTH / 2, 0, HUD_MARGIN)
        background = center.attachNewNode(maker.generate())
        background.setPos(*bar_pos)
        background.setColor(0.3, 0.1, 0.1, 1)
        self.health_fill = center.attachNewNode(maker.generate())
        self.health_fill.setPos(*bar_pos)
        self.health_fill.setColor(0.2, 0.9, 0.3, 1)

        # Weapon levels just over the health bar, e.g. "B2  L1  M3"; the selected weapon is highlighted.
        above_bar = HUD_MARGIN + HEALTH_BAR_HEIGHT + 0.02
        self.weapon_texts = {
            weapon: self._hud_text(center, x, above_bar, TextNode.ACenter, HUD_SMALL, HUD_DIM_COLOR)
            for weapon, x in zip(WEAPONS, (-WEAPON_SPACING, 0.0, WEAPON_SPACING), strict=True)
        }
        # The secondary weapon after them, if the ship carries one: "+T" or "+Z".
        self.secondary_text = self._hud_text(center, 2 * WEAPON_SPACING, above_bar, TextNode.ACenter, HUD_SMALL * 1.25)

        # The boss's health bar at the top edge, its name under it: only while a boss is on screen.
        self.boss_hud = self.a2dTopCenter.attachNewNode("hud_boss")
        maker = CardMaker("boss_health")
        maker.setFrame(0, BOSS_BAR_WIDTH, -BOSS_BAR_HEIGHT, 0)
        background = self.boss_hud.attachNewNode(maker.generate())
        background.setPos(-BOSS_BAR_WIDTH / 2, 0, -HUD_MARGIN)
        background.setColor(0.25, 0.07, 0.05, 1)
        self.boss_fill = self.boss_hud.attachNewNode(maker.generate())
        self.boss_fill.setPos(-BOSS_BAR_WIDTH / 2, 0, -HUD_MARGIN)
        self.boss_fill.setColor(1.0, 0.4, 0.15, 1)
        below_bar = -HUD_MARGIN - BOSS_BAR_HEIGHT - HUD_SMALL
        self.boss_name = self._hud_text(self.boss_hud, 0.0, below_bar, TextNode.ACenter, HUD_SMALL, (1, 0.75, 0.6, 1))
        self.boss_hud.hide()
        # What's currently shown, so _update_hud only touches a text (Panda3D rebuilds its geometry each time)
        # when its value actually changed, instead of every single frame.
        self._hud_score: int | None = None
        self._hud_lives: int | None = None
        self._hud_weapon_state: dict[str, tuple[int, bool]] = {}
        self._hud_secondary: str | None = None
        self._hud_boss_name: str | None = None
        self._hud_boss_visible = False

    def _hud_text(
        self,
        parent: NodePath,
        x: float,
        z: float,
        align: TextAlign,
        scale: float = HUD_TEXT,
        color: Color = (1, 1, 1, 1),
    ) -> OnscreenText:
        return OnscreenText(pos=(x, z), align=align, scale=scale, fg=color, mayChange=True, parent=parent)

    def _show_hud(self, visible: bool) -> None:
        for part in self.hud_parts:
            part.show() if visible else part.hide()
        if not visible:
            self.boss_hud.hide()

    def _update_fps(self) -> None:
        """Averaged over the last second, rewritten twice a second at most (setText rebuilds the text)."""
        now = self.clock.getFrameTime()
        if not config.SHOW_FPS or now < self._fps_next:
            return
        self._fps_next = now + FPS_REFRESH
        fps = round(self.clock.getAverageFrameRate())
        if fps != self._fps_shown:
            self._fps_shown = fps
            self.fps_text.setText(f"{fps} FPS")

    def _update_hud(self) -> None:
        if self.world is None:
            return
        if self.world.score != self._hud_score:
            self._hud_score = self.world.score
            self.score_text.setText(f"Score {self.world.score}")
        if self.world.lives != self._hud_lives:
            self._hud_lives = self.world.lives
            self.lives_text.setText(f"Lives {self.world.lives}")
        fraction = max(self.world.player.health, 0) / self.world.ship.health
        self.health_fill.setSx(max(fraction, 0.001))  # a zero scale makes Panda3D print warnings
        self._update_weapons_hud(self.world.arsenal)
        boss = self.world.boss
        if boss is None or boss.y - boss.height / 2 > self.world.view_top:  # none, or still above the screen
            if self._hud_boss_visible:
                self.boss_hud.hide()
                self._hud_boss_visible = False
            return
        if not self._hud_boss_visible:
            self.boss_hud.show()
            self._hud_boss_visible = True
        if boss.spec.name != self._hud_boss_name:
            self._hud_boss_name = boss.spec.name
            self.boss_name.setText(boss.spec.name)
        self.boss_fill.setSx(max(boss.health_fraction, 0.001))

    def _update_weapons_hud(self, arsenal: Arsenal) -> None:
        for weapon, text in self.weapon_texts.items():
            selected = weapon == arsenal.selected
            state = (arsenal.levels[weapon], selected)
            if self._hud_weapon_state.get(weapon) == state:
                continue  # setText/setFg/setTextScale rebuild the text's geometry: skip when nothing changed
            self._hud_weapon_state[weapon] = state
            text.setText(f"{LETTERS[weapon]}{arsenal.levels[weapon]}")
            text.setFg(WEAPON_COLORS[weapon] if selected else HUD_DIM_COLOR)
            text.setTextScale(HUD_SMALL * 1.25 if selected else HUD_SMALL)
        secondary = arsenal.secondary.kind if arsenal.secondary else None
        if secondary != self._hud_secondary:
            self._hud_secondary = secondary
            self.secondary_text.setText(f"+{SECONDARY_LETTERS[secondary]}" if secondary else "")
            if secondary:
                self.secondary_text.setFg(SECONDARY_COLORS[secondary])
