variable "project" {
  description = "Project name"
  type        = string
}

variable "environment" {
  description = "Environment name"
  type        = string
}

variable "vpc_id" {
  description = "VPC ID where resources will be created"
  type        = string
}

variable "public_subnet_ids" {
  description = "List of public subnet IDs for ALB"
  type        = list(string)
}

variable "private_subnet_ids" {
  description = "List of private subnet IDs for ECS tasks"
  type        = list(string)
}

variable "ecs_tasks_security_group_id" {
  description = "Security Group ID for ECS Tasks"
  type        = string
}

variable "alb_security_group_id" {
  description = "Security Group ID for ALB"
  type        = string
}

variable "ecs_task_execution_role_arn" {
  description = "IAM Role ARN for ECS Task Execution"
  type        = string
}

variable "ecs_task_role_arn" {
  description = "IAM Role ARN for ECS Task"
  type        = string
}

variable "container_port" {
  description = "Port exposed by the FastAPI container"
  type        = number
  default     = 8000
}

variable "api_cpu" {
  description = "Fargate instance CPU units for API"
  type        = string
  default     = "256"
}

variable "api_memory" {
  description = "Fargate instance memory for API"
  type        = string
  default     = "512"
}

variable "worker_cpu" {
  description = "Fargate instance CPU units for worker"
  type        = string
  default     = "256"
}

variable "worker_memory" {
  description = "Fargate instance memory for worker"
  type        = string
  default     = "512"
}

variable "api_image" {
  description = "ECR image URI for API"
  type        = string
  default     = "123456789012.dkr.ecr.us-east-1.amazonaws.com/api:latest"
}

variable "worker_image" {
  description = "ECR image URI for worker"
  type        = string
  default     = "123456789012.dkr.ecr.us-east-1.amazonaws.com/worker:latest"
}

variable "certificate_arn" {
  description = "ACM certificate ARN for HTTPS. Empty string disables HTTPS and forwards HTTP directly."
  type        = string
  default     = ""
}

variable "tags" {
  description = "Common resource tags"
  type        = map(string)
  default     = {}
}
