################################################################################
# CloudWatch Log Groups
################################################################################

resource "aws_cloudwatch_log_group" "api" {
  name              = "/ecs/${var.project}-${var.environment}-api"
  retention_in_days = 30
  tags              = var.tags
}

resource "aws_cloudwatch_log_group" "worker" {
  name              = "/ecs/${var.project}-${var.environment}-worker"
  retention_in_days = 30
  tags              = var.tags
}

resource "aws_cloudwatch_log_group" "beat" {
  name              = "/ecs/${var.project}-${var.environment}-beat"
  retention_in_days = 30
  tags              = var.tags
}

################################################################################
# CloudWatch Alarms
################################################################################

# Alarm: P1 Platform Down (UnHealthyHostCount >= 1)
resource "aws_cloudwatch_metric_alarm" "platform_down" {
  alarm_name          = "${var.project}-${var.environment}-p1-platform-down"
  comparison_operator = "GreaterThanOrEqualToThreshold"
  evaluation_periods  = 1
  metric_name         = "UnHealthyHostCount"
  namespace           = "AWS/ApplicationELB"
  period              = 60
  statistic           = "Maximum"
  threshold           = 1.0
  alarm_description   = "P1 Alarm: No healthy hosts behind ALB. Platform is down."
  treat_missing_data  = "breaching"

  dimensions = {
    LoadBalancer = var.alb_arn_suffix
  }

  tags = var.tags
}

# Alarm: P1 DB Down (RDS CPU >= 95%)
resource "aws_cloudwatch_metric_alarm" "db_cpu_high" {
  alarm_name          = "${var.project}-${var.environment}-p1-db-cpu-high"
  comparison_operator = "GreaterThanOrEqualToThreshold"
  evaluation_periods  = 2
  metric_name         = "CPUUtilization"
  namespace           = "AWS/RDS"
  period              = 300
  statistic           = "Average"
  threshold           = 95.0
  alarm_description   = "P1 Alarm: RDS CPU utilization is critically high (>= 95%)."

  dimensions = {
    DBInstanceIdentifier = var.db_instance_identifier
  }

  tags = var.tags
}

# Alarm: P2 High HTTP 5XX Error Rate
resource "aws_cloudwatch_metric_alarm" "high_5xx_errors" {
  alarm_name          = "${var.project}-${var.environment}-p2-high-5xx-errors"
  comparison_operator = "GreaterThanOrEqualToThreshold"
  evaluation_periods  = 1
  metric_name         = "HTTPCode_Target_5XX_Count"
  namespace           = "AWS/ApplicationELB"
  period              = 60
  statistic           = "Sum"
  threshold           = 10.0
  alarm_description   = "P2 Alarm: High 5XX error count from backend targets (>= 10 in 1 min)."

  dimensions = {
    LoadBalancer = var.alb_arn_suffix
  }

  tags = var.tags
}

################################################################################
# CloudWatch Dashboard
################################################################################

resource "aws_cloudwatch_dashboard" "main" {
  dashboard_name = "${var.project}-${var.environment}-dashboard"

  dashboard_body = jsonencode({
    widgets = [
      {
        type   = "metric"
        x      = 0
        y      = 0
        width  = 12
        height = 6
        properties = {
          metrics = [
            ["AWS/ApplicationELB", "RequestCount", "LoadBalancer", var.alb_arn_suffix]
          ]
          period = 300
          stat   = "Sum"
          region = "us-east-1"
          title  = "ALB Request Count"
        }
      },
      {
        type   = "metric"
        x      = 12
        y      = 0
        width  = 12
        height = 6
        properties = {
          metrics = [
            ["AWS/RDS", "CPUUtilization", "DBInstanceIdentifier", var.db_instance_identifier]
          ]
          period = 300
          stat   = "Average"
          region = "us-east-1"
          title  = "Database CPU Utilization"
        }
      }
    ]
  })
}
