#!/bin/bash
# Database setup and migration script

set -e

echo "NexTOps Backend - Database Setup"
echo "=================================="
echo ""

# Check environment
if [ ! -f .env ]; then
    echo "❌ .env file not found!"
    echo "Creating from .env.example..."
    cp .env.example .env
    echo "⚠️  Please update .env with your database credentials"
    exit 1
fi

# Load environment
set -a
source .env
set +a

echo "Database Configuration:"
echo "  Host: $POSTGRES_HOST"
echo "  Port: $POSTGRES_PORT"
echo "  User: $POSTGRES_USER"
echo "  Database: $POSTGRES_DB"
echo ""

# Check Python virtual environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python -m venv venv
fi

# Activate venv
source venv/bin/activate

# Install/upgrade dependencies
echo "Installing dependencies..."
pip install -r requirements.txt -q

echo ""
echo "Running Alembic migrations..."
echo ""

# Run migrations
alembic upgrade head

echo ""
echo "✅ Database setup complete!"
echo ""
echo "Next steps:"
echo "  1. Start the server: ./run.sh"
echo "  2. Access API docs: http://localhost:8000/docs"
echo "  3. Check health: curl http://localhost:8000/health"
echo ""
