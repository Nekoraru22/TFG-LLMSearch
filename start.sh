#!/bin/bash

# Load environment variables from .env file
source ./.env

# Configure prefect server
prefect config set PREFECT_API_URL="http://$PREFECT_IP:$PREFECT_PORT/api"

# Try to stop any existing Prefect server
prefect server stop

# Start the Prefect
prefect server start --host $PREFECT_IP --port $PREFECT_PORT --background

# Start the backend
python main.py