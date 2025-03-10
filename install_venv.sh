#!/bin/bash

# Create a virtual environment
python -m venv myenv

# Activate the virtual environment
source myenv/bin/activate

# Install the required packages
pip install -r requirements.txt

echo "Activate the virtual environment by running 'source myenv/bin/activate'"