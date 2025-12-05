#!/bin/bash

# Create virtual environment if it doesn't exist
if [ ! -d "backend/venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv backend/venv
fi

# Activate virtual environment
source backend/venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r backend/requirements.txt

# Create a local .env file for backend if needed, or just export the variable
export POSTGRES_HOST=localhost

echo "Setup complete!"
echo "To run the app locally:"
echo "  cd backend"
echo "  source venv/bin/activate"
echo "  export POSTGRES_HOST=localhost"
echo "  python -m app.main"
echo ""
echo "To run alembic locally:"
echo "  cd backend"
echo "  source venv/bin/activate"
echo "  alembic upgrade head"
