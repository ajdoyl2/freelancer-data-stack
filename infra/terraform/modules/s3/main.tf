resource "random_string" "bucket_suffix" {
  for_each = toset(["data-lake", "artifacts", "logs"])
  length   = 8
  special  = false
  upper    = false
}

# S3 Buckets
resource "aws_s3_bucket" "buckets" {
  for_each = toset(["data-lake", "artifacts", "logs"])
  bucket   = "${var.project_name}-${each.key}-${var.environment}-${random_string.bucket_suffix[each.key].result}"

  tags = {
    Name        = "${var.project_name}-${each.key}-${var.environment}"
    Environment = var.environment
    Project     = var.project_name
    BucketType  = each.key
  }
}

# S3 Bucket Versioning
resource "aws_s3_bucket_versioning" "buckets" {
  for_each = aws_s3_bucket.buckets
  bucket   = each.value.id
  
  versioning_configuration {
    status = var.enable_versioning ? "Enabled" : "Disabled"
  }
}

# S3 Bucket Server-side Encryption
resource "aws_s3_bucket_server_side_encryption_configuration" "buckets" {
  for_each = aws_s3_bucket.buckets
  bucket   = each.value.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# S3 Bucket Public Access Block
resource "aws_s3_bucket_public_access_block" "buckets" {
  for_each = aws_s3_bucket.buckets
  bucket   = each.value.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# S3 Bucket Lifecycle Configuration
resource "aws_s3_bucket_lifecycle_configuration" "buckets" {
  for_each = aws_s3_bucket.buckets
  bucket   = each.value.id

  dynamic "rule" {
    for_each = var.lifecycle_rules
    content {
      id     = rule.key
      status = rule.value.enabled ? "Enabled" : "Disabled"

      transition {
        days          = rule.value.transition_days
        storage_class = rule.value.transition_class
      }

      expiration {
        days = rule.value.expiration_days
      }

      noncurrent_version_expiration {
        noncurrent_days = rule.value.noncurrent_expiration_days
      }
    }
  }
}

# S3 Bucket Policy for Cross-Account Access
resource "aws_s3_bucket_policy" "buckets" {
  for_each = var.allowed_principals != null && length(var.allowed_principals) > 0 ? aws_s3_bucket.buckets : {}
  bucket   = each.value.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "AllowSpecifiedPrincipals"
        Effect = "Allow"
        Principal = {
          AWS = var.allowed_principals
        }
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject",
          "s3:ListBucket"
        ]
        Resource = [
          each.value.arn,
          "${each.value.arn}/*"
        ]
      }
    ]
  })
}

# S3 Bucket Notification for Data Lake (optional)
resource "aws_s3_bucket_notification" "data_lake" {
  count  = contains(keys(aws_s3_bucket.buckets), "data-lake") ? 1 : 0
  bucket = aws_s3_bucket.buckets["data-lake"].id

  # Example: SNS topic notification for new objects
  # You can customize this based on your needs
  dynamic "topic" {
    for_each = var.notification_topic_arn != null ? [1] : []
    content {
      topic_arn = var.notification_topic_arn
      events    = ["s3:ObjectCreated:*"]
    }
  }
}
