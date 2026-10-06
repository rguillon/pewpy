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
  (`graphics/lighting.py`, `graphics/models/`). The shield bubble is a smooth see-through effect; the laser is light (see "Laser" below); bullets
  are balls of energy facing the camera: a white-hot core in a solid body of the bullet's color, about its hitbox,
  with a brighter rim and an edge that ripples, the core throbbing, in a halo of light added to what's behind
  (ovals for the player's long bullets, which are bright green); with the halo, about 3.2 times their hitbox
  (`sprites.py`, `app/bullets.py`).
- Color palette / mood: TBD
- Target resolution and scaling (pixel-perfect?): TBD

## Assets

- Source of models / sprites (made by you, free packs, placeholders generated in code): generated in code
  (`src/pewpy/graphics/models/`), no 3D files. The voxel drawings (rows of characters, and each character's color and
  height in voxels) are JSON files in `data/models/`, one per model
- Model file forms: a model file (`data/models/<group>/<name>.json`) is a flat drawing (rows of characters, each
  color a thickness), a 3D drawing (`"layers"`: slices from the top down, with a palette), or a MagicaVoxel model
  (`"vox"`: a `.vox` file next to it). Engines can be placed above the middle plane (`"z"`). A flat or 3D drawing
  can list its `"weapons"`: {"number", "kind", "x", "y"}, the column and row of each barrel's tip (see
  `02-enemies.md`, "Enemy weapons"). `make voxels` moves
  a model between the three forms; `make models` remodels ships from their recipes in `pewpewdev/tools/models/recipes/`.
- Props (the things standing on the grounds: buildings, tanks, trees, hangars...) are JSON files in `data/models/props/`,
  one per prop: its `kind` (what the grounds ask for), the box it was drawn in (`size`), and its parts, each a shape
  (box, cylinder, disc, ellipsoid, gabled, ridge_roof, face, quad, lathe) with fixed geometry, fixed colors and a
  material (how the shader paints it: windows, furnace glow, light, metal...). Plain data: no conditions, no
  randomness. A kind with variants has several files; each prop on the ground picks one by its seed and is stretched
  to its lot (turned a quarter first if its longer side lies the other way). Only the lights the shader paints
  (lit and unlit windows, furnace glow) come from the scenery (`props` in `sceneries.json`).
  `make props` (`python -m pewpy.tools.generate_props <count>`) writes random prop candidates (assemblies of
  shapes, fixed size and colors) to `data/models/candidates/props/`, shown by the Prop candidates screen of `make dev`
  (ten a page, all at the same scale, leaning to show their roofs); a candidate joins the game when it's moved to
  `data/models/props/` with a name and a kind of its own.
- File formats (Panda3D supports `.egg`, `.bam`, `.gltf` via panda3d-gltf, `.png` textures…): TBD
- Asset folder layout: `data/models/` holds the voxel drawings by group, `enemies/` (projectiles included), `bosses/`
  (cores and parts), `player/` (the ships and the player's missile) and `items/` (the pickups), each named once across
  the groups (the game data names a model without its group); `props/` the props (`<name>.json`); `candidates/` what
  the tools make, not in the game: `enemies/`, `player/`, `bosses/`, `props/` *(the user's choice)*; other assets
  TBD

> Until real assets exist, Claude should use simple placeholder shapes generated in code.

## Effects

| Effect | Description |
|--------|-------------|
| Explosions | A fireball of soft glowing circles (pale yellow in the middle, orange to red around, swelling then shrinking, adding light where they overlap), round sparks, and tumbling voxel debris cubes in the colors of what blew up; bigger things blow up bigger. Missiles explode in an orange fireball with a ring of sparks. *(details are a placeholder)* |
| Laser | A thin white-cyan core that flickers, in a soft cyan halo, with streaks of light shooting up it from the ship's nose (about 3 to 4 screen heights a second, wobbling a little) and vanishing where the beam ends; more streaks for a wider beam. A pulsing glow at the nose and a flickering one on each enemy it burns. Streaks in flight when the beam is cut fly on and fade out. Enemies' laser beams (Lancer, Pincer, bosses) look the same in red, their streaks shooting down from the enemy's muzzle (a pulsing glow there) *(the user's choice)*; a laser's warning, before it fires, is a thin red line *(the user's choice)*. (`effects/laser.py`, `effects_view.py`) *(placeholder)* |
| Secondary weapons | The turret: a small green dome on the ship with a dark barrel turning toward its target; its shots look like the bullets. The lightning gun: a glowing violet orb on the ship; its bolt is a thin pale-violet zigzag line from the ship's nose to each enemy struck in turn, crackling (a new zigzag every frame). Losing one: a small explosion on the ship in its color. *(placeholder)* |
| Hit flash | Enemies flash white when hit (see `02-enemies.md`), and the whole time the laser touches them *(placeholder)* |
| Screen shake | TBD |
| Particles (engine trail, debris) | Sparks (soft glowing circles) where shots hit (enemies, shields, the player) and where the laser burns; voxel debris cubes from explosions. Engine flames: the player, the player's missiles and the ships that fly (enemies and bosses) have a jet flame behind each engine, pale blue with a white-hot core, soft and fading towards the tip, flickering; the player's grow when flying up and shrink when flying down. Each model's drawing says where its engines are and how big their flames are (`"engines"` in `data/models/<group>/<name>.json`). *(placeholder)* |
| Background (parallax layers, starfield, 3D terrain) | One per level, matching its setting, dark and muted so bullets and enemies stand out; see "Backgrounds" in `03-levels.md`. Frozen in menus and pause. *(details are a placeholder)* |
| Post-processing (bloom, CRT filter…) | None yet (lighting is done in the models' shader); bloom: TBD |
