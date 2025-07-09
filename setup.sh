#!/usr/bin/env bash
set -euo pipefail

# システム依存パッケージ
sudo apt-get update
sudo xargs -a deploy/system_packages.yml \
  bash -c 'cat $0 | yq ".[] | .[]" | xargs sudo apt-get install -y'

# Python仮想環境
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt