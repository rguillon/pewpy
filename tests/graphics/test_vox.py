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


def chunk(name: bytes, content: bytes = b"", children: bytes = b"") -> bytes:
    return name + len(content).to_bytes(4, "little") + len(children).to_bytes(4, "little") + content + children


def vox_file(*children: bytes) -> bytes:
    return b"VOX " + (150).to_bytes(4, "little") + chunk(b"MAIN", children=b"".join(children))


def test_a_vox_file_needs_its_main_chunk_and_a_model():
    with pytest.raises(vox.VoxError, match="MAIN"):
        vox.read(b"VOX " + (150).to_bytes(4, "little") + chunk(b"PACK", b"\x01\x00\x00\x00"))
    with pytest.raises(vox.VoxError, match="no model"):
        vox.read(vox_file())


def test_what_a_vox_file_has_besides_its_first_model_is_skipped():
    size = (1).to_bytes(4, "little") * 3
    voxels = (1).to_bytes(4, "little") + bytes([0, 0, 0, 1])
    model = vox.read(vox_file(chunk(b"SIZE", size), chunk(b"XYZI", voxels), chunk(b"SIZE", size), chunk(b"nTRN")))
    assert model.size == (1, 1, 1) and model.voxels == [(0, 0, 0, 1)]
