#!/bin/bash

# Freelancer Data Stack - Streamlit Runner
# ========================================
# This script runs the Streamlit analytics application

echo "🏗️ Starting Freelancer Data Stack Analytics..."
echo "📊 Streamlit application will be available at: http://localhost:8501"

# Ensure we're in the correct directory
cd "$(dirname "$0")"

# Install dependencies if needed
echo "🔧 Installing dependencies..."
cd ../../  # Go to project root
uv sync --group viz
cd viz/streamlit/  # Return to streamlit directory

# Set environment variables from .env if it exists
if [ -f "../../.env" ]; then
    echo "🔑 Loading environment variables..."
    set -a
    source ../../.env
    set +a
fi

# Run Streamlit
echo "🚀 Launching Streamlit..."
cd ../../  # Go to project root to use uv
uv run streamlit run viz/streamlit/app.py --server.address=0.0.0.0 --server.port=8501

echo "✨ Streamlit application started successfully!"
