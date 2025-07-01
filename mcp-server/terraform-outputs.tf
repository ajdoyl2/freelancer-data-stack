# Terraform outputs for MCP Server

output "mcp_server_service_name" {
  description = "Name of the MCP Server Kubernetes service"
  value       = "mcp-server"
}

output "mcp_server_namespace" {
  description = "Namespace where MCP Server is deployed"
  value       = var.mcp_server_namespace
}

output "mcp_server_endpoint" {
  description = "MCP Server endpoint URL"
  value       = "http://${var.mcp_server_service_name}.${var.mcp_server_namespace}.svc.cluster.local"
}

output "mcp_server_port" {
  description = "MCP Server port"
  value       = 80
}

output "mcp_server_graphql_endpoint" {
  description = "MCP Server GraphQL endpoint"
  value       = "http://${var.mcp_server_service_name}.${var.mcp_server_namespace}.svc.cluster.local/graphql"
}

output "mcp_server_websocket_endpoint" {
  description = "MCP Server WebSocket endpoint"
  value       = "ws://${var.mcp_server_service_name}.${var.mcp_server_namespace}.svc.cluster.local/ws"
}

output "mcp_server_health_endpoint" {
  description = "MCP Server health check endpoint"
  value       = "http://${var.mcp_server_service_name}.${var.mcp_server_namespace}.svc.cluster.local/health"
}

# Variables
variable "mcp_server_namespace" {
  description = "Kubernetes namespace for MCP Server"
  type        = string
  default     = "default"
}

variable "mcp_server_service_name" {
  description = "Kubernetes service name for MCP Server"
  type        = string
  default     = "mcp-server"
}

# Helm release resource
resource "helm_release" "mcp_server" {
  name       = "mcp-server"
  chart      = "./helm/mcp-server"
  namespace  = var.mcp_server_namespace
  
  values = [
    file("${path.module}/helm/mcp-server/values.yaml")
  ]

  set {
    name  = "image.repository"
    value = var.mcp_server_image_repository
  }

  set {
    name  = "image.tag"
    value = var.mcp_server_image_tag
  }

  depends_on = [
    kubernetes_namespace.mcp_server
  ]
}

resource "kubernetes_namespace" "mcp_server" {
  metadata {
    name = var.mcp_server_namespace
    labels = {
      name = var.mcp_server_namespace
      app  = "mcp-server"
    }
  }
}

variable "mcp_server_image_repository" {
  description = "Docker image repository for MCP Server"
  type        = string
  default     = "mcp-server"
}

variable "mcp_server_image_tag" {
  description = "Docker image tag for MCP Server"
  type        = string
  default     = "latest"
}
