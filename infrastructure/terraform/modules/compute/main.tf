################################################################################
# ECS Cluster
################################################################################

resource "aws_ecs_cluster" "main" {
  name = "${var.project}-${var.environment}-cluster"

  tags = merge(var.tags, {
    Name = "${var.project}-${var.environment}-cluster"
  })
}

################################################################################
# Application Load Balancer (ALB)
################################################################################

resource "aws_lb" "api" {
  name               = "${var.project}-${var.environment}-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [var.alb_security_group_id]
  subnets            = var.public_subnet_ids

  tags = merge(var.tags, {
    Name = "${var.project}-${var.environment}-alb"
  })
}

resource "aws_lb_target_group" "api" {
  name        = "${var.project}-${var.environment}-tg"
  port        = var.container_port
  protocol    = "HTTP"
  vpc_id      = var.vpc_id
  target_type = "ip"

  health_check {
    path                = "/health"
    protocol            = "HTTP"
    port                = "traffic-port"
    interval            = 30
    timeout             = 5
    healthy_threshold   = 3
    unhealthy_threshold = 3
  }

  tags = merge(var.tags, {
    Name = "${var.project}-${var.environment}-tg"
  })
}

resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.api.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type = var.certificate_arn != "" ? "redirect" : "forward"

    dynamic "redirect" {
      for_each = var.certificate_arn != "" ? [1] : []
      content {
        port        = "443"
        protocol    = "HTTPS"
        status_code = "HTTP_301"
      }
    }

    dynamic "forward" {
      for_each = var.certificate_arn == "" ? [1] : []
      content {
        target_group {
          arn = aws_lb_target_group.api.arn
        }
      }
    }
  }
}

resource "aws_lb_listener" "https" {
  count             = var.certificate_arn != "" ? 1 : 0
  load_balancer_arn = aws_lb.api.arn
  port              = 443
  protocol          = "HTTPS"
  ssl_policy        = "ELBSecurityPolicy-TLS13-1-2-2021-06"
  certificate_arn   = var.certificate_arn

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.api.arn
  }
}

################################################################################
# ECS Task Definitions
################################################################################

resource "aws_ecs_task_definition" "api" {
  family                   = "${var.project}-${var.environment}-api"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = var.api_cpu
  memory                   = var.api_memory
  execution_role_arn       = var.ecs_task_execution_role_arn
  task_role_arn            = var.ecs_task_role_arn

  container_definitions = jsonencode([
    {
      name      = "api"
      image     = var.api_image
      essential = true
      portMappings = [
        {
          containerPort = var.container_port
          hostPort      = var.container_port
        }
      ]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = "/ecs/${var.project}-${var.environment}-api"
          "awslogs-region"        = "us-east-1"
          "awslogs-stream-prefix" = "api"
        }
      }
    }
  ])

  tags = merge(var.tags, {
    Name = "${var.project}-${var.environment}-api-task"
  })
}

resource "aws_ecs_task_definition" "worker" {
  family                   = "${var.project}-${var.environment}-worker"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = var.worker_cpu
  memory                   = var.worker_memory
  execution_role_arn       = var.ecs_task_execution_role_arn
  task_role_arn            = var.ecs_task_role_arn

  container_definitions = jsonencode([
    {
      name      = "worker"
      image     = var.worker_image
      essential = true
      command   = ["celery", "-A", "workers.celery_app", "worker", "--loglevel=info"]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = "/ecs/${var.project}-${var.environment}-worker"
          "awslogs-region"        = "us-east-1"
          "awslogs-stream-prefix" = "worker"
        }
      }
    }
  ])

  tags = merge(var.tags, {
    Name = "${var.project}-${var.environment}-worker-task"
  })
}

resource "aws_ecs_task_definition" "beat" {
  family                   = "${var.project}-${var.environment}-beat"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = var.worker_cpu
  memory                   = var.worker_memory
  execution_role_arn       = var.ecs_task_execution_role_arn
  task_role_arn            = var.ecs_task_role_arn

  container_definitions = jsonencode([
    {
      name      = "beat"
      image     = var.worker_image
      essential = true
      command   = ["celery", "-A", "workers.celery_app", "beat", "--loglevel=info"]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = "/ecs/${var.project}-${var.environment}-beat"
          "awslogs-region"        = "us-east-1"
          "awslogs-stream-prefix" = "beat"
        }
      }
    }
  ])

  tags = merge(var.tags, {
    Name = "${var.project}-${var.environment}-beat-task"
  })
}

################################################################################
# ECS Services
################################################################################

resource "aws_ecs_service" "api" {
  name            = "${var.project}-${var.environment}-api"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.api.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = var.private_subnet_ids
    security_groups  = [var.ecs_tasks_security_group_id]
    assign_public_ip = false
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.api.arn
    container_name   = "api"
    container_port   = var.container_port
  }

  depends_on = [aws_lb_listener.http, aws_lb_listener.https]

  tags = merge(var.tags, {
    Name = "${var.project}-${var.environment}-api-service"
  })
}

resource "aws_ecs_service" "worker" {
  name            = "${var.project}-${var.environment}-worker"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.worker.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = var.private_subnet_ids
    security_groups  = [var.ecs_tasks_security_group_id]
    assign_public_ip = false
  }

  tags = merge(var.tags, {
    Name = "${var.project}-${var.environment}-worker-service"
  })
}

resource "aws_ecs_service" "beat" {
  name            = "${var.project}-${var.environment}-beat"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.beat.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = var.private_subnet_ids
    security_groups  = [var.ecs_tasks_security_group_id]
    assign_public_ip = false
  }

  tags = merge(var.tags, {
    Name = "${var.project}-${var.environment}-beat-service"
  })
}

################################################################################
# Autoscaling
################################################################################

resource "aws_appautoscaling_target" "api" {
  max_capacity       = 5
  min_capacity       = 1
  resource_id        = "service/${aws_ecs_cluster.main.name}/${aws_ecs_service.api.name}"
  scalable_dimension = "ecs:service:DesiredCount"
  service_namespace  = "ecs"
}

resource "aws_appautoscaling_policy" "api_cpu" {
  name               = "${var.project}-${var.environment}-api-cpu-scaling"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.api.resource_id
  scalable_dimension = aws_appautoscaling_target.api.scalable_dimension
  service_namespace  = aws_appautoscaling_target.api.service_namespace

  target_tracking_scaling_policy_configuration {
    target_value       = 70.0
    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageCPUUtilization"
    }
    scale_in_cooldown  = 300
    scale_out_cooldown = 60
  }
}
