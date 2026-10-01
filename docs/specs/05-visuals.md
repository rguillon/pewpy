# 05 — Visuals

## Art style

- Overall style (pixel art, low-poly, neon vector, realistic…): voxels, like pixel art extruded into blocks or
  Minecraft. Ships look industrial sci-fi rather than cartoonish: grey metal hulls (lighter on top), recessed panel
  seams, dark engine nacelles with vents, dark glass cockpits and small orange or red lights; each kind of ship
  keeps its color as paint markings (blue for the player, red for the Drone...). Ships, missiles and pickups are drawn as rows of characters; each character has a color and a
  thickness in voxels, so cockpits and domes stick out and wings are thin. Every model is built with the same
  cubes, the Swarmer's (0.06 / 9 world units, `MODEL_VOXEL` in `config.py`), never stretched: a model's size comes
  from its drawing, about its hitbox (bigger ships have more cubes; a boss is up to about 70 cubes wide). Shiny look: per-pixel lighting,
  specular highlights, reflections of a made-up space environment, bevelled voxel edges and ambient occlusion
  (`lighting.py`, `models.py`). The shield bubble is a smooth see-through effect; the laser is light (see "Laser" below); bullets
  are soft round dots facing the camera: solid in the middle, fading out towards the edge (ovals for the
  player's long bullets, which are bright green), about 1.8 times their hitbox (`sprites.py`).
- Color palette / mood: TBD
- Target resolution and scaling (pixel-perfect?): TBD

## Assets

- Source of models / sprites (made by you, free packs, placeholders generated in code): generated in code
  (`src/pewpy/graphics/models.py`), no 3D files. The voxel drawings (rows of characters, and each character's color and
  height in voxels) are JSON files in `src/pewpy/models/`, one per model
- File formats (Panda3D supports `.egg`, `.bam`, `.gltf` via panda3d-gltf, `.png` textures…): TBD
- Asset folder layout: `src/pewpy/models/<name>.json` for the voxel drawings; other assets TBD

> Until real assets exist, Claude should use simple placeholder shapes generated in code.

## Effects

| Effect | Description |
|--------|-------------|
| Explosions | A fireball of soft glowing circles (pale yellow in the middle, orange to red around, swelling then shrinking, adding light where they overlap), round sparks, and tumbling voxel debris cubes in the colors of what blew up; bigger things blow up bigger. Missiles explode in an orange fireball with a ring of sparks. *(details are a placeholder, see decisions.md)* |
| Laser | A thin white-cyan core that flickers, in a soft cyan halo, with streaks of light shooting up it from the ship's nose (about 3 to 4 screen heights a second, wobbling a little) and vanishing where the beam ends; more streaks for a wider beam. A pulsing glow at the nose and a flickering one on each enemy it burns. Streaks in flight when the beam is cut fly on and fade out. (`effects.py`, `effects_view.py`) *(placeholder, see decisions.md)* |
| Hit flash | Enemies flash white when hit (see `02-enemies.md`), and the whole time the laser touches them *(placeholder, see decisions.md)* |
| Screen shake | TBD |
| Particles (engine trail, debris) | Sparks (soft glowing circles) where shots hit (enemies, shields, the player) and where the laser burns; voxel debris cubes from explosions. Engine flames: the player, the player's missiles and the ships that fly (enemies and bosses) have a jet flame behind each engine, pale blue with a white-hot core, soft and fading towards the tip, flickering; the player's grow when flying up and shrink when flying down. Each model's drawing says where its engines are and how big their flames are (`"engines"` in `src/pewpy/models/<name>.json`). *(placeholder, see decisions.md)* |
| Background (parallax layers, starfield, 3D terrain) | One per level, matching its setting, dark and muted so bullets and enemies stand out; see "Backgrounds" in `03-levels.md`. Frozen in menus and pause. *(details are a placeholder, see decisions.md)* |
| Post-processing (bloom, CRT filter…) | None yet (lighting is done in the models' shader); bloom: TBD |
