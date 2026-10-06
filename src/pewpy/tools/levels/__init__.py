"""Generate the game's levels (data/levels/) from the plan of the worlds (worlds/, 03-levels.md).

    make levels                        # every world, the same levels every time
    make levels ARGS="--seed 1234"     # another draw of the waves (the looks and the bosses stay)

(or `uv run python -m pewpy.tools.levels ...`).

Each world keeps one ground (one background preset) on all its levels; its levels only change that ground's
numbers: time of day, clouds, haze, layout seed, the preset's shape and layout knobs, a few colors. Each level has
a difficulty: level L of world W is 2 (W - 1) + L, so a world's first level is as hard as the level 3 of the world
before. The difficulty sets the scroll speed, the size of the groups, the threat of each half of the level (its
enemies' points, spread over about 46 s: the harder, the denser) and which enemies come (each enemy has the difficulty
it unlocks at).

A level has two halves, each a warm-up wave, the main waves, then a finale of its signature enemies close together,
and a boss 6 s after its last wave: the level's mini boss after the first half, its final boss after the second. The
second half is harder: its groups and its threat are those of a level SECOND_HALF_HARDER steps harder. The waves'
clock stops while a boss is fought (see World.wave_time), so the second half waits for the mini boss.

The worlds' plans are in worlds/ (one module per world, see plan.py), the enemies' unlocks and formations in
enemies.py; difficulty.py, waves.py and generate.py make the levels from them.
"""
