"""The waves of a half level."""

import random

import pytest

from pewpy.game.enemies.roster import ENEMY_TYPES
from pewpy.generators.levels import waves
from pewpy.generators.levels.difficulty import GROWTH, budget
from pewpy.generators.levels.enemies import SHAPES, UNLOCK, WARM_UP
from pewpy.generators.levels.waves import HALF_TIME, LINE_SPAN, SIDE_SPAN, make_half, make_wave, threat


def test_every_enemy_sent_has_shapes_and_an_unlock() -> None:
    assert set(SHAPES) == set(UNLOCK)
    assert set(UNLOCK) <= set(ENEMY_TYPES)
    assert all(UNLOCK[enemy] == 1 for enemy in WARM_UP)


def test_a_group_grows_with_the_difficulty(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setitem(SHAPES, "drone", ({"formation": "column", "x": 0.5, "count": 2.0},))
    rng = random.Random(1)
    assert make_wave(rng, "drone", 1) == {"enemy": "drone", "count": 2, "formation": "column", "x": 0.5}
    assert make_wave(rng, "drone", 11)["count"] == round(2.0 * GROWTH**10)


def test_a_single_enemy_has_no_count_unless_it_has_a_formation(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setitem(SHAPES, "condor", ({"x": 0.0, "count": 0.35},))
    assert make_wave(random.Random(1), "condor", 1) == {"enemy": "condor", "x": 0.0}


@pytest.mark.parametrize(
    ("shape", "span"), [({"spacing": 0.5}, LINE_SPAN), ({"spacing": 0.25, "side": "left"}, SIDE_SPAN)]
)
def test_a_line_is_cut_down_to_fit_the_screen(monkeypatch: pytest.MonkeyPatch, shape: dict, span: float) -> None:
    monkeypatch.setitem(SHAPES, "drone", ({"formation": "line", "count": 40.0, **shape},))
    wave = make_wave(random.Random(1), "drone", 1)
    assert wave["count"] == int(span / shape["spacing"]) + 1


def test_a_waves_threat_is_its_enemies_points() -> None:
    assert threat({"enemy": "drone", "count": 4}) == 4 * ENEMY_TYPES["drone"].points
    assert threat({"enemy": "gunship"}) == ENEMY_TYPES["gunship"].points


@pytest.mark.parametrize(("d", "harder"), [(1, 0), (7, 2), (20, 2)])
def test_a_half_warms_up_then_reaches_its_threat_over_46_seconds(d: int, harder: int) -> None:
    pool = sorted(enemy for enemy, unlock in UNLOCK.items() if unlock <= d)
    half = make_half(random.Random(d), pool, d, 10.0, harder)
    assert half[0]["enemy"] in WARM_UP
    assert half[0]["time"] == 10.0
    assert half[-1]["time"] == pytest.approx(10.0 + HALF_TIME)
    times = [wave["time"] for wave in half]
    assert times == sorted(times)
    assert {wave["enemy"] for wave in half} <= set(pool)
    total = sum(map(threat, half))
    assert total >= budget(d + harder)
    assert total - threat(half[-1]) < budget(d + harder)  # it stops once the threat is reached


def test_the_newest_enemies_are_the_signature_of_the_finale() -> None:
    d = 18
    pool = sorted(enemy for enemy, unlock in UNLOCK.items() if unlock <= d)
    newest = {enemy for enemy in pool if UNLOCK[enemy] == d}
    finale = make_half(random.Random(5), pool, d, 0.0)[-3:]
    assert {wave["enemy"] for wave in finale} & newest


def test_some_waves_come_together(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(waves, "TWIN_WAVES", (1.0, 1.0))  # every wave with the one before, if it can
    pool = sorted(enemy for enemy, unlock in UNLOCK.items() if unlock <= 10)
    half = make_half(random.Random(2), pool, 10, 0.0)
    times = [wave["time"] for wave in half]
    assert len(set(times)) < len(times)
