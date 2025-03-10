@echo off
python -m venv myenv
call myenv\Scripts\activate
pip install -r requirements.txt
echo "Activate the virtual environment by running 'myenv\Scripts\activate'"