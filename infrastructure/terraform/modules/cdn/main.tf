################################################################################
# CloudFront Origin Access Control (OAC)
################################################################################

resource "aws_cloudfront_origin_access_control" "oac" {
  name                              = "${var.project}-${var.environment}-oac"
  description                       = "OAC for static assets bucket"
  origin_access_control_origin_type = "s3"
  signing_behavior                  = "always"
  signing_protocol                  = "sigv4"
}

################################################################################
# CloudFront Distribution
################################################################################

resource "aws_cloudfront_distribution" "assets" {
  origin {
    domain_name              = "${var.assets_bucket_name}.s3.amazonaws.com"
    origin_id                = "s3-assets"
    origin_access_control_id = aws_cloudfront_origin_access_control.oac.id
  }

  enabled             = true
  is_ipv6_enabled     = true
  default_root_object = "index.html"

  default_cache_behavior {
    allowed_methods  = ["GET", "HEAD", "OPTIONS"]
    cached_methods   = ["GET", "HEAD"]
    target_origin_id = "s3-assets"

    forwarded_values {
      query_string = false
      cookies {
        forward = "none"
      }
    }

    viewer_protocol_policy = "redirect-to-https"
    min_ttl                = 0
    default_ttl            = 3600
    max_ttl                = 86400
  }

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

  viewer_certificate {
    cloudfront_default_certificate = true
  }

  tags = merge(var.tags, {
    Name = "${var.project}-${var.environment}-cdn"
  })
}

################################################################################
# S3 Bucket Policy for CloudFront OAC Access
################################################################################

resource "aws_s3_bucket_policy" "allow_cloudfront" {
  bucket = var.assets_bucket_name

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "AllowCloudFrontServicePrincipal"
        Effect = "Allow"
        Principal = {
          Service = "cloudfront.amazonaws.com"
        }
        Action   = "s3:GetObject"
        Resource = "${var.assets_bucket_arn}/*"
        Condition = {
          StringEquals = {
            "AWS:SourceArn" = aws_cloudfront_distribution.assets.arn
          }
        }
      }
    ]
  })
}
