#!/bin/bash

# Create a virtual environment
python3.10 -m venv myenv

# Activate the virtual environment
source myenv/bin/activate

# Upgrade pip
python -m pip install --upgrade pip

# Install the latest version of Prefect
pip install -U prefect

# Install the required packages
pip install -r requirements.txt

echo "\n\nActivate the virtual environment by running 'source myenv/bin/activate'"