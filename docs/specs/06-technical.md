# 06 — Technical

## Platform and versions

- Python: 3.10+ (from `pyproject.toml`)
- Panda3D version: TBD (1.10.x is currently installed)
- Extra libraries allowed (e.g. panda3d-gltf, numpy): `types-panda3d` (dev only, so `ty` can type-check
  Panda3D); `numpy` (building the voxel meshes, see decisions.md); others: TBD

## Performance

- Target frame rate: TBD (e.g. 60 FPS)
- Max simultaneous bullets on screen: TBD
- Minimum hardware: TBD
- Window: 1280x1024 (the user's choice, see decisions.md); resizable, the game keeps its 5:4 shape with black bars
  around it; fullscreen toggle: TBD

## Architecture preferences

> Leave `TBD` to let Claude propose something, or write your own preferences.

- Overall structure (states/scenes, entity classes, ECS…): TBD
- Game loop timing (variable dt / fixed timestep): TBD
- Collision detection (Panda3D CollisionTraverser / custom simple circles-boxes): TBD
- Configuration (constants in code / TOML file for tunable values): TBD
- Use Panda3D's `DirectGUI` for menus, or custom: TBD

## Testing

- What must be unit tested: the game logic (movement, collisions, scoring, wave spawning), kept separate from
  rendering: `app.py` only handles window, input and drawing, so the logic is tested without opening a window
- Headless tests (Panda3D `window-type none`) acceptable? TBD

## Packaging and distribution

- How players run it (`uv run`, pip install, standalone build with Panda3D's `build_apps`): a standalone build with
  Panda3D's `build_apps`: `make package` makes `dist/pewpy-<version>_win_amd64.zip`, holding `pewpy.exe` with the
  data files next to it (see decisions.md); developers still use `uv run` (`make run`)
- Target OSes for builds: Windows (64-bit) for now; the same setup can also build Linux and macOS

## Coding style

- Type hints everywhere? TBD
- Docstring style: TBD
- Anything else: TBD
