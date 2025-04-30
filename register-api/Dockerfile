# Use Python 3.11 slim image as base
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV ENVIRONMENT production

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    skopeo \
    libpq-dev \
    postgresql-client \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Create entrypoint script
RUN printf '#!/bin/sh\n\
printenv\n\
echo "Waiting for database..."\n\
python app/db/init_db.py\n\
if [ $? -eq 0 ]; then\n\
    echo "Database initialized successfully"\n\
    exec uvicorn main:app --host 0.0.0.0 --port 8000\n\
else\n\
    echo "Database initialization failed"\n\
    exit 1\n\
fi' > /app/entrypoint.sh && \
    chmod 755 /app/entrypoint.sh

# Copy the rest of the application
COPY . .

# Create storage directory
RUN mkdir -p storage

# Expose the port the app runs on
EXPOSE 8000

# Use the entrypoint script
ENTRYPOINT ["/app/entrypoint.sh"] 
