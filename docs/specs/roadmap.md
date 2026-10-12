# Roadmap

> Ordered milestones. Claude implements one milestone at a time and ticks boxes when done.
> Edit freely: reorder, add, remove. The suggested milestones below are just a starting point.

## Milestone 1 — Window and ship

- [x] Add Panda3D as a dependency, `python -m pewpy` opens a window
- [x] Player ship (placeholder shape) moves with the keyboard, stays inside the play area
- [x] Basic tests running with `make test`

## Milestone 2 — Shooting and one enemy

- [x] Player fires bullets
- [x] One enemy type spawns and moves
- [x] Collisions: bullets kill enemies, enemies/bullets kill the player
- [x] Score and lives on screen

## Milestone 3 — First level

- [x] Level data format and loader
- [x] Wave timeline for level 1
- [x] Scrolling background
- [x] Game over and restart

## Milestone 4 — Depth

- [x] Weapons and power-ups
- [x] More enemy types
- [x] Levels 2 and 3
- [x] Enemy drops
- [x] First boss

## Milestone 5 — Polish

- [ ] Menus, pause, options
- [x] Sound and music
- [ ] Effects (explosions, particles, screen shake)
- [ ] High scores

## Later / ideas

- [x] AI player: learns to play by itself, measures its win rates on every level with every ship (`07-ai.md`)
- [x] Screenshots in the Dev menu: one per world, a moment of one of its levels drawn at random, saved as its README picture
  (`04-ui-audio.md`)
- [x] Music in the Dev menu: a music browser playing the songs, composing new ones and saving them (`04-ui-audio.md`)
- [x] AI playing in the game: the Dev menu's AI playing screen, the trained AI playing from the ship and level picked
  (`07-ai.md`, `04-ui-audio.md`)
- [x] Secondary weapons from enemy drops: a turret and a lightning gun, lost instead of health when hit (`01-gameplay.md`)
- [x] Longer levels in two halves, the second harder: the old bosses as mini bosses halfway, a bigger final boss per
  level; bosses' new shots (accel, curve, pellets, snaking, projectiles) and lasers announced by a warning beam
  (`03-levels.md`, `02-enemies-bosses.md`)
- [x] Dev menu in the game: a model browser for the player's ships, the enemies and the bosses, making new models of
  a size each model registers, every model with the same cubes (`04-ui-audio.md`, `05-visuals.md`)
- [x] Ships assembled from a catalog of over 400 built-in parts (hulls, wings, cockpits, engines, guns, details) placed
  where they fit, some ships lopsided; a parts browser in the Dev menu (`05-visuals.md`, `04-ui-audio.md`)
- [x] Bosses made like every other ship, only bigger, their destructible parts modules assembled at random from the
  catalog; gigantic guns, bigger wings, hulls and engines (`05-visuals.md`)
- [x] Any enemy may have destructible parts, by its size alone, made and saved like a boss's (`05-visuals.md`,
  `04-ui-audio.md`)
- [x] Bigger ships like flying cities: several hulls joined by beams (multihull, cluster) or a deck carrying buildings,
  likelier the bigger the ship (`05-visuals.md`)
- [x] Bigger ships have more engines (a row across every hull's tail) and longer flames (`05-visuals.md`)
