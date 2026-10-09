# 04 — UI, Game Flow and Audio

Units: see `00-vision.md`. The screens and the moves between them are listed in `01-gameplay.md` (GAM-1).

## Game flow

```text
Main menu -> Ship select -> World select -> Level select (the world's 6 levels) -> Playing <-> Paused
Playing -> Level complete ("World complete" after a world's last level) -> next level, or after the last level:
           "YOU WIN" -> Main menu
Playing -> Game over -> Continue (restart the level) or Main menu
Paused -> Main menu
Main menu <-> Dev menu <-> Model browser (Players, Enemies or Bosses), Music browser, Background browser, Screenshots
Dev menu -> AI playing: Ship select (Back: to the Dev menu) -> World select -> Level select -> the AI playing
            -> (Escape) back to the Level select
```

## Menus

- **UIA-1** Every menu shall be a title and a list of items: Up/Down move the highlight (wrapping around), Enter
  chooses the highlighted item, Escape goes back. The highlighted item shall be shown between markers ("> Start <").
- **UIA-2** Menu look *(placeholder: colors and layout)*: a gunmetal plate with bevelled edges and a screw in each
  corner, the title stencilled on it, over a recessed dark display with faint scanlines where the items glow amber
  (dimmer than the HUD's readouts), the highlighted one bright on a lit row.
- **UIA-3** Behind every menu without a level behind it (main menu, ship, world and level selects, Dev menu, music
  browser, screenshots before one is taken) the ground of a level drawn at random shall scroll by at that level's
  speed, as in the game; another level shall be drawn each time the menus come back from a level. Pause, Game over and
  Level complete shall show their menu over the level, frozen.
- **UIA-4** Every text shall use one geometric sci-fi font (Orbitron, SIL Open Font License, shipped with its
  license).

### Main menu

- **UIA-5** The main menu, titled "PEWPEW", shall have: Start (to the ship select), Dev (to the Dev menu), Quit (closes
  the game).

### Ship select

- **UIA-6** The ship select, titled "SELECT SHIP", shall have one item per ship (Vanguard, Juggernaut, Phantom,
  Tester), then Back (to the main menu, or to the Dev menu when picking for the AI). It shall open on the ship played
  last.
- **UIA-7** Under the menu, every ship shall be shown side by side (closer together when they would not fit across the
  screen), spinning, each with its name and four bars comparing it with the others: Armor (health), Speed, Size and
  Repair, each bar showing the ship's value as a share of the best of the regular ships (the Tester's bars are full
  where it is at least as good). The highlighted ship shall be bigger, its bars bright, and its description and
  numbers shall show at the bottom. These shall be on an amber-lit console of their own along the bottom.

### World and level select

- **UIA-8** The world select, titled "SELECT WORLD", shall have one item per world ("1. Highlands") then Back (to
  the ship select). It shall open on the world of the last level played.
- **UIA-9** The level select, titled with the world's name in capitals, shall have the world's 6 levels ("2-5
  Twilight Grove") then Back (to the world select). It shall open on the last level played if it is in this world,
  else on the first one, so that playing again is just Enter.
- **UIA-10** Next to the level list, on its right, a window in a steel frame shall show the highlighted level's
  ground scrolling by, as in the game; nothing when Back is highlighted.

### Pause, game over, level complete

- **UIA-11** Escape during play shall pause the game: the "PAUSED" menu has Resume and Main menu; Escape resumes.
- **UIA-12** The "GAME OVER" menu shall have Continue (GAM-46) and Main menu; Escape goes to the main menu.
- **UIA-13** The level complete menu shall be titled "LEVEL COMPLETE" with Next level and Main menu; after a world's
  last level, "WORLD COMPLETE" and the world's name, with Next world and Main menu; after the last level, "ALL
  LEVELS COMPLETE / YOU WIN!" with Main menu only. Escape goes to the main menu.
- **UIA-14** There shall be no options menu and no high score screen: volumes, window size and keys are fixed
  (UIA-42, TEC-3, GAM-3).

## HUD

- **UIA-15** During play the bottom of the screen shall show three cockpit instrument panels: gunmetal plates with a
  bevelled rim and a screw in each corner, their readouts in recessed dark displays *(placeholder layout)*:

| Panel | Shows |
|-------|-------|
| Bottom left | "SCORE" over an amber 7-digit readout (leading zeros) |
| Bottom centre | A tile per weapon (B, L, M): its letter and 5 pips for its level, the selected one lit in its color, the others dim. A fourth tile, "AUX", shows the secondary weapon's letter (T or Z) lit in its color while the ship carries one. Under the tiles, "HULL": a gauge of 20 segments showing the health left (green above half, amber above a quarter, red below) |
| Bottom right | "LIVES" over an amber digit, and a lamp per life up to 9 (green when lit) |

- **UIA-16** While a boss is on screen (not while it is still above it), its health bar shall show at the top centre of
  the screen: a wide orange bar in a recessed display, shrinking with the health left of the core and its parts
  together, the boss's name under it.
- **UIA-17** The frames per second shall show in the top-right corner, small and dim, on every screen (menus too),
  averaged over a second and refreshed twice a second; it can be turned off by a setting.
- **UIA-18** The HUD shall be hidden on screens without a level in play.

## Dev menu

- **UIA-19** The Dev menu, titled "DEV", shall have: Players, Enemies, Bosses, Parts, Music, Backgrounds, AI
  playing, Screenshots, Back. Coming back to it shall highlight the entry last used.

### Model browser

- **UIA-20** Players, Enemies and Bosses shall open the model browser on that category's models: the player's ships;
  the enemies and projectiles with a model of their own (a model shared by two kinds once); the bosses in the order
  they are played (the mini boss of 1-1, its final boss, the mini boss of 1-2...), a boss in no level last.
- **UIA-21** The browser shall show one model at a time on a plain dark background, a boss with its parts in place (the
  parts lit up for the first half of every 1.2 s), swaying 25° each way to show its depth, inside a frame showing the
  model's intended size, the size new models are made to. The model and the frame shall be drawn to the scale fitting
  the bigger of the two, so they compare.
- **UIA-22** Above the model: its name, its number in the category ("Drone  (1/51)") and a short description from the
  game's data (what it does, a boss's parts, a ship's description). Below: the intended size (in world units and in
  cubes), the model's own size in cubes, what is going on, and the keys.
- **UIA-23** Keys: Left/Right go to the previous or next model (wrapping around; a new model not saved is dropped);
  Z/S make the intended size 5% taller or shorter and D/Q 5% wider or narrower, each on its own, so the model's shape
  can change (keys placed for an AZERTY keyboard) *(placeholder)*; Up/Down do nothing; Space makes a new random model of
  that size (shown, not saved; again for another one; a message if none can be made that size); Enter saves it in
  place of the model, or, without a new model, saves the size alone *(placeholder)*; Escape goes back to the Dev menu.
  Saving shall update the game at once. The keys shall be listed at the bottom of the screen.
- **UIA-24** Saving a ship (a new model or a new size) shall scale its hitbox as much as its size changed (an
  enemy's width and height each by its own change; a player's square hitbox by the change of the size's area).
- **UIA-25** Saving a boss shall save its new parts: their places and sizes, named after their kind ("drill 1",
  "turret 2"...). A final boss is then made again from its plan (BOS-20 to BOS-25). A mini boss keeps its phases, the
  parts they name replaced by the new ones: the phases waiting for parts to be destroyed each get a share of the new
  parts, the front ones (nearest the bottom of the screen) to the first, a group sharing a model kept together when
  there are enough groups; a gun fired from old parts is fired from the parts that took their place (from all of them
  for old parts no phase waited for); new parts are as strong and worth as much as the old ones of their phase (a mini
  boss that had none: 25 health, 400 points *(placeholder)*).
- **UIA-26** New models shall be made as described in `05-visuals.md` ("Model makers").

### Parts browser

- **UIA-46** Parts shall open the Parts menu, titled "PARTS": one entry for each kind of built-in part ships are made
  of (VSL-33), in the catalog's order (Hulls, Wings, Cockpits, Engines, Guns, Missiles, Vents, Intakes, Fins,
  Antennas, Sensors, Tanks, Armor, Lights, Machinery), then Back. Coming back to it shall highlight the kind last
  browsed. A kind shall open the parts browser on its parts, one part at a time, in the model browser's view (swaying,
  a frame its size, on a plain dark background), its front up the screen, an engine's flame showing; a part smaller
  than 12 cubes drawn to the scale fitting 12, so it looks small *(placeholder)*. Above it: its name, its number among
  its kind ("Bubble, wide  (4/22)"), its kind, what it is and how it mounts on a ship. Below: its size in cubes
  (across, along, up), how many weapons and nozzles it has, and the keys.
- **UIA-47** Keys: Left/Right go to the previous or next part of the kind, wrapping around; Up, Down, Space and Enter do
  nothing (parts are drawn in code, nothing to make or save); Escape goes back to the Parts menu.

### Music browser

- **UIA-27** Music shall open the music browser: the game's 12 songs, one at a time, in this order: title, world_1 …
  world_8, boss, level_complete, game_over; over the menus' ground, its texts on a console like the menus'.
- **UIA-28** The song on show shall play ("Rendering..." until it can; a jingle once; "Music off: M turns it on" while
  the music is off). Above: its name and number ("world_1  (2/12)"), its title, key, tempo, length, whether it loops,
  and its chords. Below: what is going on, and the keys.
- **UIA-29** Keys: Left/Right go to the previous or next song (wrapping around; a new song not saved is dropped);
  Space composes a new one from the song's plan (see "Music") and plays it, not saved (again for another one); Enter
  saves it in place of the song, and the game plays it from then on; M turns the music on and off; Escape goes back to
  the Dev menu.

### Background browser

- **UIA-30** Backgrounds shall show candidates for new level backgrounds, one at a time on the whole screen, scrolling
  as in the game (at 0.2), under a panel at the top: its name, theme, seed, ground, time of day and clouds, and the
  keys.
- **UIA-31** Candidates shall come from themes, one theme after the other, each on one of the newer grounds (salt pan,
  savanna, badlands): earth-like only, after real places, nothing alien-looking. A theme gives a candidate its palette,
  sometimes other water, its numbers, its time of day and clouds: salt, turquoise, copper and clay pans, a salt shore;
  Serengeti, green-season, Kalahari or outback savannas; painted, grey, cream or rainbow badlands; kept dark and muted
  like the game's backgrounds *(placeholder: the themes)*. A candidate's name comes from its theme's words; it shall be
  made again from its theme and seed, so the seed is all a world needs to take it *(placeholder: nothing is saved)*.
- **UIA-32** Keys: Left/Right go to the previous or next theme (wrapping around); Space makes a new candidate of the
  theme (another seed); Escape goes back to the Dev menu.

### AI playing

- **UIA-33** AI playing shall open the ship, world and level selects, each titled "AI PLAYING" over its usual title, to
  pick the ship and level the AI plays (see `07-ai.md`); Back from the ship select goes back to the Dev menu.
- **UIA-34** Picking a level shall start the AI playing it, by the game's rules, with its music, effects and sounds.
  Over the game, a panel shall show: "AI PLAYING", the brain's generation (or that a new brain plays), what is on
  screen (the ship and the level), the games played from the level picked and how many cleared it (and the share), and
  the most levels cleared in one game. Escape shall go back to the level select, on that level.

### Screenshots

- **UIA-35** Screenshots shall make the README's picture of each world, one per world. Left/Right go to the previous or
  next world (starting from the world of the last level played; wrapping around), over the menus' ground.
- **UIA-36** Space shall play one of the world's levels, drawn at random, up to a moment drawn at random, and show it
  frozen with the HUD *(placeholders)*: a regular ship, a weapon selected, every weapon at the same level (2 to 5), a
  secondary weapon 40% of the time; 8 to 45 s into the level, or a quarter of the time 2 to 6 s into its first boss
  fight (giving up waiting after 180 s); the ship weaving around the screen with Fire held, unable to die. Space again
  for another one.
- **UIA-37** Enter shall save the game area as the world's screenshot, without the texts over it (a panel at the top:
  the world, the level and the shot, what is going on, the keys). Escape goes back to the Dev menu.

## Audio

### Music

- **UIA-38** The music shall be synthwave, made of MIDI songs played by the game's own synthesizer. Any MIDI file can
  replace a song.
- **UIA-39** The songs shall be *(placeholder)*:

| Song | Plays |
|------|-------|
| title | On every menu screen, the Dev menu's included (looping) |
| world_1 … world_8 | During that world's levels, paused or not, and while the AI plays them (looping) |
| boss | While any boss is in play, and from a final boss's destruction to the end of the level (looping) |
| level_complete | Once, on the level complete screen |
| game_over | Once, on the game over screen |

- **UIA-40** When the song changes, the old one shall fade out in 0.8 s. While paused, the music shall play at 35% of
  its volume. M shall turn the music on and off.
- **UIA-41** Each song shall be rendered once, in the background, in the order likely needed (title, the worlds', boss,
  the jingles), and kept in the user's cache folder, rendered again only when the synthesizer changes.
- **UIA-42** Volumes: sound effects 0.8, music 0.6 *(placeholders, until an options menu)*.
- **UIA-43** A new song (music browser) shall be composed from its song's plan, varied by a seed drawn at random
  *(placeholder)*: another key, a tempo within 10% of the plan's, another chord progression (the songs' own and a few
  more), drums, bass and arpeggio styles, brass or not, and new tunes; a jingle keeps its chords (a win or a loss), only
  its key, tempo and tune change. A song's title shall hold its name, key and chords ("Neon Horizon | A minor | i VImaj7
  III VII").

### Sound effects

- **UIA-44** Every sound effect shall be synthesized *(placeholders)*:

| Event | Sound |
|-------|-------|
| Player fires bullets, turret fires | A quick falling "pew" |
| Player fires missiles | A rising whoosh |
| Laser firing | A hum, as long as it fires |
| Lightning strike | A short crackling buzz |
| Player's shot hits an enemy | A short metallic tick |
| Explosion | Small (below 0.12 across), medium, or big (0.4 across or more, long); a missile's blast |
| Upgrade or secondary weapon picked up | A quick major arpeggio up |
| Repair picked up | A bright glide up |
| Extra life picked up | A bright fanfare climbing two octaves |
| Player's ship explodes | A big blast and a falling wail |
| Player hit without dying | A harsh falling buzz |
| A hit takes the secondary weapon | A short crunch and a falling blip |
| Menu: highlight moves / choose / back | A blip / two rising blips / two falling blips |
| Switching weapons | Two blips |
| A boss comes | A two-tone siren |

- **UIA-45** Each sound shall play at most once per frame, and not start again sooner than 0.05 s after itself (hits
  0.07 s, big explosions 0.4 s, the siren 2 s); up to 4 copies of a sound may play over each other.
