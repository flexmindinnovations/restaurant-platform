################################################################################
# KMS Key
################################################################################

resource "aws_kms_key" "main" {
  description             = "KMS Key for ${var.project}-${var.environment}"
  deletion_window_in_days = 7
  enable_key_rotation     = true

  tags = merge(var.tags, {
    Name = "${var.project}-${var.environment}-kms"
  })
}

resource "aws_kms_alias" "main" {
  name          = "alias/${var.project}-${var.environment}-key"
  target_key_id = aws_kms_key.main.key_id
}

################################################################################
# Secrets Manager
################################################################################

resource "aws_secretsmanager_secret" "db_credentials" {
  name                    = "${var.project}-${var.environment}-db-creds"
  kms_key_id              = aws_kms_key.main.id
  recovery_window_in_days = 0 # dev size override

  tags = var.tags
}

resource "random_password" "db_password" {
  length           = 32
  special          = true
  override_special = "!#$%&*()-_=+[]{}:?"
}

resource "aws_secretsmanager_secret_version" "db_credentials" {
  secret_id = aws_secretsmanager_secret.db_credentials.id
  secret_string = jsonencode({
    username = "platform"
    password = random_password.db_password.result
  })
}

resource "aws_secretsmanager_secret" "jwt_keys" {
  name                    = "${var.project}-${var.environment}-jwt-keys"
  kms_key_id              = aws_kms_key.main.id
  recovery_window_in_days = 0

  tags = var.tags
}

resource "random_password" "jwt_secret" {
  length  = 64
  special = false
}

resource "aws_secretsmanager_secret_version" "jwt_keys" {
  secret_id = aws_secretsmanager_secret.jwt_keys.id
  secret_string = jsonencode({
    secret_key = random_password.jwt_secret.result
  })
}

################################################################################
# IAM Roles & Policies
################################################################################

resource "aws_iam_role" "ecs_execution" {
  name = "${var.project}-${var.environment}-ecs-exec-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })

  tags = var.tags
}

resource "aws_iam_role_policy_attachment" "ecs_execution" {
  role       = aws_iam_role.ecs_execution.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

resource "aws_iam_policy" "ecs_secrets_access" {
  name        = "${var.project}-${var.environment}-ecs-secrets-policy"
  description = "Allows ECS Tasks to retrieve secrets from Secrets Manager"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue",
          "kms:Decrypt"
        ]
        Resource = [
          aws_secretsmanager_secret.db_credentials.arn,
          aws_secretsmanager_secret.jwt_keys.arn,
          aws_kms_key.main.arn
        ]
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "ecs_execution_secrets" {
  role       = aws_iam_role.ecs_execution.name
  policy_arn = aws_iam_policy.ecs_secrets_access.arn
}

resource "aws_iam_role" "ecs_task" {
  name = "${var.project}-${var.environment}-ecs-task-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })

  tags = var.tags
}

################################################################################
# WAF Web ACL
################################################################################

resource "aws_wafv2_web_acl" "main" {
  name        = "${var.project}-${var.environment}-waf"
  description = "WAF for Application Load Balancer"
  scope       = "REGIONAL"

  default_action {
    allow {}
  }

  rule {
    name     = "AWSManagedRulesCommonRuleSet"
    priority = 1

    override_action {
      none {}
    }

    statement {
      managed_rule_group_statement {
        name        = "AWSManagedRulesCommonRuleSet"
        vendor_name = "AWS"
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "WAFCommonRuleSetMetric"
      sampled_requests_enabled   = true
    }
  }

  visibility_config {
    cloudwatch_metrics_enabled = true
    metric_name                = "${var.project}-${var.environment}-waf-metric"
    sampled_requests_enabled   = true
  }

  tags = var.tags
}
