# Decisions and Open Questions

> Claude appends here when it has to choose something the specs don't cover.
> Review regularly: move answers into the proper spec file, then delete the entry or mark it resolved.

## Open questions

### 2026-09-29 — Scrolling, play area and camera (00-vision.md is all TBD)
- Context: the user chose 3D with cubes (see "Decisions made"); the rest is still a placeholder.
- Placeholder chosen: vertical scroller, 3:4 portrait play area 1.5 x 2.0 world units, window 675x900 (was 600x800).
  Gameplay stays flat (2D rules); only the rendering is 3D. Perspective camera with a 40° vertical field of
  view, in front of and below the play area, tilted 25° so the top of the screen is farther away; it backs
  off until the whole play area fits. The player's ship rolls up to 25° when moving sideways.
  `CAMERA_FOV` / `CAMERA_TILT` in `config.py`, bank angle in `app.py`.
- Recorded as a placeholder in 00-vision.md ("Genre and perspective") and 06-technical.md ("Window").
- Options: vertical / horizontal scroller; more or less tilt (0° looks flat, like the old 2D view).

### 2026-09-29 — Unit of "Movement speed: 1.0"
- Context: 01-gameplay.md gives speed 1.0 without a unit.
- Placeholder chosen: 1.0 world unit per second, i.e. 2 s to cross the play area vertically,
  1.5 s horizontally (`PLAYER_SPEED`).
- Options: keep, or express as "screen heights per second".

### 2026-09-29 — Amount of inertia and ship size
- Placeholder chosen: velocity eases to target speed with `PLAYER_RESPONSIVENESS = 12` (~0.2 s to reach
  full speed, short drift on release). Ship is a 0.12 x 0.12 cyan square. Both in `config.py`.

### 2026-09-29 — Health, damage, level restart and continue
- Placeholder chosen: 5 health per life; enemy bullet 1 damage, enemy ramming the ship 2 damage (the
  enemy dies, no points). Losing a life restarts the level from the beginning and puts the score back to
  what it was when the level started (so replaying waves can't farm points). "Continue" after game over
  restarts the current level with 5 lives and score 0. Score and remaining lives carry over to the next
  level. In `config.py` / `world.py` / `app.py`.
- Questions: are these values right? Should continue keep the score?

### 2026-09-29 — Firing details
- Placeholder chosen: holding Space auto-fires every weapon (auto-fire is TBD). Ctrl (bomb) does nothing
  yet: its effect is TBD.
- Auto-fire recorded as a placeholder in 01-gameplay.md ("Controls").

### 2026-09-29 — Weapon details the spec doesn't cover
- Placeholder chosen: an enemy touched by the laser flashes white the whole time. Only kills by the
  player's weapons (not ramming) score and can drop pickups; the enemies a missile explosion destroys count
  too. Score and weapon levels carry over to the next level. The weapon HUD sits just above the health bar.
  Pickups are colored capsules showing their letter; repair is white with a red cross.
- Laser flash recorded as a placeholder in 05-visuals.md ("Hit flash"), weapon HUD position in 04-ui-audio.md.

### 2026-09-29 — Menus, keys and HUD layout (04-ui-audio.md is empty)
- Placeholder chosen: text-only screens for each state of the global state machine, driven by keys:
  main menu Enter/Q, level select Enter/Escape, pause Escape (resume) / Q, game over Enter (continue) /
  Escape (main menu). Pause "quit" goes to the main menu; Q on the main menu closes the game.
  HUD: score top-left, lives top-right, health bar bottom-center.
- Recorded as a placeholder in 04-ui-audio.md ("Game flow", "Screens", "HUD").

### 2026-09-30 — Bosses (asked by the user in chat)
- Context: the user asked for bosses with their own health bar and several shooting patterns, some fighting in
  phases, with parts that can be destroyed, which changes how they shoot; then for a boss at the end of every level,
  each one new (answered in chat). The Bosses block in 02-enemies.md was all TBD.
- Placeholder chosen: 40 bosses, one per level, about 6 s after its last wave. Each world's keep to its theme and
  get harder level by level (more health, parts and phases, denser patterns) up to its big boss at x-8: Warden,
  Harvester, Tidebreaker, Colossus, Overmind. Every boss has at least two phases; some have no parts and change phase
  on their health, most have an armored core until their parts are destroyed. All numbers are in 02-enemies.md
  ("Bosses", written from the data) and `src/pewpy/boss_catalog.py`; the health bar is at the top (04-ui-audio.md,
  "HUD"). Checked with a simulated player (bullets level 1 and 3, tracking the boss without dodging): each fight
  takes about 6 to 32 s.
- How: a boss is a core (`Boss`) plus parts (`BossPart`), each an enemy of the world, so everything that hits
  enemies hits them; the core moves them and fires every gun. Guns and phases are data (`Gun`, `Phase`,
  `BossSpec`); a level spawns a boss with a wave like `{"time": 71, "enemy": "warden"}`. Bosses and their parts
  don't leave the screen and can't be rammed away. Their models are drawings in `src/pewpy/models/`, shown whole
  on the Models screen, one page per world. Tests check that every part can be shot from below and that every
  hitbox has its drawing's shape.
- Options: a time limit; more than one boss per level; levels without a boss.

<!-- Format:
### YYYY-MM-DD — Short title
- Context: why the question came up
- Placeholder chosen: what Claude implemented for now (and where to change it)
- Options: A / B / C
-->


### 2026-09-29 — Level file fields
- Placeholder chosen: fields of the JSON level files (the format itself is now in 03-levels.md): `name`,
  `scroll_speed` (world units/s), `waves`. Each wave: `time` (seconds from level start, required), `enemy`
  (`drone`, `weaver`, `diver`, `gunship`, `turret`, `swarmer`, `sniper`, `mine_layer`, `shield_carrier`,
  `splitter`), `count`, `formation` (`"line"` / `"column"`), `x`, `spacing`, `interval`, and for enemies that
  enter from the side (`swarmer`, `mine_layer`) `side` (`"left"` / `"right"`) and `y`. Typos and unknown
  values are reported with the file and wave number. `pre-commit` formats these files one field per line.
- Options: TOML or YAML (easier to hand-write, needs a library on Python 3.10), or Python files.

### 2026-09-29 — Enemy details the specs don't cover
- Placeholder chosen: enemy models follow the colors and rough shapes of 02-enemies.md (the Weaver is a
  diamond, the Diver an arrowhead, the Shield Carrier's "outline" is a bubble). A Splitter rammed by the
  player doesn't split. Mines count as enemies, so a level only
  ends once its mines have scrolled off screen or been shot. Enemies only shoot once on screen. Enemy
  drops aren't implemented yet (they come with weapons and pickups).
- Difficulty: a test bot that only sweeps left and right while firing takes about 22–26 hits per level,
  roughly 4–5 lives at 5 health per life. It probably needs tuning once you play it.

### 2026-09-29 — Level end and new LEVEL_COMPLETE state
- Placeholder chosen: a level ends when every wave has entered and no enemy is left. This needed a state
  that is not in the spec's list: LEVEL_COMPLETE ("Enter: next level", or "ALL LEVELS COMPLETE / YOU WIN"
  after the last level, then main menu).
- Question: OK to add it to the "Global state" list in 01-gameplay.md, or should it work differently?
- Recorded as a placeholder in 04-ui-audio.md ("Game flow"); 01-gameplay.md's state list is unchanged.

### 2026-09-29 — Background
- Placeholder chosen: 3-layer parallax starfield scrolling at the level's `scroll_speed`, frozen in menus
  and pause. `background.py`, `STAR_COUNT` in `config.py`.
- Recorded as a placeholder in 05-visuals.md ("Background").
- Superseded by "Per-level backgrounds" below (the starfield is still used by the space and debris levels).

### 2026-09-29 — Details of the per-level backgrounds
- Context: the user chose per-level backgrounds, dark and muted (see "Decisions made"); the details are mine.
- Placeholder chosen: each level file has a `background` field: `space` (level 1: stars, 5 faint nebula clouds,
  a distant voxel planet turning slowly), `planet` (level 2: dusty brown voxel hills and craters, no stars),
  `debris` (level 3: stars and tumbling voxel asteroids at two depths). Stars fill the whole visible area
  (they only covered the play area before, leaving the top of the screen empty) and are drawn behind
  everything. The ground is a 4.2-unit seamless loop built when the level starts, with less shine than the
  ships. On screen it moves at 30% of the scroll speed (`GROUND_SPEED`), as if flying high: at the scroll
  speed, Drones (only a bit faster) looked like they sat on the ground. 30% is the farthest from every level 2
  enemy (parked Snipers 0, Gunships 60%, Turrets 100%, Drones 120%, Weavers 140%). Asked by the user in chat:
  turrets keep the scroll speed and slide over the ground; 02-enemies.md ("fixed to the ground") is unchanged.
  The main menu shows the space background. Depths, counts and speeds are constants at the top of
  `background.py`; colors in `models.py` (`GROUND_COLORS`, `ROCK_COLORS`, `PLANET_COLORS`) and
  `background_view.py` (`CLOUD_COLORS`, `GROUND_LOOK`).
- Ground voxel size (picked by the user in chat, after trying 0.0175, 0.025 and 0.04 on a test copy, level 4):
  level 2 uses `"ground_voxel": 0.04` in its level file (default 0.07). Hills keep the same size in the world;
  only the squares get smaller. Voxels buried on every side aren't drawn.
- Performance (software rendering, 675x900): ~610 fps space, ~690 fps debris; planet ~99 fps with 0.04
  squares (33k ground triangles, 0.4 s level start; it was ~210 fps with 0.07).
- City (asked by the user in chat, on level 4 "Neon City", a copy of level 2's waves): `"background": "city"`.
  A sci-fi city at night made of 0.04 voxels: a looping street grid (`CITY_BLOCK`, `CITY_STREET`), blocks split
  into 1-3 lots per side, one building per lot (mostly low and mid-rise, a few towers up to `CITY_MAX_HEIGHT`,
  some empty plazas). It sits deeper than the hills (`CITY_DEPTH` 0.7) so towers stay behind the ships.
  Buildings alternate floor slabs and rows of windows; some windows are lit (dim teal or amber), drawn by the
  shader as a glowing pane in each voxel face; roofs carry small machinery blocks; each tall tower has one dim
  red beacon; streets have a few dim cyan lights. Nothing pink, so enemy bullets stay easy to spot. Colors in
  `models.py` (`BUILDING_COLORS`, `WINDOW_COLORS`, …), shine in `background_view.py` (`CITY_LOOK`).
  ~104 fps, 0.7 s level start (61k ground triangles).
- Options: use the city for a real level (level 4 is still a copy of level 2's waves); neon signs, flying traffic.
- Ocean (asked by the user in chat, level 5 "Archipelago", with level 1's waves since turrets make no sense on
  water): `"background": "ocean"`. Voxel islands (0.04) in a sea: land where smooth noise is highest, the sea
  level picked so `ISLAND_SHARE` (22%) of the map is land whatever the random values; sandy beaches, grass,
  forest and rocky peaks in bands, muted (`ISLAND_COLORS` in `models.py`). The water is one flat surface per
  strip (not voxels), dark blue and lighter in the shallows near the coasts; the shader sways its normal with
  moving waves for small glints and some reflection, kept low so the sea stays dark behind the bullets. The
  waves continue across strips and repeat exactly once per loop, so there are no seams. The sea sits at
  `SEA_DEPTH` 0.5, islands rise up to `ISLAND_MAX_HEIGHT`. ~160 fps, 0.1 s level start (11k ground triangles).
- Options: clouds drifting between the ship and the sea; boats; foam along the coasts.

### 2026-09-29 — Levels 6 to 15 (asked by the user in chat: "be creative with the backgrounds, keep it in the atmosphere, no space")
- Placeholder chosen: ten new levels, each flying over its own voxel ground (0.04 voxels):
  6 Dune Sea (desert: dune ridges, rock mesas, oasis pools with palms), 7 Greenwood (forest canopy, clearings, a
  winding river), 8 Red Canyon (layered cliffs down to a river), 9 Patchwork (farmland: wheat, crops, plowed
  earth, lavender, hedges, orchards, farms with silos), 10 Pack Ice (ice floes and icebergs on a dark sea),
  11 Ember Fields (black volcanic hills, glowing lava rivers and cracks, at night), 12 Mire (swamp: muddy islets,
  reeds, dead trees), 13 Cloud Deck (flat moonlit clouds, with town lights far below in the gaps), 14 Refinery
  (tanks, pipe yards, plants with glowing furnaces, flaming stacks, at night), 15 High Peaks (snowy ridges,
  glaciers, pine forests). Every one has haze: the farther ground (top of the screen) fades into the color of
  the air. All kept dark and muted; lava is red rather than orange, and nothing is pink, so bullets stand out.
- Waves: each level has its own mix of enemies to suit it (no turrets over water or clouds), a warm-up, about
  16 waves and a finale; counts grow a little and waves come a little faster from level 6 to 15. Not
  playtested: the difficulty probably needs tuning.
- How: each kind of ground is a `Biome` in `terrain.py` (a generator, depth, height, water, haze, sky color);
  its colors are a painter in `ground_look.py`. Burning voxels (lava, flames) shine all over and flicker.
- Fixed on the way: level 2's hills could reach 0.04 behind the play plane, touching the ships (about 0.1
  deep); their base is now at depth 0.35.
- Performance (software rendering): 78 to 180 fps, 0.2 to 0.8 s level start.
- Options: other settings per level (city, ocean, space station…); more variety along a level (the ground
  repeats every ~17 s at level 2's speed); scenery obstacles that collide (03-levels.md says "none" for now).

### 2026-09-29 — Level select keys
- Placeholder chosen: number keys 1-9 pick a level in the level select screen.
- Superseded by "Menus picked with the arrow keys" (the number keys are gone).
- Recorded as a placeholder in 04-ui-audio.md ("Title / main menu").

## Decisions made

### 2026-10-01 — The code in subdirectories (asked by the user in chat)
- Decision (the user's): organize the code into subdirectories.
- Placeholder chosen (06-technical.md's "Overall structure" is TBD), grouped by domain, the game's rules kept apart
  from Panda3D so they're tested without a window:
  - `pewpy/`: `app.py` (the window, input, drawing; the entry point), `config.py`, `data.py`, `__main__.py`;
  - `pewpy/game/`: the rules, no Panda3D: entities, player, weapons, world, states, level, enemies, fleet,
    roster, bosses, boss_catalog;
  - `pewpy/scenery/`: backgrounds and grounds: their shapes and layouts (background, terrain, relief, landscapes,
    settlement) and drawing them (background_view, ground_look, ground_shader, prop_meshes);
  - `pewpy/graphics/`: models, vox, lighting, sprites, effects, effects_view;
  - `pewpy/ui/`: menu, menu_view, showcase, ship_select_view, level_preview;
  - data unchanged: `pewpy/levels/`, `pewpy/models/`.
- Modules moved with `git mv` (their history follows), every import rewritten; nothing else changed. Earlier
  entries below name modules where they were then.

### 2026-10-01 — Real 3D models: 3D drawings and MagicaVoxel (asked by the user in chat: option C + B)
- Decision (the user's): of the ways to make models real 3D voxels, try B (3D drawings as layers) + C (MagicaVoxel
  import); the automatic sculpting (D) was tried and reverted.
- Done: a model file (`models/<name>.json`) is one of three forms, all read into the same cubes (`load_voxels`):
  a flat drawing as before (rows, each color a thickness), a 3D drawing ("layers": slices from the top, nearest
  the camera, down, the middle one on the model's middle plane; a palette of colors), or a MagicaVoxel model
  ("vox": a .vox file next to it; lying on the ground seen from above, its z up towards the camera). Engines can
  have a "z" (cubes above the middle plane). `vox.py` reads and writes .vox files (the first model; the palette;
  no palette means grey). `tools/voxels.py` (`make voxels ARGS="..."`): export a model to .vox (to edit it in
  MagicaVoxel), use its .vox, or turn it into layers; engines are kept. The packaged game includes .vox models.
- The aircraft candidates (tools/make_candidates.py) are now real 3D: round fuselages, a canopy on top, thin
  wings rising a little to their tips, upright fins taller at the back, pods and guns underneath. The industrial
  ships and the bosses are still flat drawings. No existing model was changed.

### 2026-09-30 — Clouds above the mountains (asked by the user in chat: peaks went higher than the clouds)
- The see-through clouds were at fixed depths (0.08 and 0.18 behind the ships), but the mountains' peaks reach 0.2
  and the planet's hills 0.14, so peaks showed through or in front of them. Now each cloud layer is at most 40 %
  and 75 % of the way from the ships down to the ground's highest point (`mist_depths` in background.py): over the
  mountains 0.08 and 0.15, over the hills and the city about 0.06 and 0.11.

### 2026-09-30 — A denser city (asked by the user in chat: smaller buildings, more roads)
- Blocks about 0.38 across (were 0.6), streets 0.07 wide (were 0.1), 40 % of blocks cut in two by a 0.035 alley,
  lots from 0.06 (were 0.1), and a little lower: towers 0.31 to 0.48, mid-rises 0.12 to 0.26, low buildings 0.03
  to 0.11. `CITY_*` in settlement.py.

### 2026-09-30 — Bigger city windows (asked by the user in chat: too small, they looked like they flickered)
- Windows were 2 to 3 pixels at 1280 x 1024, so they landed on different pixels as the city scrolled. Now about
  twice as big (offices 0.022 x 0.03, homes 0.026 x 0.034, the refinery's furnaces 0.035), their edges softened
  over a pixel (`window` in ground_shader.py's prop shader), so they don't shimmer.

### 2026-09-30 — A 1280 x 1024 window (asked by the user in chat)
- Decision (the user's): the default window is 1280 x 1024 (5:4, landscape; it was 675 x 900, 3:4 portrait), with
  the levels' and enemies' movements adapted.
- How: the play area keeps its height (2.0) and widens to 2.5 (it was 1.5), so speeds, entry and stop heights and
  timings stay as they were; what goes across the screen is widened by `WIDTH_SCALE` (5/3): the waves' x and line
  spacings in every level, the Weaver's and Albatross's weaves, the side-entry enemies' crossing speeds (Mine
  Layer, Bomber, Kestrel, Manta, Broadside: they cross in the same time), the Swarmer's turn (its curve reaches as
  far in) and the bosses' sway. Enemies bouncing off the edges, spawning, the grounds and the camera follow the new
  width by themselves. The screen now shows to about x ±1.86 at the sides.
- Screens reworked for the wide shape: the level preview is to the right of the list, the ship select packed under
  its menu with wider columns, and the model screens' circle is an ellipse as wide as the screen allows
  (`SHOWCASE_STRETCH`), the models going round it.
- Checked: the bot finishes all 40 levels and meets all 29 new enemies.

### 2026-09-30 — Boss candidates (asked by the user in chat)
- Decision (the user's): a script to generate boss candidates, a main menu entry to see them, and a make target.
- Done: `tools/make_boss_candidates.py` (`make boss-candidates ARGS="..."`: `--count` (default 40), `--seed`,
  `--pool`, `--out`, `--append`), writing into `models/boss_candidates/`. Like the game's bosses, each is a core
  (41 to 71 cubes wide, thicker than the enemies: 3 to 17 cubes) and destroyable parts on it: `NNN.json` (the core,
  with its engines), `NNN_a.json`... (the parts) and `NNN.parts.json` (where they go, in cubes from the core's
  middle). Cores: carrier, dreadnought, station, hammerhead, twin hull, flying wing, crescent, modular (a fifth
  lopsided), with superstructure, a bridge, hangar bays, armor bands, engine banks, lights, and a thin socket under
  each part; parts: turrets, cannons, generators, missile launchers, drills (0 to 7 per boss). The most different
  are kept, as for the enemies. `tools` is now a package: the boss script uses the enemy script's pieces.
- Main menu: "Candidates" became "Enemy candidates", and "Boss candidates" is new (6 per page, same scale).
- Then more diversity and bigger bosses (asked by the user): 18 core families (adding citadel, spider, trident,
  barge, mothership, chain, fortress, blade, gunline, ring cluster), a quarter combining two, 0 to 3 appendages
  (big wings, arms with pods, armor spikes, a halo ring, engine nacelles, radiator panels, masts), sizes medium (41
  to 61 cubes wide), large (up to 85) or huge (up to 115, half the screen), paint schemes (plain, two-tone, glowing
  seams), 11 kinds of parts sized to the boss (adding missile pods, beam emitters, shield nodes, radar dishes, flak
  guns, claws), up to 10 on the biggest, a few kinds per boss. The kept ones are also chosen to differ by family,
  paint and parts. The screen shows 4 per page, drawn bigger (a 125-cube boss fills its place).

### 2026-09-30 — The second fleet: 29 enemies from the model candidates (asked by the user in chat)
- Decision (the user's): candidates 001, 008, 011, 024, 025, 037, 041, 059, 065, 068, 087, 095, 109, 146, 172, 206,
  219, 232, 237, 239, 251, 266, 272, 281, 297, 365, 372, 412 and 422 (024 was listed twice) become enemies, each
  with its own game logic.
- Placeholders chosen: their names and every behavior and number (catalog in 02-enemies.md, "The second fleet";
  `fleet.py`). New mechanics among them: entering from the bottom (Tick), blinking and untouchable while hidden
  (Wisp), armored except while firing (Rampart), carriers launching smaller enemies (Behemoth: Darts; Brood:
  Sparks), shells timed to burst where the player was (Howitzer), sweeping streams (Stormcrow), twin beams
  (Pincer), and models turning to face where they fly (Dart, Tick, Spark).
- In the levels: two waves in each level, in its two biggest gaps, by difficulty (small ones in world 1, fighters
  in world 2, gunships in world 3, heavies in worlds 4 and 5), heavies at least 22 s before the boss. Checked:
  a bot that never dies finishes all 40 levels and meets all 29.
- The enemy names the levels use moved to `roster.py` (both enemies.py and fleet.py). The Models screen has two
  pages for them.

### 2026-09-30 — Model candidates for new enemies (asked by the user in chat)
- Decision (the user's): a new main menu screen to view model candidates, and 100 generated enemy models (models
  only, no game logic), numbered, to pick the ones to turn into new enemies.
- Done: "Candidates" on the main menu, like the Models screen, 10 numbered models per page (Previous page added
  to the Models and Bosses screens too), all drawn to the same scale, labelled with their number and size in cubes.
- Then more diversity (asked by the user: too many near-identical round ships; bigger and smaller ones, not all
  symmetric): the drawings (`models/candidates/001.json` to `100.json`, made by a generator not in the repo) are a
  core hull (spindle, block, wedge, egg, segmented, cross, crescent, frame, diamond, arrowhead) plus 1 to 3
  attachments (delta, swept or straight wings, biplanes, nacelles, booms, mandibles, fins, turrets, a side cannon,
  containers, radiators, antennas), from 7-cube drones to 35-cube heavies, a third of them lopsided (parts on one
  side, an off-centre cockpit). Out of 600 generated, the 100 kept are the most different from each other
  (outline, size, proportions), picked separately among symmetric and lopsided ones. Enemy greys, a teal cockpit,
  a sensor, one accent color, a hull tint (8), sometimes a painted livery panel; engines with flames at the back.
- Then a new batch of 200 (asked by the user: plane-like ones had wings too thick; make them aerodynamic): 90
  aircraft from their own generator (a slender fuselage with an ogive nose; thin wings tapering to their tips:
  swept, delta, cranked, forward-swept, ogival or long and straight; a tailplane or canards; thin fins; engines at
  the tail or in slim underwing pods; a light leading edge and dark flap line; wing markings one cube thick), 65
  symmetric and 45 lopsided industrial ships (their wings taper too), kept out of 1400 generated as the most
  different within each group. 20 pages on the Candidates screen.
- The generator is now in the repo (asked by the user, to try many times): `tools/make_candidates.py`, or
  `make candidates ARGS="..."`: `--count`, `--kind aircraft|industrial|all`, `--seed` (printed each run, to make a
  batch again), `--pool`, `--out`, `--append`. It replaces the candidates unless `--append`.
- Next: the user picks numbers; the chosen drawings move to `models/` with a name, and get enemy logic.

### 2026-09-30 — Level preview on the level select (asked by the user in chat)
- Decision (the user's): a preview window of the level in the level selection menu.
- Placeholder chosen: a framed window above the list (`FRAME` in level_preview.py), showing the highlighted
  level's background live, scrolling at the level's speed, with its time of day, clouds and sky: a second camera
  placed like the game's but seeing only the middle of the ground, drawing its own scene into its own display
  region (under the menus). Hidden on "Back". Each preview is built once while on the level select.
- Recorded in 04-ui-audio.md (main menu entries).

### 2026-09-30 — Frame rate under WSL, and lighter trees (the user got 24 fps in level 2-2)
- Cause: under WSL, OpenGL defaulted to Mesa's CPU renderer (llvmpipe), not the GPU; the new grounds' pixel
  shaders and the farmland's hundreds of trees were heavy for it. Through WSL's GPU path (Mesa's d3d12 driver,
  `GALLIUM_DRIVER=d3d12`) the same level renders at over a thousand frames per second.
- `make run` now uses the d3d12 driver when WSL's GPU device (`/dev/dxg`) is there. That driver can hang while the
  window closes, so the game leaves at once when it's in use (`finalizeExit` in app.py).
- Also lighter for the CPU renderer: trees are crowns only (7 sides, 3 rings, no trunk: 100k triangles down to 23k
  in level 2-2), orchard trees a bit farther apart (0.042), and the ground shader uses fewer noise layers (about 10
  lookups a pixel instead of 28). Level 2-2 on the CPU renderer: ~32 to ~50-65 fps (noisy measurements).

### 2026-09-30 — Frames per second on screen (asked by the user in chat)
- Decision (the user's): an FPS counter in the top-right corner.
- Placeholder chosen: small dim text ("552 FPS") at the game area's top-right corner on every screen, averaged over
  the last second and refreshed twice a second; `SHOW_FPS` in `config.py` (on) turns it off. Not Panda3D's own
  meter, which would sit in the letterbox bars on a wide window.
- Recorded in 04-ui-audio.md (HUD).

### 2026-09-30 — Smooth, near-photorealistic grounds: option A prototype (asked by the user in chat)
- Decision (the user's): grounds should look close to photorealistic, still procedurally generated, not made
  of cubes; of the options (A: procedural shader materials, B: CC0 photo textures, C: B plus erosion, D: scrolling
  images), try A first.
- Prototype, on the mountains biome only (the others are still voxels): `relief.py` makes a smooth height field
  (numpy, looping like the voxel grounds): eroded noise (finer layers damped on steep slopes) plus ridged crests on
  the high ground, flat valley floors; it bakes each point's cavity (hollows get less sky light) and cast shadows
  from a low sun in the top left. `ground_shader.py` draws it as a fine mesh per strip (a point every 0.02 world
  units) with its own shader: rock with strata on steep faces, scree, snow settling on gentle high slopes, meadows
  and pine forest in the valleys, fine bumps on the normal, the same sun as the baked shadows, blue sky light, and
  the level's haze and time-of-day tint. A biome opts in with `Biome.relief`.
- Placeholders: every color, height and threshold in `relief.py` and `ground_shader.py`.
- Then the built-up grounds (asked by the user: keep a similar ground, with models of buildings and items placed
  on it, colors in the same range): the city, the refinery and the farmland are smooth too (level or gently rolling),
  with a layout (`settlement.py`): a surface map the ground shader paints (streets with lamp light at night,
  pavements, stained yards, dirt roads, fields with furrows, pastures) and props standing on it, built with numpy
  (`prop_meshes.py`): buildings (towers with setbacks, roof machinery, red beacons), process plants with furnace
  windows, tanks, flaring stacks, pipe racks, houses, barns, silos, trees, hedges. A prop shader paints windows (more
  lit at dusk and night), furnaces, flames, metal sheen, roofing and foliage. Props cast shadows and darken the
  ground around them: shadows are now a map of how high they reach, read pixel by pixel by both shaders. Colors are
  from the voxel versions' palettes, checked side by side.
- Known limit: ground enemies stay on the play plane, so over the city they can show on a roof rather than a street.
- Then every other ground (asked by the user: "many levels still use the cubes, replace them too"): no level uses
  voxel grounds any more. `landscapes.py` has a landscape per ground: the dusty planet (eroded hills and craters),
  islands in a sea, desert (dune ridges, mesas, oases with palms), forest (a canopy of round crowns, clearings, a
  river), canyon (terraced cliffs down to a river with sandbanks), pack ice (floes split by leads, icebergs),
  volcano (black hills, lava lakes and rivers), swamp (islets with reeds and dead trees) and the cloud deck. Below
  height 0 is the ground's fluid (`Biome.fluid`): water (flat, depth-tinted from the voxel grounds' colors, shallows
  lighter, foam at the coasts, the sun's glints on looping waves), lava (a glowing flow under a drifting crust) or
  the gaps between clouds (the dark ground far below, a few town lights). Shores fall between grid points (the
  depth is signed), and cliff edges span a few grid points, so no edge is jagged. Colors are the voxel grounds'.
- The voxel ground code (terrain.py's generators, ground_look.py, models.py's ground cells) is no longer drawn.

### 2026-09-30 — Thinner models (asked by the user in chat)
- Decision (the user's): most models were too thick; remove 2 layers of cubes.
- Done: every palette height in the drawings (`src/pewpy/models/*.json`) is 2 less (at least 1), so each part lost
  a cube on both faces. Left alone: the drawings only 1 to 3 cubes thick (missile, rocket, the tank's and the
  turret's barrels), which would have gone flat.
- Then the player ships' noses taper (asked by the user: the Vanguard's tip was 5 cubes thick, one is enough):
  Vanguard and Phantom tips 1 cube thick, then 3; Juggernaut's nose 3 thick at the front, its ridge 3, 5, 7 then 9.

### 2026-09-30 — Laser look (asked by the user in chat)
- Decision (the user's): the laser looked boring; it should look like particles of light going at the enemies.
- Placeholders chosen: the solid box is now only a thin flickering core; around it a soft halo of overlapping
  glowing circles; streaks of light (160 a second for the level 1 beam, more when wider) shoot up the beam at 2.8 to
  4.2 units a second, wobbling sideways, and vanish where it ends; glows at the ship's nose and on every enemy it
  burns. Numbers in `effects.py` (`PHOTON_*`) and `effects_view.py`.
- Recorded in 05-visuals.md ("Laser").

### 2026-09-30 — Ground units move with the ground (bug reported by the user in chat)
- The ground scrolls at 30% of the level's speed on screen (03-levels.md), but ground units moved at the full
  scroll speed, so they slid over it and looked like they were floating. They now scroll at `GROUND_SPEED` times
  the level's speed (`World.scroll_speed`), like the ground under them. The Rocket Truck still drives 0.15 faster.
- Consequence: ground units stay on screen about 3.5 times longer if not shot.
- Recorded in 02-enemies.md (ground enemies' speeds).

### 2026-09-30 — A moment after the boss (asked by the user in chat)
- Decision (the user's): once the boss is beaten, enemy bullets and missiles are destroyed and the player plays on
  for 3 seconds to pick up power-ups, before the level ends.
- Placeholder chosen: every enemy still there blows up too (without points), and anything fired during those 3 s
  vanishes at once (a spark where each shot was). `BOSS_BEATEN_TIME` in `config.py`.
- Recorded in 03-levels.md (bosses).

### 2026-09-30 — Player ships (asked by the user in chat)
- Decision (the user's): three player ships, chosen on a ship select screen: a normal one, one with more armor but
  a little slower, and a quick one with low armor that regenerates health when not shooting.
- Placeholders chosen (numbers): Vanguard (normal, the old ship) 5 health, speed 1.0, size 0.12; Juggernaut 8
  health, speed 0.8, size 0.14; Phantom 3 health, speed 1.3, size 0.10, repairs 0.5 health a second once it hasn't
  fired for 1.5 s. Names and numbers in `SHIPS` (`player.py`), drawings `player.json`, `player_heavy.json`,
  `player_light.json`.
- Ship select: from Start, before the world select (Back from the world select returns to it); opens on the ship
  played last. Under the menu, every ship side by side with its name and bars comparing armor, speed, size and repair
  (each scaled to the best of the three); the highlighted one bigger, spinning, with bright bars and its description
  and numbers at the bottom (asked by the user: a view of each ship and its characteristics; `ship_select_view.py`). The Models screen shows
  all three.
- Recorded in 01-gameplay.md ("Ships") and 04-ui-audio.md (flow, main menu).

### 2026-09-30 — Windows package (asked by the user in chat)
- Decision (the user's): a `make package` target building and packaging a Windows executable.
- How: Panda3D's own `build_apps` (settings in `packaging/setup.py`), which works from any OS by downloading the
  Windows wheels of the dependencies (exported from `uv.lock` to `build/requirements.txt`). It freezes the code
  into `pewpy.exe` and copies the level and model files to a `pewpy` folder next to it (`pewpy/data.py` finds them
  there when the game is frozen). The result is `dist/pewpy-<version>_win_amd64.zip` (about 36 MB). `setuptools` and
  `pip` are new dev dependencies (build_apps needs them). Panda3D's list of numpy's hidden imports is still for numpy
  1, so every module of numpy 2's core is included explicitly. Errors of the packaged game (it has no console) go to
  `%LOCALAPPDATA%\pewpy\output.log`.
- Checked on Windows (from WSL): the built `pewpy.exe` starts and runs.
- Recorded in 06-technical.md ("Packaging and distribution").

### 2026-09-30 — More enemies and enemy weapons (asked by the user in chat)
- Decision (the user's): more kinds of enemies with more diverse weapons, some firing missiles, some homing missiles.
- Placeholder chosen (mine): seven enemies (Rocketeer, Hunter, Missile Silo, Bomber, Lancer, Serpent, Buckshot) and
  new weapons: accelerating rockets, homing missiles, cluster bombs, snaking shots, shotgun pellets and a laser beam
  (numbers in 02-enemies.md, "Enemy weapons" and the catalog). Rockets, missiles and bombs are small enemies of
  their own, so the player can shoot them down; they hit like ramming (2 damage). A laser beam goes on through the
  player. Introduced gradually: Rocketeer from 1-2, Serpent from 1-4, Buckshot from 1-6, Hunter from 2-1, Missile
  Silo from 2-2 (ground levels only), Bomber from 2-4, Lancer from 3-1; each level from 1-2 on gets 1 to 3 waves of
  them (1 in Orbit, 2 in Heartland and Waters, 3 in Badlands and Metropolis), a newly introduced one always among
  them. Every level was played through headless to make sure it still ends. The Models screen now has three pages
  (player, pickups and projectiles; flying enemies; ground enemies).
- Recorded in 02-enemies.md and 04-ui-audio.md ("Models").

### 2026-09-30 — Ground enemies (asked by the user in chat)
- Decision (the user's): more ground enemies, like turrets or tanks; some shoot "vertically", some at the player.
- Placeholder chosen (mine): "vertically" read as straight down the screen (not aimed). Three new enemies with the
  Turret (fixed, aimed): the Flak Cannon (fixed, pairs of shots straight down), the Tank (crawls sideways on the
  ground, its turret aims) and the Rocket Truck (drives down the road, big rockets straight down). Numbers in
  02-enemies.md. Ground enemies are marked `ground` in `enemies.py`; a test keeps every one of them away from levels
  over water, ice floes or clouds. Added to every level with solid ground (worlds 2, 4 and 5, not the swamps; the
  asteroids of 1-8 keep only their Turrets), introduced gradually (Flak Cannon from 2-1, Tank from 2-3, Rocket Truck
  from 2-5): each of these levels has at least one wave of every ground unit introduced so far, 2 to 3 new ground
  waves per level. The Tank's model has its dome and gun on the node the game turns to aim, like
  the Turret's barrel.
- Recorded in 02-enemies.md.

### 2026-09-30 — Faster loading: voxel meshes built with numpy (chosen by the user in chat)
- Decision (the user's, out of several options: a disk cache of built meshes, background loading, more pure-Python
  tuning, numpy): build the voxel meshes with numpy. `numpy` is now a dependency.
- How: `MeshBuilder.cells` (`models.py`) works on every cube at once: an occupancy grid finds the visible faces and
  their corner shading (`occlusion_level`), `merged_faces` merges them into rectangles in the same order as before,
  and the vertices are written into Panda3D in one copy (`build`). Shapes built a triangle at a time (boxes,
  spheres, water) are unchanged. Every mesh the game builds (ships, pickups, bosses and their parts, rocks, planet,
  nebula, the grounds of every biome) was checked to come out identical, triangle for triangle.
- Result (software rendering, this machine): level starts went from a median of about 480 ms to 145 ms (slowest
  820 to 285 ms), building all boss models from 3.8 to 0.8 s, game startup from about 460 to 320 ms.
- Recorded in 06-technical.md ("Extra libraries allowed").

### 2026-09-30 — Merged voxel faces (asked by the user in chat)
- Decision (the user's): adjacent cube faces of the same color make a single polygon.
- How: greedy meshing in `MeshBuilder.cells` (`models.py`): the visible faces of each flat layer are covered with
  as few rectangles as possible, each made of faces with the same color and corner shading (ambient occlusion); a
  rectangle only grows along a direction where the shading doesn't change, so it looks the same. Voxel faces' texture
  coordinates now count cubes (0 to 5 across a 5-cube rectangle) and the shader bevels each cube with their
  fractional part, so the cube grid still shows; glowing, water and burning faces moved to negative texture
  coordinates and stay one per cube. The voxel grounds use it too. Tests check the merged faces cover exactly the
  cubes' faces.
- Result: the 40 bosses went from about 613,000 to 122,000 triangles (5 times fewer; the small ships gain less,
  their faces are mostly near edges). With software rendering, boss fights are back to their speed before the
  finer cubes (the Warden's about 410 frames per second, a Metropolis one about 70 to 85).

### 2026-09-30 — Bosses screen (asked by the user in chat)
- Decision (the user's): a main menu entry showing all the bosses.
- Placeholder chosen (mine): "Bosses", after "Models": the boss pages moved from the Models screen to this new
  screen (new global state BOSSES, main menu <-> bosses), one world per page with Next page (wrapping around),
  Reload models and Back. The Models screen keeps the ships and pickups, on one page.
- Recorded in 04-ui-audio.md ("Game flow", "Main menu", "Bosses") and 01-gameplay.md ("Global state").

### 2026-09-30 — Industrial sci-fi ships (asked by the user in chat)
- Decision (the user's): ships look industrial sci-fi rather than cartoonish alien, like reference pictures the
  user gave (grey metal ships with panels, ribbed engine pods, dark glass and small orange lights).
- Placeholder chosen (mine): the player and the regular enemies were redrawn first, then the bosses: grey hulls
  in a few shades (lighter spine and top faces, darker sides), seams one or two voxels lower than the hull, darker
  nacelles with recessed vents, dark teal glass with a light glint, orange running lights. Each ship keeps its old
  color as paint markings so they stay easy to tell apart. The greys are kept a little dark to suit the muted
  backgrounds.
- Bosses (the user: "no more animals", all industrial giant space ships, renaming allowed): every boss is a ship
  now, drawn by a generator from a recipe (hull shape: block, wedge, prow, delta, long, round, cross, twin or ring;
  engines; raised deck; command tower with windows; reactor; wings; prow guns; vents; seams; paint color by world),
  and every part is a machine (turret, cannon, launcher, clamp, generator, ram, fuel tank, engine, armor plate,
  press, blade, dish, drill). Every boss now has engine flames at its nacelles (and engine parts at theirs).
  Their fights didn't change (same hitboxes, parts, health and guns). Renamed: Mine
  Mother -> Mine Carrier, Scarecrow -> Picket, Beetle -> Bulwark, Windmill -> Turbine, Silo Walker -> Silo Hauler,
  Hornet Queen -> Hive Carrier, Tractor King -> Tugmaster, Crab -> Clamp Barge, Jellyfish -> Pulsar, Manta -> Delta
  Raider, Iceberg Fort -> Cryo Fortress, Kraken -> Grappler, Leviathan -> Tidebreaker, Scorpion -> Breacher, Dust
  Devil -> Cyclone, Sandworm -> Borer, Mesa Fort -> Bastion, Lava Golem -> Foundry, Vulture -> Scavenger; their parts
  too (claws -> clamps, tentacles -> grapples, fins and wings -> batteries or hangars, and so on). The level files use
  the new names.
- Recorded in 05-visuals.md ("Art style"), 02-enemies.md ("Look", "Bosses") and 03-levels.md (worlds' tables).

### 2026-09-30 — Every model has the same cubes (asked by the user in chat)
- Decision (the user's): all models have cubes the size of the Swarmer's, so the other ships, enemies and bosses
  get more cubes.
- How: models are built in world units with cubes of `MODEL_VOXEL` (0.06 / 9, the Swarmer's: its 0.06 hitbox
  over its 9 columns, in `config.py`), no longer stretched to their hitbox; a model's size comes from its drawing.
  Every drawing was redrawn on the finer grid, keeping its size and look: each new cell takes the color covering
  most of it once the old drawing is smoothly stretched, so edges and diagonals come out smoother instead of in
  steps; thicknesses and engine positions were scaled the same way. Enemies that were stretched unevenly (Gunship,
  Mine Layer, Sniper...) keep the stretched shape, now drawn with square cubes. The Ice Cannon, Sentry Node and
  Sniper, which were smaller than their hitbox, were redrawn to fill it. Tests check every model is about its
  hitbox's size.
- Placeholder chosen (mine): boss models are built when first needed (the level's boss when it starts, the
  Models screen's bosses one page at a time), since building all 40 at the finer grid takes about 8 s (6 s once
  faces are merged, see "Merged voxel faces").
- Recorded in 05-visuals.md ("Art style") and 02-enemies.md ("Bosses").

### 2026-09-30 — Engine flames (asked by the user in chat)
- Decision (the user's): a jet flame behind the engines of the player and of the ships that move, like a
  reference picture (a pale blue flame behind a ship's engines); each model defines where its flames are and how
  big.
- How: a drawing file can have "engines", a list of {"x", "y", "width", "length", "towards", and maybe "color"}:
  the nozzle's column and row in the drawing (it can be between two voxels, like 5.5), the flame's width at the
  nozzle and its length in voxels, and whether it goes towards the drawing's "top" or "bottom" (enemies point down
  the screen, so their flames go to the top). `models.py` (`parse_engines`, `add_flame`) adds each flame to the
  model as a child node, so it follows the ship, its banking and its turns.
- Placeholder chosen (mine): two crossed glowing cards (added light), pale blue by default with a white core,
  widest and brightest at the nozzle, fading towards the tip; they waver in length (`flame_scale` in `app.py`,
  `FLAME_FLICKER`), and the player's are 35% longer flying up at full speed and shorter flying down
  (`FLAME_THRUST`). Flames on: the player, drone, weaver, diver, gunship, swarmer, sniper, mine layer, shield
  carrier, splitter, and the bosses with visible engines (Warden, Prowler, Rockbreaker, Twin Fang and its guns,
  Mine Mother, Gunship Prime and its engines). Not on turrets and mines (fixed to the ground), or pickups. Later
  (asked by the user): the player's missiles too, a jet behind each one that turns with it as it homes in.
- Recorded in 05-visuals.md ("Effects").

### 2026-09-30 — Voxel drawings in JSON files (asked by the user in chat)
- Decision: the voxel models' drawings moved from Python to JSON, one file per model in `src/pewpy/models/`
  (`player.json`, `drone.json`, …; the turret's barrel is `turret_barrel.json`). Each file has "rows" (the
  drawing, first row = top of the screen, "." or " " for no voxel) and "palette": for each character, "color"
  (red, green, blue from 0 to 1) and "height" (how many voxels thick, odd, centered on the model's depth).
  `models.py` reads them (`load_drawing`, checked by `parse_drawing`, errors name the file) and keeps the code:
  meshes, the turret's barrel placement, the pickup letter, the shapes that aren't drawings.
- Placeholder chosen (mine): the pickup capsule (`capsule.json`) is drawn in greys, multiplied by the pickup's
  color. The files are read every time the models are built, so "Reload models" picks up edits. They are left
  out of the pre-commit JSON formatter so each palette entry stays on one line.
- Recorded in 05-visuals.md ("Assets"), 02-enemies.md ("Looks") and 04-ui-audio.md ("Models").

### 2026-09-30 — See-through clouds over the grounds (asked by the user in chat)
- Decision: the atmosphere levels (worlds 2 to 5) get layers of soft see-through clouds, some levels very few,
  some many (level field `clouds`, 0 to 1).
- Placeholder chosen (mine): two layers between the ground and the ships (depths 0.08 and 0.18, up to 10 clouds
  each), drifting down at 50% and 42% of the scroll speed on screen and slightly sideways (wind); pale grey-blue
  mixed with the air's color, dimming less than the ground at night; opacity 0.14 to 0.34 each. The amounts per
  level are in 03-levels.md (from 0.05 to 0.9). Cost: about 12% of the frame rate at the most clouds (software
  rendering). `MIST_*` constants in `background.py` and `background_view.py`.
- Recorded in 03-levels.md.

### 2026-09-30 — HUD along the bottom edge (asked by the user in chat)
- Decision: the whole HUD sits on the bottom edge so it doesn't block the view: score bottom-left, the weapon levels
  over a thin health bar in the middle, lives bottom-right. Each part hangs on Panda3D's edge anchors, so it
  stays at the real edges in any window (before, it assumed the offscreen layout and sat 25% inward in a real
  window). Margins and sizes are constants at the top of `app.py` (`HUD_MARGIN`, `HUD_TEXT`, ...).
- Recorded in 04-ui-audio.md ("HUD").

### 2026-09-30 — Round, soft bullets and effects (asked by the user in chat)
- Decision: bullets and glowing particles (sparks, fireballs, laser sparks) are circles instead of squares, solid in
  the middle and fading out towards the edge. The explosion debris stay small lit voxel cubes, and missiles keep
  their voxel model.
- Placeholder chosen (mine): each circle always faces the camera. Bullets are drawn over the scene (readable on
  bright grounds too), about 1.8 times their hitbox, ovals for the player's long bullets; glowing particles add
  light, so overlapping ones blend into a glow. All drawn in one call per kind (`sprites.py`).
- Recorded in 05-visuals.md and 02-enemies.md.

### 2026-09-30 — Models screen (asked by the user in chat)
- Decision: a "Models" entry in the main menu opens a screen showing every model (ships, enemies, missile,
  pickups) in a circle, each spinning, the circle turning, to make working on the models easier. It can reload
  `models.py` without restarting the game. New global state MODELS (main menu <-> models).
- Placeholder chosen (mine): the circle faces the camera (on the tilted play plane it looked squashed), plain dark
  background, names under the models, "Reload models" and "Back" in the middle. `src/pewpy/showcase.py`.
- Recorded in 04-ui-audio.md ("Game flow", "Models") and 01-gameplay.md ("Global state").

### 2026-09-30 — Enemies enter from off screen (asked by the user in chat)
- Decision: enemies appear just beyond the screen's real edges (the tilted camera shows more than the play area:
  up to about 1.65 at the top, 1.13 on the sides) and fly in, instead of popping up inside the screen; they
  are removed once fully off screen again (02-enemies.md: "disappear once they are fully off screen").
  Swarmers fly straight in until the play area's edge, then curve as before.
- Consequence: every enemy reaches the play area a little later than its wave's time (about 2 s for a Drone,
  4 s for a Gunship); the levels' timelines weren't changed.

### 2026-09-30 — Worlds of 8 levels (answered by the user in chat)
- Decision: levels are grouped in 5 themed worlds of 8 levels each (40 levels), each world mixing related grounds
  with variations: 1 Orbit (space, asteroids), 2 Heartland (hills, farmland, forest, swamp), 3 Waters (islands,
  pack ice, clouds), 4 Badlands (desert, canyon, volcano, mountains), 5 Metropolis (city, refinery). Menus:
  Start -> world select -> the world's level select; everything open from the start. "Next level" goes on
  into the next world after a world's last level ("WORLD COMPLETE").
- Placeholder chosen (mine): the level names and order (see the level select, or `src/pewpy/levels/`);
  variations are the ground, its layout (`background_seed`: the same every time) and the time of day
  (`time_of_day`: day, dusk or night, which tints the ground, its haze and the sky; lights keep their colors);
  space levels also get their own nebula and planet colors and planet size. Waves: the three levels of
  03-levels.md keep theirs; the other 37 were generated, difficulty rising over the whole game, each world
  favoring its own enemies. Not playtested.
- Spec impact: 03-levels.md's Level 1, 2, 3 are now 1-1 Outer Belt, 2-1 Ground Defense and 1-8 Minefield
  (their waves are unchanged). So "First appears in level" in 02-enemies.md now reads: level 1 = 1-1, level 3's
  enemies (mine layer, shield carrier, splitter) = 1-8, level 2's (turret, swarmer, sniper) = swarmers and
  snipers from 1-2, turrets from 1-8 (Minefield has two). 03-levels.md "Level data format" is now
  `src/pewpy/levels/world_<number>/level_<number>.json`, plus `world.json` (the world's name). Done on
  2026-09-30, when the user asked to update the specs to match the code: 01-gameplay.md (states, controls,
  weapons, difficulty, win), 02-enemies.md (general rules, looks, first appearances) and 03-levels.md (worlds,
  backgrounds, levels) now describe the game as it is. Then, at the user's request, 03-levels.md keeps only the
  levels' backgrounds: the waves (including the three hand-made timelines) are only in the level files.
- New global state WORLD_SELECT between the main menu and the level select (01-gameplay.md lists the states).

### 2026-09-30 — Grounds stay voxels (answered by the user in chat)
- Decision: the ground backgrounds stay made of cubes. A smooth version (blurred heights drawn as a continuous
  surface, with houses and trees as voxel props) was tried on 2026-09-29 and reverted: the user found it ugly.

### 2026-09-29 — 3D rendering with cubes (asked by the user in chat)
- Decision: the game is drawn in 3D. The player and every enemy type have a low-poly model built in Python
  from simple shapes (`src/pewpy/models.py`, no 3D files), stretched to the entity's size (depth = smaller
  of width and height). Bullets are lit cubes. Stars stay flat, unlit points just behind the play plane.
- Extras: Turret barrels aim at the player, Swarmers and diving Divers point where they fly, mines spin,
  the Shield Carrier shows a see-through bubble while shielded, the player's ship rolls when moving sideways.
- Done: recorded in 00-vision.md ("Rendering") and 05-visuals.md ("Overall style", "Source of models").

### 2026-09-29 — Voxel ships (asked by the user in chat)
- Decision: ships, missiles and pickups are voxel models, like old-school pixel art or Minecraft. Each is drawn
  in `models.py` as rows of characters (first row = top of the screen); a palette gives every character a color
  and a thickness in voxels (odd, centered on the depth), so cockpits, eyes and domes stick out and wings are
  one voxel thin. Faces hidden between touching voxels are dropped. The shield bubble and the laser beam stay
  smooth see-through effects; bullets stay single cubes.
- Done: recorded in 05-visuals.md ("Overall style").

### 2026-09-29 — Lighting and reflections on the voxels (asked by the user in chat)
- Decision: a GLSL shader (`lighting.py`) lights the models per pixel, with specular highlights and reflections
  of a made-up space environment (dark blue sky, a wide soft light panel, a warm glow), stronger at grazing
  angles. Each voxel face gets a fake bevel: its rim bends the light like a rounded block; it fades out when a
  voxel is only a few pixels wide, so in game it's subtle and it shows on close-ups. Voxel face corners
  touching other voxels are darkened (ambient occlusion, `models.py`). Stars, bullets, the laser, the shield
  bubble and pickup letters stay unlit. Strengths are in `config.py` (`SHININESS`, `SPECULAR`, `REFLECTIVITY`,
  `BEVEL_WIDTH`, `BEVEL_STRENGTH`); `OCCLUSION_BRIGHTNESS` is in `models.py`.
- Not done: mirror reflections of the other ships (costly, and too small to see on ships this size); bloom/glow
  (Panda3D's bloom filter showed no effect in offscreen tests, and full-screen passes cost more on software
  rendering).
- Performance: no measurable cost (software rendering at 600x800 stays near 700–1000 fps with or without it).
- Done: recorded in 05-visuals.md ("Overall style", "Post-processing").

### 2026-09-29 — Per-level backgrounds (answered by the user in chat)
- Decision: each level has its own background matching its setting in 03-levels.md (open space, planet
  surface, debris field), kept dark and muted so bullets and enemies always stand out.
- To do: record in 05-visuals.md ("Background"); the details are an open question above.

### 2026-09-29 — Resizing the window (asked by the user in chat)
- Decision: the window can be resized freely; the game area (3D view and HUD) keeps its 3:4 shape, as big as
  fits, centered, with black bars on the sides or at the top and bottom (`letterbox()` in `app.py`). The window
  itself isn't forced to 3:4 (that fights the window manager and breaks maximizing).
- Recorded in 06-technical.md ("Window").

### 2026-09-29 — Menus picked with the arrow keys (asked by the user in chat)
- Decision: every menu screen is a list: Up/Down move the highlight (wrapping around), Enter chooses, Escape
  goes back; Escape still pauses while playing. The different keys per screen (Enter, Q, number keys) are gone.
  Main menu: Start, Quit. Level select: every level, then Back; opens on the last level played. Pause:
  Resume, Main menu. Game over: Continue, Main menu. Level complete: Next level, Main menu (just Main menu
  after the last level). Logic in `menu.py`, drawing in `menu_view.py`, the menus of each state in `app.py`.
- Recorded in 04-ui-audio.md ("Screens").

### 2026-09-29 — Particle effects on impacts and explosions (asked by the user in chat)
- Decision: shots hitting something throw sparks, and destroyed things explode (05-visuals.md "Explosions",
  "Particles").
- Placeholder chosen (the look is mine): every particle is a tiny cube, to match the voxel style. Impacts: 4-6
  quick glowing sparks thrown back the way the shot came; the laser throws a steady trickle of cyan sparks
  where it burns an enemy. Explosions (enemies destroyed or rammed, the player losing a life): a fireball of 6
  glowing cubes (pale yellow in the middle, orange to red around), sparks, and lit debris cubes tumbling out in
  the 3 main colors of the model that blew up (read from its mesh) plus some grey metal; the count grows with
  the size. Missiles: an orange fireball as wide as the splash and a ring of 12 sparks. Particles slow down and
  shrink away in 0.1 to 1 s, keep moving on the game over and level complete screens, freeze in pause. At most
  512 at once (the oldest go first).
- How: the World reports what happened (`World.events`), `effects.py` moves the particles (no Panda3D),
  `effects_view.py` draws them all in one call: one cube mesh repeated per particle (instancing), their
  positions, colors and rotations packed each frame into a small float texture read by the shader.
- Performance (software rendering): ~200 fps in level 1 with bullets at level 3, up to ~140 particles at once.
- Options: screen shake on big explosions; engine trails; a white flash on the whole screen when the player dies.

### 2026-09-29 — Lives vs health bar (answered by the user in chat)
- Decision: each life has its own health bar. When health reaches zero the player loses a life and the
  level restarts. Interpretation of the rest of 01-gameplay.md: when lives reach zero the player is asked
  to continue; answering no shows game over, then the main menu.
- To do: move this into 01-gameplay.md.

### 2026-09-29 — Type stubs for Panda3D
- Decision: added `types-panda3d` as a dev dependency.
- Reason: Panda3D is a compiled module; without stubs `ty` (in `make check`) cannot type-check it.
- Recorded in 06-technical.md ("Extra libraries allowed").

### 2026-09-29 — Game logic separated from Panda3D
- Decision: `player.py` has no Panda3D import; `app.py` only handles window, input and drawing.
- Reason: logic is unit tested without opening a window (06-technical.md testing suggestion).
- Recorded in 06-technical.md ("What must be unit tested").

<!-- Format:
### YYYY-MM-DD — Short title
- Decision:
- Reason:
-->
