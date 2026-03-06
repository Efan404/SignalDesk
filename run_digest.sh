#!/bin/bash
# run_digest.sh - Trigger SignalDesk daily digest

cd "$(dirname "$0")"

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Activate virtual environment and run
source .venv/bin/activate
python -m src.cli digest
