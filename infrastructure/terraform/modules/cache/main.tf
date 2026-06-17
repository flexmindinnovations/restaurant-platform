################################################################################
# Subnet & Parameter Groups
################################################################################

resource "aws_elasticache_subnet_group" "main" {
  name       = "${var.project}-${var.environment}-cache-subnet-group"
  subnet_ids = var.private_subnet_ids

  tags = merge(var.tags, {
    Name = "${var.project}-${var.environment}-cache-subnet-group"
  })
}

resource "aws_elasticache_parameter_group" "main" {
  name   = "${var.project}-${var.environment}-cache-pg"
  family = "valkey8"

  tags = merge(var.tags, {
    Name = "${var.project}-${var.environment}-cache-pg"
  })
}

################################################################################
# ElastiCache Valkey Cluster
################################################################################

resource "aws_elasticache_cluster" "main" {
  cluster_id           = "${var.project}-${var.environment}-cache"
  engine               = "valkey"
  engine_version       = "8.0"
  node_type            = var.node_type
  num_cache_nodes      = var.num_cache_nodes
  parameter_group_name = aws_elasticache_parameter_group.main.name
  subnet_group_name    = aws_elasticache_subnet_group.main.name
  security_group_ids   = [var.cache_security_group_id]
  port                 = 6379

  tags = merge(var.tags, {
    Name = "${var.project}-${var.environment}-cache-cluster"
  })
}
