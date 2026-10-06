"""Generate enemy model candidates: voxel drawings for the Candidates screen (data/models/candidates/enemies/).

    uv run python -m pewpy.tools.candidates                        # 500 ships, a new random batch each time
    uv run python -m pewpy.tools.candidates --kind fighter --count 50
    uv run python -m pewpy.tools.candidates --seed 1234              # the same batch again
    uv run python -m pewpy.tools.candidates --append --count 20      # add to the batch instead of replacing it

(or `make candidates ARGS="--kind fighter --count 50"`). Then open Main menu > Enemy candidates in `make dev` (or
"Reload models" there).

Enemies point down the screen: nose on the last row, engines at the back (flames "towards": "top"). Every ship is
assembled in 3D from a kit of hardcoded parts (kit/): a hull (a profile stretched along it), a pair of wings (an
outline), a tailplane or canards, a cockpit, engines (nozzles at the tail, or nacelles), weapons (nose barrels,
wing guns, tip guns or missiles, missiles under the wings, a turret, a gatling, a side cannon), fins, antennas, a
radar dome, intakes, armor plates, a livery stripe and markings. Kinds: fighter, interceptor, bomber, drone, gunship,
heavy (kit/archetypes.py), each a recipe choosing among the parts and placing them; a few are lopsided.
Many more ships are generated than kept (`--pool`): the ones kept are the most different from each other (outline,
size, proportions), so there are no near-duplicates. The drawings are ordinary 3D drawings ("layers", "palette",
"engines", "weapons").

The modules: kit/ (the parts and the recipes), selection.py (making ships, keeping the most different), __main__.py;
what the candidates share is in pewpy.tools.common (the command line, the 3D drawing, the colors, the variety).
"""
