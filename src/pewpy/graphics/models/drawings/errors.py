"""What goes wrong reading a drawing."""


class VoxelDrawingError(ValueError):
    """A voxel drawing or its palette is malformed."""

    @classmethod
    def ragged_rows(cls) -> "VoxelDrawingError":
        """Make the error for a drawing whose rows don't all have the same length."""
        return cls("every row of a voxel drawing must have the same length")

    @classmethod
    def malformed(cls, source: str, message: str) -> "VoxelDrawingError":
        """Make the error for a malformed drawing, naming its `source`."""
        return cls(f"{source}: {message}")

    @classmethod
    def even_thickness(cls, char: str) -> "VoxelDrawingError":
        """Make the error for a character of even thickness (it couldn't be centered)."""
        return cls(f"thickness of {char!r} must be odd, so the voxels stay centered")
