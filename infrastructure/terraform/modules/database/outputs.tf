output "db_endpoint" {
  description = "Connection endpoint for the RDS database"
  value       = aws_db_instance.main.endpoint
}

output "db_hostname" {
  description = "Hostname for the database"
  value       = aws_db_instance.main.address
}

output "db_port" {
  description = "Port number of the database"
  value       = aws_db_instance.main.port
}

output "db_instance_identifier" {
  description = "The database instance identifier"
  value       = aws_db_instance.main.identifier
}

