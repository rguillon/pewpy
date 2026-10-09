"""The Dev menu's parts browser."""

from pewpy import config
from pewpy.generators.models.parts_browser import PartBrowser, part_drawing
from pewpy.generators.models.ships.parts import KINDS, catalog
from pewpy.graphics import models


def test_left_and_right_go_through_the_parts_of_its_kind() -> None:
    browser = PartBrowser(list(KINDS).index("wing"))
    assert browser.kind == "wing"
    browser.move(-1)
    assert browser.part is browser.parts[-1]  # wrapping around
    browser.move(1)
    assert (browser.kind, browser.index) == ("wing", 0)


def test_it_says_what_the_part_is() -> None:
    browser = PartBrowser(list(KINDS).index("engine"), 0)
    part = browser.part
    assert browser.title() == f"{part.name.capitalize()}  (1/{len(browser.parts)})"
    assert browser.details().startswith(f"Engines. {part.description}")
    assert "Mounted on the back." in browser.details()
    width, length, height = part.extent()
    assert browser.info() == f"{width} x {length} x {height} cubes   1 nozzle"
    assert browser.size() == (width * config.MODEL_VOXEL, length * config.MODEL_VOXEL)


def test_every_part_is_drawn_as_the_game_reads_drawings() -> None:
    for part in catalog().values():
        drawing = part_drawing(part)
        voxels = models.parse_voxels(drawing)
        assert (voxels.width, voxels.height) == part.extent()[:2]
        assert len(voxels.cells) == len(part.cells)
        assert len(drawing["engines"]) == len(part.nozzles)
