# Use an explicit, slim stable Python image
# Reduced container size and minimal packages
FROM python:3.11-slim

# Prevent Python from writing .pyc files to disk and optimize stream buffering
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies (sqlite3 library for debugging tool states)
RUN apt-get update && apt-get install -y --no-install-recommends \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY ./app ./app

# Set up storage space and assign strict folder ownership permissions
RUN mkdir -p /app/data && \
    useradd -u 8888 appuser && \
    chown -R appuser:appuser /app

# Switch runtime to the isolated, non-root user for security
USER appuser

# Start the agent loop
CMD ["python", "app/main.py"]