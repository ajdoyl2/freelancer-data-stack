# General Variables
variable "environment" {
  description = "Environment name (local, prod, etc.)"
  type        = string
}

variable "project_name" {
  description = "Name of the project"
  type        = string
  default     = "freelancer-data-stack"
}

variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "ca-central-1"
}

# S3 Variables
variable "s3_enable_versioning" {
  description = "Enable versioning on S3 buckets"
  type        = bool
  default     = true
}

variable "s3_lifecycle_rules" {
  description = "S3 lifecycle rules configuration"
  type = map(object({
    enabled                = bool
    transition_days        = number
    transition_class       = string
    expiration_days        = number
    noncurrent_expiration_days = number
  }))
  default = {
    standard_ia = {
      enabled                = true
      transition_days        = 30
      transition_class       = "STANDARD_IA"
      expiration_days        = 365
      noncurrent_expiration_days = 90
    }
  }
}

variable "s3_allowed_principals" {
  description = "List of AWS principals allowed to access S3 buckets"
  type        = list(string)
  default     = []
}

# Snowflake Variables
variable "snowflake_account" {
  description = "Snowflake account identifier"
  type        = string
  sensitive   = true
}

variable "snowflake_username" {
  description = "Snowflake username"
  type        = string
  sensitive   = true
}

variable "snowflake_password" {
  description = "Snowflake password"
  type        = string
  sensitive   = true
}

variable "snowflake_role" {
  description = "Snowflake role"
  type        = string
  default     = "SYSADMIN"
}

variable "snowflake_database_name" {
  description = "Snowflake database name"
  type        = string
  default     = "FREELANCER_DATA"
}

variable "snowflake_warehouse_size" {
  description = "Snowflake warehouse size"
  type        = string
  default     = "X-SMALL"
}

variable "snowflake_auto_suspend" {
  description = "Auto suspend time in seconds for Snowflake warehouse"
  type        = number
  default     = 300
}

# ECR Variables
variable "ecr_repositories" {
  description = "List of ECR repositories to create"
  type        = list(string)
  default     = ["ingestion", "transformation", "orchestration", "api"]
}

variable "ecr_scan_on_push" {
  description = "Enable image scanning on push"
  type        = bool
  default     = true
}

variable "ecr_lifecycle_policy" {
  description = "ECR lifecycle policy configuration"
  type = object({
    max_images     = number
    max_age_days   = number
    tag_status     = string
  })
  default = {
    max_images   = 10
    max_age_days = 30
    tag_status   = "untagged"
  }
}

# ECS Variables
variable "vpc_id" {
  description = "VPC ID for ECS resources"
  type        = string
  default     = ""
}

variable "subnet_ids" {
  description = "Subnet IDs for ECS services"
  type        = list(string)
  default     = []
}

variable "ecs_task_definitions" {
  description = "ECS task definitions configuration"
  type = map(object({
    cpu    = number
    memory = number
    image  = string
    environment_variables = map(string)
    secrets = map(string)
  }))
  default = {}
}

variable "ecs_service_configurations" {
  description = "ECS service configurations"
  type = map(object({
    desired_count = number
    task_definition_name = string
    enable_autoscaling = bool
    min_capacity = number
    max_capacity = number
  }))
  default = {}
}

# Secrets Manager Variables
variable "secrets_config" {
  description = "Configuration for secrets to be stored in AWS Secrets Manager"
  type = map(object({
    description = string
    secret_string = string
    recovery_window_in_days = number
  }))
  default = {}
}
