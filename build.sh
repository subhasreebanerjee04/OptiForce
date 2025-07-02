#!/usr/bin/env bash
# build.sh

# Set Python to 3.12
python3.12 -m venv .venv
source .venv/bin/activate
# Add to build.sh
sudo fallocate -l 1G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
# Install with no cache
pip install --upgrade pip
pip install -r requirements.txt --no-cache-dir
