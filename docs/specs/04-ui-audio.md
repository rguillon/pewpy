# 04 — UI, Game Flow and Audio

## Game flow

> Describe the screens and how the player moves between them.

```text
Main menu -> Ship select -> World select -> Level select (the world's 6 levels) -> Playing <-> Pause
Main menu <-> Models
Main menu <-> Bosses
Main menu <-> Enemy candidates
Main menu <-> Boss candidates
Playing -> Level complete ("World complete" after a world's last level) -> next level (Playing, into the next
world after a world's last level), or after the very last level: "YOU WIN" -> Main menu
Playing -> Game over -> Continue (restart the level) or Main menu
Pause -> Main menu
```

*(placeholder: menus, keys and HUD layout; level end and the LEVEL_COMPLETE state; worlds)*

## Screens

### Title / main menu

- Every menu: Up/Down move the highlight (wrapping around), Enter chooses, Escape goes back.
- Behind the main menu: a space background *(placeholder)*.
- Entries: Start (to the ship select: one entry per ship, then Back; under the menu, every ship side by side with
  its name and bars comparing armor, speed, size and repair; the highlighted one is bigger, spins, has bright bars,
  and its description and numbers show at the bottom; then the world select: one entry per world, then Back to the ship select; then that
  world's level select: its 6
  levels, like "2-5 Twilight Grove", then Back, with a window above the list showing the highlighted level's
  ground scrolling by, as in the game; both open on the last level played), Quit *(entries are a placeholder)*
- With the dev tools (`make dev`: the game with the screens below, `src/pewpewdev/`), more entries after Start:
  Models, Bosses, Enemy candidates, Boss candidates, AI learning, AI rating (see `07-ai.md`). Not in the game.

### Models (dev tools)

- For working on the models: every ship, enemy, projectile and pickup in a circle facing the camera, each spinning
  on itself with its name under it, the circle turning slowly, on a plain dark background. Three pages (too many
  models for one circle): the player, the pickups and the projectiles (the player's missile, enemy rockets,
  missiles and bombs, mines); the flying enemies; the ground enemies.
- Entries: Next page (after the last page, back to the first), Reload models (reads `src/pewpy/graphics/models.py` and the drawings in `data/models/` again and rebuilds
  every model, in the game too; if a file has a mistake, the error is shown and the old models stay), Back. Escape
  goes back to the main menu.

### Bosses (dev tools)

- Like the Models screen, for the bosses: two pages per world, its 6 mini bosses then its 6 final bosses (whole,
  with their parts), bigger; the title says the world, which bosses and the page, like
  "Highlands: final bosses (2/16)".
- Entries: Next page (after the last world, back to the first), Previous page, Reload models, Back. Escape goes
  back to the main menu.

### Enemy candidates (dev tools)

- For picking new enemies: model candidates (drawings in `data/models/candidates/`, numbered 001, 002...; not
  used in the game) on show like the Models screen, 10 per page, each labelled with its number ("#007"); the title
  says which numbers and the page, like "11-20 (2/10)".
- Entries: Next page, Previous page, Reload models, Back. Drawings are read again whenever a page is shown.
- Made by `make candidates` (pewpewdev/tools/make_candidates.py), as real 3D voxel models: the aircraft built from their
  parts, the industrial ships sculpted from a plan (a chamfered hull, higher on top than underneath, a raised spine
  and cockpit, recessed panel lines, thin wings rising to their tips).

### Boss candidates (dev tools)

- For picking new bosses: boss candidates (`data/models/boss_candidates/`: a core, its parts' drawings and
  where they go, see pewpewdev/tools/make_boss_candidates.py; not used in the game), each whole with its parts, 4 per page,
  all drawn to the same scale, labelled with their number, size in cubes and how many parts ("#007  51x42 +2").
- Entries: Next page, Previous page, Reload models, Back. Made by `make boss-candidates`, as real 3D voxel models
  sculpted from a plan: stepped decks and a superstructure on the hull, the bridge on top, recessed panel lines and
  hangar bays; each part stands on the hull where it's mounted.

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
| Score | Bottom-left corner, close to the edges *(placeholder)* | TBD |
| Lives | Bottom-right corner, close to the edges *(placeholder)* | TBD |
| Health | Bottom center, at the edge: a thin bar, green over dark red *(placeholder)* | One bar per life |
| Bombs | TBD | TBD |
| Weapon level | Bottom center, just over the health bar *(placeholder)* | The three weapons with their level, e.g. "B2 L1 M3"; the selected one is highlighted; then the secondary weapon if the ship carries one, "+T" or "+Z" in its color *(placeholder)* |
| Frames per second | Top-right corner, small and dim, on every screen (menus too) *(the user's choice)* | Averaged over a second, refreshed twice a second; `SHOW_FPS` in `config.py` turns it off |
| Boss health bar | Top center, at the edge: a wide orange bar over dark red, the boss's name under it *(placeholder)* | Only while the boss is on screen; counts the core and its parts together |

- Font: TBD

## Audio

- Music style: synthwave *(the user's choice)*
- Music source (your files, free assets, generated): generated MIDI songs *(the user's choice)*: `make songs`
  writes them to `data/music/` (pewpewdev/tools/make_songs.py); the game plays them with its own synthesizer. Any MIDI
  file can replace one. Songs *(placeholder)*: "title" on the menus, "world_1" to "world_8" for
  each world's levels, "boss" while a boss is fought (from the final boss's coming, until the level ends), and two jingles played once,
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
