#!/bin/bash
set -ev
sudo apt-get install -y python-virtualenv
pip2 install -r files/snapstore/requirements.txt
sudo cp files/snapstore/store.py /usr/bin/store.py
