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
pip install -r requirements.txt

# Set environment variables from .env if it exists
if [ -f "../../.env" ]; then
    echo "🔑 Loading environment variables..."
    set -a
    source ../../.env
    set +a
fi

# Run Streamlit
echo "🚀 Launching Streamlit..."
streamlit run app.py --server.address=0.0.0.0 --server.port=8501

echo "✨ Streamlit application started successfully!"
