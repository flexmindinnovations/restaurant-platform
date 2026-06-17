output "cloudfront_domain_name" {
  description = "Domain name of the CloudFront distribution"
  value       = aws_cloudfront_distribution.assets.domain_name
}

output "cloudfront_distribution_id" {
  description = "ID of the CloudFront distribution"
  value       = aws_cloudfront_distribution.assets.id
}

output "cloudfront_arn" {
  description = "ARN of the CloudFront distribution"
  value       = aws_cloudfront_distribution.assets.arn
}
