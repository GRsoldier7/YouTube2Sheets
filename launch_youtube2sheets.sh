#!/bin/bash
# YouTube2Sheets Linux/macOS Launcher
# This script launches the YouTube2Sheets application on Linux/macOS

echo "🚀 Starting YouTube2Sheets..."
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed or not in PATH"
    echo "Please install Python 3.8+ from https://python.org"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
if [ ! -f "venv/bin/pip" ]; then
    echo "📦 Installing dependencies..."
    pip install -r requirements.txt
fi

# Check if environment files exist
if [ ! -f ".env" ]; then
    echo "🔧 Setting up environment..."
    python3 setup_secure_environment.py
fi

# Launch the application
echo "🎯 Launching YouTube2Sheets GUI..."
python3 youtube_to_sheets_gui.py

echo "✅ Application finished"