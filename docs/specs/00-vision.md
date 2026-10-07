# 00 — Vision

## How to read these specs

- Every requirement is a numbered line using "shall". A requirement says what the game does, never how it is coded.
- Values marked *(placeholder)* are working values, not final decisions.
- Units, used in every spec file unless stated otherwise:
    - **World units** (wu): the play area is 2.5 wu wide and 2.0 wu tall, centred on (0, 0); x grows to the
      right, y grows up the screen. The top edge of the play area is y = 1, the bottom edge y = −1, the sides
      x = ±1.25.
    - Speeds in wu per second, times in seconds (s), angles in degrees (°).
    - Angles of shots are measured from "straight ahead": straight down the screen for enemies, straight up for
      the player. A positive angle leans towards the right of the screen (+x), a negative one towards the left,
      unless stated otherwise.
    - Health in damage points: the player's first weapon does 1 damage per bullet.
    - Sizes are hitboxes, "width × height" in wu; every hitbox is an axis-aligned rectangle.
- **W** is the width factor, 5/3 (the play area's width, 2.5, over 1.5). Values marked "(×W)" are multiplied by W
  in the game; values marked "(÷W)" are divided by W.

## Pitch

- **VIS-0** pewpy shall be a vertical shoot 'em up in voxel 3D: pick one of three ships, fly through 8 worlds of 6
  levels over real-looking grounds, shoot down waves of industrial sci-fi enemies with three upgradable weapons and a
  secondary weapon, and beat a mini boss and a final boss in every level.

## Genre and perspective

- **VIS-1** The game shall be a single-player vertical-scrolling shoot 'em up.
- **VIS-2** The game rules shall be two-dimensional: every object moves and collides on the flat play area.
- **VIS-3** The game shall draw everything in 3D: ships, enemies, bosses, pickups and the ground are 3D models
  made of voxels (cubes), seen from above by a perspective camera.
- **VIS-4** The camera shall be fixed, in front of and below the play area, tilted 25° so that the top of the
  screen is farther away than the bottom, with a 40° vertical field of view *(placeholder)*.
- **VIS-5** The camera shall be placed just far enough away that the whole play area, plus a 4% margin, is
  visible. Because of the tilt, the screen shows more than the play area above it (up to about y = 1.65) and on
  its sides (up to about x = ±1.86 at the top).
- **VIS-6** The game area shall have a 5:4 shape (width:height), the same as the play area.

## Tone and theme

- **VIS-7** The game shall have an old-school industrial sci-fi look: grey metal ships with colored markings, cockpit
  instrument panels for the HUD and menus, a synthwave soundtrack.

## Scope

- **VIS-8** Version 1.0 shall have 48 levels in 8 worlds of 6 levels each (see `03-levels.md`).
- **VIS-9** The game shall be single player.
- **VIS-10** The game shall run on Linux and Windows (64-bit), from its source with Python and its libraries; macOS
  is not supported.
- **VIS-11** The game shall contain an AI player that learns to play it and can be watched playing
  (see `07-ai.md`).
- **VIS-12** The game shall contain a Dev menu to make new models, songs and backgrounds, and to take
  screenshots (see `04-ui-audio.md`).
- **VIS-13** A level shall last about two minutes of waves (two halves of 46 s plus the boss delays), plus its two boss
  fights; a full run is the 48 levels in a row.

## Out of scope

- **VIS-14** The game shall have no special weapon or bomb, no combos or score multipliers, no extra lives from
  score, no high score table, no options menu, no gamepad support and no key rebinding.
