#!/bin/bash
# Start development server

echo "Starting NexTOps Backend Development Server..."
echo "======================================"
echo ""
echo "Checking environment setup..."

# Check if .env exists
if [ ! -f .env ]; then
    echo "Creating .env from .env.example..."
    cp .env.example .env
    echo "⚠️  Please update .env with your database credentials"
fi

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python -m venv venv
    source venv/bin/activate
    echo "Installing dependencies..."
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

echo ""
echo "Starting FastAPI server..."
echo "======================================"
echo "API Documentation: http://localhost:8000/docs"
echo "ReDoc: http://localhost:8000/redoc"
echo "Health Check: http://localhost:8000/health"
echo "======================================"
echo ""

python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
