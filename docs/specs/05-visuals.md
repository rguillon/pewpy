# 05 — Visuals

Units: see `00-vision.md`.

## Art style

- **VSL-1** Every ship, enemy, boss, projectile and pickup shall be a voxel model: like pixel art extruded into blocks.
  Every model shall be built with the same cubes, 0.06 / 9 wu across (≈ 0.00667), never stretched nor scaled; a
  model's size comes from its drawing and shall be about its hitbox (bigger ships have more cubes; a boss is up to about
  70 cubes wide).
- **VSL-32** Where a model's cubes form a staircase, along any of the three axes (the outline of the drawing, or a
  thicker part stepping down to a thinner one), the stair shall read as a straight 45° slope: the cube on the outer
  corner of each step is cut in half along the diagonal through its middle. A cube is cut across an edge when its two
  sides there are open, the two opposite ones touch other cubes and the stair goes on (a cube one step further along
  it, past either side). Flat sides, the square corners of a rectangle and lone spikes stay square; glowing and burning
  cubes are never cut.
- **VSL-2** Ships shall look industrial sci-fi rather than cartoonish: grey metal hulls (lighter on top), recessed panel
  seams, dark engine nacelles with vents, dark glass cockpits and small orange or red lights; each kind of ship keeps
  its color as paint markings (bluish grey for the player's ships, red for the Drone...).
- **VSL-3** A model shall be drawn either as rows of characters, each character a color and a thickness in voxels (so
  cockpits and domes stick out and wings are thin), or as a full 3D drawing (slices from the top down).
- **VSL-4** Every model the makers build shall be one piece: each cube touches another through a face, nothing floats
  on its own; a piece left apart shall be joined to the nearest one by the shortest strut (on a boss, a strut 3 cubes
  wide under the hull; mirrored on a symmetric model).
- **VSL-5** Models shall look shiny: per-pixel lighting, specular highlights, reflections of a made-up space
  environment, bevelled voxel edges and ambient occlusion.
- **VSL-6** Models shall list where their engines are (and how big their flames are) and where their weapons' barrel
  tips are (numbered, with their kind: gun, gatling, cannon, turret, flak, missile, laser). The makers' models shall
  always have weapons: at least one on an enemy, at least five on a boss (core and parts together).
- **VSL-7** Built-in parts shall be small 3D pieces of machinery, symmetric, made to any size, stamped on models: guns
  (a turret, a twin cannon, a gatling, a missile rack, a flak gun, a beam emitter: their barrels' tips are the model's
  weapons), an engine (its nozzle a flame), and details (a reactor, a radar, an antenna, a sensor dome, a vent, a
  radiator, exhaust stacks, a fuel tank). Housings shall be plated: a lighter rim, seams across, a light in the front
  corners. Bosses are covered in them and their destructible parts are built-in parts; enemies carry one or two small
  ones on their hull, 60% of them *(placeholder)*.
- **VSL-8** Bullets shall be balls of energy facing the camera: a white-hot core in a solid body of the bullet's color,
  about its hitbox, with a brighter rim and an edge that ripples, the core throbbing, in a halo of light added to what is
  behind; with the halo, about 3.2 times their hitbox. The player's bullets shall be bright green ovals; enemy shots are
  colored by kind (ENM-11).
- **VSL-9** The player's missiles and the enemies' projectiles shall be models pointing the way they fly; mines and
  cluster bombs spin (90° per second).
- **VSL-10** Pickups shall spin on themselves at 120° per second.
- **VSL-11** A Shield Carrier's shield shall be a smooth see-through light blue bubble around it, shown while the shield
  is up.
- **VSL-12** Enemy looks by state: "flash" white (hit, charging, a boss's phase pause), "armored" darker, "hit"
  brighter (bosses), "hidden" not drawn.
- **VSL-13** Ground props (buildings, tanks, trees, hangars...) shall be plain shapes (box, cylinder, disc, ellipsoid,
  gabled roof, ridge roof, face, quad, lathe) with fixed colors and a material (windows, furnace glow, light, metal...).
  A prop with variants has several versions; each prop on the ground picks one by its place and is stretched to its
  lot (turned a quarter first if its longer side lies the other way). Only the lights (lit and unlit windows, furnace
  glow) come from the level's scenery.
- **VSL-14** No 3D model files: every model shall be made from the game's own drawings, in code.
- **VSL-30** Palette: grey metal ships with colored markings, backgrounds dark and muted, bright colored shots (green
  for the player's, pink, blue, orange, violet, cyan and yellow for the enemies'), red lasers, amber readouts on
  gunmetal panels for the HUD and menus.
- **VSL-31** The 3D view shall be smoothly scaled to the window (not pixel-perfect): it is drawn at most 1440 pixels
  tall and stretched with linear filtering (TEC-4).

## Model makers

The Dev menu's model browser makes new models (UIA-23).

- **VSL-15** An enemy shall be a real 3D voxel model assembled from a kit of parts: a hull (a profile stretched along the
  ship), wings (an outline), a tailplane or canards, a cockpit (bubble, canopy, visor, bridge or sensor eye), engines
  (tail nozzles or nacelles), weapons (nose barrels, wing and tip guns, missiles, a turret, a gatling, a side cannon),
  fins, antennas, a radar dome, intakes, armor, a livery stripe and markings. There shall be six kinds, each a recipe
  choosing and placing the parts: fighter, interceptor, bomber, drone, gunship, heavy.
- **VSL-16** A player's ship shall be made from the enemies' kit. Its class sets its size: vanguard (balanced),
  juggernaut (heavy), phantom (light); the rest is picked on its own, for variety: the hull, the wings' layout (one
  pair, crossed X wings, stacked pairs, a small pair forward, a flying wing, two booms) and outline, the engines (tail,
  booms, pods on the wings or the hull), the cockpit, the weapons and the extras. Its main color shall always be a
  bluish grey, with colored bits (a livery stripe, a nose cone, wing stripes, markings, sensors). It shall point up the
  screen, flames out of its tail, without weapons listed (the player's guns do not fire from the model).
- **VSL-17** A boss shall be a real 3D voxel model sculpted from a plan: stepped decks and a superstructure on the hull,
  the bridge on top, recessed panel lines and hangar bays, 0 to 2 big appendages; then no flat zone left plain: plating
  panels raised or sunk, and mostly built-in parts on the hull and decks (reactors, radars, antennas, sensor domes,
  vents, radiators, exhaust stacks, fuel tanks, armed guns, engines near the back with flames going back), with blocks,
  pipes, lights and lit trenches, ribs and weapon pods on the wings.
- **VSL-18** A boss's destructible parts shall be built-in parts (turrets, twin cannons, gatlings, missile racks, flak
  guns, beam emitters, reactors, radars; one to three kinds a boss), each standing on the hull where it is mounted, on a
  socket following its outline. Their number comes from the core's size: one part for every 600 square cubes of the
  core, in mirrored pairs (one in the middle for an odd number), 2 to 12 *(placeholder)*; a lopsided boss stays
  lopsided. Each drawing lists its weapons: the parts' barrels (a missile rack: its middle warhead; a gatling: its
  spindle), and guns on the core's front edge, enough for at least five on the boss.
- **VSL-19** A new model shall be made several times, scaled towards the intended size, and the one nearest that size
  (its width and its height both) kept: 60 tries for a ship, whose kind sets its proportions, so the tries' variety
  follows the shape asked; 12 for a boss, made to the width and height asked.

## Effects

- **VSL-20** Explosions shall be a fireball of soft glowing circles (pale yellow in the middle, orange to red around,
  swelling then shrinking, adding light where they overlap), round sparks, and tumbling voxel debris cubes in the colors
  of what blew up; bigger things blow up bigger *(placeholder details)*.
- **VSL-21** A missile shall explode in an orange fireball with a ring of sparks, the size of its splash.
- **VSL-22** Hits shall throw sparks (soft glowing circles) where a shot hits, flying back the way the shot came (down
  from enemies, up from the player); the laser shall throw cyan sparks where it burns.
- **VSL-23** The player's laser shall be a thin white-cyan core that flickers (its width ±12%), in a soft cyan halo, with
  streaks of light shooting up it from the ship's nose (about 3 to 4 screen heights a second, wobbling a little) and
  vanishing where the beam ends; more streaks for a wider beam. A pulsing glow shall show at the nose and a flickering
  one on each enemy it burns. Streaks in flight when the beam is cut fly on and fade out *(placeholder)*.
- **VSL-24** Enemies' laser beams (Lancer, Pincer, bosses) shall look the same in red, their streaks shooting down from
  the enemy's muzzle (a pulsing glow there). A laser's warning shall be a thin see-through red line where the beam
  will be.
- **VSL-25** The turret shall be a small green dome on the ship with a dark barrel turning towards where it last fired;
  its shots look like the bullets. The lightning gun shall be a glowing violet orb on the ship; its bolt a thin
  pale-violet zigzag line (3 pixels, a zig every 0.05 wu, up to 0.025 to each side) from the ship's nose to each enemy
  struck in turn, crackling (a new zigzag every frame). Losing one shall be a small explosion on the ship in its color
  *(placeholder)*.
- **VSL-26** Engine flames: the player, the player's missiles and the flying enemies and bosses shall have a jet flame
  behind each engine, pale blue with a white-hot core, soft and fading towards the tip, flickering (a slow and a fast
  wave in its length); the player's shall be up to 35% longer flying up and shorter flying down *(placeholder)*.
- **VSL-27** Particles shall keep moving after the last explosion of a level or a life, on the play, game over and
  level complete screens, and while the AI plays; they shall freeze in pause and the menus.
- **VSL-28** There shall be no screen shake and no post-processing (bloom, CRT filter): the glow comes from the
  models' lighting and the effects' light added to what is behind.
- **VSL-29** Backgrounds: see `03-levels.md`; they shall freeze in pause.
