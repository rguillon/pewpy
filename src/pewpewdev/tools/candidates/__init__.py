"""Generate enemy model candidates: voxel drawings for the Candidates screen (data/models/candidates/).

    uv run python -m pewpewdev.tools.candidates                     # 200 ships, a new random batch each time
    uv run python -m pewpewdev.tools.candidates --kind aircraft --count 50
    uv run python -m pewpewdev.tools.candidates --seed 1234           # the same batch again
    uv run python -m pewpewdev.tools.candidates --append --count 20   # add to the batch instead of replacing it

(or `make candidates ARGS="--kind aircraft --count 50"`). Then open Main menu > Enemy candidates in `make dev` (or
"Reload models" there).

Enemies point down the screen: nose on the last row, engines at the back (flames "towards": "top"). Kinds:
- aircraft: a slender fuselage with an ogive nose, thin wings tapering to their tips (swept, delta, cranked,
  forward-swept, ogival or long and straight), a tailplane or canards, thin fins, slim engines;
- industrial: a core hull (spindle, block, wedge, egg, segmented, cross, crescent, frame, diamond, arrowhead) with
  1 to 3 attachments (wings, nacelles, booms, mandibles, fins, turrets, a side cannon, containers, radiators,
  antennas), symmetric or lopsided.
Every ship is a real 3D model ("layers"): the aircraft are built from their parts (`aircraft_layers`); the industrial
ships are drawn as a plan, then sculpted (shaping.py): a hull chamfered from its outline, higher on top than
underneath, a spine and a cockpit raised on it, recessed panel lines, thin wings rising to their tips, rounded pods.
Many more ships are generated than kept (`--pool`): the ones kept are the most different from each other (outline,
size, proportions), so there are no near-duplicates.

Each part in its own module: canvas.py (the plan), aircraft/ (and its wing plans, aircraft/wings/), industrial/ (its
cores and attachments, one module each), details.py (on every ship), palette.py, selection.py (keeping the most
different), and __main__.py.
"""
