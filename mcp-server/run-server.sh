#!/bin/bash

# MCP Server wrapper script that uses virtual environment
set -e

# Get the project root directory
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_DIR="$PROJECT_ROOT/venv"

# Check if virtual environment exists
if [ ! -d "$VENV_DIR" ]; then
    echo "❌ Virtual environment not found at $VENV_DIR"
    echo "Please run ./setup-venv.sh from the project root first"
    exit 1
fi

# Activate virtual environment and run the MCP server
source "$VENV_DIR/bin/activate"
exec python "$(dirname "${BASH_SOURCE[0]}")/server.py" "$@"
