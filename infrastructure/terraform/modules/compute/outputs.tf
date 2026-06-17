output "alb_dns_name" {
  description = "DNS name of the Application Load Balancer"
  value       = aws_lb.api.dns_name
}

output "alb_zone_id" {
  description = "Zone ID of the Application Load Balancer"
  value       = aws_lb.api.zone_id
}

output "ecs_cluster_name" {
  description = "Name of the ECS Cluster"
  value       = aws_ecs_cluster.main.name
}

output "ecs_cluster_id" {
  description = "ID of the ECS Cluster"
  value       = aws_ecs_cluster.main.id
}

output "api_service_name" {
  description = "Name of the API ECS Service"
  value       = aws_ecs_service.api.name
}

output "worker_service_name" {
  description = "Name of the Worker ECS Service"
  value       = aws_ecs_service.worker.name
}

output "beat_service_name" {
  description = "Name of the Beat ECS Service"
  value       = aws_ecs_service.beat.name
}

output "alb_arn_suffix" {
  description = "ARN suffix of the Application Load Balancer"
  value       = aws_lb.api.arn_suffix
}


