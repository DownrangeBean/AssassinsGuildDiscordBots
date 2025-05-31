@echo off
echo Starting Discord Bot...
echo.

REM Check if virtual environment exists
if not exist .venv\Scripts\activate.bat (
    echo Virtual environment not found. Creating one...
    python -m venv .venv
    echo Virtual environment created.
)

REM Activate virtual environment
call .venv\Scripts\activate.bat

REM Install requirements if needed
echo Checking requirements...
pip install -r requirements.txt

REM Run the bot
echo.
echo Starting bot...
python bot.py

REM Deactivate virtual environment on exit
call .venv\Scripts\deactivate.bat