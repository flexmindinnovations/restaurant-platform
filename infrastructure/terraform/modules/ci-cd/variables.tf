variable "project" {
  description = "Project name"
  type        = string
}

variable "environment" {
  description = "Environment name"
  type        = string
}

variable "github_org" {
  description = "GitHub Organization name"
  type        = string
  default     = "flexmindinnovations"
}

variable "github_repo" {
  description = "GitHub Repository name"
  type        = string
  default     = "restaurant-platform"
}

variable "tags" {
  description = "Common resource tags"
  type        = map(string)
  default     = {}
}
