# 06 — Technical

## Platform

- **TEC-1** The game shall be written in Python (3.12 or later) with Panda3D (1.10.16 or later).
- **TEC-2** The game shall use no machine learning library: the AI's neural network and its training are written with
  numpy alone (see `07-ai.md`). The game shall need no other library than Panda3D and numpy.

## Window and performance

- **TEC-3** The window shall open at 1280 × 1024, titled "pewpy", resizable; the game area shall keep its 5:4 shape
  with black bars around it. There shall be no fullscreen mode.
- **TEC-4** The 3D view shall be drawn at most 1440 pixels tall, then stretched over the game area; the HUD and menus
  shall be drawn at the window's own resolution, so text stays sharp *(placeholder; open: a graphics option?)*.
- **TEC-5** The game shall sync to the screen's refresh rate. A frame's time step shall be capped at 0.1 s, so a stall
  does not make a huge jump. The frame rate is the screen's (no other cap).
- **TEC-19** At most 512 round bullets shall be drawn at once (beyond that the game logic goes on, the extra ones
  are not drawn).
- **TEC-20** The game shall run on any computer with an OpenGL graphics driver, a software renderer included
  (much slower); it shall not check the hardware.
- **TEC-6** Under WSL, the game shall use the GPU (through Mesa's d3d12 driver) when it is available, and shall close
  at once when quit.

## Game rules and data

- **TEC-7** The game rules (movement, collisions, scoring, waves, enemies, weapons, the AI player) shall run without a
  window, so they can be tested and the AI can train without one.
- **TEC-8** Collisions shall be axis-aligned rectangle overlaps of hitboxes; moves shall use the frame's time step
  (variable time step) *(placeholder)*.
- **TEC-9** Content shall be data loaded by the game, editable without changing code: the rules' numbers (lives,
  pickups, damages), the ships, the player's weapons, every enemy, boss and projectile (their bodies, states, moves,
  guns and parts), the levels, the backgrounds' values, the models' drawings and props, the songs and the AI's brain.
  The same gun description shall serve the player's weapons and the enemies'.
- **TEC-10** Content data shall be checked when loaded: a typo or an unknown value shall be reported with the file and
  the place in it (the wave's number, the enemy's name, the gun's weapon number...).
- **TEC-11** The game logic shall never need to load a 3D model; it shall only read where a model's weapons are.

## Testing

- **TEC-12** Every line and branch of the game shall be covered by unit tests (100%); the test run shall fail below it.
  Code that cannot happen shall be removed rather than tested. Content (levels, bosses, drawings) needs no tests of its
  own: the tests cover the code loading and building it.
- **TEC-13** The app itself (screens, drawing, HUD) shall be tested too, without a display (an offscreen buffer),
  silent, without rendering songs.
- **TEC-14** The development tools (making the levels, tidying data) shall get no unit tests, but shall be linted and
  type-checked like the game.

## Crash reports

- **TEC-15** An uncaught error (game loop, event handler, background thread) shall print its full stack trace and write
  a fuller report (time, versions, platform, thread, every frame's local variables) to a crash log in the user's state
  folder (`~/.local/state/pewpy/` on Linux, `%LOCALAPPDATA%\pewpy\` on Windows); the game shall then exit with code 1.
  A native crash shall print every thread's Python stack.

## Caches and files

- **TEC-16** Rendered songs shall be kept in the user's cache folder (`~/.cache/pewpy/music`, `%LOCALAPPDATA%\pewpy\music`
  on Windows).

## Packaging

- **TEC-17** On Linux the game shall run from its source in a virtual environment. On Windows a launcher to
  double-click shall create a virtual environment the first time, install the libraries in it, then run the game from
  its source. There shall be no standalone build. The game can also be installed as a Python package carrying its
  data.

## Coding style

- **TEC-18** Every function shall have type hints, checked by a type checker, and a docstring; the code shall pass
  every lint rule but a listed few, with lines of at most 120 characters.
