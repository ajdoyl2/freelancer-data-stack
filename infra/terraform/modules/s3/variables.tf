variable "environment" {
  description = "Environment name"
  type        = string
}

variable "project_name" {
  description = "Project name"
  type        = string
}

variable "enable_versioning" {
  description = "Enable versioning on S3 buckets"
  type        = bool
  default     = true
}

variable "lifecycle_rules" {
  description = "S3 lifecycle rules configuration"
  type = map(object({
    enabled                = bool
    transition_days        = number
    transition_class       = string
    expiration_days        = number
    noncurrent_expiration_days = number
  }))
  default = {}
}

variable "allowed_principals" {
  description = "List of AWS principals allowed to access S3 buckets"
  type        = list(string)
  default     = []
}

variable "notification_topic_arn" {
  description = "SNS topic ARN for S3 notifications"
  type        = string
  default     = null
}
