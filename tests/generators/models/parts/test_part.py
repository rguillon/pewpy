from pewpy.generators.models.parts.part import MOUNTS, Part, Sketch


def test_a_housing_is_plated_with_lights_in_its_front_corners() -> None:
    sketch = Sketch()
    sketch.housing(2, 0, 4, 0, 1)
    assert (sketch.cells[2, 4, 1], sketch.cells[-2, 4, 1]) == ("p", "p")
    assert sketch.cells[0, 2, 1] == "k"  # a seam across its top
    assert sketch.cells[2, 0, 0] == "N"


def test_cubes_boxes_rods_and_discs_are_mirrored_unless_told() -> None:
    sketch = Sketch()
    sketch.put(1, 0, 0, "h")
    sketch.put(3, 0, 0, "h", mirror=False)
    assert (-1, 0, 0) in sketch.cells
    assert (-3, 0, 0) not in sketch.cells
    sketch.box(1, 2, 5, 6, 0, 0, "k")
    assert len([cell for cell in sketch.cells if cell[1] in (5, 6)]) == 8
    rod = Sketch()
    rod.rod(0, 3, 1.0, "N")
    assert {(x, z) for x, _, z in rod.cells} == {(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)}
    disc = Sketch()
    disc.disc(0, 1.0, 0, 0, "N")
    assert (0, 0, 0) in disc.cells


def test_a_part_knows_its_extent_symmetry_footprint_and_rows() -> None:
    sketch = Sketch()
    sketch.box(-1, 1, 0, 3, -1, 1, "h")
    sketch.weapon("gun", 1, 3, 0)
    sketch.nozzle(0.5, 0, 0.0, 1.0)
    part = sketch.part("block", "hull", "hull", "a block")
    assert (part.low, part.high, part.extent()) == ((-1, 0, -1), (1, 3, 1), (3, 4, 3))
    assert part.symmetric
    assert len(part.footprint) == 12
    assert part.rows[0] == (1, 1, -1)
    assert part.weapons == (("gun", -1, 3, 0), ("gun", 1, 3, 0))
    assert part.nozzles == ((-0.5, 0, 0.0, 1.0), (0.5, 0, 0.0, 1.0))
    assert part.mount in MOUNTS


def test_a_part_drawn_on_one_side_is_lopsided() -> None:
    assert not Part("side", "armor", "side", "", {(0, 0, 0): "h", (-1, 0, 0): "h"}).symmetric


def test_a_housing_one_cube_wide_has_no_inner_plate() -> None:
    sketch = Sketch()
    sketch.housing(0, 0, 4, 0, 1)
    assert set(sketch.cells.values()) <= {"N", "H", "k", "p"}
    assert "h" not in sketch.cells.values()
