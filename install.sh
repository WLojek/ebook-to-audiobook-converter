#!/bin/bash
# Installation script for the Ebook to Audiobook Converter for macOS
# Python 3.11 is recommended for best compatibility with the kokoro TTS library

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is required but not installed. Please install Python 3 and try again."
    exit 1
fi

# Try to use Python 3.11 if available
PYTHON_CMD="python3"
if command -v python3.11 &> /dev/null; then
    echo "Using Python 3.11 for better compatibility with dependencies"
    PYTHON_CMD="python3.11"
else
    echo "WARNING: Python 3.11 is recommended for best compatibility with kokoro TTS."
    echo "Current Python version:"
    python3 --version
    echo "If you encounter errors, consider installing Python 3.11"
fi

# Check if espeak-ng is already installed
if ! command -v espeak-ng &> /dev/null; then
    echo "espeak-ng is not installed. Installing now (required for Kokoro text-to-speech)..."
    
    # Check if Homebrew is installed
    if ! command -v brew &> /dev/null; then
        echo "Homebrew not found. Installing Homebrew..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    fi
    
    # Install espeak-ng using Homebrew
    echo "Installing espeak-ng..."
    brew install espeak-ng
else
    echo "espeak-ng is already installed. Continuing..."
fi

# Create virtual environment
echo "Creating virtual environment..."
$PYTHON_CMD -m venv venv

# Activate virtual environment
source ./venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "Installation complete!"
echo "To convert an ebook, run: python3 src/main.py --input your_book.epub --voice af_heart"
echo "Note: If you encounter issues with kokoro installation, try:"
echo "  pip install kokoro==0.7.4 soundfile torch" 