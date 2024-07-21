#!/bin/bash
sudo apt-get update
sudo apt-get install -y python3 python3-pip python3.12-venv wireguard
python3 -m venv venv
source venv/bin/activate
pip install qrcode
python3 wireguard_install.py add --user test --ip 10.10.10.6