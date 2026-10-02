"""Remodel the game's ships in real 3D voxels (data/models/<name>.json), from recipes (recipes/: one
module per ship) written with sculpt.py.

    make models                       # every model that has a recipe
    make models ARGS="player drone"   # just these

(or `uv run python -m pewpewdev.tools.models ...`). Each recipe builds the ship in the same footprint as before (its
hitbox), with its engines where they were (their flames), and its own paint color so ships stay easy to tell
apart. The files it writes are ordinary 3D drawings: they can be edited by hand or in MagicaVoxel (`make voxels`),
but running a recipe again overwrites them.
"""
