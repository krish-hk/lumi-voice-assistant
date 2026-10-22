#!/bin/bash
# LUMI Voice Assistant — Run Script
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_DIR"

# Activate venv if exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Pass all arguments to the app
python -m lumi_voice.app "$@"
