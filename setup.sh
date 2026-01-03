#!/bin/bash

echo "=========================================="
echo "PDF Pipeline Setup"
echo "=========================================="

# Check Python version
echo ""
echo "Checking Python version..."
python --version

# Create virtual environment
echo ""
echo "Creating virtual environment..."
python -m venv venv

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source venv/Scripts/activate

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Start Docker
echo ""
echo "Starting PostgreSQL (Docker)..."
docker-compose up -d

# Wait for PostgreSQL
echo ""
echo "Waiting for PostgreSQL to start..."
sleep 5

# Create tables
echo ""
echo "Creating database tables..."
python -m src.app.create_table

echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Add credentials.json (from Google Cloud Console)"
echo "2. Start API: python -m src.app.flask_app"
echo "3. Visit: http://localhost:5000"
echo ""