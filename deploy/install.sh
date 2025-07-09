#! /usr/bin/env bash
sudo cp deploy/systemd/frame-capture.service /etc/systemd/system/
sudo systemctl daemon-reload && sudo systemctl enable frame-capture
pip install -r requirements.txt