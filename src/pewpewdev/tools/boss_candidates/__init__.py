"""Generate boss model candidates for the Boss candidates screen (data/models/boss_candidates/).

    make boss-candidates                                  # 40 bosses, a new random batch each time
    make boss-candidates ARGS="--count 20 --seed 1234"    # the same batch again
    make boss-candidates ARGS="--append --count 10"       # add to the batch instead of replacing it

(or `uv run python -m pewpewdev.tools.boss_candidates ...`). Then open Main menu > Boss candidates in `make dev`.

Like the game's bosses, each candidate is a big core and destroyable parts placed on it. For candidate 007:
- `007.json`: the core's drawing (with its engines);
- `007_a.json`, `007_b.json`...: its parts' drawings;
- `007.parts.json`: where the parts go: {"parts": [{"drawing": "007_a", "x": ..., "y": ...}]}, in cubes from the
  core's middle (x right, y up the screen); a part used on both sides is listed twice.

Cores: 18 families (carrier, dreadnought, station, hammerhead, twin hull, flying wing, crescent, modular, citadel,
spider, trident, barge, mothership, chain, fortress, blade, gunline, ring cluster), a quarter of them combining two
(a second hull at the back or on the sides), with 0 to 3 appendages (big wings, arms ending in pods, armor spikes, a
halo ring, engine nacelles, radiator panels, masts); medium (41 to 61 cubes wide), large (up to 85) or huge (up to
115, half the screen); a fifth of them lopsided. Details: raised decks and a bridge, hangar bays, armor bands, engine
banks, lights, and a paint scheme (plain, two-tone or glowing seams). Parts (11 kinds: turrets, cannons, generators,
missile launchers, drills, missile pods, beam emitters, shield nodes, radar dishes, flak guns, claws), sized to the
boss, up to 10 on the biggest, each on a socket. Everything is a real 3D model ("layers"), sculpted from its plan
(pewpewdev/tools/candidates/shaping.py): a chamfered hull, higher on top than underneath, raised decks stacked on it with the bridge on
top, recessed panel lines and hangar bays, thin wings and sponsons; each part stands on the core's surface where it
is mounted, its barrels at half its height. As for the enemies (pewpewdev.tools.candidates), many more are
made than kept, and the ones kept are the most different from each other (outline, size, family, parts).

Each part in its own module: families/ (one module per family), appendages/ (one per appendage), core.py (the core's
outline and details), part_kinds/ (one module per kind of part) and mounting.py (placing them), palette.py, shaping.py,
selection.py and __main__.py.
"""
