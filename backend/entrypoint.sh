#!/bin/bash
set -e

echo "⏳ Waiting for database to be ready..."
sleep 5

echo "🔄 Running database migrations..."
alembic upgrade head

echo "🧪 Running automated tests..."
pytest app/tests/ -v --tb=short

if [ $? -eq 0 ]; then
    echo "✅ All tests passed! Starting the application..."
else
    echo "❌ Tests failed! Please check the errors above."
    exit 1
fi

echo "🚀 Starting FastAPI server..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
