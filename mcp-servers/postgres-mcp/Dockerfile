FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy shared modules
COPY shared /app/shared

# Copy server code
COPY postgres-mcp /app/postgres-mcp

# Set Python path
ENV PYTHONPATH=/app

# Expose port
EXPOSE 9000

# Run the server
CMD ["python", "-m", "postgres-mcp.server"]
