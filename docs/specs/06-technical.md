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
- The 3D view is drawn into an offscreen buffer at most 1440 pixels tall *(placeholder,
  `config.SCENE_MAX_HEIGHT`)*, then stretched over the game area; the HUD and menus are drawn at the window's
  own resolution, so text stays sharp. On a big screen (4K) this keeps the per-pixel ground shader within reach
  of a small GPU. Open: a graphics option in the menus to pick it?

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
    `props/` (the one `PropModel` building every prop from its JSON in `data/models/props/`), and `shader/` with its GLSL in `glsl/`, one painter per kind of ground).
  - `graphics/`: `models/` (`mesh/`, `drawings/` (flat, layered, MagicaVoxel), `built/` and `background/` models
    built in code, flames), lighting, sprites, `effects/` (one module per effect, `system.py`, `view.py`).
  - `ui/` (menus, the ship select, the level preview), `audio/` (`midi/`, `synth/`, `sfx/`: one module per sound).
  The data, apart from the code, in `data/` at the top of the project: `rules.json`, `ships.json`, `weapons/`, `enemies/`, `bosses/`, `levels/`, `models/` (by group, the props and the candidates: see `05-visuals.md`), `music/` and `fonts/` (an installed wheel carries it inside the package, a packaged build next to the executable; see `pewpy/data.py`). The dev tools live in the game's package, never imported by the game, in
  `pewpy/tools/` *(the user's choice)*, one package per tool run with `python -m`, each with its own make target:
  `levels/` (`make levels`; `worlds/`: one module per world), `models/` (`make models`; `recipes/`: one module per
  model), `songs/` (`make songs`; `tracks/`: one module per part), `voxels.py` (`make voxels`), `dev/` (the game with
  the dev screens, `make dev`: `app/` with `model_screens.py` and `ai_screens.py`, its own `states.py`,
  `candidates.py` and `ui/`), `paths.py` (where the tools write), `generate_props.py` (prop candidates,
  `make props`), `player_candidates/` (player ship candidates, `make players`, from the same kit as the enemies'),
  `candidates/` (enemy candidates, `make candidates`: assembled from a kit of hardcoded parts, `kit/`,
  one module per family of parts, the kinds of ship in `archetypes.py`), `boss_candidates/` (`make boss-candidates`:
  sculpted from plans, one module per family, appendage, kind of part), `final_bosses/` (`make final-bosses`: the
  final bosses' behaviour from plans), `ai/` (the AI player, no Panda3D, see `07-ai.md`; `make learn`, `make rate`), `screenshots/` (`make screenshots`: one screenshot of every world for the README, offscreen) and `compact_json.py`. What the candidates share is in `common/`: the batch
  command line (`--seed`, `--out`, `--append`), the 3D drawing and its numbered weapons, the colors, keeping the
  most different
- Enemies as data *(the user's choice)*: every enemy, boss, boss part and projectile is one class, `Enemy`, running
  its description: a body (size, health, points, drops, entry, ground...), parts (a boss's), what it releases when
  shot down, and states. Each state has motions (`game/enemies/motions/`), guns (`game/weapons/guns/`),
  a look, whether it can be hurt, and exits to other states (`game/enemies/exits/`: a timer, a height, lined up with the player, a cycle of
  its age, visits, parts destroyed, health lost, volleys fired...), each doing actions on the way (`game/enemies/actions/`: set a speed, aim,
  relocate, fire, die). The enemies are in `data/enemies/*.json`, the bosses in `data/bosses/*.json`
  (`game/enemies/spec.py` reads them): a boss is only an enemy with parts, `"boss": true`, a state coming down and
  a state per phase (each starting with a `warmup`). Every boss comes down and fights the same way, so a boss is
  written shortly (`game/enemies/boss.py` makes it into states): its body, its parts and its `phases`, each a
  `sway` speed, `armored` or not, its guns and `until` (the exit conditions ending it: parts destroyed, health
  below a share); the bosses' usual fields (not rammable, a pickup, 30% for the parts, guns carrying their reload
  and firing off screen, the explosions...) are filled in unless given. A boss gun `from` a list of parts is fired
  by each of them in turn, their first shots spread over its interval. A gun fires from the numbered weapons drawn on
  the model of what fires it (`weapon`/`weapons`, checked when the enemies are read; see `02-enemies.md`, "Enemy
  weapons", and `game/enemies/mounts.py`, which reads them from the model file: the game logic never loads the
  models themselves). The final bosses are made by a
  dev tool from short plans (`make final-bosses`, `pewpy/tools/final_bosses/`). The enemies' and bosses' JSON
  is written compactly, each list or object on one line when it fits in 130 columns
  (`python -m pewpy.tools.compact_json <files>`; the pre-commit JSON formatter leaves these folders alone). A new
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
  Only the game (`src/pewpy`) has unit tests: the dev tools (`src/pewpy/tools`: the AI, the content
  tools, the dev screens) have none, only the linters and the type checker.
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
