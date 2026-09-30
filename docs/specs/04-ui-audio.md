# 04 — UI, Game Flow and Audio

## Game flow

> Describe the screens and how the player moves between them.

```text
Main menu -> Ship select -> World select -> Level select (the world's 8 levels) -> Playing <-> Pause
Main menu <-> Models
Main menu <-> Bosses
Playing -> Level complete ("World complete" after a world's last level) -> next level (Playing, into the next
world after a world's last level), or after the very last level: "YOU WIN" -> Main menu
Playing -> Game over -> Continue (restart the level) or Main menu
Pause -> Main menu
```

*(placeholder, see decisions.md: menus, keys and HUD layout; level end and the LEVEL_COMPLETE state; worlds)*

## Screens

### Title / main menu

- Every menu: Up/Down move the highlight (wrapping around), Enter chooses, Escape goes back.
- Entries: Start (to the ship select: one entry per ship, then Back; under the menu, every ship side by side with
  its name and bars comparing armor, speed, size and repair; the highlighted one is bigger, spins, has bright bars,
  and its description and numbers show at the bottom; then the world select: one entry per world, then Back to the ship select; then that
  world's level select: its 8
  levels, like "2-5 Harvest Dusk", then Back; both open on the last level played), Models, Bosses, Quit *(entries are a
  placeholder, see decisions.md)*

### Models

- For working on the models: every ship, enemy, projectile and pickup in a circle facing the camera, each spinning
  on itself with its name under it, the circle turning slowly, on a plain dark background. Three pages (too many
  models for one circle): the player, the pickups and the projectiles (the player's missile, enemy rockets,
  missiles and bombs, mines); the flying enemies; the ground enemies.
- Entries: Next page (after the last page, back to the first), Reload models (reads `src/pewpy/models.py` and the drawings in `src/pewpy/models/` again and rebuilds
  every model, in the game too; if a file has a mistake, the error is shown and the old models stay), Back. Escape
  goes back to the main menu.

### Bosses

- Like the Models screen, for the bosses: one page per world with its 8 bosses (whole, with their parts), bigger;
  the title says the world and the page, like "Orbit (1/5)".
- Entries: Next page (after the last world, back to the first), Reload models, Back. Escape goes back to the main
  menu.

### Options

- Settings: TBD (volume, fullscreen, resolution, key bindings, difficulty…)
- Saved where / how: TBD

### Pause

- Entries: Resume, Main menu; Escape resumes *(placeholder, see decisions.md)*

### Game over / high scores

- Game over: Continue (restart the level), Main menu; Escape goes to the main menu *(placeholder, see
  decisions.md)*
- High scores: TBD

## HUD (in-game display)

> What is shown, and where on screen.

| Element | Position | Notes |
|---------|----------|-------|
| Score | Bottom-left corner, close to the edges *(placeholder, see decisions.md)* | TBD |
| Lives | Bottom-right corner, close to the edges *(placeholder, see decisions.md)* | TBD |
| Health | Bottom center, at the edge: a thin bar, green over dark red *(placeholder, see decisions.md)* | One bar per life |
| Bombs | TBD | TBD |
| Weapon level | Bottom center, just over the health bar *(placeholder, see decisions.md)* | The three weapons with their level, e.g. "B2 L1 M3"; the selected one is highlighted |
| Boss health bar | Top center, at the edge: a wide orange bar over dark red, the boss's name under it *(placeholder, see decisions.md)* | Only while the boss is on screen; counts the core and its parts together |

- Font: TBD

## Audio

- Music style: TBD
- Music source (your files, free assets, generated): TBD
- Sound effects needed:

| Event | Description |
|-------|-------------|
| Player shot | TBD |
| Enemy hit | TBD |
| Explosion | TBD |
| Pickup | TBD |
| Player death | TBD |
| Menu select | TBD |
