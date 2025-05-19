#!/bin/bash

# Create virtual environment
echo "Creating virtual environment..."
python -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Create uploads directory
echo "Creating uploads directory..."
mkdir -p static/uploads

# Initialize database
echo "Initializing database..."
python -c "from app import init_db; init_db()"

echo "Setup complete! Run 'python app.py' to start the application."