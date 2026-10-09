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
  on its own; a piece left apart shall be joined to the nearest one by the shortest strut (mirrored on a symmetric
  model).
- **VSL-5** Models shall look shiny: per-pixel lighting, specular highlights, reflections of a made-up space
  environment, bevelled voxel edges and ambient occlusion.
- **VSL-6** Models shall list where their engines are (and how big their flames are) and where their weapons' barrel
  tips are (numbered, with their kind: gun, gatling, cannon, turret, flak, missile, laser). The makers' models shall
  always have weapons: at least one on an enemy, at least five on a boss (core and parts together).
- **VSL-7** Housings shall be plated, on every part of the catalog (VSL-33) that has one: a lighter rim, seams across,
  a light in the front corners. Bosses are covered in the catalog's parts (VSL-17) and their destructible parts are
  assembled from them (VSL-18).
- **VSL-33** The catalog of built-in parts, which ships are assembled from and bosses are covered in, shall be big
  (over 400 parts), each part drawn once in code, named ("dart hull, large", "twin barrels, short"), never stretched,
  and one piece. Its kinds: connectors (girders, lattice trusses, tubes, pipe bundles, made to any length, running
  across between two hulls; the catalog showing each in 3 lengths), hulls (16 profiles: round, boxy or diamond
  cross-sections; made to any size, the catalog showing each in 6 sizes, tiny to colossal; a hull at most 8 cubes high
  on top however wide *(placeholder)*), wings (16 outlines, some rising or drooping, no more than one 12 cubes long
  *(placeholder)*; made to any size, the catalog showing each in 8 sizes, tiny to titanic), cockpits (bubbles, framed
  canopies, a tandem and a twin canopy, visors, bridges, one on a deck, glass domes, an armored slit, a command tower
  off its middle; sensor eyes and a glazed nose on the nose), engines (tail nozzles in 4 sizes, blocks and clusters
  (giant ones, an engine bank), slot nozzles, an ion engine, afterburners; nacelles), guns (barrels, cannons,
  gatlings, beam emitters, railguns on the nose; turrets, flak guns on top; a ball turret and gun, cannon, laser pods
  underneath; tip guns; a side cannon and a sponson), heavy guns (heavy, gigantic and colossal cannons, a siege
  railgun and a mega gatling on the nose; battleship and dreadnought turrets on top), missiles (under a wing, rocket
  pods, on the tips, racks and missile batteries on top, a side launcher, a cruise missile), vents, intakes, fins,
  antennas, sensors, tanks, armor, lights and machinery. Each part says how it mounts: as the hull, between two hulls,
  on the hull's side (a left wing, mirrored for the right), on top, on the nose, on the tail, as a pod, underneath, on
  a side, on a wing's tip. Only wings, connectors, side parts and the command tower are lopsided; the right side's
  copy of a part is its mirror image. Guns' barrel tips are the ship's weapons, engines' nozzles its flames.
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

- **VSL-15** Ships (the player's, the enemies' and the bosses', VSL-17) shall be assembled from a catalog of built-in
  parts (VSL-33): hulls, wings, a cockpit, engines, guns and missiles, details. A ship is made for a size: its frame
  first (its hull, wings, pods or booms, engines), then the rest, which stays within the frame's columns and rows but
  for a little room ahead for the guns on its nose (2 rows, or 5% of its length) *(placeholder)*. Its main hull and
  its wings (and its pods and booms, but engine pods) are made to measure from a profile or an outline picked at
  random (VSL-33): the hull about its length (leaving 3 rows and 6% of it for the engines and guns), its wings
  reaching the width left; every other part is picked from the catalog in proportion to the hull (at most half its
  length, and ¾ of its thickness high, 2 cubes at least; a cockpit as high as the hull is thick; an engine or a pod 1
  cube thicker than it), each picked at random among the 4 nearest what is wanted *(placeholder)*. Its layout
  *(placeholder shares)*: classic (a hull and a pair of wings, 40%; 50% for the player), flying wing (a short hull,
  wide long-chorded wings, 12%; 15%), pods (wings and a pod beside the hull on each side: an engine nacelle or a small
  hull, 14%; 15%), booms (wings carrying a boom each, sticking out behind them, a fin on its tail, 14%; 20%), wingless
  (a wide hull, 20%; never for the player). Classic and booms ships get canards or a tailplane 40% of the time. Bigger
  ships look less like aircraft and more like flying cities: a ship takes a city-like layout instead with a chance
  growing with its area, none under 600 square cubes, 75% from 4000 *(placeholder)*: multihull (a narrow main hull and
  one or two more on each side, parallel, spaced across its width, each joined to the one inside it by one to three
  beams across, 35%), cluster (a core hull and satellites of other shapes round it, one more for every 3000 square
  cubes, up to 4, each joined by beams to the core or to a satellite already there, a chain going out, 40%), city (a
  wide deck, a boxy hull, carrying 3 to 12 buildings: smaller hulls standing on it, 30% of them with a smaller one on
  top, 25%) *(placeholder shares)*. The beams are connectors of one style a ship (VSL-33); a lopsided ship's other
  hulls may be on one side only. Satellites and side hulls may carry engines on their tails; details and destructible
  parts go on any of its hulls.
- **VSL-34** Parts shall be placed where their mount goes on what is already there: wings on the hull's sides, their
  root sinking into it; engines in a row across the tail of each of its hulls (the main one, side hulls, satellites;
  not one with another hull right behind it), about one for every 1000 square cubes of the ship, at most 16, shared
  out by how wide each tail is (across its back 15%), side by side, as wide as the tail leaves them and at most a
  quarter of their hull's length long *(placeholder)*; and maybe more at the booms' tails, under the wings or on their
  tips; always at least one; a cockpit on top of the hull in its front half, or on the nose (15%); guns and missiles
  on the nose (or a pair on its cheeks), on top, under the wings or on their tips (under the hull without wings), and
  on one side for a lopsided ship; details on top of the hull (fins near its tail) or of a wing, on the hull's sides,
  underneath (drop tanks under the wings). A part only goes where it fits: at most a share of it sinking into what's
  there (half a wing; nothing for most), on top only where at least 60% of it stands on the ship, never in front of a
  barrel or behind a nozzle, its own barrels and nozzles clear; else another place or part is tried, 12 times
  *(placeholder)*. Pieces left apart are then joined by struts (VSL-4).
- **VSL-35** 75% of the enemies' ships and 85% of the player's shall be symmetric, every part off the axis with its
  mirror image *(placeholder)*. The others are lopsided, one or two ways: different wings on each side, a pod or a
  boom on one side only, a side cannon, a sponson or a missile launcher on one side, a command tower off the axis; their
  details and wing parts go on both sides or on one of them.
- **VSL-36** Armament: an enemy gets 1 to 3 weapons, one more per 900 square cubes *(placeholder)*, always at least
  one (if nothing fits, a barrel sunk into the nose, its tip no further ahead than the room left for the nose guns);
  the player's ship 1 or 2 (shown, not listed). Details: 1 to 3, one more per 250 square cubes, at most 40, one fin at
  most *(placeholder)*. Then the bits are painted: none, one or two of a livery stripe across the top, a nose cone in
  the accent, stripes along the wings; markings on the wing tips 60% of the time.
- **VSL-37** A canopy shall be glass blown round over a dark coaming, highest towards its front, a streak of light
  along its top (a lighter glass color), thin dark frame bows across its top, and a plated fairing behind it running
  down into the hull. A visor is an armored hood, glass wrapping round its front half and sloping to the hull. A bridge
  is an armored cab, windows round its front, a roof glazed along its front edge, a mast with a light. A sensor eye is
  a lens bulging out of a dark rim; a glazed nose is panes of glass in a frame.
- **VSL-16** A player's ship shall be made like an enemy's, at its class's size. Its main color shall always be a
  bluish grey, with colored bits (a livery stripe, a nose cone, wing stripes, markings, sensors). It shall point up
  the screen, flames out of its tail (8 to 11 cubes long; an enemy's 4 to 8; on a ship more than 25 rows long, longer
  as much as it is *(placeholder)*), without weapons listed (the player's guns do not fire from the model).
- **VSL-17** The player's ships, the enemies and the bosses shall all be made the same way (VSL-15 and VSL-34 to
  VSL-36): only their size differs, and with it the chance of destructible parts (VSL-18). The game's rules add three
  things: the player's ships never have destructible parts, a boss always does, and a boss has at least five weapons,
  its own and its parts' together (anything else one); if the weapons it gets fall short, more are tried, then barrels
  sunk into its nose side by side (as VSL-36). A lopsided boss stays lopsided, a symmetric one symmetric.
- **VSL-18** Any enemy (a boss or not) may have destructible parts, by its size alone: never under 300 square cubes,
  always from 1350 (every boss), the chance growing with its area between *(placeholder)*. They shall be modules
  assembled at random from the catalog's parts, of one to three kinds a model, each kind a main piece from the
  catalog: turret (a turret, a flak gun, a battleship turret), cannon (a cannon, a railgun, a gatling on the nose),
  launcher (a missile rack or battery), emitter (a beam emitter), sensor, tank. Its size grows with the model's width
  (0 or 1, one more per 40 cubes of it, at most 6), the main piece picked among the 3 nearest 3 + 2 × size cubes wide
  *(placeholder)*: a platform (a short wide hull cut flat underneath), the main piece on it (a gun on the nose
  standing a little in from the platform's back, its barrel reaching past its front), and in mirrored pairs (or one in
  the middle): small guns on the platform's front on an armed module whose main piece leaves its front free (60%),
  armor plates on its sides (50%), stub wings (25%), 1 to 3 details on its deck (vents, sensors, antennas, tanks,
  lights, machinery) *(placeholder)*, each only where it fits, joined into one symmetric piece. Their number comes
  from the model's size: one part for every 600 square cubes of it, in pairs, 2 to 12 *(placeholder)*. They're placed
  once the cockpit is on, before the weapons: standing on the hull (from 15% to 85% of its length) or, a pair, on the
  wings (a part on each), in mirrored pairs (one on the axis for an odd number; on a lopsided model alone or in pairs,
  anywhere across), each where at least 40% of it stands on the model and it fits (a smaller one if it must); one that
  fits nowhere is left out, but a model with none at all gets the smallest on its axis, halfway along, standing on
  what's under it *(placeholder)*; nothing else is then placed where they stand nor in front of their barrels. They're
  drawn apart from the model, a pair sharing one drawing, each standing at its height on it. Each drawing lists its
  weapons: the parts' barrels, and the model's own guns.
- **VSL-19** A new model shall be framed for the intended size (VSL-15) in 4 tries *(placeholder)*: each framed once,
  then framed again from the same choices, aimed as much off the size as the first frame came out off it the other
  way, the better of the two kept. The frame nearest the size (its width and its height both, less the room for the
  nose guns) is the one finished. The same for a ship as for a boss.
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
