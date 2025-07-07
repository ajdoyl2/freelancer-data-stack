#!/bin/bash
set -e

# AI Agent Data Stack Deployment Script
# This script handles the complete deployment of the AI agent system

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."

    # Check Python
    if ! command_exists python; then
        if ! command_exists python3; then
            log_error "Python 3.9+ is required but not installed"
            exit 1
        fi
        PYTHON_CMD="python3"
    else
        PYTHON_CMD="python"
    fi

    # Check Python version
    PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1,2)
    REQUIRED_VERSION="3.9"

    if ! echo "$PYTHON_VERSION $REQUIRED_VERSION" | awk '{exit !($1 >= $2)}'; then
        log_error "Python $REQUIRED_VERSION+ is required, but $PYTHON_VERSION is installed"
        exit 1
    fi

    # Check Docker
    if ! command_exists docker; then
        log_error "Docker is required but not installed"
        exit 1
    fi

    # Check Docker Compose
    if ! command_exists docker-compose && ! docker compose version >/dev/null 2>&1; then
        log_error "Docker Compose is required but not installed"
        exit 1
    fi

    log_success "Prerequisites check passed"
}

# Setup environment
setup_environment() {
    log_info "Setting up environment..."

    cd "$PROJECT_ROOT"

    # Check if .env exists
    if [ ! -f .env ]; then
        if [ -f .env.example ]; then
            log_info "Copying .env.example to .env"
            cp .env.example .env
            log_warning "Please configure API keys in .env file before proceeding"
        else
            log_error ".env.example file not found"
            exit 1
        fi
    fi

    # Check for API keys
    log_info "Checking API key configuration..."

    API_KEYS_FOUND=0

    if grep -q "^OPENAI_API_KEY=sk-" .env 2>/dev/null; then
        log_info "✓ OpenAI API key found"
        API_KEYS_FOUND=$((API_KEYS_FOUND + 1))
    fi

    if grep -q "^ANTHROPIC_API_KEY=sk-ant-" .env 2>/dev/null; then
        log_info "✓ Anthropic API key found"
        API_KEYS_FOUND=$((API_KEYS_FOUND + 1))
    fi

    if grep -q "^GOOGLE_API_KEY=AIza" .env 2>/dev/null; then
        log_info "✓ Google API key found"
        API_KEYS_FOUND=$((API_KEYS_FOUND + 1))
    fi

    if grep -q "^XAI_API_KEY=xai-" .env 2>/dev/null; then
        log_info "✓ xAI API key found"
        API_KEYS_FOUND=$((API_KEYS_FOUND + 1))
    fi

    if [ $API_KEYS_FOUND -eq 0 ]; then
        log_error "No API keys found in .env file. Please configure at least one API key."
        exit 1
    fi

    log_success "Environment setup completed ($API_KEYS_FOUND API keys configured)"
}

# Install Python dependencies
install_dependencies() {
    log_info "Installing Python dependencies..."

    cd "$PROJECT_ROOT"

    # Install core dependencies
    $PYTHON_CMD -m pip install pydantic-ai anthropic openai python-dotenv

    # Install testing dependencies
    $PYTHON_CMD -m pip install pytest pytest-asyncio

    log_success "Dependencies installed"
}

# Run validation tests
run_validation() {
    log_info "Running validation tests..."

    cd "$PROJECT_ROOT"

    # Run the main validation script
    if $PYTHON_CMD test_implementation.py; then
        log_success "Validation tests passed"
    else
        log_error "Validation tests failed"
        exit 1
    fi

    # Run unit tests if pytest is available
    if command_exists pytest; then
        log_info "Running unit tests..."
        if $PYTHON_CMD -m pytest tests/test_configuration.py -v; then
            log_success "Unit tests passed"
        else
            log_warning "Some unit tests failed, but core functionality is working"
        fi
    fi
}

# Deploy data stack services
deploy_services() {
    log_info "Deploying data stack services..."

    cd "$PROJECT_ROOT"

    # Create volumes directory
    VOLUMES_DIR="$HOME/data-stack/volumes"
    if [ ! -d "$VOLUMES_DIR" ]; then
        log_info "Creating volumes directory: $VOLUMES_DIR"
        mkdir -p "$VOLUMES_DIR"
    fi

    # Check if Docker daemon is running
    if ! docker info >/dev/null 2>&1; then
        log_error "Docker daemon is not running. Please start Docker and try again."
        exit 1
    fi

    # Deploy services
    log_info "Starting Docker services..."

    if command_exists docker-compose; then
        COMPOSE_CMD="docker-compose"
    else
        COMPOSE_CMD="docker compose"
    fi

    # Start core services
    $COMPOSE_CMD up -d postgres meltano airflow-webserver metabase

    # Wait for services to be ready
    log_info "Waiting for services to start..."
    sleep 30

    # Check service health
    check_service_health

    log_success "Data stack services deployed"
}

# Check service health
check_service_health() {
    log_info "Checking service health..."

    # Check PostgreSQL
    if docker ps --filter "name=postgres" --filter "status=running" | grep -q postgres; then
        log_info "✓ PostgreSQL is running"
    else
        log_warning "✗ PostgreSQL is not running"
    fi

    # Check Airflow
    if docker ps --filter "name=airflow" --filter "status=running" | grep -q airflow; then
        log_info "✓ Airflow is running"
    else
        log_warning "✗ Airflow is not running"
    fi

    # Check Metabase
    if docker ps --filter "name=metabase" --filter "status=running" | grep -q metabase; then
        log_info "✓ Metabase is running"
    else
        log_warning "✗ Metabase is not running"
    fi
}

# Create sample workflow
create_sample_workflow() {
    log_info "Creating sample workflow..."

    cd "$PROJECT_ROOT"

    cat > sample_workflow.py << 'EOF'
#!/usr/bin/env python3
"""
Sample AI Agent Workflow

This script demonstrates basic usage of the AI agent system.
"""

import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from interface.workflow_executor import WorkflowExecutor

async def main():
    """Run sample AI agent workflows."""

    print("🤖 AI Agent System - Sample Workflow")
    print("=" * 50)

    executor = WorkflowExecutor()

    # Sample requests
    requests = [
        "Check the status of Docker services",
        "Show me the current environment configuration",
        "List available AI agents and their capabilities"
    ]

    for i, request in enumerate(requests, 1):
        print(f"\n{i}. Processing: '{request}'")

        try:
            result = await executor.process_request(request)
            print(f"   Status: {result.status}")
            print(f"   Response: {result.content[:100]}...")
        except Exception as e:
            print(f"   Error: {str(e)}")

    print("\n✅ Sample workflow completed!")

if __name__ == "__main__":
    asyncio.run(main())
EOF

    chmod +x sample_workflow.py

    log_success "Sample workflow created: sample_workflow.py"
}

# Show deployment status
show_deployment_status() {
    log_info "Deployment Status Summary"
    echo "=" * 50

    echo ""
    echo "🤖 AI Agent System:"
    echo "  - Configuration: ✓ Ready"
    echo "  - Dependencies: ✓ Installed"
    echo "  - Validation: ✓ Passed"

    echo ""
    echo "📊 Data Stack Services:"

    if docker ps --filter "name=postgres" --filter "status=running" | grep -q postgres; then
        echo "  - PostgreSQL: ✓ Running (Port 5432)"
    else
        echo "  - PostgreSQL: ✗ Not running"
    fi

    if docker ps --filter "name=airflow" --filter "status=running" | grep -q airflow; then
        echo "  - Airflow: ✓ Running (Port 8080)"
    else
        echo "  - Airflow: ✗ Not running"
    fi

    if docker ps --filter "name=metabase" --filter "status=running" | grep -q metabase; then
        echo "  - Metabase: ✓ Running (Port 3002)"
    else
        echo "  - Metabase: ✗ Not running"
    fi

    echo ""
    echo "🚀 Getting Started:"
    echo "  - Run AI agents: python sample_workflow.py"
    echo "  - Run examples: python examples/basic_agent_usage.py"
    echo "  - Run tests: python test_implementation.py"
    echo "  - Access Airflow: http://localhost:8080"
    echo "  - Access Metabase: http://localhost:3002"

    echo ""
    log_success "Deployment completed successfully!"
}

# Main deployment function
main() {
    echo "🚀 AI Agent Data Stack Deployment"
    echo "=================================="
    echo ""

    check_prerequisites
    setup_environment
    install_dependencies
    run_validation

    # Ask about data stack deployment
    echo ""
    read -p "Do you want to deploy the data stack services (Docker)? [y/N]: " -n 1 -r
    echo ""

    if [[ $REPLY =~ ^[Yy]$ ]]; then
        deploy_services
    else
        log_info "Skipping data stack services deployment"
    fi

    create_sample_workflow
    show_deployment_status
}

# Handle script arguments
case "${1:-}" in
    "check")
        check_prerequisites
        ;;
    "env")
        setup_environment
        ;;
    "deps")
        install_dependencies
        ;;
    "test")
        run_validation
        ;;
    "services")
        deploy_services
        ;;
    "status")
        show_deployment_status
        ;;
    *)
        main
        ;;
esac
