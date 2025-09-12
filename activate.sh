#!/bin/bash

# Convenience script to activate the virtual environment

if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Please run ./install.sh first."
    exit 1
fi

echo "Activating Perfect Game Scraper virtual environment..."
source venv/bin/activate

echo "✓ Virtual environment activated"
echo ""
echo "You can now run:"
echo "  python pg_scraper.py 'https://www.perfectgame.org/Teams/Default.aspx?ID=12345'"
echo ""
echo "When done, type 'deactivate' to exit the virtual environment."
