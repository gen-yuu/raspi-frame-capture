#!/usr/bin/env bash
set -euo pipefail

# システム依存パッケージ
echo "Installing APT packages..."
sudo apt-get update -y
sudo apt-get install -y \
    build-essential cmake git pkg-config \
    python3 python3-venv python3-dev \
    libopenblas-dev\
    python3-opencv     
    # libjpeg-dev libtiff5-dev libpng-dev \
    # libavcodec-dev libavformat-dev libswscale-dev libv4l-dev \
    #  libatlas-base-dev


# Python仮想環境
echo "Creating venv..."
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo "Setup completed."