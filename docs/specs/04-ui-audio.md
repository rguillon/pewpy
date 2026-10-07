# 04 — UI, Game Flow and Audio

## Game flow

> Describe the screens and how the player moves between them.

```text
Main menu -> Ship select -> World select -> Level select (the world's 6 levels) -> Playing <-> Pause
Dev -> AI playing: Ship select (Back: to Dev) -> World select -> Level select -> the AI playing <-> back to the Level select
Main menu <-> Dev <-> Model browser (Players, Enemies or Bosses)
Main menu <-> Dev <-> Backgrounds browser
Playing -> Level complete ("World complete" after a world's last level) -> next level (Playing, into the next
world after a world's last level), or after the very last level: "YOU WIN" -> Main menu
Playing -> Game over -> Continue (restart the level) or Main menu
Pause -> Main menu
```

*(placeholder: menus, keys and HUD layout; level end and the LEVEL_COMPLETE state; worlds)*

## Screens

### Title / main menu

- Every menu: Up/Down move the highlight (wrapping around), Enter chooses, Escape goes back.
- Look *(the user's choice: old school sci-fi, like the game)*: behind every menu without a level behind it (the
  main menu, the ship, world and level selects, the Dev menu, the music browser, the screenshots before one is
  taken), the ground of a level drawn at random, scrolling by at its speed, as in the game (another one each time
  the menus come back from a level). The model browser keeps a plain dark background. The menus look like the HUD's
  instrument panels: a gunmetal plate with bevelled edges and a screw in each corner, the title stencilled on it,
  over a recessed dark display with faint scanlines where the items glow amber (the HUD's readouts' color, dimmer),
  the highlighted one bright, between markers, on a lit row; the same under pause, game over and level complete,
  over the level. The ship select's names, bars and details are on a console of their own along the bottom (amber
  bars), the level preview has a steel frame *(colors and layout are placeholders)*.
- Entries: Start (to the ship select: one entry per ship, then Back; under the menu, every ship side by side (closer
  together when they wouldn't fit across the screen) with
  its name and bars comparing armor, speed, size and repair; the highlighted one is bigger, spins, has bright bars,
  and its description and numbers show at the bottom; then the world select: one entry per world, then Back to the ship select; then that
  world's level select: its 6
  levels, like "2-5 Twilight Grove", then Back, with a window above the list showing the highlighted level's
  ground scrolling by, as in the game; both open on the last level played), Dev (see "Dev menu" below), Quit
  *(entries are a placeholder)*

### Dev menu

- In the game itself (`make run`) *(the user's choice)*: Players, Enemies, Bosses, Music, Backgrounds, AI playing, Screenshots, Back. Each of the first three opens the model browser
  on that category's models: the player's ships (`ships.json`), the enemies drawn from a model file (catalog, fleet,
  projectiles: not the turret and the tank, built in code; a model shared by two kinds once), and the bosses (as they're
  played: the mini boss of level 1-1, its final boss, the mini boss of 1-2...; a boss in no level last). Escape goes back to the Dev menu, on the category browsed.
- The model browser shows one model at a time, a boss with its parts in place (its destroyable parts blinking
  slowly, lit up for half of every 1.2 s), swaying a little to show its depth,
  on a plain dark background, inside a frame: the model's size (its `"size"`, see `05-visuals.md`), the size new
  models are made to. The model and the frame are drawn to the scale fitting the bigger of them, so they compare.
  Above: the model's name, its number in the category ("Drone  (1/51)") and a short description from the game's
  data, so a new shape can be picked to match what it does (an enemy's or a boss's note, a boss's parts, a ship's
  description); below: the size (world units and cubes), the model's own size in cubes, what's going on, and the keys.
- Keys: Left/Right go to the previous or next model (wrapping around; a new model not saved is dropped); Up/Down
  make the size 5% bigger or smaller, keeping its proportions *(placeholder)*; Space makes a new random model of
  that size (shown, not saved; again for another one); Enter saves it in place of the model's JSON file, or, without
  a new model, saves the size alone *(placeholder)*. Saving updates the game at once (its enemies and models are
  read again).
- New models are made by `src/pewpy/makers/`: a ship of any kind (the enemies'
  six, or the player's three classes) or a whole boss, its core and its destroyable parts all new, made several
  times scaled towards the size and the nearest one kept. A boss's number of parts comes from its size: one part for
  every 600 square cubes of its core, in pairs, 2 to 12 *(placeholder)*; mirrored pairs (one in the middle for an
  odd number), a lopsided boss staying lopsided. Saving a boss writes its model file: its core's drawing and, under `"parts"`, its parts'
  drawings, named after their kind (`<boss>:drill`, then `<boss>:drill2` for a second group of drills...), and its
  description (`data/bosses/`): its size and its parts ("drill 1",
  "turret 2"...), their places and sizes. A final boss's plan (`data/bosses/final_plans.json`) gets them, and the
  boss is made again from it. A mini boss keeps its hand-written phases, the parts they name replaced by the new
  ones *(the user's choice)*: the phases waiting for parts to be destroyed each get a lot of the new parts, the
  front ones (nearest the bottom of the screen) to the first, a group sharing a drawing kept together when there
  are enough groups; a gun fired from old parts is fired from the parts that took their place (from all of them for
  old parts no phase waited for); new parts are as strong and worth as much as the old ones of their phase (a mini
  boss that had none: 25 health, 400 points *(placeholder)*). A ship's hitbox follows its model *(the user's
  choice)*: saving a ship (a new model, or a new size alone) scales its hitbox as much as its size changed (an
  enemy's `"size"`, a player's ship's in `ships.json`); an enemy sized by its cubes (`"voxels"`, the fleet) gets the
  new model's.
- How the makers make each:
  - An enemy: a real 3D voxel model assembled from a kit of hardcoded parts (`makers/ships/`): a hull (a profile
    stretched along the ship), wings (an outline), a tailplane or canards, a cockpit (bubble, canopy, visor, bridge or
    sensor eye), engines (tail nozzles or nacelles), weapons (nose barrels, wing and tip guns, missiles, a turret, a
    gatling, a side cannon), fins, antennas, a radar dome, intakes, armor, a livery stripe and markings. Six kinds, each
    a recipe choosing and placing the parts: fighter, interceptor, bomber, drone, gunship, heavy. Each lists its weapons
    (numbered, at their barrels' tips), at least one.
  - A player's ship: from the enemies' kit of parts. The class, in the spirit of the game's three ships, sets the size:
    vanguard (balanced), juggernaut (heavy), phantom (light); the rest is picked on its own, for variety: the hull, the
    wings' layout (one pair, crossed X wings, stacked pairs, a small pair forward, a flying wing, two booms) and
    outline, the engines (tail, booms, pods on the wings or the hull), the cockpit, the weapons and the extras. Their
    main color is always a bluish grey, like the game's ships, with colored bits (a livery stripe, a nose cone, wing
    stripes, markings, sensors) *(the user's choice)*. Like the game's ships, they point up the screen, flames out of
    their tail at the bottom without weapons listed (the player's guns don't fire from the model).
  - A boss: a real 3D voxel model (`makers/bosses/`) sculpted from a plan: stepped decks and a superstructure on the
    hull, the bridge on top, recessed panel lines and hangar bays, 0 to 2 big appendages; then no flat zone left plain:
    plating panels raised or sunk, and mostly built-in parts (see `05-visuals.md`) on the hull and decks: reactors,
    radars, antennas, sensor domes, vents, radiators, exhaust stacks, fuel tanks, guns (armed: their barrels are the
    core's weapons too), engines near the back (flames going back); with blocks, pipes, lights and lit trenches, ribs
    and weapon pods on the wings. The destroyable parts are built-in parts too, smaller than the old flat shapes *(the
    user's choice)*: turrets, twin cannons, gatlings, missile racks, flak guns, beam emitters, reactors, radars (one to
    three kinds a boss), each standing on the hull where it's mounted, on a socket following its outline. Each drawing
    lists its weapons: the built-in parts' barrels (a missile rack: its middle warhead; a gatling: its spindle), and
    guns on the core's front edge, enough for at least five on the boss.
- Music opens the music browser *(the user's choice)*: the game's 12 songs, one at a time, in their plans' order
  (title, world_1 … world_8, boss, level_complete, game_over), over the menus' ground, its texts on a console like the menus'. The song on show
  plays (once it's rendered: "Rendering..." until then; a jingle once). Above: its name and number ("world_1
  (2/12)"), its title, key, tempo, length, whether it loops, and its chords (read from its MIDI file, whose title
  holds the key and chords: "Neon Horizon | A minor | i VImaj7 III VII"); below: what's going on, and the keys.
  Keys: Left/Right go to the previous or next song (wrapping around; a new song not saved is dropped); Space
  composes a new one from the song's plan, varied by a seed drawn at random *(placeholder)*: another key, a tempo
  within 10% of the plan's, another chord progression (the songs' own and a few more), drums, bass and arpeggio
  styles, brass or not, and new tunes; a jingle keeps its chords (a win or a loss), only its key, tempo and tune
  change. It plays, not saved (again for another one); Enter saves it in place of the song's MIDI file (`data/music/<name>.mid`), and the game
  plays it from then on; M turns the music on and off; Escape goes back to the Dev menu, on Music.
- Backgrounds: candidates for new level backgrounds, one at a time on the whole screen, scrolling as in the game,
  over a panel at the top: its name, theme, seed, preset, time of day and clouds, and the keys. One theme after the
  other: each shows one of the kinds of ground made for them, with generators and painters of their own (`salt_pan`,
  `savanna`, `badlands`, see `03-levels.md`; three candidates became worlds 3, 5 and 6): earth-like only, after real
  places, no space and nothing alien-looking *(the user's choice)*. A theme gives one its palette, sometimes other
  water, its numbers, its time of day and clouds: salt, turquoise, copper and clay pans, a salt shore; Serengeti,
  green-season, Kalahari or outback savannas; painted, grey, cream or rainbow badlands. Kept dark and muted like the
  game's backgrounds, so bullets stand out *(placeholder: the themes)*. A candidate is what a level says of its
  background (`background`, `scenery`, `time_of_day`, `clouds`, `background_seed`, see `03-levels.md`), with a name
  from its theme's words; it's made again from its theme and seed by `src/pewpy/makers/backgrounds/`, so they are all
  a world's plan needs to take it *(placeholder: nothing is saved)*. Keys: Left/Right go to the previous or next
  theme (wrapping around); Space makes a new candidate of the theme (another seed); Escape goes back to the Dev menu,
  on Backgrounds.
- AI playing *(the user's choice)*: the ship, world and level menus, titled "AI PLAYING", pick the ship and the
  level the AI plays (see `07-ai.md`); Back from the ship select goes back to the Dev menu, on AI playing.
- Screenshots *(the user's choice)*: the README's picture of each world (`docs/screenshots/world_<number>.png`),
  one per world. Left/Right go to the previous or next world (from the world of the last level played; wrapping
  around), over the menus' ground; Space plays one of its levels, drawn at random, to a moment drawn at random and
  shows it frozen, with the HUD: a regular ship, a weapon selected, every weapon at the same level (2 to 5), a
  secondary weapon 40% of the time, 8 to 45 s into the level, or a quarter of the time 2 to 6 s into its first boss
  fight (the ship weaving around the screen with the fire button held, unable to die) *(placeholders)*; Space again
  for another one. Enter saves the game area as the world's screenshot, without the texts over it (a panel at the
  top: the world, the level and the shot, what's going on, the keys). Escape goes back to the Dev menu, on
  Screenshots.

### Options

- Settings: TBD (volume, fullscreen, resolution, key bindings, difficulty…)
- Saved where / how: TBD

### Pause

- Entries: Resume, Main menu; Escape resumes *(placeholder)*

### Game over / high scores

- Game over: Continue (restart the level), Main menu; Escape goes to the main menu *(placeholder)*
- High scores: TBD

## HUD (in-game display)

> What is shown, and where on screen.

| Element | Position | Notes |
|---------|----------|-------|
| Score | Bottom-left panel *(placeholder)* | "SCORE" over an amber 7-digit readout |
| Lives | Bottom-right panel *(placeholder)* | "LIVES" over an amber digit and a green lamp per life, up to the most the ship can have |
| Health | Bottom-center panel, under the weapons *(placeholder)* | "HULL": a gauge of 20 segments, green, amber under half, red under a quarter; one gauge per life |
| Bombs | TBD | TBD |
| Weapon level | Bottom-center panel *(placeholder)* | A tile per weapon (B, L, M) with its letter and 5 pips for its level; the selected one lit in its color. A fourth tile, "AUX", shows the secondary weapon's letter (T or Z) lit in its color while the ship carries one *(placeholder)* |
| Frames per second | Top-right corner, small and dim, on every screen (menus too) *(the user's choice)* | Averaged over a second, refreshed twice a second; `SHOW_FPS` in `config.py` turns it off |
| Boss health bar | Top center, at the edge: a wide orange bar in a recessed display, the boss's name under it *(placeholder)* | Only while the boss is on screen; counts the core and its parts together |

- Look: the bottom of the HUD is three cockpit instrument panels *(the user's choice)*: gunmetal plates with a
  bevelled rim and a screw in each corner, their readouts in recessed dark displays (`ui/panel.py`).
- Font: Orbitron, a geometric sci-fi font (SIL Open Font License, in `data/fonts/` with its license), for every
  text: menus, HUD, ship select, pickup letters (`FONT` in `app/window.py`) *(the user's choice: something sci-fi)*

## Audio

- Music style: synthwave *(the user's choice)*
- Music source (your files, free assets, generated): generated MIDI songs *(the user's choice)*, composed by
  `pewpy/makers/songs/` and saved to `data/music/` by the Dev menu's music browser, one at a time; the game plays them with its own synthesizer. Any MIDI
  file can replace one. Songs *(placeholder)*: "title" on the menus, "world_1" to "world_8" for
  each world's levels (the AI playing them too), "boss" while a boss is fought (from the final boss's coming, until the level ends), and two jingles played once,
  "level_complete" and "game_over". Lower while paused; M turns the music on and off. Volumes: `SFX_VOLUME`, `MUSIC_VOLUME` in `config.py`
  *(placeholders, until the options menu)*. Each song is rendered once, in the background, and kept as a WAV
  in the user's cache folder (`~/.cache/pewpy/music`, `%LOCALAPPDATA%\pewpy\music` on Windows).
- Sound effects needed *(placeholders: synthesized)*:

| Event | Description |
|-------|-------------|
| Player shot | Bullets and the turret: a quick falling "pew"; missiles: a rising whoosh; the laser: a hum while it fires; the lightning gun: a short crackling buzz |
| Enemy hit | A short metallic tick |
| Explosion | Three sizes, by the size of what blew up (a boss's is long); a missile's blast |
| Pickup | An upgrade: a quick major arpeggio up; a repair: a bright glide up; an extra life: a bright fanfare climbing two octaves |
| Player death | A big blast and a falling wail; hit without dying: a harsh falling buzz; a hit taking the secondary weapon: a short crunch and a falling blip |
| Menu select | A blip moving, two rising blips choosing, two falling going back; switching weapons: two blips |
| Boss coming | A two-tone siren |
