# 06 — Technical

## Platform and versions

- Python: 3.10+ (from `pyproject.toml`)
- Panda3D version: TBD (1.10.x is currently installed)
- Extra libraries allowed (e.g. panda3d-gltf, numpy): `types-panda3d` (dev only, so `ty` can type-check
  Panda3D); `numpy` (building the voxel meshes, the AI's neural networks: no machine learning library, see `07-ai.md`);
  others: TBD

## Performance

- Target frame rate: TBD (e.g. 60 FPS)
- Max simultaneous bullets on screen: TBD
- Minimum hardware: TBD
- Under WSL, `make run` uses the GPU through Mesa's d3d12 driver (`GALLIUM_DRIVER=d3d12`) when `/dev/dxg` exists;
  the CPU renderer (llvmpipe) is much slower
- Window: 1280x1024 (the user's choice); resizable, the game keeps its 5:4 shape with black bars
  around it; fullscreen toggle: TBD

## Architecture preferences

> Leave `TBD` to let Claude propose something, or write your own preferences.

- Overall structure (states/scenes, entity classes, ECS…): grouped by domain, the game's rules kept apart from
  Panda3D *(placeholder)*. Hierarchical packages: where there are several implementations of one thing (motions,
  actions, exits, bullets, timings of a gun, models built in code, kinds of ground, props, shader painters, sound
  effects, background layers...), a package holds one module per implementation and its `__init__.py` gathers them
  (a registry, or the names it re-exports).
  - `pewpy/`: `app/` (the window, input, drawing: `PewPewApp` built in layers, one module each: `window.py`,
    `entity_models.py`, `hud.py`, `drawing.py` (and `bullets.py`), `screens.py`, `keys.py`, `sound.py`);
    `config.py` (the technical constants, and the game's rules read from `rules.json`); `data.py`.
  - `game/` (the rules, no Panda3D): entities, controls, events, player, world, states, levels; `weapons/`
    (`guns/`: the guns everyone fires (`gun.py`, `state.py`, `patterns.py`, `styles.py`, `launch.py`, `laser.py`,
    `chain.py`, `timing/`: one module per way of timing shots); `bullets/`: one module per kind of shot; `player/`:
    the arsenal and the secondary weapon); `enemies/` (the one Enemy class for enemies and bosses, its descriptions
    `spec.py`, `motions/`, `actions/` and `exits/` (one class per module, each acting on the enemy's `Body`,
    `body.py`, never on `Enemy` itself), the kinds and the roster).
  - `scenery/`: `params/` (the scenery's parameters), `background/` (stars, drifting layers in `layers/`, `view.py`
    drawing them), `ground/` (terrain, relief, the bases of `landscapes.py` and `settlement.py`, `kinds/` of ground,
    `props/`, and `shader/` with its GLSL in `glsl/`, one painter per kind of ground).
  - `graphics/`: `models/` (`mesh/`, `drawings/` (flat, layered, MagicaVoxel), `built/` and `background/` models
    built in code, flames), lighting, sprites, `effects/` (one module per effect, `system.py`, `view.py`).
  - `ui/` (menus, the ship select, the level preview), `audio/` (`midi/`, `synth/`, `sfx/`: one module per sound).
  The data, apart from the code, in `data/` at the top of the project: `rules.json`, `ships.json`, `weapons/`, `enemies/`, `bosses/`, `levels/`, `models/`, `music/` and `fonts/` (an installed wheel carries it inside the package, a packaged build next to the executable; see `pewpy/data.py`). The dev tools apart, in `pewpewdev/`, not in the game nor its
  package: `ai/` (the AI player, no Panda3D, see `07-ai.md`), `tools/` (one package per tool, each run with
  `python -m`: `levels/` (`worlds/`: one module per world), `final_bosses/`, `models/` (`recipes/`: one module per
  model), `candidates/` and `boss_candidates/` (one module per family, core, attachment, appendage, wing plan, kind
  of part), `songs/` (`tracks/`: one module per part); `voxels.py`), `app/` (the game with the dev screens,
  `make dev`: `model_screens.py`, `ai_screens.py`), with their own `states.py`, `candidates.py` and `ui/`
- Enemies as data *(the user's choice)*: every enemy, boss, boss part and projectile is one class, `Enemy`, running
  its description: a body (size, health, points, drops, entry, ground...), parts (a boss's), what it releases when
  shot down, and states. Each state has motions (`game/enemies/motions/`), guns (`game/weapons/guns/`),
  a look, whether it can be hurt, and exits to other states (`game/enemies/exits/`: a timer, a height, lined up with the player, a cycle of
  its age, visits, parts destroyed, health lost, volleys fired...), each doing actions on the way (`game/enemies/actions/`: set a speed, aim,
  relocate, fire, die). The enemies are in `data/enemies/*.json`, the bosses in `data/bosses/*.json`, written the same way
  (`game/enemies/spec.py` reads them): a boss is only an enemy with parts, `"boss": true`, a state coming down and
  a state per phase (each starting with a `warmup`); only its configuration differs. The final bosses are made by a
  dev tool from short plans (`make final-bosses`, `pewpewdev/tools/final_bosses/`). A new
  behaviour is a new motion, exit condition, action (a subclass of `Motion`, `Condition` or `Action`, with only the
  fields it uses, registered by its name in its package) or gun option in code, tested; the descriptions are data and need no
  tests of their own.
- Weapons as data *(the user's choice)*: the player's weapons and the enemies' are the same guns
  (`game/weapons/guns/`): a pattern (aimed, fan, ring, beams, the player's laser "ray", the lightning "chain"),
  timing (interval or rate, volleys, charging, reloading), and what they fire (bullets of a style and size, missiles,
  enemies). The player's are in `data/weapons/` (`player.json`: one gun per level of each weapon;
  `secondary.json`), the enemies' in their own descriptions. Only how they look is in code (`app/`, `graphics/`).
- Game loop timing (variable dt / fixed timestep): TBD
- Collision detection (Panda3D CollisionTraverser / custom simple circles-boxes): TBD
- Configuration (constants in code / TOML file for tunable values): TBD
- Use Panda3D's `DirectGUI` for menus, or custom: TBD

## Testing

- What must be unit tested: the game logic (movement, collisions, scoring, wave spawning), kept separate from
  rendering: `app/` only handles window, input and drawing, so the logic is tested without opening a window.
  Only the game (`src/pewpy`) has unit tests: the dev tools (`src/pewpewdev`: the AI, the content tools, the dev
  screens) have none, only the linters and the type checker.
- Coverage: every line and branch of the game (`src/pewpy`) is tested, 100% *(the user's choice)*; `make test`
  fails below it. Code that can't happen is removed rather than tested. Content (levels, bosses, model drawings) is
  data in JSON files loaded by the game, not declarations in Python, so it needs no tests of its own *(the user's
  choice)*: the tests cover the code loading and building it.
- The app itself (screens, drawing, HUD) is tested too, without a display: one app for the whole test session,
  drawing into an offscreen buffer through EGL (`load-display p3headlessgl`), silent, its songs not rendered
  (`tests/conftest.py`). CI installs the EGL and Mesa libraries for it.

## Crash reports

- An uncaught exception (game loop, event handler, background thread) prints its full stack trace on stderr and
  writes a fuller report (time, versions, platform, thread, every frame's local variables) to `crash.log`
  (`~/.local/state/pewpy/` on Linux, `%LOCALAPPDATA%\pewpy\` on Windows); the game then exits with code 1.
  A native crash prints every thread's Python stack (faulthandler). See `pewpy.crash`.

## Packaging and distribution

- How players run it (`uv run`, pip install, standalone build with Panda3D's `build_apps`): a standalone build with
  Panda3D's `build_apps`: `make package` makes `dist/pewpy-<version>_win_amd64.zip`, holding `pewpy.exe` with the
  data files next to it; developers still use `uv run` (`make run`)
- Target OSes for builds: Windows (64-bit) for now; the same setup can also build Linux and macOS

## Coding style

- Type hints everywhere? TBD
- Docstring style: TBD
- Anything else: TBD
