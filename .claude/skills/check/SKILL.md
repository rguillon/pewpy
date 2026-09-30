---
name: check
description: Run `make check` (lock file, pre-commit/ruff, ty, deptry) and fix every reported problem until it passes. Use when asked to check, lint, or type-check the project.
---

1. Run `make check` from the project root.
2. If it passes, report that and stop.
3. Otherwise fix each reported problem in the code. Rules:
   - Fix the cause; don't silence it with `# noqa`, `# type: ignore` or config changes unless the user agrees.
   - pre-commit may auto-fix files (ruff format, whitespace). Re-read a file before editing it.
   - A deptry error about a missing dependency means adding it with `uv add <package>`, not removing the import.
4. Re-run `make check` and repeat until it passes. If the same error survives 3 attempts, stop and explain it to the user.
