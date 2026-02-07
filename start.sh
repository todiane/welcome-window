#!/bin/bash
echo "Starting The Welcome Window..."

if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate

if [ ! -f "venv/installed" ]; then
    echo "Installing dependencies..."
    pip install -r requirements.txt
    touch venv/installed
fi

if [ ! -f "welcome_window.db" ]; then
    echo "Initializing database..."
    python -c "import models; models.init_db()"
fi

echo "Starting application at http://localhost:5000"
echo "Press Ctrl+C to stop"
python app.py