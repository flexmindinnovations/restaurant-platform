variable "project" {
  description = "Project name"
  type        = string
}

variable "environment" {
  description = "Environment name"
  type        = string
}

variable "assets_bucket_name" {
  description = "Name of the S3 assets bucket"
  type        = string
}

variable "assets_bucket_arn" {
  description = "ARN of the S3 assets bucket"
  type        = string
}

variable "tags" {
  description = "Common resource tags"
  type        = map(string)
  default     = {}
}
