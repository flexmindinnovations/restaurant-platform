terraform {
  required_version = ">= 1.9"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 5.70"
    }
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = local.common_tags
  }
}

locals {
  common_tags = {
    Project     = var.project
    Environment = var.environment
    ManagedBy   = "terraform"
  }
}

module "networking" {
  source = "../../modules/networking"

  project            = var.project
  environment        = var.environment
  vpc_cidr           = var.vpc_cidr
  availability_zones = var.availability_zones

  tags = local.common_tags
}

module "security" {
  source = "../../modules/security"

  project     = var.project
  environment = var.environment

  tags = local.common_tags
}

module "storage" {
  source = "../../modules/storage"

  project     = var.project
  environment = var.environment

  tags = local.common_tags
}

module "database" {
  source = "../../modules/database"

  project                    = var.project
  environment                = var.environment
  vpc_id                     = module.networking.vpc_id
  database_subnet_ids        = module.networking.database_subnet_ids
  database_security_group_id = module.networking.database_security_group_id
  db_password                = var.db_password
  allocated_storage          = 100
  max_allocated_storage      = 1000
  instance_class             = "db.r6g.large"
  multi_az                   = true

  tags = local.common_tags
}

module "cache" {
  source = "../../modules/cache"

  project                 = var.project
  environment             = var.environment
  vpc_id                  = module.networking.vpc_id
  private_subnet_ids      = module.networking.private_subnet_ids
  cache_security_group_id = module.networking.cache_security_group_id
  node_type               = "cache.t4g.medium"
  num_cache_nodes         = 1

  tags = local.common_tags
}

module "cdn" {
  source = "../../modules/cdn"

  project            = var.project
  environment        = var.environment
  assets_bucket_name = module.storage.assets_bucket_name
  assets_bucket_arn  = module.storage.assets_bucket_arn

  tags = local.common_tags
}

module "compute" {
  source = "../../modules/compute"

  project                     = var.project
  environment                 = var.environment
  vpc_id                      = module.networking.vpc_id
  public_subnet_ids           = module.networking.public_subnet_ids
  private_subnet_ids          = module.networking.private_subnet_ids
  ecs_tasks_security_group_id = module.networking.ecs_tasks_security_group_id
  alb_security_group_id       = module.networking.alb_security_group_id
  ecs_task_execution_role_arn = module.security.ecs_task_execution_role_arn
  ecs_task_role_arn           = module.security.ecs_task_role_arn
  api_cpu                     = "1024"
  api_memory                  = "2048"
  worker_cpu                  = "1024"
  worker_memory               = "2048"

  tags = local.common_tags
}

module "monitoring" {
  source = "../../modules/monitoring"

  project                = var.project
  environment            = var.environment
  ecs_cluster_name       = module.compute.ecs_cluster_name
  api_service_name       = module.compute.api_service_name
  worker_service_name    = module.compute.worker_service_name
  beat_service_name      = module.compute.beat_service_name
  alb_arn_suffix         = module.compute.alb_arn_suffix
  db_instance_identifier = module.database.db_instance_identifier

  tags = local.common_tags
}

module "ci-cd" {
  source = "../../modules/ci-cd"

  project     = var.project
  environment = var.environment

  tags = local.common_tags
}

module "dns" {
  source = "../../modules/dns"

  project                = var.project
  environment            = var.environment
  domain_name            = var.domain_name
  alb_dns_name           = module.compute.alb_dns_name
  alb_zone_id            = module.compute.alb_zone_id
  cloudfront_domain_name = module.cdn.cloudfront_domain_name

  tags = local.common_tags
}
