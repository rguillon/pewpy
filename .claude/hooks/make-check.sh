#!/usr/bin/env bash
# Stop hook: when Claude finishes a turn that changed code, run `make check`.
# On failure, exit 2 so the output is fed back to Claude, which then fixes the code.
# Skipped when no code file changed since the last passing check; gives up after MAX_ATTEMPTS failures in a row.

MAX_ATTEMPTS=3

cd "${CLAUDE_PROJECT_DIR:-$(dirname "$0")/../..}" || exit 0
state_dir=$(git rev-parse --git-dir 2>/dev/null) || exit 0
passed_file="$state_dir/claude-make-check.passed"
attempts_file="$state_dir/claude-make-check.attempts"

# Fingerprint of the code in the working tree: tracked changes plus untracked code files.
code=(':(glob)**/*.py' pyproject.toml uv.lock)
fingerprint() {
  {
    git diff HEAD -- "${code[@]}"
    git ls-files --others --exclude-standard -z -- "${code[@]}" | xargs -0 -r cat
  } | git hash-object --stdin
}

[ "$(fingerprint)" = "$(cat "$passed_file" 2>/dev/null)" ] && exit 0

if output=$(make check 2>&1); then
  # make check may have reformatted files: record the fingerprint after its fixes.
  fingerprint >"$passed_file"
  rm -f "$attempts_file"
  exit 0
fi

attempts=$(($(cat "$attempts_file" 2>/dev/null || echo 0) + 1))
if [ "$attempts" -gt "$MAX_ATTEMPTS" ]; then
  rm -f "$attempts_file"
  echo "{\"systemMessage\": \"make check still fails after $MAX_ATTEMPTS fix attempts; stopping. Run 'make check' to see why.\"}"
  exit 0
fi
echo "$attempts" >"$attempts_file"

{
  echo "\`make check\` failed (attempt $attempts/$MAX_ATTEMPTS). Fix the problems below, then finish again."
  echo "Note: pre-commit may have auto-fixed files (ruff format, whitespace); re-read them before editing."
  echo
  echo "$output" | tail -n 80
} >&2
exit 2
