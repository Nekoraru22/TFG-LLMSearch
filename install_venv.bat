@echo off

@REM Create a virtual environment
python -m venv myenv

@REM Activate the virtual environment
call myenv\Scripts\activate

@REM Upgrade pip
python -m pip install --upgrade pip

@REM Install the latest version of Prefect
pip install -U prefect

@REM Install the custom package from for terminal command
pip install -e .

@REM Install the required packages
pip install -r requirements.txt

echo "\n\nAActivate the virtual environment by running 'myenv\Scripts\activate'"