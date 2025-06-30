# S3 Outputs
output "s3_bucket_names" {
  description = "Names of the S3 buckets created"
  value       = module.s3.bucket_names
}

output "s3_bucket_arns" {
  description = "ARNs of the S3 buckets created"
  value       = module.s3.bucket_arns
}

# Snowflake Outputs
output "snowflake_database_name" {
  description = "Name of the Snowflake database"
  value       = module.snowflake.database_name
}

output "snowflake_warehouse_name" {
  description = "Name of the Snowflake warehouse"
  value       = module.snowflake.warehouse_name
}

output "snowflake_schemas" {
  description = "List of Snowflake schemas created"
  value       = module.snowflake.schemas
}

# ECR Outputs
output "ecr_repository_urls" {
  description = "URLs of the ECR repositories"
  value       = module.ecr.repository_urls
}

output "ecr_repository_arns" {
  description = "ARNs of the ECR repositories"
  value       = module.ecr.repository_arns
}

# ECS Outputs
output "ecs_cluster_name" {
  description = "Name of the ECS cluster"
  value       = module.ecs.cluster_name
}

output "ecs_cluster_arn" {
  description = "ARN of the ECS cluster"
  value       = module.ecs.cluster_arn
}

output "ecs_service_names" {
  description = "Names of the ECS services"
  value       = module.ecs.service_names
}

# Secrets Manager Outputs
output "secrets_manager_arns" {
  description = "ARNs of the secrets in AWS Secrets Manager"
  value       = module.secrets_manager.secret_arns
  sensitive   = true
}

# GitHub OIDC Outputs for CI/CD
output "github_oidc_role_arn" {
  description = "ARN of the GitHub OIDC role for CI/CD deployments"
  value       = aws_iam_role.github_oidc.arn
}

output "github_oidc_role_name" {
  description = "Name of the GitHub OIDC role for CI/CD deployments"
  value       = aws_iam_role.github_oidc.name
}

# Infrastructure Details for CI/CD
output "aws_region" {
  description = "AWS region where resources are deployed"
  value       = data.aws_region.current.name
}

output "aws_account_id" {
  description = "AWS account ID"
  value       = data.aws_caller_identity.current.account_id
}

output "environment" {
  description = "Environment name"
  value       = var.environment
}

output "project_name" {
  description = "Project name"
  value       = var.project_name
}

# Terraform State Configuration
output "terraform_state_bucket" {
  description = "S3 bucket used for Terraform remote state"
  value       = var.environment == "prod" ? aws_s3_bucket.terraform_state[0].bucket : null
}

output "terraform_state_dynamodb_table" {
  description = "DynamoDB table used for Terraform state locking"
  value       = var.environment == "prod" ? aws_dynamodb_table.terraform_state_lock[0].name : null
}
