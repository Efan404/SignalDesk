FROM python:3.12-slim

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY pyproject.toml .
COPY src/ ./src/

# Install Python dependencies
RUN pip install --no-cache-dir -e .

# Create data directory
RUN mkdir -p /app/data

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Default command
CMD ["python", "-m", "src.cli", "--help"]
