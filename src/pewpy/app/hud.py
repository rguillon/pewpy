"""The HUD: score, lives, health, weapon levels, the boss's health bar, and the frames per second.

The in-game part looks like a cockpit's instrument panels along the bottom edge (see pewpy.ui.panel).
"""

import math

from direct.gui.OnscreenText import OnscreenText
from panda3d.core import NodePath, TextNode

from pewpy import config
from pewpy.app.entity_models import SECONDARY_COLORS, WEAPON_COLORS, EntityModels
from pewpy.app.window import Color
from pewpy.game.weapons.player.arsenal import LETTERS, MAX_LEVEL, WEAPONS, Arsenal
from pewpy.game.weapons.player.secondary import SECONDARY_LETTERS
from pewpy.game.world import World
from pewpy.ui import panel
from pewpy.ui.panel import AMBER, AMBER_GHOST, TextAlign

HUD_DIM_COLOR: Color = (0.5, 0.5, 0.55, 1)
HUD_MARGIN = 0.025  # space between the frames per second and the edges of the game area (aspect2d units)
HUD_SMALL = 0.055  # the boss's name
FPS_SCALE = 0.045
FPS_REFRESH = 0.5  # seconds between two updates of the frames per second

# The panels: score bottom-left, weapons over the hull gauge in the middle, lives bottom-right.
PANEL_MARGIN = 0.012  # between the panels and the edges of the game area
PANEL_HEIGHT = 0.13
SIDE_PANEL_WIDTH = 0.48
CENTER_PANEL_WIDTH = 0.8
PANEL_PADDING = 0.05  # from a plate's sides to what's on it (its screws are in the corners)
LABEL_GAP = 0.04  # from a plate's top to its label under it
READOUT_SCALE = 0.042
SCORE_DIGITS = 7
READOUT_INSET = 0.012  # from a display's edge to its readout, and from a readout's to the lamps
READOUT_BOTTOM, READOUT_TOP = 0.022, 0.072  # the display a readout sits in
READOUT_TEXT_Z = 0.033  # where the readout's own text sits in it
LIVES_DIGITS = 9  # the most lives shown as a number (past it the lamps alone count)
LAMP_ON: Color = (0.35, 1.0, 0.45, 1)  # a life
LAMP_OFF: Color = (0.06, 0.12, 0.07, 1)
LAMP_SIZE = 0.02
LAMP_STEP = 0.032
LAMP_BOTTOM = 0.037
TILE_WIDTH = 0.15  # a weapon's annunciator: its letter, its level beside it, lit when it's the selected weapon
TILE_GAP = 0.025
TILE_COUNT = len(WEAPONS) + 1  # a tile per weapon, then the secondary weapon's
TILE_BOTTOM, TILE_TOP = 0.055, 0.11
TILE_LETTER = 0.042
TILE_LETTER_OFFSET = 0.36  # of the letter's own scale, from the tile's middle down to the letter's middle
TILE_LIT_ALPHA = 0.22  # how transparent a selected weapon's tile's light is
AUX_SCALE = 0.024  # the "AUX" word beside the secondary weapon's letter
AUX_DROP = 0.008  # from the tile's middle down to the "AUX" word's middle
AUX_GAP = 0.002  # from the hull label to the gauge under it
PIP_WIDTH, PIP_GAP = 0.011, 0.006  # a weapon's level: MAX_LEVEL pips...
PIP_HEIGHT = 0.022
PIPS_LEFT = -0.02  # ...from here (from the tile's middle); the letter on their left
PIP_OFF: Color = (0.12, 0.13, 0.14, 1)
TILE_DIM: Color = (0.45, 0.48, 0.5, 1)  # a weapon not selected: its letter, and its level's pips
HULL_SEGMENTS = 20  # the health gauge
HULL_BOTTOM, HULL_TOP = 0.02, 0.04
HULL_INSET = 0.003  # how far the lit segments are kept inside the gauge
HULL_INSET_SHARE = 0.2  # the dark gap between them, as a share of the gauge's step
HULL_INNER = 0.115  # how far the gauge runs from the tiles' left edge
HULL_GOOD: Color = (0.3, 1.0, 0.4, 1)  # over half...
HULL_LOW: Color = (1.0, 0.75, 0.2, 1)  # ...over a quarter...
HULL_CRITICAL: Color = (1.0, 0.25, 0.2, 1)  # ...and under
HULL_OFF: Color = (0.08, 0.1, 0.08, 1)
HULL_EPSILON = 1e-9  # keeps a fraction of exactly 0.5 or 0.25 off the segment below it
HULL_LOW_AT = 0.5  # over this share of health the gauge is green...
HULL_CRITICAL_AT = 0.25  # ...over this one amber, and under it red
BOSS_BAR_WIDTH = 1.1  # at the top edge, with the boss's name under it
BOSS_BAR_HEIGHT = 0.025
BOSS_FILL_MIN = 0.001  # the least the bar is filled: a zero scale makes Panda3D print warnings
BOSS_NAME: Color = (1, 0.75, 0.6, 1)
BOSS_BAR_FILL: Color = (1.0, 0.4, 0.15, 1)
TILE_LIGHT: Color = (1, 1, 1, 0.22)  # a selected weapon's tile, lit in its own color


class Hud(EntityModels):
    """The HUD over the game, and the frames per second over every screen."""

    world: World | None

    def _setup_hud(self) -> None:
        # Each panel hangs on one of Panda3D's anchors (the game area's real edges, whatever the window's shape).
        left = self.a2dBottomLeft.attachNewNode("hud_left")
        center = self.a2dBottomCenter.attachNewNode("hud_center")
        right = self.a2dBottomRight.attachNewNode("hud_right")
        left.setPos(PANEL_MARGIN, 0, PANEL_MARGIN)
        center.setZ(PANEL_MARGIN)
        right.setPos(-PANEL_MARGIN, 0, PANEL_MARGIN)
        self.hud_parts = [left, center, right]
        self._setup_score_panel(left)
        self._setup_weapons_panel(center)
        self._setup_lives_panel(right)

        # Frames per second, top-right on every screen (not part of the in-game HUD, which menus hide).
        fps_corner = self.a2dTopRight.attachNewNode("fps")
        top_line = -HUD_MARGIN - FPS_SCALE * 0.8  # the letters' tops reach up to the margin
        self.fps_text = self._hud_text(fps_corner, -HUD_MARGIN, top_line, TextNode.ARight, FPS_SCALE, HUD_DIM_COLOR)
        self._fps_shown = -1
        self._fps_next = 1.0  # the clock averages over the last second: nothing to show before
        if not config.SHOW_FPS:
            fps_corner.hide()

        # The boss's health bar at the top edge, in a display, its name under it: only while a boss is on screen.
        self.boss_hud = self.a2dTopCenter.attachNewNode("hud_boss")
        bar_left, bar_top = -BOSS_BAR_WIDTH / 2, -HUD_MARGIN
        panel.display(self.boss_hud, bar_left, -bar_left, bar_top - BOSS_BAR_HEIGHT, bar_top)
        self.boss_fill = panel.card(self.boss_hud, 0, BOSS_BAR_WIDTH, -BOSS_BAR_HEIGHT, 0, BOSS_BAR_FILL)
        self.boss_fill.setPos(bar_left, 0, bar_top)
        below_bar = bar_top - BOSS_BAR_HEIGHT - HUD_SMALL
        self.boss_name = self._hud_text(self.boss_hud, 0.0, below_bar, TextNode.ACenter, HUD_SMALL, BOSS_NAME)
        self.boss_hud.hide()
        # What's currently shown, so _update_hud only touches a text (Panda3D rebuilds its geometry each time)
        # or recolors lamps when its value actually changed, instead of every single frame.
        self._hud_score: int | None = None
        self._hud_lives: int | None = None
        self._hud_hull: int | None = None
        self._hud_weapon_state: dict[str, tuple[int, bool]] = {}
        self._hud_secondary: str | None = None
        self._hud_boss_name: str | None = None
        self._hud_boss_visible = False

    def _setup_score_panel(self, parent: NodePath) -> None:
        """Show the score on an amber readout."""
        width, pad = SIDE_PANEL_WIDTH, PANEL_PADDING
        panel.plate(parent, 0, width, 0, PANEL_HEIGHT)
        panel.label(parent, pad, PANEL_HEIGHT - LABEL_GAP, "SCORE")
        panel.display(parent, pad, width - pad, READOUT_BOTTOM, READOUT_TOP)
        digits_right = width - pad - READOUT_INSET
        panel.text(
            parent, digits_right, READOUT_TEXT_Z, READOUT_SCALE, AMBER_GHOST, TextNode.ARight, "8" * SCORE_DIGITS
        )
        self.score_text = panel.text(parent, digits_right, READOUT_TEXT_Z, READOUT_SCALE, AMBER, TextNode.ARight)

    def _setup_lives_panel(self, parent: NodePath) -> None:
        """Show the lives: a readout, and a lamp for each up to the most the ship can have."""
        width, pad = SIDE_PANEL_WIDTH, PANEL_PADDING
        panel.plate(parent, -width, 0, 0, PANEL_HEIGHT)
        panel.label(parent, -width + pad, PANEL_HEIGHT - LABEL_GAP, "LIVES")
        panel.display(parent, -width + pad, -pad, READOUT_BOTTOM, READOUT_TOP)
        digit_left = -width + pad + READOUT_INSET
        panel.text(parent, digit_left, READOUT_TEXT_Z, READOUT_SCALE, AMBER_GHOST, TextNode.ALeft, str(LIVES_DIGITS))
        self.lives_text = panel.text(parent, digit_left, READOUT_TEXT_Z, READOUT_SCALE, AMBER)
        first = -pad - READOUT_INSET - LAMP_STEP * (config.MAX_LIVES - 1) - LAMP_SIZE
        self.life_lamps = [
            panel.card(parent, x, x + LAMP_SIZE, LAMP_BOTTOM, LAMP_BOTTOM + LAMP_SIZE, LAMP_OFF)
            for x in (first + i * LAMP_STEP for i in range(config.MAX_LIVES))
        ]

    def _setup_weapons_panel(self, parent: NodePath) -> None:
        """Show a tile per weapon with its level, the secondary weapon's tile, and the hull gauge under them."""
        half = CENTER_PANEL_WIDTH / 2
        panel.plate(parent, -half, half, 0, PANEL_HEIGHT)
        tiles_left = -(TILE_COUNT * TILE_WIDTH + (TILE_COUNT - 1) * TILE_GAP) / 2
        centers = [tiles_left + TILE_WIDTH / 2 + i * (TILE_WIDTH + TILE_GAP) for i in range(TILE_COUNT)]
        self.weapon_texts: dict[str, OnscreenText] = {}
        self.weapon_tiles: dict[str, NodePath] = {}  # lit in the weapon's color while selected
        self.weapon_pips: dict[str, list[NodePath]] = {}
        middle = (TILE_BOTTOM + TILE_TOP) / 2
        letter_z = middle - TILE_LETTER * TILE_LETTER_OFFSET  # the letter's middle on the tile's
        letter_x = (-TILE_WIDTH / 2 + PIPS_LEFT) / 2  # between the tile's left side and the pips
        pip_bottom = middle - PIP_HEIGHT / 2
        for weapon, x in zip(WEAPONS, centers[:-1], strict=True):
            self.weapon_tiles[weapon] = self._tile(parent, x)
            self.weapon_texts[weapon] = panel.text(
                parent, x + letter_x, letter_z, TILE_LETTER, TILE_DIM, TextNode.ACenter
            )
            self.weapon_pips[weapon] = [
                panel.card(parent, left, left + PIP_WIDTH, pip_bottom, pip_bottom + PIP_HEIGHT, PIP_OFF)
                for left in (x + PIPS_LEFT + i * (PIP_WIDTH + PIP_GAP) for i in range(MAX_LEVEL))
            ]
        # The secondary weapon, if the ship carries one: "T" or "Z" in its color.
        x = centers[-1]
        self.secondary_tile = self._tile(parent, x)
        self.secondary_text = panel.text(parent, x + letter_x, letter_z, TILE_LETTER, TILE_DIM, TextNode.ACenter)
        panel.text(parent, x + PIPS_LEFT, middle - AUX_DROP, AUX_SCALE, TILE_DIM, TextNode.ALeft, "AUX")

        panel.label(parent, tiles_left, HULL_BOTTOM + AUX_GAP, "HULL")
        bar_left, bar_right = tiles_left + HULL_INNER, -tiles_left
        panel.display(parent, bar_left, bar_right, HULL_BOTTOM, HULL_TOP)
        step = (bar_right - bar_left) / HULL_SEGMENTS
        gap = step * HULL_INSET_SHARE
        self.hull_segments = [
            panel.card(
                parent,
                left + gap / 2,
                left + step - gap / 2,
                HULL_BOTTOM + HULL_INSET,
                HULL_TOP - HULL_INSET,
                HULL_OFF,
            )
            for left in (bar_left + i * step for i in range(HULL_SEGMENTS))
        ]

    def _tile(self, parent: NodePath, x: float) -> NodePath:
        """Make an annunciator tile centered on `x`: a display, and return its light (hidden while off)."""
        left, right = x - TILE_WIDTH / 2, x + TILE_WIDTH / 2
        panel.display(parent, left, right, TILE_BOTTOM, TILE_TOP)
        light = panel.card(parent, left, right, TILE_BOTTOM, TILE_TOP, TILE_LIGHT)
        light.hide()
        return light

    def _hud_text(
        self,
        parent: NodePath,
        x: float,
        z: float,
        align: TextAlign,
        scale: float,
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
            self.score_text.setText(f"{self.world.score:0{SCORE_DIGITS}d}"[-SCORE_DIGITS:])
        if self.world.lives != self._hud_lives:
            self._hud_lives = self.world.lives
            self.lives_text.setText(str(min(self.world.lives, LIVES_DIGITS)))
            for index, lamp in enumerate(self.life_lamps):
                lamp.setColor(LAMP_ON if index < self.world.lives else LAMP_OFF)
        self._update_hull(max(self.world.player.health, 0) / self.world.ship.health)
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
        self.boss_fill.setSx(max(boss.health_fraction, BOSS_FILL_MIN))  # a zero scale makes Panda3D print warnings

    def _update_hull(self, fraction: float) -> None:
        """Light the hull gauge's segments: green, amber under half, red under a quarter."""
        lit = math.ceil(fraction * HULL_SEGMENTS - HULL_EPSILON)
        if lit == self._hud_hull:
            return
        self._hud_hull = lit
        color = HULL_GOOD if fraction > HULL_LOW_AT else HULL_LOW if fraction > HULL_CRITICAL_AT else HULL_CRITICAL
        for index, segment in enumerate(self.hull_segments):
            segment.setColor(color if index < lit else HULL_OFF)

    def _update_weapons_hud(self, arsenal: Arsenal) -> None:
        for weapon, text in self.weapon_texts.items():
            selected = weapon == arsenal.selected
            level = arsenal.levels[weapon]
            if self._hud_weapon_state.get(weapon) == (level, selected):
                continue  # setText/setFg rebuild the text's geometry: skip when nothing changed
            self._hud_weapon_state[weapon] = (level, selected)
            color = WEAPON_COLORS[weapon]
            text.setText(LETTERS[weapon])
            text.setFg(color if selected else TILE_DIM)
            tile = self.weapon_tiles[weapon]
            tile.setColor(*color[:3], TILE_LIT_ALPHA)
            tile.show() if selected else tile.hide()
            lit = color if selected else TILE_DIM
            for index, pip in enumerate(self.weapon_pips[weapon]):
                pip.setColor(lit if index < level else PIP_OFF)
        secondary = arsenal.secondary.kind if arsenal.secondary else None
        if secondary != self._hud_secondary:
            self._hud_secondary = secondary
            self.secondary_text.setText(SECONDARY_LETTERS[secondary] if secondary else "")
            if secondary:
                color = SECONDARY_COLORS[secondary]
                self.secondary_text.setFg(color)
                self.secondary_tile.setColor(*color[:3], TILE_LIT_ALPHA)
                self.secondary_tile.show()
            else:
                self.secondary_tile.hide()
