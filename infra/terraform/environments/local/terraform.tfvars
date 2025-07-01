# Local Environment Configuration
environment = "local"

# Snowflake Configuration (local development)
# Note: For validation testing, using placeholder values
# Replace with real values when ready to deploy
snowflake_account      = "placeholder-account"
snowflake_username     = "placeholder-username"
snowflake_password     = "placeholder-password"
snowflake_role         = "SYSADMIN"
snowflake_database_name = "FREELANCER_DATA_LOCAL"
snowflake_warehouse_size = "X-SMALL"
snowflake_auto_suspend = 60

# S3 Configuration
s3_enable_versioning = false
s3_lifecycle_rules = {
  standard_ia = {
    enabled                = true
    transition_days        = 30
    transition_class       = "STANDARD_IA"
    expiration_days        = 90
    noncurrent_expiration_days = 30
  }
}

# ECR Configuration
ecr_repositories = ["ingestion", "transformation", "orchestration", "api"]
ecr_scan_on_push = true
ecr_lifecycle_policy = {
  max_images   = 5
  max_age_days = 7
  tag_status   = "untagged"
}

# ECS Configuration (minimal for local testing)
ecs_task_definitions = {
  api = {
    cpu    = 256
    memory = 512
    image  = "nginx:latest"
    environment_variables = {
      ENV = "local"
    }
    secrets = {}
  }
}

ecs_service_configurations = {
  api = {
    desired_count = 1
    task_definition_name = "api"
    enable_autoscaling = false
    min_capacity = 1
    max_capacity = 2
  }
}
