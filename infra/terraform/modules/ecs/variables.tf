variable "environment" {
  description = "Environment name"
  type        = string
}

variable "project_name" {
  description = "Project name"
  type        = string
}

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

variable "task_definitions" {
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

variable "service_configurations" {
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
