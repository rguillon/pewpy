# CLAUDE.md

Instructions for Claude Code when working on **pewpy**, a shoot 'em up written in Python with Panda3D.

## Source of truth: the specs

The game design lives in `docs/specs/`. Read the relevant spec files **before** writing or changing code.

| File | Covers |
|------|--------|
| `docs/specs/00-vision.md` | Pitch, genre, camera, scope, references |
| `docs/specs/01-gameplay.md` | Controls, player ship, weapons, power-ups, scoring, difficulty |
| `docs/specs/02-enemies.md` | Enemy catalog, movement patterns, bosses |
| `docs/specs/03-levels.md` | Levels, waves, scrolling, backgrounds |
| `docs/specs/04-ui-audio.md` | Menus, HUD, game flow, sound, music |
| `docs/specs/05-visuals.md` | Art style, assets, effects |
| `docs/specs/06-technical.md` | Architecture, Panda3D usage, performance, testing, packaging |
| `docs/specs/roadmap.md` | Milestones — what to build, in which order |
| `docs/specs/decisions.md` | Decision log and open questions |

Rules:

- The specs win over anything said casually in chat. If chat and spec conflict, point it out and ask which one is right.
- `TBD` means **not decided yet**. Do not silently invent an answer. Either ask, or pick a sensible
  placeholder, implement it so it's easy to change (a constant or config value), and log it in
  `docs/specs/decisions.md` under "Open questions".
- Work milestone by milestone following `roadmap.md`. Tick checkboxes (`- [x]`) when an item is done and tested.
- Never edit spec content the user wrote, except to tick roadmap boxes and append to `decisions.md`.
  Suggest spec changes in chat instead.

## Project conventions

- Package layout: `src/pewpy/`, tests in `tests/`. Tooling: `uv`, `ruff`, `ty`, `pytest` (see `Makefile`).
- Install: `make install`. Checks: `make check`. Tests: `make test`.
- Run the game: `make run` (same as `uv run python -m pewpy`).
- Keep game logic (movement, collisions, scoring, waves) testable without opening a Panda3D window.
