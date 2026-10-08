"""A blueprint for building a fighter ship kind.

Fighter fighters have: tail engines, spine weapons, wing roots, and a nose gun.
"""

from random import Random

from pewpy.generators.models.assembly.frame import Frame, Slot
from pewpy.generators.models.assembly.scoring import score_assembly
from pewpy.generators.models.assembly.slots import derive_slots
from pewpy.generators.models.library.catalog import PARTS, get_part


def build_fighter(rng: Random, target_size: tuple[int, int] = (8, 6)) -> Frame:
    """Build a fighter ship of the given target size (span, length).

    Returns the assembled Frame.
    """
    frame = Frame()
    _place_hull(frame, target_size[1])
    _add_fighter_slots(frame, target_size[1])
    _fill_fighter_slots(frame, rng)
    return _assemble_and_score(frame, rng, target_size)


def _place_hull(frame: Frame, length: int) -> None:
    """Place the hull: a central column from tail to nose."""
    for y in range(length):
        width_at_y = 3 if 1 <= y <= length - 2 else 1
        half_w = width_at_y // 2
        for x in range(-half_w, half_w + 1):
            frame.put(x, y, 0, "h")


def _add_fighter_slots(frame: Frame, length: int) -> None:
    """Derive slots from the hull and add fighter-specific slots."""
    derived = derive_slots(frame)
    for name, slot in derived.items():
        frame.slots[name] = slot

    frame.slots["tail_center"] = Slot("tail_center", (0, 0, 0), "forward", 3)
    frame.slots["spine_mid"] = Slot("spine_mid", (0, length // 2, 0), "forward", 4)
    frame.slots["nose"] = Slot("nose", (0, length - 1, 0), "forward", 2)


def _fill_fighter_slots(frame: Frame, rng: Random) -> None:
    """Fill the fighter's slots with parts from the library."""
    # Tail engines (2 engines, mirrored)
    for _ in range(2):
        part = get_part("tail_engine", rng, 1)
        frame.stamp_part(part, "tail_center")

    # Spine weapon (nose gun or turret)
    part_choice = rng.choice(["nose_gun", "turret"])
    part = get_part(part_choice, rng, 1)
    frame.stamp_part(part, "spine_mid")

    # Wing roots (left and right)
    frame.slots["wing_root_left"] = Slot("wing_root_left", (-3, 2, 0), "out", 5)
    frame.slots["wing_root_right"] = Slot("wing_root_right", (3, 2, 0), "out", 5)

    part = get_part("wing_root", rng, 1)
    frame.stamp_part(part, "wing_root_left")
    frame.stamp_part(part, "wing_root_right")

    # Nose gun (optional, replace if already placed)
    if "nose" in frame.slots:
        nose_slot = frame.slots["nose"]
        central_cell = (0, nose_slot.at[1], nose_slot.at[2])
        if central_cell not in frame.cells:
            part = get_part("nose_gun", rng, 1)
            frame.stamp_part(part, "nose")


def _fill_remaining_slots(frame: Frame, rng: Random, skip: list[str]) -> None:
    """Fill any remaining slots randomly, skipping those in `skip`."""
    for slot_name in frame.slots:
        if slot_name not in skip:
            for _ in range(4):
                trial_part_name = rng.choice(list(PARTS.keys()))
                try:
                    trial_part = get_part(trial_part_name, rng, 1)
                except ValueError:
                    continue
                if frame.stamp_part(trial_part, slot_name):
                    break


def _assemble_and_score(frame: Frame, rng: Random, target_size: tuple[int, int]) -> Frame:
    """Fill remaining slots, try many configurations, and return the best."""
    skip = ["tail_center", "spine_mid", "wing_root_left", "wing_root_right", "nose"]
    _fill_remaining_slots(frame, rng, skip)

    frames = []
    for _ in range(16):  # ASSEMBLY_TRIES
        trial = Frame(cells=dict(frame.cells), slots=dict(frame.slots))
        for _ in range(4):
            trial_slot_name = rng.choice(list(trial.slots.keys()))
            if trial_slot_name not in trial.slots:
                continue
            trial_part_name = rng.choice(list(PARTS.keys()))
            try:
                trial_part = PARTS[trial_part_name](rng, 1)
            except ValueError:
                continue
            if trial.stamp_part(trial_part, trial_slot_name):
                break
        frames.append(trial)

    scored = [(score_assembly(f, target_size=target_size, require_symmetry=True), f) for f in frames]
    scored.sort(key=lambda x: x[0])
    return scored[0][1] if scored else frames[0]
