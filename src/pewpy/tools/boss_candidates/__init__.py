"""Generate boss model candidates for the Boss candidates screen (data/models/candidates/bosses/).

    make boss-candidates                                  # 40 bosses, a new random batch each time
    make boss-candidates ARGS="--count 20 --seed 1234"    # the same batch again
    make boss-candidates ARGS="--append --count 10"       # add to the batch instead of replacing it

(or `uv run python -m pewpy.tools.boss_candidates ...`). Then open Main menu > Boss candidates in `make dev`.

Like the game's bosses, each candidate is a big core and destroyable parts placed on it, all in one file, like the
game's models (see pewpy.data.read_model). Candidate 007 is `007.json`: the core's drawing (with its engines and
weapons), its parts' drawings under "parts" ({"a": ..., "b": ...}, each written once: the part "a" is
"candidates/bosses/007:a"), and where they go under "layout": [{"part": "a", "x": ..., "y": ...}], in cubes from the
core's middle (x right, y up the screen); a part used on both sides is listed twice.

A boss is made the same way as an enemy (pewpy.tools.candidates), from the same kit of hardcoded parts, bigger: its
core is a recipe placing a hull, wings, a cockpit or bridge, engines, weapons and extras (archetypes.py: carrier,
dreadnought, flying wing, twin hull, mothership, gunline), its sizes times its size class's scale: medium (about 41
to 61 cubes wide), large (up to 85) or huge (up to 115, half the screen); a fifth of them lopsided (a side cannon,
parts on one side). Its destructible parts are small ships of their own from the same kit (parts.py: turrets,
cannons, gatlings, flak batteries, missile launchers, beam emitters, radars, generators), sized to the boss, a few
kinds on each, up to 10 on the biggest, each standing on the hull on a plate, mirrored on a symmetric boss. Each
drawing lists its weapons, a part's all of its kind; the core gets turrets on its spine until the boss has at least
MIN_WEAPONS. As for the enemies, many more are made than kept, and the ones kept are the most different from each
other (outline, size, kind, parts).

The modules: archetypes.py (the cores' recipes), parts.py (the parts' recipes, and placing them), selection.py
(making bosses, keeping the most different) and __main__.py; the kit is pewpy.tools.candidates.kit, and what the
candidates share is in pewpy.tools.common (the command line, the 3D drawing, the colors, the variety).
"""
