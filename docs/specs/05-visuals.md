# 05 — Visuals

## Art style

- Overall style (pixel art, low-poly, neon vector, realistic…): voxels, like pixel art extruded into blocks or
  Minecraft. Ships, missiles and pickups are drawn as rows of characters; each character has a color and a
  thickness in voxels, so cockpits and domes stick out and wings are thin. Shiny look: per-pixel lighting,
  specular highlights, reflections of a made-up space environment, bevelled voxel edges and ambient occlusion
  (`lighting.py`, `models.py`). The shield bubble and the laser beam are smooth see-through effects; bullets
  are soft round dots facing the camera: solid in the middle, fading out towards the edge (ovals for the
  player's long bullets, which are bright green), about 1.8 times their hitbox (`sprites.py`).
- Color palette / mood: TBD
- Target resolution and scaling (pixel-perfect?): TBD

## Assets

- Source of models / sprites (made by you, free packs, placeholders generated in code): generated in code
  (`src/pewpy/models.py`), no 3D files. The voxel drawings (rows of characters, and each character's color and
  height in voxels) are JSON files in `src/pewpy/models/`, one per model
- File formats (Panda3D supports `.egg`, `.bam`, `.gltf` via panda3d-gltf, `.png` textures…): TBD
- Asset folder layout: `src/pewpy/models/<name>.json` for the voxel drawings; other assets TBD

> Until real assets exist, Claude should use simple placeholder shapes generated in code.

## Effects

| Effect | Description |
|--------|-------------|
| Explosions | A fireball of soft glowing circles (pale yellow in the middle, orange to red around, swelling then shrinking, adding light where they overlap), round sparks, and tumbling voxel debris cubes in the colors of what blew up; bigger things blow up bigger. Missiles explode in an orange fireball with a ring of sparks. *(details are a placeholder, see decisions.md)* |
| Hit flash | Enemies flash white when hit (see `02-enemies.md`), and the whole time the laser touches them *(placeholder, see decisions.md)* |
| Screen shake | TBD |
| Particles (engine trail, debris) | Sparks (soft glowing circles) where shots hit (enemies, shields, the player) and where the laser burns; voxel debris cubes from explosions. Engine flames: the player and the ships that fly (enemies and bosses with engines) have a jet flame behind each engine, pale blue with a white-hot core, soft and fading towards the tip, flickering; the player's grow when flying up and shrink when flying down. Each model's drawing says where its engines are and how big their flames are (`"engines"` in `src/pewpy/models/<name>.json`). *(placeholder, see decisions.md)* |
| Background (parallax layers, starfield, 3D terrain) | One per level, matching its setting, dark and muted so bullets and enemies stand out; see "Backgrounds" in `03-levels.md`. Frozen in menus and pause. *(details are a placeholder, see decisions.md)* |
| Post-processing (bloom, CRT filter…) | None yet (lighting is done in the models' shader); bloom: TBD |
