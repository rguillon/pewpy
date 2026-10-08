"""Score a trial assembly and keep the best one.

The assembler tries N assemblies (e.g. 20), each time filling slots with different parts from the library
in different orders, and keeps the one with the best score. The score combines:

- One-piece constraint (VSL-4): all cubes must touch through faces
- Size closeness: total span/length/height should be close to expected
- Part diversity: use a good mix of kinds
- Weapon coverage: have weapons of several kinds
- No floating parts: every part should be connected to the core
- Symmetry: if expected, the model should be symmetric

Lower score = better.
"""

from pewpy.generators.models.assembly.frame import Frame

# Score weights (tune these for the best variety)
WEIGHT_ONE_PIECE = 3.0  # if model is not one piece, this is a huge penalty
WEIGHT_SIZE = 2.0  # how close the model is to the target size
WEIGHT_DIVERSITY = 1.0  # how many different part kinds are used
WEIGHT_WEAPONS = 1.5  # how many weapon kinds are present
WEIGHT_FLOATING = 2.0  # if any part floats free


def _score_one_piece(frame: Frame) -> float:
    """Score penalty for not being one piece."""
    if not frame.is_one_piece():
        return WEIGHT_ONE_PIECE * 100.0  # massive penalty
    return 0.0


def _score_size(frame: Frame, target_size: tuple[int, int] | None) -> float:
    """Score penalty for size difference from target."""
    if not target_size:
        return 0.0
    score = 0.0
    span = frame.span()
    length = frame.length()
    wanted_span, wanted_length = target_size
    if wanted_span and wanted_span > 0:
        score += WEIGHT_SIZE * abs(span - wanted_span)
    if wanted_length and wanted_length > 0:
        score += WEIGHT_SIZE * abs(length - wanted_length)
    return score


def _score_diversity(frame: Frame) -> float:
    """Score based on part diversity (more unique chars = lower score)."""
    chars = set(frame.cells.values())
    return WEIGHT_DIVERSITY * (1.0 / max(1, len(chars)))


def _score_weapons(frame: Frame) -> float:
    """Score based on weapon coverage (more weapons = lower score)."""
    weapon_count = sum(1 for c in frame.cells.values() if c == "r")
    if weapon_count > 0:
        return WEIGHT_WEAPONS / max(1, weapon_count)
    return 0.0


def _score_floating(frame: Frame) -> float:
    """Score penalty for very sparse (floating) parts."""
    if not frame.cells:
        return 0.0
    span = frame.span()
    length = frame.length()
    height = frame.height()
    total_cells = max(1, span * length * height)
    occupied = len(frame.cells)
    fill_ratio = occupied / total_cells
    if fill_ratio < 0.15:  # very sparse
        return WEIGHT_FLOATING * 5.0
    return 0.0


def _score_symmetry(frame: Frame) -> float:
    """Return a penalty for each cell missing its mirror image across x=0."""
    penalty = 0.0
    for x, y, z in frame.cells:
        if x < 0 and (-x, y, z) not in frame.cells:
            penalty += 3.0
    return penalty


def score_assembly(
    frame: Frame, target_size: tuple[int, int] | None = None, *, require_symmetry: bool = False
) -> float:
    """Return a score for `frame`: lower is better.

    `target_size` is (span, length) in cubes; when None we only check constraints.
    `require_symmetry` means the model must be mirror-symmetric across x=0.
    """
    score = 0.0
    score += _score_one_piece(frame)
    score += _score_size(frame, target_size)
    score += _score_diversity(frame)
    score += _score_weapons(frame)
    score += _score_floating(frame)
    if require_symmetry:
        score += _score_symmetry(frame)
    return score


def pick_best(
    frames: list[Frame], target_size: tuple[int, int] | None = None, *, require_symmetry: bool = False
) -> Frame | None:
    """Return the frame with the best score from `frames`."""
    if not frames:
        return None
    scored = [(score_assembly(f, target_size, require_symmetry=require_symmetry), f) for f in frames]
    scored.sort(key=lambda x: x[0])
    return scored[0][1]
