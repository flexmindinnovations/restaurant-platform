variable "project" {
  description = "Project name"
  type        = string
}

variable "environment" {
  description = "Environment name"
  type        = string
}

variable "vpc_id" {
  description = "VPC ID where database resources will be created"
  type        = string
}

variable "database_subnet_ids" {
  description = "List of database subnet IDs"
  type        = list(string)
}

variable "database_security_group_id" {
  description = "Security Group ID for RDS Database access"
  type        = string
}

variable "allocated_storage" {
  description = "Allocated storage size in GB"
  type        = number
  default     = 20
}

variable "max_allocated_storage" {
  description = "Maximum storage size in GB for autoscaling"
  type        = number
  default     = 100
}

variable "instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.t4g.micro"
}

variable "db_name" {
  description = "Database name"
  type        = string
  default     = "restaurant_platform"
}

variable "db_username" {
  description = "Username for database admin"
  type        = string
  default     = "platform"
}

variable "db_password" {
  description = "Password for database admin"
  type        = string
  sensitive   = true
}

variable "force_ssl" {
  description = "Enforce SSL connections to the database"
  type        = bool
  default     = true
}

variable "multi_az" {
  description = "Enable Multi-AZ deployment"
  type        = bool
  default     = false
}

variable "tags" {
  description = "Common resource tags"
  type        = map(string)
  default     = {}
}
