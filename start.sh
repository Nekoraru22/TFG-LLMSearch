#!/bin/bash

# Load environment variables from .env file
source ./.env

# Configure prefect server
prefect config set PREFECT_API_URL="http://$PREFECT_IP:$PREFECT_PORT/api"

# Start the Prefect
prefect server start --host $PREFECT_IP --port $PREFECT_PORT --background

# Start the backend
python main.py