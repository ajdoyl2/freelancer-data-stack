# AWS Secrets Manager Secrets
resource "aws_secretsmanager_secret" "secrets" {
  for_each = var.secrets

  name                    = "${var.project_name}/${var.environment}/${each.key}"
  description             = each.value.description
  recovery_window_in_days = each.value.recovery_window_in_days

  tags = {
    Name        = "${var.project_name}-${each.key}-${var.environment}"
    Environment = var.environment
    Project     = var.project_name
    SecretType  = each.key
  }
}

# AWS Secrets Manager Secret Versions
resource "aws_secretsmanager_secret_version" "secrets" {
  for_each = var.secrets

  secret_id     = aws_secretsmanager_secret.secrets[each.key].id
  secret_string = each.value.secret_string
}

# Common secrets for the data stack
locals {
  default_secrets = var.environment == "local" ? {} : {
    "snowflake-credentials" = {
      description = "Snowflake database credentials"
      secret_string = jsonencode({
        account  = var.snowflake_account
        username = var.snowflake_username
        password = var.snowflake_password
        role     = var.snowflake_role
        database = var.snowflake_database
        warehouse = var.snowflake_warehouse
      })
      recovery_window_in_days = 7
    }
    
    "api-keys" = {
      description = "API keys for external services"
      secret_string = jsonencode({
        external_api_key = var.external_api_key
        webhook_secret   = var.webhook_secret
      })
      recovery_window_in_days = 7
    }
    
    "database-urls" = {
      description = "Database connection URLs"
      secret_string = jsonencode({
        postgres_url = var.postgres_url
        redis_url    = var.redis_url
      })
      recovery_window_in_days = 7
    }
  }
}

# Default secrets (only created if corresponding variables are provided)
resource "aws_secretsmanager_secret" "default_secrets" {
  for_each = {
    for k, v in local.default_secrets : k => v
    if v.secret_string != "null" && v.secret_string != ""
  }

  name                    = "${var.project_name}/${var.environment}/${each.key}"
  description             = each.value.description
  recovery_window_in_days = each.value.recovery_window_in_days

  tags = {
    Name        = "${var.project_name}-${each.key}-${var.environment}"
    Environment = var.environment
    Project     = var.project_name
    SecretType  = each.key
    Managed     = "terraform"
  }
}

resource "aws_secretsmanager_secret_version" "default_secrets" {
  for_each = aws_secretsmanager_secret.default_secrets

  secret_id     = each.value.id
  secret_string = local.default_secrets[each.key].secret_string
}

# IAM policy for accessing secrets
resource "aws_iam_policy" "secrets_access" {
  name        = "${var.project_name}-secrets-access-${var.environment}"
  description = "Policy for accessing ${var.project_name} secrets in ${var.environment}"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue",
          "secretsmanager:DescribeSecret"
        ]
        Resource = [
          for secret in aws_secretsmanager_secret.secrets : secret.arn
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue",
          "secretsmanager:DescribeSecret"
        ]
        Resource = [
          for secret in aws_secretsmanager_secret.default_secrets : secret.arn
        ]
      }
    ]
  })

  tags = {
    Name        = "${var.project_name}-secrets-access-${var.environment}"
    Environment = var.environment
    Project     = var.project_name
  }
}
