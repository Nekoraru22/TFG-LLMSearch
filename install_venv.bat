@echo off
python -m venv myenv
call myenv\Scripts\activate
python -m pip install --upgrade pip
pip install -U prefect
pip install -r requirements.txt
echo "\n\nAActivate the virtual environment by running 'myenv\Scripts\activate'"