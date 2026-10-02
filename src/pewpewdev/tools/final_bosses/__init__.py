"""Make the final bosses (data/bosses/final_bosses.json) from their plans (plans.json, in this
package), 02-enemies-bosses.md:

    make final-bosses

(or `uv run python -m pewpewdev.tools.final_bosses`).

A plan gives a final boss's drawing, size, difficulty (1 to 20), four attacks and parts. Each is a big core with its
parts, and four attacks. Its phases come from them (see `final_boss`): the front parts first, then the back ones,
while the core is armored; then the core, then the core in a rage. Everything gets harder with the difficulty.

A boss is written like any enemy (see pewpy.game.enemies.spec): it comes down to HOLD_Y, then goes through its
phases as states, each starting with PHASE_PAUSE seconds without shooting, blinking; its parts are enemies of their
own. `boss_json` (writing.py) writes a boss described shortly (BossSpec, boss.py: its parts and phases) that way;
attacks.py has the attacks' guns, plans.py reads the plans.
"""
