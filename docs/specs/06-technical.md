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
  Panda3D *(placeholder)*: `pewpy/` (`app.py`: the window, input, drawing; `config.py`, `data.py`), `game/` (the
  rules, no Panda3D: entities, player, weapons, world, states, levels, enemies, bosses), `scenery/` (backgrounds
  and grounds), `graphics/` (models, lighting, effects), `ui/` (menus, the ship select, the level preview),
  `audio/`; data in `levels/` and `models/`. The dev tools apart, in `pewpewdev/`, not in the game nor its
  package: `ai/` (the AI player, no Panda3D, see `07-ai.md`), `tools/` (making the levels, models, candidates and
  songs), `app.py` (the game with the dev screens, `make dev`: the model screens, AI learning and rating), with
  their own `states.py`, `candidates.py` and `ui/`
- Game loop timing (variable dt / fixed timestep): TBD
- Collision detection (Panda3D CollisionTraverser / custom simple circles-boxes): TBD
- Configuration (constants in code / TOML file for tunable values): TBD
- Use Panda3D's `DirectGUI` for menus, or custom: TBD

## Testing

- What must be unit tested: the game logic (movement, collisions, scoring, wave spawning), kept separate from
  rendering: `app.py` only handles window, input and drawing, so the logic is tested without opening a window.
  Only the game (`src/pewpy`) has unit tests: the dev tools (`src/pewpewdev`: the AI, the content tools, the dev
  screens) have none, only the linters and the type checker.
- Coverage: every line and branch of the game (`src/pewpy`) is tested, 100% *(the user's choice)*; `make test`
  fails below it. Code that can't happen is removed rather than tested.
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
