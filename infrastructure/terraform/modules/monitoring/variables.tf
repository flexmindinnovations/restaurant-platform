variable "project" {
  description = "Project name"
  type        = string
}

variable "environment" {
  description = "Environment name"
  type        = string
}

variable "ecs_cluster_name" {
  description = "Name of the ECS Cluster"
  type        = string
}

variable "api_service_name" {
  description = "Name of the API ECS Service"
  type        = string
}

variable "worker_service_name" {
  description = "Name of the Worker ECS Service"
  type        = string
}

variable "beat_service_name" {
  description = "Name of the Beat ECS Service"
  type        = string
}

variable "alb_arn_suffix" {
  description = "ARN suffix of the ALB (for CloudWatch metrics)"
  type        = string
}

variable "db_instance_identifier" {
  description = "Identifier of the RDS Database"
  type        = string
}

variable "tags" {
  description = "Common resource tags"
  type        = map(string)
  default     = {}
}
