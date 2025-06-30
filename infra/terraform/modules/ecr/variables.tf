variable "environment" {
  description = "Environment name"
  type        = string
}

variable "project_name" {
  description = "Project name"
  type        = string
}

variable "repositories" {
  description = "List of ECR repositories to create"
  type        = list(string)
  default     = ["ingestion", "transformation", "orchestration", "api"]
}

variable "scan_on_push" {
  description = "Enable image scanning on push"
  type        = bool
  default     = true
}

variable "lifecycle_policy" {
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

variable "allowed_principals" {
  description = "List of AWS principals allowed to pull from ECR repositories"
  type        = list(string)
  default     = []
}
