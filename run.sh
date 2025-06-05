#!/usr/bin/sh
echo 'Starting Discord Bot...'
echo

if [ ! -d ".venv" ]; then
    echo "Virtual environment not found. Creating one..."
    python -m venv .venv
    echo "Virtual environment created."
fi

source .venv/bin/activate

echo "Checking requirements...\n"
pip install -r requirements.txt

echo "Starting bot..."
python ./bot.py

deactivate
