#!/bin/sh
set -e

echo "Starting GST Billing App..."

# Wait for database to be ready
echo "Waiting for database..."
python -c "
import time
import sys
from sqlalchemy import create_engine
from app.config import settings

max_retries = 30
retry_interval = 2

for i in range(max_retries):
    try:
        engine = create_engine(settings.DATABASE_URL)
        connection = engine.connect()
        connection.close()
        print('Database is ready!')
        sys.exit(0)
    except Exception as e:
        if i == max_retries - 1:
            print(f'Failed to connect to database after {max_retries} attempts')
            print(f'Error: {e}')
            sys.exit(1)
        print(f'Database not ready, retrying... ({i+1}/{max_retries})')
        time.sleep(retry_interval)
"

# Run database migrations / create tables
echo "Running database migrations..."
python -c "
from app.database import engine, Base
from app import models  # Import models to register them
print('Creating database tables...')
Base.metadata.create_all(bind=engine)
print('Database tables created successfully!')
"

# Start the application
echo "Starting Gunicorn server..."
exec gunicorn app.main:app \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:${PORT:-8000} \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -
