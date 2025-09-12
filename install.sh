#!/bin/bash

# Perfect Game Scraper Installation Script

echo "Perfect Game Scraper Installation"
echo "================================="

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed. Please install Python 3 first."
    exit 1
fi

echo "✓ Python 3 found"

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "Error: pip3 is not installed. Please install pip first."
    exit 1
fi

echo "✓ pip3 found"

# Create virtual environment
echo ""
echo "Creating Python virtual environment..."
if [ -d "venv" ]; then
    echo "Virtual environment already exists. Removing old one..."
    rm -rf venv
fi

python3 -m venv venv

if [ $? -ne 0 ]; then
    echo "Error: Failed to create virtual environment."
    exit 1
fi

echo "✓ Virtual environment created"

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

if [ $? -ne 0 ]; then
    echo "Error: Failed to activate virtual environment."
    exit 1
fi

echo "✓ Virtual environment activated"

# Upgrade pip and install wheel
echo "Upgrading pip and installing build tools..."
pip install --upgrade pip setuptools wheel

# Install requirements with optimizations
echo "Installing Python dependencies..."
echo "This may take a few minutes for packages that need to be compiled..."

# Install packages individually to better handle issues
echo "Installing requests..."
pip install --only-binary=:all: "requests>=2.28.0,<3.0.0" || pip install "requests>=2.28.0,<3.0.0"

echo "Installing beautifulsoup4..."
pip install --only-binary=:all: "beautifulsoup4>=4.11.0,<5.0.0" || pip install "beautifulsoup4>=4.11.0,<5.0.0"

echo "Installing urllib3..."
pip install --only-binary=:all: "urllib3>=1.26.0,<3.0.0" || pip install "urllib3>=1.26.0,<3.0.0"

echo "Installing lxml (this may take longer)..."
pip install --only-binary=:all: "lxml>=4.6.0,<5.0.0" || {
    echo "Pre-built lxml not available, trying to build from source..."
    pip install "lxml>=4.6.0,<5.0.0" --timeout=300
}

echo "Installing pandas (this may take longer)..."
pip install --only-binary=:all: "pandas>=1.5.0,<3.0.0" || {
    echo "Pre-built pandas not available, trying to build from source..."
    pip install "pandas>=1.5.0,<3.0.0" --timeout=300
}

if [ $? -ne 0 ]; then
    echo "Error: Failed to install dependencies."
    exit 1
fi

echo "✓ Dependencies installed"

# Make the script executable
chmod +x pg_scraper.py
echo "✓ Script made executable"

echo ""
echo "🎉 Installation complete!"
echo ""
echo "To use the scraper:"
echo "1. Activate the virtual environment:"
echo "   source venv/bin/activate"
echo ""
echo "2. Run the scraper:"
echo "   python pg_scraper.py 'https://www.perfectgame.org/Teams/Default.aspx?ID=12345'"
echo "   python pg_scraper.py 'https://www.perfectgame.org/Teams/Default.aspx?ID=12345' -u username -p password"
echo ""
echo "3. When done, deactivate the virtual environment:"
echo "   deactivate"
echo ""
echo "For more information, see README.md"
