#!/bin/bash

# Setup script for quality and observability infrastructure
# This script initializes Prometheus, Grafana, Great Expectations, and Evidence

set -e

echo "🔧 Setting up Quality & Observability Infrastructure..."

# Create necessary directories
VOLUMES_DIR="${HOME}/data-stack/volumes"
echo "📁 Creating volume directories..."

mkdir -p "${VOLUMES_DIR}/prometheus"
mkdir -p "${VOLUMES_DIR}/grafana"
mkdir -p "${VOLUMES_DIR}/great-expectations"
mkdir -p "${VOLUMES_DIR}/evidence"

# Set proper permissions for Grafana
echo "🔐 Setting Grafana permissions..."
sudo chown -R 472:472 "${VOLUMES_DIR}/grafana" 2>/dev/null || echo "Warning: Could not set Grafana permissions"

# Initialize Great Expectations
echo "📊 Initializing Great Expectations..."
docker run --rm \
    -v "${VOLUMES_DIR}/great-expectations:/home/jovyan/work" \
    -e JUPYTER_ENABLE_LAB=yes \
    greatexpectations/great_expectations:latest \
    bash -c "cd /home/jovyan/work && great_expectations init"

# Create Great Expectations checkpoint
echo "✅ Creating Great Expectations checkpoint..."
cat > "${VOLUMES_DIR}/great-expectations/checkpoints/daily_validation.yml" << EOF
name: daily_validation
config_version: 1.0
template_name:
module_name: great_expectations.checkpoint
class_name: Checkpoint
run_name_template: "%Y%m%d-%H%M%S-daily-validation"
expectation_suite_name:
batch_request: {}
action_list:
  - name: store_validation_result
    action:
      class_name: StoreValidationResultAction
  - name: store_evaluation_params
    action:
      class_name: StoreEvaluationParametersAction
  - name: update_data_docs
    action:
      class_name: UpdateDataDocsAction
      site_names: []
evaluation_parameters: {}
runtime_configuration: {}
validations:
  - batch_request:
      datasource_name: postgres_warehouse
      data_connector_name: default_inferred_data_connector
      data_asset_name: stg_freelancers
    expectation_suite_name: freelancer_quality_suite
EOF

# Initialize Evidence project
echo "🎨 Initializing Evidence project..."
docker run --rm \
    -v "${VOLUMES_DIR}/evidence:/app" \
    evidence-dev/evidence:latest \
    npm init evidence-app . --template=basic

# Copy our custom Evidence pages
cp -r viz/evidence/pages/* "${VOLUMES_DIR}/evidence/pages/" 2>/dev/null || echo "Warning: Could not copy Evidence pages"

# Start Prometheus and Grafana
echo "🚀 Starting Prometheus and Grafana..."
docker-compose up -d prometheus grafana

# Wait for Grafana to be ready
echo "⏳ Waiting for Grafana to start..."
timeout=60
counter=0
while ! curl -s http://localhost:3000/api/health > /dev/null; do
    sleep 2
    counter=$((counter + 2))
    if [ $counter -ge $timeout ]; then
        echo "❌ Timeout waiting for Grafana to start"
        exit 1
    fi
done

# Configure Grafana data source (Prometheus)
echo "🔗 Configuring Grafana data source..."
curl -X POST \
  http://admin:admin@localhost:3000/api/datasources \
  -H 'Content-Type: application/json' \
  -d '{
    "name": "Prometheus",
    "type": "prometheus",
    "url": "http://prometheus:9090",
    "access": "proxy",
    "isDefault": true
  }' || echo "Warning: Could not configure Grafana data source"

# Import Grafana dashboard
echo "📈 Importing Grafana dashboard..."
curl -X POST \
  http://admin:admin@localhost:3000/api/dashboards/db \
  -H 'Content-Type: application/json' \
  -d @volumes/grafana/dashboards/data-stack-overview.json || echo "Warning: Could not import dashboard"

# Create initial database schemas for Great Expectations
echo "🗃️ Creating database schemas..."
docker exec -i data-stack-postgres psql -U postgres -d data_stack << EOF
CREATE SCHEMA IF NOT EXISTS great_expectations;
CREATE SCHEMA IF NOT EXISTS monitoring;

-- Create table for validation results
CREATE TABLE IF NOT EXISTS great_expectations.validations (
    id SERIAL PRIMARY KEY,
    expectation_suite_name VARCHAR(255),
    run_name VARCHAR(255),
    run_time TIMESTAMP,
    success BOOLEAN,
    statistics_validated_expectations INTEGER,
    statistics_successful_expectations INTEGER,
    statistics_unsuccessful_expectations INTEGER,
    statistics_success_percent DECIMAL(5,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create table for failed expectations
CREATE TABLE IF NOT EXISTS great_expectations.validation_results (
    id SERIAL PRIMARY KEY,
    validation_id INTEGER REFERENCES great_expectations.validations(id),
    expectation_suite_name VARCHAR(255),
    run_name VARCHAR(255),
    run_time TIMESTAMP,
    expectation_type VARCHAR(255),
    column_name VARCHAR(255),
    success BOOLEAN,
    result_element_count INTEGER,
    result_missing_count INTEGER,
    result_unexpected_count INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create table for data quality metrics
CREATE TABLE IF NOT EXISTS monitoring.data_quality_metrics (
    id SERIAL PRIMARY KEY,
    metric_name VARCHAR(255),
    metric_value DECIMAL(10,4),
    metric_timestamp TIMESTAMP,
    component VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert sample data for testing
INSERT INTO great_expectations.validations (
    expectation_suite_name, run_name, run_time, success,
    statistics_validated_expectations, statistics_successful_expectations,
    statistics_unsuccessful_expectations, statistics_success_percent
) VALUES
    ('freelancer_quality_suite', 'test-run-1', NOW() - INTERVAL '1 hour', true, 10, 10, 0, 100.00),
    ('freelancer_quality_suite', 'test-run-2', NOW() - INTERVAL '2 hours', true, 10, 9, 1, 90.00),
    ('freelancer_quality_suite', 'test-run-3', NOW() - INTERVAL '3 hours', false, 10, 7, 3, 70.00);
EOF

# Set environment variables for Slack integration
echo "💬 Setting up Slack integration..."
cat >> .env << EOF

# Slack Configuration for Alerts
SLACK_API_URL=https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK
SLACK_CHANNEL=#alerts
EOF

echo "✅ Quality & Observability setup complete!"
echo ""
echo "🎯 Access URLs:"
echo "   - Prometheus: http://localhost:9090"
echo "   - Grafana: http://localhost:3000 (admin/admin)"
echo "   - Great Expectations: http://localhost:8888"
echo "   - Evidence: http://localhost:3001"
echo "   - DataHub: http://localhost:9002"
echo ""
echo "📝 Next steps:"
echo "   1. Configure your Slack webhook URL in .env file"
echo "   2. Update Grafana admin password"
echo "   3. Create Great Expectations expectation suites"
echo "   4. Customize Evidence dashboards"
echo ""
echo "🔍 Monitor your setup with:"
echo "   docker-compose logs -f prometheus grafana"
