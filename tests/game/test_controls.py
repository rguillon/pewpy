from pewpy.game.controls import Controls


def test_with_nothing_pressed_the_ship_stays_and_holds_its_fire() -> None:
    assert Controls() == Controls(move_x=0.0, move_y=0.0, fire=False)


def test_the_controls_say_where_to_move_and_whether_to_fire() -> None:
    controls = Controls(move_x=-1.0, move_y=0.5, fire=True)
    assert (controls.move_x, controls.move_y, controls.fire) == (-1.0, 0.5, True)
