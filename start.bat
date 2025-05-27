@echo off

@REM Load environment variables from .env file
FOR /F "eol=# tokens=*" %%i IN (.env) DO SET %%i

@REM Configure prefect server
prefect config set PREFECT_API_URL="http://%PREFECT_IP%:%PREFECT_PORT%/api"

@REM Start the Prefect
prefect server start --host %PREFECT_IP% --port %PREFECT_PORT% --background

@REM Start the backend
python main.py