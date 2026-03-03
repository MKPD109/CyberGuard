#!/bin/bash

# CyberGuard Startup Script

echo "🛡️  Starting CyberGuard..."
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found!"
    echo "Please copy .env.example to .env and add your API keys"
    exit 1
fi

# Check if virtual environment should be activated
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

# Run Django
echo "Starting Django server..."
echo "Access the app at: http://localhost:8000"
echo ""
python manage.py runserver
