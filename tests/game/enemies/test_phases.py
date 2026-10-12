from pewpy.game.enemies.phases import ARMORED, BOSS, ENEMY, HOLD_Y, PHASE_PAUSE, expand_phases, preset

TWO_PHASES = {
    "name": "BOSS",
    "phases": [
        {"sway": 0.1, "armored": True, "until": {"parts": ["arm"]}, "guns": [{"pattern": "aimed"}]},
        {"sway": 0.2, "guns": [{"pattern": "ring"}]},
    ],
}


def test_a_boss_has_the_usual_fields_of_a_boss_and_anything_else_those_of_an_enemy() -> None:
    assert preset({"boss": True}) is BOSS
    assert preset({}) is ENEMY
    assert preset({"boss": False}) is ENEMY


def test_parts_are_carried_by_their_enemy() -> None:
    assert ENEMY.part == {"placeable": False, "leaves_screen": False}
    assert BOSS.part.items() >= ENEMY.part.items()
    assert not BOSS.body["leaves_screen"]


def test_phases_become_coming_down_then_a_state_per_phase() -> None:
    expanded = expand_phases(TWO_PHASES)
    assert "phases" not in expanded
    assert expanded["name"] == "BOSS"
    assert [state["name"] for state in expanded["states"]] == ["enter", "phase 1", "phase 2"]


def test_it_comes_down_armored_like_its_first_phase_and_starts_swaying_when_it_holds() -> None:
    enter = expand_phases(TWO_PHASES)["states"][0]
    assert enter.items() >= ARMORED.items()
    assert enter["coming_in"]
    (arrive,) = enter["exits"]
    assert (arrive["to"], arrive["below_y"]) == ("phase 1", HOLD_Y)
    assert arrive["then"] == [{"type": "velocity", "vy": 0.0}, {"type": "sway", "speed": 0.1}]


def test_each_phase_bounces_pauses_fires_and_ends_into_the_next_swaying_its_way() -> None:
    _, first, last = expand_phases(TWO_PHASES)["states"]
    assert first.items() >= ARMORED.items()
    assert first["motions"] == [{"type": "bounce", "clamp": True}]
    assert first["warmup"] == PHASE_PAUSE
    assert first["guns"] == [{"pattern": "aimed"}]
    assert first["exits"] == [
        {"to": "phase 2", "parts": ["arm"], "go_on": True, "then": [{"type": "sway", "speed": 0.2}]},
    ]
    assert "look" not in last
    assert last["exits"] == []


def test_where_it_holds_and_how_long_it_pauses_can_be_told() -> None:
    expanded = expand_phases(TWO_PHASES | {"hold_y": 0.3, "phase_pause": 0.5})
    assert "hold_y" not in expanded
    assert expanded["states"][0]["exits"][0]["below_y"] == 0.3
    assert expanded["states"][1]["warmup"] == 0.5
