import importlib, pkgutil


def test_import_all():
    # Import all modules in the pewpy package
    for _, modname, _ in pkgutil.walk_packages(['src/pewpy']):
        importlib.import_module(f'pewpy.{modname}')
