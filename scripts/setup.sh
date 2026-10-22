#!/bin/bash
# LUMI Voice Assistant — Setup Script (Linux/macOS)
set -e

echo "================================"
echo " LUMI Voice Assistant Setup"
echo "================================"
echo

# Check Python
PYTHON=${PYTHON:-python3}
if ! command -v $PYTHON &> /dev/null; then
    echo "ERROR: Python 3 not found. Install Python 3.10+ first."
    exit 1
fi

PY_VERSION=$($PYTHON -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo "Python: $PY_VERSION"

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    $PYTHON -m venv venv
fi
source venv/bin/activate
echo "Virtual environment activated"

# Install system dependencies (Debian/Ubuntu)
if command -v apt-get &> /dev/null; then
    echo "Installing system audio dependencies..."
    sudo apt-get update -qq
    sudo apt-get install -y -qq portaudio19-dev libsndfile1 || true
fi

# Install Python dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -e ".[dev]"

# Check Ollama
if command -v ollama &> /dev/null; then
    echo "✅ Ollama found"
    echo "   Pull a model: ollama pull gemma3:1b"
else
    echo "⚠️  Ollama not found. Install from: https://ollama.com/download"
fi

# Check Piper
if command -v piper &> /dev/null; then
    echo "✅ Piper found"
else
    echo "⚠️  Piper not found. Download from: https://github.com/rhasspy/piper/releases"
fi

echo
echo "Setup complete! Run with:"
echo "  source venv/bin/activate"
echo "  python -m lumi_voice.app"
echo
echo "Or run diagnostics:"
echo "  python scripts/diagnostics.py"
