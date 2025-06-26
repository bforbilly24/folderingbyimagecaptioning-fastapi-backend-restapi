#!/bin/bash

# Image Foldering API - Quick Start Script
# This script helps you set up and run the FastAPI backend quickly

set -e  # Exit on any error

echo "🚀 Image Foldering API - Quick Start"
echo "=================================="

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check Python version
echo "📋 Checking Python version..."
if command_exists python3; then
    PYTHON_CMD=python3
elif command_exists python; then
    PYTHON_CMD=python
else
    echo "❌ Python not found. Please install Python 3.11 or higher."
    exit 1
fi

PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | cut -d' ' -f2)
echo "✅ Found Python $PYTHON_VERSION"

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ] || [ ! -f "requirements.txt" ]; then
    echo "❌ Please run this script from the project root directory"
    exit 1
fi

# Option to choose installation method
echo ""
echo "Choose installation method:"
echo "1) UV (Recommended - faster)"
echo "2) Virtual Environment (Standard)"
echo "3) Docker"
read -p "Enter choice (1-3): " choice

case $choice in
    1)
        echo "📦 Installing with UV..."
        if ! command_exists uv; then
            echo "Installing UV..."
            $PYTHON_CMD -m pip install uv
        fi
        uv sync
        echo "🚀 Starting server with UV..."
        uv run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
        ;;
    2)
        echo "📦 Setting up virtual environment..."
        $PYTHON_CMD -m venv .venv
        
        # Activate virtual environment
        if [ -f ".venv/bin/activate" ]; then
            source .venv/bin/activate
        else
            source .venv/Scripts/activate
        fi
        
        echo "📦 Installing dependencies..."
        pip install -r requirements.txt
        
        echo "🚀 Starting server..."
        uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
        ;;
    3)
        echo "🐳 Using Docker..."
        if ! command_exists docker; then
            echo "❌ Docker not found. Please install Docker first."
            exit 1
        fi
        
        echo "Building Docker image..."
        docker build -t image-foldering-api .
        
        echo "🚀 Starting server with Docker..."
        docker run -p 8000:8000 -v $(pwd)/uploads:/app/uploads -v $(pwd)/folderisasi:/app/folderisasi image-foldering-api
        ;;
    *)
        echo "❌ Invalid choice"
        exit 1
        ;;
esac

echo ""
echo "🎉 Server should be running at:"
echo "   📍 API: http://localhost:8000"
echo "   📖 Docs: http://localhost:8000/docs"
echo "   📚 ReDoc: http://localhost:8000/redoc"
echo ""
echo "Press Ctrl+C to stop the server"
