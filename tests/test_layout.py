"""The tests mirror the code: every module has its test file, every test file its module (06-technical.md TEC-14)."""

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE, TESTS = ROOT / "src" / "pewpy", ROOT / "tests"
NAMES = {"__init__": "init", "__main__": "main"}  # their test files' names


def holds_code(path: Path) -> bool:
    """Tell whether a module does more than import, document and list what it exports."""
    for node in ast.parse(path.read_text()).body:
        if isinstance(node, ast.Import | ast.ImportFrom):
            continue
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant):
            continue
        target = node.targets[0] if isinstance(node, ast.Assign) else getattr(node, "target", None)
        if isinstance(target, ast.Name) and target.id == "__all__":
            continue
        return True
    return False


def where_tested(module: Path) -> Path:
    """Return where a module is tested."""
    relative = module.relative_to(SOURCE)
    return TESTS / relative.parent / f"test_{NAMES.get(relative.stem, relative.stem)}.py"


def expected() -> dict[Path, Path]:
    """Return every test file there should be, and its module."""
    modules = (path for path in sorted(SOURCE.rglob("*.py")) if path.name != "__init__.py" or holds_code(path))
    return {where_tested(module): module for module in modules}


def test_every_module_has_its_test_file() -> None:
    missing = [str(module.relative_to(ROOT)) for test, module in expected().items() if not test.is_file()]
    assert missing == []


def test_every_test_file_tests_a_module() -> None:
    known = set(expected()) | {Path(__file__).resolve()}
    orphans = [str(test.relative_to(ROOT)) for test in sorted(TESTS.rglob("test_*.py")) if test not in known]
    assert orphans == []


def test_a_package_that_only_gathers_its_modules_needs_no_test_file() -> None:
    assert not holds_code(SOURCE / "audio" / "synth" / "__init__.py")
    assert holds_code(SOURCE / "audio" / "sfx" / "__init__.py")
    assert (
        where_tested(SOURCE / "generators" / "levels" / "__main__.py")
        == TESTS / "generators" / "levels" / "test_main.py"
    )
