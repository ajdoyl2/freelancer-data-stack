output "cluster_name" {
  description = "Name of the ECS cluster"
  value       = aws_ecs_cluster.main.name
}

output "cluster_arn" {
  description = "ARN of the ECS cluster"
  value       = aws_ecs_cluster.main.arn
}

output "cluster_id" {
  description = "ID of the ECS cluster"
  value       = aws_ecs_cluster.main.id
}

output "service_names" {
  description = "Names of the ECS services"
  value       = { for k, v in aws_ecs_service.services : k => v.name }
}

output "service_arns" {
  description = "ARNs of the ECS services"
  value       = { for k, v in aws_ecs_service.services : k => v.id }
}

output "task_definition_arns" {
  description = "ARNs of the ECS task definitions"
  value       = { for k, v in aws_ecs_task_definition.tasks : k => v.arn }
}

output "security_group_id" {
  description = "ID of the ECS security group"
  value       = aws_security_group.ecs_tasks.id
}

output "cloudwatch_log_group_name" {
  description = "Name of the CloudWatch log group"
  value       = aws_cloudwatch_log_group.ecs.name
}

output "task_execution_role_arn" {
  description = "ARN of the ECS task execution role"
  value       = aws_iam_role.ecs_task_execution_role.arn
}

output "task_role_arn" {
  description = "ARN of the ECS task role"
  value       = aws_iam_role.ecs_task_role.arn
}
