#!/bin/bash

echo "Running code quality checks..."
make check

if [ $? -eq 0 ]; then
    echo "✅ All checks passed!"
else
    echo "❌ Some checks failed. Running auto-fixes..."
    # If needed, you can add auto-fix commands here
    echo "Fixes would be applied by linters and formatters."
fi