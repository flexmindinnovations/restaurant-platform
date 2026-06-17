output "zone_id" {
  description = "The Route 53 Hosted Zone ID"
  value       = aws_route53_zone.primary.zone_id
}

output "name_servers" {
  description = "The Route 53 Name Servers"
  value       = aws_route53_zone.primary.name_servers
}

output "api_dns_name" {
  description = "The API subdomain DNS record name"
  value       = aws_route53_record.api.name
}

output "web_dns_name" {
  description = "The Web apex domain DNS record name"
  value       = aws_route53_record.apex.name
}
