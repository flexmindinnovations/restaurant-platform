output "cache_endpoint" {
  description = "Connection endpoint of the Valkey cache"
  value       = aws_elasticache_cluster.main.cache_nodes[0].address
}

output "cache_port" {
  description = "Port of the Valkey cache"
  value       = aws_elasticache_cluster.main.cache_nodes[0].port
}
