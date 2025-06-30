# Freelancer Data Stack Infrastructure Makefile

# Variables
TERRAFORM_DIR := infra/terraform
LOCAL_ENV_DIR := $(TERRAFORM_DIR)/environments/local
PROD_ENV_DIR := $(TERRAFORM_DIR)/environments/prod

# Colors for output
RED := \033[0;31m
GREEN := \033[0;32m
YELLOW := \033[0;33m
BLUE := \033[0;34m
NC := \033[0m # No Color

.PHONY: help init-local init-prod plan-local plan-prod deploy-local deploy-prod destroy-local destroy-prod clean lint format validate check-tools

# Default target
help: ## Show this help message
	@echo "$(BLUE)Freelancer Data Stack Infrastructure$(NC)"
	@echo ""
	@echo "$(GREEN)Available commands:$(NC)"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  $(YELLOW)%-20s$(NC) %s\n", $$1, $$2}' $(MAKEFILE_LIST)

# Tool checks
check-tools: ## Check if required tools are installed
	@echo "$(BLUE)Checking required tools...$(NC)"
	@command -v terraform >/dev/null 2>&1 || { echo "$(RED)Error: terraform is not installed$(NC)"; exit 1; }
	@command -v aws >/dev/null 2>&1 || { echo "$(RED)Error: aws CLI is not installed$(NC)"; exit 1; }
	@echo "$(GREEN)All required tools are installed$(NC)"

# Local environment commands
init-local: check-tools ## Initialize Terraform for local environment
	@echo "$(BLUE)Initializing Terraform for local environment...$(NC)"
	@cd $(TERRAFORM_DIR) && \
		cp $(LOCAL_ENV_DIR)/backend.tf . && \
		terraform init -reconfigure
	@echo "$(GREEN)Local environment initialized$(NC)"

plan-local: init-local ## Plan Terraform changes for local environment
	@echo "$(BLUE)Planning Terraform changes for local environment...$(NC)"
	@cd $(TERRAFORM_DIR) && \
		terraform plan -var-file="$(LOCAL_ENV_DIR)/terraform.tfvars" -out=local.tfplan
	@echo "$(GREEN)Local environment plan completed$(NC)"

deploy-local: plan-local ## Deploy infrastructure to local environment
	@echo "$(BLUE)Deploying to local environment...$(NC)"
	@cd $(TERRAFORM_DIR) && \
		terraform apply local.tfplan
	@echo "$(GREEN)Local environment deployed successfully$(NC)"

destroy-local: init-local ## Destroy local environment infrastructure
	@echo "$(RED)WARNING: This will destroy all local infrastructure!$(NC)"
	@read -p "Are you sure? [y/N] " confirm && [ "$$confirm" = "y" ] || exit 1
	@cd $(TERRAFORM_DIR) && \
		terraform destroy -var-file="$(LOCAL_ENV_DIR)/terraform.tfvars" -auto-approve
	@echo "$(GREEN)Local environment destroyed$(NC)"

# Production environment commands
init-prod: check-tools ## Initialize Terraform for production environment
	@echo "$(BLUE)Initializing Terraform for production environment...$(NC)"
	@cd $(TERRAFORM_DIR) && \
		cp $(PROD_ENV_DIR)/backend.tf . && \
		terraform init -reconfigure
	@echo "$(GREEN)Production environment initialized$(NC)"

init-prod-first-time: check-tools ## Initialize Terraform for production (first time setup without remote backend)
	@echo "$(BLUE)Initializing Terraform for production (first time)...$(NC)"
	@echo "$(YELLOW)Note: This is for first-time setup to create the S3 backend$(NC)"
	@cd $(TERRAFORM_DIR) && \
		cp $(LOCAL_ENV_DIR)/backend.tf . && \
		terraform init -reconfigure
	@echo "$(GREEN)Production environment initialized for first-time setup$(NC)"

plan-prod: init-prod ## Plan Terraform changes for production environment
	@echo "$(BLUE)Planning Terraform changes for production environment...$(NC)"
	@cd $(TERRAFORM_DIR) && \
		terraform plan -var-file="$(PROD_ENV_DIR)/terraform.tfvars" -out=prod.tfplan
	@echo "$(GREEN)Production environment plan completed$(NC)"

deploy-prod-first-time: check-tools ## Deploy production infrastructure for the first time (creates S3 backend)
	@echo "$(BLUE)Deploying production infrastructure (first time)...$(NC)"
	@echo "$(YELLOW)Note: This will create the S3 backend and then migrate to it$(NC)"
	@cd $(TERRAFORM_DIR) && \
		cp $(LOCAL_ENV_DIR)/backend.tf . && \
		terraform init -reconfigure && \
		terraform plan -var-file="$(PROD_ENV_DIR)/terraform.tfvars" -out=prod.tfplan && \
		terraform apply prod.tfplan
	@echo "$(GREEN)Production infrastructure deployed. Now migrating to S3 backend...$(NC)"
	@cd $(TERRAFORM_DIR) && \
		cp $(PROD_ENV_DIR)/backend.tf . && \
		terraform init -migrate-state
	@echo "$(GREEN)Production environment deployed and migrated to S3 backend$(NC)"

deploy-prod: plan-prod ## Deploy infrastructure to production environment
	@echo "$(BLUE)Deploying to production environment...$(NC)"
	@echo "$(RED)WARNING: This will deploy to production!$(NC)"
	@read -p "Are you sure? [y/N] " confirm && [ "$$confirm" = "y" ] || exit 1
	@cd $(TERRAFORM_DIR) && \
		terraform apply prod.tfplan
	@echo "$(GREEN)Production environment deployed successfully$(NC)"

destroy-prod: init-prod ## Destroy production environment infrastructure
	@echo "$(RED)DANGER: This will destroy ALL production infrastructure!$(NC)"
	@echo "$(RED)This action is IRREVERSIBLE and will delete all data!$(NC)"
	@read -p "Type 'destroy-production' to confirm: " confirm && [ "$$confirm" = "destroy-production" ] || exit 1
	@cd $(TERRAFORM_DIR) && \
		terraform destroy -var-file="$(PROD_ENV_DIR)/terraform.tfvars"
	@echo "$(GREEN)Production environment destroyed$(NC)"

# Terraform utilities
validate: ## Validate Terraform configuration
	@echo "$(BLUE)Validating Terraform configuration...$(NC)"
	@cd $(TERRAFORM_DIR) && terraform validate
	@echo "$(GREEN)Terraform configuration is valid$(NC)"

format: ## Format Terraform configuration files
	@echo "$(BLUE)Formatting Terraform files...$(NC)"
	@cd $(TERRAFORM_DIR) && terraform fmt -recursive
	@echo "$(GREEN)Terraform files formatted$(NC)"

lint: format validate ## Lint Terraform configuration

# Output commands
output-local: ## Show Terraform outputs for local environment
	@echo "$(BLUE)Local environment outputs:$(NC)"
	@cd $(TERRAFORM_DIR) && terraform output

output-prod: ## Show Terraform outputs for production environment
	@echo "$(BLUE)Production environment outputs:$(NC)"
	@cd $(TERRAFORM_DIR) && terraform output

# Cleanup
clean: ## Clean up temporary files
	@echo "$(BLUE)Cleaning up temporary files...$(NC)"
	@cd $(TERRAFORM_DIR) && rm -f *.tfplan *.tfstate.backup backend.tf
	@echo "$(GREEN)Cleanup completed$(NC)"

# Environment setup helpers
setup-aws-credentials: ## Setup AWS credentials (interactive)
	@echo "$(BLUE)Setting up AWS credentials...$(NC)"
	@aws configure
	@echo "$(GREEN)AWS credentials configured$(NC)"

setup-local-secrets: ## Setup local secrets file template
	@echo "$(BLUE)Creating local secrets template...$(NC)"
	@mkdir -p $(LOCAL_ENV_DIR)
	@if [ ! -f $(LOCAL_ENV_DIR)/secrets.tfvars ]; then \
		echo '# Local secrets - DO NOT COMMIT TO VERSION CONTROL' > $(LOCAL_ENV_DIR)/secrets.tfvars; \
		echo 'snowflake_account = "your-account"' >> $(LOCAL_ENV_DIR)/secrets.tfvars; \
		echo 'snowflake_username = "your-username"' >> $(LOCAL_ENV_DIR)/secrets.tfvars; \
		echo 'snowflake_password = "your-password"' >> $(LOCAL_ENV_DIR)/secrets.tfvars; \
		echo "$(GREEN)Created $(LOCAL_ENV_DIR)/secrets.tfvars$(NC)"; \
		echo "$(YELLOW)Please edit this file with your actual credentials$(NC)"; \
	else \
		echo "$(YELLOW)$(LOCAL_ENV_DIR)/secrets.tfvars already exists$(NC)"; \
	fi

# CI/CD helpers
github-oidc-setup: ## Display GitHub OIDC setup instructions
	@echo "$(BLUE)GitHub OIDC Setup Instructions:$(NC)"
	@echo ""
	@echo "1. After deploying to production, run:"
	@echo "   $(YELLOW)make output-prod$(NC)"
	@echo ""
	@echo "2. In your GitHub repository, go to Settings > Secrets and variables > Actions"
	@echo ""
	@echo "3. Add the following secrets:"
	@echo "   - $(YELLOW)AWS_REGION$(NC): ca-central-1"
	@echo "   - $(YELLOW)AWS_ROLE_ARN$(NC): [github_oidc_role_arn from terraform output]"
	@echo "   - $(YELLOW)ECR_REGISTRY$(NC): [your-account-id].dkr.ecr.ca-central-1.amazonaws.com"
	@echo ""
	@echo "4. Use the GitHub OIDC role in your workflows to deploy to AWS"

# Comprehensive status check
status: ## Show status of both environments
	@echo "$(BLUE)Infrastructure Status:$(NC)"
	@echo ""
	@echo "$(YELLOW)Local Environment:$(NC)"
	@if [ -f $(TERRAFORM_DIR)/local.tfstate ]; then \
		echo "  State file: $(GREEN)Present$(NC)"; \
	else \
		echo "  State file: $(RED)Missing$(NC)"; \
	fi
	@echo ""
	@echo "$(YELLOW)Production Environment:$(NC)"
	@if [ -f $(TERRAFORM_DIR)/.terraform/terraform.tfstate ]; then \
		echo "  Remote state: $(GREEN)Configured$(NC)"; \
	else \
		echo "  Remote state: $(RED)Not configured$(NC)"; \
	fi
