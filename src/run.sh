#!/bin/bash
sudo apt-get update && sudo apt-get -y upgrade
sudo apt install python3
pip install qrcode
python3 wireguard_install.py add --user test --ip 10.10.10.6