output "vpc_id" {
  description = "VPC ID"
  value       = module.networking.vpc_id
}

output "public_subnet_ids" {
  description = "Public subnet IDs"
  value       = module.networking.public_subnet_ids
}

output "private_subnet_ids" {
  description = "Private subnet IDs"
  value       = module.networking.private_subnet_ids
}

output "alb_dns_name" {
  description = "DNS name of the Application Load Balancer"
  value       = module.compute.alb_dns_name
}

output "cloudfront_domain_name" {
  description = "Domain name of the CloudFront distribution"
  value       = module.cdn.cloudfront_domain_name
}

output "db_hostname" {
  description = "Hostname of the RDS Database"
  value       = module.database.db_hostname
}

output "cache_endpoint" {
  description = "Endpoint of the Valkey cache"
  value       = module.cache.cache_endpoint
}

output "dns_name_servers" {
  description = "Route 53 Hosted Zone Name Servers"
  value       = module.dns.name_servers
}
