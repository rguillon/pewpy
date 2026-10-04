import importlib
import pkgutil


def test_import_all() -> None:
    # Import all modules in the pewpy package
    for _, modname, _ in pkgutil.walk_packages(["src/pewpy"]):
        importlib.import_module(f"pewpy.{modname}")
