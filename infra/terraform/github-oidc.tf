# GitHub OIDC Provider
data "aws_iam_openid_connect_provider" "github" {
  count = var.environment == "prod" ? 1 : 0
  url   = "https://token.actions.githubusercontent.com"
}

resource "aws_iam_openid_connect_provider" "github" {
  count = var.environment == "prod" && length(data.aws_iam_openid_connect_provider.github) == 0 ? 1 : 0
  
  url = "https://token.actions.githubusercontent.com"
  
  client_id_list = [
    "sts.amazonaws.com",
  ]
  
  thumbprint_list = [
    "6938fd4d98bab03faadb97b34396831e3780aea1",
    "1c58a3a8518e8759bf075b76b750d4f2df264fcd"
  ]

  tags = {
    Name        = "${var.project_name}-github-oidc-${var.environment}"
    Environment = var.environment
    Project     = var.project_name
  }
}

# GitHub OIDC IAM Role
resource "aws_iam_role" "github_oidc" {
  name = "${var.project_name}-github-oidc-${var.environment}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRoleWithWebIdentity"
        Effect = "Allow"
        Principal = {
          Federated = var.environment == "prod" && length(data.aws_iam_openid_connect_provider.github) > 0 ? 
                     data.aws_iam_openid_connect_provider.github[0].arn : 
                     (var.environment == "prod" ? aws_iam_openid_connect_provider.github[0].arn : "")
        }
        Condition = {
          StringEquals = {
            "token.actions.githubusercontent.com:aud" = "sts.amazonaws.com"
          }
          StringLike = {
            "token.actions.githubusercontent.com:sub" = "repo:*/${var.project_name}:*"
          }
        }
      }
    ]
  })

  tags = {
    Name        = "${var.project_name}-github-oidc-${var.environment}"
    Environment = var.environment
    Project     = var.project_name
  }
}

# GitHub OIDC IAM Role Policy
resource "aws_iam_role_policy" "github_oidc" {
  name = "${var.project_name}-github-oidc-policy-${var.environment}"
  role = aws_iam_role.github_oidc.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      # ECR permissions
      {
        Effect = "Allow"
        Action = [
          "ecr:GetAuthorizationToken",
          "ecr:BatchCheckLayerAvailability",
          "ecr:GetDownloadUrlForLayer",
          "ecr:BatchGetImage",
          "ecr:BatchImportLayer",
          "ecr:PutImage",
          "ecr:InitiateLayerUpload",
          "ecr:UploadLayerPart",
          "ecr:CompleteLayerUpload"
        ]
        Resource = "*"
      },
      # ECS permissions for deployments
      {
        Effect = "Allow"
        Action = [
          "ecs:UpdateService",
          "ecs:DescribeServices",
          "ecs:DescribeTaskDefinition",
          "ecs:RegisterTaskDefinition",
          "ecs:ListTasks",
          "ecs:DescribeTasks"
        ]
        Resource = "*"
      },
      # S3 permissions for artifacts and state
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject",
          "s3:ListBucket"
        ]
        Resource = [
          "arn:aws:s3:::${var.project_name}-*",
          "arn:aws:s3:::${var.project_name}-*/*"
        ]
      },
      # Secrets Manager permissions
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue",
          "secretsmanager:DescribeSecret"
        ]
        Resource = "arn:aws:secretsmanager:*:*:secret:${var.project_name}/*"
      },
      # DynamoDB permissions for state locking
      {
        Effect = "Allow"
        Action = [
          "dynamodb:GetItem",
          "dynamodb:PutItem",
          "dynamodb:DeleteItem"
        ]
        Resource = "arn:aws:dynamodb:*:*:table/${var.project_name}-terraform-state-lock-*"
      }
    ]
  })
}

# Terraform State S3 Bucket (only for prod)
resource "aws_s3_bucket" "terraform_state" {
  count  = var.environment == "prod" ? 1 : 0
  bucket = "${var.project_name}-terraform-state-${var.environment}-${random_string.bucket_suffix[0].result}"

  tags = {
    Name        = "${var.project_name}-terraform-state-${var.environment}"
    Environment = var.environment
    Project     = var.project_name
  }
}

resource "random_string" "bucket_suffix" {
  count   = var.environment == "prod" ? 1 : 0
  length  = 8
  special = false
  upper   = false
}

resource "aws_s3_bucket_versioning" "terraform_state" {
  count  = var.environment == "prod" ? 1 : 0
  bucket = aws_s3_bucket.terraform_state[0].id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "terraform_state" {
  count  = var.environment == "prod" ? 1 : 0
  bucket = aws_s3_bucket.terraform_state[0].id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "terraform_state" {
  count  = var.environment == "prod" ? 1 : 0
  bucket = aws_s3_bucket.terraform_state[0].id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# DynamoDB Table for State Locking (only for prod)
resource "aws_dynamodb_table" "terraform_state_lock" {
  count          = var.environment == "prod" ? 1 : 0
  name           = "${var.project_name}-terraform-state-lock-${var.environment}"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "LockID"

  attribute {
    name = "LockID"
    type = "S"
  }

  tags = {
    Name        = "${var.project_name}-terraform-state-lock-${var.environment}"
    Environment = var.environment
    Project     = var.project_name
  }
}
