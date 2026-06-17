output "api_ecr_repository_url" {
  description = "URL of the API ECR repository"
  value       = aws_ecr_repository.api.repository_url
}

output "worker_ecr_repository_url" {
  description = "URL of the Worker ECR repository"
  value       = aws_ecr_repository.worker.repository_url
}

output "frontend_ecr_repository_url" {
  description = "URL of the Frontend ECR repository"
  value       = aws_ecr_repository.frontend.repository_url
}

output "github_actions_role_arn" {
  description = "ARN of the IAM role assumed by GitHub Actions"
  value       = aws_iam_role.github_actions.arn
}
