# Dockerfile for MCP Server

# Use the official Python image as a parent image
FROM python:3.11

# Set the working directory in the container
WORKDIR /app

# Install UV
RUN pip install --no-cache-dir uv

# Copy dependency files from project root for better caching
COPY pyproject.toml uv.lock ./

# Install dependencies using UV
RUN uv sync --group server --no-dev

# Copy the application code
COPY mcp-server/ /app

# Make port 80 available to the world outside this container
EXPOSE 80

# Define environment variable
ENV NAME World

# Run app.py when the container launches
CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
