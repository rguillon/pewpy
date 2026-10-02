"""The sound effects, synthesized: arcade blips, sweeps and noise bursts. Numpy only, no Panda3D.

Each is a function returning mono samples (-1 to 1) at synth.RATE; EFFECTS names them all; each
is in its own module (variants of one sound together), shaping.py has what they share. "laser" loops: it
is a whole number of cycles of everything in it, so it repeats without a click.
"""

from collections.abc import Callable

from pewpy.audio.sfx.alarm import alarm
from pewpy.audio.sfx.disarmed import disarmed
from pewpy.audio.sfx.explosions import blast, explosion, explosion_big, explosion_small, player_explosion
from pewpy.audio.sfx.extra_life import extra_life
from pewpy.audio.sfx.hit import hit
from pewpy.audio.sfx.hurt import hurt
from pewpy.audio.sfx.laser import laser
from pewpy.audio.sfx.menu import menu_back, menu_choose, menu_move
from pewpy.audio.sfx.missile import missile
from pewpy.audio.sfx.pickup import pickup
from pewpy.audio.sfx.repair import repair
from pewpy.audio.sfx.shot import shot
from pewpy.audio.sfx.switch import switch
from pewpy.audio.sfx.zap import zap
from pewpy.audio.synth import FloatArray

EFFECTS: dict[str, Callable[[], FloatArray]] = {
    "shot": shot,
    "missile": missile,
    "laser": laser,
    "hit": hit,
    "explosion_small": explosion_small,
    "explosion": explosion,
    "explosion_big": explosion_big,
    "player_explosion": player_explosion,
    "hurt": hurt,
    "blast": blast,
    "zap": zap,
    "disarmed": disarmed,
    "pickup": pickup,
    "repair": repair,
    "extra_life": extra_life,
    "switch": switch,
    "menu_move": menu_move,
    "menu_choose": menu_choose,
    "menu_back": menu_back,
    "alarm": alarm,
}
