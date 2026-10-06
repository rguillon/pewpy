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

Cores: 18 families (carrier, dreadnought, station, hammerhead, twin hull, flying wing, crescent, modular, citadel,
spider, trident, barge, mothership, chain, fortress, blade, gunline, ring cluster), a quarter of them combining two (a
second hull at the back or on the sides), with 0 to 3 appendages (big wings, arms ending in pods, armor spikes, a halo
ring, engine nacelles, radiator panels, masts); medium (41 to 61 cubes wide), large (up to 85) or huge (up to 115, half
the screen); a fifth of them lopsided. Details: raised decks and a bridge, hangar bays, armor bands, engine banks,
lights, and a paint scheme (plain, two-tone or glowing seams). Parts (11 kinds: turrets, cannons, generators, missile
launchers, drills, missile pods, beam emitters, shield nodes, radar dishes, flak guns, claws), sized to the boss, up to
10 on the biggest, each on a socket. Everything is a real 3D model ("layers"), sculpted from its plan
(sculpting.py): a chamfered hull, higher on top than underneath, raised decks stacked on it with
the bridge on top, recessed panel lines and hangar bays, thin wings and sponsons; then its flat tops broken up
(greebles.py): plating panels raised or sunk, machinery (blocks, grilled vents, domes, pipes, radiator fins, antennas,
lights, lit trenches), ribs and weapon pods on the wings, and the same, smaller, on every part; each part stands on the
core's surface where it is mounted, its barrels at half its height. As for the enemies (pewpy.tools.candidates), many
more are made than kept, and the ones kept are the most different from each other (outline, size, family, parts).

Each part in its own module: canvas.py (the plan), families/ (one module per family), appendages/ (one per
appendage), core.py (the core's outline and details), details.py (bands, panel lines, markings on a plan),
sculpting.py (a plan made 3D) and shaping.py (how a core's and a part's are), greebles.py (the surface details),
part_kinds/ (one module per kind of part), mounting.py (placing them), weapons.py, selection.py and __main__.py; what
the candidates share is in pewpy.tools.common (the command line, the 3D drawing, the colors, the variety).
"""
