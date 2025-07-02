# Production Environment Configuration
environment = "prod"

# Snowflake Configuration (production)
snowflake_account      = "your-prod-snowflake-account"
snowflake_username     = "your-prod-snowflake-username"
snowflake_password     = "your-prod-snowflake-password"
snowflake_role         = "SYSADMIN"
snowflake_database_name = "FREELANCER_DATA_PROD"
snowflake_warehouse_size = "SMALL"
snowflake_auto_suspend = 300

# S3 Configuration
s3_enable_versioning = true
s3_lifecycle_rules = {
  standard_ia = {
    enabled                = true
    transition_days        = 30
    transition_class       = "STANDARD_IA"
    expiration_days        = 365
    noncurrent_expiration_days = 90
  }
  glacier = {
    enabled                = true
    transition_days        = 90
    transition_class       = "GLACIER"
    expiration_days        = 2555 # 7 years
    noncurrent_expiration_days = 365
  }
}

# ECR Configuration
ecr_repositories = ["ingestion", "transformation", "orchestration", "api"]
ecr_scan_on_push = true
ecr_lifecycle_policy = {
  max_images   = 20
  max_age_days = 30
  tag_status   = "untagged"
}

# ECS Configuration (production scale)
ecs_task_definitions = {
  ingestion = {
    cpu    = 512
    memory = 1024
    image  = "your-account.dkr.ecr.ca-central-1.amazonaws.com/freelancer-data-stack-ingestion-prod:latest"
    environment_variables = {
      ENV = "prod"
      LOG_LEVEL = "INFO"
    }
    secrets = {
      SNOWFLAKE_PASSWORD = "arn:aws:secretsmanager:ca-central-1:your-account:secret:freelancer-data-stack/prod/snowflake-credentials"
      API_KEY = "arn:aws:secretsmanager:ca-central-1:your-account:secret:freelancer-data-stack/prod/api-keys"
    }
  }

  transformation = {
    cpu    = 1024
    memory = 2048
    image  = "your-account.dkr.ecr.ca-central-1.amazonaws.com/freelancer-data-stack-transformation-prod:latest"
    environment_variables = {
      ENV = "prod"
      LOG_LEVEL = "INFO"
    }
    secrets = {
      SNOWFLAKE_PASSWORD = "arn:aws:secretsmanager:ca-central-1:your-account:secret:freelancer-data-stack/prod/snowflake-credentials"
    }
  }

  orchestration = {
    cpu    = 512
    memory = 1024
    image  = "your-account.dkr.ecr.ca-central-1.amazonaws.com/freelancer-data-stack-orchestration-prod:latest"
    environment_variables = {
      ENV = "prod"
      LOG_LEVEL = "INFO"
    }
    secrets = {
      SNOWFLAKE_PASSWORD = "arn:aws:secretsmanager:ca-central-1:your-account:secret:freelancer-data-stack/prod/snowflake-credentials"
    }
  }

  api = {
    cpu    = 512
    memory = 1024
    image  = "your-account.dkr.ecr.ca-central-1.amazonaws.com/freelancer-data-stack-api-prod:latest"
    environment_variables = {
      ENV = "prod"
      LOG_LEVEL = "INFO"
    }
    secrets = {
      SNOWFLAKE_PASSWORD = "arn:aws:secretsmanager:ca-central-1:your-account:secret:freelancer-data-stack/prod/snowflake-credentials"
      API_KEY = "arn:aws:secretsmanager:ca-central-1:your-account:secret:freelancer-data-stack/prod/api-keys"
    }
  }
}

ecs_service_configurations = {
  ingestion = {
    desired_count = 2
    task_definition_name = "ingestion"
    enable_autoscaling = true
    min_capacity = 1
    max_capacity = 5
  }

  transformation = {
    desired_count = 1
    task_definition_name = "transformation"
    enable_autoscaling = true
    min_capacity = 1
    max_capacity = 3
  }

  orchestration = {
    desired_count = 1
    task_definition_name = "orchestration"
    enable_autoscaling = false
    min_capacity = 1
    max_capacity = 2
  }

  api = {
    desired_count = 2
    task_definition_name = "api"
    enable_autoscaling = true
    min_capacity = 2
    max_capacity = 10
  }
}
