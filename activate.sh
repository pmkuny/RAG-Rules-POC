#!/bin/bash

# Convenience script to activate the virtual environment
# Usage: source ./activate.sh

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$PROJECT_ROOT/venv"

if [ ! -d "$VENV_DIR" ]; then
    echo "❌ Virtual environment not found. Please run ./setup-venv.sh first"
    return 1 2>/dev/null || exit 1
fi

echo "🔌 Activating virtual environment..."
source "$VENV_DIR/bin/activate"
echo "✅ Virtual environment activated!"
echo "To deactivate, run: deactivate"
