#!/bin/bash

# Freelancer Data Stack Setup Script
# This script initializes the data stack environment

set -e

echo "🚀 Setting up Freelancer Data Stack..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker Desktop and try again."
    exit 1
fi

echo "✅ Docker is running"

# Create volumes directory structure
echo "📁 Creating volume directories..."
mkdir -p ~/data-stack/volumes/{postgres,airbyte/{workspace,data,local},airflow/{dags,logs,config,plugins},redis,datahub/{gms,frontend},elasticsearch,neo4j,kafka,zookeeper/{data,logs},great-expectations,evidence,metabase,duckdb,traefik}

echo "✅ Volume directories created"

# Copy DAGs to Airflow volume
echo "📋 Setting up Airflow DAGs..."
cp -r dags/* ~/data-stack/volumes/airflow/dags/ 2>/dev/null || echo "No DAGs to copy yet"

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  No .env file found. Copying from template..."
    cp .env.template .env
    echo "📝 Please edit .env file with your preferred passwords before starting the stack"
    echo "   Current file has secure defaults that you can use as-is"
fi

echo "✅ Environment configuration ready"

# Make sure scripts are executable
chmod +x scripts/*.sh

echo "🐳 Starting Docker Compose stack..."
echo "This may take a few minutes on first run as images are downloaded..."

# Start the stack
docker-compose up -d

echo ""
echo "🎉 Freelancer Data Stack is starting up!"
echo ""
echo "📊 Access your services at:"
echo "   • Airflow:              http://localhost:8080"
echo "   • Airflow Flower:       http://localhost:5555" 
echo "   • Airbyte:              http://localhost:8001"
echo "   • DataHub:              http://localhost:9002"
echo "   • Metabase:             http://localhost:3002"
echo "   • Great Expectations:   http://localhost:8888"
echo "   • Evidence.dev:         http://localhost:3001"
echo "   • DuckDB HTTP:          http://localhost:8002"
echo "   • Traefik Dashboard:    http://localhost:8090"
echo ""
echo "🔐 Default credentials:"
echo "   • Airflow: admin / (check your .env file)"
echo "   • Jupyter: token from .env file or no token if empty"
echo ""
echo "⏳ Services may take 2-3 minutes to fully initialize"
echo "📋 Run 'docker-compose logs -f [service-name]' to check individual service logs"
echo "🛑 Run 'docker-compose down' to stop all services"
echo ""
echo "Happy data engineering! 🎯"
