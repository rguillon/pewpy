# CLAUDE.md

Instructions for Claude Code when working on **pewpy**, a shoot 'em up written in Python with Panda3D.

## Source of truth: the specs

The game design lives in `docs/specs/`. Read the relevant spec files **before** writing or changing code.

| File | Covers |
|------|--------|
| `docs/specs/00-vision.md` | Pitch, genre, camera, scope, references |
| `docs/specs/01-gameplay.md` | Controls, player ship, weapons, power-ups, scoring, difficulty |
| `docs/specs/02-enemies.md` | Enemy general rules, enemy weapons, index of the files below |
| `docs/specs/02-enemies-catalog.md` | The first enemies (Drone … Buckshot) |
| `docs/specs/02-enemies-fleet.md` | The second fleet (Albatross … Pincer) |
| `docs/specs/02-enemies-bosses.md` | Boss rules, then every boss (one per level) |
| `docs/specs/03-levels.md` | Levels, waves, scrolling, backgrounds |
| `docs/specs/04-ui-audio.md` | Menus, HUD, game flow, sound, music |
| `docs/specs/05-visuals.md` | Art style, assets, effects |
| `docs/specs/06-technical.md` | Architecture, Panda3D usage, performance, testing, packaging |
| `docs/specs/07-ai.md` | The AI player: learning to play, rating the levels |
| `docs/specs/roadmap.md` | Milestones — what to build, in which order |

Rules:

- The specs win over anything said casually in chat. If chat and spec conflict, point it out and ask which one is right.
- `TBD` means **not decided yet**. Do not silently invent an answer. Either ask, or pick a sensible
  placeholder, implement it so it's easy to change (a constant or config value), and write it into the spec
  where it belongs, marked *(placeholder)*; add a short "open: …" note there if a question remains.
- Work milestone by milestone following `roadmap.md`. Tick checkboxes (`- [x]`) when an item is done and tested.
- Keep the specs up to date: whenever the user decides something in chat or a change alters how the game
  works, update the relevant spec file directly. There is no separate decision log. Don't change what the
  user decided without asking; if chat and spec conflict, ask first (see above).
- Specs describe the game, not its history: no bug-fix stories, performance measurements or "it used to be".
- Read only the spec files a task needs. In a long one (the bosses file), grep for the `### ` heading you
  need and read that section.

## Project conventions

- Package layout: the game in `src/pewpy/`, its data files (JSON, drawings, props, music) in `data/`; the dev tools in `src/pewpewdev/` (the AI, the tools making levels,
  models and songs, the dev screens), never imported by the game, except `src/pewpy/tools/` (the generators of props, enemy, player and boss candidates, final bosses), also
  never imported by the game and left out of the coverage; tests in `tests/`, for the game only: the dev
  tools get no unit tests (they are still linted and type-checked). Tooling: `uv`, `ruff`, `ty`, `pytest` (see `Makefile`).
- Install: `make install`. Checks: `make check`. Tests: `make test`.
- Run the game: `make run` (same as `uv run python -m pewpy`); with the dev screens: `make dev`.
- Keep game logic (movement, collisions, scoring, waves) testable without opening a Panda3D window.
