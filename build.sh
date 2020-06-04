#!/bin/bash
set -e
pip3 install setuptools
pip3 install -r requirements.txt -t lib/
pip3 install -r requirements-matplotlib.txt -t lib/
