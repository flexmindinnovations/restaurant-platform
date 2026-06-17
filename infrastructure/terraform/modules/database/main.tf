################################################################################
# Subnet & Parameter Groups
################################################################################

resource "aws_db_subnet_group" "main" {
  name       = "${var.project}-${var.environment}-db-subnet-group"
  subnet_ids = var.database_subnet_ids

  tags = merge(var.tags, {
    Name = "${var.project}-${var.environment}-db-subnet-group"
  })
}

resource "aws_db_parameter_group" "main" {
  name   = "${var.project}-${var.environment}-db-pg"
  family = "postgres17"

  parameter {
    name  = "rds.force_ssl"
    value = var.force_ssl ? "1" : "0"
  }

  tags = merge(var.tags, {
    Name = "${var.project}-${var.environment}-db-pg"
  })
}

################################################################################
# RDS PostgreSQL Instance
################################################################################

resource "aws_db_instance" "main" {
  identifier             = "${var.project}-${var.environment}-db"
  engine                 = "postgres"
  engine_version         = "17.1"
  instance_class         = var.instance_class
  allocated_storage      = var.allocated_storage
  max_allocated_storage  = var.max_allocated_storage
  storage_type           = "gp3"
  db_name                = var.db_name
  username               = var.db_username
  password               = var.db_password
  db_subnet_group_name   = aws_db_subnet_group.main.name
  parameter_group_name   = aws_db_parameter_group.main.name
  vpc_security_group_ids = [var.database_security_group_id]
  multi_az                    = var.multi_az
  storage_encrypted           = true
  backup_retention_period     = var.environment == "production" ? 7 : 1
  performance_insights_enabled = var.environment != "dev"
  skip_final_snapshot         = var.environment != "production"
  publicly_accessible         = false
  deletion_protection         = var.environment == "production" ? true : false

  tags = merge(var.tags, {
    Name = "${var.project}-${var.environment}-db-instance"
  })
}
