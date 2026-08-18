# Build container for EduPathway AI
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency specifications
COPY pyproject.toml .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir google-genai python-dotenv pydantic rich pytest pytest-asyncio

# Copy application source code
COPY . .

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV EDUPATHWAY_DATA_DIR=/app/data
ENV EDUPATHWAY_TRACES_DIR=/app/traces
ENV EDUPATHWAY_PROFILES_DIR=/app/data/profiles

# Default execution runs the interactive CLI
CMD ["python", "main.py"]
