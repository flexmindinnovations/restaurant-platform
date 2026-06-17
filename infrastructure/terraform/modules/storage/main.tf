################################################################################
# S3 Buckets
################################################################################

resource "aws_s3_bucket" "assets" {
  bucket        = "${var.project}-${var.environment}-assets"
  force_destroy = var.environment != "production"

  tags = merge(var.tags, {
    Name = "${var.project}-${var.environment}-assets"
  })
}

resource "aws_s3_bucket" "documents" {
  bucket        = "${var.project}-${var.environment}-documents"
  force_destroy = var.environment != "production"

  tags = merge(var.tags, {
    Name = "${var.project}-${var.environment}-documents"
  })
}

resource "aws_s3_bucket" "backups" {
  bucket        = "${var.project}-${var.environment}-backups"
  force_destroy = var.environment != "production"

  tags = merge(var.tags, {
    Name = "${var.project}-${var.environment}-backups"
  })
}

################################################################################
# Public Access Blocks
################################################################################

resource "aws_s3_bucket_public_access_block" "documents" {
  bucket                  = aws_s3_bucket.documents.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_public_access_block" "backups" {
  bucket                  = aws_s3_bucket.backups.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

################################################################################
# Lifecycle Policies
################################################################################

resource "aws_s3_bucket_lifecycle_configuration" "backups" {
  bucket = aws_s3_bucket.backups.id

  rule {
    id     = "backups-lifecycle"
    status = "Enabled"

    transition {
      days          = 30
      storage_class = "GLACIER"
    }

    expiration {
      days = 90
    }
  }
}
