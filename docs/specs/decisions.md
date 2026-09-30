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
  Harvester, Leviathan, Colossus, Overmind. Every boss has at least two phases; some have no parts and change phase
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
  Mine Mother, Gunship Prime and its engines). Not on turrets and mines (fixed to the ground), pickups, or the
  missile.
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
