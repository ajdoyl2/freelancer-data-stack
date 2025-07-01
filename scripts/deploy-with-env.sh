#!/bin/bash

# Deploy Terraform Infrastructure with Real Credentials from .env
# Usage: ./scripts/deploy-with-env.sh [local|prod] [plan|apply|destroy]

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

# Check arguments
if [ $# -ne 2 ]; then
    print_error "Usage: $0 [local|prod] [plan|apply|destroy]"
    exit 1
fi

ENVIRONMENT=$1
ACTION=$2

# Validate environment
if [[ "$ENVIRONMENT" != "local" && "$ENVIRONMENT" != "prod" ]]; then
    print_error "Environment must be 'local' or 'prod'"
    exit 1
fi

# Validate action
if [[ "$ACTION" != "plan" && "$ACTION" != "apply" && "$ACTION" != "destroy" ]]; then
    print_error "Action must be 'plan', 'apply', or 'destroy'"
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    print_error ".env file not found in project root"
    exit 1
fi

print_status "Loading environment variables from .env file..."

# Source the .env file
set -a  # automatically export all variables
source .env
set +a  # stop automatically exporting

# Verify required Snowflake variables are set
required_vars=("SNOWFLAKE_ACCOUNT" "SNOWFLAKE_USERNAME" "SNOWFLAKE_PASSWORD")
for var in "${required_vars[@]}"; do
    if [ -z "${!var:-}" ]; then
        print_error "Required environment variable $var is not set in .env file"
        exit 1
    fi
done

print_success "Environment variables loaded successfully"

# Navigate to Terraform directory
cd infra/terraform

# Copy the appropriate backend configuration
print_status "Configuring backend for $ENVIRONMENT environment..."
cp "environments/$ENVIRONMENT/backend.tf" .

# Initialize Terraform
print_status "Initializing Terraform..."
terraform init -reconfigure

# Create temporary tfvars file with real values
TEMP_TFVARS="environments/$ENVIRONMENT/terraform-with-env.tfvars"
print_status "Creating temporary tfvars file with real credentials..."

# Start with the base tfvars file
cp "environments/$ENVIRONMENT/terraform.tfvars" "$TEMP_TFVARS"

# Override Snowflake values with real credentials from .env
cat >> "$TEMP_TFVARS" << EOF

# Real credentials loaded from .env file (temporary override)
snowflake_account      = "$SNOWFLAKE_ACCOUNT"
snowflake_username     = "$SNOWFLAKE_USERNAME"
snowflake_password     = "$SNOWFLAKE_PASSWORD"
snowflake_role         = "$SNOWFLAKE_ROLE"
snowflake_database_name = "$SNOWFLAKE_DATABASE"
EOF

# Add AWS profile if set
if [ -n "${AWS_PROFILE:-}" ]; then
    echo "# AWS profile from environment" >> "$TEMP_TFVARS"
    echo "# Note: Set via AWS_PROFILE environment variable" >> "$TEMP_TFVARS"
fi

print_status "Running terraform $ACTION for $ENVIRONMENT environment..."

# Execute the Terraform command
case $ACTION in
    "plan")
        terraform plan -var-file="$TEMP_TFVARS" -out="${ENVIRONMENT}.tfplan"
        print_success "Plan completed successfully"
        print_warning "Review the plan above before running 'apply'"
        ;;
    "apply")
        if [ -f "${ENVIRONMENT}.tfplan" ]; then
            print_status "Applying existing plan..."
            terraform apply "${ENVIRONMENT}.tfplan"
        else
            print_warning "No existing plan found, creating and applying..."
            terraform plan -var-file="$TEMP_TFVARS" -out="${ENVIRONMENT}.tfplan"
            terraform apply "${ENVIRONMENT}.tfplan"
        fi
        print_success "Infrastructure deployed successfully"
        ;;
    "destroy")
        print_warning "This will DESTROY all infrastructure in $ENVIRONMENT environment!"
        if [ "$ENVIRONMENT" = "prod" ]; then
            echo -n "Type 'destroy-production' to confirm: "
            read -r confirmation
            if [ "$confirmation" != "destroy-production" ]; then
                print_error "Destruction cancelled"
                exit 1
            fi
        else
            echo -n "Are you sure? [y/N]: "
            read -r confirmation
            if [[ "$confirmation" != "y" && "$confirmation" != "Y" ]]; then
                print_error "Destruction cancelled"
                exit 1
            fi
        fi
        terraform destroy -var-file="$TEMP_TFVARS" -auto-approve
        print_success "Infrastructure destroyed successfully"
        ;;
esac

# Clean up temporary files
print_status "Cleaning up temporary files..."
rm -f "$TEMP_TFVARS"

print_success "Deployment script completed successfully"
