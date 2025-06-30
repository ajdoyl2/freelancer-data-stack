variable "environment" {
  description = "Environment name"
  type        = string
}

variable "project_name" {
  description = "Project name"
  type        = string
}

variable "secrets" {
  description = "Configuration for secrets to be stored in AWS Secrets Manager"
  type = map(object({
    description = string
    secret_string = string
    recovery_window_in_days = number
  }))
  default = {}
}

# Optional common secrets variables
variable "snowflake_account" {
  description = "Snowflake account identifier"
  type        = string
  default     = null
  sensitive   = true
}

variable "snowflake_username" {
  description = "Snowflake username"
  type        = string
  default     = null
  sensitive   = true
}

variable "snowflake_password" {
  description = "Snowflake password"
  type        = string
  default     = null
  sensitive   = true
}

variable "snowflake_role" {
  description = "Snowflake role"
  type        = string
  default     = null
}

variable "snowflake_database" {
  description = "Snowflake database name"
  type        = string
  default     = null
}

variable "snowflake_warehouse" {
  description = "Snowflake warehouse name"
  type        = string
  default     = null
}

variable "external_api_key" {
  description = "External API key"
  type        = string
  default     = null
  sensitive   = true
}

variable "webhook_secret" {
  description = "Webhook secret"
  type        = string
  default     = null
  sensitive   = true
}

variable "postgres_url" {
  description = "PostgreSQL connection URL"
  type        = string
  default     = null
  sensitive   = true
}

variable "redis_url" {
  description = "Redis connection URL"
  type        = string
  default     = null
  sensitive   = true
}
