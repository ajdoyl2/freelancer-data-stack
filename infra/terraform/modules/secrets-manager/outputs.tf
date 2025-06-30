output "secret_arns" {
  description = "ARNs of the secrets in AWS Secrets Manager"
  value = merge(
    { for k, v in aws_secretsmanager_secret.secrets : k => v.arn },
    { for k, v in aws_secretsmanager_secret.default_secrets : k => v.arn }
  )
  sensitive = true
}

output "secret_names" {
  description = "Names of the secrets in AWS Secrets Manager"
  value = merge(
    { for k, v in aws_secretsmanager_secret.secrets : k => v.name },
    { for k, v in aws_secretsmanager_secret.default_secrets : k => v.name }
  )
}

output "secrets_access_policy_arn" {
  description = "ARN of the IAM policy for accessing secrets"
  value       = aws_iam_policy.secrets_access.arn
}

output "secrets_access_policy_name" {
  description = "Name of the IAM policy for accessing secrets"
  value       = aws_iam_policy.secrets_access.name
}
