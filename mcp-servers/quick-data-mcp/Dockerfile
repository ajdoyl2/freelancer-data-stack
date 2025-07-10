# Dockerfile for Quick Data MCP Server

# Use the official Python image as a parent image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install the dependencies listed in pyproject.toml
RUN pip install --no-cache-dir mcp[cli]>=1.9.2 pandas>=2.2.3 plotly>=6.1.2 pytest>=8.3.5 pytest-asyncio>=1.0.0 fastapi>=0.104.1 uvicorn>=0.24.0

# Run the HTTP server when the container launches
CMD ["python", "http_server.py"]
