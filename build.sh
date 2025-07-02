#!/usr/bin/env bash
# build.sh

# Set Python to 3.12
python3.12 -m venv .venv
source .venv/bin/activate

# Install with no cache
pip install --upgrade pip
pip install -r requirements.txt --no-cache-dir
