variable "environment" {
  description = "Environment name"
  type        = string
}

variable "project_name" {
  description = "Project name"
  type        = string
}

variable "database_name" {
  description = "Snowflake database name"
  type        = string
}

variable "warehouse_size" {
  description = "Snowflake warehouse size"
  type        = string
  default     = "X-SMALL"
}

variable "auto_suspend" {
  description = "Auto suspend time in seconds for Snowflake warehouse"
  type        = number
  default     = 300
}

variable "schemas" {
  description = "List of schemas to create"
  type        = list(string)
  default     = ["RAW", "CLEAN", "ANALYTICS", "MARTS"]
}
