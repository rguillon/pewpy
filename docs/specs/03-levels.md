# 03 — Levels

## General

- Worlds: the levels are grouped in 5 worlds of 8 levels each (40 levels). Each world keeps to related grounds,
  and its levels vary them (see "Worlds"). A level is named by its place, like "2-5" (world 2, level 5).
- Menus: Start -> world select -> the world's level select (see `04-ui-audio.md`). Every level is open from the
  start.
- Scroll speed: constant within a level, set per level.
- Level length: time based. The level ends when every wave has entered and no enemy is left.
- Bosses: every level ends with its own boss (see the worlds' tables and `02-enemies.md`), a wave like any other
  (`"enemy": "warden"`) about 6 s after the last one; the level ends 3 s after it is destroyed: every enemy left blows up (no points), enemy shots vanish, and the player plays on to pick up what it dropped *(placeholder, see decisions.md)*. Each world's bosses get
  harder level by level, up to the world's big boss at x-8.
- Level data format: `src/pewpy/levels/world_<number>/level_<number>.json`, one JSON file per level, and
  `world.json` in each world's folder with the world's name (see `pewpy.level`). Level fields: `name`,
  `scroll_speed`, `background` (see "Backgrounds"), `scenery` (changes to the background's preset, see
  "Backgrounds"), `time_of_day` (`day`, `dusk` or `night`, default `day`), `background_seed` (the
  background's layout, and in space its colors: the same every time), `clouds` (see-through clouds over the
  ground, from 0 for none to 1 for the most, default 0), and `waves`.
- Checkpoints on death? No: losing a life restarts the level from the beginning.
- Transitions between levels: "LEVEL COMPLETE" screen ("WORLD COMPLETE" after a world's last level), Enter goes
  to the next level, into the next world after a world's last level. After the last level (5-8): "ALL LEVELS
  COMPLETE / YOU WIN", then the main menu.

## Backgrounds

Each level has one background (see `05-visuals.md`). All kept dark and muted so bullets stand out; the grounds
fade into haze towards the top of the screen.

Each background is a preset of `src/pewpy/levels/sceneries.json`, which holds every value of the sceneries: colors
(of the grounds, water, lava, props, the sky, the haze), sizes and shares (city blocks, streets, building heights,
fields, islands, dunes...), depths, stars, nebulas, asteroids, clouds, times of day. A level's `scenery` changes
any of them for that level, e.g. `"scenery": {"fluid": {"colors": {"deep": [0.02, 0.08, 0.06]}}}` for greener
water (see `pewpy.scenery.params`).

| Background | Look |
|------------|------|
| `space` | Stars, faint nebula clouds, a distant voxel planet; nebula and planet colors and the planet's size vary by level |
| `debris` | Stars and tumbling voxel asteroids at two depths |
| `planet` | Rolling hills and craters |
| `farmland` | Patchwork fields (wheat, crops, plowed earth, lavender), hedges, orchards, farms with silos, dirt roads |
| `forest` | A canopy of round treetops, clearings, a winding river |
| `swamp` | Murky water with muddy islets, reeds and dead trees |
| `ocean` | A sea with islands: beaches, grass, forest and rocky tops; animated water, lighter in the shallows |
| `pack_ice` | Ice floes and icebergs on a dark sea |
| `clouds` | Flat moonlit clouds, with town lights far below in the gaps |
| `desert` | Dune ridges, rock mesas, oasis pools with palms |
| `canyon` | Layered cliffs stepping down to a river |
| `volcano` | Black volcanic hills with glowing lava rivers |
| `mountains` | Snowy ridges, glaciers, pine forests |
| `city` | A sci-fi city at night: blocks of towers with lit windows, street lights, red beacons |
| `refinery` | Tanks, pipe yards, plants with glowing furnaces, flaming stacks, at night |

On the grounds, `time_of_day` tints the ground, its haze and the sky: `dusk` warmer, `night` darker and bluer;
lights (windows, lava, flames) keep their colors. The ground scrolls at 30% of the level's speed on screen,
as if flying high, so it never moves with the enemies (Turrets slide over it too).

Over the grounds, `clouds` adds soft see-through clouds in two layers between the ground and the ships (up to 10
per layer), drifting down a bit faster than the ground and slightly sideways in a wind, pale and in the color
of the air (dimmer at night, but less than the ground). Ships and bullets are always drawn over them. Space
levels have none.

## Worlds

### World 1: Orbit (space and asteroid fields)

| Level | Name | Background | Time of day | Clouds | Boss |
|-------|------|------------|-------------|--------|------|
| 1-1 | Outer Belt | space (purple and teal nebula) | | | Sentinel |
| 1-2 | Red Drift | space (ember nebula) | | | Prowler |
| 1-3 | Rubble Run | debris | | | Rockbreaker |
| 1-4 | Starlit Reach | space (deep blue nebula) | | | Siege Pod |
| 1-5 | Shard Belt | debris | | | Twin Fang |
| 1-6 | Green Veil | space (green nebula) | | | Relay Array |
| 1-7 | Cold Wake | debris | | | Mine Carrier |
| 1-8 | Minefield | debris | | | Warden |

### World 2: Heartland (hills, farmland, forest, swamp)

| Level | Name | Background | Time of day | Clouds | Boss |
|-------|------|------------|-------------|--------|------|
| 2-1 | Ground Defense | planet | day | 0.3 | Thresher |
| 2-2 | Patchwork | farmland | day | 0.15 | Picket |
| 2-3 | Greenwood | forest | day | 0.5 | Bulwark |
| 2-4 | Mire | swamp | day | 0.6 | Turbine |
| 2-5 | Harvest Dusk | farmland | dusk | 0.1 | Silo Hauler |
| 2-6 | Crater Fields | planet | dusk | 0.35 | Hive Carrier |
| 2-7 | Moonlit Woods | forest | night | 0.25 | Tugmaster |
| 2-8 | Fogbound Fen | swamp | night | 0.85 | Harvester |

### World 3: Waters (islands, pack ice, clouds)

| Level | Name | Background | Time of day | Clouds | Boss |
|-------|------|------------|-------------|--------|------|
| 3-1 | Archipelago | ocean | day | 0.5 | Clamp Barge |
| 3-2 | Pack Ice | pack_ice | day | 0.2 | Pulsar |
| 3-3 | Cloud Deck | clouds | day | 0.7 | Frigate |
| 3-4 | Sunset Isles | ocean | dusk | 0.35 | Delta Raider |
| 3-5 | Polar Night | pack_ice | night | 0.6 | Cryo Fortress |
| 3-6 | Storm Top | clouds | dusk | 0.9 | Grappler |
| 3-7 | Dark Tide | ocean | night | 0.4 | Dreadnought |
| 3-8 | Frozen Deep | pack_ice | dusk | 0.3 | Tidebreaker |

### World 4: Badlands (desert, canyon, volcano, mountains)

| Level | Name | Background | Time of day | Clouds | Boss |
|-------|------|------------|-------------|--------|------|
| 4-1 | Dune Sea | desert | day | 0.05 | Breacher |
| 4-2 | Red Canyon | canyon | day | 0.15 | Cyclone |
| 4-3 | Ember Fields | volcano | day | 0.3 | Borer |
| 4-4 | High Peaks | mountains | day | 0.6 | Bastion |
| 4-5 | Desert Night | desert | night | 0.1 | Foundry |
| 4-6 | Canyon Dusk | canyon | dusk | 0.25 | Scavenger |
| 4-7 | Ashen Slopes | volcano | dusk | 0.5 | Magma Rig |
| 4-8 | Summit | mountains | dusk | 0.8 | Colossus |

### World 5: Metropolis (city, refinery)

| Level | Name | Background | Time of day | Clouds | Boss |
|-------|------|------------|-------------|--------|------|
| 5-1 | Neon City | city | day | 0.2 | Patrol Drone |
| 5-2 | Refinery | refinery | day | 0.4 | Enforcer |
| 5-3 | Downtown | city | day | 0.1 | Hover Tank |
| 5-4 | Smelter | refinery | dusk | 0.5 | Spire |
| 5-5 | Neon Rain | city | night | 0.7 | Sentry Grid |
| 5-6 | Flare Stacks | refinery | night | 0.6 | Gunship Prime |
| 5-7 | Skyline | city | dusk | 0.3 | Executor |
| 5-8 | The Core | city | night | 0.9 | Overmind |
