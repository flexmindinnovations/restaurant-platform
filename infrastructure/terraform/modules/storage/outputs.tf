output "assets_bucket_name" {
  description = "Name of the S3 assets bucket"
  value       = aws_s3_bucket.assets.id
}

output "assets_bucket_arn" {
  description = "ARN of the S3 assets bucket"
  value       = aws_s3_bucket.assets.arn
}

output "documents_bucket_name" {
  description = "Name of the S3 documents bucket"
  value       = aws_s3_bucket.documents.id
}

output "documents_bucket_arn" {
  description = "ARN of the S3 documents bucket"
  value       = aws_s3_bucket.documents.arn
}

output "backups_bucket_name" {
  description = "Name of the S3 backups bucket"
  value       = aws_s3_bucket.backups.id
}
