from pewpy.graphics.models.drawings.errors import VoxelDrawingError


def test_each_drawing_error_says_what_is_wrong() -> None:
    assert isinstance(VoxelDrawingError.ragged_rows(), ValueError)
    assert "same length" in str(VoxelDrawingError.ragged_rows())
    assert str(VoxelDrawingError.malformed("ship.json", "no rows")) == "ship.json: no rows"
    assert str(VoxelDrawingError.even_thickness("a")) == "thickness of 'a' must be odd, so the voxels stay centered"
