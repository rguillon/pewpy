"""Bosses of the tests' own (the `test_bosses` fixture), so the tests of how bosses work don't follow the game's.

The game's bosses are data the Dev menu remakes (their parts, sizes and guns change); these stay as the tests need
them. Built in code (no model): their guns fire from where their descriptions say, not from a model's weapons.
"""

from typing import Any

import pytest

from pewpy.game.enemies.kinds import BOSSES, KINDS
from pewpy.game.enemies.spec import EnemySpec, parse_enemy

# Two cannons, the core armored until both are gone; then rings of 14.
HARVESTER: dict[str, Any] = {
    "name": "TEST HARVESTER",
    "boss": True,
    "size": [0.34, 0.26],
    "health": 100.0,
    "points": 6000,
    "parts": [
        {"name": "left cannon", "x": -0.26, "y": 0.02, "size": [0.14, 0.18], "health": 40.0, "points": 800},
        {"name": "right cannon", "x": 0.26, "y": 0.02, "size": [0.14, 0.18], "health": 40.0, "points": 800},
    ],
    "phases": [
        {
            "sway": 0.12,
            "armored": True,
            "until": {"parts": ["left cannon", "right cannon"]},
            "guns": [
                {"from": "left cannon", "pattern": "aimed", "interval": 1.8, "speed": 0.65, "volley": 3},
                {"from": "right cannon", "pattern": "aimed", "interval": 1.8, "speed": 0.65, "volley": 3, "delay": 0.9},
                {
                    "pattern": "fan",
                    "interval": 2.5,
                    "speed": 0.4,
                    "count": 3,
                    "spread": 25,
                    "delay": 1.2,
                    "style": "heavy",
                },
            ],
        },
        {
            "sway": 0.18,
            "guns": [
                {"pattern": "ring", "interval": 2.2, "speed": 0.4, "count": 14, "turn": 13},
                {"pattern": "aimed", "interval": 1.4, "speed": 0.6, "count": 3, "spread": 12, "delay": 0.7},
            ],
        },
    ],
}
# A cutter in front, over the core, between two augers.
REAPER: dict[str, Any] = {
    "name": "TEST REAPER",
    "boss": True,
    "size": [0.407, 0.327],
    "health": 120.0,
    "points": 7500,
    "parts": [
        {"name": "left auger", "x": -0.067, "y": -0.033, "size": [0.047, 0.093], "health": 20.0, "points": 400},
        {"name": "right auger", "x": 0.067, "y": -0.033, "size": [0.047, 0.093], "health": 20.0, "points": 400},
        {"name": "cutter", "x": 0.0, "y": -0.027, "size": [0.113, 0.147], "health": 30.0, "points": 600},
    ],
    "phases": [
        {
            "sway": 0.08,
            "armored": True,
            "until": {"parts": ["left auger", "right auger", "cutter"]},
            "guns": [{"from": "cutter", "pattern": "fan", "interval": 2.0, "speed": 0.45, "count": 5, "delay": 0.4}],
        },
        {"sway": 0.15, "guns": [{"pattern": "ring", "interval": 0.15, "speed": 0.44, "count": 3, "turn": 13}]},
    ],
}
# Four turrets far out on its sides: the outer pair, then the inner pair, then the core.
COLOSSUS: dict[str, Any] = {
    "name": "TEST COLOSSUS",
    "boss": True,
    "size": [0.34, 0.3],
    "health": 150.0,
    "points": 8000,
    "parts": [
        {"name": "left outer", "x": -0.3, "y": -0.02, "size": [0.12, 0.12], "health": 30.0, "points": 600},
        {"name": "right outer", "x": 0.3, "y": -0.02, "size": [0.12, 0.12], "health": 30.0, "points": 600},
        {"name": "left inner", "x": -0.1, "y": -0.2, "size": [0.12, 0.12], "health": 30.0, "points": 600},
        {"name": "right inner", "x": 0.1, "y": -0.2, "size": [0.12, 0.12], "health": 30.0, "points": 600},
    ],
    "phases": [
        {
            "sway": 0.08,
            "armored": True,
            "until": {"parts": ["left outer", "right outer"]},
            "guns": [
                {"from": "left outer", "pattern": "aimed", "interval": 2.0, "speed": 0.7, "volley": 3},
                {"from": "right outer", "pattern": "aimed", "interval": 2.0, "speed": 0.7, "volley": 3, "delay": 1.0},
                {"from": "left inner", "pattern": "fan", "interval": 1.6, "speed": 0.5, "count": 3, "delay": 0.5},
                {"from": "right inner", "pattern": "fan", "interval": 1.6, "speed": 0.5, "count": 3, "delay": 1.3},
            ],
        },
        {
            "sway": 0.12,
            "armored": True,
            "until": {"parts": ["left inner", "right inner"]},
            "guns": [{"pattern": "fan", "interval": 2.6, "speed": 0.4, "count": 5, "spread": 20, "style": "heavy"}],
        },
        {"sway": 0.15, "guns": [{"pattern": "ring", "interval": 0.16, "speed": 0.42, "count": 4, "turn": 10}]},
    ],
}
TEST_BOSSES: dict[str, EnemySpec] = {
    kind: parse_enemy(kind, body, kind)
    for kind, body in {"test_harvester": HARVESTER, "test_reaper": REAPER, "test_colossus": COLOSSUS}.items()
}


@pytest.fixture
def test_bosses(monkeypatch: pytest.MonkeyPatch) -> dict[str, EnemySpec]:
    """Make the tests' bosses kinds of enemy for a test, so levels can send them and make_enemy can make them."""
    for kind, spec in TEST_BOSSES.items():
        monkeypatch.setitem(KINDS, kind, spec)
        monkeypatch.setitem(BOSSES, kind, spec)
    return TEST_BOSSES
