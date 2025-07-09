#!/bin/bash

# Inait Predict Examples - Development Environment Setup
# This script sets up the UV environment for running the Jupyter notebooks

echo "🚀 Setting up inait Predict Examples environment..."

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "❌ UV is not installed. Please install it first:"
    echo "   curl -LsSf https://astral.sh/uv/install.sh | sh"
    echo "   or visit: https://docs.astral.sh/uv/getting-started/installation/"
    exit 1
fi

echo "✅ UV found, proceeding with setup..."

# Create virtual environment and install dependencies
echo "📦 Creating virtual environment and installing dependencies..."
uv sync

echo "🎉 Environment setup complete!"
echo ""
echo "To activate the environment and start Jupyter:"
echo "  uv run jupyter lab"
echo ""
echo "Or to run the notebook directly:"
echo "  uv run jupyter notebook basic_functionality.ipynb"
echo ""
echo "To activate the shell environment:"
echo "  source .venv/bin/activate"
