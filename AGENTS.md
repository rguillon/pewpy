# AGENTS.md

Vertical-scrolling shoot 'em up, Python 3.12+/Panda3D. Layout: game in `src/pewpy/`, **game content in `data/` (300+ JSON/NPZ files)**, tests in `tests/` mirroring `src/pewpy/`, specs in `docs/specs/`.

## Source of truth: specs, not this file

`docs/specs/` defines the game. Read relevant specs before writing code; specs describe behavior, not history. If chat and spec conflict, ask.

| Spec | Covers |
| --- | --- |
| `docs/specs/00-vision.md` | Vision, pillars, scope |
| `docs/specs/01-gameplay.md` | Player, weapons, powerups, scoring, loop |
| `docs/specs/02-enemies.md` | Enemy design overview |
| `docs/specs/02-enemies-catalog.md` | Enemy roster/catalog |
| `docs/specs/02-enemies-fleet.md` | The second fleet |
| `docs/specs/02-enemies-bosses.md` | Bosses |
| `docs/specs/03-levels.md` | Level structure, waves, difficulty curve |
| `docs/specs/04-ui-audio.md` | Screens, HUD, game flow, audio |
| `docs/specs/05-visuals.md` | Art direction, effects |
| `docs/specs/06-technical.md` | Architecture, data format, tooling |
| `docs/specs/07-ai.md` | AI player (learning, winrate, mutate) |
| `docs/specs/roadmap.md` | Roadmap and planned work |

## Architecture constraints
- Game logic must run **headless** (no window, no 3D models) for testability.
- Content is data-loaded with validation; same gun description used for weapons/enemies.
- App (screens, HUD) tested offscreen with one Panda3D `ShowBase` instance.

## Commands
```bash
make install   # uv sync + pre-commit install
make check     # uv lock -> pre-commit -> ty -> deptry (run before finishing)
make test      # pytest with 100% line/branch coverage
make run       # game (sets GALLIUM_DRIVER=d3d12 under WSL if /dev/dxg exists)
```

Generation/AI:
`make levels`, `make learn`, `make learn-level1`, `make winrate`, `make mutate`, `make docs-test`.

## Focused test runs
```bash
uv run python -m pytest tests/test_app.py                    # one module
uv run python -m pytest tests/game/test_world.py::TestX::test_y
uv run python -m pytest tests --no-cov                        # skip coverage gate
```

## Gotchas
- **Coverage gate**: 100% lines/branches in `src/pewpy` (`fail_under = 100`, `branch = true`).
- **Tests**: Use `app`/`data_copy` fixtures; never create a second Panda3D `ShowBase` instance.
- **`make check`**: Mutates files (runs `ruff fix`).
- **Ruff**: `select = ['ALL']`, 120-char lines, `print()` allowed only in `generators/`.
- **`ty`**: Type checker (not mypy), runs against `./.venv` at Python 3.12.
- **`data/`**: Generated but committed. Don't hand-format JSON; use `python -m pewpy.generators.compact_json`.
- **Model paths**: Resolved at runtime via `src/pewpy/data.py`, never hardcoded.
- **`mutants/`**: Gitignored scratch dir for `make mutate`; don't edit manually.
- **New features**: Add to README's feature list (repo convention).
- **No standalone build**: Linux runs from source; Windows uses `pewpy.bat` to create venv.
