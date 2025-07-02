terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    snowflake = {
      source  = "Snowflake-Labs/snowflake"
      version = "~> 0.87"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.1"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

provider "snowflake" {
  account  = var.snowflake_account
  username = var.snowflake_username
  password = var.snowflake_password
  role     = var.snowflake_role
}

# Data sources for current context
data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

# S3 Module
module "s3" {
  source = "./modules/s3"

  environment          = var.environment
  project_name        = var.project_name
  enable_versioning   = var.s3_enable_versioning
  lifecycle_rules     = var.s3_lifecycle_rules
  allowed_principals  = var.s3_allowed_principals
}

# Snowflake Module
module "snowflake" {
  source = "./modules/snowflake"

  environment     = var.environment
  project_name    = var.project_name
  database_name   = var.snowflake_database_name
  warehouse_size  = var.snowflake_warehouse_size
  auto_suspend    = var.snowflake_auto_suspend
}

# ECR Module
module "ecr" {
  source = "./modules/ecr"

  environment      = var.environment
  project_name     = var.project_name
  repositories     = var.ecr_repositories
  scan_on_push     = var.ecr_scan_on_push
  lifecycle_policy = var.ecr_lifecycle_policy
}

# ECS Module
module "ecs" {
  source = "./modules/ecs"

  environment            = var.environment
  project_name          = var.project_name
  vpc_id                = var.vpc_id
  subnet_ids            = var.subnet_ids
  task_definitions      = var.ecs_task_definitions
  service_configurations = var.ecs_service_configurations

  depends_on = [module.ecr]
}

# Secrets Manager Module
module "secrets_manager" {
  source = "./modules/secrets-manager"

  environment  = var.environment
  project_name = var.project_name
  secrets      = var.secrets_config
}
