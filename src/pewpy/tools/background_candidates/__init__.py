"""Generate background candidates for the Background candidates screen (data/models/candidates/backgrounds/).

    make backgrounds                                   # one background per theme, a new random batch each time
    make backgrounds ARGS="--count 20 --seed 1234"     # 20 of the themes, the same batch again
    make backgrounds ARGS="--append --count 10"        # add to the batch instead of replacing it

(or `uv run python -m pewpy.tools.background_candidates ...`). Then open Main menu > Background candidates in
`make dev`.

A candidate is what a level says of its background (03-levels.md): a preset of levels/sceneries.json (`background`),
its changes (`scenery`), its `time_of_day`, `clouds` and `background_seed`, with a `name` and a `note` (its theme). So
a candidate joins the game by copying those fields into a level (or into sceneries.json as a new preset).

Each shows one of the kinds of ground made for them (pewpy.scenery.ground.kinds, and their painters in its shader):
a salt pan, a savanna, badlands (their presets in sceneries.json; three of them became worlds 3, 5 and 6, see
pewpy.tools.levels). Only earth-like ones, like real places: a theme (themes.py) gives one of them its palette,
sometimes other water, its numbers, times of day and clouds: salt, turquoise, copper, clay pans and a salt shore;
Serengeti, green-season, Kalahari or outback savannas; painted, grey, cream or rainbow badlands. Each candidate
varies its theme's palette and numbers a little more; a batch has one per theme, none twice.
"""
