"""What goes wrong reading a drawing."""


class VoxelDrawingError(ValueError):
    """A voxel drawing or its palette is malformed."""

    @classmethod
    def ragged_rows(cls) -> "VoxelDrawingError":
        return cls("every row of a voxel drawing must have the same length")

    @classmethod
    def malformed(cls, source: str, message: str) -> "VoxelDrawingError":
        return cls(f"{source}: {message}")

    @classmethod
    def even_thickness(cls, char: str) -> "VoxelDrawingError":
        return cls(f"thickness of {char!r} must be odd, so the voxels stay centered")
