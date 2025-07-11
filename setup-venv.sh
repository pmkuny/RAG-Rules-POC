#!/bin/bash

# Virtual environment setup script for RAG Rules POC
set -e

VENV_DIR="venv"
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "🐍 Setting up Python virtual environment for RAG Rules POC..."

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

echo "📍 Project root: $PROJECT_ROOT"
echo "🔍 Python version: $(python3 --version)"

# Create virtual environment if it doesn't exist
if [ ! -d "$VENV_DIR" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source "$VENV_DIR/bin/activate"

# Upgrade pip in virtual environment
echo "⬆️  Upgrading pip..."
python -m pip install --upgrade pip

# Install Lambda dependencies
echo "📚 Installing Lambda dependencies..."
if [ -f "lambda/requirements.txt" ]; then
    python -m pip install -r lambda/requirements.txt
else
    echo "⚠️  lambda/requirements.txt not found"
fi

# Install MCP server dependencies
echo "🔧 Installing MCP server dependencies..."
if [ -f "mcp-server/requirements.txt" ]; then
    python -m pip install -r mcp-server/requirements.txt
else
    echo "⚠️  mcp-server/requirements.txt not found"
fi

# Install additional development dependencies
echo "🛠️  Installing development dependencies..."
if [ -f "requirements-dev.txt" ]; then
    python -m pip install -r requirements-dev.txt
else
    # Fallback to basic dependencies
    python -m pip install requests boto3
fi

echo "✅ Virtual environment setup complete!"
echo ""
echo "To activate the virtual environment manually:"
echo "  source $VENV_DIR/bin/activate"
echo ""
echo "To deactivate:"
echo "  deactivate"
echo ""
echo "Next steps:"
echo "1. Run: source $VENV_DIR/bin/activate"
echo "2. Run: ./deploy.sh"
