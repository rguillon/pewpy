"""Background candidates: what a level says of its background, made from a theme (see 04-ui-audio.md, "Backgrounds").

A candidate is what a level says of its background (03-levels.md): a preset of levels/sceneries.json (`background`),
its changes (`scenery`), its `time_of_day`, `clouds` and `background_seed`, with a `name` and a `note` (its theme). It's
made again from its theme and seed (candidate.py), so they are all a world's plan (pewpy.generators.levels) needs
to take it.

Each shows one of the kinds of ground made for them (pewpy.scenery.ground.kinds, and their painters in its shader):
a salt pan, a savanna, badlands (their presets in sceneries.json; three of them became worlds 3, 5 and 6). Only
earth-like ones, like real places: a theme (themes.py) gives one of them its palette, sometimes other water, its
numbers, times of day and clouds: salt, turquoise, copper, clay pans and a salt shore; Serengeti, green-season,
Kalahari or outback savannas; painted, grey, cream or rainbow badlands. Each candidate varies its theme's palette and
numbers a little more. The Dev menu's backgrounds browser (browser.py) shows them.
"""
