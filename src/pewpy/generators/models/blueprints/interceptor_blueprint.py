"""A blueprint for building an interceptor ship kind.

Interceptors are long and thin, with small wings, canards, and tip weapons.
"""

from random import Random

from pewpy.generators.models.assembly.frame import Frame, Slot
from pewpy.generators.models.assembly.scoring import score_assembly
from pewpy.generators.models.assembly.slots import derive_slots
from pewpy.generators.models.library.catalog import PARTS, get_part


def build_interceptor(rng: Random, target_size: tuple[int, int] = (6, 10)) -> Frame:
    """Build an interceptor ship of the given target size (span, length).

    Interceptors are long and thin: narrow hull, small wings, canards forward,
    and weapons on the wings or nose.
    """
    frame = Frame()
    _place_hull(frame, rng, target_size[1])
    _add_interceptor_slots(frame, target_size[1])
    _fill_interceptor_slots(frame, rng)
    all_slots = list(frame.slots.keys())
    _fill_remaining_slots(frame, rng, all_slots)
    return _assemble_and_score(frame, rng, target_size, all_slots)


def _place_hull(frame: Frame, rng: Random, length: int) -> None:
    """Place the hull: a long, narrow spine."""
    for y in range(length):
        width = 1 if y < 2 or y >= length - 2 else rng.choice([1, 2])
        half_w = width // 2
        for x in range(-half_w, half_w + 1):
            frame.put(x, y, 0, "h")


def _add_interceptor_slots(frame: Frame, length: int) -> None:
    """Derive slots from the hull and add interceptor-specific slots."""
    derived = derive_slots(frame)
    for name, slot in derived.items():
        frame.slots[name] = slot

    frame.slots["tail_center"] = Slot("tail_center", (0, 0, 0), "forward", 2)
    canard_y = length // 3
    frame.slots["canard"] = Slot("canard", (0, canard_y, 0), "forward", 3)
    frame.slots["spine_weapon"] = Slot("spine_weapon", (0, length // 2, 0), "forward", 3)
    frame.slots["nose"] = Slot("nose", (0, length - 1, 0), "forward", 2)
    wing_y = length // 2
    frame.slots["wing_left"] = Slot("wing_left", (-2, wing_y, 0), "out", 4)
    frame.slots["wing_right"] = Slot("wing_right", (2, wing_y, 0), "out", 4)


def _fill_interceptor_slots(frame: Frame, rng: Random) -> None:
    """Fill the interceptor's slots with parts from the library."""
    # Tail engine (small, centered)
    part = get_part("tail_engine", rng, 1)
    frame.stamp_part(part, "tail_center")

    # Canard (small wing-like part)
    part = get_part("wing_root", rng, 1)
    frame.stamp_part(part, "canard")

    # Spine weapon (turret or nose gun)
    part_choice = rng.choice(["nose_gun", "turret"])
    part = get_part(part_choice, rng, 1)
    frame.stamp_part(part, "spine_weapon")

    # Wing weapons (optional)
    for wing_slot in ["wing_left", "wing_right"]:
        if rng.random() < 0.5:
            part = get_part("nose_gun", rng, 1)
            frame.stamp_part(part, wing_slot)

    # Nose gun (optional, if space)
    if rng.random() < 0.6:
        part = get_part("nose_gun", rng, 1)
        central_cell = (0, frame.slots["nose"].at[1], frame.slots["nose"].at[2])
        if central_cell not in frame.cells:
            frame.stamp_part(part, "nose")


def _fill_remaining_slots(frame: Frame, rng: Random, all_slots: list[str]) -> None:
    """Fill any remaining slots randomly from `all_slots`."""
    for _ in range(8):
        if not all_slots:
            break
        slot_name = rng.choice(all_slots)
        if slot_name not in frame.slots:
            all_slots.remove(slot_name)
            continue
        for _ in range(4):
            trial_part_name = rng.choice(list(PARTS.keys()))
            try:
                trial_part = PARTS[trial_part_name](rng, 1)
            except ValueError:
                continue
            if frame.stamp_part(trial_part, slot_name):
                all_slots.remove(slot_name)
                break


def _assemble_and_score(frame: Frame, rng: Random, target_size: tuple[int, int], all_slots: list[str]) -> Frame:
    """Try many configurations and return the best."""
    frames = []
    for _ in range(20):  # ASSEMBLY_TRIES
        trial = Frame(cells=dict(frame.cells), slots=dict(frame.slots))
        for _ in range(4):
            if not all_slots:
                break
            trial_slot_name = rng.choice(all_slots)
            if trial_slot_name not in trial.slots:
                all_slots.remove(trial_slot_name)
                continue
            for _ in range(3):
                trial_part_name = rng.choice(list(PARTS.keys()))
                try:
                    trial_part = PARTS[trial_part_name](rng, 1)
                except ValueError:
                    continue
                if trial.stamp_part(trial_part, trial_slot_name):
                    all_slots.remove(trial_slot_name)
                    break
        frames.append(trial)

    scored = [(score_assembly(f, target_size=target_size, require_symmetry=True), f) for f in frames]
    scored.sort(key=lambda x: x[0])
    return scored[0][1] if scored else frames[0]
