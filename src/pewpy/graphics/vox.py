"""Reading and writing MagicaVoxel's .vox files (https://github.com/ephtracy/voxel-model/blob/master/MagicaVoxel-file-format-vox.txt).

A .vox file is "VOX " and a version, then chunks: an id (4 letters), the size of its own content, the size of its
children, the content, the children. The "MAIN" chunk holds the rest: "SIZE" (x, y, z) and "XYZI" (the voxels: x,
y, z and a color index from 1 to 255 each) for each model, and "RGBA" (the palette: color i is entry i - 1). Newer
files add a scene graph and materials, which are skipped: only the first model is read, as it is.

MagicaVoxel's z is up: the game reads a ship lying on the ground, seen from above like in the game (see models.py).
Independent from Panda3D.
"""

import struct
from dataclasses import dataclass

Voxel = tuple[int, int, int, int]  # x, y, z, color index (1 to 255)
RGBA = tuple[int, int, int, int]


class VoxError(ValueError):
    """Not a .vox file the game can read."""

    @classmethod
    def not_vox(cls) -> "VoxError":
        return cls("not a MagicaVoxel .vox file")

    @classmethod
    def no_main(cls) -> "VoxError":
        return cls("no MAIN chunk")

    @classmethod
    def no_model(cls) -> "VoxError":
        return cls("no model (SIZE and XYZI chunks)")


@dataclass
class VoxModel:
    size: tuple[int, int, int]  # x, y, z
    voxels: list[Voxel]
    palette: list[RGBA]  # 256 entries: color index i is palette[i - 1]


def _gray_palette() -> list[RGBA]:
    """Used when a file has no palette of its own (MagicaVoxel then means its default one, which isn't known
    here): shades of grey, so the shape still shows.
    """
    return [(i, i, i, 255) for i in range(256)]


def _chunks(data: bytes, start: int, end: int) -> list[tuple[bytes, bytes, int, int]]:
    """(id, content, children start, children end) of each chunk from `start` to `end`."""
    chunks = []
    at = start
    while at + 12 <= end:
        chunk_id = data[at : at + 4]
        content_size, children_size = struct.unpack_from("<ii", data, at + 4)
        content_start = at + 12
        children_start = content_start + content_size
        chunks.append((chunk_id, data[content_start:children_start], children_start, children_start + children_size))
        at = children_start + children_size
    return chunks


def _four(data: bytes, at: int) -> tuple[int, int, int, int]:
    return data[at], data[at + 1], data[at + 2], data[at + 3]


def read(data: bytes) -> VoxModel:
    if len(data) < 8 or data[:4] != b"VOX ":
        raise VoxError.not_vox()
    main = _chunks(data, 8, len(data))
    if not main or main[0][0] != b"MAIN":
        raise VoxError.no_main()
    _, _, children_start, children_end = main[0]
    size: tuple[int, ...] | None = None
    voxels: list[Voxel] | None = None
    palette = _gray_palette()
    for chunk_id, content, _, _ in _chunks(data, children_start, children_end):
        if chunk_id == b"SIZE" and size is None:
            size = struct.unpack_from("<iii", content)
        elif chunk_id == b"XYZI" and voxels is None:
            (count,) = struct.unpack_from("<i", content)
            voxels = [_four(content, 4 + 4 * i) for i in range(count)]
        elif chunk_id == b"RGBA":
            palette = [_four(content, 4 * i) for i in range(256)]
    if size is None or voxels is None:
        raise VoxError.no_model()
    return VoxModel((size[0], size[1], size[2]), voxels, palette)


def write(model: VoxModel) -> bytes:
    def chunk(chunk_id: bytes, content: bytes, children: bytes = b"") -> bytes:
        return chunk_id + struct.pack("<ii", len(content), len(children)) + content + children

    size = chunk(b"SIZE", struct.pack("<iii", *model.size))
    xyzi = chunk(b"XYZI", struct.pack("<i", len(model.voxels)) + b"".join(bytes(voxel) for voxel in model.voxels))
    palette = (list(model.palette) + [(0, 0, 0, 255)] * 256)[:256]
    rgba = chunk(b"RGBA", b"".join(bytes(color) for color in palette))
    return b"VOX " + struct.pack("<i", 150) + chunk(b"MAIN", b"", size + xyzi + rgba)
