variable "project" {
  description = "Project name"
  type        = string
  default     = "restaurant-platform"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "staging"
}

variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
  default     = "10.1.0.0/16"
}

variable "availability_zones" {
  description = "List of availability zones"
  type        = list(string)
  default     = ["us-east-1a", "us-east-1b"]
}

variable "db_password" {
  description = "Password for database admin — must be provided via tfvars or TF_VAR_db_password"
  type        = string
  sensitive   = true
}

variable "domain_name" {
  description = "Domain name for the platform"
  type        = string
  default     = "staging.flexmindinnovations.com"
}
