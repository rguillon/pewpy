# 03 — Levels

Units: see `00-vision.md`.

## Worlds and levels

- **LVL-1** The game shall have 48 levels in 8 worlds of 6 levels each. A level shall be named by its place, like
  "2-5" (world 2, level 5), and by its own name.
- **LVL-2** Every level shall be open from the start; the player picks a world, then one of its levels (see
  `04-ui-audio.md`).
- **LVL-3** Each level shall be the same every time it is played (its waves and its background are fixed); only the
  enemies' first-shot waits (ENM-7) and the pickups dropped are random.
- **LVL-4** Each world shall keep one kind of ground on all its levels, so its look stays consistent; its levels shall
  vary that ground's details, the time of day and the clouds (see "Worlds"). Each world shall have two levels by day,
  two at dusk and two at night (a level named for its time keeps it), and clouds from nearly clear (0.2 or less) to
  heavy (0.8 or more), in no rising order.
- **LVL-5** Completing a level shall show the Level complete screen ("WORLD COMPLETE" after a world's last level);
  from there the player goes on to the next level, into the next world after a world's last level. After the last
  level (8-6) the game shows "ALL LEVELS COMPLETE / YOU WIN!" and goes back to the main menu.

## Difficulty

- **LVL-6** Level L of world W shall have the difficulty d = 2 (W − 1) + L, from 1 (1-1) to 20 (8-6): each level is
  harder than the one before in its world, and a world's first level is as hard as the third level of the world before.
- **LVL-7** A level's scroll speed shall be constant, 0.2 + 0.11 × (d − 1) / 19 (0.2 at difficulty 1, 0.31 at
  difficulty 20), rounded to 3 decimals.

## How a level is played

- **LVL-8** A level shall start with the ship flying in (GAM-12); the level's clock shall start once it has arrived.
- **LVL-9** A level shall be a list of waves, each entering at its time on the level's clock. A wave is a group of one
  kind of enemy (or a boss) with:
    - a time (seconds from the start of the level's clock);
    - a formation: a **column** sends its enemies one after another at the same place, a given interval apart (0.5 s
      unless stated); a **line** sends them at the same time side by side, a given spacing apart (0.2 unless stated),
      centred on its x (on its y for side entries);
    - an x (0 unless stated) for enemies coming from the top, or a side (left or right) and a y (0.5 unless stated)
      for enemies coming from a side.
- **LVL-10** The level's clock shall stop while a boss is in play (from the moment it appears until it is destroyed),
  so the waves after it wait for the fight to end.
- **LVL-11** Each level shall have two halves: a mini boss comes 6 s after the first half's last wave; the second
  half's first wave comes 3 s (on the level's clock) after the mini boss came, whenever it is destroyed; the final
  boss comes 6 s after the second half's last wave.
- **LVL-12** Destroying the mini boss shall make every enemy shot vanish; the level goes on.
- **LVL-13** When the final boss is destroyed, for the next 3 s every enemy left shall blow up (without points) and
  every enemy shot shall vanish, as soon as it appears, while the player plays on to pick up what was dropped
  *(placeholder)*. Then, once every wave has entered and no enemy is left, the level is over: the ship flies away
  (GAM-13) and the level is complete.
- **LVL-14** Losing a life shall restart the level from its beginning (GAM-19).

## What the levels send

The levels shall be made by these rules, with a fixed random seed so they come out the same every time
*(placeholder: not playtested)*.

- **LVL-15** A level's **pool** shall be every enemy whose unlock difficulty (given with each enemy) is at most the
  level's difficulty, without the ground enemies (Turret, Flak Cannon) in worlds 3 and 5.
- **LVL-16** Each half shall have its own **signature** enemies: 2 or 3 of them (drawn at random), the enemies the
  level unlocks (unlock difficulty = d) first, then others of the pool drawn at random.
- **LVL-17** Each half shall use a set of **main** enemies: its signature enemies, plus others drawn from the pool,
  newer enemies more likely (weight 1 + their unlock difficulty), until the set has round(6 + 11 × (d − 1) / 19)
  kinds (6 at difficulty 1, 17 at difficulty 20), or the whole pool if smaller.
- **LVL-18** A half's **threat** shall be the sum of the points of all its enemies (a wave's threat is its count times
  its enemy's points). The first half's goal shall be 8600 + 13900 × ((d − 1) / 19)^0.6 points; the second half shall
  be as hard as a level 2 steps harder: its goal and its group sizes are those of difficulty d + 2 (the formula goes on
  growing past 20).
- **LVL-19** A half shall start with one warm-up wave (a Drone, Weaver, Dart or Mite group from the pool), then add
  waves of its main enemies until its threat reaches its goal; once its threat is past 80% of the goal, the waves added
  are of its signature enemies (the **finale**).
- **LVL-20** Each wave's shape shall be drawn among its enemy's group shapes (listed with each enemy), its size grown
  with the difficulty: max(1, round(base × 1.073^(d − 1))), a line cut down to fit within 2.1 wu across (1.0 wu tall
  when coming from a side).
- **LVL-21** Waves shall be spread over the half in proportion to their threat: the gap after a wave is 46 s × its
  share of the half's threat, times a random 0.8 to 1.2 (times 0.6 in the finale, so its waves come closer
  together), at least 0.8 s. Some waves shall come at the same time as the one before: 15% of them at difficulty 1,
  rising to 35% at difficulty 20.
- **LVL-22** The waves' times shall then be stretched so that the half's last wave comes exactly 46 s after its first.
  The first half's first wave comes 2 s into the level.

## Backgrounds

- **LVL-23** Each level shall have a background matching its world, kept dark and muted so that bullets and enemies
  stand out. The grounds shall fade into haze towards the top of the screen.
- **LVL-24** The ground shall scroll down at 30% of the level's scroll speed on screen, as if flying high, so it never
  moves with the flying enemies. Ground enemies move with it (ENM-5).
- **LVL-25** The time of day (day, dusk, night) shall tint the ground, its haze and the sky: dusk warmer, night darker
  and bluer; lights (windows, flames) keep their colors.
- **LVL-26** Clouds (from 0, none, to 1, the most) shall be soft see-through clouds in two layers between the ground
  and the ships, up to 10 per layer, drifting down a bit faster than the ground and slightly sideways in a wind, pale
  and in the color of the air (dimmer at night, but less than the ground). Ships and bullets shall always be drawn over
  them.
- **LVL-27** Behind the menus there shall be a space background: stars, faint nebula clouds and a distant voxel
  planet, their colors and the planet's size varying with its seed; or the ground of a level (see `04-ui-audio.md`).
- **LVL-28** The kinds of ground shall be:

| Ground | Look |
|--------|------|
| Mountains | Snowy ridges, glaciers, pine forests |
| Forest | A canopy of round treetops, clearings, a winding river |
| Savanna | Golden grassland gently rolling, a pale dry riverbed winding through it, small boulder piles, trees standing alone (more along the riverbed) |
| Farmland | Patchwork fields (wheat, crops, plowed earth, lavender), hedges, orchards, farms with silos and greenhouses, dirt roads |
| Salt pan | A flat salt crust cracked into polygon plates with raised edges, pools of brine |
| Badlands | Bare ridges eroded into branching gullies, striped in colored layers, sandy floors |
| Refinery | Tanks, pipe yards, plants with glowing furnaces, cooling towers, flaming stacks |
| City | A sci-fi city: blocks of towers with lit windows, street lights, red beacons |

- **LVL-29** Every ground shall also have **outposts**: small compounds set where the ground is flattest (dry and open:
  in a forest's clearings, not on reeds). About a third shall stand on a concrete apron with painted lines, packed;
  the others on the bare ground, looser, about a third of their lots left empty *(placeholder)*. The ground under each
  shall be levelled and blend back into the land around it; on the city, the refinery and the farmland a compound
  takes the place of what stood there. Compounds are 0.26 to 0.4 across; they are close together on the natural grounds
  (spacing 0.75) and further apart on the built-up ones, city, refinery and farmland (spacing 1.1) *(placeholder)*.
- **LVL-30** A compound shall be cut into a few lots: its main buildings first, the rest picked among its others:

| Compound | Main buildings | Others |
|----------|----------------|--------|
| Airfield | A hangar, a landing pad | Hangars, containers, an antenna mast, a tank, an industrial hall, pads |
| Radar station | A radar, an antenna mast | Radars, a dome, an industrial hall, containers |
| Factory | Two industrial halls | Containers, tanks, a flaring stack, halls, a hangar |
| Depot | Container stacks, an industrial hall | More containers, a tank, an antenna, a hangar |
| Colony | A dome, a landing pad | Domes, energy pylons, an antenna, a radar |

- **LVL-31** The buildings shall be: hangars (vaulted halls, sometimes two side by side, a dark door with a light over
  it), industrial halls (sawtooth roofs with glazed teeth or flat roofs with vents, loading doors, sometimes an office
  block), container stacks (one to three high, in rows), radars (a dish looking up, or a radome on a tower), domes (on
  a ring wall with a glowing cyan band; some glass, with plants inside), antenna masts (a red light at the tip),
  landing pads (eight-sided, a painted ring and cross, cyan lights, sometimes a small craft parked), energy pylons
  (six-sided spires with glowing rings and a crystal).
- **LVL-32** Each ground shall pick its compounds:

| Ground | Compounds |
|--------|-----------|
| Mountains | Radar stations (twice as likely), colonies, airfields |
| Forest | Factories, depots, radar stations, airfields |
| Savanna | Airfields, depots, radar stations |
| Farmland | Airfields, depots, factories |
| Salt pan | Airfields, depots, factories |
| Badlands | Factories, depots, radar stations |
| Refinery | Factories, depots, airfields |
| City | Colonies, airfields, radar stations |

## Worlds

- **LVL-33** The worlds and levels shall be as follows (difficulty and scroll speed follow LVL-6 and LVL-7):

### World 1: Highlands (mountains)

| Level | Name | Difficulty | Speed | Time | Clouds | Ground's details | Mini boss | Final boss |
|-------|------|-----------:|------:|------|-------:|------------------|-----------|------------|
| 1-1 | High Peaks | 1 | 0.2 | day | 0.1 | as it is | Sentinel | Avalanche |
| 1-2 | Pine Ridge | 2 | 0.206 | night | 0.5 | bigger ranges, smaller crests | Thresher | Frostjaw |
| 1-3 | Glacier Pass | 3 | 0.212 | day | 0.45 | more haze, greyer snow | Prowler | Iron Summit |
| 1-4 | Stormcrest | 4 | 0.217 | dusk | 0.9 | bigger crests | Pulsar | Stormpeak |
| 1-5 | Dusk Peaks | 5 | 0.223 | dusk | 0.2 | smaller ranges | Rockbreaker | Ridgebreaker |
| 1-6 | Summit | 6 | 0.229 | night | 0.7 | bigger ranges and crests | Warden | Highlord |

### World 2: Wildwood (forest)

| Level | Name | Difficulty | Speed | Time | Clouds | Ground's details | Mini boss | Final boss |
|-------|------|-----------:|------:|------|-------:|------------------|-----------|------------|
| 2-1 | Greenwood | 3 | 0.212 | day | 0.3 | as it is | Patrol Drone | Ironbark |
| 2-2 | Riverbend | 4 | 0.217 | dusk | 0.1 | more and wider rivers | Cyclone | Thornback |
| 2-3 | Deep Canopy | 5 | 0.223 | night | 0.6 | bigger treetops, fewer rivers | Siege Pod | Rootmaw |
| 2-4 | Autumn Wood | 6 | 0.229 | day | 0.5 | autumn colors (brown, dark red, olive) | Delta Raider | Wildfire |
| 2-5 | Twilight Grove | 7 | 0.235 | dusk | 0.85 | smaller treetops | Breacher | Grovekeeper |
| 2-6 | Moonlit Woods | 8 | 0.241 | night | 0.2 | as it is | Harvester | Old Growth |

### World 3: Lush Veld (savanna, green-season colors; no ground enemies)

| Level | Name | Difficulty | Speed | Time | Clouds | Ground's details | Mini boss | Final boss |
|-------|------|-----------:|------:|------|-------:|------------------|-----------|------------|
| 3-1 | Lush Veld | 5 | 0.223 | dusk | 0.21 | the world's look | Turbine | Bogmaw |
| 3-2 | Winding Sands | 6 | 0.229 | day | 0.05 | tighter riverbed bends | Clamp Barge | Mirelord |
| 3-3 | Kopje Country | 7 | 0.235 | night | 0.5 | twice the rocky outcrops | Spire | Fenwraith |
| 3-4 | Acacia Dusk | 8 | 0.241 | dusk | 0.4 | more lone trees | Twin Fang | Hydra |
| 3-5 | Long Grass | 9 | 0.246 | day | 0.85 | bigger rolling land | Frigate | Marsh Titan |
| 3-6 | Veld by Night | 10 | 0.252 | night | 0.3 | the world's look | Tidebreaker | Drowned King |

### World 4: Heartland (farmland)

| Level | Name | Difficulty | Speed | Time | Clouds | Ground's details | Mini boss | Final boss |
|-------|------|-----------:|------:|------|-------:|------------------|-----------|------------|
| 4-1 | Harvest Dusk | 7 | 0.235 | dusk | 0.1 | as it is | Picket | Scarecrow |
| 4-2 | Golden Fields | 8 | 0.241 | day | 0.4 | mostly wheat fields | Bulwark | Combine |
| 4-3 | Lavender Rows | 9 | 0.246 | night | 0.6 | mostly lavender fields | Borer | Locust |
| 4-4 | Orchard Country | 10 | 0.252 | day | 0.2 | more orchards and hedges | Silo Hauler | Granary |
| 4-5 | Hay Moon | 11 | 0.258 | night | 0.85 | more farms | Bastion | Harrowmaster |
| 4-6 | Last Harvest | 12 | 0.264 | dusk | 0.5 | more greenhouses, bigger blocks | Reaper | Black Harvest |

### World 5: Rust Pan (salt pan, copper colors; no ground enemies)

| Level | Name | Difficulty | Speed | Time | Clouds | Ground's details | Mini boss | Final boss |
|-------|------|-----------:|------:|------|-------:|------------------|-----------|------------|
| 5-1 | Rust Pan | 9 | 0.246 | dusk | 0 | the world's look | Enforcer | Maelstrom |
| 5-2 | Copper Flats | 10 | 0.252 | night | 0.3 | fewer pools | Hive Carrier | Man O' War |
| 5-3 | Brine Pools | 11 | 0.258 | day | 0.6 | more pools | Hover Tank | Typhoon |
| 5-4 | Mineral Dusk | 12 | 0.264 | dusk | 0.15 | the world's look | Cryo Fortress | Tsunami |
| 5-5 | Dust Storm | 13 | 0.269 | day | 0.9 | thick haze | Sentry Grid | Abyssal |
| 5-6 | Night Crust | 14 | 0.275 | night | 0.45 | the world's look | Leviathan | Kraken |

### World 6: Bright Ridges (badlands, rainbow-striped)

| Level | Name | Difficulty | Speed | Time | Clouds | Ground's details | Mini boss | Final boss |
|-------|------|-----------:|------:|------|-------:|------------------|-----------|------------|
| 6-1 | Bright Ridges | 11 | 0.258 | day | 0.3 | the world's look | Relay Array | Mesa |
| 6-2 | Striped Gullies | 12 | 0.264 | night | 0.1 | smaller, tighter ridges | Scavenger | Dust Devil |
| 6-3 | Ochre Walls | 13 | 0.269 | dusk | 0.6 | narrower sandy floors | Mine Carrier | Landslide |
| 6-4 | Red Dusk | 14 | 0.275 | dusk | 0.2 | the world's look | Foundry | Basilisk |
| 6-5 | Rainbow Breaks | 15 | 0.281 | day | 0.85 | bigger ridges | Gunship Prime | Sandworm |
| 6-6 | Dark Strata | 16 | 0.287 | night | 0.5 | the world's look | Colossus | Monolith |

### World 7: Ironworks (refinery)

| Level | Name | Difficulty | Speed | Time | Clouds | Ground's details | Mini boss | Final boss |
|-------|------|-----------:|------:|------|-------:|------------------|-----------|------------|
| 7-1 | Refinery | 13 | 0.269 | day | 0.4 | as it is | Grappler | Furnace |
| 7-2 | Tank Farm | 14 | 0.275 | night | 0.15 | mostly tanks | Tugmaster | Smokestack |
| 7-3 | Smelter | 15 | 0.281 | dusk | 0.6 | as it is | Magma Rig | Slag King |
| 7-4 | Pipe Maze | 16 | 0.287 | day | 0.9 | mostly pipe yards | Dreadnought | Forgemaster |
| 7-5 | Flare Stacks | 17 | 0.293 | night | 0.3 | mostly flaming stacks | Flare Rig | Inferno |
| 7-6 | Meltdown | 18 | 0.298 | dusk | 0.85 | mostly plants and cooling towers | Crucible | Reactor |

### World 8: Metropolis (city)

| Level | Name | Difficulty | Speed | Time | Clouds | Ground's details | Mini boss | Final boss |
|-------|------|-----------:|------:|------|-------:|------------------|-----------|------------|
| 8-1 | Neon City | 15 | 0.281 | dusk | 0.2 | as it is | Executor | Neon Tyrant |
| 8-2 | Downtown | 16 | 0.287 | day | 0.1 | more towers | Interdictor | Gridlock |
| 8-3 | Skyline | 17 | 0.293 | day | 0.5 | more towers and mid-rise buildings | Nightwatch | Blackout |
| 8-4 | Neon Rain | 18 | 0.298 | night | 0.9 | as it is | Arc Tower | Skybreaker |
| 8-5 | Night Grid | 19 | 0.304 | night | 0.35 | smaller blocks, fewer parks | Apex | Sovereign |
| 8-6 | The Core | 20 | 0.31 | dusk | 0.7 | the most towers | Overmind | Singularity |
