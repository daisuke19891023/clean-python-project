#!/bin/bash

# Script to run Python quality checks after file edits
# This is called by Claude Code's PostToolUse hook

# Get the file path from the first argument (if provided)
FILE_PATH="$1"

# Check if the file is a Python file
if [[ "$FILE_PATH" == *.py ]]; then
    echo "Running quality checks for Python file: $FILE_PATH"
    # run format
    echo "Running format..."
    FORMAT_OUTPUT=$(uv run nox -s format_code 2>&1)
    FORMAT_EXIT_CODE=$?
    if [ $FORMAT_EXIT_CODE -ne 0 ]; then
        echo "ERROR: Formatting failed. Please fix the issues below:" >&2
        echo "$FORMAT_OUTPUT" >&2
        exit 2
    fi

    # Run linting
    echo "Running linting..."
    LINT_OUTPUT=$(uv run nox -s lint 2>&1)
    LINT_EXIT_CODE=$?
    if [ $LINT_EXIT_CODE -ne 0 ]; then
        echo "ERROR: Linting failed. Please fix the issues below:" >&2
        echo "$LINT_OUTPUT" >&2
        exit 2
    fi

    # Run type checking
    echo "Running type checking..."
    TYPING_OUTPUT=$(uv run nox -s typing 2>&1)
    TYPING_EXIT_CODE=$?
    if [ $TYPING_EXIT_CODE -ne 0 ]; then
        echo "ERROR: Type checking failed. Please fix the issues below:" >&2
        echo "$TYPING_OUTPUT" >&2
        exit 2
    fi

    echo "All quality checks passed!"
else
    echo "Skipping quality checks for non-Python file: $FILE_PATH"
fi

exit 0
