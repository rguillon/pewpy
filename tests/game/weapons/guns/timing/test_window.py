from pewpy.game.weapons.guns.gun import Gun
from pewpy.game.weapons.guns.state import GunState
from pewpy.game.weapons.guns.timing import window
from tests.game.weapons.guns.shooting import DT, degrees, shooter


def test_a_gun_can_sweep_streams_in_a_window_each_interval() -> None:
    gun = Gun("fan", 2.0, speed=0.5, window=1.0, gap=0.1, reach=60.0)
    state = GunState(cooldown=0.0)
    angles = []
    for frame in range(1, round(4.0 / DT)):
        angles += [(frame, round(degrees(shot))) for shot in window.step(gun, state, shooter(clock=frame * DT), DT)]
    first = [angle for frame, angle in angles if frame < 120]
    second = [angle for frame, angle in angles if frame >= 120]
    assert first[0] < 0 < first[-1]  # left to right...
    assert second[0] > 0 > second[-1]  # ...then right to left
    assert not [frame for frame, _ in angles if 60 < frame < 120]  # a pause after each sweep
