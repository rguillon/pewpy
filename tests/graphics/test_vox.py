import pytest

from pewpy.graphics import vox


def test_vox_files_round_trip():
    model = vox.VoxModel((3, 2, 4), [(0, 0, 0, 1), (2, 1, 3, 2)], [(255, 0, 0, 255), (0, 0, 255, 255)])
    back = vox.read(vox.write(model))
    assert back.size == model.size
    assert back.voxels == model.voxels
    assert back.palette[:2] == model.palette


def test_not_a_vox_file_is_refused():
    with pytest.raises(vox.VoxError):
        vox.read(b"nope")
