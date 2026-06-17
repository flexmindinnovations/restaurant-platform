output "vpc_id" {
  description = "VPC ID"
  value       = aws_vpc.main.id
}

output "public_subnet_ids" {
  description = "Public subnet IDs"
  value       = aws_subnet.public[*].id
}

output "private_subnet_ids" {
  description = "Private subnet IDs"
  value       = aws_subnet.private[*].id
}

output "database_subnet_ids" {
  description = "Database subnet IDs"
  value       = aws_subnet.database[*].id
}

output "alb_security_group_id" {
  description = "ALB Security Group ID"
  value       = aws_security_group.alb.id
}

output "ecs_tasks_security_group_id" {
  description = "ECS tasks Security Group ID"
  value       = aws_security_group.ecs_tasks.id
}

output "database_security_group_id" {
  description = "Database Security Group ID"
  value       = aws_security_group.database.id
}

output "cache_security_group_id" {
  description = "Cache Security Group ID"
  value       = aws_security_group.cache.id
}
