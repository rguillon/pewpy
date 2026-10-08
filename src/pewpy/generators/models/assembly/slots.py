"""Derive slots from a frame's geometry, so the assembler knows where parts may be stamped.

Slots are derived from the frame's cells: wherever there's a natural place (tail, spine, wings, nose),
a slot is created. The assembler then fills these slots with parts from the library.

Each slot has a name, a position (where the part's anchor goes), a face (which way barrels point), and a
capacity (max part half-width).
"""

from pewpy.generators.models.assembly.frame import Slot

ZERO = 0


def derive_slots(frame: object) -> dict[str, Slot]:
    """Derive slots from a frame's cells, so the assembler knows where parts may be stamped.

    Look for natural places:
    - at the tail (row 0, where engines go)
    - along the spine (x=0, where weapons/parts go)
    - on the wings (where wing parts go)
    - on the flanks (where side parts go)
    - under the hull (where bottom parts go)
    """
    slots: dict[str, Slot] = {}

    if not frame.cells:
        return slots

    # Get bounds
    ys = [c[1] for c in frame.cells]
    max_y = max(ys)

    # --- Tail slot: at row 0, centered ---
    # If the frame has cells at row 0, place an engine slot
    tail_cells_at_0 = [(x, z) for x, y, z in frame.cells if y == 0]
    if tail_cells_at_0:
        # Center the tail slot
        x_mid = sum(x for x, z in tail_cells_at_0) // len(tail_cells_at_0)
        slots["tail_center"] = Slot("tail_center", (x_mid, 0, 0), "forward", 3)

    # --- Spine slot: along x=0 ---
    spine_cells = [(y, z) for x, y, z in frame.cells if x == 0]
    if spine_cells:
        # Middle of the spine
        y_mid = sum(y for y, z in spine_cells) // len(spine_cells)
        slots["spine_mid"] = Slot("spine_mid", (0, y_mid, 0), "forward", 4)

    # --- Wing slots: where wings attach ---
    # Look for cells with x < 0 (left side) that could be wing roots
    wing_root_cells = [(x, y, z) for x, y, z in frame.cells if x < 0 and y < 5]  # near tail
    if wing_root_cells:
        # Pick one near the tail on the left
        wx, wy, wz = wing_root_cells[0]
        slots["wing_root_left"] = Slot("wing_root_left", (wx, wy, wz), "out", 5)
        # Mirror slot on the right
        slots["wing_root_right"] = Slot("wing_root_right", (-wx, wy, wz), "out", 5)

    # --- Nose slot: at the last row ---
    max_y = max(y for _, y, _ in frame.cells)
    nose_cells = [(x, y, z) for x, y, z in frame.cells if y >= max_y - 2]
    if nose_cells:
        nx, ny, nz = nose_cells[0]
        slots["nose"] = Slot("nose", (nx, ny, nz), "forward", 2)

    # --- Flank slots: on the sides, away from the middle ---
    # Look for cells with |x| > 1 and y in the middle range
    flank_cells = [(x, y, z) for x, y, z in frame.cells if abs(x) > 1 and 1 <= y <= 5]
    if flank_cells:
        # Pick one on each side if possible
        for x, y, z in flank_cells[:2]:
            if x < 0:
                slots["flank_left"] = Slot("flank_left", (x, y, z), "out", 3)
            elif x > 0:
                slots["flank_right"] = Slot("flank_right", (x, y, z), "out", 3)

    return slots
