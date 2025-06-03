#!/bin/bash
echo "Waiting for database..."
python app/db/init_db.py
if [ $? -eq 0 ]; then
    echo "Database initialized successfully"
    exec uvicorn main:app --host 0.0.0.0 --port 8000
else
    echo "Database initialization failed"
    exit 1
fi
