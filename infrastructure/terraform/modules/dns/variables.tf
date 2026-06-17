variable "project" {
  description = "Project name"
  type        = string
  default     = "restaurant-platform"
}

variable "environment" {
  description = "Environment name"
  type        = string
}

variable "domain_name" {
  description = "Primary domain name for the platform"
  type        = string
}

variable "alb_dns_name" {
  description = "DNS name of the Application Load Balancer"
  type        = string
}

variable "alb_zone_id" {
  description = "Zone ID of the Application Load Balancer"
  type        = string
}

variable "cloudfront_domain_name" {
  description = "Domain name of the CloudFront distribution"
  type        = string
}

variable "cloudfront_hosted_zone_id" {
  description = "Hosted zone ID for CloudFront (typically Z2FDTNDATAQYW2)"
  type        = string
  default     = "Z2FDTNDATAQYW2"
}

variable "tags" {
  description = "Common tags for all resources"
  type        = map(string)
  default     = {}
}
