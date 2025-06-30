output "bucket_names" {
  description = "Names of the S3 buckets created"
  value       = { for k, v in aws_s3_bucket.buckets : k => v.bucket }
}

output "bucket_arns" {
  description = "ARNs of the S3 buckets created"
  value       = { for k, v in aws_s3_bucket.buckets : k => v.arn }
}

output "bucket_ids" {
  description = "IDs of the S3 buckets created"
  value       = { for k, v in aws_s3_bucket.buckets : k => v.id }
}

output "data_lake_bucket_name" {
  description = "Name of the data lake S3 bucket"
  value       = aws_s3_bucket.buckets["data-lake"].bucket
}

output "artifacts_bucket_name" {
  description = "Name of the artifacts S3 bucket"
  value       = aws_s3_bucket.buckets["artifacts"].bucket
}

output "logs_bucket_name" {
  description = "Name of the logs S3 bucket"
  value       = aws_s3_bucket.buckets["logs"].bucket
}
