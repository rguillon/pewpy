"""Reading GLSL source: the functions it defines, whether its brackets match."""

import re

DEFINITION = re.compile(r"^(?:vec[234]|float|void|int|bool|mat[34]) (\w+)\(", re.MULTILINE)


def defines(glsl: str) -> set[str]:
    """Return the names of the functions the source defines."""
    return set(DEFINITION.findall(glsl))


def balanced(glsl: str) -> bool:
    """Tell whether every bracket of the source is closed, in order."""
    closing = {")": "(", "]": "[", "}": "{"}
    open_ones: list[str] = []
    for char in re.sub(r"//[^\n]*", "", glsl):
        if char in "([{":
            open_ones.append(char)
        elif char in closing and (not open_ones or open_ones.pop() != closing[char]):
            return False
    return not open_ones
