#!/usr/bin/env bash
set -euo pipefail

# システム依存パッケージ
echo "Installing APT packages..."
sudo apt-get update -y --fix-missing
sudo apt-get install -y --no-install-recommends \
    build-essential cmake git pkg-config \
    python3 python3-venv python3-dev \
    libopenblas-dev\
    python3-opencv     
    # libjpeg-dev libtiff5-dev libpng-dev \
    # libavcodec-dev libavformat-dev libswscale-dev libv4l-dev \
    #  libatlas-base-dev


# Python依存パッケージ"
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "Setup completed."