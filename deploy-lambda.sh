#!/bin/bash

# Deploy Lambda function script
set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$PROJECT_ROOT/venv"

echo "Building Lambda deployment package..."

# Check if virtual environment exists
if [ ! -d "$VENV_DIR" ]; then
    echo "❌ Virtual environment not found. Please run ./setup-venv.sh first"
    exit 1
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source "$VENV_DIR/bin/activate"

# Create temporary directory
TEMP_DIR=$(mktemp -d)
cd lambda

# Install dependencies using virtual environment
echo "📦 Installing dependencies to temporary directory..."
python -m pip install -r requirements.txt -t $TEMP_DIR

# Copy Lambda code
cp handler.py $TEMP_DIR/

# Create deployment package
cd $TEMP_DIR
zip -r "$PROJECT_ROOT/lambda/governance_rules_handler.zip" .

# Clean up
rm -rf $TEMP_DIR

# Deactivate virtual environment
deactivate

echo "✅ Lambda deployment package created: lambda/governance_rules_handler.zip"
echo "Run 'terraform apply' to deploy the updated Lambda function."
