# pewpy Development Guide

This guide helps agents understand how to work with the pewpy codebase effectively.

## Project Overview

pewpy is a vertical-scrolling shoot 'em up game written in Python with Panda3D. It consists of:
- Game logic in `src/pewpy/`
- Data files in `data/` directory
- Tests in `tests/`
- Documentation in `docs/`

## Key Commands

### Setup & Development
```bash
make install    # Install virtual environment and pre-commit hooks
make check      # Run linting, type-checking, and dependency checks
make run        # Run the game (requires WSL + Mesa d3d12 driver or regular setup)
make test       # Run tests with coverage
make help       # Show all available Makefile commands
```

### Game Generation & AI Training
```bash
make levels     # Generate game levels from world plans
make learn      # Train AI to play the game (default: all ships, all levels)
make learn-level1  # Train on level 1-1 only
make learn-random  # Train with random selection of levels
make winrate     # Test current AI performance on all levels
```

## Development Environment

- Requires Python 3.12 or newer
- Uses `uv` for package management (install with `pip install uv`)
- Uses pre-commit hooks (`make install` sets them up)
- Game uses Panda3D rendering engine (version > 1.10.16)

## Important Directory Structure

- `src/pewpy/`: Main game code
  - `app/`: Application framework and main entrypoint
  - `game/`: Game logic, entities, levels, player controls
  - `generators/`: Level and AI data generation tools
  - `ui/`: User interface components
  - `audio/`: Audio handling
- `data/`: Game assets (ships, enemies, music, etc.)
- `tests/`: Test suite
- `docs/specs/`: Game design documents

## Key Code Areas

### Entry Points
- `src/pewpy/__main__.py`: Application entry point
- `src/pewpy/app/__init__.py`: Main game application class (`PewPewApp`)

### Testing Patterns
- Tests are located in `tests/` with organized modules
- Test files use pytest fixtures and conventions
- Some code intentionally uses `print()` for command-line tools (see pyproject.toml ruff ignore rules)

### Special Considerations
- The game is designed for Windows/WDDM 12 GPU driver (`/dev/dxg`) via WSL, but fallbacks to CPU rendering exist
- AI training uses genetic algorithms with multiple ships and levels
- Many files include special ruff ignores because they make legitimate use of `print()` statements or intentional magic values

## Framework/Toolchain Quirks

- Uses `uv` for package management instead of pip/virtualenv
- Uses pre-commit hooks for code quality
- Uses `ty` (static type checker) with `ruff` linter
- Uses `pytest` and `coverage` for testing
- Uses `mkdocs` for documentation generation
- Uses `mutmut` for mutation testing
- Game data is generated via Python scripts in `src/pewpy/generators/`
- AI training uses genetic algorithms with evolutionary computation

## Testing

### Running Specific Tests
```bash
# Run specific test module
uv run python -m pytest tests/test_app.py

# Run tests with coverage
make test

# Run a single test class or method
uv run python -m pytest tests/test_app.py::TestClassName::test_method_name
```

## Code Style & Conventions

The project uses ruff for linting and formatting. Key conventions:
- Uses `print()` in generator scripts as appropriate for command-line interaction
- Intentionally ignores `S101` assertions (allowed in tests)
- Intentionally ignores documentation requirements (`D100`, `D101`, etc.) in test files
- Uses `ty` for static type checking

## Code Readability Improvements Made

This branch implements several readability enhancements:

1. **Enhanced docstrings**: Added more descriptive docstrings with parameter and return information
2. **Improved type hints**: Added comprehensive typing annotations for better IDE support
3. **Better documentation of complex methods**: Added detailed explanations for methods like `_play_area_visible`
4. **Consistent function signatures**: Improved clarity of function interfaces

These changes improve maintainability without altering core functionality.
