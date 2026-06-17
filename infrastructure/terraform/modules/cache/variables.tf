variable "project" {
  description = "Project name"
  type        = string
}

variable "environment" {
  description = "Environment name"
  type        = string
}

variable "vpc_id" {
  description = "VPC ID where cache resources will be created"
  type        = string
}

variable "private_subnet_ids" {
  description = "List of private subnet IDs for ElastiCache"
  type        = list(string)
}

variable "cache_security_group_id" {
  description = "Security Group ID for ElastiCache access"
  type        = string
}

variable "node_type" {
  description = "Cache node type"
  type        = string
  default     = "cache.t4g.micro"
}

variable "num_cache_nodes" {
  description = "Number of cache nodes"
  type        = number
  default     = 1
}

variable "tags" {
  description = "Common resource tags"
  type        = map(string)
  default     = {}
}
