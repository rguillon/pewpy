# pewpy

[![Build status](https://img.shields.io/github/actions/workflow/status/rguillon/pewpy/main.yml?branch=main)](https://github.com/rguillon/pewpy/actions/workflows/main.yml?query=branch%3Amain)
[![codecov](https://codecov.io/gh/rguillon/pewpy/branch/main/graph/badge.svg)](https://codecov.io/gh/rguillon/pewpy)
[![Commit activity](https://img.shields.io/github/commit-activity/m/rguillon/pewpy)](https://img.shields.io/github/commit-activity/m/rguillon/pewpy)
[![License](https://img.shields.io/github/license/rguillon/pewpy)](https://img.shields.io/github/license/rguillon/pewpy)

A vertical-scrolling shoot 'em up written in Python with [Panda3D](https://www.panda3d.org/).

This project is just me trying vibe coding, do not expect quality.

Nothing is done manually (so far), the levels, ships and even the music are all generated with Claude Code.

You fly a ship over scrolling landscapes and shoot down waves of enemy aircraft, ground turrets and bosses. The
ships and enemies are voxel models built in code, and the ground is painted live by shaders; a tilted 3D camera
gives the flat, arcade-style gameplay some depth.

- **8 worlds of 6 levels each**, from the Highlands to the Metropolis, every level a little harder than the last.
  Each level has a mini boss halfway and a bigger final boss at the end.
- **3 ships** to choose from: the balanced Vanguard, the armored Juggernaut and the fast, self-repairing Phantom.
- **3 weapons**, switched at any time: spreading bullets, a continuous laser and homing missiles, each upgraded
  up to level 5 by the capsules enemies drop. Some drops also add a secondary weapon (a turret or a lightning gun)
  that fires on its own.
- Synthwave music, generated, and an AI player that learns to play the levels to rate their difficulty.

## Screenshots

|                                                                 |                                                                 |
| :-------------------------------------------------------------: | :-------------------------------------------------------------: |
|   ![Highlands](docs/screenshots/world_1.png) **1. Highlands**   |    ![Wildwood](docs/screenshots/world_2.png) **2. Wildwood**    |
|    ![Lush Veld](docs/screenshots/world_3.png) **3. Lush Veld**    |   ![Heartland](docs/screenshots/world_4.png) **4. Heartland**   |
| ![Rust Pan](docs/screenshots/world_5.png) **5. Rust Pan** | ![Bright Ridges](docs/screenshots/world_6.png) **6. Bright Ridges** |
|   ![Ironworks](docs/screenshots/world_7.png) **7. Ironworks**   |  ![Metropolis](docs/screenshots/world_8.png) **8. Metropolis**  |

## Playing

You need [uv](https://docs.astral.sh/uv/) and Python 3.12 or newer.

```bash
make install   # set up the environment
make run       # play
```

| Action        | Key                                                 |
| ------------- | --------------------------------------------------- |
| Move          | arrows                                              |
| Fire          | space (hold it to keep firing)                      |
| Switch weapon | shift (bullets → laser → missiles)                  |
| Pause         | escape                                              |
| Menus         | up/down to move, enter to choose, escape to go back |

## Developing

The game design lives in [`docs/specs/`](docs/specs/), and the milestones in
[`docs/specs/roadmap.md`](docs/specs/roadmap.md).

- `make check`: lint and type-check; `make test`: run the tests.
- `make dev`: the game with the dev screens (models, bosses, AI learning and rating).
- `make screenshots`: retake the screenshots above.
- `make help`: every other tool (levels, models, songs, the AI...).

- **Github repository**: <https://github.com/rguillon/pewpy/>

---

Repository initiated with [osprey-oss/cookiecutter-uv](https://github.com/osprey-oss/cookiecutter-uv).
